from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ESP.esp.models import *
from ESP.esp import models



class CaseAdmin(admin.ModelAdmin):
    list_filter = ('caseWorkflow',)
    #ordering = ('updated_timestamp', 'created_timestamp')
    #list_display = ['provider', 'workflow_state', 'updated_timestamp', 'notes']
    ordering = ('caseLastUpDate', 'casecreatedDate')
    list_display = ['caseProvider', 'caseWorkflow', 'caseLastUpDate',]

class EncOptions(admin.ModelAdmin):
    list_display = ('EncPatient', 'EncEncounter_Date','EncMedical_Record_Number')
    search_fields = ['EncPatient', 'EncMedical_Record_Number']

class Hl7OutputFileOptions(admin.ModelAdmin):
    list_display = ('filename', 'case','demogMRN')
    search_fields =('filename', 'case')

class ProviderOptions(admin.ModelAdmin):
    list_display = ('provLast_Name', 'provFirst_Name','provPrimary_Dept')
    search_fields = ['provLast_Name']

class ConditionDrugNameOptions(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiDrugName','CondiDrugRoute')
    search_fields = ['CondiDrugName']

class TestCaseOptions(admin.ModelAdmin):
    list_filter = ('caseWorkflow','caseQueryID','caseMsgFormat','caseProvider')
    ordering = ('caseLastUpDate', 'casecreatedDate')
    list_display = ('caseProvider','caseWorkflow','caseComments','caseLastUpDate','caseQueryID','caseMsgFormat')

class ConditionLOINCOptions(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiLOINC')
    search_fields = ['CondiLOINC']

class ConditionNdcOptions(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiNdc')
    search_fields = ['CondiNdc']

class CPTLOINCMapOptions(admin.ModelAdmin):
    list_display = ('CPT', 'CPTCompt')
    search_fields = ['CPT']

class ConditionIcd9Options(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiICD9')
    search_fields = ['CondiICD9']

class DataFileOptions(admin.ModelAdmin):
    list_display = ('filename', 'numrecords', 'datedownloaded')
    search_fields = ['filename']

class DemogOptions(admin.ModelAdmin):
    list_display = ('DemogFirst_Name', 'DemogLast_Name', 'DemogMedical_Record_Number','DemogDate_of_Birth')
    search_fields = ['DemogLast_Name']

class CaseWorkflowOptions(admin.ModelAdmin):
    list_filter = ('workflowState','workflowChangedBy',)
    list_display = ('workflowDate','workflowState','workflowChangedBy','workflowComment',)
    search_fields = ['workflowComment',]
    ordering = ('workflowDate',)

class RuleAdmin(admin.ModelAdmin):
    list_display = ('ruleName',)

class LoincAdmin(admin.ModelAdmin):
    list_display = ['loinc_num', 'name']
    search_fields = ['loinc_num', 'long_common_name', 'shortname']
    save_on_top = True

class HeuristicEventAdmin(admin.ModelAdmin):
    list_display = ['heuristic_name', 'patient', 'date']
    list_filter = ['heuristic_name']

class Hl7InputFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'timestamp', 'status',]
    list_filter = ['status',]


admin.site.register(TestCase, CaseAdmin)
admin.site.register(SocialHistory)
admin.site.register(Enc, EncOptions)
admin.site.register(Allergy)
# admin.site.register(Hl7OutputFile, Hl7OutputFileOptions)
admin.site.register(Rx)
admin.site.register(Provider, ProviderOptions)
admin.site.register(Lx)
admin.site.register(ConditionDrugName, ConditionDrugNameOptions)
admin.site.register(Problem)
admin.site.register(TestCase, TestCaseOptions)
admin.site.register(Lxo)
admin.site.register(Immunization)
admin.site.register(DataFile, DataFileOptions)
admin.site.register(Icd9Fact)
admin.site.register(Demog, DemogOptions)
admin.site.register(CaseWorkflow, CaseWorkflowOptions)
admin.site.register(Rule, RuleAdmin)
admin.site.register(models.Loinc, LoincAdmin)
admin.site.register(models.HeuristicEvent, HeuristicEventAdmin)
admin.site.register(Hl7InputFile, Hl7InputFileAdmin)

admin.site.register(Vaccine)
admin.site.register(ImmunizationManufacturer)
