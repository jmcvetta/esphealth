from django.contrib.sites.models import Site
from django.db.models import Q

from ESP.vaers.models import AdverseEvent
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


    for case in cases_to_notify:
        try:
            case.mail_notification()
        except Exception, why:
            print 'Failed to send in case %s.\nReason: %s' % (case.id, why)


            

