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

import abc
from ESP.nodis.base import DiseaseDefinition
from ESP.hef.base import BaseLabResultHeuristic
from ESP.hef.models import Event
from ESP.conf.models import LabTestMap
from ESP.nodis.base import Case
from ESP.utils import log
from ESP.utils.utils import queryset_iterator


class ODHPositiveHeuristic(BaseLabResultHeuristic): 
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    
    def __init__(self, test_name, date_field='order', titer_dilution=None):
        '''
        @param titer_dilution: The demoninator showing titer dilution
        @type  titer_dilution: Integer
        '''
        assert test_name
        self.test_name = test_name
        self.date_field = date_field
        if titer_dilution:
            assert isinstance(titer_dilution, int)
            self.titer_dilution = titer_dilution
        else:
            self.titer_dilution = None
    
    @property
    def short_name(self):
        name = 'labresult:%s:positive' % self.test_name
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        if self.titer_dilution:
            name += ':titer:%s' % self.titer_dilution
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
        # TODO: issue 334 The negative and indeterminate query sets should be generated 
        # *after* creating of preceding queries' events, so that labs bound to 
        # those events are ignored.  This will allow negative lab query to much
        # simpler.
        #
        log.debug('Generating events for "%s"' % self)
        #
        # Build numeric query
        #
        #--------------------------------------------------------------------------------
        # Not doing abnormal flag yet, because many values are not null but a blank string
        #
        #if result_type == 'positive':
            #pos_q = Q(abnormal_flag__isnull=False)
        #else:
            #pos_q = None
        #--------------------------------------------------------------------------------
        map_qs = LabTestMap.objects.filter(test_name=self.test_name)
        if not map_qs:
            log.warning('No tests mapped for "%s", cannot generate events.' % self.test_name)
            return 0
        #
        # All labs can be classified pos/neg if they have reference high and 
        # numeric result
        #
        ref_high_float_q = Q(ref_high_float__isnull=False)
        result_float_q = Q(result_float__isnull=False)
        numeric_q = ref_high_float_q & result_float_q
        positive_q = ( numeric_q & Q(result_float__gte = F('ref_high_float')) )
        negative_q = ( numeric_q & Q(result_float__lt = F('ref_high_float')) )
        indeterminate_q = None
        xpositive_q = None
        xnegative_q = None
        xindeterminate_q = None
        all_labs_q = None
        #
        # Build queries with custom result strings or fallback thresholds
        #
        simple_strings_lab_q = None
        for map in map_qs:
            lab_q = map.lab_results_q_obj
            #
            # Labs mapped with extra result strings need to be handled specially
            #
            if map.extra_positive_strings.all() \
                or map.extra_negative_strings.all() \
                or map.extra_indeterminate_strings.all() \
                or map.excluded_positive_strings.all() \
                or map.excluded_negative_strings.all() \
                or map.excluded_indeterminate_strings.all():
                if xpositive_q:
                    xpositive_q |= (map.positive_string_q_obj & lab_q)
                else:
                    xpositive_q = (map.positive_string_q_obj & lab_q)
                if xnegative_q:
                    xnegative_q |= (map.negative_string_q_obj & lab_q)
                else:
                    xnegative_q = (map.negative_string_q_obj & lab_q)
                if xindeterminate_q:
                    xindeterminate_q |= (map.indeterminate_string_q_obj & lab_q)
                else:
                    xindeterminate_q = (map.indeterminate_string_q_obj & lab_q)
                continue
            if all_labs_q:
                all_labs_q |= lab_q
            else:
                all_labs_q = lab_q
            # Threshold criteria is *in addition* to reference high
            if map.threshold:
                num_lab_q = (lab_q & result_float_q)
                positive_q |= ( num_lab_q & Q(result_float__gte=map.threshold) )
                negative_q |= ( num_lab_q & Q(result_float__lt=map.threshold) )
            if simple_strings_lab_q:
                simple_strings_lab_q |= lab_q
            else:
                simple_strings_lab_q = lab_q
        #
        # All labs in the simple_strings_lab_q can be queried using the standard
        # set of result strings
        #
        if simple_strings_lab_q:
            pos_rs_q = ResultString.get_q_by_indication('pos')
            neg_rs_q = ResultString.get_q_by_indication('neg')
            ind_rs_q = ResultString.get_q_by_indication('ind')
            positive_q |= (simple_strings_lab_q & pos_rs_q)
            negative_q |= (simple_strings_lab_q & neg_rs_q)
            if indeterminate_q:
                indeterminate_q |= (simple_strings_lab_q & ind_rs_q)
            else:
                indeterminate_q = (simple_strings_lab_q & ind_rs_q)
        #
        # Add titer string queries
        #
        if self.titer_dilution:
            positive_q=None
            negative_q=None
            positive_titer_strings = ['1:%s' % 2**i for i in range(int(math.log(self.titer_dilution, 2)), int(math.log(4096,2)))]
            negative_titer_strings = ['1:%s' % 2**i for i in range(int(math.log(self.titer_dilution, 2)))]
            log.debug('positive_titer_strings: %s' % positive_titer_strings)
            log.debug('negative_titer_strings: %s' % negative_titer_strings)
            for s in positive_titer_strings:
                if positive_q:
                    positive_q |= Q(result_string__icontains=s)
                else: 
                    positive_q = Q(result_string__icontains=s)
            for s in negative_titer_strings:
                if negative_q:
                    negative_q |= Q(result_string__icontains=s)
                else:
                    negative_q = Q(result_string__icontains=s)
        positive_q = all_labs_q & positive_q
        negative_q = all_labs_q & negative_q
        indeterminate_q = all_labs_q & indeterminate_q
        if xpositive_q:
            positive_q = (positive_q) | (xpositive_q)
        if xnegative_q:
            negative_q = (negative_q) | (xnegative_q)
        if xindeterminate_q:
            indeterminate_q = (indeterminate_q) | (xindeterminate_q)
        #
        # Generate Events
        #
        positive_labs = self.unbound_labs.filter(positive_q)
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
        negative_labs = self.unbound_labs.filter(negative_q)
        #log_query('Negative labs for %s' % self, negative_labs)
        log.info('Generating negative events for %s' % self)
        neg_counter = 0
        for lab in queryset_iterator(negative_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.negative_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            neg_counter += 1
        log.info('Generated %s new negative events for %s' % (neg_counter, self))
        indeterminate_labs = self.unbound_labs.filter(indeterminate_q)
        #log_query('Indeterminate labs for %s' % self, indeterminate_labs)
        log.info('Generating indeterminate events for %s' % self)
        ind_counter = 0
        for lab in queryset_iterator(indeterminate_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.indeterminate_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            ind_counter += 1
        log.info('Generated %s new indeterminate events for %s' % (ind_counter, self))
        return pos_counter + neg_counter + ind_counter
    

class ODHPositiveTestDiseaseDefinition(DiseaseDefinition):
    '''
    Defines a single ODH test condition.
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
            heuristics.add( ODHPositiveHeuristic(test_name=test_name) )
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

ODH_CONFIG = [
    {    
        'condition': 'chlamydia',    
        'short_name': 'chlamydia',    
        'test_names' : ['chlamydia'],    
        'test_name_search_strings': ['chlam','trac'],    
        'recurrence_interval': 0    
    },             
            
    ]

all_conditions = []
all_heuristics = []
for i in ODH_CONFIG:
    class ODHCondition(ODHPositiveTestDiseaseDefinition):
        '''
        A pseudo-disease for ODH Lab Reporting Test 
        '''        
        condition = "elr-odh:" + i['condition']
        short_name = "elr-odh:" + i['short_name']
        uri = 'urn:x-esphealth:disease:commonwealth:%s:v1' % condition 
        test_names = i['test_names']
        test_name_search_strings = i['test_name_search_strings']
        recurrence_interval = i['recurrence_interval']
        nat_keys = i['nat_keys']
                    
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
