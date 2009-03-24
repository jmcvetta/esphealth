'''
Core Data Model Choices
for
ESP Health
'''

# Subset of Django query operators used for matching Loinc_Rules
OPERATORS = [
    ('iexact', 'Exact (case insenstive)'),
    ('icontains', 'Contains (case insensitive)'),
    ('gt', '>'),
    ('gte', '>='),
    ('lt', '<'),
    ('lte', '<='),
    ('istartswith', 'Starts With (case insensitive)'),
    ('iendswith', 'Ends With (case insensitive)'),
    ]

FORMAT_TYPES = (
    ('Text','Plain text representation'),
    ('XML','eXtended Markup Language format'),
    ('HL7', 'Health Level 7 markup'),
    ('MADPHSimple', 'MADPH Simple markup (pipe delim simplifiedhl7)'),
)

WORKFLOW_STATES = [
    ('AR','AWAITING REVIEW'),
    ('UR','UNDER REVIEW'),
    ('RM', 'REVIEW By MD'),
    ('FP','FALSE POSITIVE - DO NOT PROCESS'),
    ('Q','CONFIRMED CASE, TRANSMIT TO HEALTH DEPARTMENT'), 
    ('S','TRANSMITTED TO HEALTH DEPARTMENT')
    ]

DEST_TYPES = (
    ('TextFile','Text file on the filesystem - path'),
    ('PHIN-MS','PHINMS server URL'),
    ('SOAP', 'SOAP service URL'),
    ('XMLRPC', 'XML-RPC Server URL'),
)


