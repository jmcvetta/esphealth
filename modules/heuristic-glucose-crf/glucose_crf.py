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

from ESP.emr.models import Encounter, Patient
from ESP.hef.base import AbstractLabTest, BaseEventHeuristic, EventType
from ESP.hef.models import Event, Timespan
from ESP.utils import log, log_query
from django.core.management.base import BaseCommand
from django.db.models import Min, Q
from optparse import make_option
import datetime
import optparse




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The VERSION_URI string uniquely describes this heuristic.
# It MUST be incremented whenever any functionality is changed!
VERSION_URI = 'urn:x-esphealth:heuristic:glucose-compound-random-fasting:v1'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




class CompoundRandomFastingGlucoseHeuristic(BaseEventHeuristic):
    
    name = 'glucose_crf'
    
    uri = VERSION_URI
    
    core_uris = [
        'urn:x-esphealth:core:v1',
        ]
    
    __rand_140 = EventType(
        name = 'glucose_random_140',
        uri = 'urn:x-esphealth:event:labresult:glucose-random:v1:threshold:140',
        )
    __rand_200 = EventType(
        name = 'glucose_random_200',
        uri = 'urn:x-esphealth:event:labresult:glucose-random:v1:threshold:200',
        )
    __fast_140 = EventType(
        name = 'glucose_fasting_140',
        uri = 'urn:x-esphealth:event:labresult:glucose-fasting:v1:threshold:140',
        )
    __fast_200 = EventType(
        name = 'glucose_fasting_200',
        uri = 'urn:x-esphealth:event:labresult:glucose-fasting:v1:threshold:200',
        )
    
    result_test = AbstractLabTest(
    	name = 'crfg_result',
    	uri = 'urn:x-esphealth:abstractlabtest:glucose-compound-random-fasting-result:v1'
    	)

    flag_test = AbstractLabTest(
    	name = 'crfg_flag',
    	uri = 'urn:x-esphealth:abstractlabtest:glucose-compound-random-fasting-flag:v1'
    	)

    
    event_types = [
        __rand_140,
        __rand_200,
        __fast_140,
        __fast_200,
        ]
    
    def generate(self):
        '''
        The native codes bound to self.result_test can indicate either a random 
        or a fasting glucose test.  If patient has a test from self.flag_test 
        with a certain result_string ordered on the same day as their result_test,
        then a fasting glucose test is indicated.  Otherwise, test is assumed 
        to be random glucose.
        '''
        #
        # NOTE:
        #
        # It appears that Django's fairly limited ORM cannot construct the type
        # of join required to make this heuristic run efficiently.  For now I
        # am going to handle this programmatically by looping over patient/date
        # pairs.  In the future, this might be a good candidate for conversion
        # to SqlAlchemy or some other ORM.
        #
        counter = 0
        #
        # Find unbound test results
        #
        relevant_events = Event.objects.filter(self.event_uri_q)
        lab_qs = self.result_test.lab_results
        lab_qs = lab_qs.filter(result_float__gte=140) # Only scores over 140 have events defined
        lab_qs = lab_qs.exclude(tags__event__in=relevant_events)
        #
        # Find flags
        #
        flag_results = self.flag_test.lab_results
        fasting_flag_records = flag_results.filter(result_string__istartswith='fast').exclude(result_string__iendswith='rand')
        fasting_patients = fasting_flag_records.values_list('patient', flat=True)
        fasting_qs = fasting_flag_records.values('patient', 'date').distinct()
        log_query('fasting flag patients & dates', fasting_qs)
        fasting_pat_dates = {}
        for pat_date in fasting_qs:
            p = pat_date['patient']
            d = pat_date['date']
            if p in fasting_pat_dates:
                fasting_pat_dates[p].append(d)
            else:
                fasting_pat_dates[p] = [d]
        #
        # Find fasting test results
        log_query('random/fasting glucose labs', lab_qs)
        #
        for lab in lab_qs:
            fasting = False # Assume random glucose by default
            over_200 = lab.result_float >= 200 # Is test score over 200?
            if lab.date in fasting_pat_dates.get(lab.patient.id, []):
                e = self.__fast_140.create_event(lab.patient, lab.provider, lab.date)
                e.tag(lab)
                e.tag_qs( fasting_flag_records.filter(patient=lab.patient, date=lab.date) )
                counter += 1
                if over_200:
                    e = self.__fast_200.create_event(lab.patient, lab.provider, lab.date)
                    e.tag(lab)
                    e.tag_qs( fasting_flag_records.filter(patient=lab.patient, date=lab.date) )
                    counter += 1
            else:
                e = self.__rand_140.create_event(lab.patient, lab.provider, lab.date)
                e.tag(lab)
                counter += 1
                if over_200:
                    e = self.__rand_200.create_event(lab.patient, lab.provider, lab.date)
                    e.tag(lab)
                    counter += 1
        return counter
        
    
    

def get_heuristics():
    return [
        CompoundRandomFastingGlucoseHeuristic(),
        ]
