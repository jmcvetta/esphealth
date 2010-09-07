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


class PracticePatients(models.Model):
    '''
    The count of practice patients for any given month, where a practice 
    patient is defined by any patient who has two or more encounter records
    in the past 3 years.
    '''
    month = models.DateField(primary_key=True)
    patient_count = models.IntegerField(blank=False)
    
    @classmethod
    @commit_on_success
    def regenerate(cls):
        PracticePatients.objects.all().delete() # Truncate table before repopulating
        end_date = None
        month_start_date = None
        for month_end_date in Encounter.objects.dates('date', 'month'):
            if not month_start_date:
                month_start_date = month_end_date                
                continue
            end_date = month_end_date
            begin_date = month_start_date - relativedelta(years=3)
            encs = Encounter.objects.filter(date__gte=begin_date, date__lt=end_date)
            prac_pts = encs.values('patient').annotate(enc_count=Count('pk')).filter(enc_count__gte=2)
            #log_query('practice patients for %s' % begin_date, prac_pts)
            prac_pt_count = prac_pts.count()
            PracticePatients(month=month_start_date, patient_count=prac_pt_count).save()
            log.debug('Practice patients for %s: %s' % (month_start_date, prac_pt_count))
            month_start_date = month_end_date