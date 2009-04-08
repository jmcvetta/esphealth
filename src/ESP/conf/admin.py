from django.contrib import admin

from ESP.conf.models import Format
from ESP.conf.models import Dest
from ESP.conf.models import NativeToLoincMap


class FormatOptions(admin.ModelAdmin):
    ordering = ('formatVerDate', 'formatName')

class DestOptions(admin.ModelAdmin):
    ordering = ('destVerDate', 'destName')

class NativeToLoincMapAdmin(admin.ModelAdmin):
    list_display = ['native_code', 'native_name', 'loinc', ]
    save_on_top = True


admin.site.register(Format, FormatOptions)
admin.site.register(Dest, DestOptions)
admin.site.register(NativeToLoincMap, NativeToLoincMapAdmin)
