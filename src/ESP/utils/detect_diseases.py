#!/usr/bin/env python
'''
Detect cases of (reportable) disease
'''

import pprint

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models.query import QuerySet


from ESP import settings
from ESP.esp import models
from ESP.utils.utils import log


class BaseDiseaseComponent:
    '''
    Abstract interface class for components detection algorithms
    '''
    
    def __init__(self):
        self.encounter_q = None # Q object
        self.patient_q = None # Q object
        self.result_q = None # Q object
        
    def encounters(self, queryset=None):
        if queryset:
            qs = queryset
        else:
            qs = models.Enc.objects.all()
        if not self.encounter_q:
            return qs.none()
        log.debug('encounter_q: %s' % self.encounter_q)
        return qs.filter(self.encounter_q)
    
    def lab_results(self, queryset=None):
        if queryset:
            qs = queryset
        else:
            qs = models.Lx.objects.all()
        if not self.result_q:
            return qs.none()
        log.debug('result_q: %s' % self.result_q)
        return qs.filter(self.result_q)
    
    def patients(self, queryset=None):
        if queryset:
            qs = queryset.select_related()
        else:
            qs = models.Demog.objects.select_related()
        if not self.patient_q:
            return qs.none()
        log.debug('patient_q: %s' % self.patient_q)
        return qs.filter(self.patient_q)


class Jaundice(BaseDiseaseComponent):
    '''
    Jaundice, not of newborn
    '''
    def __init__(self):
        self.encounter_q = Q(EncICD9_Codes__icontains='782.4')
        self.patient_q = Q(enc__EncICD9_Codes__icontains='782.4')
        self.result_q = None


class Alt_2x_Upper_Limit(BaseDiseaseComponent):
    '''
    Alanine aminotransferase (ALT) >2x upper limit of normal
    '''
    def __init__(self):
        loinc_q = Q(LxLoinc__icontains='1920-8')
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * 2)
        static_comp_q = ~no_ref_q & Q(LxTest_results__gt=132)
        self.result_q = loinc_q & (ref_comp_q | static_comp_q)
        #
        loinc_q = Q(lx__LxLoinc__icontains='1920-8')
        no_ref_q = Q(lx__LxReference_High=None) | Q(LxReference_High='')
        ref_comp_q = no_ref_q & Q(lx__LxTest_results__gt=F('lx__LxReference_High') * 2)
        static_comp_q = ~no_ref_q & Q(lx__LxTest_results__gt=132)
        self.patient_q = None




if __name__ == '__main__':
    j = Jaundice()
    print j.lab_results().count()
    print j.encounters().count()
    print j.patients().count()
    pprint.pprint(connection.queries)