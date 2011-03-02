


from django.contrib import admin
#from django.utils.translation import ugettext_lazy as _

from ESP.static.models import Icd9


class Icd9Admin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']

admin.site.register(Icd9, Icd9Admin)