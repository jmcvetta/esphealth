'''
                                  ESP Health
                         Notifiable Diseases Framework
MDPH XML Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


INSTITUTION_NAME = 'HVMA'
INSTITUTION_CLIA = '22D0666230'
VERSION = '2.3.1'



import time
from lxml import etree

from ESP.nodis.models import Case


#
# This is used in various places, and needs to be same everywhere
#
ISO_DATE = time.strftime('%Y%m%d%H%M%S',time.localtime())


def compose():
    #
    # Batch root container
    #
    namespace = 'urn:hl7-org:v2xml'
    nsmap = {None: namespace}
    batch = etree.Element('BATCH', nsmap=nsmap)
    #
    # Batch Headers
    #
    fhs = etree.SubElement(batch, 'FHS')
    etree.SubElement(fhs, 'FHS.1').text = '|'
    etree.SubElement(fhs, 'FHS.2').text = '^\&amp;'
    etree.SubElement(fhs, 'FHS.3').text = 'ESP0.001'
    etree.SubElement(fhs, 'FHS.4').text = 'Test'
    etree.SubElement(etree.SubElement(fhs, 'FHS.7'), 'TS.1').text = ISO_DATE
    messagebatch = etree.SubElement(batch, 'MESSAGEBATCH')
    bhs = etree.SubElement(messagebatch, 'BHS')
    etree.SubElement(bhs, 'BHS.1').text = '|'
    etree.SubElement(bhs, 'BHS.2').text = '^\&amp;'
    etree.SubElement(bhs, 'BHS.3').text = 'ESP0.001'
    etree.SubElement(bhs, 'BHS.4').text = 'Test'
    etree.SubElement(etree.SubElement(bhs, 'BHS.7'), 'TS.1').text = ISO_DATE
    messages = etree.SubElement(messagebatch, 'MESSAGES')
    #
    # Message List
    #
    #oru_r01 = etree.Element('ORU_R01')
    #
    #
    #
    #messages.text = etree.CDATA(etree.tostring(oru_r01, pretty_print=True))
    return batch


def encode_case(case):
    '''
    @param case: Case to be encoded in HL7v3
    @type case: Case
    '''
    oru = etree.Element('ORU_R01')
    #
    # Message Header
    #
    msh = etree.SubElement(oru, 'MSH')
    etree.SubElement(msh, 'MSH.1').text = '|'
    etree.SubElement(msh, 'MSH.2').text = '^~\&'
    msh4 = etree.SubElement(msh, 'MSH.4')
    etree.SubElement(msh4, 'HD.1').text = INSTITUTION_NAME
    etree.SubElement(msh4, 'HD.2').text = INSTITUTION_CLIA
    etree.SubElement(msh4, 'HD.3').text = 'CLIA'
    etree.SubElement(etree.SubElement(msh, 'MSH.5'), 'HD.1').text = 'MDPH-ELR'
    etree.SubElement(etree.SubElement(msh, 'MSH.6'), 'HD.1').text = 'MDPH'
    etree.SubElement(etree.SubElement(msh, 'MSH.7'), 'TS.1').text = ISO_DATE
    msh9 = etree.SubElement(msh, 'MSH.9')
    etree.SubElement(msh9, 'MSG.1').text = 'ORU'
    etree.SubElement(msh9, 'MSG.2').text = 'R01'
    etree.SubElement(msh, 'MSH.10').text = 'MDPH%s' % ISO_DATE
    # MSH.11, the 'processingFlag', was passed as an argument in the old code.
    # While the only value that code ever passed for it was 'T', nevertheless
    # Ross et al must have thought the value would sometimes be other than 'T'.
    etree.SubElement(etree.SubElement(msh, 'MSH.11'), 'PT.1').text = 'T'
    etree.SubElement(etree.SubElement(msh, 'MSH.12'), 'VID.1').text = VERSION
    #
    #
    #
    etree.SubElement(oru, 'ORU_R01.PIDPD1NK1NTEPV1PV2ORCOBRNTEOBXNTECTI_SUPPGRP')
    return oru
    




#batch = compose()
#print(etree.tostring(batch, pretty_print=True))

c = Case.objects.all()[0]
print etree.tostring(encode_case(c), pretty_print=True)