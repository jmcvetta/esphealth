


from django.contrib import admin
#from django.utils.translation import ugettext_lazy as _

from ESP.nodis.models import Case
from ESP.nodis.models import CaseStatusHistory



class CaseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'condition', 'patient', 'date']
    

class CaseStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['case', 'timestamp', 'new_status', 'changed_by']
    raw_id_fields = ['case']



admin.site.register(Case, CaseAdmin)
admin.site.register(CaseStatusHistory, CaseStatusHistoryAdmin)