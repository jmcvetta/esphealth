#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from django.db.models import Count
from django.template import Context
from django.template.loader import get_template

from ESP.emr.models import Encounter
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

        for day in self.days:
            # Now, on to getting all the encounters and doing the count.
            encounters = Encounter.objects.syndrome_care_visits().filter(date=day)
            zip_codes = encounters.exclude(patient__zip5__isnull=True).values(
                'patient__zip5').annotate(count=Count('patient__zip5')).order_by('patient__zip5')

            for code in zip_codes:
                volume = code['count']
                zip_code = code['patient__zip5']
                if not volume: continue

                
                # Initialize a map to count age groups
                age_group_counts = {}
                for group in AGE_GROUPS:  age_group_counts[group] = 0
                for e in encounters:
                    patient_group = e.patient.age_group()
                    if (patient_group and (zip_code == e.patient.zip5)): age_group_counts[patient_group] += 1

                if volume < sum(age_group_counts.values()): 
                    log.warn('Total at zip" %s, Sum of age counts: %s' % (volume, sum(age_group_counts.values())))


                summary = [str_from_date(day), zip_code, str(volume)]
                line = '\t'.join(summary + [str(age_group_counts[group]) for group in AGE_GROUPS])
                outfile.write(line + '\n')

        outfile.close()

    def total_site_encounters(self):
        header = ['encounter date', 'zip', 'total'] + [str(x) for x in AGE_GROUPS]
        filename = ENCOUNTERS_BY_SITE_ZIP_FILENAME % self.timestamps
        outfile = open(os.path.join(self.folder, filename), 'w')

        outfile.write('\t'.join(header) + '\n')

        zip_codes = Site.objects.values_list('zip_code', flat=True).distinct().order_by('zip_code')

        for day in self.days:
            for zip_code in zip_codes:
                encounters = Site.encounters_by_zip(zip_code).filter(date=day)
                volume = encounters.count()

                if not volume: continue
                
                # Initialize a map to count age groups
                age_group_counts = {}
                for group in AGE_GROUPS:  age_group_counts[group] = 0
                for e in encounters:
                    patient_group = e.patient.age_group()
                    if patient_group: age_group_counts[patient_group] += 1

                if volume < sum(age_group_counts.values()): 
                    log.warn('Total at zip" %s, Sum of age counts: %s' % (volume, sum(age_group_counts.values())))



                summary = [str_from_date(day), zip_code, str(volume)]
                line = '\t'.join(summary + [str(age_group_counts[group]) for group in AGE_GROUPS])
                log.info(line)
                outfile.write(line + '\n')
        
        outfile.close()


def all_encounters_report(begin_date, end_date):
    report = Report(begin_date, end_date)
    report.total_residential_encounters()
    report.total_site_encounters()
        












    
