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
        make_option('--no-regenerate-statistics', action='store_false', dest='regenerate', 
            help='Do not regenerate montly statistics before producing report', default=True),
        make_option('--summary', action='store_true', dest='summary', default=False,
            help='Produce monthly summary report'),
        make_option('--linelist', action='store_true', dest='linelist', default=False,
            help='Produce patient line list report'),
        )
    
    QUERIES = {
        'ogtt': Q(event_type__name__startswith='ogtt', event_type__name__endswith='--any_result'),
        'a1c': Q(event_type__name='a1c--any_result'),
        'glucose': Q(event_type__name='glucose_fasting--any_result'),
        }
    
    def handle(self, *args, **options):
        if options['regenerate']:
            self.regenerate()
        if options['linelist']:
            self.linelist()
        elif options['summary']:
            self.summary()
        else:
            sys.stderr.write('You must choose either --summary or --linelist\n')
            sys.exit(-1)
    
    
    @commit_on_success
    def regenerate(self):
        log.debug('Truncating MonthlyStatistic table')
        MonthlyStatistic.objects.all().delete() # Truncate table before repopulating
        log.debug('Regenerating monthly statistics')
        all_months = set(Encounter.objects.filter(date__isnull=False).dates('date', 'month').order_by('date'))
        #all_months |= set(LabResult.objects.filter(date__isnull=False).dates('date', 'month').order_by('date'))
        #all_months |= set(LabOrder.objects.filter(date__isnull=False).dates('date', 'month').order_by('date'))
        #all_months |= set(Prescription.objects.filter(date__isnull=False).dates('date', 'month').order_by('date'))
        # Calling distinct() on the QS above does not return distinct month 
        # values.  So we convert the QS to a set object, thereby eliminating 
        # duplicates, then convert the set to a list so it can be sorted.
        all_months = list(all_months)
        all_months.sort() 
        for month_start in all_months:
            values = {}
            end_date = month_start + relativedelta(months=1)
            #
            values['total_encounters'] = Encounter.objects.filter(date__gte=month_start, date__lt=end_date).count()
            encs = Encounter.objects.filter(date__gte=month_start, date__lt=end_date)
            fem_encs = Encounter.objects.filter(date__gte=month_start, date__lt=end_date, patient__gender__iexact='F')
            values['patients_with_encounter'] = encs.values('patient').distinct().count()
            values['female_patients_with_encounter'] = fem_encs.values('patient').distinct().count()
            #
            practic_patient_start = month_start - relativedelta(years=3)
            prac_pt_encs = Encounter.objects.filter(date__gte=practic_patient_start, date__lt=end_date)
            prac_pts = prac_pt_encs.values('patient').annotate(enc_count=Count('pk')).filter(enc_count__gte=2)
            log_query('practice patients', prac_pts)
            values['practice_patients'] = prac_pts.count()
            #
            distinct_races = Patient.objects.filter(race__isnull=False).exclude(race='').values_list('race', flat=True).distinct()
            dob_14 = month_start - relativedelta(years=14)
            dob_45 = month_start - relativedelta(years=45)
            younger_q = Q(patient__date_of_birth__lte=dob_14, patient__date_of_birth__gt=dob_45)
            older_q = Q(patient__date_of_birth__lte=dob_45)
            for race in distinct_races:
                lrace = race.lower().replace(' ', '_')
                values['female_%s_patients' % lrace] = fem_encs.filter(patient__race=race).values('patient').distinct().count()
                values['female_%s_14_to_44_patients' % lrace] = fem_encs.filter(patient__race=race).filter(younger_q).values('patient').distinct().count()
                values['female_%s_over_44_patients' % lrace] = fem_encs.filter(patient__race=race).filter(older_q).values('patient').distinct().count()
            for name in values:
                ms = MonthlyStatistic(
                    month = month_start,
                    name = name,
                    value = values[name],
                    )
                ms.save()
                log.debug(ms)
    
        
    def summary(self):
        '''
        Produces monthly summary report
        '''
        field_names = ['month', 'practice_patients', 'total_encounters', 'patients_with_encounter', 'any_test']
        field_names += self.QUERIES.keys()
        writer = csv.DictWriter(sys.stdout, field_names)
        writer.writerow(field_names) # Header for CSV file
        for ms in MonthlyStatistic.objects.all():
            next_month = ms.month + relativedelta(months=1)
            events = Event.objects.filter(date__gte=ms.month, date__lt=next_month)
            names = self.QUERIES.keys()
            any_q = self.QUERIES[names[0]]
            for name in names[1:]:
                any_q |= self.QUERIES[name]
            self.QUERIES['any_test'] = any_q
            values = {
                'month': ms.month,
                'practice_patients': ms.practice_patients,
                'total_encounters': ms.total_encounters,
                'patients_with_encounter': ms.patients_with_encounter,
                }
            for name in self.QUERIES:
                values[name] = events.filter(self.QUERIES[name]).values('patient').distinct().count()
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