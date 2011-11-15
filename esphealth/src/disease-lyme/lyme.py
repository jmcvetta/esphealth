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
            name = 'syphilis_diagnosis',
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
        dx_ev_names = ['dx:syphilis_diagnosis']
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
        for this_event in combined_criteria_qs:
            existing_cases = Case.objects.filter(
                condition='syphilis', 
                patient=this_event.patient,
                #date__gte=(this_event.date - relativedelta(days=28) # Adds recurrence interval
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
                condition = 'syphilis',
                patient = this_event.patient,
                provider = this_event.provider,
                date = this_event.date,
                criteria = 'combined syphilis criteria',
                source = self.uri,
                )
            new_case.save()
            new_case.events.add(this_event)
            all_relevant_events = Event.objects.filter(patient=this_event.patient, name__in=all_event_names)
            for related_event in all_relevant_events:
                new_case.events.add(related_event)
            new_case.save()
            log.info('Created new syphilis case: %s' % new_case)
            counter += 1
        return counter # Count of new cases
            
    

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
