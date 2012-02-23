'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Pertussis Case Generator


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2012 Commonwealth Informatics
@license: LGPL
'''

# In most instances it is preferable to use relativedelta for date math.  
# However when date math must be included inside an ORM query, and thus will
# be converted into SQL, only timedelta is supported.
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.db.models import F

from ESP.utils import log
from ESP.hef.base import Event
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.hef.base import LabOrderHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case


class Pertussis(DiseaseDefinition):
    '''
    Pertussis
    '''
    
    condition = ['pertussis']
    
    uri = 'urn:x-esphealth:disease:commoninf:pertussis:v1'
    
    short_name = 'pertussis'
    
    test_name_search_strings = ['pertcult','PCR','pert',]
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #
        # Diagnosis Codes
        #
        
        heuristic_list.append( DiagnosisHeuristic(
            name = 'pertussis',
            icd9_queries = [
                Icd9Query(starts_with='033.0'),
                ]
            ))
        heuristic_list.append( DiagnosisHeuristic(
            name = 'cough',
            icd9_queries = [
                Icd9Query(starts_with='033.9'),
                ]
            ))
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'pertussis_med',
            drugs = ['erythromyciin','clarithromycin',
                'azithromycin','trimethoprim-sulfamethoxazole', ],
            ))
        #
        # Lab Results
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'pertussis_culture',
             ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'pertussis_pcr',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'pertussis_serology',
            ))
        #
        # Lab Orders
        #
        # TODO add more orders based on spec.
        heuristic_list.append( LabOrderHeuristic(
            test_name = 'pertussis_serology',
            ))
        
        return heuristic_list
    
    @transaction.commit_on_success
    def generate(self):
        #
        # Criteria Set #1 (dx or lab order + rx within 7 days) 
        #
        dx_ev_names = ['dx:bordetella','dx:cough']
        lx_ev_names = ['lx:bordetella pertussis:order'] #TODO need to check for all the test orders
        rx_ev_names = ['rx:pertussis_antibiotics']
        
        #
        dxrx_event_qs = Event.objects.filter(
            name__in = dx_ev_names,
            patient__event__name__in = rx_ev_names + lx_ev_names,
            patient__event__date__gte = (F('date') - 7 ),
            patient__event__date__lte = (F('date') + 7 ),
            )
        #
        # Criteria Set #2 positive of culture for pertussis
        #
        #TODO add more labs names ??
        labo_ev_names =  [   
            'lx:pertusis:positive',
            
            ]
        test_event_qs = Event.objects.filter(
            name__in = labo_ev_names,  
            )
        #
        # Combined Criteria
        #
        combined_criteria_qs = dxrx_event_qs | test_event_qs 
        combined_criteria_qs = combined_criteria_qs.exclude(case__condition='pertussis')
        combined_criteria_qs = combined_criteria_qs.order_by('date')
        all_event_names = dx_ev_names + rx_ev_names + labo_ev_names + lx_ev_names 
        counter = 0
        for this_event in combined_criteria_qs:
            existing_cases = Case.objects.filter(
                condition='pertussis', 
                patient=this_event.patient) # does not recurr
                
            existing_cases = existing_cases.order_by('date')
            if existing_cases:
                old_case = existing_cases[0]
                old_case.events.add(this_event)
                old_case.save()
                log.debug('Added %s to %s' % (this_event, old_case))
                continue # Done with this event, continue loop
            # No existing case, so we create a new case
            new_case = Case(
                condition = 'pertussis',
                patient = this_event.patient,
                provider = this_event.provider,
                date = this_event.date,
                criteria = 'combined pertussis criteria',
                source = self.uri,
                )
            new_case.save()
            new_case.events.add(this_event)
            all_relevant_events = Event.objects.filter(patient=this_event.patient, name__in=all_event_names)
            for related_event in all_relevant_events:
                new_case.events.add(related_event)
            new_case.save()
            log.info('Created new pertussis case: %s' % new_case)
            counter += 1
        return counter # Count of new cases
            
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

pertussis_definition = Pertussis()

def event_heuristics():
    return pertussis_definition.event_heuristics

def disease_definitions():
    return [pertussis_definition]
