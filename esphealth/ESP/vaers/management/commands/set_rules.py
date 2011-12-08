#!/usr/bin/env python 
#-*- coding: utf-8 -*-
from optparse import OptionParser, make_option, Values

from django.core.management.base import BaseCommand

from vaers.rules import define_active_rules, map_lab_tests



class Command(BaseCommand):
    #
    # Parse command line options
    #
    help = 'Gets all mapped lab tests and Icd9 codes to be identified and used by the VAERS engine'
    
    def handle(self, *fixture_labels, **options):
        define_active_rules()
        map_lab_tests()


        
