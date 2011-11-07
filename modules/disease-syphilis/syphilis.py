'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Chlamydia Case Generator


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

from django.db.models import F

from ESP.nodis.base import DiseaseDefinition
from ESP.hef.base import Event
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic



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
    
    def generate(self):
        raise NotImplementedError('nothing to see here')
        #
        # Criteria Set #1
        #
        dx_ev_name = 'dx:syphilis'
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
            name = dx_ev_name,
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
