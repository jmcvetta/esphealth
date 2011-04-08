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


class Condition(object):
    '''
    A disease or medical condition
    '''
    
    def __init__(self, name, uri, description):
        '''
        @param name: Short English name for this condition
        @param uri: A URI that uniquely describes this condition
        @param description: Detailed description of this disease
        '''
        assert name and uri and description # Sanity check
        self.name = name
        self.uri = uri
        self.description = description
    
    @classmethod
    def condition_choices(cls):
        # TODO: write me!
        return ['foo', 'bar']

    @classmethod
    def all_test_name_search_strings(cls):
        # TODO: write me!
        return ['foo', 'bar']


class DiseaseDefinition(object):

    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def conditions(self):
        '''
        Conditions which this disease definition can detect
        @rtype: List of Condition objects
        '''
    
    @abc.abstractmethod
    def generate(self):
        '''
        Examine the database and generate new cases of this disease
        '''