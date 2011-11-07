'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Chlamydia Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''

from ESP.nodis.base import DiseaseDefinition
from ESP.hef.base import PrescriptionHeuristic



class Syphilis(DiseaseDefinition):
    '''
    Syphilis
    '''
    
    condition = 'syphilis'
    
    uri = 'urn:x-esphealth:disease:channing:syphilis:v1'
    
    short_name = 'syphilis'
    
    test_name_search_strings = [],
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        heuristic_list.append( PrescriptionHeuristic(
            name = 'penicillin_g',
            drugs = ['penicillin g', 'pen g'],
            ))
        return heuristic_list
    

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
