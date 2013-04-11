#!/usr/bin/python
# -*- coding: utf-8 -*-

from segments import OBX
from ESP.utils import utils
from ESP.conf.models import VaccineCodeMap
from ESP.static.models import Vaccine

class VaccineDetail(object):
    def __init__(self, immunization):
        vaccine_type = OBX()
        vaccine_type.value_type = 'CE'
        CVXVax = Vaccine.objects.get(id=VaccineCodeMap.objects.filter(native_code=self.imm_type).distinct('canonical_code_id').canonical_code_id)
            #sites have been known to update their vaccine names, while keeping the IDs the same, causing the need for multiple
            # rows in VaccineCodeMap for each immunization type.  This will break if rows for the same immunization type are mapped to
            # multiple canonical codes in static_vaccine
        vaccine_type.identifier = ['30955-9&30956-7', 'Vaccine type', 'LN']
        vaccine_type.value = [CVXVax.code, 
                              CVXVax.short_name, 'CVX']
        vaccine_type.observation_result_status = 'F'

        if immunization.vaccine_manufacturer:
            manufacturer = OBX()
            manufacturer.value_type = 'CE'
            manufacturer.identifier = ['30955-9&30957-5', 'Manufacturer', 'LN']
            manufacturer.value = [immunization.vaccine_manufacturer, 'MVX']
            manufacturer.observation_result_status = 'F'
        else:
            manufacturer = None
            
        if immunization.lot:
            lot_no = OBX()
            lot_no.value_type = 'ST'
            lot_no.identifier = ['30955-9&30959-1', 'Lot number', 'LN']
            lot_no.value = immunization.lot
            lot_no.observation_result_status = 'F'        
        else:
            lot_no = None
           
        self.vaccine_type = vaccine_type
        self.manufacturer = manufacturer
        self.lot_no = lot_no

        for idx, seg in enumerate(self.segments):
            seg.subsequence_id = idx + 1

    segments = property(lambda x: [segment for segment in [x.vaccine_type, x.manufacturer, x.lot_no] if segment is not None])

class PriorVaccinationDetail(VaccineDetail):
    def __init__(self, immunization):
        
        self.vaccine_type = OBX()
        self.vaccine_type.value_type = 'CE'
        CVXVax = Vaccine.objects.get(id=VaccineCodeMap.objects.filter(native_code=self.imm_type).distinct('canonical_code_id').canonical_code_id)
            #sites have been known to update their vaccine names, while keeping the IDs the same, causing the need for multiple
            # rows in VaccineCodeMap for each immunization type.  This will break if rows for the same immunization type are mapped to
            # multiple canonical codes in static_vaccine
        self.vaccine_type.identifier = ['30961-7&30956-7', 'Vaccine type', 'LN']
        self.vaccine_type.value = [CVXVax.code, 
                                   CVXVax.short_name, 'CVX']
        self.vaccine_type.observation_result_status = 'F'
        

        if immunization.vaccine_manufacturer:
            self.manufacturer = OBX()
            self.manufacturer.value_type = 'CE'
            self.manufacturer.identifier = ['30961-7&30957-5', 'Manufacturer', 'LN']
            self.manufacturer.value = [immunization.vaccine_manufacturer.code, 
                                       immunization.vaccine_manufacturer.full_name, 'MVX']
            self.manufacturer.observation_result_status = 'F'
        else:
            self.manufacturer = None
        
        if immunization.lot:
            self.lot_no = OBX()
            self.lot_no.value_type = 'ST'
            self.lot_no.identifier = ['30955-9&30959-1', 'Lot number', 'LN']
            self.lot_no.value = immunization.lot
            self.lot_no.observation_result_status = 'F'        
        else:
            self.lot_no = None
           
        self.date_given = OBX()
        self.date_given.value_type = 'TS'
        self.date_given.identifier = ['30961-7&31035-9', 'Date given^LN']
        self.date_given.value = utils.str_from_date(immunization.date)
        self.date_given.observation_result_status = 'F'


        for idx, seg in enumerate(self.segments):
            seg.subsequence_id = idx + 1

    segments = property(lambda x: [segment for segment in [x.vaccine_type, x.manufacturer, x.lot_no, x.date_given] if segment is not None])



class VaersProjectIdentification(object):
    def __init__(self):
        self.report_type = OBX()
        self.report_type.value_type = 'CE'
        self.report_type.identifier = ['30978-1', 'Report type', 'LN']
        self.report_type.value = ['I', 'Initial', 'NIP010']
        self.report_type.observation_result_status = 'F'
        
    segments = property(lambda x: [x.report_type])

        
