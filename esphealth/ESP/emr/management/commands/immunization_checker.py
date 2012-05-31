#!/usr/bin/python
'''
Rolls through immunization records, setting isvaccine to false based on current contents for ImmuExclusion. 
'''

import re

from django.core.management.base import BaseCommand
from ESP.emr.models import Immunization
from ESP.conf.models import ImmuExclusion
    
class Command(BaseCommand):
    '''
    This command is used to flag immunizaiton data for non-vaccines.
    If EMR_IMMUNIZATION includes non vaccine immunotherapies, these non-vaccines can be listed in conf_immuexclusion.
    This command must be re-run each time you update conf_immuexclusion.
    If the EMR_IMMUNIZATION table is large, this command will take some time to complete updates.
    It requires site specific data in the conf_immuexclusion table
    '''
    help = 'Flag immunization data to identify vaccines from larger set of immunotherapies. \n'
    help += 'Requires site specific data in the conf_immuexclusion data model.'
    
    def handle(self, *fixture_labels, **options):
        self.updt_immu()
        
    ImmuEx_qs = ImmuExclusion.objects.distinct('non_immu_name')


    def updt_immu(self):
        Immunization.objects.update(isvaccine=True)
        Immunization.objects.filter(name__in=self.ImmuEx_qs.values('non_immu_name')).update(isvaccine=False)
        
    
