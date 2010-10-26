from ESP.hef.models import AbstractLabTest
from ESP.hef.models import LabTestMap


a1c = AbstractLabTest.objects.get(name='a1c')
ogtt75_series = AbstractLabTest.objects.get(name = 'ogtt75_series')
glucose_fasting = AbstractLabTest.objects.get(name='glucose_fasting')
gad65 = AbstractLabTest.objects.get(name='gad65')
ica512 = AbstractLabTest.objects.get(name='ica512')
islet_cell_antibody = AbstractLabTest.objects.get(name='islet_cell_antibody')
c_peptide = AbstractLabTest.objects.get(name='c_peptide')
insulin_ab = AbstractLabTest.objects.get(name='insulin_antibody')

for c in [
    '80061--258',
    'MR0001--258',
    'MR0001--2882',
    'MR0001--7621',
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test = a1c,
        native_code = c,
        code_match_type = 'exact',
        record_type = 'result',
        )
    if created:
        print 'Created: %s' % obj
    else:
        print 'Already existed: %s' % obj
    
    
obj, created = LabTestMap.objects.get_or_create(
    test = a1c,
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
        test = ogtt75_series,
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
        test = glucose_fasting,
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
    test = gad65,
    native_code = '83519--3571',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 1.0,
    )

LabTestMap.objects.get_or_create(
    test = ica512,
    native_code = '86341--7163',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 0.8,
    )

LabTestMap.objects.get_or_create(
    test = islet_cell_antibody,
    native_code = '86341--3421',
    code_match_type = 'exact',
    record_type = 'both',
    )

LabTestMap.objects.get_or_create(
    test = islet_cell_antibody,
    native_code = '86341--3422',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 1.25,
    )

#
# C-Peptide
#
LabTestMap.objects.get_or_create(
    test = c_peptide,
    native_code = '84681--1245',
    code_match_type = 'exact',
    record_type = 'both',
    )
LabTestMap.objects.get_or_create(
    test = c_peptide,
    native_code = '84681--5497',
    code_match_type = 'exact',
    record_type = 'both',
    )


#
# Insulin AB
#
LabTestMap.objects.get_or_create(
    test = insulin_ab,
    native_code = '86337--2491',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 0.4,
    )
LabTestMap.objects.get_or_create(
    test = insulin_ab,
    native_code = 'N1892--1655',
    code_match_type = 'exact',
    record_type = 'both',
    threshold = 0.8,
    )
