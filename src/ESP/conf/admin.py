from django.contrib import admin

from ESP.conf.models import CodeMap
from ESP.conf.models import IgnoredCode
from ESP.conf.models import ConditionConfig
from ESP.conf.models import ReportableLab
from ESP.conf.models import ReportableIcd9
from ESP.conf.models import ReportableMedication


class CodeMapAdmin(admin.ModelAdmin):
    list_display = ['id', 'native_code', 'native_name', 'heuristic', 'threshold', 'output_code', 'notes']
    list_filter = ['heuristic']
    search_fields = ['native_code', 'native_name', 'output_code']
    save_on_top = True
    ordering = ['output_code', 'native_code', 'heuristic']

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
	    'icd9_days_before',
	    'icd9_days_after',
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

class ReportableIcd9Admin(admin.ModelAdmin):
    list_display = ['condition', 'icd9']
    ordering = ['condition', 'icd9']
    list_filter = ['condition']
    raw_id_fields = ['icd9']

admin.site.register(CodeMap, CodeMapAdmin)
admin.site.register(IgnoredCode, IgnoredCodeAdmin)
admin.site.register(ConditionConfig, ConditionConfigAdmin)
admin.site.register(ReportableLab, ReportableLabAdmin)
admin.site.register(ReportableMedication, ReportableMedicationAdmin)
admin.site.register(ReportableIcd9, ReportableIcd9Admin)