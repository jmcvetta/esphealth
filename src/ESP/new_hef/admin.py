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


class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'patient', 'content_object']


class AbstractLabTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'reportable']


class LabTestMapAdmin(admin.ModelAdmin):
    list_display = ['test', 'code', 'code_match_type']


class LabOrderHeuristicAdmin(admin.ModelAdmin):
    list_display = ['verbose_name', 'test']

class LabResultPositiveHeuristicAdmin(admin.ModelAdmin):
    list_display = ['test']


admin.site.register(AbstractLabTest, AbstractLabTestAdmin)
admin.site.register(LabTestMap, LabTestMapAdmin)
admin.site.register(LabOrderHeuristic, LabOrderHeuristicAdmin)
admin.site.register(LabResultPositiveHeuristic, LabResultPositiveHeuristicAdmin)
