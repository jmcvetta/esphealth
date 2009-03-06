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
from django.db.models.query import QuerySet


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

class BaseHeuristic:
    '''
    Abstract interface lclass for heuristics, concrete instances of which are
    used as components of disease definitions.l
    '''
    
    def setup(self):
        '''
        Setup the name, Q objects, etc -- this must be implemented in concrete 
        classes.
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
    
    def patients(self, begin_date=None, end_date=None):
        '''
        Return a list of patients who are indicated as positive by this heuristic.
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
    
    def is_positive(self, patient, begin_date=None, end_date=None):
        '''
        Return True if specified patient is indicated positive by this heuristic.
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
    
    def make_date_str(self, date):
        '''
        Returns a string representing a datetime.date object (kludge for old 
        ESP data model)
        '''
        if type(date) == types.StringType:
            log.debug('String given as date -- no conversion')
            return date
        return util.str_from_date(date)
    
    
class LabHeuristic(BaseHeuristic):
    '''
    Abstract base class for lab test heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self):
        '''
        @param lookback: Include encounters/lab results occurring no more 
            than this many days before today.  If lookback is 0 or None, all 
            records are examined.
        @type lookback: Integer
        '''
        self.name = None # Name of this heuristic, used for logging etc
        self.loinc_nums = [] # List of LOINC numbers relevant to this heuristic
        self.pos_q = None # Identifies positives from among the lab tests indicated by self.loinc_nums
        self.setup() 
        assert self.name # Concrete class must define this!
    
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
        
    def relevant_labs(self, begin_date=None, end_date=None, patient=None, queryset=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get lab results relevant to "%s".' % self.name)
        if queryset:
            qs = queryset
        else:
            qs = models.Lx.objects.all()
        if patient:
            qs = qs.filter(LxPatient=patient)
        if begin_date and end_date:
            begin = self.make_date_str(begin_date)
            end = self.make_date_str(end_date)
            qs = qs.filter(LxDate_of_result__gte=begin, LxDate_of_result__lte=end)
        return qs.filter(self.lab_q)
    
    def positive_labs(self, begin_date=None, end_date=None, patient=None, queryset=None):
        '''
        Return all lab results matching this component.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        qs = self.relevant_labs(begin_date=begin_date, end_date=end_date, patient=patient, queryset=queryset)
        log.debug('Get positive lab results for "%s".' % self.name)
        log.debug('pos_q: %s' % self.pos_q)
        return qs.filter(self.pos_q)
    
    def patients(self, begin_date=None, end_date=None, include_result=False):
        '''
        Return all patients matching this component
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get patients for "%s".' % self.name)
        labs = self.get_lab_results(begin_date=begin_date, end_date=end_date)
        if include_result:
            return [(l.LxPatient, l.LxTest_results) for l in labs.select_related('LxPatient')]
        else:
            return [l.LxPatient for l in labs.select_related('LxPatient')]
    
    def is_positive(self, patient, begin_date=None, end_date=None):
        if self.positive_labs(begin_date=begin_date, end_date=end_date, patient=patient):
            return True
        else:
            return False


class EncounterHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self):
        self.name = None
        self.icd9s = []
        self.setup()
        assert self.name # The name of this kind of encounter
        assert self.icd9s # The ICD9 code(s) that define this kind of encounter
    
    def __get_enc_q(self):
        '''
        Returns a Q object to select all Encounters indicated by self.icd9s
        '''
        enc_q = Q()
        for code in self.icd9s:
            enc_q = enc_q | Q(EncICD9_Codes__icontains=code)
        return enc_q
    enc_q = property(__get_enc_q)

    def encounters(self, begin_date=None, end_date=None, patient=None, queryset=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get lab results relevant to "%s".' % self.name)
        if queryset:
            qs = queryset
        else:
            qs = models.Enc.objects.all()
        if patient:
            qs = qs.filter(EncPatient=patient)
        if begin_date and end_date:
            begin = self.make_date_str(begin_date)
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__gte=begin, EncEncounter_Date__lte=end)
        return qs.filter(self.enc_q)
    
    def patients(self, begin_date=None, end_date=None, include_result=False):
        '''
        Return a list of patients who are indicated as positive by this heuristic
        '''
        encounters = self.encounters(begin_date=begin_date, end_date=end_date).select_related('EncPatient')
        if include_result:
            return [(e.EncPatient, 'Enc: %s' % self.name) for e in encounters]
        else:
            return [e.EncPatient for e in encounters]

    def is_positive(self, patient, begin_date=None, end_date=None):
        if self.encounters(begin_date=begin_date, end_date=end_date, patient=patient):
            return True
        else:
            return False


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
            if isinstance(c, LabHeuristic):
                # NOTE: We are fetching all *relevant* lab tests, not just 
                # those which indicate positive.
                labs += [i for i in c.relevant_labs(patient=patient)] 
            elif isinstance(c, EncounterHeuristic):
                encounters += [i for i in c.encounters(patient=patient)]
            else:
                raise 'Fail!'
        existing_cases = models.Case.objects.filter(caseDemog=patient)
        # Extract list of lab/encounter ID numbers from comma-delimited fields
        existing_labs = ','.join([case.caseLxID for case in existing_cases]).split(',')
        existing_encounters = ','.join([case.caseEncID for case in existing_cases]).split(',')
        for case_info in self.split_cases(patient, labs=labs, encounters=encounters):
            # Loop through the labs & encounters, and see if any of them 
            # belongs to an existing case.  If so, skip to the next set of 
            # case_events.
            is_existing = False # Flag for use below
            for l in case_info['labs']:
                if l.id in existing_labs:
                    log.debug('Lab "%s" belongs to an existing case' % l)
                    is_existing = True
            for e in case_info['encounters']:
                if e.id in existing_encounters:
                    log.debug('Encounter "%s" belongs to an existing case' % e)
                    is_existing = True
            if is_existing:
                log.debug('These events belong to an existing case.  Skipping to next bunch')
                continue
            self.make_single_case(patient, case_info)

    def make_single_case(self, patient, case_info):
        '''
        Makes a new case for specified patient, attaching relevant labs & 
            encounters.
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

class Jaundice(EncounterHeuristic):
    '''
    Jaundice, not of newborn
    '''
    def setup(self):
        self.name = 'Jaundice, not of newborn'
        self.icd9s = ['782.4']


class Chronic_Hep_B(EncounterHeuristic):
    '''
    Chronic Hepatitis B
    '''
    def setup(self):
        self.name = 'Chronic Hepatitis B'
        self.icd9s = ['070.32']
                                

#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                

class ALT_2x_Upper_Limit(LabHeuristic):
    '''
    Alanine aminotransferase (ALT) >2x upper limit of normal
    '''
    def setup(self):
        self.name = 'Alanine aminotransferase (ALT) >2x upper limit of normal'
        self.loinc_nums = ['1742-6']
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = ~no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 2)
        static_comp_q = no_ref_q & Q(LxTest_results__gt=132)
        #
        self.pos_q = (ref_comp_q | static_comp_q)


class ALT_5x_Upper_Limit(LabHeuristic):
    '''
    Alanine aminotransferase (ALT) >5x upper limit of normal
    '''
    def setup(self):
        self.name = 'Alanine aminotransferase (ALT) >5x upper limit of normal'
        self.loinc_nums = ['1742-6']
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 5)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=330)
        #
        self.pos_q = (ref_comp_q | static_comp_q)


class AST_2x_Upper_Limit(LabHeuristic):
    '''
    Aspartate aminotransferase (AST) >2x upper limit of normal
    '''
    def setup(self):
        self.name = 'Aspartate aminotransferase (AST) >2x upper limit of normal'
        self.loinc_nums = ['1920-8']
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 2)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=132)
        #
        self.pos_q = (ref_comp_q | static_comp_q)


class AST_5x_Upper_Limit(LabHeuristic):
    '''
    Aspartate aminotransferase (AST) >2x upper limit of normal
    '''
    def setup(self):
        self.name = 'Aspartate aminotransferase (AST) >2x upper limit of normal'
        self.loinc_nums = ['1920-8']
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 5)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=330)
        #
        self.pos_q = (ref_comp_q | static_comp_q)


class Hep_A_IgM_Ab(LabHeuristic):
    '''
    IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)
    '''
    def setup(self):
        self.name = 'IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)'
        self.loinc_nums = ['22314-9']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Hep_B_IgM_Ab(LabHeuristic):
    '''
    IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)
    '''
    def setup(self):
        self.name = 'IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)'
        self.loinc_nums = ['31204-1']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Hep_B_Surface(LabHeuristic):
    '''
    Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)
    '''
    def setup(self):
        self.name = 'Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)'
        self.loinc_nums = ['5195-3']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Hep_B_e_Antigen(LabHeuristic):
    '''
    Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)
    '''
    def setup(self):
        self.name = 'Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)'
        self.loinc_nums = ['13954-3']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Hep_B_Viral_DNA(LabHeuristic):
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


class Hep_E_Ab(LabHeuristic):
    '''
    Hepatitis E antibody
    '''
    def setup(self):
        self.name = 'Hepatitis E antibody'
        self.loinc_nums = ['14212-5']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Hep_C_Ab(LabHeuristic):
    '''
    Hepatitis C antibody = "REACTIVE" (may be truncated)
    '''
    def setup(self):
        self.name = 'Hepatitis C antibody = "REACTIVE" (may be truncated)'
        self.encounter_q = None
        self.loinc_nums = ['16128-1']
        self.pos_q = Q(LxTest_results__istartswith='reactiv')


class Total_Bilirubin_gt_1_5(LabHeuristic):
    '''
    Total bilirubin > 1.5
    '''
    def setup(self):
        self.name = 'Total bilirubin > 1.5'
        self.loinc_nums = ['33899-6']
        self.pos_q = Q(LxTest_results__gt=1.5)


class Calculated_Bilirubin_gt_1_5(LabHeuristic):
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

class Acute_Hepatitis_A(DiseaseDefinition):
    '''
    A case of Acute Hepatitis A is defined as a patient who has
        a) Positive test for IgM Antibody to Hepatitis A
        b) Either Diagnosis of Jaundice; ALT test > 2x normal; or AST test > 2x normal 
    where (b) must occur "within 14 days" of (a)
    '''
    condition = models.Rule.objects.get(ruleName__icontains='acute hepatitis a')
    related_components = [
        Jaundice,
        ALT_2x_Upper_Limit,
        AST_2x_Upper_Limit,
        Hep_A_IgM_Ab,
        ]
    report_icd9 = [
                   '780.6A',
                   '782.4',
                   '783.0',
                   '780.79B',
                   '789.0',
                   '787.01',
                   '787.02',
                   '787.91',
                   ]
    report_rx = []
    
    def get_patients(self):
        log.info('Searching for cases of Acute Hepatitis A')
        j = Jaundice()
        alt = ALT_2x_Upper_Limit()
        ast = AST_2x_Upper_Limit()
        ab = Hep_A_IgM_Ab()
        positive = sets.Set() # patients positive for Hep A
        for lab in ab.positive_labs().select_related('LxPatient'):
            # These patients all tested positive for Hep A IgM antibody.  
            # Let's find out if they meet any of the other conditions.
            patient = lab.LxPatient
            log.debug('Patient has positive Hep A IgM antibody test:\n    %s' % patient)
            lab_date = util.date_from_str(lab.LxOrderDate)
            fourteen = datetime.timedelta(days=14)
            begin_date = lab_date - fourteen
            end_date = lab_date + fourteen
            log.debug('Analyzing time window %s to %s.' % (begin_date, end_date))
            for test in [j, alt, ast]:
                if test.is_positive(patient):
                    msg = '\n'
                    msg += '    The following patient tested positive for Hepatitis A IgM antibody, and\n' 
                    msg += '    for "%s"\n' % test.name
                    msg += '    within +/- 14 days, fulfilling criteria for an Acute Hep A case:\n'
                    msg += '    %s' % patient
                    log.info(msg)
                    positive.add(patient)
                    break # Only need one positive in this bunch
        return positive
                                
    def split_cases(self, patient, labs, encounters):
        '''
        From Mike Klompas:  "For acute hepatitis A it's one diagnosis per 
        lifetime.  Subsequent positives are false positives."  Case date is 
        the order date for Hepatitis A IgM lab test
        '''
        case_info = {'patient': patient,
                     'labs': labs,
                     'encounters': encounters,}
        # It's easier to hit the DB just one time, than to loop through the
        # list of all relevant labs provided as argument.
        pos_test = Hep_A_IgM_Ab().positive_labs(patient=patient)[0]
        case_info['date'] = util.date_from_str(pos_test.LxOrderDate)
        case_info['provider'] = pos_test.LxOrdering_Provider
        return [case_info]



if __name__ == '__main__':
    hep_a= Acute_Hepatitis_A()
    for p in hep_a.get_patients():
        hep_a.make_cases(p)
    #pprint.pprint(connection.queries)
    
