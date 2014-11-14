'''
                              ESP Health Project
                            Quality Metrics module
                  generate population results from hqmf document logic

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import ntpath
from datetime import datetime
from optparse import make_option
from ESP.qmetric.base import ResultGenerator
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-d', '--docname', dest='docname', help='HQMF document name'),
        make_option('-s', '--startdt', dest='pstart', help='Period start date as YYYY-mm-dd'),
        make_option('-e', '--enddt', dest='pend', help='Period end data as YYYY-mm-dd'),
        )
    
    help = 'generate population events from hqmf document logic'

    
    def handle(self, *fixture_labels, **options):
        docname = options['docname']
        assert docname 
        pstart = datetime.strptime(options['pstart'],'%Y-%m-%d')
        assert pstart 
        pend = datetime.strptime(options['pend'],'%Y-%m-%d')
        assert pend
        #TODO: manage exceptions raised by assert if no values for required options 
        cmsname=ntpath.splitext(docname)[0]
        rg = ResultGenerator(pstart,pend,cmsname)
        ncounts, dcounts = rg.genpop()
        print str(dcounts) + ' denominator records loaded, and ' + str(ncounts) + ' numerator records loaded'
        return