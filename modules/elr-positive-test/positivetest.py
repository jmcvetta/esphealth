'''
                                  ESP Health
                         Notifiable Diseases Framework
                            Electronic Lab Reporting


@author: Rich Schaaf <rschaaf@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2012 Commonwealth Informatics
@license: LGPL
'''

from ESP.nodis.base import SinglePositiveTestDiseaseDefinition

# Note: In the following ELR_CONFIG entries, a recurrence_interval of 0
# means that only lab test results for the same date will be considered
# part of the same "case".
ELR_CONFIG = [
    {
        'condition': 'chlamydia',
        'short_name': 'chlamydia',
        'test_names' : ['chlamydia'],
        'test_name_search_strings': ['chlam','trac'],
        'recurrence_interval': 0
    },
    {
        'condition': 'gonorrhea',
        'short_name': 'gonorrhea',
        'test_names' : ['gonorrhea'],
        'test_name_search_strings': ['gon','gc'],
        'recurrence_interval': 0
    },
    {
        'condition': 'clostridium_difficile',
        'short_name': 'clostridium_difficile',
        'test_names' : ['clostridium_difficile_eia', 'clostridium_difficile_pcr'],
        'test_name_search_strings': ['diff', 'toxin'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'rapid_flu',
        'short_name': 'rapid_flu',
        'test_names' : ['rapid_flu'],
        'test_name_search_strings': ['quick','rapid', 'flue'],
        'recurrence_interval': 0
    },             
            
    ]

all_conditions = []
all_heuristics = []
for i in ELR_CONFIG:
    class ElrCondition(SinglePositiveTestDiseaseDefinition):
        '''
        A pseudo-disease for Electronic Lab Reporting 
        '''        
        condition = "elr:" + i['condition']
        short_name = "elr:" + i['short_name']
        uri = 'urn:x-esphealth:disease:channing:%s:v1' % condition 
        test_names = i['test_names']
        test_name_search_strings = i['test_name_search_strings']
        recurrence_interval = i['recurrence_interval']
                    
    disease = ElrCondition()
    all_conditions.append(disease)
    all_heuristics.extend(disease.event_heuristics)

    
#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

def event_heuristics():
    return all_heuristics

def disease_definitions():
    return all_conditions
