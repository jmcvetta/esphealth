'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Giardiasis Case Generator


@author: Carolina Chacin <cchacin@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2012 Commonwealth Informatics
@license: LGPL
'''

from ESP.nodis.base import SinglePositiveTestDiseaseDefinition



class Giardiasis(SinglePositiveTestDiseaseDefinition):
    '''
    Giardiasis
    '''
    
    condition = 'giardiasis'
    
    uri = 'urn:x-esphealth:disease:commoninf:giardiasis:v1'
    
    short_name = 'giardiasis'
    
    test_name_search_strings = ['giard']
    
    test_names = ['giardiasis']
    
          
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

giardiasis_definition = Giardiasis()

def event_heuristics():
    return giardiasis_definition.event_heuristics

def disease_definitions():
    return [giardiasis_definition]
