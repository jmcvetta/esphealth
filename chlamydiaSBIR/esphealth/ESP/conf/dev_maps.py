'''
Code maps for development - remove before release
'''

from ESP.conf.models import ResultString
from ESP.conf.models import LabTestMap


#-------------------------------------------------------------------------------
#
# Result Strings
#
#-------------------------------------------------------------------------------
ResultString.objects.get_or_create(
    value = 'reactiv',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'pos',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'detec',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'confirm',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'non',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'neg',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'not det',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'nr',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'indeterminate',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'not done',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'tnp',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )



#-------------------------------------------------------------------------------
#
# Compound Random/Fasting Glucose
#
#-------------------------------------------------------------------------------
for c in [
    '80061--6748',
    '82951--7889',
    '82947--6748',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'glucose-compound-random-fasting-flag',
        native_code = c,
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'result',
            },
        )
    if created:
        print 'created: %s' % obj
    else:
        print 'already existed: %s' % obj

for c in [
    '82947--111',
    '82947--61',
    '82948--61',
    '82947--1795',
    '82948--1795',
    '82947--2948',
    '82948--2948',
    '82962--2948',
    '87220--2948',
    '82948--2948',
    '83036--2948',
    '82947--6545',
    '80004--2523',
    '80004--3301',
    '80048--2523',
    '80051--2523',
    '80053--2523',
    '80069--2523',
    '80076--2523',
    '81000--2523',
    '81001--2523',
    '81002--2523',
    '81003--2523',
    '82040--2523',
    '82272--2523',
    '82947--2523',
    '82947--3302',
    '82947--5758',
    '82948--2523',
    '82948--2948',
    '82948--3301',
    '82948--3302',
    '82948--3303',
    '82948--3305',
    '82948--3307',
    '82951--2523',
    '82951--3301',
    '82951--3302',
    '82951--3303',
    '82951--3305',
    '82951--3306',
    '82951--3307',
    '82951--4506',
    '82951--4774',
    '82951--5758',
    '82962--2523',
    '84520--2523',
    'N1460--2523',
    'N1646--2523',
    'N2897--2523',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'glucose-compound-random-fasting-result',
        native_code = c,
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'result',
            },
        )
    if created:
        print 'created: %s' % obj
    else:
        print 'already existed: %s' % obj


    
#-------------------------------------------------------------------------------
#
# A1C
#
#-------------------------------------------------------------------------------

for c in [
    '80061--258',
    'MR0001--258',
    'MR0001--2882',
    'MR0001--7621',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'a1c',
        native_code = c,
        code_match_type = 'exact',
        record_type = 'result',
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'result',
            },
        )
    if created:
        print 'Created: %s' % obj
    else:
        print 'Already existed: %s' % obj
    
    
obj, created = LabTestMap.objects.get_or_create(
    test_name = 'a1c',
    native_code = '83036',
    code_match_type = 'istartswith',
    record_type = 'order',
    )
if created:
    print 'Created: %s' % obj
else:
    print 'Already existed: %s' % obj

for c in ['82951F', '82951H', '82951K', '82951M']:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'ogtt75-series',
        native_code = c,
        code_match_type = 'exact',
        record_type = 'order',
        )
    if created:
        print 'Created: %s' % obj
    else:
        print 'Already existed: %s' % obj


for c in [
    '80048--2877',
    '80053--2877',
    '82947--2877',
    '82948--560',
    '82951--2876',
    '82951--2877',
    '82951--2943',
    '82951--3301',
    '82951--560',
    '82951--882',
    '82952--560',
    'DMA002--2877',
    'N1646--2877',
    'N1646--3301',
    'N1646--560',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'glucose-fasting',
        native_code = c,
        code_match_type = 'exact',
        record_type = 'result',
        )
    if created:
        print 'Created: %s' % obj
    else:
        print 'Already existed: %s' % obj


#-------------------------------------------------------------------------------
#
# Diabetes Auto-Antibody Tests
#
#-------------------------------------------------------------------------------

LabTestMap.objects.get_or_create(
    test_name = 'gad65',
    native_code = '83519--3571',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 1.0,
    )

LabTestMap.objects.get_or_create(
    test_name = 'ica512',
    native_code = '86341--7163',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 0.8,
    )

LabTestMap.objects.get_or_create(
    test_name = 'islet-cell-antibody',
    native_code = '86341--3421',
    code_match_type = 'exact',
    record_type = 'both',
    )

LabTestMap.objects.get_or_create(
    test_name = 'islet-cell-antibody',
    native_code = '86341--3422',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 1.25,
    )

#
# C-Peptide
#
LabTestMap.objects.get_or_create(
    test_name = 'c-peptide',
    native_code = '84681--1245',
    code_match_type = 'exact',
    record_type = 'both',
    )
LabTestMap.objects.get_or_create(
    test_name = 'c_peptide',
    native_code = '84681--5497',
    code_match_type = 'exact',
    record_type = 'both',
    )


#
# Insulin AB
#
LabTestMap.objects.get_or_create(
    test_name = 'insulin-antibody',
    native_code = '86337--2491',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 0.4,
    )
LabTestMap.objects.get_or_create(
    test_name = 'insulin-antibody',
    native_code = 'N1892--1655',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 0.8,
    )


# 
# HDL Cholesterol
#
for code in [
    '80061--390',
    '80061EXT--390',
    '82465--390',
    '82947--390',
    '83718--390',
    'LA0346--390',
    'MR0001--390',
    'N1460--390',
    '80061--7628',
    '80061EXT--7628',
    '82272--7628',
    '82465--7628',
    '82947--7628',
    '83718--7628',
    'MR0001--7628',
    '80061--390',
    '82465--390',
    '83718--390',
    '80061--799',
    '83718--799',
    '83721--799',
    'DMA019--799',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'cholesterol-hdl',
        native_code = code,
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'both',
            }
        )
    if created:
        print 'Added new map: %s' % obj


# 
# LDL Cholesterol
#
for code in [
    '80061--1505',
    '80061EXT--1505',
    '82465--1505',
    '83036--1505',
    '83721--1505',
    'MR0001--1505',
    'N1985--1505',
    '80061--7625',
    '80061EXT--7625',
    '82465--7625',
    '82947--7625',
    '83721--7625',
    '83721EXT--7625',
    'N1985--7625',
    '80061--7629',
    '80061--800',
    '80061EXT--7629',
    '82272--7629',
    '82465--800',
    '82947--800',
    '83036--800',
    '83721--800',
    'DMA019--800',
    'LA0346--800',
    'MR0001--7629',
    'N1460--800',
    'N1985--7629',
    'N1985--800',
    '80061--63',
    'N1985--63',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'cholesterol-ldl',
        native_code = code,
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'both',
            }
        )
    if created:
        print 'Added new map: %s' % obj


# 
# Total Cholesterol
#
for code in [
    '80061--374',
    '80076--374',
    '82040--374',
    '82465--374',
    '82947--374',
    '83715--374',
    '83721--374',
    'DMA019--374',
    'LA0346--374',
    'MR0001--374',
    'N1460--374',
    '80061--7626',
    '80061EXT--7626',
    '82272--7626',
    '82465--7626',
    '84478--7626',
    'MR0001--7626',
    '80061--1321',
    '82465--1321',
    'MR0001--1321',
    '83715--4839',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'cholesterol-total',
        native_code = code,
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'both',
            }
        )
    if created:
        print 'Added new map: %s' % obj

# 
# Triglycerides
#
for code in [
    '80061--456',
    '80061--7627',
    '80061EXT--7627',
    '80299--823',
    '82040--456',
    '82272--7627',
    '82465--456',
    '82465--7627',
    '82947--456',
    '82947--7627',
    '83715--456',
    '83715--4840',
    '83715--4840',
    '83719--456',
    '83721--456',
    '84478--456',
    '84478--4840',
    '84478--7627',
    'DMA019--456',
    'MR0001--456',
    'MR0001--7627',
    'N1460--456',
    '83715--4840',
    '84478--4840',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'triglycerides',
        native_code = code,
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'both',
            }
        )
    if created:
        print 'Added new map: %s' % obj


# 
# ALT
#
for code in [
    '80053--1728',
    '80061EXT--1728',
    '83718--1728',
    '84450EXT--1728',
    '84460--1728',
    'LA0297--1728',
    '80053--58',
    '80076--58',
    '82040--58',
    '82947--58',
    '83036--58',
    '84450--58',
    '84460--1793',
    '84460--58',
    '85048--58',
    '87522--58',
    'LA0269--1793',
    'LA0269--58',
    '80076--7671',
    '82565EXT--7671',
    '82947--7671',
    '84460EXT--7671',
    '82947--286',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_name = 'alt',
        native_code = code,
        defaults = {
            'code_match_type': 'exact',
            'record_type': 'both',
            }
        )
    if created:
        print 'Added new map: %s' % obj

