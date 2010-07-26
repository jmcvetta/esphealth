'''
                              ESP Health Project
                          Heuristic Events Framework
                         Admin Interface Configuration
'''

from django.contrib import admin

from ESP.new_hef.models import AbstractLabTest
from ESP.new_hef.models import LabTestMap
from ESP.new_hef.models import LabOrderHeuristic
from ESP.new_hef.models import LabResultPositiveHeuristic
from ESP.new_hef.models import LabResultRatioHeuristic
from ESP.new_hef.models import LabResultFixedThresholdHeuristic
from ESP.new_hef.models import Dose


class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'patient', 'content_object']

class AbstractLabTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'reportable']

class LabTestMapAdmin(admin.ModelAdmin):
    list_display = ['test', 'code', 'code_match_type']

class LabOrderHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test']
    list_filter = ['test']

class LabResultPositiveHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test']
    list_filter = ['test']

class LabResultRatioHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test', 'ratio']
    list_filter = ['test']

class LabResultFixedThresholdHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test', 'threshold']
    list_filter = ['test']

class DoseAdmin(admin.ModelAdmin):
    list_display = ['units', 'quantity']
    list_filter = ['units']

admin.site.register(AbstractLabTest, AbstractLabTestAdmin)
admin.site.register(LabTestMap, LabTestMapAdmin)
admin.site.register(LabOrderHeuristic, LabOrderHeuristicAdmin)
admin.site.register(LabResultPositiveHeuristic, LabResultPositiveHeuristicAdmin)
admin.site.register(LabResultRatioHeuristic, LabResultRatioHeuristicAdmin)
admin.site.register(LabResultFixedThresholdHeuristic, LabResultFixedThresholdHeuristicAdmin)