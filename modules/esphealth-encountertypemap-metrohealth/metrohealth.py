'''
                                  ESP Health
                     Encounter-Type Mapper for MetroHealth

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc.
@contact: http://www.esphealth.org
@copyright: (c) 2012 Commonwealth Informatics Inc.
@license: LGPL
'''

from ESP.emr.models import Encounter
from ESP.emr.base import SiteDefinition


class metrohealth(SiteDefinition):
    '''
    metrohealth
    '''
    
    uri = 'urn:x-esphealth:encountertypemap:commoninf:metrohealth:v1'
    
    short_name = 'metrohealth'
    

    def generate(self):
        Encounter.objects.filter(encounter_type=None, raw_encounter_type='HOSP ENC', site_name__contains='Emergency').update(encounter_type='ER',priority=1)
        Encounter.objects.filter(encounter_type=None, raw_encounter_type__contains='HOSP').update(encounter_type='hospitalization',priority=2)
        Encounter.objects.filter(encounter_type=None, raw_encounter_type__in=['APPT','HISTORY','VISIT','IMMUNIZATION']).update(encounter_type='visit',priority=3)
        Encounter.objects.filter(encounter_type=None).update(encounter_type='other',priority=4)
