'''
                                  ESP Health
                         Notifiable Diseases Framework
                              Disease Defintions


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from ESP.settings import DEFAULT_REPORTABLE_ICD9S
from ESP.nodis.core import DiseaseCriterion
from ESP.nodis.core import DiseaseDefinition
from ESP.hef.events import jaundice
from ESP.hef.events import fever
from ESP.hef.events import alt_2x
from ESP.hef.events import ast_2x
from ESP.hef.events import alt_5x
from ESP.hef.events import ast_5x
from ESP.hef.events import hep_b_igm_ab
from ESP.hef.events import hep_b_surface
from ESP.hef.events import hep_b_viral_dna
from ESP.hef.events import hep_b_igm_ab
from ESP.hef.events import chronic_hep_b
from ESP.hef.events import no_hep_b_surface
from ESP.hef.events import high_calc_bilirubin
from ESP.hef.events import total_bilirubin_high
from ESP.hef.events import gonorrhea as gonorrhea_event
from ESP.hef.events import chlamydia as chlamydia_event
from ESP.hef.events import CHLAMYDIA_LOINCS
from ESP.hef.events import GONORRHEA_LOINCS
from ESP.hef.events import hep_a_igm_ab


#===============================================================================
#
# Chlamydia
#
#-------------------------------------------------------------------------------

chlamydia_crit_1 = DiseaseCriterion(
    name = 'Chlamydia Criterion 1',
    version = 1,
    window = 30, # Not applicable, since only one primary event
    require = [
        (chlamydia_event,),
        ],
    )

chlamydia = DiseaseDefinition(
    name = 'Chlamydia',
    criteria = [chlamydia_crit_1,],
    icd9s = [
        '788.7',
        '099.40',
        '597.80',
        '780.6A',
        '616.0',
        '616.10',
        '623.5',
        '789.07',
        '789.04',
        '789.09',
        '789.03',
        '789.00',
        ],
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    med_names = [
        'azithromycin',
        'levofloxacin',
        'ofloxacin',
        'ciprofloxacin',
        'doxycycline',
        'eryrthromycin',
        'amoxicillin',
        'EES',
        ],
    med_days_before = 7,
    med_days_after = 14,
    # Report both Chlamydia and Gonorrhea labs
    lab_loinc_nums = CHLAMYDIA_LOINCS + GONORRHEA_LOINCS,
    lab_days_before = 30,
    lab_days_after = 30,
    )


#===============================================================================
#
# Gonorrhea
#
#-------------------------------------------------------------------------------

gonorrhea_crit_1 = DiseaseCriterion(
    name = 'Gonorrhea Criterion 1',
    version = 1,
    window = 30,
    require = [
        (gonorrhea_event,),
        ],
    )

gonorrhea = DiseaseDefinition(
    name = 'Gonorrhea',
    criteria = [gonorrhea_crit_1,],
    icd9s = [
        '788.7',
        '099.40',
        '597.80',
        '616.0',
        '616.10',
        '623.5',
        '789.07',
        '789.04',
        '789.09',
        '789.03',
        '789.00',
        ],
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = GONORRHEA_LOINCS, 
    lab_days_before = 28,
    lab_days_after = 28,
    med_names = [
        'amoxicillin',
        'cefixime',
        'cefotaxime',
        'cefpodoxime',
        'ceftizoxime',
        'ceftriaxone',
        'gatifloxacin',
        'levofloxacin',
        'ofloxacin',
        'spectinomycin',
        'moxifloxacin',
        ],
    med_days_before = 7,
    med_days_after = 14
    )



#===============================================================================
#
# Hepatitis A
#
#-------------------------------------------------------------------------------

hep_a_crit_1 = DiseaseCriterion(
    name = 'Acute Hepatitis A Criterion 1',
    version = 1,
    window = 30,
    require = [
        (hep_a_igm_ab, ),
        (jaundice, alt_2x, ast_2x),
        ]
    )
 
acute_hep_a = DiseaseDefinition(
    name = 'Acute Hepatitis A',
    criteria = [hep_a_crit_1,],
    icd9s = DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = ['1742-6', '1920-8', '22314-9', '14212-5', '16128-1'],
    lab_days_before = 30,
    lab_days_after = 30,
    )



#===============================================================================
#
# Hepatitis B
#
#-------------------------------------------------------------------------------


'''
Acute Hepatitis B definitions:
1)  (jaundice OR alt_5x OR ast_5x) 
    AND hep_b_igm_ab 
    WITHIN 14 days
2)  (jaundice OR alt_5x OR ast_5x) 
    AND (total_bilirubin_high OR high_calc_bilirubin)
    AND (hep_b_surface OR hep_b_viral_dna)
    WITHIN 21 days
    AND NOT (chronic_hep_b OR hep_b_surface OR hep_b_viral_dna) EVER IN PAST
3)  hep_b_surface
    AND NOT (hep_b_surface OR hep_b_viral_dna OR jaundice) EVER IN PAST
'''
    
hep_b_1 = DiseaseCriterion(
    name = 'Acute Hepatitis B Criterion 1',
    version = 1,
    window = 14, # days
    require = [
        (jaundice, alt_5x, ast_5x),
        (hep_b_igm_ab,),
        ]
    )

hep_b_2 = DiseaseCriterion(
    name = 'Acute Hepatitis B Criterion 2',
    version = 1,
    window = 21, # days
    require = [
        (jaundice, alt_5x, ast_5x),
        (total_bilirubin_high, high_calc_bilirubin),
        (hep_b_surface, hep_b_viral_dna),
    ],
    exclude = [
        (chronic_hep_b,),
        ],
    exclude_past = [
        (chronic_hep_b, hep_b_surface, hep_b_viral_dna),
        ],
    )

hep_b_3 = DiseaseCriterion(
    name = 'Hepatitis B Component 3',
    version = 1,
    window = 1, # Not applicable, since only one primary event
    require = [
        (hep_b_surface,),
        ],
    require_past = [
        (no_hep_b_surface,),
        ],
    require_past_window = 365, # 1 year
    exclude = [
        (chronic_hep_b,),
        ],
    exclude_past = [
        (chronic_hep_b, hep_b_surface, hep_b_viral_dna),
        ],
    )


hep_b = DiseaseDefinition(
    name = 'Acute Hepatitis B',
    criteria = [hep_b_1, hep_b_2, hep_b_3],
    icd9s = DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = [
        '1742-6', 
        '1920-8', 
        '31204-1', 
        '5195-3',
        '13954-3',
        '13126-8',
        '5009-6',
        '16943-2',
        '14212-5',
        '22314-9',
        '16128-1',
        ],
    lab_days_before = 14,
    lab_days_after = 14,
    )

#hep_c_1 = DiseaseCriterion(
#    name = 'Acute Hepatitis C Criterion 1',
#    version = 1,
#    require = [
#        ()
#        ],
#    )

