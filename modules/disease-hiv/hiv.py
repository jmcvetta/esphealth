'''
                                  ESP Health
                         Notifiable Diseases Framework
                           HIV Case Generator


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
from ESP.utils import overlap
from django.db import transaction
from django.db.models import F

from ESP.hef.base import Event
from ESP.hef.base import PrescriptionHeuristic,BaseEventHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic,LabResultAnyHeuristic,LabResultFixedThresholdHeuristic

from ESP.hef.base import LabOrderHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Dx_CodeQuery
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case
from ESP.static.models import DrugSynonym
from decimal import Decimal


class HIV(DiseaseDefinition):
    '''
    HIV
    '''
    
    conditions = ['hiv']
    
    uri = 'urn:x-esphealth:disease:channing:hiv:v1'
    
    short_name = 'hiv'
    
    test_name_search_strings = [
        'hiv',
        'immuno',
        'cd4'
        ]
    
    timespan_heuristics = []
    
    #recurrence_interval = 360 #TODO episode length  1 year
    
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #

        # Diagnosis Codes
        #
        '''
        heuristic_list.append( DiagnosisHeuristic(
            name = 'hiv',
            dx_code_queries = [
                Dx_CodeQuery(starts_with='042', type='icd9'),
                Dx_CodeQuery(starts_with='V08', type='icd9'),
                Dx_CodeQuery(starts_with='B20', type='icd10'),
                Dx_CodeQuery(starts_with='B21', type='icd10'),
                Dx_CodeQuery(starts_with='B22', type='icd10'),
                Dx_CodeQuery(starts_with='B23', type='icd10'),
                Dx_CodeQuery(starts_with='B24', type='icd10'),
                Dx_CodeQuery(starts_with='Z21', type='icd10'),
                Dx_CodeQuery(starts_with='098.7', type='icd10'),
                
                ]
            ))
        #opportunistic infection
        heuristic_list.append( DiagnosisHeuristic(
            name = 'op-infection',
            dx_code_queries = [
                Dx_CodeQuery(starts_with='136.3', type='icd9'),
                Dx_CodeQuery(starts_with='130', type='icd9'),
                Dx_CodeQuery(starts_with='B59', type='icd10'),
                Dx_CodeQuery(starts_with='B58', type='icd10'),
                Dx_CodeQuery(starts_with='117.5', type='icd9'),
                Dx_CodeQuery(starts_with='321.0', type='icd9'),
                Dx_CodeQuery(starts_with='B45.0', type='icd10'),
                Dx_CodeQuery(starts_with='B45.1', type='icd10'),
                Dx_CodeQuery(starts_with='B45.7', type='icd10'),
                Dx_CodeQuery(starts_with='B45.9', type='icd10'),
                Dx_CodeQuery(starts_with='007.4', type='icd9'),
                Dx_CodeQuery(starts_with='A07.2', type='icd10'),
                Dx_CodeQuery(starts_with='010', type='icd9'),
                Dx_CodeQuery(starts_with='011', type='icd9'),
                Dx_CodeQuery(starts_with='012', type='icd9'),
                Dx_CodeQuery(starts_with='013', type='icd9'),
                Dx_CodeQuery(starts_with='014', type='icd9'),
                Dx_CodeQuery(starts_with='015', type='icd9'),
                Dx_CodeQuery(starts_with='016', type='icd9'),
                Dx_CodeQuery(starts_with='017', type='icd9'),
                Dx_CodeQuery(starts_with='018', type='icd9'),
                Dx_CodeQuery(starts_with='A15', type='icd10'),
                Dx_CodeQuery(starts_with='A16', type='icd10'),
                Dx_CodeQuery(starts_with='A17', type='icd10'),
                Dx_CodeQuery(starts_with='A18', type='icd10'),
                Dx_CodeQuery(starts_with='A19', type='icd10'),
                Dx_CodeQuery(starts_with='112', type='icd9'),
                Dx_CodeQuery(starts_with='B37', type='icd10'),
                Dx_CodeQuery(starts_with='031.2', type='icd9'),
                Dx_CodeQuery(starts_with='A31.2', type='icd10'),
                Dx_CodeQuery(starts_with='046.3', type='icd9'),
                Dx_CodeQuery(starts_with='A81.2', type='icd10'),
                ]
            ))
        '''
        #
        # Lab Results
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hiv_elisa',
             ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hiv_ag_ab',
             ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hiv_pcr',
             ))
        heuristic_list.append( LabResultPositiveHeuristic( 
            test_name = 'hiv_wb',
            
            ))
        # TODO fix this lab
        heuristic_list.append( LabResultPositiveHeuristic( 
            test_name = 'hiv_rna_viral',
            
            ))
        
        #
        # Threshold Tests ??? or positive negative code something special given the comments below
        #
        for test_name, match_type, threshold in [
                       
            # the lower limit of detection varies depending on which generation test is being used. 
            # Historically it used to be 400 copies/ml. More recently it's 48 or 40 copies/ml.
            #What I think we want to do is assess whether the tests have a normal range associated 
            #with them or not.  If not, then would generate lists of the unique results from each test
            # for review.  Most of the viral loads I see are reported as "<XX copies per ml" or 
            #"below the limit of detection" or something to that effect.
            # If we confirm that this is the convention with Mass League as well then we'd simply say
            #that any numeric result without a preceding "<" is positive. ???
            ('hiv_rna_viral', 'gte', 400), 
            ('hiv_rna_viral', 'gte', 40),
            ('hiv_rna_viral', 'gte', 48),
            ]:
            h = LabResultFixedThresholdHeuristic(
                test_name = 'hiv_rna_viral',
                match_type = match_type,
                threshold = Decimal(str(threshold)),
                )
            heuristic_list.append(h)
       
        #
        # Prescriptions
        #
        
        heuristic_list.append( PrescriptionHeuristic(
            name = 'zidovudine',
            drugs = DrugSynonym.generics_plus_synonyms(['Zidovudine ','Retrovir' ]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'didanosine',
            drugs = DrugSynonym.generics_plus_synonyms(['Didanosine','Videx' ]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'stavudine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Stavudine']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Lamivudine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Lamivudine','Epivir']),
            ))    
        heuristic_list.append( PrescriptionHeuristic(
            name = 'emtricitabine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Emtricitabine','Emtriva']),
            ))   
        heuristic_list.append( PrescriptionHeuristic(
            name = 'tenofovir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Tenofovir','Viread']),
            ))   
           
        heuristic_list.append( PrescriptionHeuristic(
            name = 'abacavir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Abacavir','Ziagen']),
            ))
        
        heuristic_list.append( PrescriptionHeuristic(
            name = 'afavirenz',
            drugs =  DrugSynonym.generics_plus_synonyms(['Efavirenz','Sustiva']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'nivarapine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Nivarapine','Viramune']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'rilpivirine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Rilpivirine','Edurant']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'etravirine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Etravirine','Intelence']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'delavirdine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Delavirdine','Rescriptor']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'raltegravir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Raltegravir','Isentress']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'dolutegravir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Dolutegravir','Tivicay']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'elvitegravir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Elvitegravir',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'enfuvirtide',
            drugs =  DrugSynonym.generics_plus_synonyms(['Enfuvirtide','Fuzeon']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'maraviroc',
            drugs =  DrugSynonym.generics_plus_synonyms(['Maraviroc','Selzentry']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'tipranavir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Tipranavir','Aptivus']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ritonavir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Ritonavir','Norvir']),
            ))
    
        heuristic_list.append( PrescriptionHeuristic(
                name = 'indinavir',
                drugs =  DrugSynonym.generics_plus_synonyms(['Indinavir','Crixivan']),
                ))
        heuristic_list.append( PrescriptionHeuristic(
                name = 'darunavir',
                drugs =  DrugSynonym.generics_plus_synonyms(['Darunavir','Prezista']),
                ))
        heuristic_list.append( PrescriptionHeuristic(
                name = 'saquinavir',
                drugs =  DrugSynonym.generics_plus_synonyms(['Saquinavir','Invirase']),
                ))
        heuristic_list.append( PrescriptionHeuristic(
                name = 'atazanavir',
                drugs =  DrugSynonym.generics_plus_synonyms(['Atazanavir','Reyataz']),
                ))
        heuristic_list.append( PrescriptionHeuristic(
                name = 'nelfinavir',
                drugs =  DrugSynonym.generics_plus_synonyms(['Nelfinavir','Viracept']),
                ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Fosamprenavir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Fosamprenavir','Lexiva']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Fosamprenavir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Fosamprenavir','Lexiva']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'Fosamprenavir',
            drugs =  DrugSynonym.generics_plus_synonyms(['Fosamprenavir','Lexiva']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'pyrimethamine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Pyrimethamine','Daraprim']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'atovaquone',
            drugs =  DrugSynonym.generics_plus_synonyms(['Atovaquone','Mepron']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'pentamidine',
            drugs =  DrugSynonym.generics_plus_synonyms(['Pentamidine','Nebupent','Pentam 300']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'tmp-smx',
            drugs =  DrugSynonym.generics_plus_synonyms(['TMP-SMX','Bactrim']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'dapsone',
            drugs =  DrugSynonym.generics_plus_synonyms(['Dapsone']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'azithromycin',
            drugs =  DrugSynonym.generics_plus_synonyms(['Azithromycin','Zithromax','Zmax']),
            ))
         # count 2
        heuristic_list.append( PrescriptionHeuristic(
            name = 'tenofovir-emtricitabine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Truvada']),
            #require = ['Tenofovir','Emtricitabine'],
            ))       
        heuristic_list.append( PrescriptionHeuristic(
            name = 'zidovudine-jamivudine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Combivir',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'abacavir-lamivudine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Epzicom',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'lopinavir-ritonavir:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Kaletra',]),
            ))
         
         #count 3 
        heuristic_list.append( PrescriptionHeuristic(
            name = 'abacavir-lamivudine-zidovudine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Trizivir',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'efavirenz-tenofovir-emtricitabine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Atripla',]),
            ))
       
        heuristic_list.append( PrescriptionHeuristic(
            name = 'rilpivirine-tenofovir-emtricitabine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Complera',]),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'dolutegravir-abacavir-lamivudine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Triumeq',]),
            ))
        #count 4
        heuristic_list.append( PrescriptionHeuristic(
            name = 'elvitegravir-cobicistat-tenofovir-emtricitabine:trade',
            drugs =  DrugSynonym.generics_plus_synonyms(['Stribild',]),
            ))
        
        return heuristic_list
        
    def generate_def_ab (self):
    #
    # criteria 2
    #  concurrent prescription 3 or more for 3 months and negative viral load, 
    # exclude patients with hep b and receiving pre por post exposure prophylaxis
    # 
       
        #dx_ev_names = ['dx:hiv','op-infection']
        rx2_ev_names = [
            'rx:lopinavir-ritonavir',
            'rx:abacavir-lamivudine',
            'rx:zidovudine-lamivudine',
            'rx:tenofovir-emtricitabine',
            ]
        rx3_4_ev_names = [
            'rx:abacavir-lamivudine-zidovudine',
            'rx:efavirenz-tenofovir-emtricitabine',
            'rx:rilpivirine-tenofovir-emtricitabine',
            'rx:dolutegravir-abacavir-lamivudine ',
            'rx:elvitegravir-cobicistat-tenofovir-emtricitabine',
            ]
        rx1_ev_names = [
            'rx:zidovudine',
            'rx:didanosine',
            'rx:stavudine',
            'rx:lamivudine',
            'rx:emtricitabine',
            'rx:tenofovir',
            'rx:abacavir',
            'rx:efavirenz',
            'rx:nivarapine',
            'rx:rilpivirine',
            'rx:etravirine',
            'rx:delavirdine',
            'rx:raltegravir',
            'rx:dolutegravir',
            'rx:elvitegravir',
            'rx:enfuvirtide',
            'rx:maraviroc',
            'rx:tipranavir',
            'rx:ritonavir',
            'rx:indinavir',
            'rx:darunavir',
            'rx:saquinavir',
            'rx:atazanavir',
            'rx:nelfinavir',
            'rx:fosamprenavir',
            'rx:tmp-smx',
            'rx:dapsone',
            'rx:pyrimethamine',
            'rx:atovaquone',
            'rx:pentamidine',
            'rx:azithromycin',
        ]
        
        lx_ev_names = ['lx:hiv_wb:positive', 
                       'lx:hiv_pcr:positive', 
                       'lx:hiv_rna_viral:positive',
                       'lx:hiv_rna_viral:threshold:gte:400',
                       'lx:hiv_rna_viral:threshold:gte:40',
                       'lx:hiv_rna_viral:threshold:gte:48', ] 
        
        lx_ev_comb_names = [
                       'lx:hiv_elisa:positive', 
                       'lx:hiv_ag_ab:positive', 
                            ]
        
        log.info('Generating cases for HIV')
               
        # criteria 1
        #  positive western blot or  hiv rn viral> lower lim or pos hiv cualitative pcr 
        log.info('Generating cases for HIV Definition (a), (c), (d)')
        counter_a = 0
               
        #
        # FIXME: This date math works on PostgreSQL; but it's not clear that 
        # the ORM will generate reasonable queries for it on other databases.
        #
        lx_event_qs = Event.objects.filter(
            name__in = lx_ev_names,
            ).exclude(case__condition=self.conditions[0]).order_by('date').select_related()
        
        lx_patients = set()
        for event in lx_event_qs:
            lx_patients.add(event.patient)
        
        lx_patient_events = {}
        for event in lx_event_qs:
            try:
                lx_patient_events[event.patient_id].append(event)
            except:
                lx_patient_events[event.patient_id] = [event]
                 
        
        patients_with_existing_cases = self.process_existing_cases(lx_patients,None,lx_patient_events)
        
        if lx_event_qs:
            self.criteria =  'Criteria 1. #a #c #d pos western blot or hiv viral load > lower limit or pos hiv qualt pcr'
        
        for patient in lx_patients - set(patients_with_existing_cases): 
            t, new_case = self._create_case_from_event_list(
                            condition = self.conditions[0],
                            criteria = self.criteria,
                            recurrence_interval = None, # Does not recur
                            event_obj = lx_patient_events[patient.id][0],
                            relevant_event_names = lx_patient_events[patient.id],
                            )
            if t:
                counter_a += 1
                log.info('Created new hiv case def a,c,d : %s' % new_case)
            if (counter_a % 100)==0:
                    transaction.commit() 
        
        #criteria 2
        # (pos hiv antigen/antibody and pos hiv elisa)
        lxcomb_event_qs = Event.objects.filter(
            name__in = 'lx:hiv_ag_ab:positive',
            patient__event__name__in = 'lx:hiv_elisa:positive', 
            ).exclude(case__condition=self.conditions[0]).order_by('date').select_related()
        
        lxcomb_patients = set()
        for event in lxcomb_event_qs:
            lxcomb_patients.add(event.patient)
        
        lxcomb_patient_events =  {}
        for event in lxcomb_event_qs:
            try:
                lxcomb_patient_events[event.patient_id].append(event)
            except:
                lxcomb_patient_events[event.patient_id] = [event]
                      
        log.info('Generating cases for HIV definition (b)')
        counter_b = 0
        
        patients_with_existing_cases = self.process_existing_cases(lxcomb_patients,None,lxcomb_patient_events)
        
        
        if lxcomb_event_qs:
            self.criteria =  'Criteria 2. pos hiv elisa and pos hiv antigen/antibody'
        
        for patient in lxcomb_patients - set(patients_with_existing_cases): 
            t, new_case = self._create_case_from_event_list(
                            condition = self.conditions[0],
                            criteria = self.criteria,
                            recurrence_interval = None, # Does not recur
                            event_obj = lxcomb_patient_events[patient.id][0],
                            relevant_event_names = lxcomb_patient_events[patient.id],
                            )
            if t:
                counter_b += 1
                log.info('Created new hiv  new case def b: %s' % new_case)
            if (counter_b % 100)==0:
                    transaction.commit() 
        
        #criteria 3
        #c.    Concurrent prescriptions for 3 or more antiretrovirals for at least 3 months
        # meds to count multiple if combo + 2 or 3 or 4, 
        #  and  with negative viral load, and exclude pre-post exposure prophylaxis?? 
        
        rx_event_qs = BaseEventHeuristic.get_events_by_name(name=rx1_ev_names + rx2_ev_names + rx3_4_ev_names).exclude(case__condition=self.conditions[0]).select_related()
        '''rx_event_qs = Event.objects.filter( 
            name__in = rx1_ev_names + rx2_ev_names + rx3_4_ev_names, 
            #patient__event__name__in = 'lx:hiv_rna_viral:negative', TODO not needed?
            # exclude hep 
            ).exclude(case__condition = self.conditions[0]).order_by('date').select_related()
        '''
        # distinct patients
        rx_patients = set()
        for event in rx_event_qs:
            rx_patients.add(event.patient)
        
        rx_patient_events = {}
        for event in rx_event_qs:
            try:
                rx_patient_events[event.patient_id].append(event)
            except:
                rx_patient_events[event.patient_id] = [event]
                
        log.info('Generating cases for HIV new Definition (c)')
        counter_c = 0
                
        patients_with_existing_cases = self.process_existing_cases(rx_patients,None,rx_patient_events)
        
        if rx_event_qs:
            self.criteria =  'Criteria 3. 3 or more hiv concurrent prescriptions for 3 months, with negative viral rna and excluding pre or post prophylaxia exposure'
        
        for patient in rx_patients - set(patients_with_existing_cases): 
            #take care of 3 + meds
            count = 0
            for event in rx_patient_events[patient.id]:
                # check for concurrent for 3 months, count meds and check for the time
                #tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                if event.name in rx3_4_ev_names and abs((event.content_object.end_date - event.content_object.start_date).days) >= 90:
                     # has 3 or 4 meds for 3 months
                     count =3
                     break 
            
            if count <3:
                #take care of meds <3 or 4
                for event in rx_patient_events[patient.id]:
                    if (event.name in rx2_ev_names and len(rx_patient_events[patient.id]) >=2)  :#has 2 and 1s
                        for event2 in rx_patient_events[patient.id]:
                            #calculate concurrency with any of the other meds??
                            if event2.id != event.id: # exclude 
                                overlap = overlap (event.content_object.start_date,event.content_object.end_date,event2.content_object.start_date, event2.content_object.end_date )
                                if overlap >= 90:
                                    count = 3
                                    break #inner loop
                        if count == 3: break #outter for 
                
                if count<3:
                    # take care of single drugs 
                    if len(rx_patient_events[patient.id]) >=3 : # has only ones
                        for event in rx_patient_events[patient.id]:        
                        # for event2 in rx_patient_events[patient.id]:
                            if (event.name in rx1_ev_names):
                                for event2 in rx_patient_events[patient.id]: 
                                    if event2.id != event.id and event2.name in rx1_ev_names: # exclude 
                                        overlap = overlap (event.content_object.start_date,event.content_object.end_date,event2.content_object.start_date, event2.content_object.end_date )
                                        if overlap >= 90:
                                            count +=1
                                        if count ==3: break  
                                if count == 3: break                                
                                               
            if count >=3:       
                t, new_case = self._create_case_from_event_list(
                                        condition = self.conditions[0],
                                        criteria = self.criteria,
                                        recurrence_interval = None, # Does not recur
                                        event_obj = event,
                                        relevant_event_names = rx_patient_events[patient.id],
                                        )
                if t:
                    counter_c += 1
                    log.info('Created new hiv  new case def e: %s' % new_case)
                    #count all                 
            if ( counter_c % 100)==0:
                transaction.commit() 
        
        count = counter_a + counter_b + counter_c
        log.debug('Generated %s new cases of HIV' % count )       
        return count # Count of new cases # Count of new cases
    
    @transaction.commit_manually
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
        counter = 0
        counter += self.generate_def_ab()
        transaction.commit()
        log.debug('Generated %s new cases of HIV' % counter)
        
        return counter # Count of new cases
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

hiv_definition = HIV()

def event_heuristics():
    return hiv_definition.event_heuristics

def disease_definitions():
    return [hiv_definition]
