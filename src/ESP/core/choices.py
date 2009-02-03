'''
Choices for Core Data Model
'''

LAB_RESULT_STATUS = (
    ('P', 'Positive'),
    ('N', 'Negative'),
    ('I', 'Indeterminate'),
    )

FORMAT_TYPES = (
    ('Text','Plain text representation'),
    ('XML','eXtended Markup Language format'),
    ('HL7', 'Health Level 7 markup'),
    ('MADPHSimple', 'MADPH Simple markup (pipe delim simplifiedhl7)'),
)

WORKFLOW_STATES = [('AR','AWAITING REVIEW'),('UR','UNDER REVIEW'),('RM', 'REVIEW By MD'),('FP','FALSE POSITIVE - DO NOT PROCESS'),('Q','CONFIRMED CASE, TRANSMIT TO HEALTH DEPARTMENT'), ('S','TRANSMITTED TO HEALTH DEPARTMENT')]

DEST_TYPES = (
    ('TextFile','Text file on the filesystem - path'),
    ('PHIN-MS','PHINMS server URL'),
    ('SOAP', 'SOAP service URL'),
    ('XMLRPC', 'XML-RPC Server URL'),
)

RECODEFILE_TYPES = (
    (u'Encounters',u'Daily encounter records - ICD9, demographics...'),
    (u'Labs',u'Lab Orders and Lab Results - LOINC, CPT'),
    (u'Rx', u'Prescription data - NDC'),
    (u'PCP', u'Primary Care Physicians'),
    )
