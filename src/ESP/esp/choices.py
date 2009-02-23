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
    ('istartswith', 'Starts With (cae insensitive)'),
    ('iendswith', 'Ends With (case insensitive)'),
    ]