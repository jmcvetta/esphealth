import rules




def codes():
    '''
    Returns a set of all the codes that are indicator of diagnosis
    that may be an adverse event.
    '''
    codes = []
    for key in rules.VAERS_DIAGNOSTICS.keys():
        codes.extend(key.split(';'))
    return set(codes)


# This can be a constant
VAERS_DIAGNOSTICS_CODES = codes()

def by_code(icd9_code):
    # Check all rules, to see if the code we have is a possible adverse event
    for key in rules.VAERS_DIAGNOSTICS.keys():
        codes = key.split(';')
        # for all the codes that indicate the diagnosis, we see if it matches
        # It it does, we have it.
        for code in codes:
            if match_icd9_expression(icd9_code, code.strip()):
                return rules.VAERS_DIAGNOSTICS[key]

    # Couldn't find a match
    return None


        
def exclusion_codes(icd9_code):
    '''
    Given an icd9 code represented by event_code, returns a list of
    icd9 codes that indicate that the diagnosis is not an adverse
    event
    '''
    diagnosis = by_code(icd9_code)
    return (diagnosis and diagnosis.get('ignore_codes', None))


def is_match(code):
    for expression in VAERS_DIAGNOSTICS_CODES:
        if match_icd9_expression(code, expression):
            return True
    return False
    

def match_icd9_expression(icd9_code, expression_to_match):
    '''
    considering expressions to represent:
    - A code: 558.3
    - An interval of codes: 047.0-047.1
    - A wildcard to represent a family of codes: 320*, 345.*
    - An interval with a wildcard: 802.3-998*
    
    this function verifies if icd9_code matches the expression, 
    i.e, satisfies the condition represented by the expression
    '''

    def transform_expression(expression):
        '''
        considering expressions to represent:
        - An interval of codes: 047.0-047.1
        - A wildcard to represent a family of codes: 320*, 345.*
        - An interval with a wildcard: 802.3-998*
        '''


        if '-' in expression:
            # It's an expression to show a range of values
            low, high = expression.split('-')
            if '.*' in low: low = low.replace('.*', '.00')
            if '*' in low: low = low.replace('*', '.00')

            if '.*' in high: high = high.replace('.*', '.99')
            if '*' in high: high = high.replace('*', '.99')
            
        if '*' in expression and '-' not in expression:
            ls, hs = ('00', '99') if '.*' in expression else ('.00', '.99')
                
            low, high = expression.replace('*', ls), expression.replace('*', hs)
            
        if '*' not in expression and '-' not in expression:
            raise ValueError, 'not a valid icd9 expression'

        # We must get two regular codes in the end.
        ll, hh = float(low), float(high)    


        assert(type(ll) is float)
        assert(type(hh) is float)
    
        return ll, hh
            
    
    def match_precise(code, expression):
        return code == expression
    
    def match_range(code, floor, ceiling):
        return floor <= code <= ceiling

    def match_wildcard(code, regexp):
        floor, ceiling = transform_expression(regexp)
        return match_range(code, floor, ceiling)

    # Verify first if the icd9 code is valid
    # We will only accept icd9 codes in the DDD.D(D?) format
    try:
        length = len(icd9_code.strip())
        assert(5 <= length <= 6)
        assert('.' == icd9_code[3])
        target = float(icd9_code)
    except Exception:
        #In case it is a code that is really out of the pattern
        return match_precise(icd9_code.strip(), 
                             expression_to_match.strip())
    
    try:
        expression = float(expression_to_match)
        return match_precise(target, expression)
    except ValueError:
        # expression_to_match is not a code
        return match_wildcard(target, expression_to_match)




        






        


            
    
