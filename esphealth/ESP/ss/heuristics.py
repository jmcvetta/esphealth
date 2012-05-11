#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime

from django.db.models import Q, Count, Max
from django.contrib.contenttypes.models import ContentType

from ESP.conf.common import EPOCH
from ESP.emr.models import Encounter, Patient
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.hef.models import Event
from ESP.utils.utils import log, date_from_str, str_from_date, days_in_interval, timeit
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



class SyndromeHeuristic(DiagnosisHeuristic):
    
    
    
    def encounters(self, **kw):
        '''
        Overrides DiagnosisHeuristic.encounter property to return only 
        encounters matching both diagnosis codes and syndrome.  
        '''
        qs = NonSpecialistVisitEvent.syndrome_care_visits() # TODO FIXME: Bad location for syndrome_care_visits()
        qs = qs & super(SyndromeHeuristic, self).encounters
        return qs

    def generate(self, **kw):
        created = 0
        detected = 0
        raw_encounter_type = ContentType.objects.get_for_model(Encounter)
        begin_date = kw.get('begin_date', EPOCH)
        end_date = kw.get('end_date', datetime.date.today())


        for encounter in self.matches().filter(date__gte=begin_date, date__lte=end_date):
            detected +=1 
            try:
                site = Site.objects.get(code=encounter.site_natural_key)
            except:
                site = None
                                
            patient_zip = encounter.patient.zip
            if patient_zip: patient_zip = patient_zip[:5].strip()
            
            ev, new = NonSpecialistVisitEvent.objects.get_or_create(
                name=self.name, provider=encounter.provider, date=encounter.date, patient=encounter.patient, 
                content_type=raw_encounter_type, object_id=encounter.id, 
                defaults = {'reporting_site':site, 
                            'patient_zip_code':patient_zip, 'encounter':encounter
                            }
                )
            if new: created+= 1
                
        log.info('%s events detected' % detected)
        log.info('%s events created' % created)

        return created
    
   

    def make_reports(self, date, end_date=None):
        self.aggregate_residential_report(date, end_date=end_date)
        self.aggregate_site_report(date, end_date=end_date)
        self.detailed_site_report(date, end_date=end_date)

    
    def aggregate_residential_report(self, date, end_date=None, exclude_duplicates=True):

        ''' 
        For this report, we need - for a given date:
         - How many patients were identified with the syndrome
         - How many patients were seen at the non-specialty sites
         - The syndrome ratio
        '''

        if not end_date: end_date = date

        folder = report_folder(date, end_date, subfolder='reports')

        log.info('Aggregate residential report for %s on %s-%s' % (self.name, date, end_date))
        header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 'total encounters', 
                  'pct syndrome']
        
        timestamp_begin = str_from_date(date)
        timestamp_end = str_from_date(end_date)

        outfile = open(os.path.join(folder, AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME % (
                    self.name, timestamp_begin, timestamp_end)), 'w')
        
        outfile.write('\t'.join(header) + '\n')
        
        zip_codes = Patient.objects.values_list('zip5', flat=True).distinct().order_by('zip5')
        days = days_in_interval(date, end_date)

        encounters = NonSpecialistVisitEvent.syndrome_care_visits(sites=Site.site_ids()).values(
            'date', 'patient__zip5').exclude(patient__zip5__isnull=True)

        events = NonSpecialistVisitEvent.objects.filter(name=self.name).values(
            'date', 'patient_zip_code').exclude(patient_zip_code__isnull=True)
        
        if exclude_duplicates: 
            encounters = encounters.distinct('patient')
            events = events.distinct('patient')
            
        encounters = encounters.annotate(count=Count('patient__zip5')).filter(
            date__gte=date, date__lte=end_date).order_by('date', 'patient__zip5').iterator()
        events = events.annotate(count=Count('patient_zip_code')).filter(
            date__gte=date, date__lte=end_date).order_by('date', 'patient_zip_code').iterator()


        try:
            e = encounters.next(); ev = events.next()
        except StopIteration:
            e, ev = None, None


        while e and ev:
            try:
                while e['date'] < ev['date']: e = encounters.next()
                while (e['patient__zip5'] < ev['patient_zip_code']) and (e['date'] == ev['date']): e = encounters.next()
        
                if (e['date'] == ev['date']) and (e['patient__zip5'] == ev['patient_zip_code']):
                    total_encounters = e['count']
                    total_cases = ev['count']
                    pct_syndrome = 100*(float(total_cases)/float(total_encounters))
                                    
                    line = '\t'.join([str(x) for x in [
                                str_from_date(e['date']), e['patient__zip5'], self.name, 
                                total_cases, total_encounters, '%1.3f' % pct_syndrome]])
                    log.debug(line)
                    outfile.write(line + '\n')

                ev = events.next()
            except StopIteration:
                break

        outfile.close()


    
    def aggregate_site_report(self, date, end_date=None, exclude_duplicates=True):

        if not end_date: end_date = date

        folder = report_folder(date, end_date, subfolder='reports')

        log.info('Aggregate site report for %s on %s-%s' % (self.name, date, end_date))
        header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 'total encounters', 
                  'pct syndrome']
        
        timestamp_begin = str_from_date(date)
        timestamp_end = str_from_date(end_date)

        outfile = open(os.path.join(folder, AGGREGATE_BY_SITE_ZIP_FILENAME % (
                    self.name, timestamp_begin, timestamp_end)), 'w')

        outfile.write('\t'.join(header) + '\n')

        sites = dict([(s.code, s.zip_code) for s in Site.objects.all()])
        site_zips = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')

        days = days_in_interval(date, end_date)

        encounters = NonSpecialistVisitEvent.syndrome_care_visits(sites=Site.site_ids()).values(
            'date', 'site_natural_key')

        events = NonSpecialistVisitEvent.objects.filter(name=self.name).values(
            'date', 'reporting_site__zip_code')
        
        if exclude_duplicates: 
            encounters = encounters.distinct('patient')
            events = events.distinct('patient')
            
        encounters = encounters.annotate(count=Count('site_natural_key')).filter(
            date__gte=date, date__lte=end_date).order_by('date').iterator()
        events = events.annotate(count=Count('reporting_site__zip_code')).exclude(
            reporting_site__isnull=True).filter(
            date__gte=date, date__lte=end_date).order_by('date').iterator()
    
                
        try:
            e = encounters.next(); ev = events.next()
        except StopIteration:
            e, ev = None, None


        while e and ev:

            while e['date'] < ev['date']: e = encounters.next()
            while e['date'] > ev['date']: ev = events.next()

            assert e['date'] == ev['date']

            cur_date = e['date']
            encounters_by_zip = dict([(zip_code, 0) for zip_code in site_zips])
            events_by_zip = dict([(zip_code, 0) for zip_code in site_zips])
            
            try:
                while e['date'] == cur_date:
                    site_zip = sites.get(e['site_natural_key'])
                    if site_zip: encounters_by_zip[site_zip] += 1
                    try:
                        e = encounters.next()
                    except StopIteration:
                        e['date'] = None
                while ev['date'] == cur_date:
                    events_by_zip[ev['reporting_site__zip_code']] +=1
                    ev = events.next()

            except StopIteration:
                break
            finally:
                for zip_code in sorted(site_zips):
                    total_encounters = encounters_by_zip.get(zip_code, 0)
                    total_events = events_by_zip.get(zip_code, 0)
                    
                    if not (total_encounters and total_events): continue
                    
                    pct_syndrome = 100*(float(total_events)/float(total_encounters))
                    line = '\t'.join([str(x) for x in [
                                str_from_date(cur_date), zip_code, self.name, total_events, 
                                total_encounters, '%1.3f' % pct_syndrome]
                                      ])
                    log.debug(line)
                    outfile.write(line + '\n')


        outfile.close()


    def detailed_site_report(self, date, end_date=None):
        if not end_date: end_date = date
        folder = report_folder(date, end_date, subfolder='reports')
        
        log.info('Detailed site report for %s on %s-%s' % (self.name, date, end_date))
        log.info('syndrome,encounter date,zip residence,zip site,age 5yrs,icd9,temperature,encounters at age and residential zip,encounters at age and site zip')
       
        header = ['syndrome', 'encounter date', 'zip residence', 'zip site', 'age 5yrs', 'icd9', 
                  'temperature',  'encounters at age and residential zip', 
                  'encounters at age and site zip']
        
        timestamp_begin = str_from_date(date)
        timestamp_end = str_from_date(end_date)
        
        outfile = open(os.path.join(folder, INDIVIDUAL_BY_SYNDROME_FILENAME % (
                    self.name, timestamp_begin, timestamp_end)), 'w')
        outfile.write('\t'.join(header) + '\n')

        events = NonSpecialistVisitEvent.objects.filter(
            name=self.name, date__gte=date, date__lte=end_date, reporting_site__isnull=False
            ).order_by('date', 'patient_zip_code')
        
        for ev in events:                
            if not ev.patient.age: continue
            
            patient_age_group = ev.patient.age_group(when=ev.date)
            
            encounter_codes = [x.code for x in ev.encounter.icd9_codes.all()]
            icd9_codes = ' '.join([code for code in encounter_codes if code in self.icd9_queries])
            
            count_by_locality_and_age = ev.similar_age_group().filter(
                patient_zip_code=ev.patient_zip_code, date=ev.date).count()
                
            count_by_site_and_age = ev.similar_age_group().filter(
                reporting_site__zip_code=ev.reporting_site.zip_code, date=ev.date).count()

            line = '\t'.join([str(x) for x in [
                        self.name, str_from_date(ev.date), ev.patient_zip_code, 
                        ev.reporting_site.zip_code, patient_age_group, icd9_codes, 
                        ev.encounter.temperature,
                        count_by_locality_and_age, count_by_site_and_age, '\n']])
            log.debug(line)
            outfile.write(line)
               

        outfile.close()

class InfluenzaHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0 # Temperature in Fahrenheit
    def matches(self, **kw):        
        
        begin = kw.get('begin_date', EPOCH)
        end = kw.get('end_date', datetime.date.today())
        q_measured_fever = Q(temperature__gte=InfluenzaHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_fever = Q(temperature__isnull=True, icd9_codes__in=ICD9_FEVER_CODES)
        
        # Make it really readable. 
        # (icd9 code + measured fever) or (icd9 code + icd9code for fever)
        # Logically: (a&b)+(a&c) = a&(b+c)
        influenza = (q_measured_fever | q_unmeasured_fever)
        
        return self.encounters().filter(influenza).filter(date__gte=begin, date__lte=end)

                
class OptionalFeverSyndromeHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0
    def __init__(self, name, long_name, icd9_fever_map):
        # The only reason why we are overriding __init__ is because
        # each the heuristic depends on the icd9 as well as if a fever
        # is required for that icd9.
        icd9_queries = [Icd9Query(exact=icd9_str) for icd9_str in icd9_fever_map.keys()]
        super(OptionalFeverSyndromeHeuristic, self).__init__(name, long_name, icd9_queries)
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

'''
haematological = OptionalFeverSyndromeHeuristic('Haematological', make_long_name('Haematological'), dict(haematological))
lymphatic = OptionalFeverSyndromeHeuristic('Lymphatic', make_long_name('Lymphatic'), dict(lymphatic))
rash = OptionalFeverSyndromeHeuristic('Rash', make_long_name('Rash'), dict(rash))
lesions = SyndromeHeuristic('Lesions', make_long_name('Lesions'), dict(lesions).keys())
respiratory = SyndromeHeuristic('Respiratory', make_long_name('Respiratory'), dict(respiratory).keys())
lower_gi = SyndromeHeuristic('Lower GI', make_long_name('Lower GI'), dict(lower_gi).keys())
upper_gi = SyndromeHeuristic('Upper GI', make_long_name('Upper GI'), dict(upper_gi).keys())
neuro = SyndromeHeuristic('Neurological', make_long_name('Neurological'), dict(neurological).keys())
'''

def syndrome_heuristics():
    icd9_queries = [Icd9Query(exact=icd9_str) for icd9_str in dict(influenza_like_illness).keys()]
    ili = InfluenzaHeuristic('ili',  icd9_queries)
    return {
        'ili':ili 
        #'haematological':haematological,
        #'lymphatic':lymphatic,
        #'rash':rash,
        #'lesions':lesions,
        #'respiratory':respiratory,
        #'lower_gi':lower_gi,
        #'upper_gi':upper_gi,
        #'neuro':neuro      
    }
