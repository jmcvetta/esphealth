'''
                              ESP Health Project
                          Heuristic Events Framework
                         Admin Interface Configuration
'''

from django.contrib import admin


from ESP.hef.models import LabTestMap
from ESP.hef.models import LabOrderHeuristic
from ESP.hef.models import LabResultPositiveHeuristic
from ESP.hef.models import LabResultRatioHeuristic
from ESP.hef.models import LabResultRangeHeuristic
from ESP.hef.models import LabResultFixedThresholdHeuristic
from ESP.hef.models import DiagnosisHeuristic
from ESP.hef.models import PrescriptionHeuristic
from ESP.hef.models import Dose
from ESP.hef.models import ResultString


class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'patient', 'content_object']

class LabTestMapAdmin(admin.ModelAdmin):
    list_display = ['test', 'native_code', 'record_type', 'code_match_type']
    list_filter = ['record_type', 'test']
    search_fields = ['native_code']
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
            'fields': ('test',)
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
    

class LabOrderHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test']
    list_filter = ['test']

class LabResultPositiveHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test']
    list_filter = ['test']

class LabResultRatioHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test', 'ratio']
    list_filter = ['test']
    
class LabResultRangeHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test', 'minimum', 'maximum']
    list_filter = ['test']

class LabResultFixedThresholdHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test', 'threshold']
    list_filter = ['test']

class DoseAdmin(admin.ModelAdmin):
    list_display = ['units', 'quantity']
    list_filter = ['units']

class EncounterHeuristicAdmin(admin.ModelAdmin):
    list_display = ['name', ]

class PrescriptionHeuristicAdmin(admin.ModelAdmin):
    list_display = ['name', 'drugs', 'exclude', 'require']

class ResultStringAdmin(admin.ModelAdmin):
    list_display = ['value', 'indicates', 'match_type', 'applies_to_all']
    list_filter = ['indicates', 'match_type', 'applies_to_all']


admin.site.register(LabTestMap, LabTestMapAdmin)
admin.site.register(LabOrderHeuristic, LabOrderHeuristicAdmin)
admin.site.register(LabResultPositiveHeuristic, LabResultPositiveHeuristicAdmin)
admin.site.register(LabResultRatioHeuristic, LabResultRatioHeuristicAdmin)
admin.site.register(LabResultRangeHeuristic, LabResultRangeHeuristicAdmin)
admin.site.register(LabResultFixedThresholdHeuristic, LabResultFixedThresholdHeuristicAdmin)
admin.site.register(DiagnosisHeuristic, EncounterHeuristicAdmin)
admin.site.register(PrescriptionHeuristic, PrescriptionHeuristicAdmin)
admin.site.register(ResultString, ResultStringAdmin)