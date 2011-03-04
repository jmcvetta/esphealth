'''
                              ESP Health Project
                          Heuristic Events Framework
                                  Core Logic

@author: Jason McVetta <jason.mcvetta@heliotropi.cc>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The VERSION_URI string uniquely describes this version of HEF core.  
# It MUST be incremented whenever any core functionality is changed!
VERSION_URI = 'https://esphealth.org/reference/hef/core/1.0'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


import abc

from django.db.models import Q
from django.utils.encoding import force_unicode
from django.utils.encoding import smart_str

from ESP.utils import log
from ESP.hef.models import Event


class EventType(object):
    '''
    A distinct type of medical event
    '''
    
    def __init__(self, name, uri):
        assert name
        assert uri
        self.__name = name
        self.__uri = uri
    
    def __get_name(self):
        '''
        Common English name for this kind of event
        '''
        return self.__name
    name = property(__get_name)
    
    def __get_uri(self):
        '''
        URI which uniquely describes this kind of event
        '''
        return self.__uri
    uri = property(__get_uri)


class BaseHeuristic(object):
    '''
    A heuristic for generating Events from raw medical records
    (Abstract base class)
    '''
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def name(self):
        '''
        Common English name for this heuristic
        '''
    
    @abc.abstractproperty
    def uri(self):
        '''
        URI which uniquely describes this heuristic, including its version
        '''
    
    @abc.abstractproperty
    def core_uris(self):
        '''
        A list of one or more URIs indicating the version(s) of HEF core with 
        which this heuristic is compatible
        '''
    
    def __str__(self):
        return smart_str(self.name)
    

class BaseEventHeuristic(BaseHeuristic):
    '''
    A heuristic for generating Events from raw medical records
    (Abstract base class)
    '''
    
    @abc.abstractproperty
    def event_types(self):
        '''
        A list of one or more EventType objects describing all the possible 
        event types this heuristic can generate
        '''

    @abc.abstractmethod
    def generate_events(self):
        '''
        Generate Event objects from raw medical records in database
        '''
    
    @property
    def event_uri_q(self):
        '''
        Returns a Q object to select events related to this heuristic based 
        on their URI.
        '''
        q_obj = None
        for et in self.event_types:
            if q_obj:
                q_obj |= Q(uri=et.uri)
            else:
                q_obj = Q(uri=et.uri)
        return q_obj
    
    @property
    def bound_record_q(self):
        '''
        Returns a Q object to select EMR records which are bound to events 
        related to this heuristic.
        '''
        event_qs = Event.objects.filter(self.event_uri_q)
        q_obj = Q(tags__event__in=event_qs)
        return q_obj


class BaseTimespanHeuristic(BaseHeuristic):
    '''
    A heuristic for generating Timespans from Events
    (Abstract base class)
    '''
    
    @abc.abstractmethod
    def generate_timespans(self):
        '''
        Generate Event objects from raw medical records in database
        '''
