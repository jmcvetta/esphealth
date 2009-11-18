


from django.contrib import admin
#from django.utils.translation import ugettext_lazy as _

from ESP.nodis.models import Case
from ESP.nodis.models import CaseStatusHistory
from ESP.nodis.models import ValidatorResult



class CaseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'condition', 'patient', 'date']
    

class CaseStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['case', 'timestamp', 'new_status', 'changed_by']
    raw_id_fields = ['case']
    

class ValidatorResultAdmin(admin.ModelAdmin):
    list_display = ['pk', 'run', 'date', 'condition', 'patient', 'disposition', 'nodis_case']
    list_filter = ['disposition', 'run', ]
    ordering = ['ref_case__date', 'ref_case__condition', 'ref_case__patient']



admin.site.register(Case, CaseAdmin)
admin.site.register(CaseStatusHistory, CaseStatusHistoryAdmin)
admin.site.register(ValidatorResult, ValidatorResultAdmin)