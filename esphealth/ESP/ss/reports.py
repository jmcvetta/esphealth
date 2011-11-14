#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, pdb

from django.db.models import Count
from django.template import Context
from django.template.loader import get_template

from ESP.emr.models import Encounter, Patient
from ESP.utils.utils import str_from_date, days_in_interval, log, timeit
from ESP.ss.models import Site, NonSpecialistVisitEvent, age_group_filter
from ESP.ss.utils import report_folder

from definitions import ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME, ENCOUNTERS_BY_SITE_ZIP_FILENAME
from definitions import MINIMUM_RESIDENTIAL_CASE_THRESHOLD
from definitions import AGE_GROUP_INTERVAL, AGE_GROUP_CAP, AGE_GROUPS

#-----------------------------------------------------------------------------
#
#   Methods to generate Tab-delimited and XML files for reports related to ALL
#   encounters
#
#-----------------------------------------------------------------------------

class Report(object):

    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'templates')

    GIPSE_TEMPLATE = os.path.join(TEMPLATE_FOLDER, 'xml', 'gipse-response.xml')
    GIPSE_SITE_FILENAME = 'GIPSE_Response_Site_%s_%s.xml'
    GIPSE_RESIDENTIAL_FILENAME = 'GIPSE_Response_Residential_%s_%s.xml'
    GIPSE_REQUESTING_USER = 'Tester'

    def __init__(self, begin_date, end_date):
        assert begin_date <= end_date

        self.begin_date = begin_date
        self.end_date = end_date
        self.days = days_in_interval(self.begin_date, self.end_date)
        self.timestamps = str_from_date(self.begin_date), str_from_date(self.end_date)
        self.folder = report_folder(begin_date, end_date, subfolder='reports')
        self.encounters = Encounter.objects.syndrome_care_visits(sites=Site.site_ids()).filter(
            date__gte=self.begin_date, date__lte=self.end_date)


    def _write_date_zip_summary(self, day, zip_code, age_group_map, outfile):
            # Output results for this date and zip to the file.
            age_sum = sum(age_group_map.values())
            if not age_sum: return

            age_group_map = [str(age_group_map[group]) for group in AGE_GROUPS]            
            summary = [str_from_date(day), zip_code, str(age_sum)]
            line = '\t'.join(summary + age_group_map)
            log.debug(line)
            outfile.write(line + '\n')

    def gipse_report(self):

        filename = GIPSE_SITE_FILENAME % self.timestamps
        outfile = open(os.path.join(self.folder, filename), 'w')
        events = NonSpecialistVisitEvent.objects.filter(date__gte=self.begin_date, 
                                                        date__lte=self.end_date)

        counts = NonSpecialistVisitEvent.counts_by_site(self.begin_date, self.end_date)

        zip_codes = events.values_list('reporting_site__zip_code', flat=True).distinct()
        syndromes = events.values_list('heuristic', flat=True).distinct()

        msg = get_template(Report.GIPSE_TEMPLATE).render(Context({
                    'timestamp':datetime.datetime.now(),
                    'requesting_user':Report.GIPSE_REQUESTING_USER,
                    'heuristic_counts':counts,
                    'syndromes':syndromes,
                    'zip_codes':zip_codes
                    }))

        log.debug(msg)
        outfile.write(msg)
        outfile.close()
        
    def total_residential_encounters(self):
        header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
        filename = ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME % self.timestamps
        log.info('Writing file %s' % filename)

        outfile = open(os.path.join(self.folder, filename), 'w')
        outfile.write('\t'.join(header) + '\n')


        encounters = self.encounters.select_related('patient').exclude(
            patient__zip5__isnull=True).order_by('date', 'patient__zip5').iterator()

        try:
            e = encounters.next()
        except StopIteration:
            e = None

        while e:
            cur_date, cur_zip = e.date, e.patient.zip5
            age_group_counts = dict([(group, 0) for group in AGE_GROUPS])
            try:
                while (e.date == cur_date) and (e.patient.zip5 == cur_zip):
                    patient_group = e.patient.age_group(when=e.date)
                    if ((patient_group is not None) and (e.patient.zip5)): 
                        age_group_counts[patient_group] += 1
                    e = encounters.next()
            except StopIteration:
                break
            finally:
                self._write_date_zip_summary(cur_date, cur_zip, age_group_counts, outfile)

            
        outfile.close()


    def total_site_encounters(self):
        header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
        filename = ENCOUNTERS_BY_SITE_ZIP_FILENAME % self.timestamps
        outfile = open(os.path.join(self.folder, filename), 'w')

        outfile.write('\t'.join(header) + '\n')

        site_codes = dict([(s.code, s.zip_code) for s in Site.objects.all()])
        zip_codes = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')

        encounters = self.encounters.order_by('date').iterator()

        try:
            e = encounters.next()
        except StopIteration:
            e = None


        while e:
            cur_date = e.date
            mapping = {}
            for zip_code in zip_codes:
                for group in AGE_GROUPS:
                    mapping[(zip_code, group)] = 0
            try:
                while e.date == cur_date:
                    patient_group = e.patient.age_group(when=e.date)
                    site_zip_code = e.site_natural_key and site_codes.get(e.site_natural_key)
                    if site_zip_code and (patient_group is not None): 
                        mapping[(site_zip_code, patient_group)] += 1
                    e = encounters.next()
            except StopIteration:
                break
            finally:
                for zip_code in zip_codes:
                    age_group_counts = dict([(group, mapping[(zip_code, group)]) for group in AGE_GROUPS])
                    self._write_date_zip_summary(cur_date, zip_code, age_group_counts, outfile)
                
        outfile.close()        
    

def all_encounters_report(begin_date, end_date):
    report = Report(begin_date, end_date)
    report.total_residential_encounters()
    report.total_site_encounters()
        












    
