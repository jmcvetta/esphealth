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
from ESP.hef.base import Icd9Query
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case



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
            icd9_queries = [
                Icd9Query(starts_with='090'),
                Icd9Query(starts_with='091'),
                Icd9Query(starts_with='092'),
                Icd9Query(starts_with='093'),
                Icd9Query(starts_with='094'),
                Icd9Query(starts_with='095'),
                Icd9Query(starts_with='096'),
                Icd9Query(starts_with='097'),
                ]
            ))
        #
        # Prescriptions
        #
        heuristic_list.append( PrescriptionHeuristic(
            name = 'penicillin_g',
            drugs = ['penicillin g', 'pen g'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'doxycycline_7_day',
            drugs = ['doxycycline',],
            min_quantity = 14, # Need 14 pills for 7 days
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ceftriaxone_1_or_2_gram',
            drugs = ['ceftriaxone',],
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
            test_name = 'ftp-abs',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'tp-igg',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'vrdl-csf',
            ))
        return heuristic_list
    
    @transaction.commit_on_success
    def generate(self):
        #
        # Criteria Set #1
        #
        dx_ev_names = ['dx:syphilis']
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
        #
        # Criteria Set #2
        #
        rpr_ev_names = [
            'lx:rpr:positive',
            'lx:vrdl:positive',
            ]
        ttpa_ev_names = [
            'lx:ttpa:positive',
            'lx:fta-abs:positive',
            'lx:tp-igg:positive',
            ]
        test_event_qs = Event.objects.filter(
            name__in = rpr_ev_names,
            patient__event__name__in = ttpa_ev_names,
            )
        #
        # Criteria Set #3
        #
        vrdl_csf_ev_names = ['lx:vrdl-csf:positive']
        vrdl_csf_qs = Event.objects.filter(name__in=vrdl_csf_ev_names)
        #
        # Combined Criteria
        #
        combined_criteria_qs = dxrx_event_qs | test_event_qs | vrdl_csf_qs
        combined_criteria_qs = combined_criteria_qs.exclude(case__condition='syphilis')
        combined_criteria_qs = combined_criteria_qs.order_by('date')
        all_event_names = dx_ev_names + rx_ev_names + rpr_ev_names + ttpa_ev_names + vrdl_csf_ev_names
        counter = 0
        new_case_count = self._create_cases_from_events(
            condition = 'syphilis',
            criteria = 'combined syphilis criteria', 
            recurrence_interval = None, 
            event_qs = combined_criteria_qs, 
            relevent_event_names = all_event_names,
            )
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
