'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                         Admin Interface Configuration

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


from django.contrib import admin

from ESP.emr.models import Provenance
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import LabOrder
from ESP.emr.models import Encounter,EncounterTypeMap
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Allergy
from ESP.emr.models import Problem
from ESP.emr.models import Hospital_Problem
from ESP.emr.models import SocialHistory, Pregnancy
from ESP.emr.models import Patient_Addr
from ESP.emr.models import Patient_ExtraData
from ESP.emr.models import Patient_Guardian
from ESP.emr.models import Provider_idInfo
from ESP.emr.models import Provider_phones
from ESP.emr.models import Order_idInfo, Order_Extension
from ESP.emr.models import LabInfo
from ESP.emr.models import Specimen
from ESP.emr.models import SpecObs

STANDARD_SEARCH_FIELDS = ['natural_key', 'patient__mrn', 'patient__last_name', 'provider__last_name']
STANDARD_RAW_ID_FIELDS = ['provenance', 'patient', 'provider']


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'name', 'dept']
    search_fields = ['natural_key','last_name']

class PatientAdmin(admin.ModelAdmin):
    ordering = ['natural_key','mrn','last_name']
    list_display = ['natural_key','mrn', 'name', 'pcp', 'zip']
    search_fields = ['natural_key', 'mrn','last_name']

class Patient_AddrAdmin(admin.ModelAdmin):
    ordering = ['mrn']
    list_display = ['mrn', 'address1']
    search_fields = ['address1', 'mrn']
    
class Patient_ExtraDataAdmin (admin.ModelAdmin):
    ordering = ['mrn']
    list_display = ['mrn', 'auth_nid']
    search_fields = ['mrn', 'auth_nid']
    
class Patient_GuardianAdmin(admin.ModelAdmin):
    ordering = ['mrn','first_name','last_name']
    list_display = [  'mrn','first_name','last_name']
    search_fields = [  'first_name','last_name']
    
class Provider_idInfoAdmin(admin.ModelAdmin):
    ordering = ['provider_natural_key']
    list_display = ['provider_natural_key', 'provider_nistid']
    search_fields = ['provider_natural_key', 'provider_nistid']
    
class Provider_phonesAdmin(admin.ModelAdmin):
    ordering = ['provider_natural_key']
    list_display = ['provider_natural_key', 'provider_phone_id']
    search_fields = ['provider_natural_key', 'provider_phone_id']

class LabResultAdmin(admin.ModelAdmin):
    list_display = ['pk', 'natural_key', 'native_name', 'native_code', 'patient', 'provider', 'result_string']
    list_display_links = ['pk', 'natural_key']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['native_code', 'native_name']
    ordering = ['-date']

class LabOrderAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'procedure_code', 'procedure_modifier', 'procedure_name', 'order_type']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['procedure_name', 'procedure_code']
    ordering = ['-date']
    
class Order_ExtensionAdmin(admin.ModelAdmin):
    ordering = ['order_natural_key']
    list_display = ['order_natural_key', 'question']
    search_fields = ['order_natural_key', 'question']
    

class Order_idInfoAdmin(admin.ModelAdmin):
    ordering = ['order_natural_key']
    list_display = ['order_natural_key', 'placer_ord_eid']
    search_fields = ['order_natural_key', 'placer_ord_eid']
    
class EncounterAdmin(admin.ModelAdmin):
    list_display = ['pk', 'natural_key', 'patient', 'provider', 'date']
    raw_id_fields = STANDARD_RAW_ID_FIELDS + ['dx_codes','encounter_type']
    search_fields = STANDARD_SEARCH_FIELDS
#    ordering = ['-date']
    ordering = ['pk']
    
class EncounterTypeMapAdmin(admin.ModelAdmin):
    list_display = ['pk',  'raw_encounter_type', 'mapping', 'priority']
    search_fields = [ 'raw_encounter_type', 'mapping']
    ordering = ['pk']

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'date', 'patient', 'name', 'dose']
    raw_id_fields = STANDARD_RAW_ID_FIELDS 
    search_fields = STANDARD_SEARCH_FIELDS + ['name']
    ordering = ['-date']

class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'date', 'patient', 'name']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['name']
    ordering = ['-date']
    
class LabInfoAdmin(admin.ModelAdmin):
    ordering = ['CLIA_ID']
    list_display = ['CLIA_ID', 'laboratory_name']
    search_fields = ['CLIA_ID']

class AllergyAdmin(admin.ModelAdmin):
    list_display = ['date', 'patient', 'name','status','description']
    raw_id_fields = STANDARD_RAW_ID_FIELDS 
    search_fields = STANDARD_SEARCH_FIELDS + ['name']
    ordering = ['-date']
    
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'date', 'patient', 'status','comment']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['comment']
    ordering = ['-date']
 
class HospitalProblemAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'date', 'patient', 'status']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['dx_code']
    ordering = ['-date']
   
class SocialHistoryAdmin(admin.ModelAdmin):
    list_display = ['date', 'patient','tobacco_use','alcohol_use']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['tobacco_use','alcohol_use']
    ordering = ['-date']
    
class SpecimenAdmin(admin.ModelAdmin):
    ordering = ['specimen_num']
    list_display = ['specimen_num', 'order_natural_key']
    search_fields = ['specimen_num']

class SpecObsAdmin(admin.ModelAdmin):
    ordering = ['specimen_num']
    list_display = ['specimen_num', 'order_natural_key']
    search_fields = ['specimen_num','result']

class PregnancyAdmin(admin.ModelAdmin):
    list_display = ['actual_date', 'patient','edd', 'outcome','ga_delivery', 'birth_weight']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS 
    ordering = ['-edd']    

class ProvenanceAdmin(admin.ModelAdmin):
    list_display = ['provenance_id', 'timestamp', 'source', 'status']
    list_display_links = ['provenance_id', 'source']
    ordering = ['-timestamp']
    search_fields = ['source']
    list_filter = ['status']


admin.site.register(Provider, ProviderAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(LabResult, LabResultAdmin)
admin.site.register(LabOrder, LabOrderAdmin)
admin.site.register(Encounter, EncounterAdmin)
admin.site.register(EncounterTypeMap,EncounterTypeMapAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(Immunization, ImmunizationAdmin)
admin.site.register(Allergy, AllergyAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Hospital_Problem, HospitalProblemAdmin)
admin.site.register(SocialHistory, SocialHistoryAdmin)
admin.site.register(Pregnancy, PregnancyAdmin)
admin.site.register(Provenance, ProvenanceAdmin)
admin.site.register(Order_Extension, Order_ExtensionAdmin)
#added for meaninful use
admin.site.register(Patient_Addr, Patient_AddrAdmin)
admin.site.register(Patient_ExtraData, Patient_ExtraDataAdmin)
admin.site.register(Patient_Guardian, Patient_GuardianAdmin)
admin.site.register(Provider_idInfo, Provider_idInfoAdmin)
admin.site.register(Provider_phones, Provider_phonesAdmin)
admin.site.register(Order_idInfo, Order_idInfoAdmin)
admin.site.register(LabInfo, LabInfoAdmin)
admin.site.register(Specimen, SpecimenAdmin)
admin.site.register(SpecObs, SpecObsAdmin)