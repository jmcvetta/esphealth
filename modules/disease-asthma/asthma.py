'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Asthma Case Generator


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics http://www.commoninf.com
@contact: http://www.esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL
'''

# In most instances it is preferable to use relativedelta for date math.  
# However when date math must be included inside an ORM query, and thus will
# be converted into SQL, only timedelta is supported.
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from ESP.utils import log
from django.db import transaction
from django.db.models import F

from ESP.hef.base import Event
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic,LabResultAnyHeuristic

from ESP.hef.base import LabOrderHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case
from ESP.static.models import DrugSynonym



class Asthma(DiseaseDefinition):
    '''
    Asthma
    '''
    
    conditions = ['asthma']
    
    uri = 'urn:x-esphealth:disease:channing:asthma:v1'
    
    short_name = 'asthma'
    
    test_name_search_strings = [
        
        ]
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #
        # Diagnosis Codes
        #
        heuristic_list.append( DiagnosisHeuristic(
            name = 'asthma',
            icd9_queries = [
                Icd9Query(starts_with='493.'),
                ]
            ))
       
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Levalbuterol',
            drugs = DrugSynonym.generics_plus_synonyms(['Xopenex', ]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Pirbuterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Maxair',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Albuterol',
            drugs = DrugSynonym.generics_plus_synonyms(['AccuNeb', 'Ventolin', 'Proventil', 'ProAir', 'VoSpire', 'Airomir', 'Asmavent', 'salbutamol', ]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Arformoterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Brovana',]),
            ))    
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Formeterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Foradil', 'Perforomist', 'Oxeze',]),
            ))   
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Indacaterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Arcapta',]),
            ))   
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Salmeterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Serevent',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Beclomethasone',
            drugs =  DrugSynonym.generics_plus_synonyms(['Qvar',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Budesonide INH',
            drugs =  DrugSynonym.generics_plus_synonyms(['Pulmicort',]),
            ))
        
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Flunisolide INH',
            drugs =  DrugSynonym.generics_plus_synonyms(['Aerobid', 'Aerospan',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Fluticasone INH',
            drugs =  DrugSynonym.generics_plus_synonyms(['Flovent',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Mometasone INH',
            drugs =  DrugSynonym.generics_plus_synonyms(['Asmanex',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Montelukast',
            drugs =  DrugSynonym.generics_plus_synonyms(['Singulair',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Zafirlukast',
            drugs =  DrugSynonym.generics_plus_synonyms(['Accolate',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Zileuton',
            drugs =  DrugSynonym.generics_plus_synonyms(['Zyflo',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Ipratropium',
            drugs =  DrugSynonym.generics_plus_synonyms(['Atrovent',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Tiotropium',
            drugs =  DrugSynonym.generics_plus_synonyms(['Serevent',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Cromolyn INH',
            drugs =  DrugSynonym.generics_plus_synonyms(['Intal', 'Gastrocrom', 'Nalcrom',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Omalizumab',
            drugs =  DrugSynonym.generics_plus_synonyms(['Xolair',]),
            ))
    
        #combinations 
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Advair',#Fluticasone + Salmeterol 
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Combivent', #Albuterol + Ipratropium 
            drugs =  DrugSynonym.generics_plus_synonyms(['Duoneb',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Dulera', #Mometasone + Formoterol 
            drugs =  DrugSynonym.generics_plus_synonyms(['Zenhale',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Symbicort', #Budesonide + Formoterol 
            ))
         
               
        return heuristic_list
    
    @transaction.commit_manually
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
       
        dx_ev_names = ['dx:asthma']
        rx_ev_names = [
            'rx:Albuterol',
            'rx:Levalbuterol',
            'rx:Pirbuterol',
            'rx:Arformoterol',
            'rx:Formeterol',
            'rx:Indacaterol',
            'rx:Salmeterol',
            'rx:Beclomethasone',
            'rx:Budesonide INH',
            'rx:Ciclesonide INH',
            'rx:Flunisolide INH',
            'rx:Fluticasone INH',
            'rx:Mometasone INH',
            'rx:Montelukast',
            'rx:Zafirlukast',
            'rx:Zileuton',
            'rx:Ipratropium',
            'rx:Tiotropium',
            'rx:Cromolyn INH',
            'rx:Omalizumab',
            ]
        
        rx_comb_ev_names = [
             'rx:Advair',
             'rx:Combivent', 
             'rx:Dulera',
             'rx:Symbicort',
            ]
        
        def generate_def_a (self):
        #
        # criteria 1
        #  ≥4 encounters with ICD9 code 493.xx and asthma drug prescriptions 
        # (can be ≥2 scripts for the same med or scripts for 2 or more different meds)
        #
        
        # FIXME: This date math works on PostgreSQL; but it's not clear that 
        # the ORM will generate reasonable queries for it on other databases.
        #
        
            log.info('Generating cases for Asthma Definition (a)')
            counter = 0
            allrx_event_names =  rx_ev_names + rx_comb_ev_names
               
            dx_qs = BaseEventHeuristic.get_events_by_name(dx_ev_names)
            dx_qs = dx_qs.exclude(case__condition=self.conditions[0])
            dx_qs = dx_qs.order_by('patient', 'date') 
            for dx_event in dx_qs:            
                
                dx4_event = Event.objects.filter(name__in=dx_ev_names, patient = dx_event.patient)
                
                if dx4_event.count() >= 4:              
                    rx_qs = BaseEventHeuristic.get_events_by_name(name=allrx_event_names)
                    rx_qs = rx_qs.filter(patient=dx_event.patient)
                    
                    if rx_qs.values('name').count() >= 2:
                        #
                        # Patient has Asthma
                        #
                        t, new_case = self._create_case_from_event_obj(
                            condition = self.conditions[0],
                            criteria = 'Diagnosis >=4 with >=2 prescriptions',
                            #recurrence_interval = None, # Does not recur
                            event_obj = dx_event,
                            relevant_event_qs = rx_qs + dx4_event,
                            )
                        counter += 1
                        if t: log.info('Created new asthma case def a: %s' % new_case)
            
            return counter
        
        def generate_def_b (self):
            
            # criteria 2
            # ≥4 asthma drug dispensing events (any combination of multiple scripts
            # for the same med or scripts for different meds
             
            log.info('Generating cases for Asthma Definition (b)')
            counter = 0
            allrx_event_names =  rx_ev_names + rx_comb_ev_names
               
            mainrx_qs = BaseEventHeuristic.get_events_by_name(allrx_event_names)
            mainrx_qs = mainrx_qs.exclude(case__condition=self.conditions[0])
            mainrx_qs = mainrx_qs.order_by('patient', 'date') 
            for rx_event in mainrx_qs:            
                
                rx4_event = Event.objects.filter(name__in=allrx_event_names, patient = rx_event.patient)
                
                if rx4_event.count() >= 4:              
                    #
                    # Patient has Asthma
                    #
                    t, new_case = self._create_case_from_event_obj(
                        condition = self.conditions[0],
                        criteria = '>=4 prescriptions',
                        #recurrence_interval = None, # Does not recur
                        event_obj = rx_event,
                        relevant_event_qs = rx_qs + rx4_event,
                        )
                    counter += 1
                    if t: log.info('Created new asthma case def b: %s' % new_case)
            
            return counter # Count of new cases
    
    @transaction.commit_on_success
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
        counter = 0
        counter += self.generate_def_a()
        counter += self.generate_def_b()
        log.debug('Generated %s new cases of asthma' % counter)
        
        return counter # Count of new cases
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

asthma_definition = Asthma()

def event_heuristics():
    return asthma_definition.event_heuristics

def disease_definitions():
    return [asthma_definition]
