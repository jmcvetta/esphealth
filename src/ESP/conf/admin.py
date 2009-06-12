from django.contrib import admin

from ESP.conf import models


class FormatOptions(admin.ModelAdmin):
    ordering = ('formatVerDate', 'formatName')

class DestOptions(admin.ModelAdmin):
    ordering = ('destVerDate', 'destName')

class LoincAdmin(admin.ModelAdmin):
    ordering = ('loinc_num',)
    search_fields = ('loinc_num', 'long_common_name', 'shortname')

class NativeToLoincMapAdmin(admin.ModelAdmin):
    list_display = ['native_code', 'native_name', 'loinc', ]
    raw_id_fields = ['loinc']
    save_on_top = True

class SourceSystemAdmin(admin.ModelAdmin):
    list_display = ['name', 'software']


admin.site.register(models.Format, FormatOptions)
admin.site.register(models.Dest, DestOptions)
admin.site.register(models.NativeCode, NativeToLoincMapAdmin)
admin.site.register(models.SourceSystem, SourceSystemAdmin)
admin.site.register(models.Vaccine)
admin.site.register(models.ImmunizationManufacturer)
admin.site.register(models.Loinc, LoincAdmin)
