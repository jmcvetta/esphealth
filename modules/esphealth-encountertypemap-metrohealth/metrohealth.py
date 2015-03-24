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
    
    def set_enctype(self, e):
        '''
        This method will return appropriate values for encounter_type and priority so that VAERS heuristics will provide
        the correct priority to cases.  Determination of encounter type will depend on site specific data collection practices
        '''
        if (e.raw_encounter_type) and (e.site_name): #make sure values are available
            try:
                if e.raw_encounter_type=='HOSP ENC' and e.site_name.find('Emergency')>-1:
                    encounter_type='ER'
                    priority=1
                elif e.raw_encounter_type.find('HOSP')>-1:
                    encounter_type='hospitalization'
                    priority=2
                elif any(x==e.raw_encounter_type for x in['APPT','HISTORY','VISIT','IMMUNIZATION']):
                    encounter_type='visit'
                    priority=3
                else:
                    encounter_type='other'
                    priority=4
                return encounter_type, priority
            except AttributeError as detail:
                log.debug("Attribute error: %s " % detail)
                return None, None
            else:
                log.debug("Unexpected error: %s " % sys.exc_info()[0])
                return None, None
        else:
            return None, None


    def set_hospprobs(self, hp):
        '''
        Attempts to update hospital_problem model instance with site specific decoding algorithm 
        '''
        try:
            if hp.priority_code==1:
                priority='High'
            elif hp.priority_code==2:
                priority='Medium'
            elif hp.priority_code==3:
                priority='Low'
            elif (hp.priority_code):
                priority='no decode'
            else:
                priority=None
                
            #need decodes for principal_prob, and present_on_adm
            principal_prob=None
            present_on_adm=None

            return principal_prob, present_on_adm, priority
        except:
            log.debug("Unexpected error: ")
            log.debug(sys.exc_info()[0])
            return None, None


def encountertypemap():
    return [Metrohealth()]