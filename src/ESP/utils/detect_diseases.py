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
#--- ~~~ Base Classes ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseDiseaseComponent:
    '''
    Abstract base class for disease component detection algorithms
    '''
    
    name = '[name of component]' # This should be defined in your concrete classes
    
    def __init__(self):
        '''
        @param lookback: Include encounters/lab results occurring no more 
            than this many days before today.  If lookback is 0 or None, all 
            records are examined.
        @type lookback: Integer
        '''
        self.encounter_q = None # Q object
        self.patient_q = None # Q object
        self.lab_q = None # Q object
        self.q_setup() 
        assert self.name # Concrete class must define this!
        self.variant # Used for the sanity checks
    
    def _get_variant(self):
        '''
        Returns 'lab' or 'encounter'.
        '''
        # Sanity checks:
        assert (self.encounter_q or self.lab_q) # Gotta have one or the other
        assert not (self.encounter_q and self.lab_q) # Can't have both
        #
        if self.lab_q:
            return 'lab'
        elif self.encounter_q:
            return 'encounter'
    variant = property(_get_variant)
    
    def q_setup(self):
        '''
        Setup the Q objects -- this must be implemented in concrete classes
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseDiseaseComponent.')
    
    def make_date_str(self, date):
        '''
        Returns a string representing a datetime.date object (kludge for old 
        ESP data model)
        '''
        if type(date) == types.StringType:
            log.debug('String given as date -- no conversion')
            return date
        return util.str_from_date(date)
        
    def get_encounters(self, begin_date=None, end_date=None, patient=None, queryset=None, **kw):
        '''
        Return all encounters matching this component
	        @type begin_date: datetime.date
	        @type end_date:   datetime.date
	        @type patient:    models.Demog
	        @type queryset:   QuerySet
        '''
        
        log.debug('Get encounters for "%s".' % self.name)
        if queryset:
            qs = queryset
        else:
            qs = models.Enc.objects.all()
        if not self.encounter_q:
            return qs.none()
        if patient:
            qs = qs.filter(EncPatient=patient)
        if begin_date and end_date:
            begin = self.make_date_str(begin_date)
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__gte=begin, EncEncounter_Date__lte=end)
        log.debug('encounter_q: %s' % self.encounter_q)
        return qs.filter(self.encounter_q).distinct()
    encounters = property(get_encounters)
    
    def get_lab_results(self, begin_date=None, end_date=None, patient=None, queryset=None):
        '''
        Return all lab results matching this component
	        @type begin_date: datetime.date
	        @type end_date:   datetime.date
	        @type patient:    models.Demog
	        @type queryset:   QuerySet
        '''
        log.debug('Get lab results for "%s".' % self.name)
        if queryset:
            qs = queryset
        else:
            qs = models.Lx.objects.all()
        if not self.lab_q:
            return qs.none()
        if patient:
            qs = qs.filter(LxPatient=patient)
        if begin_date and end_date:
            begin = self.make_date_str(begin_date)
            end = self.make_date_str(end_date)
            qs = qs.filter(LxDate_of_result__gte=begin, LxDate_of_result__lte=end)
        log.debug('lab_q: %s' % self.lab_q)
        return qs.filter(self.lab_q).distinct()
    lab_results = property(get_lab_results)
    
    def get_patients(self, begin_date=None, end_date=None, patient=None, queryset=None, include_result=True):
        '''
        Return all patients matching this component
	        @type begin_date: datetime.date
	        @type end_date:   datetime.date
	        @type patient:    models.Demog
	        @type queryset:   QuerySet
        '''
        log.debug('Get patients for "%s".' % self.name)
        if self.lab_q and self.encounter_q:
            raise "I don't know how to deal with this situation."
        elif self.lab_q:
            labs = self.get_lab_results(begin_date=begin_date, end_date=end_date, patient=patient, queryset=queryset)
            if include_result:
                return [(l.LxPatient, l.LxTest_results) for l in labs.select_related('LxPatient')]
            else:
                return [l.LxPatient for l in labs.select_related('LxPatient')]
            #patient_set = sets.Set()
            #[patient_set.add(l.LxPatient) for l in labs.select_related('LxPatient')]
            #return patient_set
        elif self.encounter_q:
            encs = self.get_encounters(begin_date=begin_date, end_date=end_date, patient=patient, queryset=queryset)
            if include_result:
                return [(e.EncPatient, 'ICD9 Codes: %s' % e.EncICD9_Codes) for e in encs.select_related('EncPatient')]
            else:
                return [e.EncPatient for e in encs.select_related('EncPatient')]
            #patient_set = sets.Set()
            #[patient_set.add(e.EncPatient) for e in encs.select_related('EncPatient')]
            #return patient_set
        else:
            raise 'WTF?'
    patients = property(get_patients)


class CaseAlreadyExists(BaseException):
    '''
    A case already exists for this disease + patient
    '''
    pass


class BaseDiseaseDefinition:
    '''
    Abstract base class for disease definitions
    '''
    
    def __init__(self):
        #
        # Sanity Checks
        #
        assert isinstance(self.condition, models.Rule) # Must have a valid condition ("Rule" in old ESP parlance)
        assert type(self.report_icd9s) == types.ListType
        assert type(self.related_components) == types.ListType
        
    def get_patients(self):
        raise NotImplementedError
    
    def make_case(self, patient):
        '''
        Makes cases for the given patient
            @type patient: models.Demog
        '''
        events = []
        for component in self.related_components:
            c = component()
            if c.variant == 'lab':
                events += [(l.LxDate_of_result, l) for l in c.get_lab_results(patient=patient)]
            elif c.variant == 'encounter':
                events += [(e.EncEncounter_Date, e) for e in c.get_encounters(patient=patient)]
            else:
                raise 'Fail!'
        events.sort()
        print '--------------------------------------------------------------------------------'
        for e in events:
            print e
        

#===============================================================================
#
#--- ~~~ Diagnosis Components ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                
class Jaundice(BaseDiseaseComponent):
    '''
    Jaundice, not of newborn
    '''
    name = 'Jaundice, not of newborn'
    def q_setup(self):
        self.encounter_q = Q(EncICD9_Codes__icontains='782.4')


class Chronic_Hep_B(BaseDiseaseComponent):
    '''
    Chronic Hepatitis B ICD9 = 070.32
    '''
    name = 'Chronic Hepatitis B ICD9 = 070.32'
    def q_setup(self):
        self.encounter_q = Q(EncICD9_Codes__icontains='070.32')
        

#===============================================================================
#
#--- ~~~ Lab Test Components ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                

class ALT_2x_Upper_Limit(BaseDiseaseComponent):
    '''
    Alanine aminotransferase (ALT) >2x upper limit of normal
    '''
    name = 'Alanine aminotransferase (ALT) >2x upper limit of normal'
    def q_setup(self):
        # Lab Result Query
        loinc_q = Q(LxLoinc='1742-6')
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = ~no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 2)
        static_comp_q = no_ref_q & Q(LxTest_results__gt=132)
        self.lab_q = loinc_q & (ref_comp_q | static_comp_q)


class ALT_5x_Upper_Limit(BaseDiseaseComponent):
    '''
    Alanine aminotransferase (ALT) >5x upper limit of normal
    '''
    name = 'Alanine aminotransferase (ALT) >5x upper limit of normal'
    def q_setup(self):
        # Lab Result Query
        loinc_q = Q(LxLoinc='1742-6')
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 5)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=330)
        self.lab_q = loinc_q & (ref_comp_q | static_comp_q)


class AST_2x_Upper_Limit(BaseDiseaseComponent):
    '''
    Aspartate aminotransferase (AST) >2x upper limit of normal
    '''
    name = 'Aspartate aminotransferase (AST) >2x upper limit of normal'
    def q_setup(self):
        #
        # Lab Result Query
        #
        loinc_q = Q(LxLoinc='1920-8')
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 2)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=132)
        #
        self.lab_q = loinc_q & (ref_comp_q | static_comp_q)


class AST_5x_Upper_Limit(BaseDiseaseComponent):
    '''
    Aspartate aminotransferase (AST) >2x upper limit of normal
    '''
    name = 'Aspartate aminotransferase (AST) >2x upper limit of normal'
    def q_setup(self):
        #
        # Lab Result Query
        #
        loinc_q = Q(LxLoinc='1920-8')
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 5)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=330)
        #
        self.lab_q = loinc_q & (ref_comp_q | static_comp_q)


class Hep_A_IgM_Ab(BaseDiseaseComponent):
    '''
    IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)
    '''
    name = 'IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)'
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='22314-9', LxTest_results__istartswith='reactiv')


class Hep_B_IgM_Ab(BaseDiseaseComponent):
    '''
    IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)
    '''
    name = 'IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)'
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='31204-1', LxTest_results__istartswith='reactiv')


class Hep_B_Surface(BaseDiseaseComponent):
    '''
    Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)
    '''
    name = 'Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)'
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='5195-3', LxTest_results__istartswith='reactiv')


class Hep_B_e_Antigen(BaseDiseaseComponent):
    '''
    Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)
    '''
    name = 'Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)'
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='13954-3', LxTest_results__istartswith='reactiv')


class Hep_B_Viral_DNA(BaseDiseaseComponent):
    '''
    Hepatitis B Viral DNA
    '''
    name = 'Hepatitis B Viral DNA'
    def q_setup(self):
        # NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" portion of algorithm
        #
        # Lab Result Query
        #
        # HEP B DNA PCR (QL) 
        lab_q = Q(LxLoinc='13126-8')
        lab_q = lab_q & ( Q(LxTest_results__istartswith='positiv') | Q(LxTest_results__istartswith='detect') )
        # HEP B VIRAL DNA IU/ML 
        lab_q = lab_q | Q(LxLoinc='16934-2', LxTest_results__gt=100)
        # HEP B DNA COPIES/ML 
        lab_q = lab_q | Q(LxLoinc='5009-6', LxTest_results__gt=160)
        self.lab_q = lab_q


class Hep_E_Ab(BaseDiseaseComponent):
    '''
    Hepatitis E antibody
    '''
    name = 'Hepatitis E antibody'
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='14212-5', LxTest_results__istartswith='reactiv')


class Hep_C_Ab(BaseDiseaseComponent):
    '''
    Hepatitis C antibody = "REACTIVE" (may be truncated)
    '''
    name = 'Hepatitis C antibody = "REACTIVE" (may be truncated)'
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='16128-1', LxTest_results__istartswith='reactiv')


class Total_Bilirubin_gt_1_5(BaseDiseaseComponent):
    '''
    Total bilirubin > 1.5
    '''
    name = 'Total bilirubin > 1.5'
    def q_setup(self):
        self.lab_q = Q(LxLoinc='33899-6', LxTest_results__gt=1.5)

class Calculated_Bilirubin_gt_1_5(BaseDiseaseComponent):
    '''
    '''
    name = ''
    def q_setup(self):
        self.encounter_q = None
    
        

#===============================================================================
#
#--- ~~~ Disease Definitions ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Acute_Hepatitis_A(BaseDiseaseDefinition):
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
    report_icd9s = []
    
    def get_patients(self):
        log.info('Searching for cases of Acute Hepatitis A')
        j = Jaundice()
        alt = ALT_2x_Upper_Limit()
        ast = AST_2x_Upper_Limit()
        ab = Hep_A_IgM_Ab()
        positive = sets.Set() # patients positive for Hep A
        for lab in ab.lab_results.select_related('LxPatient'):
            # These patients all tested positive for Hep A IgM antibody.  
            # Let's find out if they meet any of the other conditions.
            patient = lab.LxPatient
            log.debug('Patient has positive Hep A IgM antibody test:\n    %s' % patient)
            lab_date = util.date_from_str(lab.LxOrderDate)
            fourteen = datetime.timedelta(days=14)
            begin_date = lab_date - fourteen
            end_date = lab_date + fourteen
            log.debug('Analysing time window %s to %s.' % (begin_date, end_date))
            for test in [j, alt, ast]:
                tuple = test.get_patients(begin_date, end_date, patient, include_result=True)
                if tuple: # We got a positive!
                    msg = '\n'
                    msg += '    The following patient tested positive for Hepatitis A IgM antibody, and\n' 
                    msg += '    for "%s"\n' % test.name
                    msg += '    with results: "%s"\n' % tuple[0][1]
                    msg += '    within +/- 14 days, fulfilling criteria for an Acute Hep A case:\n'
                    msg += '    %s' % patient
                    log.info(msg)
                    positive.add(patient)
                    break # Only need one positive in this bunch
        return positive
                                

if __name__ == '__main__':
    hep_a= Acute_Hepatitis_A()
    for p in hep_a.get_patients():
        hep_a.make_case(p)
    #pprint.pprint(connection.queries)
    
