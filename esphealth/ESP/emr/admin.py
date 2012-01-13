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
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Allergy
from ESP.emr.models import Problem
from ESP.emr.models import SocialHistory

STANDARD_SEARCH_FIELDS = ['natural_key', 'patient__mrn', 'patient__last_name', 'provider__last_name']
STANDARD_RAW_ID_FIELDS = ['provenance', 'patient', 'provider']


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'name', 'dept']
    search_fields = ['natural_key','last_name']

class PatientAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'name', 'pcp', 'zip']
    search_fields = ['natural_key', 'last_name']

class LabResultAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'native_name', 'patient', 'provider', 'result_string']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['native_code', 'native_name']
    ordering = ['-date']

class LabOrderAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'procedure_code', 'procedure_modifier', 'procedure_name', 'order_type']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['procedure_name', 'procedure_code']
    ordering = ['-date']

class EncounterAdmin(admin.ModelAdmin):
    list_display = ['natural_key', 'patient', 'provider', 'date']
    raw_id_fields = STANDARD_RAW_ID_FIELDS + ['icd9_codes']
    search_fields = STANDARD_SEARCH_FIELDS
    ordering = ['-date']

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
    
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['date', 'patient', 'name','status','description']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['name']
    ordering = ['-date']
    
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['problem_id', 'date', 'patient', 'status','comment']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['comment']
    ordering = ['-date']
    
class SocialHistoryAdmin(admin.ModelAdmin):
    list_display = ['date', 'patient','tobacco_use','alcohol_use']
    raw_id_fields = STANDARD_RAW_ID_FIELDS
    search_fields = STANDARD_SEARCH_FIELDS + ['tobacco_use','alcohol_use']
    ordering = ['-date']

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
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(Immunization, ImmunizationAdmin)
admin.site.register(Allergy, AllergyAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(SocialHistory, SocialHistoryAdmin)
admin.site.register(Provenance, ProvenanceAdmin)
