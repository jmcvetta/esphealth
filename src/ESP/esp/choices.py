'''
                            Core Data Model Choices
                                      for
                                  ESP Health

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

# These are used by both conf.models.Rule and esp.models.Case
from ESP.conf.choices import FORMAT_TYPES
from ESP.conf.choices import WORKFLOW_STATES
from ESP.conf.choices import DEST_TYPES

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
