'''
                              ESP Health Project
                          Heuristic Events Framework
                         Admin Interface Configuration
'''

from django.contrib import admin

from ESP.hef.models import HeuristicEvent


class HeuristicEventAdmin(admin.ModelAdmin):
    list_display = ['heuristic_name', 'date', 'patient', 'content_object']


admin.site.register(HeuristicEvent, HeuristicEventAdmin)
