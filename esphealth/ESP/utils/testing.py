'''
                                  ESP Health
Utilities
Unit Testing Tools


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2012 Channing Laboratory
@license: LGPL
'''

from django.test import TestCase

from ESP.utils import log
from ESP.conf.models import LabTestMap
from ESP.emr.models import Provenance
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter



class EspTestCase(TestCase):
    
    def setUp(self):
        log.info('Creating TEST provenance')
        self.provenance = Provenance(source='TEST', hostname='TEST')
        self.provenance.save()
        
    def tearDown(self):
        log.info('Deleting TEST provenance')
        self.provenance.delete()
        del self.provenance
    
    
    def create_lab_result(self, provider, patient, date, alt, **kwargs):
        '''
        Create a LabResult and a LabTestMap for the specified abstract lab test.
        @param alt: Abstract lab test name
        @type alt:  String
        '''
        native_code = 'natcode--' + alt 
        native_code = native_code[:255]
        ltm, created = LabTestMap.objects.get_or_create(
            test_name = alt,
            native_code = native_code,
            code_match_type = 'exact',
            record_type = 'result',
            )
        if created:
            log.debug('Created %s' % ltm)
        new_lab = LabResult(
            provenance = self.provenance,
            provider = provider, 
            patient = patient,
            date = date,
            native_code = native_code,
            )
        for key in kwargs:
            if hasattr(new_lab, key):
                value = kwargs[key]
                setattr(new_lab, key, value)
        new_lab.save()
        log.debug('Created fake lab result: %s' % new_lab)
        return new_lab
    
    def create_diagnosis(self, provider, patient, date, codeset, diagnosis_code):
        '''
        Create a encounter record with the provided dxcode diagnosis'
        @param dxcode_str: dx code string to use in the record
        @type dxcode_str:  String
        @return: An encounter with the indicated properties
        @rtype:  Encounter
        '''
        new_enc = Encounter(
            provenance = self.provenance,
            provider = provider,
            patient = patient,
            date = date,
            )
        new_enc.save()
        new_enc.add_diagnosis(codeset=codeset, diagnosis_code=diagnosis_code)
        return new_enc
    
    def create_provider(self, last, first):
        new_prov = Provider(provenance=self.provenance, last_name=last, first_name=first)
        new_prov.save()
        return new_prov
    
    def create_patient(self, last, first, pcp):
        new_pat = Patient(provenance=self.provenance, last_name=last, first_name=first, pcp=pcp)
        new_pat.save()
        return new_pat
            

