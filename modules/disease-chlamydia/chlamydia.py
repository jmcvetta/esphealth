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

from ESP.nodis.base import SinglePositiveTestDiseaseDefinition





class Chlamydia(SinglePositiveTestDiseaseDefinition):
    '''
    Chlamydia
    '''
    
    condition = 'chlamydia'
    
    uri = 'urn:x-esphealth:disease:channing:chlamydia:v1'
    
    short_name = 'chlamydia'
    
    test_name_search_strings = ['chlam','trac']
    
    test_names = ['chlamydia']
    
    recurrence_interval = 28
    
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

chlamydia_definition = Chlamydia()

def event_heuristics():
    return chlamydia_definition.event_heuristics

def disease_definitions():
    return [chlamydia_definition]
