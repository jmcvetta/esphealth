'''
                              ESP Health Project
Public Health Intervention Tracker
                                  Data Models

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''


from django.db import models
from django.db.models import Count
from django.db.transaction import commit_on_success
from dateutil.relativedelta import relativedelta

from ESP.emr.models import Encounter
from ESP.utils import log
from ESP.utils import log_query


class MonthlyStatistics(models.Model):
    '''
    The count of practice patients for any given month, where a practice 
    patient is defined by any patient who has two or more encounter records
    in the past 3 years.
    '''
    month = models.DateField(primary_key=True)
    practice_patients = models.IntegerField(blank=False)
    total_encounters = models.IntegerField(blank=False)
    patients_with_encounter = models.IntegerField(blank=False)
    
    @classmethod
    @commit_on_success
    def regenerate(cls):
        log.debug('Truncating MonthlyStatistics table')
        cls.objects.all().delete() # Truncate table before repopulating
        log.debug('Regenerating MonthlyStatistics table')
        months_qs = Encounter.objects.filter(date__isnull=False).dates('date', 'month').order_by('date')
        log_query('Encounter months', months_qs)
        # Calling distinct() on the QS above does not return distinct month 
        # values.  So we convert the QS to a set object, thereby eliminating 
        # duplicates, then convert the set to a list so it can be sorted.
        all_months = list(set(months_qs))
        all_months.sort() 
        for month_start in all_months:
            end_date = month_start + relativedelta(months=1)
            practic_patient_start = month_start - relativedelta(years=3)
            total_encounters = Encounter.objects.filter(date__gte=month_start, date__lt=end_date).count()
            patients_with_encounter = Encounter.objects.filter(date__gte=month_start, date__lt=end_date).values('patient').distinct().count()
            prac_pt_encs = Encounter.objects.filter(date__gte=practic_patient_start, date__lt=end_date)
            prac_pts = prac_pt_encs.values('patient').annotate(enc_count=Count('pk')).filter(enc_count__gte=2)
            log_query('practice patients', prac_pts)
            prac_pt_count = prac_pts.count()
            log.debug('Monthly Statistics for %s' % month_start)
            log.debug('    Practice patients:       %s' % prac_pt_count)
            log.debug('    Total Encounters:        %s' % total_encounters)
            log.debug('    Patients with Encounter: %s' % patients_with_encounter)
            cls(
                month=month_start, 
                practice_patients = prac_pt_count,
                total_encounters = total_encounters,
                patients_with_encounter = patients_with_encounter,
                ).save()