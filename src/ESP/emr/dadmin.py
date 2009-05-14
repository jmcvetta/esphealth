from django.contrib import admin
from ESP.core.models import SourceSystem
from ESP.core.models import Provider
from ESP.core.models import Patient
from ESP.core.models import LabOrder
from ESP.core.models import LabResult
from ESP.core.models import Encounter

class Source_System_Admin(admin.ModelAdmin):
    list_display = ['name', 'software']
    #list_filter = ['software']

class Provider_Admin(admin.ModelAdmin):
    list_display = ['name',]

class Patient_Admin(admin.ModelAdmin):
    list_display = ['name',]

class Lab_Order_Admin(admin.ModelAdmin):    
    list_display = ['ext_order_id_num',]

class Lab_Result_Admin(admin.ModelAdmin):
    list_display = ['native_code', 'patient', 'provider',]

class Loinc_Admin(admin.ModelAdmin):
    list_display = ['loinc_num', 'name']
    search_fields = ['loinc_num',]

class External_To_Loinc_Map_Admin(admin.ModelAdmin):
    list_display = ['ext_code', 'loinc', 'system',]
    list_filter = ['system',]
    list_search = ['ext_code', 'loinc',]

class Encounter_Admin(admin.ModelAdmin):
    list_display = ['patient', 'provider', 'cpt']
    raw_id_fields = ['patient', 'provider', 'cpt']

class Medical_Event_Admin(admin.ModelAdmin):
    list_display = ['patient', 'provider']
    raw_id_fields = ['patient', 'provider']

admin.site.register(SourceSystem, Source_System_Admin)
admin.site.register(Provider, Provider_Admin)
admin.site.register(Patient, Patient_Admin)
admin.site.register(LabOrder, Lab_Order_Admin)
admin.site.register(LabResult, Lab_Result_Admin)
admin.site.register(Encounter, Encounter_Admin)
