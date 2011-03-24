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
from ESP.hef.core import EventType
from ESP.hef.core import AbstractLabTest
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.hef.models import Timespan


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The VERSION_URI string uniquely describes this heuristic.
# It MUST be incremented whenever any functionality is changed!
VERSION_URI = 'urn:x-esphealth:heuristic:compound-random-fasting-glucose:v1'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




class CompoundRandomFastingGlucoseHeuristic(BaseEventHeuristic):
    
    name = 'crf_glucose'
    
    uri = VERSION_URI
    
    core_uris = [
        'urn:x-esphealth:core:v1',
        ]
    
    __rand_pos = EventType(
        name = 'glucose_random_positive',
        uri = 'urn:x-esphealth:event:labresult:glucose-random:v1:positive',
        )
    __rand_neg = EventType(
        name = 'glucose_random_negative',
        uri = 'urn:x-esphealth:event:labresult:glucose-random:v1:negative',
        )
    __rand_ind = EventType(
        name = 'glucose_random_indeterminate',
        uri = 'urn:x-esphealth:event:labresult:glucose-random:v1:indeterminate',
        )
    __fast_pos = EventType(
        name = 'glucose_fasting_positive',
        uri = 'urn:x-esphealth:event:labresult:glucose-fasting:v1:positive',
        )
    __fast_neg = EventType(
        name = 'glucose_fasting_negative',
        uri = 'urn:x-esphealth:event:labresult:glucose-fasting:v1:negative',
        )
    __fast_ind = EventType(
        name = 'glucose_fasting_indeterminate',
        uri = 'urn:x-esphealth:event:labresult:glucose-fasting:v1:indeterminate',
        )
    
    result_test = AbstractLabTest(
    	name = 'crfg_result',
    	uri = 'urn:x-esphealth:abstractlabtest:glucose-compound-random-fasting-result:v1'
    	)

    flag_test = AbstractLabTest(
    	name = 'crfg_flag',
    	uri = 'urn:x-esphealth:abstractlabtest:glucose-compound-random-fasting-flag:v1'
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
        for res in self.result_test.lab_results:
            print res
        return 0
        
    
    

def get_heuristics():
    return [
        CompoundRandomFastingGlucoseHeuristic(),
        ]
