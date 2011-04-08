import sys

from django.db.models import Q

from ESP.hef.models import Event
from ESP.emr.models import  LabResult


raise RuntimeError("Don't use this script unless you REALLY know what you're doing.")


q_obj = Q(content_type=13) & ~Q(name__iendswith='_order')
Event.objects.filter(q_obj)
Event.objects.filter(q_obj).values('object_id')
event_lab_ids = Event.objects.filter(q_obj).values('object_id')
del q_obj


q_obj = Q(result_string__icontains='tnp') & ~Q(events__name__iendswith='_order')
q_obj = q_obj | Q(native_code='87522--8006')


bogus_labs = LabResult.objects.filter(q_obj)
bogus_lab_ids = bogus_labs.values_list('pk', flat=True)
bogus_events = Event.objects.filter(content_type=13, object_id__in=bogus_lab_ids )

print 'bogus event count: %s' % bogus_events.count()


q_obj = Q(case__pk__isnull=False) | Q(case_after__pk__isnull=False) | Q(case_before__pk__isnull=False) | Q(case_ever__pk__isnull=False)
bogus_events_w_cases = bogus_events.filter(q_obj)

for e in bogus_events_w_cases:
    print e
    cases = e.case_set.all() | e.case_before.all() | e.case_after.all() | e.case_ever.all()
    print 'deleting cases:  %s' % cases
    cases.delete()
    print 'deleting event: %s' % e
    e.delete()


# Regenerate, to skip the ones we deleted above
bogus_events = Event.objects.filter(content_type=13, object_id__in=bogus_lab_ids )

print 'deleting bogus events without cases'
bogus_events.delete()
