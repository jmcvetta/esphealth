from django.contrib import admin

from ESP.conf.models import CodeMap
from ESP.conf.models import IgnoredCode


class CodeMapAdmin(admin.ModelAdmin):
    list_display = ['id', 'native_code', 'native_name', 'heuristic', 'threshold', 'output_code', 'notes']
    list_filter = ['heuristic']
    search_fields = ['native_code', 'native_name', 'output_code']
    save_on_top = True
    ordering = ['output_code', 'native_code', 'heuristic']

class IgnoredCodeAdmin(admin.ModelAdmin):
    search_fields = ['native_code']
    ordering = ['native_code']


admin.site.register(CodeMap, CodeMapAdmin)
admin.site.register(IgnoredCode, IgnoredCodeAdmin)