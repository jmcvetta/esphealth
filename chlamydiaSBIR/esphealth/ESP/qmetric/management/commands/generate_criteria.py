'''
                              ESP Health Project
                            Quality Metrics module
                  generate criteria events from hqmf document logic

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import os
from optparse import make_option
from ESP.qmetric.base import DSTU2Qualifier, HQMF_Parser
from django.core.management.base import BaseCommand


#TODO: this should be a configurable setting
hqmf_datadir = '/home/bobz/workspace/hqmf'

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-r', '--regen', dest='regen', action='store_true', default=False, help='UMLS username'),
        make_option('-d', '--docname', dest='docname', help='HQMF document name'),
        )
    
    help = 'generate population events from hqmf document logic'
    
    def handle(self, *fixture_labels, **options):
        docname = options['docname']
        assert docname
        filepath = os.path.join(hqmf_datadir, docname)
        if not os.path.exists(filepath):
            print 'Could not find HQMF file %s' % docname
            #TODO: raise an exception here
            return
        hp = HQMF_Parser(filepath)
        if hp.gettype() in ['POQM_HD000001','POQM_HD000001UV02']:
            popqual = DSTU2Qualifier(hp)
            #I actually have the nomenclature wrong here - should not be DSTU2, and shouldn't include both types.
            counts=popqual.load_criteria()
            print str(counts) + " criteria records loaded"
        #Note: the two types above are the only two HQMF definitions by HL7 as of late 2014.   
        else:
            #TODO: raise exception
            return
        return