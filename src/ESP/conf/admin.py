from django.contrib import admin

from ESP.conf.models import NativeCode
from ESP.conf.models import IgnoredCode


class NativeCodeAdmin(admin.ModelAdmin):
    list_display = ['native_code', 'native_name', 'loinc', ]
    search_fields = ['native_code', 'native_name']
    raw_id_fields = ['loinc']
    save_on_top = True
    ordering = ['native_code']

class IgnoredCodeAdmin(admin.ModelAdmin):
    search_fields = ['native_code']
    ordering = ['native_code']


admin.site.register(NativeCode, NativeCodeAdmin)
admin.site.register(IgnoredCode, IgnoredCodeAdmin)