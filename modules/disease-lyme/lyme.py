'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Lyme Case Generator


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

from django.db import transaction
from django.db.models import F

from ESP.utils import log
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



class Lyme(DiseaseDefinition):
    '''
    Lyme
    '''
    
    conditions = ['lyme']
    
    uri = 'urn:x-esphealth:disease:channing:lyme:v1'
    
    short_name = 'lyme'
    
    test_name_search_strings = [
	    'lyme',
	    'burg',
        'borr',
	    ]
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #
        # Diagnosis Codes
        #
        heuristic_list.append( DiagnosisHeuristic(
            name = 'lyme',
            icd9_queries = [
                Icd9Query(starts_with='088.81'),
                ]
            ))
        heuristic_list.append( DiagnosisHeuristic(
            name = 'rash',
            icd9_queries = [
                Icd9Query(starts_with='782.1'),
                ]
            ))
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'doxycycline',
            drugs = DrugSynonym.generics_plus_synonyms(['doxycycline', ]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'lyme_other_antibiotics',
            drugs =  DrugSynonym.generics_plus_synonyms(['Amoxicillin','Cefuroxime', 'Ceftriaxone', 'Cefotaxime',]),
            ))
        
        #
        # Lab Results
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_elisa',
             ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_igg_eia',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_igm_eia',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_igg_wb',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_igm_wb',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_pcr',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_pcr_csf',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'lyme_ab_csf',
            ))
        
        #
        # Lab order/any result
        #
        for test_name in [
            'lyme_elisa',
            'lyme_igg_eia',
            'lyme_igm_eia',
            ]:
            heuristic_list.append( LabResultAnyHeuristic(
                test_name = test_name,
                date_field = 'order',
                ) )
        
        
        return heuristic_list
    
    @transaction.commit_manually
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
       
        #
        # Criteria Set #1 condition 3 in spec
        # diagnosis and meds within 14 days
        # 
        dx_ev_names = ['dx:lyme']
        rx_ev_names = [
            'rx:doxycycline',
            'rx:lyme_other_antibiotics',
            ]
        #
        # FIXME: This date math works on PostgreSQL; but it's not clear that 
        # the ORM will generate reasonable queries for it on other databases.
        #
        dxrx_event_qs = Event.objects.filter(
            name__in = dx_ev_names,
            patient__event__name__in = rx_ev_names,
            patient__event__date__gte = (F('date') - 14 ),
            patient__event__date__lte = (F('date') + 14 ),
            )
        
        # Criteria #2 condition 2 in spec 
        # wb test positive or pcr
        # 
        lx_ev_names = [ 
            'lx:lyme_pcr:positive',
            'lx:lyme_pcr_csf:positive',
            'lx:lyme_ab_csf:positive',
            'lx:lyme_igg_wb:positive',
            'lx:lyme_igm_wb:positive',  ]
        
        lx_event_qs = Event.objects.filter(
            name__in =  lx_ev_names,
            )
        #
        # Criteria Set #3 condition 1 from spec
        # (Lyme ELISA or IGM EIA or IGG EIA) and (Lyme ICD9 or Lyme Antibiotics) w/in 30 days
        #
        rpr_ev_names = dx_ev_names + rx_ev_names
            
        ig_ev_names = [   
            'lx:lyme_elisa:positive',
            'lx:lyme_igg_eia:positive',
            'lx:lyme_igm_eia:positive',]
        
        test_event_qs = Event.objects.filter(
            name__in = rpr_ev_names,  
            patient__event__name__in = ig_ev_names,
            patient__event__date__gte = (F('date') - 30 ),
            patient__event__date__lte = (F('date') + 30 ),  
            )
        #
        # Criteria Set #4 (lyme condition 4 from spec)
        # Rash and doxycycline and (order for Lyme ELISA or IGM EIA or IGG EIA) within 30d
        #
        rash_ev_names = ['dx:rash']
        rash_rx_ev_names = ['rx:doxycycline']
        rash_lx_ev_names = ['lx:lyme_elisa:any-result','lx:lyme_igg_eia:any-result', 'lx:lyme_igm_eia:any-result',]
        
        rash_qs = Event.objects.filter(
            name__in = rash_ev_names,
            patient__event__name__in = rash_rx_ev_names,
            patient__event__date__gte = (F('date') - 30 ),
            patient__event__date__lte = (F('date') + 30 ),
            ).filter(
	            patient__event__name__in = rash_lx_ev_names,
	            patient__event__date__gte = (F('date') - 30 ),
	            patient__event__date__lte = (F('date') + 30 ),
            )
        #
        # Combined Criteria
        #
        combined_criteria_qs = dxrx_event_qs | lx_event_qs | test_event_qs | rash_qs 
        combined_criteria_qs = combined_criteria_qs.exclude(case__condition='lyme')
        #ordering by patient to commit after processing every patient 
        combined_criteria_qs = combined_criteria_qs.distinct().order_by('patient','date')
        
        
        all_event_names = dx_ev_names + lx_ev_names + rx_ev_names + rpr_ev_names + ig_ev_names + rash_ev_names + rash_rx_ev_names + rash_lx_ev_names
        counter = 0
        
        previous_patient_id = None
        for this_event in combined_criteria_qs:
            current_patient = this_event.patient
            # Setting up transaction control so that changes are committed only at patient boundaries.
            if previous_patient_id and current_patient.id != previous_patient_id:
                transaction.commit()
            previous_patient_id = current_patient.id
            
            existing_cases = Case.objects.filter(
                condition='lyme', 
                patient=this_event.patient,
                date__gte=(this_event.date - relativedelta(days=365)) # Adds recurrence interval
                )
            existing_cases = existing_cases.order_by('date')
            if existing_cases:
                old_case = existing_cases[0]
                old_case.events.add(this_event)
                old_case.save()
                log.debug('Added %s to %s' % (this_event, old_case))
                continue # Done with this event, continue loop
            # No existing case, so we create a new case
            new_case = Case(
                condition = 'lyme',
                patient = this_event.patient,
                provider = this_event.provider,
                date = this_event.date,
                criteria = 'combined lyme criteria',
                source = self.uri,
                )
            new_case.save()
            new_case.events.add(this_event)
            all_relevant_events = Event.objects.filter(patient=this_event.patient, name__in=all_event_names)
            for related_event in all_relevant_events:
                new_case.events.add(related_event)
            new_case.save()
            log.info('Created new lyme case: %s' % new_case)
            counter += 1
        transaction.commit()
        
        log.debug('Generated %s new cases of lyme' % counter)
        
        return counter # Count of new cases
    

#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

lyme_definition = Lyme()

def event_heuristics():
    return lyme_definition.event_heuristics

def disease_definitions():
    return [lyme_definition]
