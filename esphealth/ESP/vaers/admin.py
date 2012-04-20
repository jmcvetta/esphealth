from django.contrib import admin
from ESP.vaers.models import EncounterEvent, LabResultEvent, PrescriptionEvent, AllergyEvent
from ESP.vaers.models import DiagnosticsEventRule, Sender

class EncounterEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    raw_id_fields = ['encounter']
    list_display = ['pk', 'matching_rule_explain', 'object_id', 'date', 'category',
                    'state', 'digest']
    list_filter = ['date', 'category', 'state']

class LabResultAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    fields = ['matching_rule_explain', 'date', 'category', 'state']
    list_display = ['matching_rule_explain', 'object_id', 'date', 'category',
                    'state', 'digest']
    list_filter = ['date', 'category', 'state']
    
class PrescriptionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    fields = ['matching_rule_explain', 'date', 'category', 'state']
    list_display = ['matching_rule_explain', 'object_id', 'date', 'category',
                    'state', 'digest']
    list_filter = ['date', 'category', 'state']  
      
class AllergyEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    raw_id_fields = ['allergy']
    list_display = ['pk', 'matching_rule_explain', 'object_id', 'date', 'category',
                    'state', 'digest']
    list_filter = ['date', 'category', 'state']
    
class SenderAdmin(admin.ModelAdmin):
    raw_id_fields = ['provider_id']
    list_display = ['pk','name']
    
admin.site.register(EncounterEvent, EncounterEventAdmin)
admin.site.register(LabResultEvent, LabResultAdmin)
admin.site.register(PrescriptionEvent, PrescriptionAdmin)
admin.site.register(AllergyEvent, AllergyEventAdmin)
admin.site.register(DiagnosticsEventRule)
admin.site.register(Sender,SenderAdmin)
