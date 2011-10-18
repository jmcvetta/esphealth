'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Gonorrhea Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''

from ESP.nodis.base import SinglePositiveTestDiseaseDefinition





class Gonorrhea(SinglePositiveTestDiseaseDefinition):
    '''
    Gonorrhea
    '''
    
    condition = 'gonorrhea'
    
    uri = 'urn:x-esphealth:disease:channing:gonorrhea:v1'
    
    short_name = 'gonorrhea'
    
    test_name_search_strings = ['gon', 'gc',]
    
    test_names = ['gonorrhea']
    
    recurrence_interval = 28
    
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

gonorrhea_definition = Gonorrhea()

def event_heuristics():
    return gonorrhea_definition.event_heuristics

def disease_definitions():
    return [gonorrhea_definition]
