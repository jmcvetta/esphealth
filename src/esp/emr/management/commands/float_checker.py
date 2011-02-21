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
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from optparse import make_option
from esp.emr.models import LabResult
from esp.emr.models import Prescription
from esp.utils.utils import log_query


    
class Command(BaseCommand):
    
    help = 'Ensure float fields in all LabResult and Encounter objects are correctly converted \n'
    help += 'from their corresponding string fields.'
    
    def handle(self, *fixture_labels, **options):
        self.check_labs()
        self.check_prescriptions()

    FLOAT_CATCHER = re.compile(r'(\d+\.?\d*)') 
    
    def float_or_none(self, string):
        '''
        Copied from load_epic.py
        '''
        m = self.FLOAT_CATCHER.match(str(string))
        if m and m.groups():
            return float(m.groups()[0])
        else:
            return None
    
    @transaction.commit_manually
    def check_labs(self):
        i = 0
        q_obj = Q(ref_high_string__isnull=False, ref_high_float__isnull=True)
        q_obj |= Q(ref_low_string__isnull=False, ref_low_float__isnull=True)
        q_obj |= Q(result_string__isnull=False, result_float__isnull=True)
        qs = LabResult.objects.filter(q_obj)
        #log_query('Lab results to check for float results', qs)
        tot = qs.count()
        #tot = 0
        for lab in qs.iterator():
            i += 1
            sid = transaction.savepoint()
            lab.ref_high_float = self.float_or_none(lab.ref_high_string)
            lab.ref_low_float = self.float_or_none(lab.ref_low_string)
            lab.result_float = self.float_or_none(lab.result_string)
            try:
                lab.save()
                #transaction.savepoint_commit(sid)
                transaction.commit()
            except:
                transaction.savepoint_rollback(sid)
                print 'ERROR: Could not process record # %s' % lab.pk
                continue
            print 'Lab  %20s/%s' % (i, tot)
    
    @transaction.commit_manually
    def check_prescriptions(self):
        i = 0
        qs = Prescription.objects.filter(quantity__isnull=False, quantity_float__isnull=True).order_by('pk')
        tot = qs.count()
        for rx in qs:
            i += 1
            sid = transaction.savepoint()
            rx.quantity_float = self.float_or_none(rx.quantity)
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
    

    
