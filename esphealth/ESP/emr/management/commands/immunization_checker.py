#!/usr/bin/python
'''
Rolls through immunization records, setting isvaccine to false based on current contents for ImmuExclusion. 
'''

import re

from django.core.management.base import BaseCommand
from ESP.emr.models import Immunization
from ESP.conf.models import ImmuExclusion
    
class Command(BaseCommand):
    
    help = 'Flag immunization data to identify vaccines from larger set of immunotherapies. \n'
    help += 'Requires site specific data in the conf_vaccineRegEx data model.'
    
    def handle(self, *fixture_labels, **options):
        self.updt_immu()
        
    ImmuEx_qs = ImmuExclusion.objects.distinct('non_immu_name')


    def updt_immu(self):
        Immunization.objects.update(isvaccine=True)
        Immunization.objects.filter(name__in=self.ImmuEx_qs.values('non_immu_name')).update(isvaccine=False)
        
    
