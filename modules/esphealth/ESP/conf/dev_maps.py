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
        test_uri = 'urn:x-esphealth:abstractlabtest:glucose-compound-random-fasting-flag:v1',
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
    ]:
    obj, created = LabTestMap.objects.get_or_create(
        test_uri = 'urn:x-esphealth:abstractlabtest:glucose-compound-random-fasting-result:v1',
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
