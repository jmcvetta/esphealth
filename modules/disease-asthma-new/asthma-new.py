'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Asthma new Case Generator


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics http://www.commoninf.com
@contact: http://www.esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL
'''

# In most instances it is preferable to use relativedelta for date math.  
# However when date math must be included inside an ORM query, and thus will
# be converted into SQL, only timedelta is supported.
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from ESP.utils import log
from django.db import transaction
from django.db.models import F

from ESP.hef.base import Event
from ESP.hef.base import PrescriptionHeuristic,BaseEventHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic,LabResultAnyHeuristic

from ESP.hef.base import LabOrderHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Dx_CodeQuery
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case
from ESP.static.models import DrugSynonym



class AsthmaNew(DiseaseDefinition):
    '''
    Asthma new
    '''
    
    conditions = ['asthma-new']
    
    uri = 'urn:x-esphealth:disease:channing:asthma-new:v1'
    
    short_name = 'asthma-new'
    
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
            dx_code_queries = [
                Dx_CodeQuery(starts_with='J45', type='icd10'),
                Dx_CodeQuery(starts_with='493.', type='icd9'),
                Dx_CodeQuery(starts_with='J46', type='icd10'),
                ]
            ))
        
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'albuterol',
            drugs = DrugSynonym.generics_plus_synonyms(['Albuterol', ]),
            exclude = ['Levalbuterol','Ipratropium'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'levalbuterol',
            drugs = DrugSynonym.generics_plus_synonyms(['Levalbuterol' ]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'pirbuterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Pirbuterol']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'arformoterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Arformoterol',]),
            ))    
        heuristic_list.append( PrescriptionHeuristic(
            name = 'formeterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Formeterol',]),
            exclude = ['Arformoterol','Mometasone','Budesonide'],
            ))   
        heuristic_list.append( PrescriptionHeuristic(
            name = 'indacaterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Indacaterol',]),
            ))   
        heuristic_list.append( PrescriptionHeuristic(
            name = 'salmeterol',
            drugs =  DrugSynonym.generics_plus_synonyms(['Salmeterol',]),
            exclude = ['Fluticasone'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'beclomethasone',
            drugs =  DrugSynonym.generics_plus_synonyms(['Beclomethasone',]),
            ))
        # test that is not going to pick up when it has both aer and inh
        heuristic_list.append( PrescriptionHeuristic(
            name = 'budesonide-inh',
            drugs =  DrugSynonym.generics_plus_synonyms(['Budesonide',]),
            qualifiers = ['INH',' NEB', 'AER'],
            exclude = ['Formeterol','Pulmicort'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'pulmicort',
            drugs =  DrugSynonym.generics_plus_synonyms(['Pulmicort',]),
            ))       
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ciclesonide-inh',
            drugs =  DrugSynonym.generics_plus_synonyms(['Ciclesonide',]),
            qualifiers = ['INH',' NEB', 'AER'],
            exclude = ['Alvesco'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'alvesco',
            drugs =  DrugSynonym.generics_plus_synonyms(['Alvesco',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'flunisolide-inh',
            drugs =  DrugSynonym.generics_plus_synonyms(['Flunisolide',]),
            qualifiers = ['INH',' NEB', 'AER'],
            exclude = ['Aerobid','Aerospan'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'aerobid',
            drugs =  DrugSynonym.generics_plus_synonyms(['Aerobid']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'fluticasone-inh',
            drugs =  DrugSynonym.generics_plus_synonyms(['Fluticasone',]),
            qualifiers = ['INH',' NEB', 'AER'],
            exclude = ['Salmeterol','Flovent']
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'flovent',
            drugs =  DrugSynonym.generics_plus_synonyms(['Flovent',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'mometasone-inh',
            drugs =  DrugSynonym.generics_plus_synonyms(['Mometasone',]),
            qualifiers = ['INH',' NEB', 'AER'],
            exclude = ['Formeterol','Asmanex'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'asmanex',
            drugs =  DrugSynonym.generics_plus_synonyms(['Asmanex',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'montelukast',
            drugs =  DrugSynonym.generics_plus_synonyms(['Montelukast',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'zafirlukast',
            drugs =  DrugSynonym.generics_plus_synonyms(['Zafirlukast',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'zileuton',
            drugs =  DrugSynonym.generics_plus_synonyms(['Zileuton',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ipratropium',
            drugs =  DrugSynonym.generics_plus_synonyms(['Ipratropium',]),
            exclude = ['Albuterol'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'tiotropium',
            drugs =  DrugSynonym.generics_plus_synonyms(['Tiotropium',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'cromolyn-inh',
            drugs =  DrugSynonym.generics_plus_synonyms(['Cromolyn',]),
            qualifiers = ['INH',' NEB', 'AER'],
            exclude = ['Intal','Gastrocrom','Nalcrom'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'intal',
            drugs =  DrugSynonym.generics_plus_synonyms(['Intal']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'omalizumab',
            drugs =  DrugSynonym.generics_plus_synonyms(['Omalizumab',]),
            ))
    
        #combinations         
        heuristic_list.append( PrescriptionHeuristic(
            name = 'fluticasone-salmeterol:generic', 
            drugs =  DrugSynonym.generics_plus_synonyms(['Fluticasone',]),
            require = ['Salmeterol','Fluticasone'],
            exclude = ['Advair']
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'fluticasone-salmeterol:trade',  
            drugs =  DrugSynonym.generics_plus_synonyms(['Advair']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'albuterol-ipratropium:generic', 
            drugs =  DrugSynonym.generics_plus_synonyms(['Albuterol',]),
            require = ['Albuterol','Ipratropium'],
            exclude = ['Combivent','Duoneb']
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'albuterol-ipratropium:trade', 
            drugs =  DrugSynonym.generics_plus_synonyms(['Combivent',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'mometasone-formeterol:generic', 
            drugs =  DrugSynonym.generics_plus_synonyms(['Mometasone',]),
            require = ['Mometasone','Formeterol'],
            exclude = ['Dulera', 'Zenhale']
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'mometasone-formeterol:trade', 
            drugs =  DrugSynonym.generics_plus_synonyms(['Dulera',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'budesonide-formeterol:generic', 
            drugs =  DrugSynonym.generics_plus_synonyms(['Budesonide',]),
            require = ['Budesonide','Formeterol'],
            exclude = ['Symbicort']
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'budesonide-formeterol:trade', 
            drugs =  DrugSynonym.generics_plus_synonyms(['Symbicort',]),
            ))        
               
        return heuristic_list
        
    def generate_def_ab (self):
    #
    # criteria 1
    # >=4 encounters with dx code 493.xx and asthma drug prescriptions 
    # (can be >=2 scripts for the same med or scripts for 2 or more different meds)
    #
       
        dx_ev_names = ['dx:asthma']
        rx_ev_names = [
            'rx:albuterol',
            'rx:levalbuterol',
            'rx:pirbuterol',
            'rx:arformoterol',
            'rx:formeterol',
            'rx:indacaterol',
            'rx:salmeterol',
            'rx:beclomethasone',
            'rx:budesonide-inh',
            'rx:pulmicort',
            'rx:ciclesonide-inh',
            'rx:alvesco',
            'rx:flunisolide-inh',
            'rx:aerobid',
            'rx:fluticasone-inh',
            'rx:flovent',
            'rx:mometasone-inh',
            'rx:asmanex',
            'rx:montelukast',
            'rx:zafirlukast',
            'rx:zileuton',
            'rx:ipratropium',
            'rx:tiotropium',
            'rx:cromolyn-inh',
            'rx:intal',
            'rx:omalizumab',
        ]
        
        rx_comb_ev_names = [
             'rx:fluticasone-salmeterol:generic',
             'rx:albuterol-ipratropium:generic', 
             'rx:mometasone-formeterol:generic',
             'rx:budesonide-formeterol:generic',
             'rx:fluticasone-salmeterol:trade',
             'rx:albuterol-ipratropium:trade', 
             'rx:mometasone-formeterol:trade',
             'rx:budesonide-formeterol:trade',
            ]
        log.info('Generating cases for Asthma Definition (a)')
        counter_a = 0
        allrx_event_names =  rx_ev_names + rx_comb_ev_names
               
        # possibly split in two sections for new and added events to existing cases 
        #or run two checks the dxs and rxs walk through the two lists.       
        dx_qs = BaseEventHeuristic.get_events_by_name(dx_ev_names)
        dx_qs = dx_qs.exclude(case__condition=self.conditions[0]).order_by('date')
        
        dx_qs_patient  = dx_qs.values('patient').distint()
        for patient in dx_qs_patient:
            dx4_event_qs = dx_qs.filter(patient = patient).count()
            if dx4_event_qs>=4:
                rx_qs = BaseEventHeuristic.get_events_by_name(name=allrx_event_names)
                rx_qs = rx_qs.exclude(case__condition=self.conditions[0]) 
                rx_qs = rx_qs.filter(patient=patient)
                if rx_qs.count() >= 2: 
                    #
                    # Patient has Asthma
                    #
                    t, new_case = self._create_case_from_event_obj(
                            condition = self.conditions[0],
                            criteria = 'Criteria #1: Asthma diagnosis >=4 and >=2 prescriptions',
                            recurrence_interval = None, # Does not recur
                            event_obj = dx4_event_qs[0],
                            relevant_event_qs = rx_qs | dx4_event_qs,
                            )
                    if t:
                        counter_a += 1
                        log.info('Created new asthma case def a: %s' % new_case)
            if (counter_a % 100)==0:
                transaction.commit() 
         
       
        # criteria 2
        # >=4 asthma drug dispensing events (any combination of multiple scripts
        # for the same med or scripts for different meds
        log.info('Generating cases for Asthma Definition (b)')
        counter_b = 0
        allrx_event_names =  rx_ev_names + rx_comb_ev_names
               
        mainrx_qs = BaseEventHeuristic.get_events_by_name(allrx_event_names)
        mainrx_qs = mainrx_qs.exclude(case__condition=self.conditions[0]).order_by('date')
        mainrx_qs_patient = mainrx_qs.values('patient').distinct()
        for patient in mainrx_qs_patient:
            rx_qs = mainrx_qs.filter(patient=patient)
            if rx_qs.count() >= 2: 
                    #
                    # Patient has Asthma
                    #
                    t, new_case = self._create_case_from_event_obj(
                            condition = self.conditions[0],
                            criteria = 'Criteria #2: >=4 prescriptions',
                            recurrence_interval = None, # Does not recur
                            event_obj = dx4_event_qs[0],
                            relevant_event_qs = rx_qs | dx4_event_qs,
                            )
            if t:
                counter_b += 1
                log.info('Created new asthma case def b: %s' % new_case)
            if (counter_b % 100)==0:
                    transaction.commit()   
         
                     
        return counter_a + counter_b # Count of new cases
    
    @transaction.commit_manually
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
        counter = 0
        counter += self.generate_def_ab()
        transaction.commit()
        log.debug('Generated %s new cases of asthma' % counter)
        
        return counter # Count of new cases
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------


def event_heuristics():
    return AsthmaNew().event_heuristics

def disease_definitions():
    return [AsthmaNew()]
