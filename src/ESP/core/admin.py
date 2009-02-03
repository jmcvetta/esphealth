'''
                        Core Data Model Admin Interface
                                      for
                                  ESP Health
'''

from ESP.core import models
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class CaseAdmin(admin.ModelAdmin):
    #list_filter = ('caseWorkflow','caseQueryID','caseMsgFormat','caseProvider')
    #ordering = ('caseLastUpDate', 'casecreatedDate')
    list_display = ('patient', 'provider',)

class ProvenanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'source', 'user',)

class LoincAdmin(admin.ModelAdmin):
    list_display = ('code',)


admin.site.register(models.Case, CaseAdmin)
admin.site.register(models.Provenance, ProvenanceAdmin)
admin.site.register(models.Loinc, LoincAdmin)
