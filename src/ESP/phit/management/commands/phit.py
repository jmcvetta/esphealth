#!/usr/bin/env python
'''
                                  ESP Health
Public Health Intervention Tracker
Practice Patient Count Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory

@license: LGPL
'''

import csv
import sys
from optparse import make_option
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models import F
from django.db.models import Count
from django.db.transaction import commit_on_success

from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.phit.models import MonthlyStatistic
from ESP.hef.models import Event
from ESP.utils import log
from ESP.utils import log_query


#===============================================================================
#
#--- ~~~ Main ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
class Command(BaseCommand):
    
    help = 'Generate counts of practice patients per month'
    
    option_list = BaseCommand.option_list + (
        make_option('--statistics', action='store_true', dest='statistics', 
            help='Regenerate monthly statistics', default=False),
        make_option('--summary', action='store_true', dest='summary', default=False,
            help='Monthly summary report'),
        make_option('--linelist', action='store_true', dest='linelist', default=False,
            help='Patient line list report'),
        )
    
    QUERIES = {
        'ogtt': Q(event_type__name__startswith='ogtt', event_type__name__endswith='--any_result'),
        'a1c': Q(event_type__name='a1c--any_result'),
        'glucose': Q(event_type__name='glucose_fasting--any_result'),
        }
    
    def handle(self, *args, **options):
        if options['statistics']:
            self.regenerate()
        elif options['linelist']:
            self.linelist()
        elif options['summary']:
            self.summary()
        else:
            sys.stderr.write('You must specify either --summary, --linelist, or --statistics\n')
            sys.exit(-1)
    
    @commit_on_success
    def regenerate(self):
        '''
        Regenerate monthly statistics -- those stats that relate only to a 
        month, not to a particular patient -- used to provide denominators 
        for PHIT event data.
        '''
        log.debug('Truncating MonthlyStatistic table')
        MonthlyStatistic.objects.all().delete() # Truncate table before repopulating
        log.debug('Regenerating monthly statistics')
        all_months = Encounter.objects.filter(date__isnull=False).dates('date', 'month').order_by('date')
        log_query('all_months', all_months)
        all_months = set(all_months)
        #all_months |= set(LabResult.objects.filter(date__isnull=False).dates('date', 'month').order_by('date'))
        #all_months |= set(LabOrder.objects.filter(date__isnull=False).dates('date', 'month').order_by('date'))
        #all_months |= set(Prescription.objects.filter(date__isnull=False).dates('date', 'month').order_by('date'))
        #
        # Calling distinct() on the QS above does not return distinct month 
        # values.  So we convert the QS to a set object, thereby eliminating 
        # duplicates, then convert the set to a list so it can be sorted.
        all_months = list(all_months)
        all_months.sort() 
        distinct_races = Patient.objects.filter(race__isnull=False).exclude(race='').values_list('race', flat=True).distinct()
        for month_start in all_months:
            queries = {}
            end_date = month_start + relativedelta(months=1)
            # Encounter stats
            encs = Encounter.objects.filter(date__gte=month_start, date__lt=end_date)
            fem_encs = encs.filter(patient__gender__iexact='F')
            queries['total_encounters'] = encs
            queries['patients_with_encounter'] = encs.values('patient').distinct()
            queries['female_patients_with_encounter'] = fem_encs.values('patient').distinct()
            # Practice patients -- those patients who "belong" to Atrius practice
            practic_patient_start = month_start - relativedelta(years=3)
            prac_pt_encs = Encounter.objects.filter(date__gte=practic_patient_start, date__lt=end_date)
            prac_pts = prac_pt_encs.values('patient').annotate(enc_count=Count('pk')).filter(enc_count__gte=2)
            queries['practice_patients'] = prac_pts
            # Age stratifications
            dob_14 = month_start - relativedelta(years=14)
            dob_45 = month_start - relativedelta(years=45)
            younger_q = Q(patient__date_of_birth__lte=dob_14, patient__date_of_birth__gt=dob_45)
            older_q = Q(patient__date_of_birth__lte=dob_45)
            for race in distinct_races:
                lrace = race.lower().replace(' ', '_')
                queries['female_%s_patients' % lrace] = fem_encs.filter(patient__race=race).values('patient').distinct()
                queries['female_%s_14_to_44_patients' % lrace] = fem_encs.filter(patient__race=race).filter(younger_q).values('patient').distinct()
                queries['female_%s_over_44_patients' % lrace] = fem_encs.filter(patient__race=race).filter(older_q).values('patient').distinct()
            # Lab stats
            labs = LabResult.objects.filter(date__gte=month_start, date__lt=end_date)
            fem_labs = labs.filter(patient__gender__iexact='F')
            queries['total_labresults'] = labs
            queries['patients_with_labresult'] = labs.values('patient').distinct()
            queries['female_patients_with_labresult'] = fem_labs.values('patient').distinct()
            for query_name in queries:
                log_query(query_name, queries[query_name])
                ms = MonthlyStatistic(
                    month = month_start,
                    name = query_name,
                    value = queries[query_name].count(),
                    )
                ms.save()
                log.debug(ms)
    
    def summary(self):
        '''
        Produces monthly summary report
        '''
        # Populate list of field names to initialize dict writer and output header
        field_names = ['month',]
        distinct_races = Patient.objects.filter(race__isnull=False).exclude(race='').values_list('race', flat=True).distinct()
        for query_name in ['any_test'] + self.QUERIES.keys():
            field_names += ['%s_female' % query_name]
            field_names += ['%s_all_patients' % query_name]
            for race in distinct_races:
                lrace = race.lower().replace(' ', '_')
                field_names += ['%s_female_%s' % (query_name, lrace) ]
                field_names += ['%s_female_%s_14_to_44' % (query_name, lrace) ]
                field_names += ['%s_female_%s_over_44' % (query_name, lrace) ]
        all_stat_names = MonthlyStatistic.objects.values_list('name', flat=True).distinct()
        field_names += all_stat_names
        writer = csv.DictWriter(sys.stdout, field_names)
        writer.writerow(dict(zip(field_names, field_names))) # Header for CSV file
        #
        for month in MonthlyStatistic.objects.values_list('month', flat=True).order_by('month').distinct():
            next_month = month + relativedelta(months=1)
            dob_14 = month - relativedelta(years=14)
            dob_45 = month - relativedelta(years=45)
            younger_q = Q(patient__date_of_birth__lte=dob_14, patient__date_of_birth__gt=dob_45)
            older_q = Q(patient__date_of_birth__lte=dob_45)
            #
            events = Event.objects.filter(date__gte=month, date__lt=next_month)
            fem_events = events.filter(patient__gender__iexact='F')
            stratifications = {
                'all_patients': events,
                'female': fem_events,
                }
            for race in distinct_races:
                lrace = race.lower().replace(' ', '_')
                stratifications['female_%s' % lrace] = fem_events.filter(patient__race=race).values('patient').distinct()
                stratifications['female_%s_14_to_44' % lrace] = fem_events.filter(patient__race=race).filter(younger_q).values('patient').distinct()
                stratifications['female_%s_over_44' % lrace] = fem_events.filter(patient__race=race).filter(older_q).values('patient').distinct()
            #
            names = self.QUERIES.keys()
            any_q = self.QUERIES[names[0]]
            for name in names[1:]:
                any_q |= self.QUERIES[name]
            self.QUERIES['any_test'] = any_q
            values = {'month': month, }
            for query_name in self.QUERIES:
                for strat_name in stratifications:
                    out_name = '%s_%s' % (query_name, strat_name)
                    qs = stratifications[strat_name].filter(self.QUERIES[query_name]).values('patient').distinct()
                    log_query(out_name, qs)
                    values[out_name] = qs.count()
            # Add statistical denominators
            for statname in all_stat_names:
                values[statname] = MonthlyStatistic.objects.get(month=month, name=statname).value
            log.debug(values)
            writer.writerow(values)
    
    def linelist(self):
        log.info('Generating patient line list')
        field_names = [
            'month', 
            'patient_last', 
            'patient_first', 
            'patient_mrn', 
            'patient_age',
            'patient_gender',
            'patient_race',
            ]
        field_names += self.QUERIES.keys()
        all_stat_names = MonthlyStatistic.objects.values_list('name', flat=True).distinct()
        field_names += all_stat_names
        writer = csv.DictWriter(sys.stdout, field_names)
        writer.writerow(dict(zip(field_names, field_names))) # Header for CSV file
        for month in MonthlyStatistic.objects.values_list('month', flat=True).distinct().order_by('month'):
            next_month = month + relativedelta(months=1)
            events = Event.objects.filter(date__gte=month, date__lte=next_month)
            # Q object that matches patients who match any query in self.QUERIES
            any_q = Q(pk__isnull=True) # Null Q object
            for name in self.QUERIES:
                any_q |= self.QUERIES[name]
            month_values = {}
            # Get statistics for this month
            for statname in all_stat_names:
                month_values[statname] = MonthlyStatistic.objects.get(month=month, name=statname).value
            # Make a dict associating query names with all patient IDs who match the query this month
            query_pats = {}
            for name in self.QUERIES:
                query_pats[name] = list(events.filter(self.QUERIES[name]).values_list('patient', flat=True).distinct())
            # Generate the line list
            for pat_id in events.filter(any_q).values_list('patient', flat=True).distinct():
                patient = Patient.objects.get(pk=pat_id)
                values = {
                    'month': month,
                    'patient_last': patient.last_name,
                    'patient_first': patient.first_name,
                    'patient_mrn': patient.mrn,
                    'patient_age': relativedelta(month, patient.date_of_birth).years,
                    'patient_gender': patient.gender,
                    'patient_race': patient.race,
                    }
                # Look up patient in query_pats dict to see if pat matches query this month
                for name in self.QUERIES:
                    if patient.pk in query_pats[name]:
                        values[name] = True
                    else:
                        values[name] = False
                values.update(month_values)
                log.debug(values)
                writer.writerow(values)