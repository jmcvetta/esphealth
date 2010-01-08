#!/usr/bin/python
'''
Rolls through all EMR records, checking that relevant string fields have been
correctly converted to float fields. 
'''

import re
import sys
import pprint
import datetime

from django.db import transaction
from django.db.models import Q
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.utils.utils import log_query


    
FLOAT_CATCHER = re.compile(r'(\d+\.?\d*)') 

def float_or_none(string):
    '''
    Copied from load_epic.py
    '''
    m = FLOAT_CATCHER.match(string)
    if m and m.groups():
        return float(m.groups()[0])
    else:
        return None

@transaction.commit_manually
def check_prescriptions():
    i = 0
    qs = Prescription.objects.filter(quantity__isnull=False, quantity_float__isnull=True).order_by('pk')
    tot = qs.count()
    for rx in qs:
        i += 1
        sid = transaction.savepoint()
        rx.quantity_float = float_or_none(rx.quantity)
        try:
            rx.save()
            #transaction.savepoint_commit(sid)
            transaction.commit()
        except:
            transaction.savepoint_rollback(sid)
            print 'ERROR: Could not process record # %s' % rx.pk
            continue
        del rx
        del sid
        print 'Rx  %20s/%s' % (i, tot)


@transaction.commit_manually
def check_labs():
    i = 0
    q_obj = Q(ref_high_string__isnull=False, ref_high_float__isnull=True)
    q_obj |= Q(ref_low_string__isnull=False, ref_low_float__isnull=True)
    q_obj |= Q(result_string__isnull=False, result_float__isnull=True)
    qs = LabResult.objects.filter(q_obj).order_by('pk')
    log_query('Lab results to check for float results', qs)
    tot = qs.count()
    for lab in qs:
        i += 1
        sid = transaction.savepoint()
        lab.ref_high_float = float_or_none(lab.ref_high_string)
        lab.ref_low_float = float_or_none(lab.ref_low_string)
        lab.result_float = float_or_none(lab.result_string)
        try:
            lab.save()
            #transaction.savepoint_commit(sid)
            transaction.commit()
        except:
            transaction.savepoint_rollback(sid)
            print 'ERROR: Could not process record # %s' % lab.pk
            continue
        print 'Lab  %20s/%s' % (i, tot)


if __name__ == '__main__':
    check_labs()
    check_prescriptions()
    
