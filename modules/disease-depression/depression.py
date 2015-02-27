'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Depression Case Generator


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics http://www.commoninf.com
@contact: http://www.esphealth.org
@copyright: (c) 2015 
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



class Depression(DiseaseDefinition):
    '''
    Depression
    '''
    
    conditions = ['depression']
    
    uri = 'urn:x-esphealth:disease:channing:depression:v1'
    
    short_name = 'depression'
    
    test_name_search_strings = [
        
        ]
    
    timespan_heuristics = []
    
    recurrence_interval = 365 # episode length 1 year
    
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #

        # Diagnosis Codes
        #
        heuristic_list.append( DiagnosisHeuristic(
            name = 'depression',
            dx_code_queries = [
                Dx_CodeQuery(starts_with='296.2', type='icd9'),
                Dx_CodeQuery(starts_with='296.3', type='icd9'),
                Dx_CodeQuery(starts_with='300.4', type='icd9'),
                Dx_CodeQuery(starts_with='308.0', type='icd9'),
                Dx_CodeQuery(starts_with='309.0', type='icd9'),
                Dx_CodeQuery(starts_with='309.1', type='icd9'), 
                Dx_CodeQuery(starts_with='309.28', type='icd9'),
                Dx_CodeQuery(starts_with='311', type='icd9'),
                Dx_CodeQuery(starts_with='V79.0', type='icd9'),
                Dx_CodeQuery(starts_with='F32.', type='icd10'), 
                Dx_CodeQuery(starts_with='F33.', type='icd10'), 
                Dx_CodeQuery(starts_with='F34.1', type='icd10'),
                Dx_CodeQuery(starts_with='F43.21', type='icd10'),
                Dx_CodeQuery(starts_with='F43.23', type='icd10'),
                Dx_CodeQuery(starts_with='F06.31', type='icd10'),
                Dx_CodeQuery(starts_with='F06.32', type='icd10'),
                
                ]
            ))
        
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'amitryptyline',
            drugs = DrugSynonym.generics_plus_synonyms(['Amitryptyline', ]),
            ))
                
        heuristic_list.append( PrescriptionHeuristic(
            name = 'clomipramine',
            drugs = DrugSynonym.generics_plus_synonyms(['Clomipramine' ]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'desipramine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Desipramine']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'doxepin',
            drugs =  DrugSynonym.generics_plus_synonyms(['Doxepin',]),
            ))    
        heuristic_list.append( PrescriptionHeuristic(
            name = 'imipramine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Imipramine',]),
            ))   
        heuristic_list.append( PrescriptionHeuristic(
            name = 'nortriptyline',
            drugs =  DrugSynonym.generics_plus_synonyms(['Nortriptyline',]),
            ))   
           
        heuristic_list.append( PrescriptionHeuristic(
            name = 'protriptyline',
            drugs =  DrugSynonym.generics_plus_synonyms(['Protriptyline',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'isocarboxazid',
            drugs =  DrugSynonym.generics_plus_synonyms(['Isocarboxazid',]),
            ))       
        heuristic_list.append( PrescriptionHeuristic(
            name = 'phenelzine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Phenelzine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'selegiline',
            drugs =  DrugSynonym.generics_plus_synonyms(['Selegiline',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'tranylcypromine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Tranylcypromine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'citalopram',
            drugs =  DrugSynonym.generics_plus_synonyms(['Citalopram']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'escitalopram',
            drugs =  DrugSynonym.generics_plus_synonyms(['Escitalopram',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'fluoxetine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Fluoxetine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'fluvoxamine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Fluvoxamine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'paroxetine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Paroxetine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'sertraline',
            drugs =  DrugSynonym.generics_plus_synonyms(['Sertraline',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'desvenlafaxine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Desvenlafaxine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'duloxetine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Duloxetine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'venlafaxine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Venlafaxine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'bupropion',
            drugs =  DrugSynonym.generics_plus_synonyms(['Bupropion',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'mirtazapine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Mirtazapine',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'trazodone',
            drugs =  DrugSynonym.generics_plus_synonyms(['Trazodone']),
            ))
    
        
        return heuristic_list
        
    def generate_def_a (self):
    #
    # criteria 1
    #
       
        dx_ev_names = ['dx:depression']
        rx_ev_names = [
            'rx:amitryptyline',
            'rx:clomipramine',
            'rx:desipramine',
            'rx:doxepin',
            'rx:imipramine',
            'rx:nortriptyline',
            'rx:protriptyline',
            'rx:isocarboxazid',
            'rx:phenelzine',
            'rx:selegiline',
            'rx:tranylcypromine',
            'rx:citalopram',
            'rx:escitalopram',
            'rx:fluoxetine',
            'rx:fluvoxamine',
            'rx:paroxetine',
            'rx:sertraline',
            'rx:desvenlafaxine',
            'rx:duloxetine',
            'rx:venlafaxine',
            'rx:bupropion',
            'rx:mirtazapine',
            'rx:trazodone',
        ]
        
        
        log.info('Generating cases for Depression')
               
        # criteria 1
        #  depression drug dispensing events and diagnosis code for depression
        log.info('Generating cases for Depression Definition ')
        all_event_names =  dx_ev_names + rx_ev_names
               
        #
        # FIXME: This date math works on PostgreSQL; but it's not clear that 
        # the ORM will generate reasonable queries for it on other databases.
        #
        dxrx_event_qs = Event.objects.filter(
            name__in = dx_ev_names,
            patient__event__name__in = rx_ev_names,
            patient__event__date__gte = (F('date') - 60 ),
            patient__event__date__lte = (F('date') + 60 ),
            )
        
        if dxrx_event_qs:
            self.criteria =  'Criteria #1 depression dx code and prescription for antidepressant within 60 days'
         
        dxrx_event_qs = dxrx_event_qs.exclude(case__condition='depression')
        # ordering here doesnt matter because create cases from event sorts again
        dxrx_event_qs = dxrx_event_qs.order_by('date')
        
        new_case_count = self._create_cases_from_event_qs(
            condition = 'depression',
            criteria = self.criteria, 
            recurrence_interval = self.recurrence_interval, 
            event_qs = dxrx_event_qs, 
            relevant_event_names = all_event_names,
            )
        
        log.debug('Generated %s new cases of depression' % new_case_count)       
        return new_case_count # Count of new cases
    
    @transaction.commit_manually
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
        counter = 0
        counter += self.generate_def_a()
        transaction.commit()
        log.debug('Generated %s new cases of depression' % counter)
        
        return counter # Count of new cases
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

depression_definition = Depression()

def event_heuristics():
    return depression_definition.event_heuristics

def disease_definitions():
    return [depression_definition]
