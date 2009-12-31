'''
                                  ESP Health
                         Notifiable Diseases Framework
                              Disease Defintions


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from ESP.emr.models import Patient
from ESP.hef import events # Load events
from ESP.hef.core import BaseHeuristic
from ESP.nodis.models import ComplexEventPattern
from ESP.nodis.models import Condition
from ESP.settings import DEFAULT_REPORTABLE_ICD9S
from django.db import connection
import pprint


GONORRHEA_LOINCS = ['691-6', '23908-7', '24111-7', '36902-5'] 
CHLAMYDIA_LOINCS = ['4993-2', '6349-5', '16601-7', '20993-2', '21613-5', '36902-5', ] 



#===============================================================================
#
# Chlamydia
#
#-------------------------------------------------------------------------------

chlamydia_1 = ComplexEventPattern(
    name = 'Chlamydia pattern #1',
    patterns = [
        'chlamydia_pos',
        ],
    operator = 'and',
    )

chlamydia = Condition(
    name = 'chlamydia',
    patterns = [(chlamydia_1, 0)],
    recur_after = 28, # New cases after 28 days
    test_name_search = ['chla'],
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
#    # Report both Chlamydia and Gonorrhea labs
#    lab_days_before = 30,
    )



#===============================================================================
#
# Gonorrhea
#
#-------------------------------------------------------------------------------

gonorrhea_1 = ComplexEventPattern(
    name = 'Gonorrhea pattern #1',
    patterns = [
        'gonorrhea_pos',
        ],
    operator = 'and',
    )

gonorrhea = Condition(
    name = 'gonorrhea',
    patterns = [(gonorrhea_1, 1)],
    recur_after = 28, # New cases after 28 days
    test_name_search = ['gon', 'gc'],
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
#    fever = True,
#    lab_days_before = 28,
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
    )


#===============================================================================
#
# Acute Hepatitis A
#
#-------------------------------------------------------------------------------

jaundice_or_blood_2x = ComplexEventPattern(
    patterns = [
        'jaundice', 
        'alt_2x', 
        'ast_2x',
        ],
    operator = 'or',
    )

hep_a_1 = ComplexEventPattern(
    name = 'Acute Hepatitis A Definition 1',
    patterns = [
        jaundice_or_blood_2x, # (#1 or #2 or #3)
        'hep_a_igm_pos',       # AND #4
        ],
    operator = 'and',
    )
 
acute_hep_a = Condition(
    name = 'acute_hep_a',
    patterns = [(hep_a_1, 30)],
    recur_after = -1, # Never recur
    test_name_search = ['hep', 'alt', 'ast', 'tbil', 'bili'],
#    icd9s = DEFAULT_REPORTABLE_ICD9S,
#    icd9_days_before = 14,
#    fever = True,
#    lab_days_before = 30,
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


jaundice_or_blood_5x = ComplexEventPattern(
    patterns = ['jaundice', 'alt_5x', 'ast_5x',],
    operator = 'or',
    )
    
hep_b_1 = ComplexEventPattern(
    name = 'Acute Hepatitis B Definition 1',
    patterns = [jaundice_or_blood_5x, 'hep_b_igm_pos'],
    operator = 'and',
    )

bilirubin = ComplexEventPattern(
    patterns = ['total_bilirubin_high_pos', 'high_calc_bilirubin'],
    operator = 'or'
    )

hep_b_lab_pos = ComplexEventPattern(
    patterns = ['hep_b_surface_pos', 'hep_b_viral_dna_pos'],
    operator = 'or'
    )

hep_b_2 = ComplexEventPattern(
    name = 'Acute Hepatitis B definition 2',
    patterns = [jaundice_or_blood_5x, bilirubin, hep_b_lab_pos],
    operator = 'and',
    exclude = ['chronic_hep_b'],
    exclude_past = ['chronic_hep_b', 'hep_b_surface_pos', 'hep_b_viral_dna_pos'],
    )

hep_b_3 = ComplexEventPattern(
    name = 'Hepatitis B definition 3',
    patterns = ['hep_b_surface_pos'],
    operator = 'and', # Meaningless w/ only one pattern
    require_past = ['hep_b_surface_neg'],
    require_past_window = 365, # 1 year
    exclude = ['chronic_hep_b'],
    exclude_past = ['chronic_hep_b', 'hep_b_surface_pos', 'hep_b_viral_dna_pos'],
    )

hep_b = Condition(
    name = 'acute_hep_b',
    patterns = [
        (hep_b_1, 14),
        (hep_b_2, 14),
        (hep_b_3, 1), # Single present event -- match window is meaningless
    ],
    recur_after = -1, # Never recur
    test_name_search = ['hep', 'alt', 'ast', 'tbil', 'bili', 'hb', 'core',],
#    icd9s = DEFAULT_REPORTABLE_ICD9S,
#    icd9_days_before = 14,
#    fever = True,
#    lab_days_before = 14,
    )


#===============================================================================
#
# Acute Hepatitis C
#
#-------------------------------------------------------------------------------

jaundice_alt400 = ComplexEventPattern(
    patterns = [
        'jaundice',
        'alt_400',
        ],
    operator = 'or'
    )
    
no_hep_b_surf = ComplexEventPattern(
    patterns = [
        'hep_b_surface_neg',
        ],
    operator = 'and',
    exclude = [
        'hep_b_igm_order',
        ]
    )

no_hep_a = ComplexEventPattern(
    patterns = [
        'hep_a_igm_neg',
        'hav_tot_neg', # Hep A total antibodies
        ],
    operator = 'or'
    )

no_hep_b = ComplexEventPattern(
    patterns = [
        'hep_b_igm_neg',
        'hep_b_core_neg',
        no_hep_b_surf,
        ],
    operator = 'or'
    )

hep_c_1 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (a)', # Name is optional, but desirable on top-level patterns
    patterns = [
        jaundice_alt400,    # (1 or 2)
        'hep_c_elisa_pos',  # 3 positive
        no_hep_a,           # (7 negative or 11 negative)
        no_hep_b,           # (8 negative or 9 non-reactive)
        ],
    exclude = [
        'hep_c_signal_cutoff_neg', # 4 positive (if done)
        'hep_c_riba_neg',          # 5 positive (if done)
        'hep_c_rna_neg',           # 6 positive (if done)
        ],
    exclude_past = [
        'hep_c_elisa_pos',   # no prior positive 3 or 5 or 6
        'hep_c_riba_pos',    # "
        'hep_c_rna_pos',     # "
        'chronic_hep_b', # no ICD9 (070.54 or 070.70) ever prior to this encounter
        ],
    operator = 'and',
    )

hep_c_2 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (b)',
    patterns = [
        jaundice_alt400,    # (1 or 2)
        'hep_c_rna_pos',    # 6 positive
        no_hep_a,           # (7 negative or 11 negative)
        no_hep_b,           # (8 negative or 9 non-reactive)
        ],
    exclude = [
        'hep_c_signal_cutoff_neg', # 4 positive (if done)
        'hep_c_riba_neg',          # 5 positive (if done)
        ],
    exclude_past = [
        'hep_c_elisa_pos',   # no prior positive 3 or 5 or 6
        'hep_c_riba_pos',    # "
        'hep_c_rna_pos',     # "
        'chronic_hep_b', # no ICD9 (070.54 or 070.70) ever prior to this encounter
        ],
    operator = 'and',
    )

hep_c_3 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (c)',
    patterns = ['hep_c_rna_pos'],
    require_past = ['hep_c_elisa_neg'],
    require_past_window = 365,
    operator = 'and',
    )

hep_c_4 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (d)',
    patterns = ['hep_c_elisa_pos'],
    require_past = ['hep_c_elisa_neg'],
    require_past_window = 365,
    operator = 'and',
    )


hep_c = Condition(
    name = 'acute_hep_c',
    patterns = [
            (hep_c_1, 28),
            (hep_c_2, 28),
            (hep_c_3, 1), # Single event -- time window not meaningful
            (hep_c_4, 1), # Single event -- time window not meaningful
            ],
    recur_after = -1, # Never recur
    test_name_search = ['hep', 'alt', 'ast', 'tbil', 'bili', 'hc'],
#    icd9s = DEFAULT_REPORTABLE_ICD9S,
#    icd9_days_before = 14,
#    fever = True,
#    lab_days_before = 28,
    )



#===============================================================================
#
# Lyme Disease
#
#-------------------------------------------------------------------------------


lyme_test_pos = ComplexEventPattern(
    patterns = ['lyme_elisa_pos', 'lyme_igg_pos', 'lyme_igm_pos', 'lyme_pcr_pos'],
    operator = 'or'
    )

lyme_diag_ab = ComplexEventPattern(
    patterns = ['lyme_diagnosis', 'doxycycline', 'lyme_other_antibiotics'],
    operator = 'or'
    )

doxy_lyme_ab = ComplexEventPattern(
    patterns = ['doxycycline', 'lyme_other_antibiotics'],
    operator = 'or'
    )

lyme_1 = ComplexEventPattern(
    name = 'Lyme Disease definition 1',
    patterns = [lyme_test_pos, lyme_diag_ab],
    operator = 'and',
    )

lyme_2 = ComplexEventPattern(
    name = 'Lyme Disease definition 2',
    patterns = ['lyme_diagnosis', doxy_lyme_ab],
    operator = 'and'
    )

lyme_3 = ComplexEventPattern(
    name = 'Lyme Disease Definition 3',
    patterns = ['rash', 'lyme_elisa_order', 'doxycycline'],
    operator = 'and'
    )


lyme = Condition(
    name = 'lyme',
    patterns = [
        (lyme_1, 30),
        (lyme_2, 14),
        (lyme_3, 14),
        ],
    recur_after = 365, # 1 year
    test_name_search = ['lyme'],
#    icd9s = [
#        '782.1',
#        '711.8',
#        '320.7',
#        '351.0',
#        '723.4',
#        '724.4',
#        '422.0',
#        '426.0',
#        '426.12',
#        '426.13',
#        '780.6',
#        ],
#    icd9_days_before = 30,
#    fever = True,
#    lab_days_before = 30,
#    med_names = [
#        'doxycycline',
#        'amoxicillin',
#        'cefuroxime',
#        'ceftriaxone',
#        'cefotaxime',
#        ],
#    med_days_before = 30,
    )
    

#===============================================================================
#
# Pelvic Inflammatory Disease (PID)
#
#-------------------------------------------------------------------------------


chlam_or_gon = ComplexEventPattern(
    patterns = ['chlamydia_pos', 'gonorrhea_pos'],
    operator = 'or'
    )

pid_1 = ComplexEventPattern(
    patterns = [chlam_or_gon, 'pid_diagnosis'],
    operator = 'and'
    )


pid = Condition(
    name = 'pid',
    patterns = [
        (pid_1, 28),
        ],
    recur_after = 28, # 1 year
    test_name_search = ['chlam', 'gon', 'gc'],
#    icd9s = [
#        '614.0',
#        '614.2',
#        '614.3',
#        '614.5',
#        '614.9',
#        '099.56',
#        ],
#    icd9_days_before = 30,
#    fever = False,
#    lab_days_before = 30,
#    med_names = [
#        'ampicillin-sulbactam',
#        'amoxicillin-clavulinic acid',
#        'clindamycin',
#		'levofloxacin',
#		'ciprofloxacin',
#		'ofloxacin',
#		'cefotetan',
#		'cefoxitin',
#		'ceftriaxone',
#		'cefotaxime',
#		'cefitizoxine',
#		'doxycycline',
#		'gentamicin',
#		'metronidazole',
#		'azithromycin',
#        ],
#    med_days_before = 30,
    )

#
# Active Tuberculosis (TB)
#

tb_1 = ComplexEventPattern(
    patterns = ['tb_meds'],
    operator = 'and'
    )

tb = Condition(
    name = 'tb',
    patterns = [
        (tb_1, 1),
        ],
    recur_after = -1, # Never
    test_name_search = ['myco', 'afb', 'tb', 'tuber',], 
#    icd9s = [
#        '786.50',
#        '786.51',
#        '786.52',
#        '786.53',
#        '786.54',
#        '786.55',
#        '786.56',
#        '786.57',
#        '786.58',
#        '786.59',
#        '783.2',
#        '783.21',
#        '786.2',
#        '795.5',
#        ],
#    icd9_days_before = 30,
#    fever = True,
#    lab_days_before = 30,
#    med_names = [
#        'Pyrazinamide',
#        'PZA',
#        'RIFAMPIN',
#        'RIFAMATE',
#        'Ethambutol',
#        'Rifabutin',
#        'Rifapentine',
#        'Streptomycin',
#        'Para-aminosalicyclic acid',
#        'Kanamycin',
#        'Capreomycin',
#        'Cycloserine',
#        'Ethionamide',
#        'Levofloxacin',
#        'Ciprofloxacin',
#        'Moxifloxacin',
#        'Gatifloxacin',
#        'Azithromycin',
#        ],
#    med_days_before = 30,
    )


#===============================================================================
#
# Syphilis
#
#-------------------------------------------------------------------------------

syphilis_meds = ComplexEventPattern(
    patterns = [
        'penicillin_g',
        'doxycycline_7_days',
        'ceftriaxone_1g',
        ],
    operator = 'or',
    )

# Definition (1)
syphilis_diagnosis_or_meds = ComplexEventPattern(
    patterns=[
        'syphilis_diagnosis',
        syphilis_meds,
    ],
    operator = 'and',
    )

syphilis_secondary_tests = ComplexEventPattern(
    patterns = [
        'ttpa_pos',
        'fta_abs_pos',
        ],
    operator = 'or',
    )

syphilis_tests = ComplexEventPattern(
    patterns = [
        'rpr_pos',
        syphilis_secondary_tests,
        ],
    operator = 'and',
    )


syphilis = Condition(
    name = 'syphilis',
    patterns = [
        (syphilis_diagnosis_or_meds, 14),
        (syphilis_tests, 14),
        ],
    recur_after = -1, # Never
    test_name_search = ['syph', 'rpr', 'vdrl', 'tp','fta'],
#    # FIXME:  We need to add ability to express large ranges of ICD9s here - this is incomplete.
#    icd9s = [],
#    icd9_days_before = 28,
#    fever = True,
#    lab_days_before = 28,
#    med_names = [
#        'penicillin g',
#        'pen g',
#        'doxycycline',
#        'ceftriaxone',
#        ],
#    med_days_before = 28,
    )
