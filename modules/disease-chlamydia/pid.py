'''
                                  ESP Health
                         Notifiable Diseases Framework
                         Pelvic Inflamatory Case Generator


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics http://www.commoninf.com
@contact: http://www.esphealth.org
@copyright: (c) 2011Channing Laboratory
@license: LGPL
'''

from ESP.nodis.base import DiseaseDefinition
from ESP.hef.base import DiagnosisHeuristic



class Syphilis(DiseaseDefinition):
    '''
    PID
    '''
    
    condition = 'PID'
    
    uri = 'urn:x-esphealth:disease:channing:pid:v1'
    
    short_name = 'pid'
    
    test_name_search_strings = [],
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        # Diagnosis Codes
        #
        heuristic_list.append( DiagnosisHeuristic(
            name = 'pid_diagnosis',
            icd9_queries = [
                Icd9Query(starts_with='610'),
                Icd9Query(starts_with='099.56'),
               ]
            ))
        return heuristic_list
    

#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

pid_definition = PID()

def event_heuristics():
    return pid_definition.event_heuristics

def disease_definitions():
    return [pid_definition]
