#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from ESP.utils.utils import str_from_date, log
from ESP.ss.models import Site, Locality, NonSpecialistVisitEvent
from heuristics import syndrome_heuristics


REPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')

ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME = 'ESPAtrius_AllEnc_zip5_Excl_Res_%s_%s.xls'
ENCOUNTERS_BY_SITE_ZIP_FILENAME = 'ESPAtrius_AllEnc_zip5_Excl_Res_%s_%s.xls'
AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME = 'ESPAtrius_SyndAgg_zip5_Res_Excl_%s_%s_%s.xls'
AGGREGATE_BY_SITE_ZIP_FILENAME = 'ESPAtrius_SyndAgg_zip5_Site_Excl_%s_%s_%s.xls'
INDIVIDUAL_BY_SYNDROME_FILENAME = 'ESPAtrius_SyndInd_zip5_Site_Excl_%s_%s_%s.xls'

MINIMUM_RESIDENTIAL_CASE_THRESHOLD = 5

AGE_GROUP_INTERVAL = 5
AGE_GROUP_CAP = 90    

AGE_GROUPS = xrange(0, AGE_GROUP_CAP, AGE_GROUP_INTERVAL)


#-----------------------------------------------------------------------------
#
#   Methods to generate Tab-delimited files 
#
#-----------------------------------------------------------------------------

def total_residential_encounters_report(date):
    header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
    timestamp = str_from_date(date)
    filename = os.path.join(REPORT_FOLDER, ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME % (timestamp, timestamp))
    log.debug('Writing file %s' % filename)
    outfile = open(filename, 'w')

    outfile.write('\t'.join(header) + '\n')
    for local in Locality.objects.order_by('zip_code'):
        volume = local.volume(date)
        if not volume: continue
        counts_by_age = [str(x) for x in [local.at_age_group(age, age+AGE_GROUP_INTERVAL, date=date).count()
                         for age in AGE_GROUPS]]

        summary = [timestamp, local.zip_code, str(volume)]
        line = '\t'.join(summary + counts_by_age)
        log.debug(line)
        outfile.write(line + '\n')

    outfile.close()

            
        
def total_site_encounters_report(date):
    header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
    timestamp = str_from_date(date)
    outfile = open(os.path.join(REPORT_FOLDER, ENCOUNTERS_BY_SITE_ZIP_FILENAME % (timestamp, timestamp)), 'w')

    outfile.write('\t'.join(header) + '\n')
    zip_codes = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')

    for zip_code in zip_codes:
        volume = Site.volume_by_zip(zip_code, date)
        if not volume: continue
        counts_by_age = [str(x) for x in [Site.age_group_aggregate(zip_code, date, age, age+AGE_GROUP_INTERVAL) 
                         for age in AGE_GROUPS]]

        summary = [timestamp, zip_code, str(volume)]
        line = '\t'.join(summary + counts_by_age)
        log.debug(line)
        outfile.write(line + '\n')
        

    outfile.close()


def aggregate_residential_report(syndrome, date):
    header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 
              'total encounters', 'pct syndrome']

    timestamp = str_from_date(date)
    outfile = open(os.path.join(REPORT_FOLDER, AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME % (
            syndrome.heuristic_name, timestamp, timestamp)), 'w')

    outfile.write('\t'.join(header) + '\n')

    for local in Locality.objects.order_by('zip_code'):
        total = local.volume(date)
        if not total: continue
        syndrome_count = syndrome.from_locality(local.zip_code).filter(date=date).count()
        pct_syndrome = 0 if total == 0 else syndrome_count/total

        line = '\t'.join([str(x) for x in [timestamp, local.zip_code, syndrome.heuristic_name, syndrome_count, total, pct_syndrome]])
        print line
        outfile.write(line + '\n')

    outfile.close()

def aggregate_site_report(syndrome, date):

    log.info('Aggregate site report')
    header = ['encounter date', 'zip', 'syndrome', 'syndrome events', 
              'total encounters', 'pct syndrome']

    timestamp = str_from_date(date)
    outfile = open(os.path.join(REPORT_FOLDER, AGGREGATE_BY_SITE_ZIP_FILENAME % (
            syndrome.heuristic_name, timestamp, timestamp)), 'w')

    outfile.write('\t'.join(header) + '\n')

    site_zips = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')
    for zip_code in site_zips:
        total = Site.volume_by_zip(zip_code, date)
        if not total: continue

        syndrome_count = syndrome.from_site_zip(zip_code).filter(date=date).count()
        pct_syndrome = 0 if total == 0 else syndrome_count/total

        line = '\t'.join([str(x) for x in [timestamp, zip_code, syndrome.heuristic_name, syndrome_count, total, pct_syndrome]])
        print line
        outfile.write(line + '\n')

    outfile.close()

    
def detailed_site_report(syndrome, date):
    
    header = ['syndrome', 'encounter date', 'zip residence', 'zip site',
              'age 5yrs', 'icd9', 'temperature', 
              'encounters at age and residential zip', 
              'encounters at age and site zip']

    timestamp = str_from_date(date)
    outfile = open(os.path.join(REPORT_FOLDER, INDIVIDUAL_BY_SYNDROME_FILENAME % (
            syndrome.heuristic_name, timestamp, timestamp)), 'w')
    outfile.write('\t'.join(header) + '\n')
    
    for ev in NonSpecialistVisitEvent.objects.filter(
        heuristic_name=syndrome.heuristic_name, date=date).order_by('patient_zip_code'):

        patient_age = int(ev.patient.age/365.25)
        patient_age_group = int(patient_age/AGE_GROUP_INTERVAL)*AGE_GROUP_INTERVAL
        
        icd9_codes = ','.join([
                str(x.code) for x in ev.encounter.icd9_codes.all()])

        count_by_locality_and_age = syndrome.counts_by_age_range(
            patient_age_group, patient_age_group+AGE_GROUP_INTERVAL, 
            locality_zip_code=ev.patient_zip_code)

        count_by_site_and_age = syndrome.counts_by_age_range(
            patient_age_group, patient_age_group+AGE_GROUP_INTERVAL, 
            site_zip_code=ev.reporting_site.zip_code)

        outfile.write('\t'.join([str(x) for x in [
                        syndrome.heuristic_name, timestamp, 
                        ev.patient_zip_code, ev.reporting_site.zip_code, 
                        patient_age_group, icd9_codes, 
                        ev.encounter.temperature,
                        count_by_locality_and_age, count_by_site_and_age, '\n']]))


    outfile.close()
        
        
#-----------------------------------------------------------------------------
#
#   Methods that use the file-generating methods above.
#
#-----------------------------------------------------------------------------


def day_report(date):
    total_residential_encounters_report(date)
    total_site_encounters_report(date)
    
    for heuristic in syndrome_heuristics().values():
        aggregate_site_report(heuristic, date)
        aggregate_residential_report(heuristic, date)
        detailed_site_report(heuristic, date)















    
