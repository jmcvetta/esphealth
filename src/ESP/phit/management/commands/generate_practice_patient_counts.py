#!/usr/bin/env python
'''
                                  ESP Health
Public Health Intervention Tracker
Practice Patient Count Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory

@license: LGPL
'''


from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.phit.models import PracticePatients
from ESP.utils import log
from ESP.utils import log_query


#===============================================================================
#
#--- ~~~ Main ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
class Command(BaseCommand):
    
    help = 'Generate counts of practice patients per month'
    
    def handle(self, *args, **options):
        PracticePatients.regenerate()