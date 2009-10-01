#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from django.template import Context
from django.template.loader import get_template

from ESP.emr.models import Encounter
from ESP.utils.utils import str_from_date, log
from ESP.ss.models import Site
from ESP.ss.models import age_group_filter

import settings

REPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')

ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME = 'ESPAtrius_AllEnc_zip5_Excl_Res_%s_%s.xls'
ENCOUNTERS_BY_SITE_ZIP_FILENAME = 'ESPAtrius_AllEnc_zip5_Excl_Res_%s_%s.xls'

MINIMUM_RESIDENTIAL_CASE_THRESHOLD = 5


#-----------------------------------------------------------------------------
#
#   Methods to generate Tab-delimited and XML files for reports related to ALL
#   encounters
#
#-----------------------------------------------------------------------------

class Report(object):


    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'templates')
    REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')
    OLD_REPORT_FOLDER = os.path.join(REPORTS_FOLDER, 'archive')
    NEW_REPORT_FOLDER = os.path.join(REPORTS_FOLDER, 'new')

    GIPSE_TEMPLATE = os.path.join(TEMPLATE_FOLDER, 'xml', 'gipse-response.xml')

    AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME = 'ESPAtrius_SyndAgg_zip5_Res_Excl_%s_%s_%s.xls'
    AGGREGATE_BY_SITE_ZIP_FILENAME = 'ESPAtrius_SyndAgg_zip5_Site_Excl_%s_%s_%s.xls'
    INDIVIDUAL_BY_SYNDROME_FILENAME = 'ESPAtrius_SyndInd_zip5_Site_Excl_%s_%s_%s.xls'
    GIPSE_SITE_FILENAME = 'GIPSE_Response_Site_%s_%s.xml'
    GIPSE_RESIDENTIAL_FILENAME = 'GIPSE_Response_Residential_%s_%s.xml'


    def __init__(self, date):
        self.date = date

    def gipse_report(self, end_date=None):
        if not end_date: end_date = self.date
        assert end_date >= self.date

        filename = GIPSE_SITE_FILENAME % (str_from_date(self.date), str_from_date(end_date))
        outfile = open(os.path.join(Report.REPORTS_FOLDER, filename), 'w')


        counts = NonSpecialistVisitEvent.counts_by_site(self.date, end_date)
        zip_codes = NonSpecialistVisitEvent.objects.filter(
            date__gte=self.date, date__lte=end_date).values_list('reporting_site__zip_code', 
                                                                  flat=True).distinct()
        syndromes = NonSpecialistVisitEvent.objects.filter(
            date__gte=self.date, date__lte=end_date).values_list('heuristic', flat=True).distinct()

        params = {
            'timestamp':datetime.datetime.now(),
            'requesting_user':settings.GIPSE_REQUESTING_USER,
            'heuristic_counts':counts,
            'syndromes':syndromes,
            'zip_codes':zip_codes}

        msg = get_template(Report.GIPSE_TEMPLATE).render(Context(params))
        log.info(msg)
        outfile.write(msg)
        outfile.close()
        
    def total_residential_encounters(self):
        header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
        timestamp = str_from_date(self.date)
        filename = os.path.join(REPORT_FOLDER, ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME % (timestamp, timestamp))
        log.debug('Writing file %s' % filename)
        
        zip_codes = Encounter.objects.filter(date=self.date).values_list(
            'patient__zip5', flat=True).distinct().order_by('patient__zip5')

        site_ids = Site.objects.values_list('code', flat=True)

        outfile = open(filename, 'w')
        outfile.write('\t'.join(header) + '\n')
        
        log.info('Total Zip codes: %d' % len(zip_codes))

        for zip_code in zip_codes:
            counts_by_age = [Encounter.volume(self.date, age_group_filter(age, age+AGE_GROUP_INTERVAL), 
                                              patient__zip5=zip_code, native_site_num__in=[str(x) for x in site_ids])
                             for age in AGE_GROUPS]

            volume = sum(counts_by_age)
        
            log.info('volume: %d' % volume)
            
            summary = [timestamp, zip_code, str(volume)]
            line = '\t'.join(summary + [str(x) for x in counts_by_age])
            log.info(line)
            outfile.write(line + '\n')

        outfile.close()

    def total_site_encounters_report(self):
        header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
        timestamp = str_from_date(self.date)
        outfile = open(os.path.join(REPORT_FOLDER, ENCOUNTERS_BY_SITE_ZIP_FILENAME % (timestamp, timestamp)), 'w')

        outfile.write('\t'.join(header) + '\n')

        zip_codes = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')

        for zip_code in zip_codes:
            counts_by_age = [Site.age_group_aggregate(zip_code, self.date, age, age+AGE_GROUP_INTERVAL) 
                             for age in AGE_GROUPS]
            volume = sum(counts_by_age)
            if not volume: continue

            summary = [timestamp, zip_code, str(volume)]
            line = '\t'.join(summary + [str(x) for x in counts_by_age])
            log.info(line)
            outfile.write(line + '\n')
        

        outfile.close()

    def compare_encounter_counts(self):
        pass

    def _compare_aggregate_file(self, syndrome, filename):
        # Get the contents of the file corresponding to date and syndrome
        date_str = str_from_date(self.date)

        try:
            old_lines = open(os.path.join(Report.OLD_REPORT_FOLDER, 
                                          filename % (syndrome.name, date_str, date_str)
                                          )).readlines()[1:]
            new_lines = open(os.path.join(Report.NEW_REPORT_FOLDER, 
                                          filename % (syndrome.name, date_str, date_str)
                                          )).readlines()[1:]
        except Exception, why:
            return {'etc':why}


        # Some ugly manipulation to get a dictionary of data keyed by zip code.
        new = {}; old = {}

        for line in new_lines:
            data = line.split('\t')
            zip_code, synd_count, total_encounters = data[1], data[3], data[4]
            new[zip_code] = (synd_count, total_encounters)

        for line in old_lines:
            data = line.split('\t')
            zip_code, synd_count, total_encounters = data[1], data[3], data[4]
            old[zip_code] = (synd_count, total_encounters)

        

        # What errors are we looking for? There might be zip codes
        # that are only found on the old code, and vice-versa. Also,
        # there may be the case where a a given zip code has too
        # disparate results between the new code and the old one.

        # Let's start by finding zip codes that are missing.
        old_zips = set(old.keys())
        new_zips = set(new.keys())

        intersection = old_zips.intersection(new_zips)
        missing_in_old = new_zips - old_zips
        missing_in_new = old_zips - new_zips


        disparities = {}
        syndrome_count_disparities = []
        encounter_count_disparities = []
        for zip_code in intersection:
            try:
                new_count, old_count = new[zip_code], old[zip_code]
                if new_count == old_count: continue
                else:
                    disparities[zip_code] = {}
                    if new_count[0] != old_count[0]:
                        disparities[zip_code]['syndrome'] = {'new': new_count[0], 'old': old_count[0]}

                    if new_count[1] != old_count[1]:
                        disparities[zip_code]['encounters'] = {'new':new_count[1], 'old': old_count[1]}

            except Exception, why:
                import pdb; pdb.set_trace()
                        


        result = {}
        if missing_in_old: result['missing_in_old'] = missing_in_old
        if missing_in_new: result['missing_in_new'] = missing_in_new
        if disparities: result['disparities'] = disparities

        return result



    def _compare_aggregate_residential(self, syndrome):
        return self._compare_aggregate_file(syndrome, Report.AGGREGATE_BY_RESIDENTIAL_ZIP_FILENAME)        
    
    def _compare_aggregate_site(self, syndrome):
        return self._compare_aggregate_file(syndrome, Report.AGGREGATE_BY_SITE_ZIP_FILENAME)


        
        

def all_encounters_report(date):
    report = Report(date)
    report.total_residential_encounters()
    report.total_site_encounters()
        












    
