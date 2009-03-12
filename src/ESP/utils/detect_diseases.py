#!/usr/bin/env python
'''
Detect cases of (reportable) disease
'''

import datetime
import pprint
import types
import sets

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP import settings
from ESP.esp import models
from ESP.utils import utils as util
from ESP.utils.utils import log


#===============================================================================
#
#--- ~~~ Exceptions ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HeuristicAlreadyRegistered(BaseException):
    '''
    A Heuristic instance has already been registered with the same name 
    as the instance you are trying to register.
    '''
    pass

class DiseaseDefinitionAlreadyRegistered(BaseException):
    '''
    A Disease_Definition instance has already been registered with the same 
    name as the instance you are trying to register.
    '''
    pass

class CaseAlreadyExists(BaseException):
    '''
    A case already exists for this disease + patient.
    '''
    pass


#===============================================================================
#
#--- ~~~ Heuristics Framework ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Heuristic:
    '''
    Abstract interface class for heuristics, concrete instances of which are
    used as components of disease definitions.
    '''
    
    def __init__(self, name, verbose_name=None):
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
    
    __registry = {} # Class variable
    def _register(self, allow_duplicate_name=False):
        '''
        Add this instance to the Heuristic registry
        '''
        name = self.name
        registry = self.__registry
        if allow_duplicate_name and name in registry:
            if not self in registry[name]:
                log.debug('Registering additional heuristic for name "%s".' % name)
                registry[name] += [self]
        elif name in registry:
            raise HeuristicAlreadyRegistered('A Heuristic instance is already registered with name "%s".' % name)
        else:
            log.debug('Registering heuristic with name "%s".' % name)
            registry[name] = [self]
    
    @classmethod
    def get_all_heuristics(cls):
        '''
        Returns a list of all registered Heuristic instances.
        '''
        result = []
        keys = cls.__registry
        keys.sort()
        [result.extend(cls.__registry[key]) for key in keys]
        log.debug('All Heuristic instances: %s' % result)
        return result
    
    def matches(self, begin_date=None, end_date=None):
        '''
        Return a QuerySet of matches for this heuristic
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
        
    def save_events(self, begin_date=None, end_date=None):
        '''
        Generate models.Heuristic_Event records for each item returned by
        matches, if it does not already have one.
        @return: Integer number of new records created
        '''
        log.info('Generating events for heuristic "%s".' % self.name)
        counter = 0 # Counts how many new records have been created
        # First we retrieve a list of object IDs for this 
        existing = models.Heuristic_Event.objects.filter(heuristic_name=self.name).values_list('object_id')
        existing = [int(item[0]) for item in existing] # Convert to a list of integers
        for event in self.matches(begin_date, end_date):
            if event.id in existing:
                log.debug('Heuristic event "%s" already exists for: %s' % (self.name, event))
                continue
            content_type = ContentType.objects.get_for_model(event)
            obj, created = models.Heuristic_Event.objects.get_or_create(heuristic_name=self.name,
                                                         date=event.date,
                                                         patient=event.patient,
                                                         content_type=content_type,
                                                         object_id=event.pk,
                                                         )
            if created:
                log.info('Creating new heuristic event "%s" for %s' % (self.name, event))
                obj.save()
                counter += 1
            else:
                log.debug('Did not create heuristic event - found a matching event: %s' % obj)
        log.info('Generated %s new events for "%s".' % (counter, self.name))
        return counter
    
    @classmethod
    def save_all_events(cls, begin_date=None, end_date=None):
        '''
        Generate Heuristic_Event records for every registered Heuristic 
            instance.
        @param begin_date: Beginning of time window to examine
        @type begin_date:  datetime.date
        @param end_date:   End of time window to examine
        @type end_date:    datetime.date
        @return:           Integer number of new records created
        '''
        counter = 0 # Counts how many total new records have been created
        for heuristic in cls.get_all_heuristics():
            counter += heuristic.save_events()
        log.info('Generated %s TOTAL new events.' % counter)
        return counter
    
    
    
    def make_date_str(self, date):
        '''
        Returns a string representing a datetime.date object (kludge for old 
        ESP data model)
        '''
        if type(date) == types.StringType:
            log.debug('String given as date -- no conversion')
            return date
        return util.str_from_date(date)
    
    def __repr__(self):
        return '<Heuristic: %s>' % self.name
    
    
class Lab_Heuristic(Heuristic):
    '''
    Abstract base class for lab test heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, name, verbose_name=None, loinc_nums=[], **kwargs):
        '''
        @param lookback: Include encounters/lab results occurring no more 
            than this many days before today.  If lookback is 0 or None, all 
            records are examined.
        @type lookback: Integer
        '''
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        assert self.name # Concrete class must define this!
        self._register(**kwargs)
    
    def __get_lab_q(self):
        '''
        Returns a Q object that selects all labs identified by self.loinc_nums.
        '''
        lab_q = Q(LxLoinc='%s' % self.loinc_nums[0])
        for num in self.loinc_nums[1:]:
            lab_q = lab_q | Q(LxLoinc='%s' % num)
        return lab_q
    lab_q = property(__get_lab_q)
        
    def relevant_labs(self, begin_date=None, end_date=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get lab results relevant to "%s".' % self.name)
        log.debug('Time window: %s to %s' % (begin_date, end_date))
        qs = models.Lx.objects.all()
        if begin_date:
            begin = self.make_date_str(begin_date)
            qs = qs.filter(LxDate_of_result__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(LxDate_of_result__lte=end)
        #
        # Build Q object
        #
        lab_q = Q(LxLoinc='%s' % self.loinc_nums[0])
        for num in self.loinc_nums[1:]:
            lab_q = lab_q | Q(LxLoinc='%s' % num)
        log.debug('lab_q: %s' % lab_q)
        return qs.filter(self.lab_q)


class High_Numeric_Lab_Heuristic(Lab_Heuristic):
    '''
    Matches labs with high numeric scores, as determined by a ratio to 
    '''
    
    def __init__(self, name, verbose_name=None, loinc_nums=[], ratio=None, default_high=None, **kwargs):
        '''
        @param name: Name of this heuristic (short slug)
        @type name: String
        @param verbose_name: Long name of this heuristic
        @type verbose_name: String
        @param loinc_nums: LOINC numbers relevant to this heuristic
        @type loinc_nums: List of strings
        @param ratio: Match on result > ratio * reference_high
        @type ratio: Integer
        @param default_high: If no reference high, match on result > default_high
        @type default_high: Integer
        '''
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        self.ratio = ratio
        self.default_high = default_high
        assert self.name # Sanity check
        # Should we sanity check verbose_name?
        assert self.loinc_nums # Sanity check
        assert self.ratio or self.default_high # Sanity check -- one or the other or both required
        self._register(kwargs)
    
    def matches(self, begin_date=None, end_date=None):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default_high has been specified, compare result
        against that default 'high' value.
        '''
        relevant_labs = self.relevant_labs(begin_date, end_date)
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        if self.default_high:
            static_comp_q = no_ref_q & Q(LxTest_results__gt=self.default_high)
            pos_q = static_comp_q
        if self.ratio:
            ref_comp_q = ~no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * self.ratio)
            pos_q = ref_comp_q
        if self.default_high and self.ratio:
            pos_q = (ref_comp_q | static_comp_q)
        log.debug('pos_q: %s' % pos_q)
        return relevant_labs.filter(pos_q)


class String_Match_Lab_Heuristic(Lab_Heuristic):
    '''
    Matches labs with results containing specified strings
    '''
    
    def __init__(self, name, verbose_name=None, loinc_nums=[], strings=[], match_type='istartswith', **kwargs):
        '''
        @param name:         Name of this heuristic (short slug)
        @type name:          String
        @param verbose_name: Long name of this heuristic
        @type verbose_name:  String
        @param strings:      Strings to match against
        @type strings:       List of strings
        @param match_type:   Right now, only 'istartswith'
        @type match_type:    String
        '''
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        self.strings = strings
        self.match_type = match_type
        assert self.name # Sanity check
        # Should we sanity check verbose_name?
        assert self.loinc_nums # Sanity check
        assert self.strings # Sanity check
        assert self.match_type # Sanity check
        self._register(**kwargs)
    
    def matches(self, begin_date=None, end_date=None):
        '''
        Compare record's result field against strings.
            #
        @param begin_date: Beginning of time window to examine
        @type begin_date:  datetime.date
        @param end_date:   End of time window to examine
        @type end_date:    datetime.date
        '''
        if self.match_type == 'istartswith':
            pos_q = Q(LxTest_results__istartswith=self.strings[0])
            for s in self.strings[1:]:
                pos_q = pos_q | Q(LxTest_results__istartswith=s)
        else:
            raise NotImplementedError('The only match type supported at this time is "istartswith".')
        log.debug('pos_q: %s' % pos_q)
        return self.relevant_labs(begin_date, end_date).filter(pos_q)



class Encounter_Heuristic(Heuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, name, verbose_name=None, icd9s=[], **kwargs):
        self.name = name
        self.verbose_name = verbose_name
        self.icd9s = icd9s
        assert self.name # The name of this kind of encounter
        self._register(kwargs)
    
    def __get_enc_q(self):
        '''
        Returns a Q object to select all Encounters indicated by self.icd9s
        '''
        enc_q = Q()
        for code in self.icd9s:
            enc_q = enc_q | Q(EncICD9_Codes__icontains=code)
        return enc_q
    enc_q = property(__get_enc_q)

    def encounters(self, begin_date=None, end_date=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters relevant to "%s".' % self.name)
        qs = models.Enc.objects.all()
        if begin_date and end_date:
            begin = self.make_date_str(begin_date)
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__gte=begin, EncEncounter_Date__lte=end)
        elif begin_date or end_date:
            raise 'If you specify either begin_date or end_date, you must also specify the other.'
        return qs.filter(self.enc_q)
    
    def matches(self, begin_date=None, end_date=None):
        return self.encounters(begin_date, end_date)


class Disease_Definition:
    '''
    Abstract base class for disease definitions
    '''
    
    def __init__(self, 
        name, 
        get_cases_func,
        # Reporting
        icd9s = [],
        icd9_days_before = 14,
        icd9_days_after = 14,
        fever = True, 
        lab_loinc_nums = [], 
        lab_days_before = 14,
        lab_days_after = 14,
        med_names = [], 
        med_days_before = 14,
        med_days_after = 14,
        ):
        '''
        @param name:             Name of this disease definition
        @type name:              String
        @param get_cases_func:   Callback that returns list of Case objects
        @type get_cases_func:    Function
        @param icd9s:            Report encounters matching these ICD9s
        @type icd9s:             List of strings
        @param icd9_days_before: How many days before case to search for encounters
        @type icd9_days_before:  Integer
        @param icd9_days_after:  How many days after case to search for encounters
        @type icd9_days_after:   Integer
        @param fever:            Do we report fever, determined as temp > 100.4, rather than as ICD9?
        @type fever: 		     Boolean
        @param lab_loinc_nums:   Report lab results matching these LOINCs
        @type lab_loinc_nums:    List of strings
        @param lab_days_before:  How many days before case to search for labs
        @type lab_days_before:   Integer
        @param lab_days_after:   How many days after case to search for labs
        @param med_names:        Report medicines matching these names
        @type med_names:         List of strings
        @param med_days_before:  How many days before case to search for medicines
        @type med_days_before:   Integer
        @param med_days_after:   How many days after case to search for medicines
        @type med_days_after:    Integer
        '''
        self.name = name
        self.get_cases = get_cases_func
        self.icd9s = icd9s
        self.icd9_days_before = icd9_days_before
        self.icd9_days_after = icd9_days_after
        self.fever = fever
        self.lab_loinc_nums = lab_loinc_nums
        self.lab_days_before = lab_days_before
        self.lab_days_after = lab_days_after
        self.med_names = med_names
        self.med_days_before = med_days_before
        self.med_days_after = med_days_after
        #
        # Sanity checks
        #
        assert self.name 
        assert self.get_cases 
        assert self.icd9_days_before
        assert self.icd9_days_after
        assert self.lab_days_before
        assert self.lab_days_after
        assert self.med_days_before
        assert self.med_days_after
        self.condition = models.Rule.objects.get(ruleName=self.name)
        self._register()
    
    __registry = {} # Class variable
    def _register(self):
        if self.name in self.__registry:
            raise DiseaseDefinitionAlreadyRegistered('A disease definition with the name "%s" is already registered.' % self.name)
        else:
            self.__registry[self.name] = self
    
    def new_case(self, primary_event, all_events):
        '''
        Returns a new Case object.  Case variables like provider and date are
            set based on primary_event.  The set of primary_event + all_events 
            are attached as the Case's events member.
        @param primary_event: Event on which this case is based
        @type primary_event:  Heuristic_Event
        @param all_events:    All events that together establish this case
        @type all_events:     [Heuristic_Event, Heuristic_Event, ...]
        '''
        case = models.Case()
        case.caseDemog = primary_event.patient
        case.caseProvider = primary_event.provider
        case.caseRule = self.condition
        case.events = sets.Set([primary_event]) + sets.Set(all_events)
        return case
    
    def update_reportable_events(self, case):
        '''
        @param case: The case to update
        @type case:  models.Case
        '''
        pass
        
    
    def save_cases(self):
        pass
        

#===============================================================================
#
#--- ~~~ Encounter Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

jaundice = Encounter_Heuristic(name='jaundice', 
                              verbose_name='Jaundice, not of newborn',
                              icd9s=['782.4'],
                              )

chronic_hep_b = Encounter_Heuristic(name='chronic_hep_b',
                                   verbose_name='Chronic Hepatitis B',
                                   icd9s=['070.32'],
                                   )

#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

alt_2x = High_Numeric_Lab_Heuristic(
    name='alt_2x',
    verbose_name='Alanine aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=2,
    default_high=132,
    )

alt_5x = High_Numeric_Lab_Heuristic(
    name='alt_5x',
    verbose_name='Alanine aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=5,
    default_high=330,
    )

ast_2x = High_Numeric_Lab_Heuristic(
    name='ast_2x',
    verbose_name='Aspartate aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=2,
    default_high=132,
    )

ast_5x = High_Numeric_Lab_Heuristic(
    name='ast_5x',
    verbose_name='Aspartate aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=5,
    default_high=330,
    )

hep_a_igm_ab = String_Match_Lab_Heuristic(
    name='hep_a_igm_ab',
    verbose_name='IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)',
    loinc_nums=['22314-9'],
    strings=['reactiv'],
    )

hep_b_igm_ab = String_Match_Lab_Heuristic(
    name='hep_b_igm_ab',
    verbose_name='IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['31204-1'],
    strings=['reactiv'],
    )

hep_b_surface = String_Match_Lab_Heuristic(
    name='hep_b_surface',
    verbose_name='Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['5195-3'],
    strings=['reactiv'],
    )

hep_b_e_antigen = String_Match_Lab_Heuristic(
    name = 'hep_b_e_antigen',
    verbose_name = 'Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['13954-3'],
    strings=['reactiv'],
    )

#
# Hep B Viral DNA
#
# There are three different heuristics here, a string match and a two numeric
# comparisons, all of which indicate the same condition.  Thus I have assigned
# them all the same name, so they will be identical in searches of heuristic
# events.  I think this is an okay scheme, but it doesn't quite feel elegant;
# so let me know if you can think of a better way to do it
#
#
# NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm
#
hep_b_viral_dna_str = String_Match_Lab_Heuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['13126-8', '16934', '5009-6'],
    strings = ['positiv', 'detect'],
    )
hep_b_viral_dna_num1 = High_Numeric_Lab_Heuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['16934-2'],
    default_high = 100,
    allow_duplicate_name=True,
    )
hep_b_viral_dna_num2 = High_Numeric_Lab_Heuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['5009-6'],
    default_high = 160,
    allow_duplicate_name=True,
    )


hep_e_ab = String_Match_Lab_Heuristic(
    name = 'hep_a_ab',
    verbose_name = 'Hepatitis E antibody',
    loinc_nums = ['14212-5'],
    strings = ['reactiv'],
    )

hep_c_ab = String_Match_Lab_Heuristic(
    name = 'hep_c_ab',
    verbose_name = 'Hepatitis C antibody = "REACTIVE" (may be truncated)',
    loinc_nums = ['16128-1'],
    strings = ['reactiv'],
    )

total_bilirubin_high = High_Numeric_Lab_Heuristic(
    name = 'total_bilirubin_high',
    verbose_name = 'Total bilirubin > 1.5',
    loinc_nums = ['33899-6'],
    default_high = 1.5,
    )

class High_Calculated_Bilirubin_Heuristic(Lab_Heuristic):
    '''
    Special heuristic for high Calculated Bilirubin values.  Since the value 
    of calculated bilirubin is the sum of results of two seperate tests (w/ 
    separate LOINCs), it cannot be handled by a generic Heuristic class.
    '''
    def __init__(self):
        self.name = 'high_calc_bilirubin'
        self.verbose_name = 'Calculated Bilirubin = (direct bilirubin + indirect bilirubin) > 1.5'
        self.loinc_nums = ['29760-6', '14630-8']
        self._register()
        
    def matches(self, begin_date=None, end_date=None):
        log.debug('Looking for high calculated bilirubin scores')
        # First, we return a list of patient & order date pairs, where the sum
        # of direct and indirect bilirubin tests ordered on the same day is 
        # greater than 1.5.
        relevant = self.relevant_labs(begin_date, end_date)
        vqs = relevant.values('LxPatient', 'LxOrderDate') # returns ValueQuerySet
        vqs = vqs.annotate(calc_bil=Sum('LxTest_results'))
        vqs = vqs.filter(calc_bil__gt=1.5)
        # Next we loop thru the patient/order-date list, fetch the relevant 
        # (direct + indirect) > 1.5, just in case there is a funky situation
        # where, e.g., the patient has had two indirect bilirubin tests ordered
        # on the same day.
        matches = []
        for item in vqs:
            matches += [i for i in relevant.filter(LxPatient__id=item['LxPatient'], LxOrderDate=item['LxOrderDate']) ]
        return matches
            
high_calc_bilirubin = High_Calculated_Bilirubin_Heuristic()


#===============================================================================
#
#--- ~~~ Disease Definitions ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        
def hep_a_cases(self, new_only=False):
    '''
    Only one Hep A case per lifetime -- so return one case, with all relevant events attached.
    '''
    
    result = {} # {Patient: Case}
    igm_events = models.Heuristic_Event.objects.filter(heuristic_name='hep_a_igm_ab')
    for event in igm_events:
        patient = event.patient
        fourteen = datetime.timedelta(days=14)
        begin = event.date - fourteen
        end = event.date + fourteen
        other_names = ('jaundice', 'alt_2x', 'ast_2x')
        q_obj = Q(patient=patient, heuristic_name__in=other_names, date__gte=begin, date__lte=end)
        other_events = models.Heuristic_Event.objects.filter(q_obj)
        if not other_events:
            continue # Not a case
        all_events = [event] + [e for e in other_events]
        #
        # Case established -- but a patient can have only one Acute Hep A 
        # diagnosis per lifetime, so let's check and see if he already has 
        # one.
        #
        if patient in result: # First, have we seen it in this detection run:
            log.debug('Result list already contains case for %s.  Updating its events and continuing.' % patient)
            case = result[patient]
            case.events = sets.Set(case.events) + sets.Set(all_events)
            continue
        # Now check the db:
        existing = models.Case.objects.filter(caseDemog=patient, caseRule=self.condition)
        if existing and new_only:
            log.debug('Existing case found for %s.  Flag new_only is set, so skipping & continuing.' % patient)
            continue
        elif existing:
            log.debug('Existing case found for %s.  Updating its events (not saving), putting it in result list, and continuing.' % patient)
            case = existing[0] # should be only one hep A case
            case.events = sets.Set(case.events) + sets.Set(all_events)
            result[patient] = case
        else:
            # No case --
            log.debug('Creating new case for %s' % patient)
            result[patient] = self.new_case(primary_event=event, all_events=all_events)
    return result

hep_a = Disease_Definition(
    name = 'Acute Hepatitis A',
    get_cases_func = hep_a_cases,
    )
    

if __name__ == '__main__':
    #alt_2x.save_events()
    #Heuristic.save_all_events()
    #high_calc_bilirubin.save_events()
    #pprint.pprint(connection.queries)
    Acute_Hepatitis_A().generate_cases()
    pass
    
