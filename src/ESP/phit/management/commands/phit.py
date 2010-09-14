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
from django.db.models import Q, F

from ESP.phit.models import MonthlyStatistics
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
    
    QUERIES = {
        'ogtt': Q(event_type__name__startswith='ogtt', event_type__name__endswith='--any_result'),
        'a1c': Q(event_type__name='a1c--any_result'),
        'glucose': Q(event_type__name='glucose_fasting--any_result'),
        }
    
    def handle(self, *args, **options):
        log.info('Regenerating monthly statistics')
        MonthlyStatistics.regenerate()
        field_names = ['month', 'practice_patients', 'total_encounters', 'patients_with_encounter', 'any_test']
        field_names += self.QUERIES.keys()
        writer = csv.DictWriter(sys.stdout, field_names)
        for ms in MonthlyStatistics.objects.all():
            next_month = ms.month + relativedelta(months=1)
            events = Event.objects.filter(date__gte=ms.month, date__lte=next_month)
            any_q = Q(pk__isnull=True) # Null Q object
            for name in self.QUERIES:
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