from django.contrib import admin

from ESP.conf.models import NativeCode


class NativeCodeAdmin(admin.ModelAdmin):
    list_display = ['native_code', 'native_name', 'loinc', ]
    raw_id_fields = ['loinc']
    save_on_top = True


admin.site.register(NativeCode, NativeCodeAdmin)