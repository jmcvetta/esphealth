#!/usr/bin/python
'''
Checks static_icd9 for "added by load epic" records, and add them to exclusion list.
'''

import re

from django.core.management.base import BaseCommand
from ESP.vaers.models import ExcludedICD9Code
from ESP.static.models import Icd9
    
class Command(BaseCommand):
    '''
    This command is used to exclude from the VAERS heuristic any ICD9 codes that are added by load_epic
    '''
    
    def handle(self, *fixture_labels, **options):
        self.updt_exclud()
        
    def updt_exclud(self):
        Ex_qs = Icd9.objects.filter(name__icontains='load_epic')
        for ex_code in Ex_qs:
            ex_row, cre8td =ExcludedICD9Code.objects.all().get_or_create(code=ex_code.code)
            if cre8td:
                ex_row.descripton=ex_code.name
                ex_row.save()
        
    
