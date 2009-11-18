


from django.contrib import admin
#from django.utils.translation import ugettext_lazy as _

from ESP.nodis.models import Case
from ESP.nodis.models import CaseStatusHistory
from ESP.nodis.models import ValidatorResult
from ESP.nodis.models import ReferenceCase



class CaseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'condition', 'patient', 'date']
    

class CaseStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['case', 'timestamp', 'new_status', 'changed_by']
    raw_id_fields = ['case']
    

class ValidatorResultAdmin(admin.ModelAdmin):
    list_display = ['pk', 'run', 'date', 'condition', 'patient', 'disposition', 'nodis_case']
    list_filter = ['disposition', 'run', ]
    ordering = ['ref_case__date', 'ref_case__condition', 'ref_case__patient']
    raw_id_fields = ['events', 'cases', 'lab_results', 'encounters', 'prescriptions']


class ReferenceCaseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'list', 'condition', 'date', 'patient', 'ignore']
    list_filter = ['ignore', 'list', 'condition']
    ordering = ['date', 'condition', 'patient']
    search_fields = ['patient__last_name', 'patient__first_name']
    raw_id_fields = ['patient']
    
    def ignore_cases(self, request, queryset):
        rows_updated = queryset.update(ignore=True)
        if rows_updated == 1:
            msg_part = '1 reference case was'
        else:
            msg_part = '%s references cases were' % rows_updated
        self.message_user(request, "%s ignored." % msg_part)
    ignore_cases.short_description = 'Ignore selected cases'
        
    def unignore_cases(self, request, queryset):
        rows_updated = queryset.update(ignore=False)
        if rows_updated == 1:
            msg_part = '1 reference case was'
        else:
            msg_part = '%s references cases were' % rows_updated
        self.message_user(request, "%s un-ignored." % msg_part)
    unignore_cases.short_description = 'Un-ignore selected cases'
    
    actions = [ignore_cases, unignore_cases]



admin.site.register(Case, CaseAdmin)
admin.site.register(CaseStatusHistory, CaseStatusHistoryAdmin)
admin.site.register(ValidatorResult, ValidatorResultAdmin)
admin.site.register(ReferenceCase, ReferenceCaseAdmin)