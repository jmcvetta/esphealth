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

from functools import partial

from django.db import transaction
from django.db.models import Q
from django.db.models import Min

from ESP.utils import log, log_query
from ESP.utils.utils import wait_for_threads
from ESP.emr.models import Encounter
from ESP.emr.models import Patient
from ESP.hef.base import AbstractLabTest
from ESP.hef.base import BaseEventHeuristic
from ESP.hef.models import Event


class CompoundRandomFastingGlucoseHeuristic(BaseEventHeuristic):
    
    short_name = 'labresult:glucose-crf'
    
    uri = 'urn:x-esphealth:heuristic:channing:glucose-compound-random-fasting:v1'
    
    core_uris = [
        'urn:x-esphealth:hef:core:v1',
        ]
    
    result_test = AbstractLabTest('glucose-compound-random-fasting-result')
    flag_test = AbstractLabTest('glucose-compound-random-fasting-flag')
    
    _rand_any     = 'lx:glucose-random:any-result'
    _rand_140_200 = 'lx:glucose-random:range:gte:140:lt:200'
    _rand_140     = 'lx:glucose-random:threshold:140'
    _rand_200     = 'lx:glucose-random:threshold:200'
    _fast_any     = 'lx:glucose-fasting:any-result'
    _fast_100_125 = 'lx:glucose-fasting:range:gte:100:lte:125'
    _fast_140     = 'lx:glucose-fasting:threshold:140'
    _fast_200     = 'lx:glucose-fasting:threshold:200'
    
    event_names = [
        _rand_any,
        _rand_140_200,
        _rand_140,
        _rand_200,
        _fast_any,
        _fast_100_125,
        _fast_140,
        _fast_200,
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
        # Find flags
        #
        flag_results = self.flag_test.lab_results
        fasting_qs = flag_results.filter(result_string__istartswith='fast').exclude(result_string__iendswith='rand')
        fasting_qs = fasting_qs.exclude(tags__event_name__in=self.event_names)
        self.fasting_qs = fasting_qs
        log_query('fasting flag patients & dates', fasting_qs)
        fasting_pat_dates = {}
        log.debug('Populating fasting patient/date dictionary')
        for pat_date in fasting_qs.values('patient', 'date').distinct():
            p = pat_date['patient']
            d = pat_date['date']
            if p in fasting_pat_dates:
                fasting_pat_dates[p].append(d)
            else:
                fasting_pat_dates[p] = [d]
        self.fasting_pat_dates = fasting_pat_dates
        #
        # Find unbound test results
        #
        lab_qs = self.result_test.lab_results
        lab_qs = lab_qs.exclude(tags__event_name__in=self.event_names)
        lab_qs = lab_qs.order_by('date')
        log_query('random/fasting glucose labs', lab_qs)
        #
        # Examine labs
        #
        log.debug('Preparing threads')
        funcs = [partial(self.events_from_lab, lab) for lab in lab_qs]
        event_counter = wait_for_threads(funcs)
        return event_counter
    
    @transaction.commit_on_success
    def events_from_lab(self, lab):
        '''
        Examine a glucose CRF lab and generate appropriate events.  This is 
        done in a separate function so we can use transaction control to 
        (hopefully) speed things up.
        '''
        log.debug('Generating events for lab #%s' % lab.pk)
        counter = 0
        res = lab.result_float
        events = [] # Names of events to create
        fasting = False
        if lab.date in self.fasting_pat_dates.get(lab.patient.id, []):
            #
            # This is a fasting glucose lab
            #
            fasting = True
            events.append(self._fast_any)
            if 100 <= res <= 125:
                events.append(self._fast_100_125)
            if res >= 140:
                events.append(self._fast_140)
            if res >= 200:
                events.append(self._fast_200)
        else:
            #
            # This is a random glucose lab
            #
            events.append(self._rand_any)
            if 140 <= res < 200:
                events.append(self._rand_140_200)
            if res >= 140:
                events.append(self._rand_140)
            if res >= 200:
                events.append(self._rand_200)
        for event_name in events:
            e = Event(
                name = event_name,
                source = self.uri,
                patient = lab.patient,
                provider = lab.provider,
                date = lab.date,
                )
            e.save()
            e.tag(lab)
            if fasting:
                e.tag_qs( self.fasting_qs.filter(patient=lab.patient, date=lab.date) )
            log.debug('Created event: %s' % e)
            counter += 1
        return counter
        
    
    

def get_heuristics():
    return [
        CompoundRandomFastingGlucoseHeuristic(),
        ]
