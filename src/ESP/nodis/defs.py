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
from ESP.nodis.models import MultipleEventPattern
from ESP.nodis.models import TuberculosisDefC
from ESP.nodis.models import Condition
from django.db import connection


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
    require_before = ['hep_b_surface_neg'],
    require_before_window = 365, # 1 year
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
    require_before = ['hep_c_elisa_neg'],
    require_before_window = 365,
    operator = 'and',
    )

hep_c_4 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (d)',
    patterns = ['hep_c_elisa_pos'],
    require_before = ['hep_c_elisa_neg'],
    require_before_window = 365,
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
    )

#
# Active Tuberculosis (TB)
#

# Definition (a)
tb_a = ComplexEventPattern(
    patterns = [
        'pyrazinamide',
        ],
    operator = 'or'
    )

tb_diagnosis_before = ComplexEventPattern(
    patterns = ['tb_lab_order'],
    operator = 'and', # n/a
    require_before = ['tb_diagnosis'],
    require_before_window = 14,
    )

tb_diagnosis_after = ComplexEventPattern(
    patterns = ['tb_lab_order'],
    operator = 'and', # n/a
    require_after = ['tb_diagnosis'],
    require_after_window = 60,
    )

# Definition (b)
tb_b = ComplexEventPattern(
    patterns = [
        tb_diagnosis_before,
        tb_diagnosis_after,
        ],
    operator = 'or',
    )

tb_c = TuberculosisDefC()

tb = Condition(
    name = 'tb',
    patterns = [
        (tb_a, 1),
        (tb_b, 1),
        (tb_c, 1),
        ],
    recur_after = -1, # Never
    test_name_search = ['myco', 'afb', 'tb', 'tuber',], 
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

syphilis_tests = ComplexEventPattern(
    patterns = ['rpr_pos',],
    operator = 'and', # n/a
    require_ever = [
        # Operator is 'OR'
        'ttpa_pos',
        'fta_abs_pos',
        ],
    )


syphilis = Condition(
    name = 'syphilis',
    patterns = [
        (syphilis_diagnosis_or_meds, 14),
        (syphilis_tests, 14),
        ],
    recur_after = -1, # Never
    test_name_search = ['syph', 'rpr', 'vdrl', 'tp','fta'],
    )

#===============================================================================
#
# Giardiasis
#
#-------------------------------------------------------------------------------

giardiasis_1 = ComplexEventPattern(
    name = 'Giardiasis pattern #1',
    patterns = [
        'giardiasis_antigen_pos',
        ],
    operator = 'and',
    )

giardiasis = Condition(
    name = 'giardiasis',
    patterns = [(giardiasis_1, 0)],
    recur_after = 365, # New cases after 365 days
    test_name_search = ['giar', 'giard'],
    )




#===============================================================================
#
# Gestational Diabetes
#
#-------------------------------------------------------------------------------

#gdm_fasting_glucose = ComplexEventPattern(
#    name = 'GDM based on fasting glucose',
#    patterns = ['glucose_fasting_pos',],
#    operator = 'or',
#    require_timespan = ['pregnancy']
#    )
#
#gdm_ogtt50 = ComplexEventPattern(
#    name = 'GDM based on OGTT50',
#    patterns = [
#        'ogtt50_1hr_pos',
#        'ogtt50_fasting_pos',
#        'ogtt50_random_pos',
#        ],
#    operator = 'or',
#    require_timespan = ['pregnancy']
#    )
#
#ogtt75_multi = MultipleEventPattern(
#    events = [
#        'ogtt75_1hr_pos',
#        'ogtt75_2hr_pos',
#        'ogtt75_30m_pos',
#        'ogtt75_90m_pos',
#        'ogtt75_fasting_pos',
#        'ogtt75_fasting_urine_pos',
#        ],
#    count = 2,
#    )
#
#gdm_ogtt75 = ComplexEventPattern(
#    name = 'GDM based on OGTT75',
#    patterns = [ogtt75_multi],
#    operator = 'or',
#    require_timespan = ['pregnancy']
#    )
#
#ogtt100_multi = MultipleEventPattern(
#    events = [
#        'ogtt100_1hr_pos',
#        'ogtt100_2hr_pos',
#        'ogtt100_30m_pos',
#        'ogtt100_90m_pos',
#        'ogtt100_fasting_pos',
#        'ogtt100_fasting_urine_pos',
#        ],
#    count = 2,
#    )
#
#gdm_ogtt100 = ComplexEventPattern(
#    name = 'GDM based on OGTT100',
#    patterns = [ogtt100_multi],
#    operator = 'or',
#    require_timespan = ['pregnancy']
#    )
#
#lancets_or_test_strips = ComplexEventPattern(
#    name = 'Prescription for lancets or test strips',
#    patterns = ['lancets_rx', 'test_strips_rx'],
#    operator = 'or',
#    )
#
#gdm_lancets = ComplexEventPattern(
#    name = 'GDM based on diagnosis and lancets/test strips prescription',
#    patterns = ['gdm_diagnosis', lancets_or_test_strips],
#    operator = 'and',
#    require_timespan = ['pregnancy']
#    )
#
#gdm = Condition(
#    name = 'gdm',
#    patterns = [
#        (gdm_lancets, 14),
#        (gdm_fasting_glucose, 14),
#        (gdm_ogtt50, 14),
#        (gdm_ogtt75, 14),
#        (gdm_ogtt100, 14),
#        ],
#    recur_after = 365, # New cases after 365 days
#    test_name_search = ['glucose'],
#    )


#===============================================================================
#
# Pertussis
#
#-------------------------------------------------------------------------------


pertussis_diagnosis_or_lab_order = ComplexEventPattern(
    name = 'Positive result for Pertussis lab',
    patterns = [
        'pertussis_diagnosis',
        'pertussis_pcr_order',
        'pertussis_culture_order',
        'pertussis_serology_order',
        ],
    operator = 'or',
    )

pertussis_1 = ComplexEventPattern(
    #(ICD9 for pertussis or lab order for a pertussis test) and antibiotic prescription within 7 day window
    name = 'Pertussis definition 1',
    patterns = ['pertussis_rx', pertussis_diagnosis_or_lab_order],
    operator = 'and',
    )

pertussis_2 = ComplexEventPattern(
    # Positive culture or PCR for pertussis
    name = 'Pertussis definition 2',
    patterns = ['pertussis_pcr_pos', 'pertussis_culture_pos'],
    operator = 'or', # irrelevant for single pattern
    )

pertussis = Condition(
    name = 'pertussis',
    patterns = [
        (pertussis_1, 7),
        (pertussis_2, 0), # Single pattern match requires no date window
        ],
    recur_after = -1, # FIXME: Can Pertussis recur?
    test_name_search = ['pertussis'],
    )
