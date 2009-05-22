from django.contrib import admin
from vaers.models import EncounterEvent, LabResultEvent
from vaers.models import DiagnosticsEventRule

class EncounterEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    fields = ['matching_rule_explain', 'date', 'category', 'state']
    list_display = ['matching_rule_explain', 'encounter', 'date', 'category',
                    'state', 'digest']
    list_filter = ['date', 'category', 'state']

class LabResultAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    fields = ['matching_rule_explain', 'date', 'category', 'state']
    list_display = ['matching_rule_explain', 'lab_result', 'date', 'category',
                    'state', 'digest']
    list_filter = ['date', 'category', 'state']

admin.site.register(EncounterEvent, EncounterEventAdmin)
admin.site.register(LabResultEvent, LabResultAdmin)
admin.site.register(DiagnosticsEventRule)
