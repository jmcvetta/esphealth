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
