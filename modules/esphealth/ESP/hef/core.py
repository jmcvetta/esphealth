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
# The HEF_CORE_URI string uniquely describes this version of HEF core.  
# It MUST be incremented whenever any core functionality is changed!
HEF_CORE_URI = 'https://esphealth.org/reference/hef/core/1.0'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


import abc

from pkg_resources import iter_entry_points

from django.db.models import Q
from django.utils.encoding import force_unicode
from django.utils.encoding import smart_str

from ESP.utils import log
from ESP.utils import log_query
from ESP.utils.utils import queryset_iterator
from ESP.static.models import Icd9
from ESP.conf.models import LabTestMap
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import LabOrder
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
    
    def create_event(self, patient, provider, date):
        '''
        Creates an event of this type
        @type patient: ESP.emr.models.Patient
        @type provider: ESP.emr.models.Provider
        @type date: datetime.date
        '''
        new_event = Event(
            name = self.name,
            uri = self.uri,
            patient = patient,
            provider = provider,
            date = date, 
            )
        new_event.save()
        log.debug('Created new event: %s' % new_event)
        return new_event


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
    
    @abc.abstractmethod
    def generate(self):
        '''
        Examine data and generate new objects
        @return: Count of new objects generated
        @rtype:  Integer
        '''
    
    def __str__(self):
        return smart_str(self.name)
    
    __registered_heuristics = {}
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known heuristics of any type
        @rtype:  List
        '''
        heuristics = set()
        heuristics.update(BaseEventHeuristic.get_all())
        heuristics.update(BaseTimespanHeuristic.get_all())
        heuristics = list(heuristics)
        heuristics.sort(key = lambda h: h.name)
        return heuristics


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
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known event heuristics
        @rtype:  List
        '''
        heuristics = set()
        for entry_point in iter_entry_points(group='esphealth', name='event_heuristics'):
            factory = entry_point.load()
            heuristics.update(factory())
        heuristics = list(heuristics)
        heuristics.sort(key = lambda h: h.name)
        return heuristics


class BaseTimespanHeuristic(BaseHeuristic):
    '''
    A heuristic for generating Timespans from Events
    (Abstract base class)
    '''
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known timespan heuristics
        @rtype:  List
        '''
        heuristics = set()
        for entry_point in iter_entry_points(group='esphealth', name='timespan_heuristics'):
            factory = entry_point.load()
            heuristics.update(factory())
        heuristics = list(heuristics)
        heuristics.sort(key = lambda h: h.name)
        return heuristics


class Icd9Query(object):
    '''
    A query for selecting encounters based on ICD9 codes
    '''
    
    def __init__(self, exact, starts_with, ends_with, contains):
        '''
        @param exact: Encounter must include this exact ICD9 code
        @type exact:  String
        #
        # We use "starts_with" instead of Django-style "startswith", to
        # discourage people from thinking this argument is case-sensistive,
        # like a Django startswith query would be.
        #
        # Let's hope we never need to deal with case-sensitive ICD9 codes.
        #
        @param starts_with: Encounter must include an ICD9 code starting with this string
        @type exact:  String
        @param ends_with: Encounter must include an ICD9 code ending with this string
        @type exact:  String
        @param contains: Encounter must include an ICD9 code containing this string
        @type exact:  String
        '''
        assert (exact or starts_with or ends_with or contains) # Sanity check
        self.exact = exact
        self.starts_with = starts_with
        self.ends_with = ends_with
        self.contains = contains
        
    
    def __get_icd9_q_obj(self):
        '''
        Returns a Q object suitable for selecting ICD9 objects that match this query
        '''
        q_obj = Q() # Null Q object
        if self.exact:
            q_obj &= Q(code__iexact=self.exact)
        if self.starts_with:
            q_obj &= Q(code__istartswith=self.starts_with)
        if self.ends_with:
            q_obj &= Q(code__iendswith=self.ends_with)
        if self.contains:
            q_obj &= Q(code__icontains=self.contains)
        return q_obj
    icd9_q_obj = property(__get_icd9_q_obj)
    
    def __get_encounters(self):
        codes = Icd9.objects.filter(self.icd9_q_obj)
        return Encounter.objects.filter(icd9_codes__in=codes)
    encounters = property(__get_encounters)

    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return 'ICD9 Query: %s | %s | %s | %s' % (self.exact, self.starts_with, self.ends_with, self.contains),
    verbose_name = property(__get_verbose_name)


class DiagnosisHeuristic(BaseHeuristic):
    '''
    A heuristic for detecting events based on one or more ICD9 diagnosis codes
    from a physician encounter.
    '''

    def __get_encounters(self):
        encs = Encounter.objects.none()
        for icd9_query in self.icd9query_set.all():
            encs |= icd9_query.encounters
        log_query('Encounters for %s' % self, encs)
        return encs
    encounters = property(__get_encounters)
    
    def __get_icd9_q_obj(self):
        q_obj = self.icd9query_set.all()[0].icd9_q_obj
        for icd9_query in self.icd9query_set.all()[1:]:
            q_obj |= icd9_query.icd9_q_obj
        return q_obj
    icd9_q_obj = property(__get_icd9_q_obj)
    
    def generate(self):
        icd9s = Icd9.objects.filter(self.icd9_q_obj)
        encounters = Encounter.objects.filter(icd9_codes__in=icd9s)
        encounters = encounters.exclude(tags__event__event_type__heuristic=self)
        log_query('Encounters for %s' % self.name, encounters)
        log.info('Generating events for "%s"' % self.verbose_name)
        event_type = EventType.objects.get(name='dx--%s' % self.name)
        for enc in queryset_iterator(encounters):
            new_event = Event(
                name = self.name,
                uri = self.uri,
                patient = enc.patient,
                date = enc.date,
                provider = enc.provider,
                )
            new_event.save()
            new_event.tag_object(enc)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (encounters.count(), self.name))
        return encounters.count()


class AbstractLabTest(object):
    '''
    Represents an abstract type of lab test
    '''
    
    def __init__(self, name, uri):
        '''
        @param name: Common English name for this ALT
        @type name:  String
        @param uri:  URI that uniquely describes this ALT
        @type uri:   String
        '''
        assert name and uri
        self.name = name
        self.uri = uri
        
        
    def __unicode__(self):
        return u'Abstract Lab Test - %s' % self.name
    
    def __get_lab_results(self):
        testmaps = LabTestMap.objects.filter(test_uri = self.uri).filter( Q(record_type='result') | Q(record_type='both') )
        qs = LabResult.objects.filter(native_code__in=testmaps.values('native_code'))
        log_query('Lab Results for %s' % self.name, qs)
        return qs
    lab_results = property(__get_lab_results)
    
    def __get_lab_orders(self):
        testmaps = LabTestMap.objects.filter(test_uri = self.uri).filter( Q(record_type='order') | Q(record_type='both') )
        qs = LabOrder.objects.filter(native_code__in=testmaps.values('native_code'))
        log_query('Lab Orders for %s' % self.name, qs)
        return qs
    lab_orders = property(__get_lab_orders)
    
    def __get_heuristic_set(self):
        heuristic_set = set(self.laborderheuristic_set.all())
        heuristic_set |= set(self.labresultanyheuristic_set.all())
        heuristic_set |= set(self.labresultpositiveheuristic_set.all())
        heuristic_set |= set(self.labresultratioheuristic_set.all())
        heuristic_set |= set(self.labresultrangeheuristic_set.all())
        heuristic_set |= set(self.labresultfixedthresholdheuristic_set.all())
        return heuristic_set
    heuristic_set = property(__get_heuristic_set)

    def generate(self):
        count = 0
        log.info('Generating events for %s' % self)
        for heuristic in self.heuristic_set:
            count += heuristic.generate()
        return count


