from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context
from django.db.models import Q

from vaers.models import AdverseEvent
from ESP import settings

import datetime

def send_notifications():
    now = datetime.datetime.now()
    three_days_ago = now - datetime.timedelta(days=3)

    # Category 3 (cases that need clinicians confirmation for report)
    must_confirm = Q(category='confirm') 

    # Category 2 (cases that are reported by default, i.e, no comment
    # from the clinician after 72 hours since the detection.
    may_receive_comments = Q(category='default', created_on__gte=three_days_ago)

    cases_to_notify = AdverseEvent.objects.filter(must_confirm|may_receive_comments)
    current_site = Site.objects.get_current()

    for case in cases_to_notify:
        try:
            provider = case.patient.DemogProvider
            params = {
                'provider':provider,
                'url':'http://%s%s' % (current_site, reverse(
                        'verify_case', kwargs={'key':case.digest})),
                'misdirected_email_contact':settings.VAERS_EMAIL_SENDER
                }
            
            t = get_template('email_messages/notify_case.txt')
            msg = t.render(Context(params))
            send_mail(settings.VAERS_NOTIFICATION_EMAIL_SUBJECT, msg,
                      settings.VAERS_EMAIL_SENDER, 
                      [settings.VAERS_EMAIL_RECIPIENT],
                      fail_silently=False)

        except Exception, why:
            print 'Failed to send in case %s.\nReason: %s' % (case.id, why)


            

