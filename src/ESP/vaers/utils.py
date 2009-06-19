
import datetime

from django.contrib.sites.models import Site
from django.db.models import Q


def make_clustering_event_report_file(filename, events):
    f = open(filename, 'w')
    f.write('\t'.join(['id', 'vdate', 'edate', 'gap', 'vaccine', 
                       'comment', 'age', 'gender']))
    f.write('\n')
    for ev in events:
        f.write(ev.render_temporal_report())
        f.write('\n')
    f.close()


def send_event_alert(**kw):
    '''Send newly found adverse events'''
    from ESP.vaers.models import AdverseEvent
    tests_only = kw.pop('test', False)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    for ev in AdverseEvent.objects.filter(created_on__gt=yesterday):
        if tests_only and ev.is_fake(): 
            ev.mail_notification()



if __name__ == '__main__':
    send_event_alert(test=True)
    

