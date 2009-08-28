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
    exclude = [
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
        jaundice_alt400,    # (1 or 2)
        'hep_c_elisa_pos',  # 3 positive
        'hep_a_igm_neg',    # 7 negative
        no_hep_b,           # (8 negative or 9 non-reactive)
        ],
    exclude = [
        'hep_c_signal_cutoff_neg', # 4 positive (if done)
        'hep_c_riba_neg',          # 5 positive (if done)
        'hep_c_rna_neg',           # 6 positive (if done)
        ],
    exclude_past = [
        'hep_c_elisa_pos',   # no prior positive 3 or 5 or 6
        'hep_c_riba_pos',    # "
        'hep_c_rna_pos',     # "
        'chronic_hep_b', # no ICD9 (070.54 or 070.70) ever prior to this encounter
        ],
    operator = 'and',
    )

