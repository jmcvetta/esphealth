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
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['provider_id_num', 'name', 'dept']
    search_fields = ['provider_id_num','last_name']

class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id_num', 'name', 'pcp', 'zip']
    search_fields = ['patient_id_num', 'last_name']

class LabResultAdmin(admin.ModelAdmin):
    list_display = ['order_num', 'native_name', 'patient', 'provider', 'result_string']
    list_display_links = ['order_num']
    search_fields = ['native_code', 'native_name', 'patient', 'provider', 'result_string']
    ordering = ['-date']

class EncounterAdmin(admin.ModelAdmin):
    list_display = ['native_encounter_num', 'patient', 'provider', 'date']
    list_display_links = ['native_encounter_num']
    raw_id_fields = ['patient', 'provider']
    search_fields = ['native_encounter_num', 'patient__last_name', 'provider__last_name']
    ordering = ['-date']

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['order_num', 'date', 'patient', 'name', 'dose']
    search_fields = ['order_num', 'name', 'patient__last_name']
    ordering = ['-date']

class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ['imm_id_num', 'date', 'patient', 'name']
    search_fields = ['imm_id_num', 'name', 'patient__last_name']
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
admin.site.register(Encounter, EncounterAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(Immunization, ImmunizationAdmin)
admin.site.register(Provenance, ProvenanceAdmin)
