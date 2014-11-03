'''
                              ESP Health Project
                            Quality Metrics module
                           load elements from hqmf

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import os
from optparse import make_option
from datetime import datetime
from ESP.qmetric.base import HQMF_Parser
from ESP.qmetric.models import Element
from django.core.management.base import BaseCommand
from django.db import transaction
from ESP.utils import log

#TODO: this should be a configurable setting
hqmf_datadir = '/home/bobz/workspace/hqmf'

class hqmf_loader(object):
    
    def __init__(self,filepath):
        assert filepath
        self.filepath=filepath
    
    @transaction.autocommit
    def load(self):
        log.info('Loading hqmf file "%s" with %s' % (self.filepath, self.__class__))
        cur_row = 0 # Row counter
        hqmf = HQMF_Parser(self.filepath)
        hqmfdict = hqmf.hqmfdict 
        #mostly this won't work from here
        element_titles = ['Data criteria (QDM Data Elements)','Supplemental Data Elements']
        for comp in hqmfdict['QualityMeasureDocument']['component']:
            if any(comp['section']['title'] in s for s in element_titles):
                sectionTitle=comp['section']['title']
                for item in comp['section']['text']['list']['item']:
                    element = Element(cmsname = os.path.basename(os.path.splitext(self.filepath)[0]),
                                      ename = item['content'].replace('"',''),
                                      oid = item['#text'][item['#text'].find('(2')+1:item['#text'].find(')',item['#text'].find('(2'))],
                                      use = sectionTitle[0:sectionTitle.find('(')-1],
                                      created_timestamp = datetime.now())
                    try:
                        element.save()
                    except:
                        raise #TODO: just for testing
                    cur_row += 1
        log.info('Loaded %s records.' % (cur_row))
        return (cur_row)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-r', '--reload', dest='reload', action='store_true', default=False, help='UMLS username'),
        )
    
    help = 'load element data from hqmf'

    
    def handle(self, *fixture_labels, **options):
        dir_contents = os.listdir(hqmf_datadir)
        for item in dir_contents:
            filepath = os.path.join(hqmf_datadir, item)
            l = hqmf_loader(filepath)
            valid = l.load()
            print valid
        
