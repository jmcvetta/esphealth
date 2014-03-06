from django.contrib import admin

from ESP.conf.models import LabTestMap
from ESP.conf.models import IgnoredCode
from ESP.conf.models import ConditionConfig
from ESP.conf.models import ReportableLab
from ESP.conf.models import ReportableDx_Code
from ESP.conf.models import ReportableMedication
from ESP.conf.models import ResultString


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
            'fields': ('native_code', 'code_match_type', 'record_type'),
            }),
        ('Reporting', {
            'fields': ('reportable', 'output_code', 'output_name', 'snomed_pos', 'snomed_neg',  'snomed_ind'),
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
        ]
    list_filter = ['initial_status']

class ReportableLabAdmin(admin.ModelAdmin):
    ordering = ['condition', 'native_code']
    list_display = ['condition', 'native_code', 'output_code']
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

class ResultStringAdmin(admin.ModelAdmin):
    list_display = ['value', 'indicates', 'match_type', 'applies_to_all']
    list_filter = ['indicates', 'match_type', 'applies_to_all']

admin.site.register(IgnoredCode, IgnoredCodeAdmin)
admin.site.register(ConditionConfig, ConditionConfigAdmin)
admin.site.register(ReportableLab, ReportableLabAdmin)
admin.site.register(ReportableMedication, ReportableMedicationAdmin)
admin.site.register(ReportableDx_Code, ReportableDx_CodeAdmin)
admin.site.register(LabTestMap, LabTestMapAdmin)
admin.site.register(ResultString, ResultStringAdmin)