'''
                              ESP Health Project
                          Heuristic Events Framework
                         Admin Interface Configuration
'''

from django.contrib import admin

from ESP.hef.models import NativeToLoincMap


class NativeToLoincMapAdmin(admin.ModelAdmin):
    list_display = ['native_code', 'native_name', 'loinc', ]
    save_on_top = True


admin.site.register(NativeToLoincMap, NativeToLoincMapAdmin)
