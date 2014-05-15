from django.contrib import admin
#from django.utils.translation import ugettext_lazy as _

from ESP.static.models import Dx_code, Allergen, Vaccine
from ESP.static.models import DrugSynonym, ImmunizationManufacturer
from ESP.static.models import ILI_encounter_type
from ESP.static.models import Loinc
from ESP.static.models import Ndc
from ESP.static.models import Site
from ESP.static.models import Sitegroup
from ESP.static.models import hl7_vocab


class Dx_codeAdmin(admin.ModelAdmin):
    list_display = ['code', 'type', 'name']
    search_fields = ['code', 'name']

class AllergenAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    
class DrugSynonymAdmin(admin.ModelAdmin):
    list_display = ['generic_name', 'other_name']
    search_fields = ['generic_name', 'other_name']

class ImmunizationManufacturerAdmin(admin.ModelAdmin):
    list_display = ['code', 'full_name']
    search_fields = ['code', 'full_name']
    
class VaccineAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    
class ILI_encounter_typeAdmin(admin.ModelAdmin):
    ordering = ['raw_encounter_type']
    search_fields = ['raw_encounter_type']

class LoincAdmin(admin.ModelAdmin):
    ordering = ['loinc_num']
    search_fields = ['loinc_num']

class NdcAdmin(admin.ModelAdmin):
    ordering = ['label_code']
    search_fields = ['label_code']

class SiteAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class SitegroupAdmin(admin.ModelAdmin):
    ordering = ['group']
    search_fields = ['group']

class hl7_vocabAdmin(admin.ModelAdmin):
    ordering = ['value']
    search_fields = ['value']


admin.site.register(Dx_code, Dx_codeAdmin)
admin.site.register(Allergen, AllergenAdmin)
admin.site.register(DrugSynonym, DrugSynonymAdmin)
admin.site.register(ImmunizationManufacturer, ImmunizationManufacturerAdmin)
admin.site.register(Loinc, LoincAdmin)
admin.site.register(Ndc, NdcAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Vaccine, VaccineAdmin)
admin.site.register(Sitegroup, SitegroupAdmin)
admin.site.register(hl7_vocab, hl7_vocabAdmin)
admin.site.register(ILI_encounter_type, ILI_encounter_typeAdmin)

