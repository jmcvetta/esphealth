#!/usr/bin/python
'''
Checks static_dx_code for "added by load epic" records, and add them to exclusion list.
'''

import re

from django.core.management.base import BaseCommand
from ESP.vaers.models import ExcludedDx_Code
from ESP.static.models import Dx_code
    
class Command(BaseCommand):
    '''
    This command is used to exclude from the VAERS heuristic any dx codes that are added by load_epic
    '''
    
    def handle(self, *fixture_labels, **options):
        self.updt_exclud()
        
    def updt_exclud(self):
        Ex_qs = Dx_code.objects.filter(name__icontains='load_epic')
        for ex_code in Ex_qs:
            ex_row, cre8td =ExcludedDx_Code.objects.all().get_or_create(code=ex_code.code, type = ex_code.type)
            if cre8td:
                ex_row.descripton=ex_code.name
                ex_row.save()
        
    
