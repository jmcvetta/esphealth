'''
ESP Health
Notifiable Diseases Framework
Base Classes

@author: Carolina chacin <cchacin@commoninf.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


import abc
import sys
import datetime

from pkg_resources import iter_entry_points

from django.db.models.query import QuerySet

from ESP.settings import HEF_THREAD_COUNT
from ESP.settings import FILTER_CENTERS
from ESP.utils import log
from ESP.utils import log_query
from django.db.models import Q

from ESP.hef.base import BaseHeuristic, PrescriptionHeuristic
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.conf.models import ConditionConfig
from ESP.hef.models import Event
from ESP.nodis.models import Case
from ESP.utils.utils import wait_for_threads
from django.core.exceptions import ObjectDoesNotExist


class UnknownDiseaseException(BaseException):
    '''
    Raised when a named disease cannot be found
    '''
    pass

class DiseaseDefinition(object):

    __metaclass__ = abc.ABCMeta
    
    criteria = ''
    recurrence_interval = None
    #
    # Abstract class interface
    #
    
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
        A URI which uniquely describes this disease definition.  URIs should
        follow this general format:
            'urn:x-esphealth:disease:your_organization_name:disease_name:version'
        For example:
            'urn:x-esphealth:disease:channing:chlamydia:v1'
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
    
    @abc.abstractproperty
    def test_name_search_strings(self):
        '''
        @return: A list of all strings to use when searching native lab test 
            names for tests potentially relevant to this disease.
        @rtype: [String, String, ...]
        '''
        
    @abc.abstractmethod
    def generate(self):
        '''
        Examine the database and generate new cases of this disease
        @param dependencies: Should we generate dependency Events for this disease?
        @type dependencies:  Boolean
        @return: The count of new cases generated
        @rtype:  Integer
        '''
    
    #-------------------------------------------------------------------------------
    #
    # Class Methods
    #
    #-------------------------------------------------------------------------------
    
    @classmethod
    def generate_dependencies(cls, disease_list, thread_count=HEF_THREAD_COUNT):
        '''
        Generate dependency Events and Timespans for a list of diseases
        @param disease_list: Generete dependencies for these diseases
        @type disease_list:  [DiseaseDefinition, DiseaseDefinition, ...]
        '''
        log.debug('Generating dependencies for %s' % cls)
        event_heuristics = set()
        timespan_heuristics = set()
        for disdef in disease_list:
            [event_heuristics.add(h) for h in disdef.event_heuristics]
            [timespan_heuristics.add(h) for h in disdef.timespan_heuristics]
        event_funcs = [h.generate for h in event_heuristics]
        timespan_funcs = [h.generate for h in timespan_heuristics]
        counter = 0
        counter += wait_for_threads(event_funcs, max_workers=thread_count)
        counter += wait_for_threads(timespan_funcs, max_workers=thread_count)
        return counter
    
    @classmethod
    def generate_all(cls, disease_list=None, dependencies=False, thread_count=HEF_THREAD_COUNT):
        '''
        Generate cases for all DiseaseDefinition instances.
        @param disease_list: If specified, generete cases only for these diseases
        @type disease_list:  [DiseaseDefinition, DiseaseDefinition, ...]
        @param dependecies: Should we generate dependency Events and Timespans?
        @type dependecies:  Boolean
        '''
        if disease_list:
            for this_disease in disease_list:
                assert isinstance(this_disease, cls)
        else:
            disease_list = cls.get_all()
        log.debug('Diseases to be generated: %s' % disease_list)
        if dependencies:
            cls.generate_dependencies(disease_list, thread_count)
        funcs = [this_disease.generate for this_disease in disease_list]
        counter = wait_for_threads(funcs, max_workers=thread_count)
        log.info('Generated %20s cases' % counter)
        return counter
    
    @classmethod
    def get_all_test_name_search_strings(cls):
        '''
        @return: A list of all strings to use when searching native lab test 
            names for tests potentially relevant to any defined disease.
        @rtype: [String, String, ...]
        '''
        search_strings = set()
        for disdef in cls.get_all():
            try:
                [search_strings.add(s) for s in disdef.test_name_search_strings]
            except:
                err_msg = 'Invalid search strings in %s' % disdef
                log.error(err_msg)
                raise sys.exc_info()
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
            try:
                [conditions.add(s) for s in disdef.conditions]
            except:
                err_msg = 'Problem with condition string in %s' % disdef
                log.error(err_msg)
                raise sys.exc_info()
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
    def get_by_short_name(cls, short_name):
        '''
        Returns the disease specified by short name
        '''
        diseases = {}
        all = cls.get_all()
        #Special case to handle diabetes conditions where 
        #multiple conditions are handled by a single class
        if short_name.find('diabetes')>-1:
            short_name = 'diabetes'
        for d in all:
            diseases[d.short_name] = d
        if not short_name in diseases:
            raise UnknownDiseaseException('Could not get disease definition for name: "%s"' % short_name)
        return diseases[short_name]
    
    @classmethod
    def get_by_uri(cls, uri):
        '''
        Returns the disease indicated by URI
        '''
        diseases = {}
        for d in cls.get_all():
            diseases[d.uri] = d
        if not uri in diseases:
            raise UnknownDiseaseException('Could not get disease definition for uri: "%s"' % uri)
        return diseases[uri]
    
    def __get_medications(self):
        ''' 
        Returns set of medication names used in this condition's definition.
        '''
        med_names = set()
        for heuristics in self.event_heuristics:
            if isinstance(heuristics, PrescriptionHeuristic):
                med_names |= set( heuristics.drugs )
        return med_names
    medications = property(__get_medications)
    
    #-------------------------------------------------------------------------------
    #
    # Instance methods
    #
    #-------------------------------------------------------------------------------
    
    def _create_case_from_event_obj(self,
        condition,
        criteria,
        recurrence_interval,
        event_obj, 
        relevant_event_names = [],
        relevant_event_qs = None,
        ):
        '''
        Create a new case for specified event object.
        @param condition: Create a case of this condition
        @type condition:  String
        @param criteria: Criteria for creating these cases
        @type criteria:  String
        @param recurrence_interval: How many days after a case until this condition can recur?
        @type recurrence_interval: Integer or None (if condition cannot recur)
        @param event_obj: Event on which to base new case
        @type event_obj:  models.Model chil instance
        @param relevant_event_qs: Attach these events to a new case
        @type relevant_event_qs:  QuerySet instance
        @param relevant_event_names: Attach events matching with these names to new case
        @type relevant_event_names:  [String, String, ...]
        @return: Was new case created, and case object (new or existing) to which event was attached
        @rtype: (Bool, Case)
        '''
        # 
        # Check recurrence
        #
        if recurrence_interval is None:
            # Non-recurring condition - once you have it, you've always 
            # got it.
            existing_cases = Case.objects.filter(
                patient = event_obj.patient,
                condition = condition,
                ).order_by('date')
        else:
            delta = datetime.timedelta(days=recurrence_interval)
            max_date = event_obj.date + delta
            min_date = event_obj.date - delta
            existing_cases = Case.objects.filter(
                patient = event_obj.patient,
                condition = condition,
                date__gte = min_date,
                date__lte = max_date,
                ).order_by('date')
        # If this patient has an existing case, we attach this event 
        # to that case and continue.
        
        if existing_cases:
            first_case = existing_cases[0] 
            first_case.events.add(event_obj)
            # redmine 467 transition existing 'S' status cases from 'S' to 'RQ' 
            # whenever events are added to an existing case.
            if (first_case.status == 'S'):
                first_case.status = 'RQ'
            first_case.save()
            
            log.debug('Added %s to %s' % (event_obj, first_case))
            return (False, first_case)
        #
        # Create new case
        #
        try:
            #redmine 491, by default FILTER_CENTERS has one element with an empty list.
            if ( FILTER_CENTERS[0]=='' or (FILTER_CENTERS and event_obj.patient.center_id in FILTER_CENTERS )):
                status=ConditionConfig.objects.get(name=condition).initial_status
            else:
                status='AR'
        except ObjectDoesNotExist:
            status='AR'
        new_case = Case(
            patient = event_obj.patient,
            provider = event_obj.provider,
            date = event_obj.date,
            condition =  condition,
            criteria = criteria,
            source = self.uri,
            status = status,
            )
        new_case.save()
        new_case.events.add(event_obj)
        #
        # Attach all relevant events, that are not already attached to a
        # case of this condition.
        #
        if relevant_event_names:
            all_relevant_events = Event.objects.filter(
                patient=event_obj.patient,
                name__in=relevant_event_names,
                ).exclude(
                    case__condition=condition,
                    )
            for related_event in all_relevant_events:
                new_case.events.add(related_event)
            new_case.save()
        if relevant_event_qs:
            relevant_event_qs = relevant_event_qs.filter(patient=event_obj.patient)
            for this_event in relevant_event_qs:
                new_case.events.add(this_event)
        new_case.save()
        log.debug('Created new case: %s' % new_case)
        return (True, new_case)
    
    
    def _create_cases_from_event_qs(self, 
        condition,
        criteria,
        recurrence_interval,
        event_qs, 
        relevant_event_names = [],
        ):
        '''
        For each event in an Event QuerySet, either attach the event to an
            exiting case, or create a new case
        @param condition: Create a case of this condition
        @type condition:  String
        @param criteria: Criteria for creating these cases
        @type criteria:  String
        @param recurrence_interval: How many days after a case until this condition can recur?
        @type recurrence_interval: Integer or None (if condition cannot recur)
        @param event_qs: Events on which to base n
        @type event_qs:  QuerySet instance
        @param relevant_event_names: Attach events matching with these names to new case
        @type relevant_event_names:  [String, String, ...]
        '''
        counter = 0
        event_qs = event_qs.exclude(case__condition=condition)
        event_qs = event_qs.order_by('patient', 'date')
        #log_query('Events for %s' % self.short_name, event_qs)
        for this_event in event_qs:
            created, this_case = self._create_case_from_event_obj(
                condition = condition, 
                criteria = criteria, 
                recurrence_interval = recurrence_interval, 
                event_obj = this_event, 
                relevant_event_names = relevant_event_names,
                )
            if created:
                counter += 1
        return counter
        


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

class SinglePositiveTestDiseaseDefinition(DiseaseDefinition):
    '''
    Defines a single condition, for which a single positive test from a given
    set is sufficient to detect a case.
    '''

    #__metaclass__ = abc.ABCMeta
    
    #
    # Abstract class interface
    #
    
    criteria = ''
    
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
            heuristics.add( LabResultPositiveHeuristic(test_name=test_name) )
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
        event_qs = Event.objects.filter(name__in=pos_event_names)
        new_case_count = self._create_cases_from_event_qs(
            condition = self.condition, 
            criteria = self.criteria + ' Single positive lab test', 
            recurrence_interval = self.recurrence_interval, 
            event_qs = event_qs, 
            relevant_event_names = pos_event_names,
            )
        log.debug('Generated %s new cases of %s' % (new_case_count, self.short_name))
        
        return new_case_count
    
class ReinfectionDiseaseDefinition (DiseaseDefinition):
    '''
    Defines a single condition, for which a single positive test from a given
    set is sufficient to detect a case and has reinfection events 
    '''

    #__metaclass__ = abc.ABCMeta
    
    #
    # Abstract class interface
    #
    
    criteria = ''
    
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
            heuristics.add( LabResultPositiveHeuristic(test_name=test_name) )
        return heuristics
    
    @property
    def reinfection(self):
        '''
        retreives the reinfection days from the configuration
        '''
        reinfection_days = ConditionConfig.objects.get(name=self.condition).reinfection_days
        if not reinfection_days:
            return 0
        else:
            return reinfection_days
        
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
        log.info('Generating cases of %s with Reinfection' % self.short_name)
        pos_event_names = set()
        
        for heuristic in self.event_heuristics:
            pos_event_names.add(heuristic.positive_event_name)
        event_qs = Event.objects.filter(name__in=pos_event_names)
        new_case_count = self._create_cases_from_event_qs(
            condition = self.condition, 
            criteria = self.criteria + ' Single positive lab test with reinfection' , 
            recurrence_interval = self.recurrence_interval, 
            event_qs = event_qs, 
            relevant_event_names = pos_event_names,
            )
        
        log.debug('Generated %s new cases of %s with Reinfection' % (new_case_count, self.short_name))
        
        '''
        reinfection logic
        checks for events that happened within the window of reinfection days .
        This window starts from the end of the reinfection window. 
        It will add the events found to the existing cases as a followup_event 
        and change the status to RQ if the status is S for the existing cases
        '''
        if self.reinfection >0:
            all_event_names = set()
            for heuristic in self.event_heuristics:
                for name in heuristic.event_names:
                    all_event_names.add(name)   
                 
            q_obj = Q(patient=event_qs[0].patient, name__in=all_event_names)
            case_start = event_qs[0].date - datetime.timedelta(days=self.recurrence_interval) - datetime.timedelta(days=self.reinfection) 
            case_end = event_qs[0].date 
            q_obj = Q(patient=event_qs[0].patient, condition = self.condition)
            q_obj &= Q(date__gte = case_start )
            q_obj &= Q(date__lte = case_end )
            cases  = Case.objects.filter(q_obj)
            for case in cases:
                event_start = case.date + datetime.timedelta(days=self.recurrence_interval) 
                event_end  = event_start + datetime.timedelta(days=self.reinfection)  
                q_obj = Q(patient=event_qs[0].patient, name__in=all_event_names)
                q_obj &= Q(date__gte = event_start )
                q_obj &= Q(date__lte = event_end )
                followup_events = Event.objects.filter( q_obj).order_by('date')
                #add events to follow up of these cases 
                if followup_events:
                    for event in followup_events:
                        if not case.followup_events.all() or event not in case.followup_events.all():
                            case.followup_events.add(event)
                            #change the status of all the cases in this query set
                            if (case.status == 'S' or case.status == 'RS') and not case.followup_sent :
                                log.info('Requeing cases of %s with Reinfection' % self.short_name)
                                case.status = 'RQ'
                                case.followup_sent = True
                        
                case.save()
        return new_case_count
        