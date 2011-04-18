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
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known disease definitions
        @rtype:  List
        '''
        diseases = set()
        for entry_point in iter_entry_points(group='esphealth', name='disease_definitions'):
            factory = entry_point.load()
            diseases.update(factory())
        diseases = list(diseases)
        diseases.sort(key = lambda h: h.uri)
        return diseases
    
    def generate_dependencies(self, thread_count=HEF_THREAD_COUNT):
        '''
        Generates events & timespans for all heuristics on which this disease 
        definition depends.  
        '''
        log.info('Generating dependencies for %s' % self)
        heuristic_list = []
        heuristic_list.extend(self.event_heuristics)
        heuristic_list.extend(self.timespan_heuristics)
        log.debug('heuristic_list: %s' % heuristic_list)
        return BaseHeuristic.generate_all(heuristic_list, thread_count)
    
        


class Report(object):
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def short_name(self):
        '''
        Short name (SlugField-compatible) for this report.
        '''
    
    @abc.abstractproperty
    def generate(self):
        '''
        Produce the report
        @return: The report as a printable string
        @rtype:  String
        '''
