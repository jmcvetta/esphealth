'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Syphilis Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
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
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Dx_CodeQuery
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case
from ESP.static.models import DrugSynonym


class Syphilis(DiseaseDefinition):
    '''
    Syphilis
    '''
    
    conditions = ['syphilis']
    
    uri = 'urn:x-esphealth:disease:channing:syphilis:v1'
    
    short_name = 'syphilis'
    
    test_name_search_strings = [
	    'syph',
	    'rpr', 
	    'vdrl',
	    'tp', 
	    'fta',
	    'trep',
	    'pallidum',
	    ]
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        #
        # Diagnosis Codes
        #
        heuristic_list.append( DiagnosisHeuristic(
            name = 'syphilis',
            dx_code_queries = [
                Dx_CodeQuery(starts_with='090', type='icd9'),
                Dx_CodeQuery(starts_with='091', type='icd9'),
                Dx_CodeQuery(starts_with='092', type='icd9'),
                Dx_CodeQuery(starts_with='093', type='icd9'),
                Dx_CodeQuery(starts_with='094', type='icd9'),
                Dx_CodeQuery(starts_with='095', type='icd9'),
                Dx_CodeQuery(starts_with='096', type='icd9'),
                Dx_CodeQuery(starts_with='097', type='icd9'),
                Dx_CodeQuery(starts_with='A50', type='icd10'),
                Dx_CodeQuery(starts_with='A51', type='icd10'),
                Dx_CodeQuery(starts_with='A52', type='icd10'),
                Dx_CodeQuery(starts_with='A53', type='icd10'),
                ]
            ))
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'penicillin_g',
            drugs = DrugSynonym.generics_plus_synonyms(['penicillin g', 'pen g']),
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'doxycycline_7_day',
            drugs = DrugSynonym.generics_plus_synonyms(['doxycycline',]),
            min_quantity = 14, # Need 14 pills for 7 days
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ceftriaxone_1_or_2_gram',
            drugs = DrugSynonym.generics_plus_synonyms(['ceftriaxone',]),
            doses = [ 
                Dose(quantity = 1, units = 'g'),
                Dose(quantity = 2, units = 'g'),
                ],
            ))
        #
        # Lab Results
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'rpr',
            titer_dilution = 8,
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'vdrl',
            titer_dilution = 8,
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'tppa',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'fta-abs',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'tp-igg',
            ))
        #new heuristic in v7 of spec 
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'tp-igm',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'vdrl-csf',
            titer_dilution = 1,
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'tppa-csf',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'fta-abs-csf',
            ))

        return heuristic_list
    
    @transaction.commit_on_success
    def generate(self):
        log.info('Generating cases of %s' % self.short_name)
        self.criteria = ''
        #
        # Criteria Set #1
        #
        dx_ev_names = ['dx:syphilis']
        lx_ev_names = ['lx:tp-igm:positive',]
        rx_ev_names = [
            'rx:penicillin_g',
            'rx:doxycycline_7_day',
            'rx:ceftriaxone_1_or_2_gram',
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
        
        lxrx_event_qs = Event.objects.filter(
            name__in = lx_ev_names,
            patient__event__name__in = rx_ev_names,
            patient__event__date__gte = (F('date') - 14 ),
            patient__event__date__lte = (F('date') + 14 ),
            )
        if dxrx_event_qs or lxrx_event_qs:
            self.criteria = 'Criteria #1: syphilis diagnosis or tp-igm:positive and prescription of penicillin_g or doxycycline_7_day or ceftriaxone_1_or_2_gram w/in 14 days'
        #
        # Criteria Set #2
        #
        rpr_ev_names = [
            'lx:rpr:positive',
            'lx:vdrl:positive',
            ]
        tppa_ev_names = [
            'lx:tppa:positive',
            'lx:fta-abs:positive',
            'lx:tp-igg:positive',
            ]
        test_event_qs = Event.objects.filter(
            name__in = rpr_ev_names,
            patient__event__name__in = tppa_ev_names,
            patient__event__date__lte = (F('date') + 30 ),
            )
        if test_event_qs:
            self.criteria += ' Criteria #2: rpr_pos or vdrl_pos and (tppa_pos or fta-abs_pos or tp-igg_pos) ever in the past up to 1 month following positive (titer dilution 8) rpr or vdrl'
        #
        # Criteria Set #3
        #
        vdrl_csf_ev_names = ['lx:vdrl-csf:positive',
                             'lx:fta-abs-csf:positive',
                             'lx:tppa-csf:positive', 
                                ]
        vdrl_csf_qs = Event.objects.filter(name__in=vdrl_csf_ev_names)
        
        if vdrl_csf_qs:
            self.criteria += ' Criteria #3: vdrl-csf:pos (titer dilution 1) or  fta-abs-csf:pos or tppa-csf:pos'
        #
        # Combined Criteria
        #
        combined_criteria_qs = dxrx_event_qs | lxrx_event_qs | test_event_qs | vdrl_csf_qs
        combined_criteria_qs = combined_criteria_qs.exclude(case__condition='syphilis')
        # ordering here doesnt matter because create cases from event sorts again
        combined_criteria_qs = combined_criteria_qs.order_by('date')
        all_event_names = dx_ev_names + lx_ev_names + rx_ev_names + rpr_ev_names + tppa_ev_names + vdrl_csf_ev_names
        
        new_case_count = self._create_cases_from_event_qs(
            condition = 'syphilis',
            criteria = self.criteria, 
            recurrence_interval = None, 
            event_qs = combined_criteria_qs, 
            relevant_event_names = all_event_names,
            )
        
        log.debug('Generated %s new cases of syphilis' % new_case_count)
        
        return new_case_count
            
    

#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

syphilis_definition = Syphilis()

def event_heuristics():
    return syphilis_definition.event_heuristics

def disease_definitions():
    return [syphilis_definition]
