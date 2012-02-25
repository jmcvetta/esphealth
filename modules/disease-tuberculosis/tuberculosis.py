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
from ESP.hef.base import Event
from ESP.hef.base import BaseEventHeuristic
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.hef.base import LabOrderHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case


class Tuberculosis(DiseaseDefinition):
    '''
    Tuberculosis
    '''
    
    conditions = ['tuberculosis']
    
    uri = 'urn:x-esphealth:disease:commoninf:tuberculosis:v1'
    
    short_name = 'tuberculosis'
    
    test_name_search_strings = ['tuber','afb','mycob',]
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #
        # Diagnosis Codes
        # 010.00-018.99
        heuristic_list.append( DiagnosisHeuristic(
            name = 'tuberculosis',
            icd9_queries = [
                Icd9Query(starts_with='010.'),
                Icd9Query(starts_with='011.'),
                Icd9Query(starts_with='012.'),
                Icd9Query(starts_with='013.'),
                Icd9Query(starts_with='014.'),
                Icd9Query(starts_with='015.'),
                Icd9Query(starts_with='016.'),
                Icd9Query(starts_with='017.'),
                Icd9Query(starts_with='018.'),
                ]
            ))
        #
        # Lab Orders
        #
        heuristic_list.append( LabOrderHeuristic(
            test_name = 'tuberculosis_pcr',
            ))
        heuristic_list.append( LabOrderHeuristic(
            test_name = 'tuberculosis_afb',
            ))
        heuristic_list.append( LabOrderHeuristic(
            test_name = 'tuberculosis_mycob',
            ))
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'pyrazinamide',
            drugs = [ 'pyrazinamide', 'PZA',],
            exclude = 'CAPZA', 
            ))
        
        heuristic_list.append( PrescriptionHeuristic(
            name = 'moxifloxacin',
            drugs = ['moxifloxacin',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ethambutol',
            drugs = ['ethambutol',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'rifampin',
            drugs = ['rifampin',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'rifabutin',
            drugs = ['rifabutin',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'rifapentine',
            drugs = ['rifapentine',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'streptomycin',
            drugs = ['streptomycin',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'para_aminosalicyclic_acid',
            drugs = ['para_aminosalicyclic_acid',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'kanamycin',
            drugs = ['kanamycin',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'capreomycin',
            drugs = ['capreomycin',],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'cycloserine',
            drugs = ['cycloserine',],
            ))
        # TODO define each
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ethionamide',
            drugs = ['ethionamide',],
            ))
        
        heuristic_list.append( PrescriptionHeuristic(
            name = 'isoniazid',
            drugs = [ 'Isoniazid','INH',],
            exclude = 'INHAL, INHIB', 
            ))
        
        return heuristic_list
    
    def generate_def_c(self):
        log.info('Generating cases for Tuberculosis Definition (C)')
        counter = 0
        rx_event_names =  ['rx:rifabutin','rx:capreomycin','rx:ethionamide','rx:isoniazid','rx:pyrazinamide']
        dx_qs = BaseEventHeuristic.get_events_by_name('dx:tuberculosis')
        dx_qs = dx_qs.exclude(case__condition=self.conditions[0])
        dx_qs = dx_qs.order_by('patient', 'date') 
        for dx_event in dx_qs:
            relevancy_begin = dx_event.date - relativedelta(days=60)
            relevancy_end = dx_event.date + relativedelta(days=60)
            rx_qs = BaseEventHeuristic.get_events_by_name(name=rx_event_names)
            rx_qs = rx_qs.filter(patient=dx_event.patient)
            rx_qs = rx_qs.filter(date__gte=relevancy_begin, date__lte=relevancy_end)
            if rx_qs.values('name').distinct().count() >= 2:
                #
                # Patient has Tuberculosis
                #
                self._create_case_from_event_obj(
                    condition = self.conditions[0],
                    criteria = 'Diagnosis with >=2 prescriptions',
                    recurrence_interval = None, # Does not recur
                    event_obj = dx_event,
                    relevant_event_qs = rx_qs,
                    )
                counter += 1
        return counter

        
        
    @transaction.commit_on_success
    def generate(self):
        
        #
        # Criteria Set #1 (single rx) 
        #
        rx_ev_names = ['rx:pyrazinamide']
        
        rx_event_qs = Event.objects.filter(
            name__in = rx_ev_names,
            )
        #
        # Criteria Set #2 (dx or lab order  prior 14 days or 60 after icd9 code) 
        #
        dx_ev_names = ['dx:tuberculosis']
        lx_ev_names = ['lx:tuberculosis_prc:order','lx:tuberculosis_mycob:order','lx:tuberculosis_afb:order'] 
                
        dxlx_event_qs = Event.objects.filter(
            name__in = dx_ev_names,
            patient__event__name__in =  lx_ev_names,
            patient__event__date__gte = (F('date') - 60 ),
            patient__event__date__lte = (F('date') + 14 ),
            )
        #
        # Criteria Set #3 dx and 2 distinct prescription orders
        #  
        rxall_ev_names =  ['rx:rifabutin','rx:capreomycin','rx:ethionamide','rx:isoniazid','rx:pyrazinamide' ]
        #  count of 2 or more of each rx
        #  get list of pt for each list of meds and 
        # get the count of events for each distinct patients.
        dx_qs = BaseEv
        potential_patient_qs = Patient.objects.filter(event__name='dx:tuberculosis')
        rx_event_qs = Event.objects.filter(name=rxall_ev_names)
        rx_event_qs = rx_event_qs.filter(patient__in=potential_patient_qs)
        rx_event_qs = rx_event_qs.exclude(case__condition='tuberculosis')
        rx_event_qs = rx_event_qs.order_by('patient', 'date')
        for rx_event in rx_event_qs:
            pass
        #twice_vqs = twice_qs.annotate(count=Count('patient'))
        #twice_vqs = twice_vqs.filter(count__gte=2)
        #twice_patients = twice_vqs.values_list('patient')
        
        dxrx_event_qs = Event.objects.filter(
            name__in = dx_ev_names,
            patient__in=twice_patients,
            patient__event__name__in =  rxall_ev_names,
            patient__event__date__gte = (F('date') - 60 ),
            patient__event__date__lte = (F('date') + 60 ),
            )
            
        #
        # Combined Criteria
        #
        combined_criteria_qs = rx_event_qs | dxlx_event_qs | dxrx_event_qs  
        combined_criteria_qs = combined_criteria_qs.exclude(case__condition='tuberculosis')
        combined_criteria_qs = combined_criteria_qs.order_by('date')
        all_event_names = rx_ev_names + dx_ev_names + lx_ev_names + rxall_ev_names
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
                criteria = 'combined tuberculosis criteria',
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
