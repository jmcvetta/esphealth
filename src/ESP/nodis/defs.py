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
from ESP.nodis.core import DiseaseCriterion, DiseaseDefinition
from ESP.hef.events import jaundice
from ESP.hef.events import alt_2x, ast_2x, alt_5x, ast_5x
from ESP.hef.events import hep_b_igm_ab, hep_b_surface, hep_b_viral_dna, hep_b_igm_ab, chronic_hep_b, no_hep_b_surface
from ESP.hef.events import total_bilirubin_high, high_calc_bilirubin

class Foo:
    pass

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
    name = 'Hepatitis B',
    components = [hep_b_1, hep_b_2, hep_b_3],
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





#hep_c_1 = Foo(disease='Hepatitis C', version=1)
#hep_c_1.window = 14 # 14 day window
#hep_c_1.require(jaundice, alt_5x, ast_5x) # OR
#hep_c_1.require(hep_b_igm_ab)
#
#hep_c_2 = Foo(disease='Hepatitis C', version=1)
#hep_c_2.window = 21 # 21 day window
#hep_c_2.require = [
#    (jaundice, alt_5x, ast_5x),
#    (hep_b_surface, hep_b_viral_dna),
#    ]
#hep_c_2.exclude = []
#hep_c_2.exclude_past = [
#    (chronic_hep_b, hep_b_surface, hep_b_viral_dna),
#    ]
#
#
#
#
#
#
#
#
#
#
#
#
#    
#acute_hep_a_def = Foo(
#    name = 'Acute Hepatitis A',
#    queries = [HEP_A_SQL,],
#    time_window = 0,
#    icd9s = settings.DEFAULT_REPORTABLE_ICD9S,
#    icd9_days_before = 14,
#    icd9_days_after = 14,
#    fever = True,
#    lab_loinc_nums = ['1742-6', '1920-8', '22314-9', '14212-5', '16128-1'],
#    lab_days_before = 30,
#    lab_days_after = 30,
#    )
#
#acute_hep_b_def = Foo(
#    name = 'Acute Hepatitis B',
#    queries = [HEP_B_DEF_1_SQL, HEP_B_DEF_2_SQL, ], 
#    time_window = 365,
#    )
#
#
#chlamydia_def = Foo(
#    name = 'Chlamydia',
#    heuristic_name = 'chlamydia', 
#    time_window = 365,
#    icd9s = [
#        '788.7',
#        '099.40',
#        '597.80',
#        '780.6A',
#        '616.0',
#        '616.10',
#        '623.5',
#        '789.07',
#        '789.04',
#        '789.09',
#        '789.03',
#        '789.00',
#        ],
#    icd9_days_before = 14,
#    icd9_days_after = 14,
#    fever = True,
#    med_names = [
#        'azithromycin',
#        'levofloxacin',
#        'ofloxacin',
#        'ciprofloxacin',
#        'doxycycline',
#        'eryrthromycin',
#        'amoxicillin',
#        'EES',
#        ],
#    med_days_before = 7,
#    med_days_after = 14,
#    # Report both Chlamydia and Gonorrhea labs
#    lab_loinc_nums = CHLAMYDIA_LOINCS + GONORRHEA_LOINCS,
#    lab_days_before = 30,
#    lab_days_after = 30,
#    )
#
#gonorrhea_def = Foo(
#    name = 'Gonorrhea',
#    heuristic_name = 'gonorrhea', 
#    time_window = 365,
#    icd9s = [
#        '788.7',
#        '099.40',
#        '597.80',
#        '616.0',
#        '616.10',
#        '623.5',
#        '789.07',
#        '789.04',
#        '789.09',
#        '789.03',
#        '789.00',
#        ],
#    icd9_days_before = 14,
#    icd9_days_after = 14,
#    fever = True,
#    lab_loinc_nums = GONORRHEA_LOINCS, 
#    lab_days_before = 28,
#    lab_days_after = 28,
#    med_names = [
#        'amoxicillin',
#        'cefixime',
#        'cefotaxime',
#        'cefpodoxime',
#        'ceftizoxime',
#        'ceftriaxone',
#        'gatifloxacin',
#        'levofloxacin',
#        'ofloxacin',
#        'spectinomycin',
#        'moxifloxacin',
#        ],
#    med_days_before = 7,
#    med_days_after = 14
#    )
#
#

