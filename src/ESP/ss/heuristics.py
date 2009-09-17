#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime

from django.db.models import Q, Count, Max
from django.contrib.contenttypes.models import ContentType

from ESP.conf.common import EPOCH
from ESP.emr.models import Encounter
from ESP.hef.core import EncounterHeuristic
from ESP.hef.models import Run
from ESP.utils.utils import log, date_from_str, str_from_date

from ESP.ss.models import NonSpecialistVisitEvent, Site

from definitions import ICD9_FEVER_CODES
from definitions import influenza_like_illness, haematological, lesions, rash
from definitions import lymphatic, lower_gi, upper_gi, neurological, respiratory


REPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')
AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME = 'ESPAtrius_SyndAgg_zip5_Res_Excl_%s_%s_%s.xls'
AGGREGATE_BY_SITE_ZIP_FILENAME = 'ESPAtrius_SyndAgg_zip5_Site_Excl_%s_%s_%s.xls'
INDIVIDUAL_BY_SYNDROME_FILENAME = 'ESPAtrius_SyndInd_zip5_Site_Excl_%s_%s_%s.xls'
AGE_GROUP_INTERVAL = 5
AGE_GROUP_CAP = 90    

AGE_GROUPS = xrange(0, AGE_GROUP_CAP, AGE_GROUP_INTERVAL)



# According to the specs, all of the syndromes have their specific
# lists of icd9 codes that are always required as part of the
# definition. They could've been simply defined as encounter
# heuristics, except for the fact that some might require a fever
# measurement, and ILI always required a fever to be reported. (Either
# through an icd9 code indicating fever, or through a measured
# temperature).

# So, we're creating two classes for Syndromic
# Surveillance. InfluenzaHeuristic is for events that are defined by a
# set of icd9 and always a fever. OptionFeverHeuristic is for events that
# have a set of icd9s and that a fever *may* be required, depending on
# the icd9 code.

# The definitions that rely only on a set of icd9s (no fever) are just
# instantiated as regular SyndromeHeuristics.


class SyndromeHeuristic(EncounterHeuristic):
    def generate_events(self, incremental=True, **kw):

        #
        # Incremental processing
        #
        if incremental:
            log.debug('Incremental processing requested.')
            runs = Run.objects.filter(def_name = self.def_name, status = 's')
            begin_timestamp = runs.aggregate(ts = Max('timestamp'))['ts'] # aggregate() returns dict
        else:
            log.debug('Incremental processing NOT requested.')
            begin_timestamp = EPOCH
        log.debug('begin_timestamp: %s' % begin_timestamp)

        counter = 0
        encounter_type = ContentType.objects.get_for_model(Encounter)


        begin_date = kw.get('begin_date', begin_timestamp)
        end_date = kw.get('end_date', datetime.date.today())


        for encounter in self.matches(begin_timestamp=begin_date).filter(date__lte=end_date):
            try:
                site = Site.objects.get(code=encounter.native_site_num)
            except:
                site = None
                
            try:
                NonSpecialistVisitEvent.objects.get_or_create(
                    heuristic = self.name,
                    encounter = encounter,
                    date = encounter.date,
                    patient = encounter.patient,
                    definition = self.def_name,
                    def_version = self.def_version,
                    patient_zip_code = encounter.patient.zip[:5].strip(),
                    reporting_site = site,
                    object_id = encounter.id,
                    defaults = {
                        'content_type':encounter_type
                        }
                    )

                counter +=1 

            except Exception, why:
                # There is not much to do if some of the information is bad, so we just log and skip it.
                log.error('Error %s making event from %s' % (why, encounter))

        log.debug('%s events detected' % counter)

        if incremental:
            self.run = Run(def_name = self.def_name) # New Run object for this run
            self.run.save()
            log.debug('Generated new Run object for this run: %s' % self.run)

        return counter
    
    def counts_by_age_range(self, lower, upper=150, **kw):
        '''
        returns the count of occurances of this event, that occur with
        patients only on the date range defined by lower and upper.
        Can also break it by zip code and by date.
        '''
        
        date = kw.get('date', None)
        locality_zip_code = kw.get('locality_zip_code', None)
        site_zip_code = kw.get('site_zip_code', None)

        today = datetime.date.today()
        
        younger_patient_date = datetime.date(year=(today.year - abs(lower)), 
                                     month=today.month, day=today.day)
        older_patient_date = datetime.date(year=(today.year - abs(upper)), 
                                   month=today.month, day=today.day)

        events = NonSpecialistVisitEvent.objects.filter(
            heuristic=self.name, 
            patient__date_of_birth__gte=older_patient_date,
            patient__date_of_birth__lt=younger_patient_date)

        if date:
            events = events.filter(date=date)

        if locality_zip_code:
            events = events.filter(patient_zip_code=locality_zip_code)

        if site_zip_code:
            events = events.filter(reporting_site__zip_code=site_zip_code)

        return events.count()


    def make_reports(self, date):
        self.aggregate_site_report(date)
        self.aggregate_residential_report(date)
        self.detailed_site_report(date)

    def aggregate_site_report(self, date):
        log.debug('Aggregate site report for %s on %s' % (self.name, date))
        header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 
              'total encounters', 'pct syndrome']
        
        timestamp = str_from_date(date)
        outfile = open(os.path.join(REPORT_FOLDER, AGGREGATE_BY_SITE_ZIP_FILENAME % (
                    self.name, timestamp, timestamp)), 'w')

        outfile.write('\t'.join(header) + '\n')

        site_zips = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')
        for zip_code in site_zips:
            total = Site.volume_by_zip(zip_code, date)
            syndrome_count = NonSpecialistVisitEvent.objects.filter(
                date=date, heuristic=self.name, reporting_site__zip_code=zip_code).count()


            if not (total and syndrome_count): continue

            pct_syndrome = 100*(float(syndrome_count)/float(total))

            line = '\t'.join([str(x) for x in [timestamp, zip_code, self.name, syndrome_count, total, '%1.3f' % pct_syndrome]])
            log.debug(line)
            outfile.write(line + '\n')

        outfile.close()

        

    def aggregate_residential_report(self, date):

        ''' 
        For this report, we need - for a given date:
         - How many patients were identified with the syndrome
         - How many patients were seen at the non-specialty sites
         - The syndrome ratio
        '''

        log.debug('Aggregate residential report for %s on %s' % (self.name, date))
        header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 
              'total encounters', 'pct syndrome']

        timestamp = str_from_date(date)
        outfile = open(os.path.join(REPORT_FOLDER, AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME % (
                    self.name, timestamp, timestamp)), 'w')
        
        outfile.write('\t'.join(header) + '\n')

        zip_codes = Encounter.objects.filter(date=date).filter(native_site_num__in=Site.site_ids()).values_list(
            'patient__zip5', flat=True).distinct().order_by('patient__zip5')
        
        for zip_code in zip_codes:
            non_specialty_encounters = Encounter.objects.filter(
                date=date, patient__zip5=zip_code, native_site_num__in=Site.site_ids())
            total_patients = non_specialty_encounters.values_list('patient', flat=True).distinct().count()
            syndrome_patients = NonSpecialistVisitEvent.objects.filter(
                heuristic=self.name, date=date, patient_zip_code=zip_code).count()

            if not (total_patients and syndrome_patients): continue

            pct_syndrome = 100*(float(syndrome_patients)/float(total_patients))

            line = '\t'.join([str(x) for x in [timestamp, zip_code, self.name, syndrome_patients, total_patients, '%1.3f' % pct_syndrome]])
            log.debug(line)
            outfile.write(line + '\n')

        outfile.close()


    def detailed_site_report(self, date):
        log.debug('Detailed site report for %s on %s' % (self.name, date))

        header = ['syndrome', 'encounter date', 'zip residence', 'zip site',
                  'age 5yrs', 'icd9', 'temperature', 
                  'encounters at age and residential zip', 
                  'encounters at age and site zip']

        timestamp = str_from_date(date)
        outfile = open(os.path.join(REPORT_FOLDER, INDIVIDUAL_BY_SYNDROME_FILENAME % (
                    self.name, timestamp, timestamp)), 'w')
        outfile.write('\t'.join(header) + '\n')
    
        for ev in NonSpecialistVisitEvent.objects.filter(
            heuristic=self.name, date=date).exclude(
            reporting_site__isnull=True).order_by('patient_zip_code'):

            if not ev.patient.age: continue

            patient_age = int(ev.patient.age.days/365.25)
            patient_age_group = int(patient_age/AGE_GROUP_INTERVAL)*AGE_GROUP_INTERVAL
        
            encounter_codes = [x.code for x in ev.encounter.icd9_codes.all()]
            icd9_codes = ' '.join([code for code in encounter_codes if code in self.icd9s])

            count_by_locality_and_age = self.counts_by_age_range(
                patient_age_group, patient_age_group+AGE_GROUP_INTERVAL, 
                locality_zip_code=ev.patient_zip_code)

            count_by_site_and_age = self.counts_by_age_range(
                patient_age_group, patient_age_group+AGE_GROUP_INTERVAL, 
                site_zip_code=ev.reporting_site.zip_code)

            outfile.write('\t'.join([str(x) for x in [
                            self.name, timestamp, ev.patient_zip_code, ev.reporting_site.zip_code, 
                            patient_age_group, icd9_codes, ev.encounter.temperature,
                            count_by_locality_and_age, count_by_site_and_age, '\n']]))


        outfile.close()

class InfluenzaHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0 # Temperature in Fahrenheit
    def matches(self, begin_timestamp=None, **kw):        
        q_measured_fever = Q(temperature__gte=InfluenzaHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_fever = Q(temperature__isnull=True, icd9_codes__in=ICD9_FEVER_CODES)
        q_codes = Q(icd9_codes__in=self.icd9s)
        
        # Make it really readable. 
        # (icd9 code + measured fever) or (icd9 code + icd9code for fever)
        # Logically: (a&b)+(a&c) = a&(b+c)
        influenza = (q_codes & (q_measured_fever | q_unmeasured_fever))
        
        
        return self.encounters(begin_timestamp).filter(influenza)

                
class OptionalFeverSyndromeHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0
    def __init__(self, name, def_name, def_version, icd9_fever_map):
        # The only reason why we are overriding __init__ is because
        # each the heuristic depends on the icd9 as well as if a fever
        # is required for that icd9.
        super(OptionalFeverSyndromeHeuristic, self).__init__(name, def_name, 
                                                def_version, icd9_fever_map.keys())
        self.required_fevers = icd9_fever_map

    def matches(self, begin_timestamp=None, **kw):
        
        icd9_requiring_fever = [code for code, required in self.required_fevers.items() if required]
        icd9_non_fever = [code for code, required in self.required_fevers.items() if not required]
        
        q_measured_fever = Q(temperature__gte=OptionalFeverSyndromeHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_fever = Q(temperature__isnull=True, icd9_codes__in=ICD9_FEVER_CODES)

        q_fever_requiring_codes = Q(icd9_codes__in=icd9_requiring_fever)
    
        fever_requiring = (q_fever_requiring_codes & (q_measured_fever | q_unmeasured_fever))
        non_fever_requiring = Q(icd9_codes__in=icd9_non_fever)
        
        return self.encounters(begin_timestamp).filter(fever_requiring | non_fever_requiring)
            



ili = InfluenzaHeuristic('ILI', 'ILI', 1, dict(influenza_like_illness).keys())
haematological = OptionalFeverSyndromeHeuristic('Haematological', 'haematological', 1, dict(haematological))
lymphatic = OptionalFeverSyndromeHeuristic('Lymphatic', 'lymphatic', 1, dict(lymphatic))
rash = OptionalFeverSyndromeHeuristic('Rash', 'rash', 1, dict(rash))
lesions = SyndromeHeuristic('Lesions', 'lesions', 1, dict(lesions).keys())
respiratory = SyndromeHeuristic('Respiratory', 'respiratory', 1, dict(respiratory).keys())
lower_gi = SyndromeHeuristic('Lower GI', 'lower gi', 1, dict(lower_gi).keys())
upper_gi = SyndromeHeuristic('Upper GI', 'upper gi', 1, dict(upper_gi).keys())
neuro = SyndromeHeuristic('Neurological', 'neurological', 1, dict(neurological).keys())


def syndrome_heuristics():
    return {
        'ili':ili,
        'haemotological':haematological,
        'lymphatic':lymphatic,
        'rash':rash,
        'lesions':lesions,
        'respiratory':respiratory,
        'lower_gi':lower_gi,
        'upper_gi':upper_gi,
        'neuro':neuro
    }
