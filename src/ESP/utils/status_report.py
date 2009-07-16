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
import email
from email.mime.text import MIMEText
import smtplib

from django.db.models import Max

from ESP.settings import ADMINS
from ESP.settings import DATE_FORMAT
from ESP.settings import SITE_NAME
from ESP.settings import EMAIL_HOST
from ESP.settings import EMAIL_PORT
from ESP.settings import EMAIL_SENDER
from ESP.emr.models import Patient
from ESP.emr.models import Hl7Message
from ESP.nodis.models import Case
from ESP.nodis import defs
from ESP.nodis.core import Disease
from ESP.utils.utils import log


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
        condition = dis.name
        count = Case.objects.filter(condition=condition).count()
        out += [template % (condition, count)]
    return '\n'.join(out)
    
    

def generate_message():
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
    log.debug('values: %s' % values)
    return MESSAGE_TEMPLATE % values


def send_email(message):
    msg = MIMEText(message)
    msg['Subject'] = '%s ESP Status Report %s' % (SITE_NAME, datetime.datetime.now().strftime(DATE_FORMAT))
    msg['From'] = EMAIL_SENDER
    to = ', '.join( [row[1] for row in ADMINS] )
    to = 'jason.mcvetta@channing.harvard.edu'
    msg['To'] = to
    smtp = smtplib.SMTP()
    smtp.connect()
    status = smtp.sendmail(EMAIL_SENDER, [row[1] for row in ADMINS], msg.as_string())
    log.debug('status: %s' % status)
    
    

def main():
    msg = generate_message()
    #send_email(message=msg)
    print msg
    
    
    
    
if __name__ == '__main__':
    main()
