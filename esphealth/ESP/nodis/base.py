'''
ESP Health
Notifiable Diseases Framework
Base Classes

@author: Jason McVetta <jason.mcvetta@heliotropi.cc>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


import abc
from pkg_resources import iter_entry_points

from ESP.settings import HEF_THREAD_COUNT
from ESP.utils import log
from ESP.hef.base import BaseHeuristic


class DiseaseDefinition(object):

    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def conditions(self):
        '''
        Conditions which this disease definition can detect
        @rtype: List of strings
        '''
        
    @abc.abstractproperty
    def short_name(self):
        '''
        Short name (SlugField-compatible) for this report.
        @rtype: String
        '''
    
    
    @abc.abstractproperty
    def uri(self):
        '''
        A URI which uniquely describes this disease definition
        @rtype: String
        '''
    
    @abc.abstractproperty
    def event_heuristics(self):
        '''
        Event heuristics on which this disease definition depends.
        @rtype: List of EventHeuristic instances
        '''
    
    @abc.abstractproperty
    def timespan_heuristics(self):
        '''
        Timespan heuristics on which this disease definition depends.
        @rtype: List of TimespanHeuristic instances
        '''
    
    @abc.abstractmethod
    def generate(self):
        '''
        Examine the database and generate new cases of this disease
        @return: The count of new cases generated
        @rtype:  Integer
        '''
        
    @abc.abstractproperty
    def test_name_search_strings(self):
        '''
        @return: A list of all strings to use when searching native lab test 
            names for tests potentially relevant to this disease.
        @rtype: [String, String, ...]
        '''
    
    @classmethod
    def get_all_test_name_search_strings(cls):
        '''
        @return: A list of all strings to use when searching native lab test 
            names for tests potentially relevant to any defined disease.
        @rtype: [String, String, ...]
        '''
        search_strings = set()
        for disdef in cls.get_all():
            [search_strings.add(s) for s in disdef.test_name_search_strings]
        search_strings = list(search_strings)
        search_strings.sort()
        return search_strings
    
    @classmethod
    def get_all_conditions(cls):
        '''
        @return: A list of all conditions which can be detected by 
            defined DiseaseDefinitions
        @rtype: [String, String, ...]
        '''
        conditions = set()
        for disdef in cls.get_all():
            [conditions.add(s) for s in disdef.conditions]
        conditions = list(conditions)
        conditions.sort()
        return conditions
    
    @classmethod
    def get_all_condition_choices(cls):
        '''
        @return: A list of tuples describing all detectable conditions, 
            suitable for use with Django forms.
        @rtype: [(String, String), (String, String), ...]
        '''
        return [(c, c) for c in cls.get_all_conditions()]
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known disease definitions
        @rtype:  List
        '''
        #
        # Retrieve from modules
        #
        diseases = []
        for entry_point in iter_entry_points(group='esphealth', name='disease_definitions'):
            factory = entry_point.load()
            diseases += factory()
        diseases.sort(key = lambda h: h.short_name)
        # 
        # Sanity check
        #
        names = {}
        uris = {}
        for d in diseases:
            if d.uri in uris:
                msg = 'Cannot load: %s' % d
                msg = 'Duplicate disease URI: "%s"' % d.uri
                log.critical(msg)
                raise RuntimeError(msg)
            else:
                uris[d.uri] = d
            if d.short_name in names:
                msg = 'Cannot load: %s' % d
                msg = 'Duplicate disease name "%s"' % d.short_name
                log.critical(msg)
                raise RuntimeError(msg)
            else:
                names[d.short_name] = d
        return diseases
    
    @classmethod
    def get_by_name(cls, short_name):
        '''
        Returns the named heuristic
        '''
        class UnknownDiseaseException(BaseException):
            '''
            Raised when a named disease cannot be found
            '''
        diseases = {}
        for d in cls.get_all():
            diseases[d.short_name] = d
        if not short_name in diseases:
            raise UnknownDiseaseException('Could not get disease definition for name: "%s"' % short_name)
        return diseases[short_name]
    
    @property
    def dependencies(self):
        '''
        Returns the set of all heuristics on which this disease definition depends
        '''
        heuristics = set()
        heuristics |= set(self.event_heuristics)
        heuristics |= set(self.timespan_heuristics)
        return heuristics
    
    def generate_dependencies(self, thread_count=HEF_THREAD_COUNT):
        '''
        Generates events & timespans for all heuristics on which this disease 
        definition depends.  
        '''
        log.info('Generating dependencies for %s' % self)
        return BaseHeuristic.generate_all(self.dependencies, thread_count)
    
        


class Report(object):
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def short_name(self):
        '''
        Short name (SlugField-compatible) for this report.
        '''
    
    @abc.abstractproperty
    def run(self):
        '''
        Run the report
        @return: The report as a printable string
        @rtype:  String
        '''

    @classmethod
    def get_all(cls):
        '''
        @return: All known reports
        @rtype:  List of Report child instances
        '''
        report_set = set()
        for entry_point in iter_entry_points(group='esphealth', name='reports'):
            factory = entry_point.load()
            report_set.update(factory())
        report_list = list(report_set)
        report_list.sort(key = lambda h: h.short_name)
        return report_list
    
