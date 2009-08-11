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
from ESP.hef2.models import HeuristicEvent
from ESP.nodis2.core import EventPattern
from ESP.emr.models import Patient


jaundice_alt400 = EventPattern(
    name = 'jaundice_alt400',
    reqs = [
        'jaundice',
        'alt_400',
        ],
    operator = 'or'
    )
    
no_hep_b_surf = EventPattern(
    name = 'no_hep_b_surf',
    reqs = [
        'hep_b_surface_neg',
        ],
    operator = 'and',
    exclusions = [
        'hep_b_igm_order',
        ]
    )

no_hep_b = EventPattern(
    name = 'no_hep_b',
    reqs = [
        'hep_b_igm_neg',
        'hep_b_core_neg',
        no_hep_b_surf,
        ],
    operator = 'or'
    )

hep_c_1 = EventPattern(
    name = 'hep_c_1',
    reqs = [
        'hep_c_elisa_pos',
        'hep_a_igm_neg',
        jaundice_alt400,
        no_hep_b
        ],
    operator = 'and',
    )



#print 'jaundice_alt400', jaundice_alt400.plausible_events().count()
#print 'no_hep_b_surf', no_hep_b_surf.plausible_events().count()
#print 'no_hep_b', no_hep_b.plausible_events().count()
clumps = hep_c_1.clumps(condition='acute_hep_c', days=28)
for c in clumps:
    print c




#HeuristicEvent.objects.filter(heuristic_name = 'hep_c_rna')

#pprint.pprint(connection.queries)
