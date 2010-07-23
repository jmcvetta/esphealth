#!/usr/bin/env python


from ESP.new_hef.models import AbstractLabTest
from ESP.new_hef.models import LabTestMap
from ESP.conf.models import CodeMap


TRANSLATION = {
    'rpr': 'syphilis_rpr',
    'vdrl_serum': 'syphilis_vdrl_serum',
    'vdrl_csf': 'syphilis_vdrl_csf',
    }

test_names = AbstractLabTest.objects.values_list('name', flat=True)

for cm in CodeMap.objects.all():
    heuristic = cm.heuristic
    if heuristic in TRANSLATION:
        heuristic = TRANSLATION[heuristic]
    if not heuristic in test_names:
        print 'No AbstractLabTest found matching "%s"' % heuristic
        continue
    test = AbstractLabTest.objects.get(name=heuristic)
    ltm, created = LabTestMap.objects.get_or_create(
        test = test,
        code = cm.native_code,
        defaults = {
            'code_match_type': 'exact',
            'threshold': cm.threshold,
            'reportable': cm.reportable,
            'output_code': cm.output_code,
            'output_name': cm.output_name,
            'snomed_pos': cm.snomed_pos,
            'snomed_neg': cm.snomed_neg,
            'snomed_ind': cm.snomed_ind,
            'notes': cm.notes,
            }
        )
    if created:
        print 'Created new LabTestMap for %s, %s' % (test, cm.native_code)
    else:
        print 'LabTestMap for %s, %s already exists' % (test, cm.native_code)
