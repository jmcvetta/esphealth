from django.contrib import admin
#from django.utils.translation import ugettext_lazy as _

from ESP.static.models import Icd9, Allergen, Vaccine
from ESP.static.models import DrugSynonym, ImmunizationManufacturer


class Icd9Admin(admin.ModelAdmin):
    list_display = ['code', 'name']
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

#TODO Ndc and Loinc are not added here 
    
admin.site.register(Icd9, Icd9Admin)
admin.site.register(Allergen, AllergenAdmin)
admin.site.register(DrugSynonym, DrugSynonymAdmin)
admin.site.register(ImmunizationManufacturer, ImmunizationManufacturerAdmin)
admin.site.register(Vaccine, VaccineAdmin)
