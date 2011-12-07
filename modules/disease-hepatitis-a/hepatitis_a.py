'''
                                   ESP Health
                         Notifiable Diseases Framework
                           Hepatitis A Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2011 Channing Laboratory
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
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.base import Case



class Hepatitis_A(DiseaseDefinition):
    '''
    Hepatitis A
    '''
    
    # A future version of this disease definition may also detect chronic hep a
    conditions = ['hepatitis_a:acute']
    
    uri = 'urn:x-esphealth:disease:channing:hepatitis_a:v1'
    
    short_name = 'hepatitis_a'
    
    test_name_search_strings = [
        'hep',
        'alt',
        'ast',
	    ]
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
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
        #
        # Lab Results
        #
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'hep_a_igm',
            ))
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'alt',
            ratio = Decimal('2.0'),
            ))
        heuristic_list.append( LabResultRatioHeuristic(
            test_name = 'ast',
            ratio = Decimal('2.0'),
            ))
        return heuristic_list
    
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
        relevent_event_names = [primary_event_name] + secondary_event_names
        new_case_count = self.create_cases_from_events(
            condition = 'hepatitis_a:acute', 
            criteria = '(dx:jaundice or lx:alt:ratio:2 or lx:ast:ratio:2) AND lx:hep_a_igm:positive within 14 days', 
            recurrence_interval = None,
            event_qs = event_qs, 
            relevent_event_names = relevent_event_names,
            )
        return new_case_count
            
    

#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

hep_a_def = Hepatitis_A()

def event_heuristics():
    return hep_a_def.event_heuristics

def disease_definitions():
    return [hep_a_def]
