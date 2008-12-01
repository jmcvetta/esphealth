

#[Sat Sep 20 09:35:05 rossl@rosst61:~/py/informatics/django/ESP/esp ] $ python makeNewadmin.py models.py
from esp.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class CaseOptions(admin.ModelAdmin):
    list_filter = ('caseWorkflow','caseQueryID','caseMsgFormat','caseProvider')
    ordering = ('caseLastUpDate', 'casecreatedDate')
    list_display = ('caseProvider','caseWorkflow','caseComments','caseLastUpDate','caseQueryID','caseMsgFormat')

class EncOptions(admin.ModelAdmin):
    list_display = ('EncPatient', 'EncEncounter_Date','EncMedical_Record_Number')
    search_fieldsets = ('EncMedical_Record_Number')

class HL7FileOptions(admin.ModelAdmin):
    list_display = ('filename', 'case','demogMRN')
    search_fieldsets =('filename', 'case')

class ProviderOptions(admin.ModelAdmin):
    list_display = ('provLast_Name', 'provFirst_Name','provPrimary_Dept')
    search_fieldsets = ('provLast_Name')

class ConditionDrugNameOptions(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiDrugName','CondiDrugRoute')
    search_fieldsets = ('CondiDrugName')

class FormatOptions(admin.ModelAdmin):
    ordering = ('formatVerDate', 'formatName')

class DestOptions(admin.ModelAdmin):
    ordering = ('destVerDate', 'destName')

class TestCaseOptions(admin.ModelAdmin):
    list_filter = ('caseWorkflow','caseQueryID','caseMsgFormat','caseProvider')
    ordering = ('caseLastUpDate', 'casecreatedDate')
    list_display = ('caseProvider','caseWorkflow','caseComments','caseLastUpDate','caseQueryID','caseMsgFormat')

class ConditionLOINCOptions(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiLOINC')
    search_fieldsets = ('CondiLOINC')

class ConditionNdcOptions(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiNdc')
    search_fieldsets = ('CondiNdc')

class CPTLOINCMapOptions(admin.ModelAdmin):
    list_display = ('CPT', 'CPTCompt')
    search_fieldsets = ('CPT')

class ConditionIcd9Options(admin.ModelAdmin):
    list_display = ('CondiRule', 'CondiICD9')
    search_fieldsets = ('CondiICD9')

class DataFileOptions(admin.ModelAdmin):
    list_display = ('filename', 'numrecords', 'datedownloaded')
    search_fieldsets =('filename')

class DemogOptions(admin.ModelAdmin):
    list_display = ('DemogFirst_Name', 'DemogLast_Name', 'DemogMedical_Record_Number','DemogDate_of_Birth')
    search_fieldsets = ('DemogLast_Name')

class CaseWorkflowOptions(admin.ModelAdmin):
    list_filter = ('workflowState','workflowChangedBy',)
    list_display = ('workflowDate','workflowState','workflowChangedBy','workflowComment',)
    search_fieldsets = ('workflowComment',)
    ordering = ('workflowDate',)

admin.site.register(Case, CaseOptions)
admin.site.register(SocialHistory)
admin.site.register(Enc, EncOptions)
admin.site.register(Allergies)
admin.site.register(HL7File, HL7FileOptions)
admin.site.register(Rx)
admin.site.register(Provider, ProviderOptions)
admin.site.register(Lx)
admin.site.register(ConditionDrugName, ConditionDrugNameOptions)
admin.site.register(Format, FormatOptions)
admin.site.register(Dest, DestOptions)
admin.site.register(Problems)
admin.site.register(TestCase, TestCaseOptions)
admin.site.register(ConditionLOINC, ConditionLOINCOptions)
admin.site.register(Lxo)
admin.site.register(ConditionNdc, ConditionNdcOptions)
admin.site.register(CPTLOINCMap, CPTLOINCMapOptions)
admin.site.register(ConditionIcd9, ConditionIcd9Options)
admin.site.register(Immunization)
admin.site.register(DataFile, DataFileOptions)
admin.site.register(icd9Fact)
admin.site.register(Demog, DemogOptions)
admin.site.register(CaseWorkflow, CaseWorkflowOptions)
admin.site.register(VAERSadditions)


