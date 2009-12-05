#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from django.db.models import Count
from django.template import Context
from django.template.loader import get_template

from ESP.emr.models import Encounter, Patient
from ESP.utils.utils import str_from_date, days_in_interval, log
from ESP.ss.models import Site, NonSpecialistVisitEvent, age_group_filter
from ESP.ss.utils import report_folder

from definitions import ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME, ENCOUNTERS_BY_SITE_ZIP_FILENAME
from definitions import MINIMUM_RESIDENTIAL_CASE_THRESHOLD
from definitions import AGE_GROUP_INTERVAL, AGE_GROUP_CAP, AGE_GROUPS

import settings

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

    def __init__(self, begin_date, end_date):
        assert begin_date <= end_date

        self.begin_date = begin_date
        self.end_date = end_date
        self.days = days_in_interval(self.begin_date, self.end_date)
        self.timestamps = str_from_date(self.begin_date), str_from_date(self.end_date)
        self.folder = report_folder(begin_date, end_date)
        self.encounters = Encounter.objects.syndrome_care_visits(sites=Site.site_ids()).filter(date__gte=self.begin_date, date__lte=self.end_date)

    def _make_date_and_zip_and_age_group_mapping(self, zip_codes):
        mapping = {}
        new_group_count = lambda: dict([(group, 0) for group in AGE_GROUPS])
        for day in self.days:
            # Initialize a map to count age groups
            mapping[day] = dict([(code, new_group_count()) for code in zip_codes])

        return mapping

    def _print_mapping_to_file(self, mapping, outfile):
        for day in self.days:
            for zip_code in sorted(mapping[day].keys()):
                age_group_counts = mapping[day][zip_code]
                age_sum = sum(age_group_counts.values())
                if not age_sum: continue

                summary = [str_from_date(day), zip_code, str(age_sum)]
                line = '\t'.join(summary + [str(age_group_counts[group]) for group in AGE_GROUPS])
                outfile.write(line + '\n')

    def gipse_report(self):

        filename = GIPSE_SITE_FILENAME % self.timestamps
        outfile = open(os.path.join(self.folder, filename), 'w')
        events = NonSpecialistVisitEvent.objects.filter(date__gte=self.begin_date, 
                                                        date__lte=self.end_date)

        counts = NonSpecialistVisitEvent.counts_by_site(self.begin_date, self.end_date)

        zip_codes = events.values_list('reporting_site__zip_code', flat=True).distinct()
        syndromes = events.values_list('heuristic', flat=True).distinct()

        params = {
            'timestamp':datetime.datetime.now(),
            'requesting_user':settings.GIPSE_REQUESTING_USER,
            'heuristic_counts':counts,
            'syndromes':syndromes,
            'zip_codes':zip_codes
            }

        msg = get_template(Report.GIPSE_TEMPLATE).render(Context(params))
        log.debug(msg)
        outfile.write(msg)
        outfile.close()
        
    def total_residential_encounters(self):
        header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
        filename = ENCOUNTERS_BY_RESIDENTIAL_ZIP_FILENAME % self.timestamps
        log.debug('Writing file %s' % filename)

        outfile = open(os.path.join(self.folder, filename), 'w')
        outfile.write('\t'.join(header) + '\n')

        zip_codes = Patient.objects.values_list('zip5', flat=True).distinct().order_by('zip5')
        mapping = self._make_date_and_zip_and_age_group_mapping(zip_codes)

        # Now, on to doing the count.
        for e in self.encounters.select_related('patient'):
            patient_group = e.patient.age_group(when=e.date)
            if ((patient_group is not None) and (e.patient.zip5)): 
                mapping[e.date][e.patient.zip5][patient_group] += 1

        # print results from count and close.
        self._print_mapping_to_file(mapping, outfile)
        outfile.close()

    def total_site_encounters(self):
        header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
        filename = ENCOUNTERS_BY_SITE_ZIP_FILENAME % self.timestamps
        outfile = open(os.path.join(self.folder, filename), 'w')

        outfile.write('\t'.join(header) + '\n')

        site_codes = dict([(s.code, s.zip_code) for s in Site.objects.all()])
        zip_codes = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')


        mapping = self._make_date_and_zip_and_age_group_mapping(zip_codes)

        for e in self.encounters:                
            patient_group = e.patient.age_group(when=e.date)
            site_zip_code = e.native_site_num and site_codes.get(e.native_site_num)
            if site_zip_code and (patient_group is not None): 
                mapping[e.date][site_zip_code][patient_group] += 1

        # print results from count and close.
        self._print_mapping_to_file(mapping, outfile)
        outfile.close()


def all_encounters_report(begin_date, end_date):
    report = Report(begin_date, end_date)
    report.total_residential_encounters()
    report.total_site_encounters()
        












    
