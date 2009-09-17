#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from ESP.emr.models import Encounter
from ESP.utils.utils import str_from_date, log
from ESP.ss.models import Site, NonSpecialistVisitEvent
from ESP.ss.models import age_group_filter
from heuristics import syndrome_heuristics


REPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')

ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME = 'ESPAtrius_AllEnc_zip5_Excl_Res_%s_%s.xls'
ENCOUNTERS_BY_SITE_ZIP_FILENAME = 'ESPAtrius_AllEnc_zip5_Excl_Res_%s_%s.xls'

MINIMUM_RESIDENTIAL_CASE_THRESHOLD = 5


#-----------------------------------------------------------------------------
#
#   Methods to generate Tab-delimited files for reports related to ALL
#   encounters
#
#-----------------------------------------------------------------------------

def total_residential_encounters_report(date):
    header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
    timestamp = str_from_date(date)
    filename = os.path.join(REPORT_FOLDER, ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME % (timestamp, timestamp))
    log.debug('Writing file %s' % filename)

    zip_codes = Encounter.objects.filter(date=date).values_list(
        'patient__zip5', flat=True).distinct().order_by('patient__zip5')

    site_ids = Site.objects.values_list('code', flat=True)

    outfile = open(filename, 'w')
    outfile.write('\t'.join(header) + '\n')

    log.info('Total Zip codes: %d' % len(zip_codes))

    for zip_code in zip_codes:
        counts_by_age = [Encounter.volume(date, age_group_filter(age, age+AGE_GROUP_INTERVAL), 
                                          patient__zip5=zip_code, native_site_num__in=[str(x) for x in site_ids])
                         for age in AGE_GROUPS]

        volume = sum(counts_by_age)
        
        log.info('volume: %d' % volume)

        summary = [timestamp, zip_code, str(volume)]
        line = '\t'.join(summary + [str(x) for x in counts_by_age])
        log.info(line)
        outfile.write(line + '\n')

    outfile.close()

            
        
def total_site_encounters_report(date):
    header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
    timestamp = str_from_date(date)
    outfile = open(os.path.join(REPORT_FOLDER, ENCOUNTERS_BY_SITE_ZIP_FILENAME % (timestamp, timestamp)), 'w')

    outfile.write('\t'.join(header) + '\n')

    zip_codes = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')

    for zip_code in zip_codes:
        counts_by_age = [Site.age_group_aggregate(zip_code, date, age, age+AGE_GROUP_INTERVAL) 
                         for age in AGE_GROUPS]
        volume = sum(counts_by_age)
        if not volume: continue

        summary = [timestamp, zip_code, str(volume)]
        line = '\t'.join(summary + [str(x) for x in counts_by_age])
        log.info(line)
        outfile.write(line + '\n')
        

    outfile.close()


        
        
#-----------------------------------------------------------------------------
#
#   Methods that use the file-generating methods above.
#
#-----------------------------------------------------------------------------


def all_encounters_report(date):
    total_residential_encounters_report(date)
    total_site_encounters_report(date)
        















    
