#!/usr/bin/env python
'''
Detect cases of (reportable) disease
'''
#
# NOTE: If you are supremely foolish enough to assign the same name to more
# than one Heuristic instance, this whole system will barf all over your data.
#

import datetime
import pprint
import types
import sets

from django.db import connection
from django.db.models import Q
from django.db.models import F
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

class CaseAlreadyExists(BaseException):
    '''
    A case already exists for this disease + patient
    '''
    pass


#===============================================================================
#
#--- ~~~ Base Classes ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HeuristicAlreadyRegistered(BaseException):
    '''
    A Heuristic instance has already been registered with the same name 
    as the instance you are trying to register.
    '''

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
    
    def matches(self, begin_date=None, end_date=None):
        '''
        Return a QuerySet of matches for this heuristic
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
        
    def generate_events(self, begin_date=None, end_date=None):
        '''
        Generate models.Heuristic_Event records for each item returned by
        matches, if it does not already have one.
        @return: Integer number of new records created
        '''
        counter = 0
        existing = models.Heuristic_Event.objects.filter(event_name=self.name).values_list('object_id')
        for event in self.matches(begin_date, end_date).select_related():
            if event.id in existing:
                log.debug('Heuristic event "%s" already exists for: %s' % (self.name, event))
                continue
            content_type = ContentType.objects.get_for_model(event)
            obj, created = models.Heuristic_Event.objects.get_or_create(event_name=self.name,
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
                log.debug('Already found a matching event: %s' % obj)
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
        log.debug('lab_q: %s' % lab_q)
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
    
    def __init__(self, name, verbose_name=None, loinc_nums=[], ratio=None, default=None, **kwargs):
        '''
        @param name: Name of this heuristic (short slug)
        @type name: String
        @param verbose_name: Long name of this heuristic
        @type verbose_name: String
        @param loinc_nums: LOINC numbers relevant to this heuristic
        @type loinc_nums: List of strings
        @param ratio: Match on result > ratio * reference_high
        @type ratio: Integer
        @param default: If no reference high, match on result > default
        @type default: Integer
        '''
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        self.ratio = ratio
        self.default = default
        assert self.name # Sanity check
        # Should we sanity check verbose_name?
        assert self.loinc_nums # Sanity check
        assert self.ratio or self.default # Sanity check -- one or the other or both required
        self._register(kwargs)
    
    def matches(self, begin_date=None, end_date=None):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default has been specified, compare result
        against that default 'high' value.
        '''
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        if self.default:
            static_comp_q = no_ref_q & Q(LxTest_results__gt=self.default)
            pos_q = static_comp_q
        if self.ratio:
            ref_comp_q = ~no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * self.ratio)
            pos_q = ref_comp_q
        if self.default and self.ratio:
            pos_q = (ref_comp_q | static_comp_q)
        log.debug('pos_q: %s' % pos_q)
        return self.relevant_labs(begin_date, end_date).filter(pos_q)


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



class EncounterHeuristic(Heuristic):
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
        log.debug('Get lab results relevant to "%s".' % self.name)
        qs = models.Enc.objects.all()
        if begin_date and end_date:
            begin = self.make_date_str(begin_date)
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__gte=begin, EncEncounter_Date__lte=end)
        elif begin_date or end_date:
            raise 'If you specify either begin_date or end_date, you must also specify the other.'
        return qs.filter(self.enc_q)


class DiseaseDefinition:
    '''
    Abstract base class for disease definitions
    '''
    
    def __init__(self):
        #
        # Sanity Checks
        #
        assert isinstance(self.condition, models.Rule) # Must have a valid condition ("Rule" in old ESP parlance)
        assert type(self.report_icd9) == types.ListType
        assert type(self.report_rx) == types.ListType
        assert type(self.related_components) == types.ListType
        
    def get_patients(self):
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from DiseaseDefinition.')
    
    def split_cases(self, patient, labs, encounters):
        '''
        Split list of labs and list of encounters into dicts, each representing
            a separate case.  By default this method returns only a single 
            event, but it's behavior can, and often should, be overridden in 
            subclasses.
        @return: [case_info, case_info, ...]
            where case_info = {'patient': patient,
                               'provider': provider,
                               'date': case_establishment_date,
                               'labs': labs,
                               'encounters': encounters, }
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from DiseaseDefinition.')

    
    def sort_events(self, events):
        '''
        Sorts a list of events (labs & encounters) by date.
        '''
        x = [(e.date, e) for e in events]
        x.sort()
        return [i[1] for i in x]

    def make_cases(self, patient):
        '''
        Makes a case for specified patient
            @type patient: models.Demog
        '''
        events = []
        labs = []
        encounters = []
        for component in self.related_components:
            c = component()
            if isinstance(c, Lab_Heuristic):
                # NOTE: We are fetching all *relevant* lab tests, not just 
                # those which indicate positive.
                labs += [i for i in c.relevant_labs(patient=patient)] 
            elif isinstance(c, EncounterHeuristic):
                encounters += [i for i in c.encounters(patient=patient)]
            else:
                raise 'Fail!'
        existing_cases = models.Case.objects.filter(caseDemog=patient)
        # Extract list of lab/encounter ID numbers from comma-delimited fields
        existing_lab_ids = []
        [existing_lab_ids.extend( util.str_to_list(case.caseLxID) ) for case in existing_cases]
        existing_encounter_ids = []
        [existing_encounter_ids.extend( util.str_to_list(case.caseEncID) ) for case in existing_cases]
        log.debug('existing_lab_ids: %s' % existing_lab_ids)
        log.debug('existing_encounter_ids: %s' % existing_encounter_ids)
        #
        # Loop through the labs & encounters, and see if any of them belongs to
        # an existing case.  If so, skip to the next set of case_events.
        #
        for case_info in self.split_cases(patient, labs=labs, encounters=encounters):
            log.debug('date: %s' % case_info['date'])
            log.debug('labs: %s' % case_info['labs'])
            log.debug('encounters: %s' % case_info['encounters'])
            is_existing = False # Flag for use below
            for l in case_info['labs']:
                if l.id in existing_lab_ids:
                    log.debug('Lab "%s" belongs to an existing case' % l)
                    is_existing = True
            for e in case_info['encounters']:
                if e.id in existing_encounter_ids:
                    log.debug('Encounter "%s" belongs to an existing case' % e)
                    is_existing = True
            if is_existing:
                log.debug('These events belong to an existing case.  Skipping to next bunch')
                continue
            log.debug('Events do match any events belonging to an existing case.')
            self.make_single_case(patient, case_info)

    def make_single_case(self, patient, case_info):
        '''
        Makes a new case for specified patient, attaching relevant labs & 
            encounters.
        FIXME: We are attaching too many labs.  Figure out how to winnow down
            the list to more manageable size.
        @type patient: models.Demog
        @param case_info: {'patient': patient, 
                           'provider': provider,
                           'date': case_establishment_date, 
                           'labs': labs, # Relevant labs (pos & neg both)
                           'encounters': encounters, }
        @type case_info: Dict
        '''
        case = models.Case()
        case_date = case_info['date']
        case.caseDemog = patient
        case.caseRule = self.condition
        case.caseEncID = ','.join( [str(e.id) for e in case_info['encounters'] ] )
        case.caseLxID = ','.join( [str(l.id) for l in case_info['labs'] ] )
        case.caseWorkflow = 'AR'
        #
        # Related Rx
        #
        rx_ids = []
        rx_begin = case_date - datetime.timedelta(days=settings.REPORT_RX_DAYS_BEFORE)
        rx_end = case_date + datetime.timedelta(days=settings.REPORT_RX_DAYS_AFTER)
        for rx_name in self.report_rx:
            result = models.Rx.objects.filter(RxPatient=patient, 
                                              RxDrugName__icontains=rx_name,
                                              RxOrderDate__gte=util.str_from_date(rx_begin),
                                              RxOrderDate__lte=util.str_from_date(rx_end),
                                              )
            if result:
                rx_ids += [r.id for r in result]
        case.caseRxID = ','.join(rx_ids)
        #
        # Related Symptoms (ICD9s)
        #
        symptom_icd9s = []
        symptom_begin = case_date - datetime.timedelta(days=settings.REPORT_ICD9_DAYS_BEFORE)
        symptom_end = case_date + datetime.timedelta(days=settings.REPORT_ICD9_DAYS_AFTER)
        for icd9 in self.report_icd9:
            result = models.Enc.objects.filter(EncPatient=patient,
                                               EncICD9_Codes__icontains=icd9,
                                               EncEncounter_Date__gte=util.str_from_date(symptom_begin),
                                               EncEncounter_Date__lte=util.str_from_date(symptom_end),
                                               )
            if result:
                symptom_icd9s += [icd9]
        case.caseICD9 = ','.join(symptom_icd9s)
        log.info('Saving new case: %s' % case)
        case.save()
        
        

#===============================================================================
#
#--- ~~~ Encounter Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

jaundice = EncounterHeuristic(name='jaundice', 
                              verbose_name='Jaundice, not of newborn',
                              icd9s=['782.4'],
                              )

chronic_hep_b = EncounterHeuristic(name='chronic_hep_b',
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
    default=132,
    )

alt_5x = High_Numeric_Lab_Heuristic(
    name='alt_5x',
    verbose_name='Alanine aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=5,
    default=330,
    )

ast_2x = High_Numeric_Lab_Heuristic(
    name='ast_2x',
    verbose_name='Aspartate aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=2,
    default=132,
    )

ast_5x = High_Numeric_Lab_Heuristic(
    name='ast_5x',
    verbose_name='Aspartate aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=5,
    default=330,
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
    default = 100,
    allow_duplicate_name=True,
    )
hep_b_viral_dna_num2 = High_Numeric_Lab_Heuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['5009-6'],
    default = 160,
    allow_duplicate_name=True,
    )

class Hep_B_Viral_DNA(Lab_Heuristic):
    '''
    Hepatitis B Viral DNA
    '''
    def setup(self):
        self.name = 'Hepatitis B Viral DNA'
        self.loinc_nums = ['13126-8', '16934', '5009-6']
        # NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" portion of algorithm
        #
        # Lab Result Query
        #
        # HEP B DNA PCR (QL) 
        q_obj = Q(LxLoinc='13126-8') | Q(LxLoinc='16934')
        q_obj = q_obj & ( Q(LxTest_results__istartswith='positiv') | Q(LxTest_results__istartswith='detect') )
        # HEP B VIRAL DNA IU/ML 
        q_obj = q_obj | Q(LxLoinc='16934-2', LxTest_results__gt=100)
        # HEP B DNA COPIES/ML 
        q_obj = q_obj | Q(LxLoinc='5009-6', LxTest_results__gt=160)
        self.pos_q = q_obj


class Hep_E_Ab(Lab_Heuristic):
    '''
    Hepatitis E antibody
    '''
    def setup(self):
        self.name = 'Hepatitis E antibody'
        self.loinc_nums = ['14212-5']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Hep_C_Ab(Lab_Heuristic):
    '''
    Hepatitis C antibody = "REACTIVE" (may be truncated)
    '''
    def setup(self):
        self.name = 'Hepatitis C antibody = "REACTIVE" (may be truncated)'
        self.encounter_q = None
        self.loinc_nums = ['16128-1']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Total_Bilirubin_gt_1_5(Lab_Heuristic):
    '''
    Total bilirubin > 1.5
    '''
    def setup(self):
        self.name = 'Total bilirubin > 1.5'
        self.loinc_nums = ['33899-6']
        self.pos_q = Q(LxTest_results__gt=1.5)


class Calculated_Bilirubin_gt_1_5(Lab_Heuristic):
    '''
    FINISH ME!
    '''
    def setup(self):
        self.name = ''
        self.encounter_q = None
    
        

#===============================================================================
#
#--- ~~~ Disease Definitions ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#class Acute_Hepatitis_A(DiseaseDefinition):
#    '''
#    A case of Acute Hepatitis A is defined as a patient who has
#        a) Positive test for IgM Antibody to Hepatitis A
#        b) Either Diagnosis of Jaundice; ALT test > 2x normal; or AST test > 2x normal 
#    where (b) must occur "within 14 days" of (a)
#    '''
#    condition = models.Rule.objects.get(ruleName__icontains='acute hepatitis a')
#    related_components = [
#        Jaundice,
#        ALT_2x_Upper_Limit,
#        AST_2x_Upper_Limit,
#        Hep_A_IgM_Ab,
#        ]
#    report_icd9 = [
#                   '780.6A',
#                   '782.4',
#                   '783.0',
#                   '780.79B',
#                   '789.0',
#                   '787.01',
#                   '787.02',
#                   '787.91',
#                   ]
#    report_rx = []
#    
#    def get_patients(self):
#        log.info('Searching for cases of Acute Hepatitis A')
#        j = Jaundice()
#        alt = ALT_2x_Upper_Limit()
#        ast = AST_2x_Upper_Limit()
#        ab = Hep_A_IgM_Ab()
#        positive = sets.Set() # patients positive for Hep A
#        for lab in ab.positive_labs().select_related('LxPatient'):
#            # These patients all tested positive for Hep A IgM antibody.  
#            # Let's find out if they meet any of the other conditions.
#            patient = lab.LxPatient
#            log.debug('Patient has positive Hep A IgM antibody test:\n    %s' % patient)
#            lab_date = util.date_from_str(lab.LxOrderDate)
#            fourteen = datetime.timedelta(days=14)
#            begin_date = lab_date - fourteen
#            end_date = lab_date + fourteen
#            log.debug('Analyzing time window %s to %s.' % (begin_date, end_date))
#            for test in [j, alt, ast]:
#                if test.is_positive(patient):
#                    msg = '\n'
#                    msg += '    The following patient tested positive for Hepatitis A IgM antibody, and\n' 
#                    msg += '    for "%s"\n' % test.name
#                    msg += '    within +/- 14 days, fulfilling criteria for an Acute Hep A case:\n'
#                    msg += '    %s' % patient
#                    log.info(msg)
#                    positive.add(patient)
#                    break # Only need one positive in this bunch
#        return positive
#                                
#    def split_cases(self, patient, labs, encounters):
#        '''
#        From Mike Klompas:  "For acute hepatitis A it's one diagnosis per 
#        lifetime.  Subsequent positives are false positives."  Case date is 
#        the order date for Hepatitis A IgM lab test
#        '''
#        case_info = {'patient': patient,
#                     'labs': labs,
#                     'encounters': encounters,}
#        # It's easier to hit the DB just one time, than to loop through the
#        # list of all relevant labs provided as argument.
#        pos_test = Hep_A_IgM_Ab().positive_labs(patient=patient)[0]
#        case_info['date'] = util.date_from_str(pos_test.LxOrderDate)
#        case_info['provider'] = pos_test.LxOrdering_Provider
#        return [case_info]



if __name__ == '__main__':
    alt_2x.generate_events()
    #pprint.pprint(connection.queries)
    
