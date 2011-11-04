'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Chlamydia Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''

from ESP.nodis.base import DiseaseDefinition
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import LabResultPositiveHeuristic



class Syphilis(DiseaseDefinition):
    '''
    Syphilis
    '''
    
    conditions = ['syphilis']
    
    uri = 'urn:x-esphealth:disease:channing:syphilis:v1'
    
    short_name = 'syphilis'
    
    test_name_search_strings = [
	    'syph',
	    'rpr', 
	    'vdrl',
	    'tp', 
	    'fta',
	    'trep',
	    'pallidum',
	    ]
    
    timespan_heuristics = []
    
    @property
    def event_heuristics(self):
        heuristic_list = []
        heuristic_list.append( PrescriptionHeuristic(
            name = 'penicillin_g',
            drugs = ['penicillin g', 'pen g'],
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'doxycycline_7_day',
            drugs = ['doxycycline',],
            min_quantity = 14, # Need 14 pills for 7 days
            ))
        heuristic_list.append( PrescriptionHeuristic(
            name = 'ceftriaxone_1_or_2_gram',
            drugs = ['ceftriaxone',],
            doses = [ 
                Dose(quantity = 1, units = 'g'),
                Dose(quantity = 2, units = 'g'),
                ],
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'rpr',
            titer_dilution = 8,
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'vdrl',
            titer_dilution = 8,
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'tppa',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'ftp-abs',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'tp-igg',
            ))
        heuristic_list.append( LabResultPositiveHeuristic(
            test_name = 'vrdl-csf',
            ))
        return heuristic_list
    
    def generate(self):
        raise NotImplementedError('nothing to see here')
    

#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

syphilis_definition = Syphilis()

def event_heuristics():
    return syphilis_definition.event_heuristics

def disease_definitions():
    return [syphilis_definition]
