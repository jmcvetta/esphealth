'''
                              ESP Health Project
                            Quality Metrics module
                           Update ValueSets from VSA

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import urllib, urllib2, xmltodict
from django.core.management.base import BaseCommand
from optparse import make_option
from ESP.qmetric.models import Element, Elementmapping
from django.db import transaction

url='https://vsac.nlm.nih.gov/vsac/ws'

class vsac_loader(object):
    
    def __init__(self,codeline, elem):
        assert codeline, elem
        self.codeline=codeline
        self.elem=elem
    
    @transaction.autocommit
    def load(self):
        mapping = Elementmapping(element=self.elem,
                                 code=self.codeline['@code'],
                                 description=self.codeline['@displayName'],
                                 codesystem=self.codeline['@codeSystemName'])
        mapping.save()
        return

        
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--username', dest='username', help='UMLS username'),
        make_option('-p', '--password', dest='password', help='UMLS password'),
        make_option('-n', '--name', dest='cmsname', help='CMS name'))
    
    help = 'Fetch VSA data'

    
    def handle(self, *fixture_labels, **options):
        umlsAccount = {'username' : options['username'],
                       'password' : options['password']} 
        creds = urllib.urlencode(umlsAccount)
        url1 = url + '/Ticket'
        vsa1 = urllib2.Request(url1,creds)
        tgt = urllib2.urlopen(vsa1)
        tgtvalue = tgt.read()
        url2 = url1 + '/' + tgtvalue
        treq = urllib.urlencode({'service': 'http://umlsks.nlm.nih.gov'})
        for elem in Element.objects.filter(cmsname=options['cmsname'], source='VSAC'):
            print 'now loading codes for element: ' + elem.ename
            count=0
            vsa2 = urllib2.Request(url2,treq)
            ticket = urllib2.urlopen(vsa2)
            ticketval = ticket.read()
            url3 = url + '/RetrieveValueSet?id=' + elem.oid + '&ticket=' + ticketval
            download = urllib2.urlopen(url3)
            getxml = download.read()
            xmldict = xmltodict.parse(getxml)
            for codeline in xmldict['ns0:RetrieveValueSetResponse']['ns0:ValueSet']['ns0:ConceptList']['ns0:Concept']:
                codestore = vsac_loader(codeline,elem)
                try:
                    codestore.load()
                    count+=1
                    if not (count % 25): print str(count) + ' code records loaded'
                except:
                    raise
            print str(count) + ' code records loaded'
        return 
