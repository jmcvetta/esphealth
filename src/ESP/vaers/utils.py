from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context

from vaers.models import AdverseEvent
from ESP import settings

def send_notifications():
    cases_to_notify = AdverseEvent.objects.filter(state='AR')
    current_site = Site.objects.get_current()

    for case in cases_to_notify:
        try:
            provider = case.patient.DemogProvider
            params = {
                'provider':provider,
                'url':'http://%s%s' % (current_site, reverse(
                        'case_details', kwargs={'case_id':case.digest})),
                'misdirected_email_contact':settings.VAERS_EMAIL_SENDER
                }
            
            t = get_template('email_messages/notify_case.txt')
            msg = t.render(Context(params))
            send_mail(settings.VAERS_NOTIFICATION_EMAIL_SUBJECT, msg,
                      settings.VAERS_EMAIL_SENDER, 
                      [settings.VAERS_EMAIL_RECIPIENT],
                      fail_silently=False)

        except:
            print 'Failed to send in case %s' % case.id
            

