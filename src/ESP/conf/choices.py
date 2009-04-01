'''
                       Configuration Data Model Choices
                                      for
                                  ESP Health

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

#
# Are these codes still used?  If so, where?
#
RECODEFILE_TYPES = (
    (u'Encounters',u'Daily encounter records - ICD9, demographics...'),
    (u'Labs',u'Lab Orders and Lab Results - LOINC, CPT'),
    (u'Rx', u'Prescription data - NDC'),
    (u'PCP', u'Primary Care Physicians'),
    )

FORMAT_TYPES = (
    ('Text','Plain text representation'),
    ('XML','eXtended Markup Language format'),
    ('HL7', 'Health Level 7 markup'),
    ('MADPHSimple', 'MADPH Simple markup (pipe delim simplifiedhl7)'),
)

DEST_TYPES = (
    ('TextFile','Text file on the filesystem - path'),
    ('PHIN-MS','PHINMS server URL'),
    ('SOAP', 'SOAP service URL'),
    ('XMLRPC', 'XML-RPC Server URL'),
)

WORKFLOW_STATES = [
    ('AR','AWAITING REVIEW'),
    ('UR','UNDER REVIEW'),
    ('RM', 'REVIEW By MD'),
    ('FP','FALSE POSITIVE - DO NOT PROCESS'),
    ('Q','CONFIRMED CASE, TRANSMIT TO HEALTH DEPARTMENT'), 
    ('S','TRANSMITTED TO HEALTH DEPARTMENT')
    ]
