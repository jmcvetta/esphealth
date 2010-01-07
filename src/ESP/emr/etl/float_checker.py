#!/usr/bin/python
'''
Rolls through all EMR records, checking that relevant string fields have been correctly converted to float fields. 
'''

import re
import sys
import pprint
import datetime

from django.db import connection
from django.db import transaction
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription

from ESP.nodis.models import ComplexEventPattern
from ESP.nodis.models import SimpleEventPattern
from ESP.nodis.models import Condition
from ESP.nodis import defs

from ESP.nodis.defs import jaundice_alt400
from ESP.nodis.defs import no_hep_b_surf
from ESP.nodis.defs import no_hep_b
from ESP.nodis.defs import hep_c_1
from ESP.nodis.defs import hep_c
from ESP.nodis.defs import chlamydia

from ESP.nodis.models import Case
from ESP.nodis.models import Pattern
from ESP.hef.models import Event

from ESP.conf.models import CodeMap
from ESP.utils.utils import log_query


    
FLOAT_CATCHER = re.compile(r'(\d+\.?\d*)') 

def float_or_none(self, string):
    '''
    Copied from load_epic.py
    '''
    m = self.float_catcher.match(string)
    if m and m.groups():
        return float(m.groups()[0])
    else:
        return None

def check_prescriptions():
    i = 0
    qs = Prescription.objects.filter(quantity__isnull=False, quantity_float__isnull=True)
    tot = qs.count()
    for rx in qs:
        i += 1
        sid = transaction.savepoint()
        rx.quantity_float = float_or_none(rx.quantity)
        try:
            rx.save()
            transaction.savepoint_commit(sid)
        except:
            transaction.savepoint_rollback(sid)
            print 'ERROR: Could not process record # %s' % rx.pk
            continue
        print 'Rx  %20s/%s' % (i, tot)


def check_labs():
    i = 0
    q_obj = Q(ref_high_string__isnull=False, ref_high_float__isnull=True)
    q_obj |= Q(ref_low_string__isnull=False, ref_low_float__isnull=True)
    q_obj |= Q(result_string__isnull=False, result_float__isnull=True)
    qs = LabResult.objects.filter(q_obj)
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
            transaction.savepoint_commit(sid)
        except:
            transaction.savepoint_rollback(sid)
            print 'ERROR: Could not process record # %s' % lab.pk
            continue
        print 'Lab  %20s/%s' % (i, tot)


def main():
    check_prescriptions()
    check_labs()

if __name__ == '__main__':
    check_labs()
