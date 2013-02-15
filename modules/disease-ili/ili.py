'''
                                  ESP Health
                         Notifiable Diseases Framework
                     Influenza like illness Case Generator


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
from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from ESP.utils import log
from ESP.hef.base import Event, BaseEventHeuristic,LabResultAnyHeuristic,  PrescriptionHeuristic
from ESP.hef.base import Dose, LabResultPositiveHeuristic, LabOrderHeuristic, DiagnosisHeuristic, Icd9Query
from ESP.nodis.base import DiseaseDefinition, Case
from ESP.static.models import DrugSynonym

class ili(DiseaseDefinition):
    '''
    Influenza like illness
    '''
    
    conditions = ['ili']
    
    uri = 'urn:x-esphealth:disease:commoninf:ili:v1'
    
    short_name = 'ili'
    
    # no tests for ili
    test_name_search_strings = [  ]
    
    timespan_heuristics = []
    
    FEVER_TEMPERATURE = 100.0 # Temperature in Fahrenheit
        
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #
        # Diagnosis Codes
        #  ili
        heuristic_list.append( DiagnosisHeuristic(
            name = 'fever',
            icd9_queries = [
                 Icd9Query(starts_with='780.6'),
                 Icd9Query(starts_with='780.31'),
                ]))
        
                
        heuristic_list.append( DiagnosisHeuristic(
            name = 'ili',
            icd9_queries = [

                 Icd9Query(starts_with='079.3'),
                 Icd9Query(starts_with='079.89'),
                 Icd9Query(starts_with='079.99'),
                 Icd9Query(starts_with='460'),
                 Icd9Query(starts_with='462'),
                 Icd9Query(starts_with='464.00'),
                 Icd9Query(starts_with='464.01'),
                 Icd9Query(starts_with='464.10'),
                 Icd9Query(starts_with='464.11'),
                 Icd9Query(starts_with='464.20'),
                 Icd9Query(starts_with='464.21'),
                 Icd9Query(starts_with='465.0'),
                 Icd9Query(starts_with='465.8'),
                 Icd9Query(starts_with='465.9'),
                 Icd9Query(starts_with='466.0'),
                 Icd9Query(starts_with='466.19'),
                 Icd9Query(starts_with='478.9'),
                 Icd9Query(starts_with='480.8'),
                 Icd9Query(starts_with='480.9'),
                 Icd9Query(starts_with='481'),
                 Icd9Query(starts_with='482.40'),
                 Icd9Query(starts_with='482.41'),
                 Icd9Query(starts_with='482.42'),
                 Icd9Query(starts_with='482.49'),
                 Icd9Query(starts_with='484.8'),
                 Icd9Query(starts_with='485'),
                 Icd9Query(starts_with='486'),
                 Icd9Query(starts_with='487.0'),
                 Icd9Query(starts_with='487.1'),
                 Icd9Query(starts_with='487.8'),
                 Icd9Query(starts_with='784.1'),
                 Icd9Query(starts_with='786.2'),   

                ]
            ))
        
        
        return heuristic_list
           
        
    @transaction.commit_on_success
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
       
        #
        # Criteria Set #1 
        # diagosis of ili and measured fever > 100
        #
        
        dx_ev_names = ['dx:ili',]
        q_measured_fever = Q(patient__event__encounter__temperature__gte =  self.FEVER_TEMPERATURE)
        
        #
        # Criteria Set #2 
        #  diagosis of ili and no fever measured but diagnosis of fever
        #
        
        dx_fever_ev_names = ['dx:fever',]
        q_unmeasured_fever = Q(patient__event__encounter__temperature__isnull=True, patient__event__name__in=dx_fever_ev_names)
        
        #
        # combined criteria
        #
        # Make it really readable. 
        # (icd9 code + measured fever) or (icd9 code + icd9code for fever)
        # Logically: (a&b)+(a&c) = a&(b+c)
        influenza = (q_measured_fever | q_unmeasured_fever)
        
        #
        # Combined Criteria
        #
        combined_criteria_qs =  Event.objects.filter(name__in = dx_ev_names).filter(influenza)
                
        combined_criteria_qs = combined_criteria_qs.exclude(case__condition='ili')
        combined_criteria_qs = combined_criteria_qs.order_by('date')
        all_event_names =  dx_ev_names + dx_fever_ev_names 
        
        counter = self._create_cases_from_event_qs( 
            condition = 'ili', 
            criteria = 'combined ili criteria a and b', 
            recurrence_interval = 42,
            event_qs = combined_criteria_qs, 
            relevant_event_names = all_event_names )
        
           
        log.debug('Generated %s new cases of ili' % counter)
        
        return counter # Count of new cases
            
            
            
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

ili_definition = ili()

def event_heuristics():
    return ili_definition.event_heuristics

def disease_definitions():
    return [ili_definition]