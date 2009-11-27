#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime

from django.db.models import Q, Count, Max
from django.contrib.contenttypes.models import ContentType

from ESP.conf.common import EPOCH
from ESP.emr.models import Encounter
from ESP.hef.core import EncounterHeuristic
from ESP.hef.models import Run, Event
from ESP.utils.utils import log, date_from_str, str_from_date, days_in_interval
from ESP.ss.utils import report_folder
from ESP.ss.models import NonSpecialistVisitEvent, Site

from definitions import AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME, AGGREGATE_BY_SITE_ZIP_FILENAME
from definitions import INDIVIDUAL_BY_SYNDROME_FILENAME
from definitions import AGE_GROUP_INTERVAL, AGE_GROUP_CAP, AGE_GROUPS
from definitions import ICD9_FEVER_CODES
from definitions import influenza_like_illness, haematological, lesions, rash
from definitions import lymphatic, lower_gi, upper_gi, neurological, respiratory

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
    def encounters(self, **kw):
        return Encounter.objects.syndrome_care_visits().filter(icd9_codes__in=self.icd9s)

    def generate_events(self, **kw):
        created = 0
        detected = 0
        encounter_type = ContentType.objects.get_for_model(Encounter)
        begin_date = kw.get('begin_date', EPOCH)
        end_date = kw.get('end_date', datetime.date.today())

        run = Run.objects.create()

        for encounter in self.matches().filter(date__gte=begin_date, date__lte=end_date):
            detected +=1 
            try:
                site = Site.objects.get(code=encounter.native_site_num)
            except:
                site = None
                                
            patient_zip = encounter.patient.zip
            if patient_zip: patient_zip = patient_zip[:5].strip()
            
            ev, new = NonSpecialistVisitEvent.objects.get_or_create(
                name=self.long_name, date=encounter.date, patient=encounter.patient, 
                content_type=encounter_type, object_id=encounter.id, 
                defaults = {'run':run, 'reporting_site':site, 
                            'patient_zip_code':patient_zip, 'encounter':encounter
                            }
                )
            if new: created+= 1
                
        run.status = 's'
        run.save()
        log.info('%s events detected' % detected)
        log.info('%s events created' % created)

        return created
    
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
            patient__date_of_birth__gte=older_patient_date,
            patient__date_of_birth__lt=younger_patient_date, name=self.long_name)

        if date:
            events = events.filter(date=date)

        if locality_zip_code:
            events = events.filter(patient_zip_code=locality_zip_code)

        if site_zip_code:
            events = events.filter(reporting_site__zip_code=site_zip_code)

        return events.count()

    def make_reports(self, date, end_date=None):


        self.aggregate_site_report(date, end_date=end_date)
        self.aggregate_residential_report(date, end_date=end_date)
        self.detailed_site_report(date, end_date=end_date)

    def aggregate_site_report(self, date, end_date=None, exclude_duplicates=True):

        if not end_date: end_date = date

        folder = report_folder(date, end_date)

        log.info('Aggregate site report for %s on %s-%s' % (self.name, date, end_date))
        header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 'total encounters', 
                  'pct syndrome']
        
        timestamp_begin = str_from_date(date)
        timestamp_end = str_from_date(end_date)

        outfile = open(os.path.join(folder, AGGREGATE_BY_SITE_ZIP_FILENAME % (
                    self.name, timestamp_begin, timestamp_end)), 'w')

        outfile.write('\t'.join(header) + '\n')

        site_zips = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')

        days = days_in_interval(date, end_date)


        for day in days:
            for zip_code in site_zips:
                total = Site.volume_by_zip(zip_code, day, exclude_duplicates=exclude_duplicates)
                syndrome_count = NonSpecialistVisitEvent.objects.filter(
                    date=day, name=self.long_name, reporting_site__zip_code=zip_code).count()

                
                if not (total and syndrome_count): continue

                pct_syndrome = 100*(float(syndrome_count)/float(total))

                line = '\t'.join([str(x) for x in [str_from_date(day), zip_code, self.name, syndrome_count, total, '%1.3f' % pct_syndrome]])
                log.info(line)
                outfile.write(line + '\n')


        outfile.close()

    def aggregate_residential_report(self, date, end_date=None, exclude_duplicates=True):

        ''' 
        For this report, we need - for a given date:
         - How many patients were identified with the syndrome
         - How many patients were seen at the non-specialty sites
         - The syndrome ratio
        '''

        if not end_date: end_date = date

        folder = report_folder(date, end_date)

        log.info('Aggregate residential report for %s on %s-%s' % (self.name, date, end_date))
        header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 'total encounters', 
                  'pct syndrome']
        
        timestamp_begin = str_from_date(date)
        timestamp_end = str_from_date(end_date)

        outfile = open(os.path.join(folder, AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME % (
                    self.name, timestamp_begin, timestamp_end)), 'w')
        
        outfile.write('\t'.join(header) + '\n')

        zip_codes = Encounter.objects.syndrome_care_visits(sites=Site.site_ids()).filter(
            date=date).values_list('patient__zip5', flat=True).distinct().order_by('patient__zip5')

        days = days_in_interval(date, end_date)
        
        for day in days:
            for zip_code in zip_codes:
                non_specialty_encounters = Encounter.objects.syndrome_care_visits(
                    sites=Site.site_ids()).filter(date=day, patient__zip5=zip_code)
                if exclude_duplicates:
                    total = non_specialty_encounters.values_list('patient').distinct().count()
                else:
                    total = non_specialty_encounters.count()

                syndrome_patients = NonSpecialistVisitEvent.objects.filter(
                    name=self.long_name, date=day, patient_zip_code=zip_code).count()

                if not (total and syndrome_patients): continue

                pct_syndrome = 100*(float(syndrome_patients)/float(total))

                line = '\t'.join([str(x) for x in [str_from_date(day), zip_code, self.name, 
                                                   syndrome_patients, total, '%1.3f' % pct_syndrome]])
                log.info(line)
                outfile.write(line + '\n')

        outfile.close()


    def detailed_site_report(self, date, end_date=None):
        if not end_date: end_date = date
        folder = report_folder(date, end_date)
        
        log.info('Detailed site report for %s on %s-%s' % (self.name, date, end_date))

        header = ['syndrome', 'encounter date', 'zip residence', 'zip site', 'age 5yrs', 'icd9', 
                  'temperature',  'encounters at age and residential zip', 
                  'encounters at age and site zip']
        
        timestamp_begin = str_from_date(date)
        timestamp_end = str_from_date(end_date)
        
        outfile = open(os.path.join(folder, INDIVIDUAL_BY_SYNDROME_FILENAME % (
                    self.name, timestamp_begin, timestamp_end)), 'w')
        outfile.write('\t'.join(header) + '\n')

        days = days_in_interval(date, end_date)
        
        for day in days:
            for ev in NonSpecialistVisitEvent.objects.filter(name=self.long_name, date=day).exclude(
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

                
                line = '\t'.join([str(x) for x in [
                            self.name, str_from_date(day), ev.patient_zip_code, 
                            ev.reporting_site.zip_code, patient_age_group, icd9_codes, 
                            ev.encounter.temperature,
                            count_by_locality_and_age, count_by_site_and_age, '\n']])
                log.info(line)
                outfile.write(line)
               

        outfile.close()

class InfluenzaHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0 # Temperature in Fahrenheit
    def matches(self, **kw):        

        begin = kw.get('begin_date', EPOCH)
        end = kw.get('end_date', datetime.date.today())

        q_measured_fever = Q(temperature__gte=InfluenzaHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_fever = Q(temperature__isnull=True, icd9_codes__in=ICD9_FEVER_CODES)
        q_codes = Q(icd9_codes__in=self.icd9s)
        
        # Make it really readable. 
        # (icd9 code + measured fever) or (icd9 code + icd9code for fever)
        # Logically: (a&b)+(a&c) = a&(b+c)
        influenza = (q_codes & (q_measured_fever | q_unmeasured_fever))
                
        return self.encounters().filter(influenza).filter(date__gte=begin, date__lte=end)

                
class OptionalFeverSyndromeHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0
    def __init__(self, name, long_name, icd9_fever_map):
        # The only reason why we are overriding __init__ is because
        # each the heuristic depends on the icd9 as well as if a fever
        # is required for that icd9.
        super(OptionalFeverSyndromeHeuristic, self).__init__(name, long_name, icd9_fever_map.keys())
        self.required_fevers = icd9_fever_map

    def matches(self, **kw):

        begin = kw.get('begin_date', EPOCH)
        end = kw.get('end_date', datetime.date.today())

        
        icd9_requiring_fever = [code for code, required in self.required_fevers.items() if required]
        icd9_non_fever = [code for code, required in self.required_fevers.items() if not required]
        
        q_measured_fever = Q(temperature__gte=OptionalFeverSyndromeHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_fever = Q(temperature__isnull=True, icd9_codes__in=ICD9_FEVER_CODES)

        q_fever_requiring_codes = Q(icd9_codes__in=icd9_requiring_fever)
    
        fever_requiring = (q_fever_requiring_codes & (q_measured_fever | q_unmeasured_fever))
        non_fever_requiring = Q(icd9_codes__in=icd9_non_fever)
        
        return self.encounters().filter(fever_requiring | non_fever_requiring).filter(
            date__gte=begin, date__lte=end)
            



def make_long_name(name):
    return 'SS:' + name

ili = InfluenzaHeuristic('ILI', make_long_name('ILI'), dict(influenza_like_illness).keys())
haematological = OptionalFeverSyndromeHeuristic('Haematological', make_long_name('Haematological'), dict(haematological))
lymphatic = OptionalFeverSyndromeHeuristic('Lymphatic', make_long_name('Lymphatic'), dict(lymphatic))
rash = OptionalFeverSyndromeHeuristic('Rash', make_long_name('Rash'), dict(rash))
lesions = SyndromeHeuristic('Lesions', make_long_name('Lesions'), dict(lesions).keys())
respiratory = SyndromeHeuristic('Respiratory', make_long_name('Respiratory'), dict(respiratory).keys())
lower_gi = SyndromeHeuristic('Lower GI', make_long_name('Lower GI'), dict(lower_gi).keys())
upper_gi = SyndromeHeuristic('Upper GI', make_long_name('Upper GI'), dict(upper_gi).keys())
neuro = SyndromeHeuristic('Neurological', make_long_name('Neurological'), dict(neurological).keys())


def syndrome_heuristics():
    return {
        'ili':ili,
        'haematological':haematological,
        'lymphatic':lymphatic,
        'rash':rash,
        'lesions':lesions,
        'respiratory':respiratory,
        'lower_gi':lower_gi,
        'upper_gi':upper_gi,
        'neuro':neuro
    }
