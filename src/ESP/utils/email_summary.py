#!/usr/bin/env python


MESSAGE_TEMPLATE = '''

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ESP STATUS REPORT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Date:  %(date)s
Local Site: %(localsite)s


--------------------------------------------------------------------------------
HL7
--------------------------------------------------------------------------------

Latest Successful HL7 timestamp: %(hl7_ts)s
Number of Successfully Loaded HL7 messages: %(hl7_num_l)s
Number of Failed HL7 messages: %(hl7_num_f)s


--------------------------------------------------------------------------------
NODIS
--------------------------------------------------------------------------------

New Cases Today:
%(new_cases)s

Case Summary:
%(case_summary)s

'''


import datetime

from django.db.models import Max

from ESP.settings import DATE_FORMAT
from ESP.settings import SITE_NAME
from ESP.emr.models import Patient
from ESP.emr.models import Hl7Message
from ESP.nodis.models import Case
from ESP.nodis import defs
from ESP.nodis.core import Disease


def new_cases(template):
    '''
    Returns string describing cases detected today.
    '''
    out = []
    today = datetime.date.today()
    for condition in Case.objects.values_list('condition').distinct():
        condition = condition[0]
        count = Case.objects.filter(created_timestamp__gte=today, condition=condition).count()
        if count:
            out += [template % (condition, count)]
    if out:
        return '\n'.join(out)
    else:
        return 'No new cases.'
    
    
def case_summary(template):
    '''
    Returns string containing count of cases by condition.
    '''
    out = []
    for dis in Disease.get_all_diseases():
        condition = dis.namek
        count = Case.objects.filter(condition=condition).count()
        out += [template % (condition, count)]
    return '\n'.join(out)
    
    

def main():
    lengths = [len(dis.name) for dis in Disease.get_all_diseases()]
    lengths.sort()
    output_template = '%%%ss: %%s' % str(lengths[-1] + 2)
    values = {}
    values['date'] = datetime.datetime.now().strftime(DATE_FORMAT)
    values['localsite'] = SITE_NAME
    values['case_summary'] = case_summary(template=output_template)
    values['new_cases'] = new_cases(template=output_template)
    values['hl7_ts'] = Hl7Message.objects.filter(status='l').aggregate(max=Max('timestamp'))['max']
    values['hl7_num_l'] = Hl7Message.objects.filter(status='l').count()
    values['hl7_num_f'] = Hl7Message.objects.filter(status='f').count()
    print MESSAGE_TEMPLATE % values
    
    
    
if __name__ == '__main__':
    main()