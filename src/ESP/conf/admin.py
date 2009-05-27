from django.contrib import admin

from ESP.conf.models import Format
from ESP.conf.models import Dest
from ESP.conf.models import NativeCode
from ESP.conf.models import SourceSystem


class FormatOptions(admin.ModelAdmin):
    ordering = ('formatVerDate', 'formatName')

class DestOptions(admin.ModelAdmin):
    ordering = ('destVerDate', 'destName')

class NativeToLoincMapAdmin(admin.ModelAdmin):
    list_display = ['native_code', 'native_name', 'loinc', ]
    save_on_top = True

class SourceSystemAdmin(admin.ModelAdmin):
    list_display = ['name', 'software']


admin.site.register(Format, FormatOptions)
admin.site.register(Dest, DestOptions)
admin.site.register(NativeCode, NativeToLoincMapAdmin)
admin.site.register(SourceSystem, SourceSystemAdmin)
