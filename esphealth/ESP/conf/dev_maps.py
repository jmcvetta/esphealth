'''
Code maps for development - remove before release
'''

from ESP.conf.models import LabTestMap

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
