'''
                                  ESP Health
                         Notifiable Diseases Framework
                         Pelvic Inflammatory Case Generator


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics http://www.commoninf.com
@contact: http://www.esphealth.org
@copyright: (c) 2011Channing Laboratory
@license: LGPL
'''

from dateutil.relativedelta import relativedelta
from ESP.utils import log
from ESP.nodis.base import DiseaseDefinition
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.hef.base import Event
from ESP.nodis.base import Case


class PelvicInflammatoryDisease(DiseaseDefinition):
    '''
    Pelvic Inflammatory Disease
    '''
    
    conditions = ['pelvic_inflammatory_disease']
    
    uri = 'urn:x-esphealth:disease:channing:pelvic_inflammatory_disease:v1'
    
    short_name = 'pelvic_inflammatory_disease'
    
    test_name_search_strings = []
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        # Diagnosis Codes
        #
        heuristic_list.append( DiagnosisHeuristic(
            name = 'pelvic_inflammatory_disease',
            icd9_queries = [
                Icd9Query(starts_with='614.'),
                Icd9Query(exact='099.56'),
               ]
            ))
        return heuristic_list
    
    def generate(self):
        
        #
        # Criteria Set #1
        #
        ev_qs = Event.objects.filter(
            name = 'dx:pelvic_inflammatory_disease'
            ).order_by('date')
        counter = 0
        for ev in ev_qs:
            existing_cases = Case.objects.filter(
                condition='pelvic_inflammatory_disease', 
                patient=ev.patient,
                date__gte=(ev.date - relativedelta(days=28)) # Adds recurrence interval
                )
            existing_cases = existing_cases.order_by('date')
            if existing_cases:
                old_case = existing_cases[0]
                old_case.events.add(ev)
                old_case.save()
                log.debug('Added %s to %s' % (ev, old_case))
                continue # Done with this event, continue loop
            # No existing case, so we create a new case
            new_case = Case(
                condition = 'pelvic_inflammatory_disease',
                patient = ev.patient,
                provider = ev.provider,
                date = ev.date,
                criteria = 'pelvic inflammatory disease criteria',
                source = self.uri,
                )
            new_case.save()
            new_case.events.add(ev)
            all_relevant_events = Event.objects.filter(patient=ev.patient, name__in=ev_qs)
            for related_event in all_relevant_events:
                new_case.events.add(related_event)
            new_case.save()
            log.info('Created new pelvic inflammatory disease case: %s' % new_case)
            counter += 1
        return counter # Count of new cases
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

pelvic_inflammatory_disease_definition = PelvicInflammatoryDisease()

def event_heuristics():
    return pelvic_inflammatory_disease_definition.event_heuristics

def disease_definitions():
    return [pelvic_inflammatory_disease_definition]
