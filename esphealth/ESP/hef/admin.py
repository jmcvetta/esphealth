'''
                              ESP Health Project
                          Heuristic Events Framework
                         Admin Interface Configuration
'''

from django.contrib import admin


from ESP.hef.models import Event
from ESP.hef.models import Timespan


class EventAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'patient', 'date', 'content_object']


class TimespanAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'patient', 'start_date', 'end_date',]
    raw_id_fields = ['events']

admin.site.register(Event, EventAdmin)
admin.site.register(Timespan, TimespanAdmin)