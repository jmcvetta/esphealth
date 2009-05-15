'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                            Choices for Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


DATA_TRANSPORT = [
    ('File', 'File'),
    ('DB_Dump', 'DB Dump'),
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
    ('Q','CONFIRMED CASE, TRANSMIT TO HEALTH DEPARTMENT'), 
    ('S','TRANSMITTED TO HEALTH DEPARTMENT')
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

HL7_MESSAGE_LOAD_STATUS = [
    ('s', 'Skipped'),
    ('a', 'Attempted'),
    ('l', 'Loaded'),
    ('f', 'Failure'),
    ]
