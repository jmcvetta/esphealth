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

from ESP.emr.models import Encounter
from ESP.emr.models import Patient
from ESP.hef.base import AbstractLabTest
from ESP.hef.base import BaseEventHeuristic
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
        'urn:x-esphealth:hef:core:v1',
        ]
    
    result_test = AbstractLabTest('glucose-compound-random-fasting-result')
    flag_test = AbstractLabTest('glucose-compound-random-fasting-flag')
    
    _rand_140 = 'lx:glucose-random:threshold:140'
    _rand_200 = 'lx:glucose-random:threshold:200'
    _fast_140 = 'lx:glucose-fasting:threshold:140'
    _fast_200 = 'lx:glucose-fasting:threshold:200'
    
    event_names = [
        _rand_140,
        _rand_200,
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
        lab_qs = self.result_test.lab_results
        lab_qs = lab_qs.exclude(tags__event_name__in=self.event_names)
        lab_qs = lab_qs.filter(result_float__gte=140) # Only scores over 140 have events defined
        #
        # Find flags
        #
        flag_results = self.flag_test.lab_results
        fasting_qs = flag_results.filter(result_string__istartswith='fast').exclude(result_string__iendswith='rand')
        fasting_qs = fasting_qs.exclude(tags__event_name__in=self.event_names)
        log_query('fasting flag patients & dates', fasting_qs)
        fasting_pat_dates = {}
        for pat_date in fasting_qs.values('patient', 'date').distinct():
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
            over_200 = lab.result_float >= 200 # Is test score over 200?
            if lab.date in fasting_pat_dates.get(lab.patient.id, []):
                e = Event(
                    name = self._fast_140,
                    source = self.uri,
                    patient = lab.patient,
                    provider = lab.provider,
                    date = lab.date,
                    )
                e.save()
                e.tag(lab)
                e.tag_qs( fasting_qs.filter(patient=lab.patient, date=lab.date) )
                log.debug('Created event: %s' % e)
                counter += 1
                if over_200:
                    e = Event(
                        name = self._fast_200,
                        source = self.uri,
                        patient = lab.patient,
                        provider = lab.provider,
                        date = lab.date,
                        )
                    e.save()
                    e.tag(lab)
                    e.tag_qs( fasting_qs.filter(patient=lab.patient, date=lab.date) )
                    log.debug('Created event: %s' % e)
                    counter += 1
            else:
                e = Event(
                    name = self._rand_140,
                    source = self.uri,
                    patient = lab.patient,
                    provider = lab.provider,
                    date = lab.date,
                    )
                e.save()
                e.tag(lab)
                log.debug('Created event: %s' % e)
                counter += 1
                if over_200:
                    e = Event(
                        name = self._rand_200,
                        source = self.uri,
                        patient = lab.patient,
                        provider = lab.provider,
                        date = lab.date,
                        )
                    e.save()
                    e.tag(lab)
                    log.debug('Created event: %s' % e)
                    counter += 1
        return counter
        
    
    

def get_heuristics():
    return [
        CompoundRandomFastingGlucoseHeuristic(),
        ]
