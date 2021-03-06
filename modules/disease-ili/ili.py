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
from ESP.hef.base import Dose, LabResultPositiveHeuristic, LabOrderHeuristic, DiagnosisHeuristic, Dx_CodeQuery
from ESP.nodis.base import DiseaseDefinition, Case
from ESP.static.models import DrugSynonym
from ESP.emr.models import Encounter



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
        # Diagnosis Codes for fever
        #  
        heuristic_list.append( DiagnosisHeuristic(
            name = 'fever',
            dx_code_queries = [
                 Dx_CodeQuery(starts_with='780.6', type='icd9'),
                 Dx_CodeQuery(starts_with='780.31', type='icd9'),
                ]))
        
        #
        # Diagnosis Codes for ili
        #        
        heuristic_list.append( DiagnosisHeuristic(
            name = 'ili',
            dx_code_queries = [

                 Dx_CodeQuery(starts_with='079.3', type='icd9'),
                 Dx_CodeQuery(starts_with='079.89', type='icd9'),
                 Dx_CodeQuery(starts_with='079.99', type='icd9'),
                 Dx_CodeQuery(starts_with='460', type='icd9'),
                 Dx_CodeQuery(starts_with='462', type='icd9'),
                 Dx_CodeQuery(starts_with='464.00', type='icd9'),
                 Dx_CodeQuery(starts_with='464.01', type='icd9'),
                 Dx_CodeQuery(starts_with='464.10', type='icd9'),
                 Dx_CodeQuery(starts_with='464.11', type='icd9'),
                 Dx_CodeQuery(starts_with='464.20', type='icd9'),
                 Dx_CodeQuery(starts_with='464.21', type='icd9'),
                 Dx_CodeQuery(starts_with='465.0', type='icd9'),
                 Dx_CodeQuery(starts_with='465.8', type='icd9'),
                 Dx_CodeQuery(starts_with='465.9', type='icd9'),
                 Dx_CodeQuery(starts_with='466.0', type='icd9'),
                 Dx_CodeQuery(starts_with='466.19', type='icd9'),
                 Dx_CodeQuery(starts_with='478.9', type='icd9'),
                 Dx_CodeQuery(starts_with='480.8', type='icd9'),
                 Dx_CodeQuery(starts_with='480.9', type='icd9'),
                 Dx_CodeQuery(starts_with='481', type='icd9'),
                 Dx_CodeQuery(starts_with='482.40', type='icd9'),
                 Dx_CodeQuery(starts_with='482.41', type='icd9'),
                 Dx_CodeQuery(starts_with='482.42', type='icd9'),
                 Dx_CodeQuery(starts_with='482.49', type='icd9'),
                 Dx_CodeQuery(starts_with='484.8', type='icd9'),
                 Dx_CodeQuery(starts_with='485', type='icd9'),
                 Dx_CodeQuery(starts_with='486', type='icd9'),
                 Dx_CodeQuery(starts_with='487.0', type='icd9'),
                 Dx_CodeQuery(starts_with='487.1', type='icd9'),
                 Dx_CodeQuery(starts_with='487.8', type='icd9'),
                 Dx_CodeQuery(starts_with='784.1', type='icd9'),
                 Dx_CodeQuery(starts_with='786.2', type='icd9'),   

                ]
            ))
        
        
        return heuristic_list
           
        
    @transaction.commit_on_success
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)       
        
        dx_ev_names = ['dx:ili',]
        dx_fever_ev_names = ['dx:fever',]
 
        # adding cases for each criterion separately because django generates 
        # bad sql when you use '|' to combine query sets.
        #
        # Criteria Set #b 
        # diagnosis of ili and no temperature measured but diagnosis of fever 
        #
       
        dx_ili_fever_qs = Event.objects.filter(
            name__in = dx_ev_names,
            patient__event__name__in = dx_fever_ev_names,
            patient__event__encounter__exact  = (F('encounter')),
            encounter__temperature__isnull=True,
            ) 

        ili_criteria_qs1 =  dx_ili_fever_qs
        ili_criteria_qs1 = ili_criteria_qs1.exclude(case__condition='ili')
        ili_criteria_qs1 = ili_criteria_qs1.order_by('date')
        all_event_names =  dx_ev_names + dx_fever_ev_names 
        
        counter = self._create_cases_from_event_qs( 
            condition = 'ili', 
            criteria = 'Criteria #2: dx:ili and no temp measured and dx:fever', 
            recurrence_interval = 42,
            event_qs = ili_criteria_qs1, 
            relevant_event_names = all_event_names )
        
        #
        # Criteria Set #a 
        # diagnosis of ili and measured temperature >= 100
        #
        
        dx_ili_measured_fever_qs = Event.objects.filter(
            name__in = dx_ev_names,
            encounter__temperature__gte = self.FEVER_TEMPERATURE,
            )

        ili_criteria_qs2 = dx_ili_measured_fever_qs 
        ili_criteria_qs2 = ili_criteria_qs2.exclude(case__condition='ili')
        ili_criteria_qs2 = ili_criteria_qs2.order_by('date')
        all_event_names =  dx_ev_names 
        
        counter += self._create_cases_from_event_qs( 
            condition = 'ili', 
            criteria = 'Criteria #1: dx:ili and measured temp >= 100', 
            recurrence_interval = 42,
            event_qs = ili_criteria_qs2, 
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