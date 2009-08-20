'''
                                  ESP Health
                         Notifiable Diseases Framework
                              Disease Defintions


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import pprint
from django.db import connection
from ESP.hef2 import events
from ESP.hef2.core import BaseHeuristic
#from ESP.hef2.models import HeuristicEvent
from ESP.nodis2.core import ComplexEventPattern
from ESP.emr.models import Patient


jaundice_alt400 = ComplexEventPattern(
    patterns = [
        'jaundice',
        'alt_400',
        ],
    operator = 'or'
    )
    
no_hep_b_surf = ComplexEventPattern(
    patterns = [
        'hep_b_surface_neg',
        ],
    operator = 'and',
    exclusions = [
        'hep_b_igm_order',
        ]
    )

no_hep_b = ComplexEventPattern(
    patterns = [
        'hep_b_igm_neg',
        'hep_b_core_neg',
        no_hep_b_surf,
        ],
    operator = 'or'
    )

hep_c_1 = ComplexEventPattern(
    patterns = [
        'hep_c_elisa_pos',
        'hep_a_igm_neg',
        jaundice_alt400,
        no_hep_b
        ],
    operator = 'and',
    )


