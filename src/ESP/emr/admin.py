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


class Provider_Admin(admin.ModelAdmin):
    list_display = ['name',]

class Patient_Admin(admin.ModelAdmin):
    list_display = ['name',]

class Lab_Result_Admin(admin.ModelAdmin):
    list_display = ['native_code', 'patient', 'provider',]

class Encounter_Admin(admin.ModelAdmin):
    list_display = ['patient', 'provider']
    raw_id_fields = ['patient', 'provider']


admin.site.register(Provider, Provider_Admin)
admin.site.register(Patient, Patient_Admin)
admin.site.register(LabResult, Lab_Result_Admin)
admin.site.register(Encounter, Encounter_Admin)
admin.site.register(Provenance)
