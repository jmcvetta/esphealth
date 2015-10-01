'''
                                  ESP Health
                                Hepatitis C New
                              Disease Definition


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: Commonwealth informatics
@contact: http://www.esphealth.org
@copyright: (c) 2011-2012 Channing Laboratory, 2011-2014 Commonwealth informatics
@license: LGPL
'''


# In most instances it is preferable to use relativedelta for date math.  
# However when date math must be included inside an ORM query, and thus will
# be converted into SQL, only timedelta is supported.
#
# This may not still be true in newer versions of Django - JM 6 Dec 2011
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.db.models import Min
from django.db.models import Max

from ESP.utils import log
from ESP.hef.models import Event
from ESP.hef.base import BaseEventHeuristic
from ESP.hef.base import AbstractLabTest
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.hef.base import LabResultRatioHeuristic
from ESP.hef.base import LabResultFixedThresholdHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Dx_CodeQuery
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case



URI_ROOT = 'urn:x-esphealth:disease:channing:hepatitis-new:'
URI_VERSION = ':v1'
TEST_NAME_SEARCH_STRINGS = [
    'hep',
    'alt',
    'ast',
    'bili',
    'tbil',
    'hbv',
    'sgpt',
    'sgot',
    'aminotrans'
    ]


class HepatitisNew(DiseaseDefinition):
    
    @property
    def event_heuristics(self):
        '''
        Event heuristics used by all Hepatitis variants
        '''
        heuristic_list = []
        #
        # Diagnosis Codes
        #
       
        heuristic_list.append( DiagnosisHeuristic(
            name = 'jaundice',
            dx_code_queries = [
            Dx_CodeQuery(starts_with='R17', type='icd10'),
            Dx_CodeQuery(starts_with='782.4', type='icd9'),
            ]
            ))
        heuristic_list.append( DiagnosisHeuristic(
            name = 'hepatitis_b:chronic',
            dx_code_queries = [
            Dx_CodeQuery(starts_with='B18.1', type='icd10'),
            Dx_CodeQuery(starts_with='070.32', type='icd9'),
            ]
            ))
        heuristic_list.append( DiagnosisHeuristic(
            name = 'hepatitis_c:chronic',
            dx_code_queries = [
            Dx_CodeQuery(starts_with='B18.2', type='icd10'),
            Dx_CodeQuery(starts_with='070.54', type='icd9'),
            ]
            ))
        heuristic_list.append( DiagnosisHeuristic(
            name = 'hepatitis_c:unspecified',
            dx_code_queries = [
            Dx_CodeQuery(starts_with='B19.20', type='icd10'),
            Dx_CodeQuery(starts_with='070.70', type='icd9'),
            ]
            ))

        #
        # Lab Results
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            # Hep B definition calls this "Hepatitis C antibody" but has same
            # test codes as Hep C "Hepatitis C ELISA" test.
            test_name = 'hepatitis_c_elisa',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_c_signal_cutoff',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_c_riba',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_c_rna',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_a_igm_antibody',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_a_total_antibodies',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_b_core_antigen_igm_antibody',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_b_core_antigen_general_antibody',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_b_surface_antigen',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_b_e_antigen',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_b_viral_dna',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_e_antibody',
            ))
        #
        # The main purpose of having heuristics for direct and indirect
        # bilirubin is to allow Abstract Lab Test mapping of these test
        # types.  We are not actually interested in "positive" events
        # for these tests, but rather in examining these tests to get
        # the calculated bilirubin value.
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'bilirubin_direct',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'bilirubin_indirect',
            ))
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'alt',
            ratio = 2,
            ))
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'alt',
            ratio = 5,
            ))
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'ast',
            ratio = 2,
            ))
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'ast',
            ratio = 5,
            ))
        heuristic_list.append( LabResultFixedThresholdHeuristic(
            test_name = 'alt',
            threshold = Decimal('400'),
            match_type = 'gt',
            ))
        heuristic_list.append( LabResultFixedThresholdHeuristic(
            test_name = 'bilirubin_total',
            threshold = Decimal('1.5'),
            match_type = 'gt',
            ))
        return heuristic_list
    


class Hepatitis_C(HepatitisNew):
    '''
    Hepatitis C New
    '''

    # A future version of this disease definition may also detect chronic hep c
    conditions = ['sandbox:hepatitis_c:acute']

    uri = URI_ROOT + 'sandbox:hepatitis_c:acute' + URI_VERSION

    short_name = 'sandbox:hepatitis_c:acute'

    test_name_search_strings = TEST_NAME_SEARCH_STRINGS

    timespan_heuristics = []

    def generate(self):
        log.info('Generating cases for %s (%s)' % (self.short_name, self.uri))
        counter = 0
        counter += self._acute_hep_c_condition_d()
        counter += self._acute_hep_c_condition_c()
        counter += self._acute_hep_c_condition_a_b()
        
        return counter

    def _acute_hep_c_condition_a_b(self):
        '''
        Detects cases based on definition (a) and (b) in spec
            for Hep C.
            a) (icd9 782.4 or alt >400) and c-elisa positive and c-signal cutoff positive (>3.8 if done) and c-riba positive (if done) 
              and c-rna positive (if done)  within a 28 day period; 
              AND  no prior positive c-elisa or c-riba or c-rna ever;  AND no ICD9 (070.54 or 070.70) ever prior to this encounter
              
            b) (icd9 782.4 or alt >400) and c-rna positive and c-signal cutoff positive (if done) and c-riba positive (if done) 
              within a 28 day period; 
             AND no prior positive c-elisa or c-riba or c-rna ever;  AND no ICD9 (070.54 or 070.70) ever prior to this encounter

        @return: Count of new cases created
        @retype: Integer
        '''
        log.debug('Generating cases for Hep C condition a and b ')
        #--------------------
        #
        # Positive ELISA or RNA
        #
        #--------------------
        # To be considered for this definition, a patient must have either a 
        # positive Hep C ELISA or Hep C RNA test result.  We will call this 
        # "trigger event" because it is absolutely required; however this type
        # of event is NOT by itself adequate to trigger a case of Hep C.
        
        trigger_conditions = ['lx:hepatitis_c_elisa:positive', 'lx:hepatitis_c_rna:positive']
        trigger_qs = Event.objects.filter(name__in=trigger_conditions) # excludes bound events
        trigger_qs = trigger_qs.exclude(case__condition__in=self.conditions)
        trigger_qs = trigger_qs.order_by('date')
        
        # Examine trigger events
        counter = 0
             
        for trigger_event in trigger_qs:
            # Acute Hep C does not recur, so if this patient already has a 
            # case, we attach this ELISA or rna event to the existing case and
            # continue.  
            # NOTE: This will attach to acute hep C case, and also any future
            # chronic hep c condition.
            existing_cases = Case.objects.filter(patient=trigger_event.patient,
                condition__in=self.conditions)
            if existing_cases:
                first_case = existing_cases[0]
                first_case.events.add(trigger_event)
                first_case.save()
                log.debug('Added %s to existing case %s' % (trigger_event, first_case))
                continue
            #
            # NOTE: The various Exclude/Require sections below may be 
            # reordered without consequence.  This may be desirable
            # for performance reasons if certain exclusions/requirements
            # are more commonly hit than others.
            #
            pat_events_qs = Event.objects.filter(patient=trigger_event.patient)
            # Establish boundaries of +/-30 day relevancy window.
            relevancy_start = trigger_event.date - relativedelta(days=28)
            relevancy_end = trigger_event.date + relativedelta(days=28)
            event_qs = pat_events_qs.filter(date__gte=relevancy_start, date__lte=relevancy_end)
            # All events prior to start of relevancy window
            prior_event_qs = pat_events_qs.filter(date__lt=relevancy_start)
            # A list of QuerySet objects containing the criteria used to 
            # establish a case of acute hep c.
            criteria_list = []
            #--------------------
            #
            # Exclude chronic Hep C
            #
            #--------------------
            # Patient cannot have a chronic Hep C diagnosis or any positive 
            # Hep C test results prior to this relevancy window.
            chronic_hep_c_event_names = [
                'dx:hepatitis_c:chronic',
                'dx:hepatitis_c:unspecified',
                'lx:hepatitis_c_elisa:positive',
                'lx:hepatitis_c_riba:positive',
                'lx:hepatitis_c_rna:positive',
                # NOTE: Signal cutoff is not mentioned in Mike's definition, but 
                # seems to belong with the rest here.
                #'lx:hepatitis_c_signal_cutoff:positive',
                ]
            chronic_hep_c_qs = prior_event_qs.filter(name__in=chronic_hep_c_event_names)
            if chronic_hep_c_qs:
                continue # Patient has chronic Hep C, and thus does not have Acute Hep C
            #--------------------
            # 
            # Require Jaundice / Elevated ALT
            #
            #--------------------
            # Patient must have jaundice or elevanted ALT levels.
            jaundice_or_alt_names = [
                'dx:jaundice', 
                'lx:alt:threshold:gt:400',
                ]
            jaundice_or_alt_qs = event_qs.filter(name__in=jaundice_or_alt_names)
            if not jaundice_or_alt_qs:
                continue # Patient does not have Acute Hep C
            criteria_list.append(jaundice_or_alt_qs)
            
            #--------------------
            # 
            # Exclude negative Hep C results
            #
            #--------------------
            # If patient has a non-ELISA Hep C test, the result must not
            # be negative.
            hep_c_neg_test_names = [
                'lx:hepatitis_c_riba:negative',
                'lx:hepatitis_c_rna:negative',
                'lx:hepatitis_c_signal_cutoff:negative',
                # NOTE: Spec does not mention exclusion of negative ELISA results
                # in definition (b), but it seems like an obvious counterpart to 
                # the exclusion of negative RIBA results in definition (a).
                'lx:hepatitis_c_elisa:negative', 
                ]
            hep_c_nonneg_test_names = [
                'lx:hepatitis_c_riba:positive',
                'lx:hepatitis_c_rna:positive',
                'lx:hepatitis_c_signal_cutoff:positive',
                'lx:hepatitis_c_riba:indeterminate',
                'lx:hepatitis_c_rna:indeterminate',
                'lx:hepatitis_c_signal_cutoff:indeterminate',
                # See note above
                'lx:hepatitis_c_elisa:positive', 
                'lx:hepatitis_c_elisa:indeterminate', 
                ]
            hep_c_neg_qs = event_qs.filter(name__in=hep_c_neg_test_names)
            hep_c_nonneg_qs = event_qs.filter(name__in=hep_c_nonneg_test_names)
            if hep_c_neg_qs:
                continue # Patient does not have Acute Hep C
            criteria_list.append(hep_c_nonneg_qs) # QuerySet may be empty
     
            #--------------------
            # 
            # Suspected Hep C case
            #
            #--------------------
            # Combine all the criteria into a single query.  
            # NOTE: This may overtax the ORM and create a bad query.  Check carefully!
            this_elisa_qs = Event.objects.filter(pk=trigger_event.pk)
            criteria_list.append(this_elisa_qs)
            combined_criteria_qs = criteria_list[0]
            for criterion_qs in criteria_list[1:]:
                combined_criteria_qs |= criterion_qs
            # Date the case based on the earliest criterion.
            # NOTE: Is this the desired behavior?
            
            criteria = ''
            if trigger_event.name == 'lx:hepatitis_c_elisa:positive':
                criteria += 'Criteria #1: {(3)positive c-elisa '
            else:
                criteria += 'Criteria #2: {(6) positive c-rna '
                
            criteria += ' AND (1 OR 2)(jaundice (not of newborn) OR alt>400) AND (4)not negative(pos/ind) hep c signal cutoff AND (5)not negative(pos/ind) c-riba)} within 28 days; exclude if:'
            criteria += ' prior/current dx=chronic hep c OR prior/current dx=unspecified hep c OR (3)prior positive c-elisa ever OR (5)prior positive c-riba ever OR (6)prior positive c-rna ever'
            created, this_case = self._create_case_from_event_obj(
                condition = 'sandbox:hepatitis_c:acute', 
                criteria = criteria, 
                recurrence_interval = None,  # Does not recur
                event_obj = trigger_event, 
                relevant_event_qs = combined_criteria_qs,
                )
            if created:
                counter += 1
        log.debug('Created %s new Hep C cases with complex algo' % counter)
        return counter

    def _acute_hep_c_condition_c(self):
        
        '''
        Detects cases based on definitions (c) in spec for Hep C.
            c)hep c rna positive and record of hep c elisa negative within the prior 12 months
                
        @return: Count of new cases created
        @retype: Integer
        '''
        log.debug('Generating cases for Hep C condition c')
        #--------------------
        #
        # Positive  RNA
        #
        #--------------------
        # To be considered for this definition, a patient must have a 
        #  Hep C RNA positive test result.
         
        trigger_conditions = ['lx:hepatitis_c_rna:positive']
        trigger_qs = Event.objects.filter(name__in=trigger_conditions)
        trigger_qs = trigger_qs.exclude(case__condition__in=self.conditions)
        trigger_qs = trigger_qs.order_by('date')
        
        # no postivie tests priors of elisa, riba and rna
        prior_positive_event_names = [
                'lx:hepatitis_c_elisa:positive',
                'lx:hepatitis_c_riba:positive',
                'lx:hepatitis_c_rna:positive',
                
        ]
        # Examine trigger events
        counter = 0
        for trigger_event in trigger_qs:
            # Acute Hep C does not recur, so if this patient already has a 
            # case, we attach this event to the existing case and
            # continue.  
            # NOTE: This will attach to acute hep C case, and also any future
            # chronic hep c condition.
            existing_cases = Case.objects.filter(patient=trigger_event.patient,
                condition__in=self.conditions)
            if existing_cases:
                first_case = existing_cases[0]
                first_case.events.add(trigger_event)
                first_case.save()
                log.debug('Added %s to existing case %s' % (trigger_event, first_case))
                continue
            neg_event_name = 'lx:hepatitis_c_elisa:negative' 
           
            relevancy_start_date = trigger_event.date - relativedelta(months=12)
            
            prior_neg_qs = Event.objects.filter(
                patient = trigger_event.patient,
                name = neg_event_name,
                date__gte = relevancy_start_date,
                date__lt = trigger_event.date,
                )
            
            prior_positives= Event.objects.filter(
                patient = trigger_event.patient,
                name = prior_positive_event_names,
                date__lt = trigger_event.date,
                )
            
            if not prior_neg_qs or prior_positives:
                # No prior negative test result or prior positive of elisa, rna or riba in the past, 
                # so patient does not meet this definition of Hep C.
                continue
            
            created, this_case = self._create_case_from_event_obj(
                condition = 'sandbox:hepatitis_c:acute', 
                criteria = 'Criteria #3: positive c-rna and c-elisa negative w/in the prior 12 months',  
                recurrence_interval = None,  # Does not recur
                event_obj = trigger_event, 
                relevant_event_qs = prior_neg_qs,
                )
            if created:
                counter += 1
        log.debug('Created %s new Hep C cases condition c' % counter)
        return counter

    def _acute_hep_c_condition_d(self):
        
        '''
        Detects cases based on definitions (d) in spec for Hep C.    
            d)elisa positive and record of elisa negative within the prior 12 months AND no prior positive of elisa or riba or rna ever
            
        @return: Count of new cases created
        @retype: Integer
        '''
        log.debug('Generating cases for Hep C condition d')
        #--------------------
        #
        # Positive  ELISA
        #
        #--------------------
        # To be considered for this definition, a patient must have a 
        # Hep C ELISA positive test result.
         
        trigger_conditions = ['lx:hepatitis_c_elisa:positive']
        
        # no postivie tests priors of elisa, riba and rna
        prior_positive_event_names = [
                'lx:hepatitis_c_elisa:positive',
                'lx:hepatitis_c_riba:positive',
                'lx:hepatitis_c_rna:positive',
                
        ]
        trigger_qs = Event.objects.filter(name__in=trigger_conditions)
        trigger_qs = trigger_qs.exclude(case__condition__in=self.conditions)
        trigger_qs = trigger_qs.order_by('date')
        # Examine trigger events
        counter = 0
        for trigger_event in trigger_qs:
            # Acute Hep C does not recur, so if this patient already has a 
            # case, we attach this event to the existing case and
            # continue.  
            # NOTE: This will attach to acute hep C case, and also any future
            # chronic hep c condition.
            existing_cases = Case.objects.filter(patient=trigger_event.patient,
                condition__in=self.conditions)
            if existing_cases:
                first_case = existing_cases[0]
                first_case.events.add(trigger_event)
                first_case.save()
                log.debug('Added %s to existing case %s' % (trigger_event, first_case))
                continue
            neg_event_name = 'lx:hepatitis_c_elisa:negative'            
            relevancy_start_date = trigger_event.date - relativedelta(months=12)
            
            prior_neg_qs = Event.objects.filter(
                patient = trigger_event.patient,
                name = neg_event_name,
                date__gte = relevancy_start_date,
                date__lt = trigger_event.date,
                )
            
            prior_positives= Event.objects.filter(
                patient = trigger_event.patient,
                name = prior_positive_event_names,
                date__lt = trigger_event.date,
                )
            if not prior_neg_qs or prior_positives:
                # No prior negative ELISA test result or prior positive of elisa, rna or riba in the past, 
                # so patient does not meet this definition of Hep C.
                continue
            
            created, this_case = self._create_case_from_event_obj(
                condition = 'sandbox:hepatitis_c:acute', 
                criteria = 'Criteria #4: c-elisa positive and c-elisa negative w/in the prior 12 months and no prior positive of c-elisa, c-riba or c-rna ever',  
                recurrence_interval = None,  # Does not recur
                event_obj = trigger_event, 
                relevant_event_qs = prior_neg_qs,
                )
            if created:
                counter += 1
        log.debug('Created %s new Hep C cases condition d' % counter)
        return counter
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Packaging
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def event_heuristics():
    return Hepatitis_C().event_heuristics # Heuristics for any Hep definition are identical

def disease_definitions():
    return [  Hepatitis_C()]
