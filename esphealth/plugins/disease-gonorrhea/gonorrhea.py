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

from sprinkles import implements

from ESP.nodis.base import SinglePositiveTestDiseaseDefinition
from ESP.utils.plugins import IPlugin





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

class GonorrheaPlugin(object):
    implements(IPlugin)
    event_heuristics = gonorrhea_definition.event_heuristics
    timespan_heuristics = []
    disease_definitions = [gonorrhea_definition]
    reports = []