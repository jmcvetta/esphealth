'''
                            ESP Health
                     Notifiable Diseases Framework
                     ODH Electronic Lab Reporting


@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL
'''

from ESP.nodis.base import SinglePositiveTestDiseaseDefinition

ODH_CONFIG = [
    {    
        'condition': 'campylobac',    
        'short_name': 'campylobac',    
        'test_names' : ['campylobac'],    
        'test_name_search_strings': ['campy'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'cryptospor',    
        'short_name': 'cryptospor',    
        'test_names' : ['cryptospor'],    
        'test_name_search_strings': ['cryptp'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'chlamydia',    
        'short_name': 'chlamydia',    
        'test_names' : ['chlamydia'],    
        'test_name_search_strings': ['chlam','trac'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'giardia',    
        'short_name': 'giardia',    
        'test_names' : ['giardia'],    
        'test_name_search_strings': ['giardia'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'gonorrhea',    
        'short_name': 'gonorrhea',    
        'test_names' : ['gonorrhea'],    
        'test_name_search_strings': ['gonorrhea','gc'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'hep_a',    
        'short_name': 'hep_a',    
        'test_names' : ['hep_a'],    
        'test_name_search_strings': ['hep','igm'],    
        'recurrence_interval': 0    
    },
    {             
        'condition': 'hep_b',    
        'short_name': 'hep_b',    
        'test_names' : ['hep_b'],    
        'test_name_search_strings': ['hep','igm'],    
        'recurrence_interval': 0    
    },             
    {             
        'condition': 'hep_c',    
        'short_name': 'hep_c',    
        'test_names' : ['hep_c'],    
        'test_name_search_strings': ['hep','igm'],    
        'recurrence_interval': 0    
    },             
    {             
        'condition': 'hep_d',    
        'short_name': 'hep_d',    
        'test_names' : ['hep_d'],    
        'test_name_search_strings': ['hep','igm'],    
        'recurrence_interval': 0    
    },             
    {             
        'condition': 'hiv',    
        'short_name': 'hiv',    
        'test_names' : ['hiv'],    
        'test_name_search_strings': ['hiv'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'pertussis',    
        'short_name': 'pertussis',    
        'test_names' : ['pertussis'],    
        'test_name_search_strings': ['bord','pert'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'salmonella',    
        'short_name': 'salmonella',    
        'test_names' : ['salmonella'],    
        'test_name_search_strings': ['salm'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'shigella',    
        'short_name': 'shigella',    
        'test_names' : ['shigella'],    
        'test_name_search_strings': ['shig'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'syphilis',    
        'short_name': 'syphilis',    
        'test_names' : ['syphilis'],    
        'test_name_search_strings': ['rpr','trep','syph'],    
        'recurrence_interval': 0    
    },             
    {    
        'condition': 'varicella',    
        'short_name': 'varicella',    
        'test_names' : ['varicella'],    
        'test_name_search_strings': ['varic'],    
        'recurrence_interval': 0    
    },             
            
    ]

all_conditions = []
all_heuristics = []
for i in ODH_CONFIG:
    class ODHCondition(SinglePositiveTestDiseaseDefinition):
        '''
        A pseudo-disease for ODH Lab Reporting Test 
        '''        
        condition = "odh:" + i['condition']
        short_name = "odh:" + i['short_name']
        uri = 'urn:x-esphealth:disease:commonwealth:%s:v1' % condition 
        test_names = i['test_names']
        test_name_search_strings = i['test_name_search_strings']
        recurrence_interval = i['recurrence_interval']
                    
    disease = ODHCondition()
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
