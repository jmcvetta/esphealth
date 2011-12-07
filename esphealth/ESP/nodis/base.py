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
import sys
import datetime
import settings

from pkg_resources import iter_entry_points

from ESP.settings import HEF_THREAD_COUNT
from ESP.utils import log
from ESP.utils import log_query

from ESP.hef.base import BaseHeuristic
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.hef.models import Event
from ESP.nodis.models import Case


class DiseaseDefinition(object):

    __metaclass__ = abc.ABCMeta
    
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
        @return: The count of new cases generated
        @rtype:  Integer
        '''
    
    #
    # Concrete members
    #
    
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
    
    def _create_cases_from_events(self, 
        condition,
        criteria,
        recurrence_interval,
        event_qs, 
        relevent_event_names,
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
        @param relevent_event_q_obj: Attach events matching this filter to a new case
        @type relevent_event_q_obj:  Q instance
        '''
        counter = 0
        # Skip events that are already bound to a case of this condition
        event_qs = event_qs.exclude(case__condition=condition)
        for this_event in event_qs:
            existing_cases = Case.objects.filter(
                condition = condition,
                patient = this_event.patient,
                )
            if recurrence_interval:
                existing_cases = existing_cases.filter(
                    date__gte=(this_event.date - relativedelta(days=recurrence_interval) )
                    )
            existing_cases = existing_cases.order_by('date')
            if existing_cases:
                old_case = existing_cases[0]
                old_case.events.add(this_event)
                old_case.save()
                log.debug('Added %s to %s' % (this_event, old_case))
                continue # Done with this event, continue loop
            # No existing case, so we create a new case
            new_case = Case(
                condition = condition,
                patient = this_event.patient,
                provider = this_event.provider,
                date = this_event.date,
                criteria = criteria,
                source = self.uri,
                )
            new_case.save()
            new_case.events.add(this_event)
            #
            # Attach all relevant events, that are not already attached to a
            # case of this condition.
            #
            all_relevant_events = Event.objects.filter(
                patient=this_event.patient,
                name__in=relevent_event_names,
                ).exclude(
                    case__condition=condition,
                    )
            for related_event in all_relevant_events:
                new_case.events.add(related_event)
            new_case.save()
            log.info('Created new case: %s' % new_case)
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
        pos_events = set()
        for heuristic in self.event_heuristics:
            pos_events.add(heuristic.positive_event_name)
        qs = Event.objects.filter(name__in=pos_events)
        qs = qs.exclude(case__condition=self.condition)
        qs = qs.order_by('patient', 'date')
        counter = 0
        log_query('Events for %s' % self.short_name, qs)
        for ev in qs:
            # 
            # Check recurrence
            #
            if self.recurrence_interval is None:
                # Non-recurring condition - once you have it, you've always 
                # got it.
                existing_cases = Case.objects.filter(
                    patient = ev.patient,
                    condition = self.condition,
                    ).order_by('date')
            else:
                delta = datetime.timedelta(days=self.recurrence_interval)
                max_date = ev.date + delta
                min_date = ev.date - delta
                existing_cases = Case.objects.filter(
                    patient = ev.patient,
                    condition = self.condition,
                    date__gte = min_date,
                    date__lte = max_date,
                    ).order_by('date')
            # If this patient has an existing case, we attach this event 
            # to that case and continue.
            if existing_cases:
                first_case = existing_cases[0] 
                first_case.events.add(ev)
                first_case.save()
                log.debug('Added %s to %s' % (ev, first_case))
                continue
            #
            # Create new case
            #
            new_case = Case(
                patient = ev.patient,
                provider = ev.provider,
                date = ev.date,
                condition =  self.condition,
                criteria = 'Positive lab test',
                source = self.uri,
                )
            new_case.save()
            new_case.events.add(ev)
            new_case.save()
            log.debug('Created new Chlamydia case: %s' % new_case)
            counter += 1
        log.info('Generated %s cases of %s' % (counter, self.short_name))
        return counter
    
