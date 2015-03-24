from django.contrib import admin

from ESP.conf.models import LabTestMap
from ESP.conf.models import IgnoredCode
from ESP.conf.models import ConditionConfig
from ESP.conf.models import ReportableLab
from ESP.conf.models import ReportableDx_Code
from ESP.conf.models import ReportableMedication
from ESP.conf.models import ReportableExtended_Variables, Extended_VariablesMap
from ESP.conf.models import ResultString
from ESP.conf.models import HL7Map
from ESP.conf.models import ImmuExclusion
from ESP.conf.models import SiteHL7
from ESP.conf.models import VaccineCodeMap
from ESP.conf.models import VaccineManufacturerMap


class LabTestMapAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'test_name',
        'native_code',
        'code_match_type',
        'record_type',
        'threshold',
        'reportable',
        'output_code',
        'output_name',
        ]
    list_filter = [
        'test_name',
        'reportable',
        'record_type'
        ]
    search_fields = [
        'test_name',
        'native_code',
        'output_code',
        'output_name'
        ]
    save_on_top = True
    ordering = ['test_name', 'native_code', 'output_code']
    filter_horizontal = [
        'extra_positive_strings', 
        'excluded_positive_strings',
        'extra_negative_strings',
        'excluded_negative_strings',
        'extra_indeterminate_strings',
        'excluded_indeterminate_strings',
        ]
    fieldsets = (
        (None, {
            'fields': ('test_name',)
            }),
        ('Mapping', {
            'fields': ('native_code', 'code_match_type', 'record_type', 'threshold'),
            }),
        ('Reporting', {
            'fields': ('reportable', 'output_code', 'output_name', 'snomed_pos', 'snomed_neg',  'snomed_ind', 'reinf_output_code'),
            'classes': ('collapse',),
            }),
        ('Result Strings', {
            'fields': (
		        'extra_positive_strings', 
		        'excluded_positive_strings',
		        'extra_negative_strings',
		        'excluded_negative_strings',
		        'extra_indeterminate_strings',
		        'excluded_indeterminate_strings',
                ),
            'classes': ('collapse',),
            }),
        ('', {
            'fields': ('notes',)
            }),
        )
    

class IgnoredCodeAdmin(admin.ModelAdmin):
    search_fields = ['native_code']
    ordering = ['native_code']

class ConditionConfigAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = [
        'name', 
        'initial_status',
	    'lab_days_before',
	    'lab_days_after',
	    'dx_code_days_before',
	    'dx_code_days_after',
	    'med_days_before',
	    'med_days_after',
        'ext_var_days_before',
        'ext_var_days_after',
        'reinfection_days',
        ]
    list_filter = ['initial_status']
    
class ReportableLabAdmin(admin.ModelAdmin):
    ordering = ['condition', 'native_name']
    list_display = ['condition', 'native_name']
    list_filter = ['condition']

class ReportableMedicationAdmin(admin.ModelAdmin):
    ordering = ['condition', 'drug_name']
    list_display = ['condition', 'drug_name']
    list_filter = ['condition']

class ReportableDx_CodeAdmin(admin.ModelAdmin):
    list_display = ['condition', 'dx_code']
    ordering = ['condition', 'dx_code']
    list_filter = ['condition']
    raw_id_fields = ['dx_code']

class ReportableExtended_VariablesAdmin(admin.ModelAdmin):
    list_display = ['condition', 'abstract_ext_var']
    ordering = ['condition', 'abstract_ext_var']
    list_filter = ['condition']
    raw_id_fields = ['abstract_ext_var']

class Extended_VariablesMapAdmin(admin.ModelAdmin):
    list_display = ['native_string', 'abstract_ext_var']
    ordering = ['abstract_ext_var', 'native_string']
    list_filter = ['abstract_ext_var']
    

class ResultStringAdmin(admin.ModelAdmin):
    list_display = ['value', 'indicates', 'match_type', 'applies_to_all']
    list_filter = ['indicates', 'match_type', 'applies_to_all']
    
class HL7MapAdmin(admin.ModelAdmin):
    search_fields = ['model']
    ordering = ['hl7']

class ImmuExclusionAdmin (admin.ModelAdmin):
    search_fields = ['non_immu_name']
    ordering = ['non_immu_name']
    
class SiteHL7Admin (admin.ModelAdmin):
    search_fields = ['location']
    ordering = ['location']

class VaccineCodeMapAdmin (admin.ModelAdmin):
    list_display = ['native_code', 'native_name','canonical_code']
    search_fields = ['native_code', 'canonical_code']
    ordering = ['native_code']

class VaccineManufacturerMapAdmin (admin.ModelAdmin):
    list_display = ['id', 'native_name','canonical_code']
    search_fields = ['native_name', 'canonical_code']
    ordering = ['native_name']

admin.site.register(IgnoredCode, IgnoredCodeAdmin)
admin.site.register(ConditionConfig, ConditionConfigAdmin)
admin.site.register(ReportableLab, ReportableLabAdmin)
admin.site.register(ReportableMedication, ReportableMedicationAdmin)
admin.site.register(ReportableDx_Code, ReportableDx_CodeAdmin)
admin.site.register(ReportableExtended_Variables, ReportableExtended_VariablesAdmin)
admin.site.register(Extended_VariablesMap, Extended_VariablesMapAdmin)
admin.site.register(LabTestMap, LabTestMapAdmin)
admin.site.register(ResultString, ResultStringAdmin)
admin.site.register(HL7Map, HL7MapAdmin)
admin.site.register(ImmuExclusion, ImmuExclusionAdmin)
admin.site.register(SiteHL7, SiteHL7Admin)
admin.site.register(VaccineCodeMap, VaccineCodeMapAdmin)
admin.site.register(VaccineManufacturerMap, VaccineManufacturerMapAdmin)

