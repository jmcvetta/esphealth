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

from sprinkles import implements

from ESP.nodis.base import SinglePositiveTestDiseaseDefinition
from ESP.utils.plugins import IPlugin





class Chlamydia(SinglePositiveTestDiseaseDefinition):
    '''
    Chlamydia
    '''
    
    condition = 'chlamydia'
    
    uri = 'urn:x-esphealth:disease:channing:chlamydia:v1'
    
    short_name = 'chlamydia'
    
    test_name_search_strings = ['chlam',]
    
    test_names = ['chlamydia']
    
    recurrence_interval = 28
    
    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

chlamydia_definition = Chlamydia()

class ChlamydiaPlugin(object):
    implements(IPlugin)
    event_heuristics = chlamydia_definition.event_heuristics
    timespan_heuristics = []
    disease_definitions = [chlamydia_definition]
    reports = []