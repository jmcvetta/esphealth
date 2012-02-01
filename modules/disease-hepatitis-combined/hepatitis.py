'''
                                  ESP Health
                           Combined Hepatitis A/B/C
                              Disease Definition


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2011-2012 Channing Laboratory
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

from ESP.utils import log
from ESP.hef.base import Event
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.hef.base import LabResultRatioHeuristic
from ESP.hef.base import LabResultFixedThresholdHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case



URI_ROOT = 'urn:x-esphealth:disease:channing:hepatitis-combined:'
URI_VERSION = ':v1'
TEST_NAME_SEARCH_STRINGS = [
    'hep',
    'alt',
    'ast',
    ]

class HepatitisCombined(DiseaseDefinition):

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
            icd9_queries = [
            Icd9Query(starts_with='782.4'),
            ]
            ))
        heuristic_list.append( DiagnosisHeuristic(
            name = 'hepatitis_c:chronic',
            icd9_queries = [
            Icd9Query(starts_with='070.54'),
            ]
            ))
        heuristic_list.append( DiagnosisHeuristic(
            name = 'hepatitis_c:unspecified',
            icd9_queries = [
            Icd9Query(starts_with='070.70'),
            ]
            ))
        #
        # Lab Results
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hepatitis_a_igm',
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
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'alt',
            ratio = Decimal('2.0'),
            ))
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'ast',
            ratio = Decimal('2.0'),
            ))
        heuristic_list.append( LabResultFixedThresholdHeuristic(
            test_name = 'alt',
            threshold = Decimal('400'),
            match_type = 'gt',
            ))
        return heuristic_list
    

class Hepatitis_A(HepatitisCombined):
    '''
    Hepatitis A
    '''

    # A future version of this disease definition may also detect chronic hep a
    conditions = ['hepatitis_a:acute']

    uri = URI_ROOT + 'hepatitis_a' + URI_VERSION

    short_name = 'hepatitis_a'

    test_name_search_strings = TEST_NAME_SEARCH_STRINGS

    timespan_heuristics = []

    @transaction.commit_on_success
    def generate(self):
        #
        # Acute Hepatitis A
        #
        # (dx:jaundice or lx:alt:ratio:2 or lx:ast:ratio:2) 
        # AND lx:hep_a_igm:positive within 14 days
        #
        primary_event_name = 'lx:hep_a_igm:positive'
        secondary_event_names = [
            'dx:jaundice',
            'lx:alt:ratio:2',
            'lx:ast:ratio:2',
            ]
        #
        # FIXME: This date math works on PostgreSQL; but it's not clear that 
        # the ORM will generate reasonable queries for it on other databases.
        #
        event_qs = Event.objects.filter(
            name = primary_event_name,
            patient__event__name__in = secondary_event_names,
            patient__event__date__gte = (F('date') - 14 ),
            patient__event__date__lte = (F('date') + 14 ),
            )
        relevant_event_names = [primary_event_name] + secondary_event_names
        new_case_count = self._create_cases_from_event_qs(
            condition = 'hepatitis_a:acute', 
            criteria = '(dx:jaundice or lx:alt:ratio:2 or lx:ast:ratio:2) AND lx:hep_a_igm:positive within 14 days', 
            recurrence_interval = None,
            event_qs = event_qs, 
            relevant_event_names = relevant_event_names,
            )
        return new_case_count


class Hepatitis_C(HepatitisCombined):
    '''
    Hepatitis C
    '''

    # A future version of this disease definition may also detect chronic hep c
    conditions = ['hepatitis_c:acute']

    uri = URI_ROOT + 'hepatitis_c' + URI_VERSION

    short_name = 'hepatitis_c'

    test_name_search_strings = TEST_NAME_SEARCH_STRINGS

    timespan_heuristics = []

    def generate(self):
        counter = 0
        counter += self._acute_definition_one()
        return counter

    def _acute_definition_one(self):
        '''
        Generate cases based on Definition One in the spec
        @return: Count of new cases created
        @retype: Integer
        '''
        #--------------------
        #
        # Positive ELISA
        #
        #--------------------
        # To be considered for this definition, a patient must have a 
        # positive Hep C ELISA test.
        elisa_qs = Event.objects.filter(name='lx:hep_c_elisa:positive')
        elisa_qs = elisa_qs.exclude(case__condition__in=self.conditions)
        elisa_qs = elisa_qs.order_by('date')
        # Examine ELISA events
        counter = 0
        for elisa_event in elisa_qs:
            # Acute Hep C does not recur, so if this patient already has a 
            # case, we attach this ELISA event to the existing case and
            # continue.  
            # NOTE: This will attach to acute hep C case, and also any future
            # chronic hep c condition.
            existing_cases = Case.objects.filter(patient=elisa_event.patient,
                condition__in=self.conditions)
            if existing_cases:
                first_case = existing_cases[0]
                first_case.events.add(elisa_event)
                first_case.save()
                log.debug('Added %s to existing case %s' % (elisa_event, first_case))
                continue
            #
            # NOTE: The various Exclude/Require sections below may be 
            # reordered without consequence.  This may be desirable
            # for performance reasons if certain exclusions/requirements
            # are more commonly hit than others.
            #
            #
            # A list of QuerySet objects containing the criteria used to 
            # establish a case of acute hep c.
            criteria_list = []
            # Establish boundaries of +/-28 day relevancy window.
            relevancy_start = elisa_event.date - relativedelta(days=28)
            relevancy_end = elisa_event.date + relativedelta(days=28)
            # We are only interested in this patient's events occurring within
            # the relevancy window.
            pat_events_qs = Event.objects.filter(patient=elisa_event.patient)
            event_qs = event_qs.filter(date__gte=relevancy_start)
            event_qs = event_qs.filter(date__lte=relevancy_end)
            #--------------------
            #
            # Exclude chronic Hep C
            #
            #--------------------
            # Patient cannot have a chronic Hep C diagnosis or any positive 
            # Hep C test results prior to this relevancy window.
            prior_event_qs = pat_events_qs(date_lt=relevancy_start)
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
            if not chronic_hep_c_qs:
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
            # Exclude Hep A
            #
            #--------------------
            # Patient must have a negative result on a Hep A test.
            hep_a_neg_names = [
                'lx:hepatitis_a_igm:negative',
                'lx:hepatitis_a_igm_antibody:negative',
                ]
            hep_a_neg_qs = event_qs.filter(name__in=hep_a_neg_names)
            if not hep_a_neg_qs:
                continue # Patient does not have Acute Hep C
            criteria_list.append(hep_a_neg_qs)
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
                ]
            hep_c_nonneg_test_names = [
                'lx:hepatitis_c_riba:positive',
                'lx:hepatitis_c_rna:positive',
                'lx:hepatitis_c_signal_cutoff:positive',
                'lx:hepatitis_c_riba:indeterminate',
                'lx:hepatitis_c_rna:indeterminate',
                'lx:hepatitis_c_signal_cutoff:indeterminate',
                ]
            hep_c_neg_qs = event_qs.filter(name__in=hep_c_neg_test_names)
            hep_c_nonneg_qs = event_qs.filter(name__in=hep_c_nonneg_test_names)
            if hep_c_neg_qs:
                continue # Patient does not have Acute Hep C
            criteria_list.append(hep_c_nonneg_qs) # QuerySet may be empty
            #--------------------
            # 
            # Exclude Hep B
            #
            #--------------------
            # Patient must either have a negative result on a Hep B antibody
            # test; or a negative Hep B surface antigen test result plus no 
            # positive results on a Hep B antibody test.
            hep_b_ab_pos_names = [
                'lx:hepatitis_b_core_antigen_general_antibody:positive',
                'lx:hepatitis_b_core_antigen_igm_antibody:positive',
                ]
            hep_b_ab_neg_names = [
                'lx:hepatitis_b_core_antigen_general_antibody:negative',
                'lx:hepatitis_b_core_antigen_igm_antibody:negative',
                ]
            hep_b_ab_neg_qs = event_qs.filter(name__in=hep_b_ab_neg_names)
            hep_b_ab_pos_qs = event_qs.filter(name__in=hep_b_ab_pos_names)
            hep_b_surface_neg_qs = event_qs.filter(name='lx:hepatitis_b_surface_antigen:positive')
            if hep_b_ab_pos_qs:
                continue # Patient does not have Acute Hep C
            if not (hep_b_ab_neg_qs or hep_b_surface_neg_qs):
                continue # Patient does not have Acute Hep C
            criteria_list.append(hep_b_ab_neg_qs) # QuerySet may be empty
            criteria_list.append(hep_b_surface_neg_qs) # QuerySet may be empty
            #--------------------
            # 
            # Suspected Hep C case
            #
            #--------------------
            # Combine all the criteria into a single query.  
            # NOTE: This may overtax the ORM and create a bad query.  Check carefully!
            this_elisa_qs = Event.objects.filter(pk=elisa_event.pk)
            criteria_list.append(this_elisa_qs)
            combined_criteria_qs = criteria_list[0]
            for criterion_qs in criterion_list[1:]:
                combined_criteria_qs |= criterion_qs
            # Date the case based on the earliest criterion.
            # NOTE: Is this the desired behavior?
            first_event = combined_criteria_qs.order_by('date')[0]
            created, this_case = self._create_case_from_event_obj(
                condition = 'hepatitis_c:acute', 
                criteria = 'Definition One', 
                recurrence_interval = None,  # Does not recur
                event_obj = first_event, 
                relevant_event_qs = combined_criteria_qs,
                )
            if created:
                counter += 1
        return counter



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Packaging
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def event_heuristics():
    return Hepatitis_A().event_heuristics # Heuristics for any Hep definition are identical

def disease_definitions():
    return [Hepatitis_A(), Hepatitis_C()]
