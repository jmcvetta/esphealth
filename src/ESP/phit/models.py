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
    def regenerate(cls):
        month_list = Encounter.objects.dates('date', 'month')
        log_query('month_list', month_list)
        print month_list