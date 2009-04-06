from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ESP.conf.models import Format
from ESP.conf.models import Dest
from ESP.conf.models import ExtToLoincMap


class FormatOptions(admin.ModelAdmin):
    ordering = ('formatVerDate', 'formatName')

class DestOptions(admin.ModelAdmin):
    ordering = ('destVerDate', 'destName')

class ExtToLoincMapAdmin(admin.ModelAdmin):
    list_display = ['ext_code', 'ext_name', 'loinc', ]
    save_on_top = True


admin.site.register(Format, FormatOptions)
admin.site.register(Dest, DestOptions)
admin.site.register(ExtToLoincMap, ExtToLoincMapAdmin)
