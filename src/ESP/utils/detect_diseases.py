#!/usr/bin/env python
'''
Detect cases of (reportable) disease
'''

import datetime
import pprint

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models.query import QuerySet


from ESP import settings
from ESP.esp import models
from ESP.utils.utils import log


#===============================================================================
#
#--- ~~~ Base Classes ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseDiseaseComponent:
    '''
    Abstract interface class for components detection algorithms
    '''
    
    def __init__(self, lookback=0):
        '''
        @param lookback: Include encounters/lab results occurring no more 
            than this many days before today.  If lookback is 0 or None, all 
            records are examined.
        @type lookback: Integer
        '''
        self.encounter_q = None # Q object
        self.patient_q = None # Q object
        self.lab_q = None # Q object
        self.lookback_days = lookback
        self.q_setup() 
    
    def q_setup(self):
        '''
        Setup the Q objects -- this must be implemented in concrete classes
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseDiseaseComponent.')
    
    def _get_begin_date_str(self):
        '''
        Returns a string representing the first date of the lookback window
        '''
        if not self.lookback_days: # Start from the beginning
            return '0'
        begin = datetime.date.today() - datetime.timedelta(days=self.lookback_days)
        y = begin.year
        m = begin.month
        d = begin.day
        return '%04d%02d%02d' % (y, m, d)
    begin_date_str = property(_get_begin_date_str)
        
    def get_encounters(self, queryset=None):
        '''
        Return all encounters matching this component
        '''
        if queryset:
            qs = queryset
        else:
            qs = models.Enc.objects.filter(EncEncounter_Date__gte=self.begin_date_str)
        if not self.encounter_q:
            return qs.none()
        log.debug('encounter_q: %s' % self.encounter_q)
        return qs.filter(self.encounter_q).distinct()
    encounters = property(get_encounters)
    
    def get_lab_results(self, queryset=None):
        '''
        Return all lab results matching this component
        '''
        if queryset:
            qs = queryset
        else:
            qs = models.Lx.objects.filter(LxDate_of_result__gte=self.begin_date_str)
        if not self.lab_q:
            return qs.none()
        log.debug('lab_q: %s' % self.lab_q)
        return qs.filter(self.lab_q).distinct()
    lab_results = property(get_lab_results)
    
    def get_patients(self, queryset=None):
        '''
        Return all patients matching this component
        '''
        if queryset:
            qs = queryset.select_related()
        else:
            qs = models.Demog.objects.select_related()
        if not self.patient_q:
            return qs.none()
        log.debug('patient_q: %s' % self.patient_q)
        return qs.filter(self.patient_q).distinct()
    patients = property(get_patients)


class BaseDiseaseDefinition:
    def get_patients(self):
        raise NotImplementedError

#===============================================================================
#
#--- ~~~ Diagnosis Components ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                
class Jaundice(BaseDiseaseComponent):
    '''
    Jaundice, not of newborn
    '''
    def q_setup(self):
        self.encounter_q = Q(EncICD9_Codes__icontains='782.4')
        self.lab_q = None
        self.patient_q = Q(enc__EncICD9_Codes__icontains='782.4')


class Chronic_Hep_B(BaseDiseaseComponent):
    '''
    Chronic Hepatitis B ICD9 = 070.32
    '''
    def q_setup(self):
        self.encounter_q = Q(EncICD9_Codes__icontains='070.32')
        self.lab_q = None
        self.patient_q = Q(enc__EncICD9_Codes__icontains='070.32')
        

#===============================================================================
#
#--- ~~~ Lab Test Components ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                

class ALT_2x_Upper_Limit(BaseDiseaseComponent):
    '''
    Alanine aminotransferase (ALT) >2x upper limit of normal
    '''
    def q_setup(self):
        # No Encounter Query
        self.encounter_q = None
        # Lab Result Query
        loinc_q = Q(LxLoinc='1742-6')
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 2)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=132)
        self.lab_q = loinc_q & (ref_comp_q | static_comp_q)
        # Patient Query
        loinc_q = Q(lx__LxLoinc='1742-6')
        no_ref_q = Q(lx__LxReference_High=None) | Q(lx__LxReference_High='')
        ref_comp_q = no_ref_q & Q(lx__LxTest_results__gt=F('lx__LxReference_High') * 2)
        static_comp_q = ~no_ref_q & Q(lx__LxTest_results__gt=132)
        self.patient_q = loinc_q & (ref_comp_q | static_comp_q)


class ALT_5x_Upper_Limit(BaseDiseaseComponent):
    '''
    Alanine aminotransferase (ALT) >5x upper limit of normal
    '''
    def q_setup(self):
        # No Encounter Query
        self.encounter_q = None
        # Lab Result Query
        loinc_q = Q(LxLoinc='1742-6')
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 5)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=330)
        self.lab_q = loinc_q & (ref_comp_q | static_comp_q)
        # Patient Query
        loinc_q = Q(lx__LxLoinc='1742-6')
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(lx__LxReference_High=None) | Q(lx__LxReference_High='')
        ref_comp_q = no_ref_q & Q(lx__LxTest_results__gt=F('lx__LxReference_High') * 5)
        static_comp_q = ~no_ref_q & Q(lx__LxTest_results__gt=330)
        self.patient_q = loinc_q & (ref_comp_q | static_comp_q)


class AST_2x_Upper_Limit(BaseDiseaseComponent):
    '''
    Aspartate aminotransferase (AST) >2x upper limit of normal
    '''
    def q_setup(self):
        # No Encounter Query
        self.encounter_q = None
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
        #
        # Patient Query
        #
        loinc_q = Q(lx__LxLoinc='1920-8')
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(lx__LxReference_High=None) | Q(lx__LxReference_High='')
        ref_comp_q = no_ref_q & Q(lx__LxTest_results__gt=F('lx__LxReference_High') * 2)
        static_comp_q = ~no_ref_q & Q(lx__LxTest_results__gt=132)
        #
        self.patient_q = loinc_q & (ref_comp_q | static_comp_q)


class AST_5x_Upper_Limit(BaseDiseaseComponent):
    '''
    Aspartate aminotransferase (AST) >2x upper limit of normal
    '''
    def q_setup(self):
        # No Encounter Query
        self.encounter_q = None
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
        #
        # Patient Query
        #
        loinc_q = Q(lx__LxLoinc='1920-8')
        # If record has a reference high, compare test result against that 
        # reference.  Otherwise, compare against a default 'high' value.
        no_ref_q = Q(lx__LxReference_High=None) | Q(lx__LxReference_High='')
        ref_comp_q = no_ref_q & Q(lx__LxTest_results__gt=F('lx__LxReference_High') * 5)
        static_comp_q = ~no_ref_q & Q(lx__LxTest_results__gt=330)
        #
        self.patient_q = loinc_q & (ref_comp_q | static_comp_q)


class Hep_A_IgM_Ab(BaseDiseaseComponent):
    '''
    IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)
    '''
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='22314-9', LxTest_results__istartswith='reactiv')
        self.patient_q = Q(lx__LxLoinc='22314-9', lx__LxTest_results__istartswith='reactiv')


class Hep_B_IgM_Ab(BaseDiseaseComponent):
    '''
    IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)
    '''
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='31204-1', LxTest_results__istartswith='reactiv')
        self.patient_q = Q(lx__LxLoinc='31204-1', lx__LxTest_results__istartswith='reactiv')


class Hep_B_Surface(BaseDiseaseComponent):
    '''
    Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)
    '''
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='5195-3', LxTest_results__istartswith='reactiv')
        self.patient_q = Q(lx__LxLoinc='5195-3', lx__LxTest_results__istartswith='reactiv')


class Hep_B_e_Antigen(BaseDiseaseComponent):
    '''
    Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)
    '''
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='13954-3', LxTest_results__istartswith='reactiv')
        self.patient_q = Q(lx__LxLoinc='13954-3', lx__LxTest_results__istartswith='reactiv')


class Hep_B_Viral_DNA(BaseDiseaseComponent):
    '''
    Hepatitis B Viral DNA
    '''
    def q_setup(self):
        self.encounter_q = None
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
        #
        # Patient Query
        #
        # HEP B DNA PCR (QL) 
        patient_q = Q(lx__LxLoinc='13126-8')
        patient_q = patient_q & ( Q(lx__LxTest_results__istartswith='positiv') | Q(lx__LxTest_results__istartswith='detect') )
        # HEP B VIRAL DNA IU/ML 
        patient_q = patient_q | Q(lx__LxLoinc='16934-2', lx__LxTest_results__gt=100)
        # HEP B DNA COPIES/ML 
        patient_q = patient_q | Q(lx__LxLoinc='5009-6', lx__LxTest_results__gt=160)
        self.patient_q = patient_q


class Hep_E_Ab(BaseDiseaseComponent):
    '''
    Hepatitis E antibody
    '''
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='14212-5', LxTest_results__istartswith='reactiv')
        self.patient_q = Q(lx__LxLoinc='14212-5', lx__LxTest_results__istartswith='reactiv')


class Hep_C_Ab(BaseDiseaseComponent):
    '''
    Hepatitis C antibody = "REACTIVE" (may be truncated)
    '''
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='16128-1', LxTest_results__istartswith='reactiv')
        self.patient_q = Q(lx__LxLoinc='16128-1', lx__LxTest_results__istartswith='reactiv')


class Total_Bilirubin_gt_1_5(BaseDiseaseComponent):
    '''
    Total bilirubin > 1.5
    '''
    def q_setup(self):
        self.encounter_q = None
        self.lab_q = Q(LxLoinc='33899-6', LxTest_results__gt=1.5)
        self.patient_q = Q(lx__LxLoinc='33899-6', LxTest_results__gt=1.5)

class Calculated_Bilirubin_gt_1_5(BaseDiseaseComponent):
    '''
    '''
    def q_setup(self):
        self.encounter_q = None
    
        

#===============================================================================
#
#--- ~~~ Disease Definitions ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Acute_Hepatitis_A(BaseDiseaseDefinition):
    def get_patients(self):
        j = Jaundice()
        alt = ALT_2x_Upper_Limit()
        ast = AST_2x_Upper_Limit()
        ab = Hep_A_IgM_Ab()
        #q_obj = ab.patient_q & (j.patient_q | alt.patient_q | ast.patient_q)
        q_obj = ab.patient_q 
        return models.Demog.objects.filter(q_obj).distinct()
                                

if __name__ == '__main__':
    x = Acute_Hepatitis_A()
    #x = Jaundice(lookback=365)
    for p in x.get_patients():
        print p
    #print 'patients:    %s' % x.get_patients().count()
    pprint.pprint(connection.queries)
    