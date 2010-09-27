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
from ESP.emr.models import LabResult
from ESP.emr.models import LabOrder
from ESP.emr.models import Prescription
from ESP.utils import log
from ESP.utils import log_query


class MonthlyStatistic(models.Model):
    '''
    The count of practice patients for any given month, where a practice 
    patient is defined by any patient who has two or more encounter records
    in the past 3 years.
    '''
    month = models.DateField(blank=False, db_index=True)
    name = models.CharField(max_length=128, blank=False, db_index=True)
    value = models.CharField(max_length=128, blank=False)
    
    def __unicode__(self):
        return u'%s %s: %s' % (self.month, self.name, self.value)