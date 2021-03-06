'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Tuberculosis Case Generator


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

class Tuberculosis(DiseaseDefinition):
    '''
    Tuberculosis
    '''
    
    conditions = ['tuberculosis']
    
    uri = 'urn:x-esphealth:disease:commoninf:tuberculosis:v1'
    
    short_name = 'tuberculosis'
    
    test_name_search_strings = ['tuber','afb','cult','mycob',
        'tb',
        'tc',
        'flu',
        'strep',
        'hav',
        'hcv',
        'oral',
        'tol',
        ]

    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #
        # Diagnosis Codes
        # 010.00-018.99
        heuristic_list.append( DiagnosisHeuristic(
            name = 'tuberculosis',
            dx_code_queries = [
                Dx_CodeQuery(starts_with='010.', type='icd9'),
                Dx_CodeQuery(starts_with='011.', type='icd9'),
                Dx_CodeQuery(starts_with='012.', type='icd9'),
                Dx_CodeQuery(starts_with='013.', type='icd9'),
                Dx_CodeQuery(starts_with='014.', type='icd9'),
                Dx_CodeQuery(starts_with='015.', type='icd9'),
                Dx_CodeQuery(starts_with='016.', type='icd9'),
                Dx_CodeQuery(starts_with='017.', type='icd9'),
                Dx_CodeQuery(starts_with='018.', type='icd9'),
                ]
            ))
        
        # defining any lab result heuristic to be able to map them
        # using the order date as the date of the heuristic
        for test_name in [
            'tuberculosis_pcr',
            'tuberculosis_afb',
            'tuberculosis_culture',
            ]:
            heuristic_list.append( LabResultAnyHeuristic(
                test_name = test_name,
                date_field = 'order',
                ) )
        
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'pyrazinamide',
            drugs = DrugSynonym.generics_plus_synonyms([ 'pyrazinamide', 'PZA',]),
            exclude = ['CAPZA',], 
            ))
        
        heuristic_list.append( PrescriptionHeuristic(
            name = 'isoniazid',
            drugs = DrugSynonym.generics_plus_synonyms([ 'Isoniazid','INH',]),
            exclude = ['INHAL', 'INHIB',], 
            ))
        
        for drug in [
            'moxifloxacin',
            'ethambutol',
            'rifampin',
            'rifabutin',
            'rifapentine',
            'streptomycin',
            'para_aminosalicyclic_acid',
            'kanamycin',
            'capreomycin',
            'cycloserine',
            'ethionamide',
            ]:
         
            heuristic_list.append( PrescriptionHeuristic(
                name = drug,
                drugs = DrugSynonym.generics_plus_synonyms([drug]),
                ))
        
        
        return heuristic_list
    
    
    def generate_def_a_b(self):   
        #
        # Criteria Set #1 (single rx) 
        #
        rx_ev_names = ['rx:pyrazinamide']
        
        rx_event_qs = Event.objects.filter(
            name__in = rx_ev_names,
            )
        self.criteria = ''
        if rx_event_qs:
            self.criteria = 'Criteria #1: Single rx:pyrazinamide '
        #
        # Criteria Set #2 
        # dx in the 14 days prior to the lab order (any test result) or 
        # dx in the 60 days following the lab order (any test result)
        #
        dx_ev_names = ['dx:tuberculosis']
        lx_ev_names = ['lx:tuberculosis_pcr:any-result','lx:tuberculosis_culture:any-result','lx:tuberculosis_afb:any-result'] 
        # TODO check to make sure we validate the event names use BaseEventHeuristic.get_events_by_name        
        dxlx14_event_qs = Event.objects.filter(
            name__in = lx_ev_names,
            patient__event__name__in =  dx_ev_names,
            patient__event__date__gte = (F('date') - 14 ),
            patient__event__date__lte = (F('date') ),
            )
        
        dxlx60_event_qs = Event.objects.filter(
            name__in = lx_ev_names,
            patient__event__name__in = dx_ev_names,
            patient__event__date__lte = (F('date') + 60 ),
            patient__event__date__gte = (F('date') ),
            )
        
        if dxlx14_event_qs or dxlx60_event_qs:
            self.criteria += ' Criteria #2: dx:tuberculosis w/in 14 days prior to the lab order (any test result) or dx w/in 60 days following the lab order (any test result)'
        #
        # Combined Criteria
        #
        combined_criteria_qs = rx_event_qs | dxlx14_event_qs  | dxlx60_event_qs 
        combined_criteria_qs = combined_criteria_qs.exclude(case__condition='tuberculosis')
        combined_criteria_qs = combined_criteria_qs.order_by('date')
        all_event_names = rx_ev_names + dx_ev_names + lx_ev_names 
        counter = 0
        for this_event in combined_criteria_qs:
            existing_cases = Case.objects.filter(
                condition='tuberculosis', 
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
                condition = 'tuberculosis',
                patient = this_event.patient,
                provider = this_event.provider,
                date = this_event.date,
                criteria = self.criteria,
                source = self.uri,
                )
            new_case.save()
            new_case.events.add(this_event)
            all_relevant_events = Event.objects.filter(patient=this_event.patient, name__in=all_event_names)
            for related_event in all_relevant_events:
                new_case.events.add(related_event)
            new_case.save()
            log.info('Created new tuberculosis case: %s' % new_case)
            counter += 1
        return counter
        
    def generate_def_c(self):
        #
        # Criteria Set #3 dx and 2 distinct prescription orders
        #  
        log.info('Generating cases for Tuberculosis Definition (C)')
        counter = 0
        allrx_event_names =  ['rx:isoniazid','rx:pyrazinamide','rx:moxifloxacin', 'rx:ethambutol',
                            'rx:rifampin','rx:rifabutin','rx:rifapentine','rx:streptomycin',
                            'rx:para_aminosalicyclic_acid','rx:kanamycin','rx:capreomycin',
                            'rx:cycloserine','rx:ethionamide',]
           
        dx_qs = BaseEventHeuristic.get_events_by_name('dx:tuberculosis')
        dx_qs = dx_qs.exclude(case__condition=self.conditions[0])
        dx_qs = dx_qs.order_by('patient', 'date') 
        for dx_event in dx_qs:            
            relevancy_begin = dx_event.date - relativedelta(days=60)
            relevancy_end = dx_event.date + relativedelta(days=60)
            rx_qs = BaseEventHeuristic.get_events_by_name(name=allrx_event_names)
            rx_qs = rx_qs.filter(patient=dx_event.patient)
            rx_qs = rx_qs.filter(date__gte=relevancy_begin, date__lte=relevancy_end)
            if rx_qs.values('name').distinct().count() >= 2:
                self.criteria = 'Criteria #3: dx:tuberculosis and 2 or > distinct prescription orders within 60 days either forward or backward in time'
                #
                # Patient has Tuberculosis
                #
                # TODO we are not getting the extra events for rx if we had an existing case see redmine #471
                t, new_case = self._create_case_from_event_obj(
                    condition = self.conditions[0],
                    criteria = self.criteria,
                    recurrence_interval = None, # Does not recur
                    event_obj = dx_event,
                    relevant_event_qs = rx_qs,
                    )
                counter += 1
                if t: log.info('Created new tuberculosis case def C: %s' % new_case)
        return counter

    @transaction.commit_on_success
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
        counter = 0
        counter += self.generate_def_a_b()
        counter += self.generate_def_c()
        log.debug('Generated %s new cases of tuberculosis' % counter)
        
        return counter # Count of new cases
            
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

tuberculosis_definition = Tuberculosis()

def event_heuristics():
    return tuberculosis_definition.event_heuristics

def disease_definitions():
    return [tuberculosis_definition]
