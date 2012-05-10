#!/usr/bin/python
'''
Rolls through immunization records, setting isvaccine boolean flag based on regex in conf_vaccineregex
correctly converted to float fields. 
'''

import re

from django.core.management.base import BaseCommand
from ESP.emr.models import Immunization
from ESP.conf.models import VaccineRegEx
    
class Command(BaseCommand):
    
    help = 'Ensure float fields in all LabResult and Encounter objects are correctly converted \n'
    help += 'from their corresponding string fields.'
    
    def handle(self, *fixture_labels, **options):
        self.updt_immu()
        
    vx_regex_qs = VaccineRegEx.objects.distinct('Vx_RegEx')
    #probably a slicker way to concat the regexs, but this works.  
    for index, row in enumerate(vx_regex_qs):
        if (index==0):
            cat_vx_regex = row.Vx_RegEx
        else:
            cat_vx_regex += '|' + row.Vx_RegEx

    def updt_immu(self):
        Immunization.objects.update(isvaccine=None)
        Immunization.objects.filter(name__iregex=self.cat_vx_regex).update(isvaccine=True)
        Immunization.objects.filter(isvaccine__isnull=True).update(isvaccine=False)
        #NB: regex filter on queryset uses native db regex syntax, not python regex syntax.
        
    
