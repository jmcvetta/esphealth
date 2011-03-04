'''
                                  ESP Health
                          Heuristic Events Framework
                Compound Random/Fasting Glucose Test Heuristic


@author: Jason McVetta <jason.mcvetta@heliotropi.cc>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import datetime
import optparse

from django.db.models import Q
from django.db.models import Min
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.utils import log
from ESP.utils import log_query
from ESP.hef.core import BaseEventHeuristic
from ESP.hef.models import AbstractLabTest
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.hef.models import Timespan


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The VERSION_URI string uniquely describes this heuristic.
# It MUST be incremented whenever any functionality is changed!
VERSION_URI = 'https://esphealth.org/reference/hef/heuristic/compound_random_fasting_glucose/1.0'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



crfg_test = AbstractLabTest.objects.get_or_create(
    name = 'compound_random_fasting_glucose',
    defaults = {
        'verbose_name': 'Compound random/fasting glucose test',
        },
    )[0]

class CompoundRandomFastingGlucoseHeuristic(BaseEventHeuristic):
    
    name = 'compound_random_fasting_glucose'
    
    uri = VERSION_URI
    
    core_uris = [
        'https://esphealth.org/reference/hef/core/1.0',
        ]
    
    __rand_pos = EventType(
        name = 'glucose_random_positive',
        uri = 'https://esphealth.org/reference/event/lab/glucose_random/positive/1.0',
        )
    __rand_neg = EventType(
        name = 'glucose_random_negative',
        uri = 'https://esphealth.org/reference/event/lab/glucose_random/negative/1.0',
        )
    __rand_ind = EventType(
        name = 'glucose_random_indeterminate',
        uri = 'https://esphealth.org/reference/event/lab/glucose_random/indeterminate/1.0',
        )
    __fast_pos = EventType(
        name = 'glucose_fasting_positive',
        uri = 'https://esphealth.org/reference/event/lab/glucose_fasting/positive/1.0',
        )
    __fast_neg = EventType(
        name = 'glucose_fasting_negative',
        uri = 'https://esphealth.org/reference/event/lab/glucose_fasting/negative/1.0',
        )
    __fast_ind = EventType(
        name = 'glucose_fasting_indeterminate',
        uri = 'https://esphealth.org/reference/event/lab/glucose_fasting/indeterminate/1.0',
        )
    
    def event_types(self):
        return [
            self.__rand_pos,
            self.__rand_neg,
            self.__rand_ind,
            self.__fast_pos,
            self.__fast_neg,
            self.__fast_ind
            ]
    
    def generate_events(self):
        for lab in self.test.lab_results.exclude(self.bound_record_q):
            print lab
    
    

crfg = CompoundRandomFastingGlucoseHeuristic()
