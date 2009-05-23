
from ssmap.models import event
from ssmap.models import geoplace
from ssmap.models import rule
from ssmap.models import enc

from django.contrib import admin

admin.site.register(event)
admin.site.register(geoplace)
admin.site.register(rule)
admin.site.register(enc)

