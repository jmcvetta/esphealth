'''
                                  ESP Health
                     Encounter-Type Mapper for MetroHealth

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc.
@contact: http://www.esphealth.org
@copyright: (c) 2012 Commonwealth Informatics Inc.
@license: LGPL
'''

import sys
from ESP.utils import log
from ESP.emr.models import Encounter
from ESP.emr.base import SiteDefinition


class Metrohealth(SiteDefinition):
    '''
    metrohealth
    '''
    
    uri = 'urn:x-esphealth:encountertypemap:commoninf:metrohealth:v1'
    
    short_name = 'metrohealth'
    

    # TODO: This method, and its analog in the base SiteDefinition class, do 
    # not actually generate anything.  Therefore they should be renamed to 
    # something more descriptive.  One possibility might be "transform()", but
    # the right name really depends on the intended range of uses for 
    # descendents of SiteDefinition.
    def set_enctype(self):
        '''
        This method will update the emr_encounter table with appropriate values for encounter_type so that VAERS heuristics will provide
        the correct priority to cases.  Determination of encounter type will depend on site specific data collection practices
        '''
        try:
            log.debug("Running Metrohealth SiteDefinition")
            Encounter.objects.filter(encounter_type=None, raw_encounter_type='HOSP ENC', site_name__contains='Emergency').update(encounter_type='ER',priority=1)
            Encounter.objects.filter(encounter_type=None, raw_encounter_type__contains='HOSP').update(encounter_type='hospitalization',priority=2)
            Encounter.objects.filter(encounter_type=None, raw_encounter_type__in=['APPT','HISTORY','VISIT','IMMUNIZATION']).update(encounter_type='visit',priority=3)
            Encounter.objects.filter(encounter_type=None).update(encounter_type='other',priority=4)
            log.debug("Metrohealth SiteDefinition run complete")
            return True
        except:
            log.debug("Unexpected error: " + sys.exc_info()[0])
            return False


def encountertypemap():
    return [Metrohealth()]