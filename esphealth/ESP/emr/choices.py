'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                            Choices for Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


DATA_SOURCE = [
    ('hl7_file', 'HL7 File'),
    ('epic_file', 'EpicCare Extract File'),
    # Add more as we get new sources
    ]

LAB_ORDER_TYPES = [
    (1, 'Lab'),
    (2, 'Imaging'),
    (3, 'EKG'),
    (9, 'Procedure')
    ]

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
    ('Q','CONFIRMED CASE, QUEUE FOR SENDING'), 
    ('S','SENT TO HEALTH DEPARTMENT'),
    ('AS','AUTO-SENT TO HEALTH DEPARTMENT (NO REVIEW)')
    ]

OPERATORS = [
    ('iexact', 'Exact (case insenstive)'),
    ('icontains', 'Contains (case insensitive)'),
    ('gt', '>'),
    ('gte', '>='),
    ('lt', '<'),
    ('lte', '<='),
    ('istartswith', 'Starts With (cae insensitive)'),
    ('iendswith', 'Ends With (case insensitive)'),
    ]

COMPARISONS = [
    ('a', 'Check "Abnormal" Flag'),
    ('n', 'Compare value with numerical result'),
    ('s', 'Compare value with string result'),
   ]

LOAD_STATUS = [
    ('skipped', 'Skipped'),
    ('attempted', 'Attempted'),
    ('errors', 'Errors - Partial Load'),
    ('loaded', 'Loaded'),
    ('failure', 'Failure'),
    ]
