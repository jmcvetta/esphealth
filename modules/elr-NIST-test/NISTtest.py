'''
                                  ESP Health
                         Notifiable Diseases Framework
                     NIST Electronic Lab Reporting Test Cases


@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL
'''

import abc
from ESP.nodis.base import DiseaseDefinition
from ESP.hef.base import BaseLabResultHeuristic
from ESP.hef.models import Event
from ESP.conf.models import LabTestMap
from ESP.nodis.base import Case
from ESP.utils import log
from ESP.utils.utils import queryset_iterator



class NISTPositiveHeuristic(BaseLabResultHeuristic): 
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    
    def __init__(self, test_name, date_field='order'):
        '''
        test names
        '''
        assert test_name
        self.test_name = test_name
        self.date_field = date_field
    
    @property
    def short_name(self):
        name = 'labresult:%s:positive' % self.test_name
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:positive:v1'
    
    @property
    def positive_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'lx:%s:positive' % self.test_name
        else:
            return u'lx:%s:positive:%s-date' % (self.test_name, self.date_field)
    
    @property
    def negative_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'lx:%s:negative' % self.test_name
        else:
            return u'lx:%s:negative:%s-date' % (self.test_name, self.date_field)
    
    @property
    def indeterminate_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'lx:%s:indeterminate' % self.test_name
        else:
            return u'lx:%s:indeterminate:%s-date' % (self.test_name, self.date_field)
    
    @property
    def event_names(self):
        return [self.positive_event_name, self.negative_event_name, self.indeterminate_event_name]
    
    def generate(self):
        #
        log.debug('Generating events for "%s"' % self)
        #
        map_qs = LabTestMap.objects.filter(test_name=self.test_name)
        if not map_qs:
            log.warning('No tests mapped for "%s", cannot generate events.' % self.test_name)
            return 0
        #
        # this is a stub heuristic for use with NIST test data -- all labs in test data are "positive"
        #
        lab_q = None
        for map in map_qs:
            if not lab_q:
                lab_q = map.lab_results_q_obj
            else:
                lab_q |= map.lab_results_q_obj
        # Generate Events
        #
        positive_labs = self.unbound_labs.filter(lab_q)
        #log_query('Positive labs for %s' % self.uri, positive_labs)
        log.info('Generating positive events for %s' % self)
        #for lab in positive_labs.iterator():
        pos_counter = 0
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.positive_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            pos_counter += 1
        log.info('Generated %s new positive events for %s' % (pos_counter, self))
        return pos_counter

class NISTPositiveTestDiseaseDefinition(DiseaseDefinition):
    '''
    Defines a single NIST test condition.
    '''

    #__metaclass__ = abc.ABCMeta
    
    #
    # Abstract class interface
    #
    
    @abc.abstractproperty
    def condition(self):
        '''
        Condition (singular) which this disease definition can detect.
        @rtype: String
        '''
        
    @abc.abstractproperty
    def test_names(self):
        '''
        Names of abstract lab tests for which a single positive equals a case
        @rtype: [String, String, ...]
        '''
    
    @abc.abstractproperty
    def recurrence_interval(self):
        '''
        The minimum number of days which must elapse after a the date of a
        case, before another case can be declared.  
        @return: Number of days or None if disease cannot recur
        @rtype: Integer or None.
        '''
    @property
    def event_heuristics(self):
        '''
        Event heuristics on which this disease definition depends.
        @rtype: List of EventHeuristic instances
        '''
        heuristics = set()
        for test_name in self.test_names:
            heuristics.add( NISTPositiveHeuristic(test_name=test_name) )
        return heuristics
    
    @property
    def conditions(self):
        '''
        Conditions (plural) which this disease definition can detect
        @rtype: List of strings
        '''
        assert str(self.condition) == self.condition # Sanity check, condition must be a string
        return [self.condition]
    
    timespan_heuristics = [] # This type of definition never uses timespans.
    
    def generate(self):
        '''
        Examine the database and generate new cases of this disease
        @return: The count of new cases generated
        @rtype:  Integer
        '''
        log.info('Generating cases of %s' % self.short_name)
        pos_event_names = set()
        
        for heuristic in self.event_heuristics:
            pos_event_names.add(heuristic.positive_event_name)
        event_qs = Event.objects.filter(name__in=pos_event_names,
                                        patient__natural_key__in=self.nat_keys)
        new_case_count = self._create_cases_from_event_qs(
            condition = self.condition, 
            criteria = 'positive lab test', 
            recurrence_interval = self.recurrence_interval, 
            event_qs = event_qs, 
            relevant_event_names = pos_event_names,
            )
        log.debug('Generated %s new cases of %s' % (new_case_count, self.short_name))
        
        return new_case_count

NIST_CONFIG = [
    {
        'condition': 'lead',
        'short_name': 'lead',
        'test_names' : ['lead'],
        'test_name_search_strings': ['lead'],
        'nat_keys': ['001.01','002.03'],
        'recurrence_interval': 0
    },
    {
        'condition': 'alt',
        'short_name': 'alt',
        'test_names' : ['alt'],
        'test_name_search_strings': ['alanine aminotransferase'],
        'nat_keys': ['001.02'],
        'recurrence_interval': 0
    },
    {
        'condition': 'cd4',
        'short_name': 'cd4',
        'test_names' : ['cd4'],
        'test_name_search_strings': ['cd4'],
        'nat_keys': ['001.03'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'cadmium',
        'short_name': 'cadmium',
        'test_names' : ['cadmium'],
        'test_name_search_strings': ['cadmium'],
        'nat_keys': ['002.01','002.02'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'Bacteria',
        'short_name': 'Bacteria',
        'test_names' : ['Bacteria'],
        'test_name_search_strings': ['Bacteria'],
        'nat_keys': ['003.01','003.02','003.03','009.01'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'CST-4_1',
        'short_name': 'CST-4_1',
        'test_names' : ['Bacteria', 'amoxicillin+clavulanate', 'trimethoprim+sulfamethoxazole', 'ciprofloxacin'],
        'test_name_search_strings': ['Bacteria', 'amoxicillin', 'trimethoprim','ciprofloxacin'],
        'nat_keys': ['004.01'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'CST-4_2',
        'short_name': 'CST-4_2',
        'test_names' : ['microorganism','streptomycin', 'isoniazid', 'rifampin','ethambutol'],
        'test_name_search_strings': ['microorganism','streptomycin', 'isoniazid', 'rifampin','ethambutol'],
        'nat_keys': ['004.02'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'CST-4_3',
        'short_name': 'CST-4_3',
        'test_names' : ['Bacteria', 'amoxicillin+clavulanate', 'ceftriaxone', 'clindamycin','cefotaxime','cefuroxime parenteral', 'erythromycin', 'cefepime', 'levofloxacin', 'meropenem', 'penicillin', 'vancomycin'],
        'test_name_search_strings': ['Bacteria', 'amoxicillin+clavulanate', 'ceftriaxone', 'clindamycin','cefotaxime','cefuroxime parenteral', 'erythromycin', 'cefepime', 'levofloxacin', 'meropenem', 'penicillin', 'vancomycin'],
        'nat_keys': ['004.03'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'FQR-5A1-B1',
        'short_name': 'FQR-5A1-B1',
        'test_names' : ['hepatitis a','hepatitis b','hepatitis c' ],
        'test_name_search_strings': ['hepatitis a','hepatitis b','hepatitis c'],
        'nat_keys': ['005A.01','005B.01'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'hep-c',
        'short_name': 'hep-c',
        'test_names' : ['hepatitis c'],
        'test_name_search_strings': ['hepatitis c'],
        'nat_keys': ['005A.03','005B.03'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'dengue',
        'short_name': 'dengue',
        'test_names' : ['dengue'],
        'test_name_search_strings': ['dengue'],
        'nat_keys': ['006.01'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'reagin-ab',
        'short_name': 'reagin-ab',
        'test_names' : ['reagin ab'],
        'test_name_search_strings': ['reagin ab'],
        'nat_keys': ['006.02'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'west-nile',
        'short_name': 'west-nile',
        'test_names' : ['west nile'],
        'test_name_search_strings': ['west nile'],
        'nat_keys': ['006.03'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'BP-7_1',
        'short_name': 'BP-7_1',
        'test_names' : ['bordetella pertussis'],
        'test_name_search_strings': ['bordetella pertussis'],
        'nat_keys': ['007.01'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'influenza',
        'short_name': 'influenza',
        'test_names' : ['influenza'],
        'test_name_search_strings': ['influenza'],
        'nat_keys': ['007.02'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'tb',
        'short_name': 'tb',
        'test_names' : ['mycobacterium tuberculosis'],
        'test_name_search_strings': ['mycobacterium tuberculosis'],
        'nat_keys': ['007.03'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'G-C-8_1',
        'short_name': 'G-C-8_1',
        'test_names' : ['neisseria gonorrhoeae','chlamydia trachomatis'],
        'test_name_search_strings': ['neisseria gonorrhoeae','chlamydia trachomatis'],
        'nat_keys': ['008.01'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'MQ-8_2',
        'short_name': 'MQ-8_2',
        'test_names' : ['adenovirus','influenza','parainfluenza','respiratory syncytial virus','rhinovirus','human metapneumovirus'],
        'test_name_search_strings': ['adenovirus','influenza','parainfluenza','respiratory syncytial virus','rhinovirus','human metapneumovirus'],
        'nat_keys': ['008.02'],
        'recurrence_interval': 0
    },    
    {         
        'condition': 'measles',
        'short_name': 'measles',
        'test_names' : ['measles'],
        'test_name_search_strings': ['measles'],
        'nat_keys': ['008.03'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'Myco-sp',
        'short_name': 'Myco-sp',
        'test_names' : ['mycobacterium sp'],
        'test_name_search_strings': ['mycobacterium sp'],
        'nat_keys': ['009.02'],
        'recurrence_interval': 0
    },             
    {         
        'condition': 'microorg',
        'short_name': 'microorg',
        'test_names' : ['microorganism'],
        'test_name_search_strings': ['microorganism'],
        'nat_keys': ['009.03','009.03alt'],
        'recurrence_interval': 0
    },             
            
    ]

all_conditions = []
all_heuristics = []
for i in NIST_CONFIG:
    class NistCondition(NISTPositiveTestDiseaseDefinition):
        '''
        A pseudo-disease for NIST Meaningful Use Lab Reporting Test 
        '''        
        condition = "nist:" + i['condition']
        short_name = "nist:" + i['short_name']
        uri = 'urn:x-esphealth:disease:commonwealth:%s:v1' % condition 
        test_names = i['test_names']
        test_name_search_strings = i['test_name_search_strings']
        recurrence_interval = i['recurrence_interval']
        nat_keys = i['nat_keys']
                    
    disease = NistCondition()
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
