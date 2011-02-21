#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
               Load default abstract lab tests, heuristics, etc


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory

@license: LGPL
'''

from django.core.management.base import BaseCommand
from optparse import make_option





#===============================================================================
#
#--- ~~~ Main ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
class Command(BaseCommand):
    
    help = 'Load default abstract lab tests, heuristics, etc'
    
    def handle(self, *args, **options):
        print 'Loading defaults...'
        from esp.hef import defaults
        print 'Defaults loaded.'