'''
                                  ESP Health
                         Notifiable Diseases Framework
                              Disease Defintions


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from ESP.nodis.models import ComplexEventPattern
from ESP.nodis.models import MultipleEventPattern
from ESP.nodis.models import TuberculosisDefC
from ESP.nodis.models import Condition
from ESP.hef.defaults import diabetes_type_1_dx


#===============================================================================
#
# Chlamydia
#
#-------------------------------------------------------------------------------

chlamydia_1 = ComplexEventPattern(
    name = 'Chlamydia pattern #1',
    patterns = [
        'lx--chlamydia--positive',
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
        'lx--gonorrhea--positive',
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
        'dx--jaundice', 
        'lx--alt--ratio--2.0', 
        'lx--ast--ratio--2.0', 
        ],
    operator = 'or',
    )

hep_a_1 = ComplexEventPattern(
    name = 'Acute Hepatitis A Definition 1',
    patterns = [
        jaundice_or_blood_2x, # (#1 or #2 or #3)
        'lx--hep_a_igm_antibody--positive',       # AND #4
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
    patterns = ['dx--jaundice', 'lx--alt--ratio--5.0', 'lx--ast--ratio--5.0',],
    operator = 'or',
    )
    
hep_b_1 = ComplexEventPattern(
    name = 'Acute Hepatitis B Definition 1',
    patterns = [jaundice_or_blood_5x, 'lx--hep_b_igm_antibody--positive'],
    operator = 'and',
    )

bilirubin = ComplexEventPattern(
    patterns = ['lx--bilirubin_total--threshold--1.5', 'lx--bilirubin_calculated--threshold--1.5'],
    operator = 'or'
    )

hep_b_pos_lab = ComplexEventPattern(
    patterns = ['lx--hep_b_surface_antigen--positive', 'lx--hep_b_viral_dna--positive'],
    operator = 'or'
    )

hep_b_2 = ComplexEventPattern(
    name = 'Acute Hepatitis B definition 2',
    patterns = [jaundice_or_blood_5x, bilirubin, hep_b_pos_lab],
    operator = 'and',
    exclude = ['dx--chronic_hep_b'],
    exclude_past = ['dx--chronic_hep_b', 'lx--hep_b_surface_antigen--positive', 'lx--hep_b_viral_dna--positive'],
    )

hep_b_3 = ComplexEventPattern(
    name = 'Hepatitis B definition 3',
    patterns = ['lx--hep_b_surface_antigen--positive'],
    operator = 'and', # Meaningless w/ only one pattern
    require_before = ['lx--hep_b_surface_antigen--negative'],
    require_before_window = 365, # 1 year
    exclude = ['dx--chronic_hep_b'],
    exclude_past = ['dx--chronic_hep_b', 'lx--hep_b_surface_antigen--positive', 'lx--hep_b_viral_dna--positive'],
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
        'dx--jaundice',
        'lx--alt--threshold--400.0',
        ],
    operator = 'or'
    )
    
no_hep_b_surf = ComplexEventPattern(
    patterns = [
        'lx--hep_b_surface_antigen--negative',
        ],
    operator = 'and',
    exclude = [
        'lx--hep_b_igm_antibody--order',
        ]
    )

no_hep_a = ComplexEventPattern(
    patterns = [
        'lx--hep_a_igm_antibody--negative',
        'lx--hep_a_total_antibody--negative', # Hep A total antibodies
        ],
    operator = 'or'
    )

no_hep_b = ComplexEventPattern(
    patterns = [
        'lx--hep_b_igm_antibody--negative',
        'lx--hep_b_core_antibody--negative',
        no_hep_b_surf,
        ],
    operator = 'or'
    )

hep_c_1 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (a)', # Name is optional, but desirable on top-level patterns
    patterns = [
        jaundice_alt400,    # (1 or 2)
        'lx--hep_c_elisa--positive',  # 3 positive
        no_hep_a,           # (7 negative or 11 negative)
        no_hep_b,           # (8 negative or 9 non-reactive)
        ],
    exclude = [
        'lx--hep_c_signal_cutoff--negative', # 4 positive (if done)
        'lx--hep_c_riba--negative',          # 5 positive (if done)
        'lx--hep_c_rna--negative',           # 6 positive (if done)
        ],
    exclude_past = [
        'lx--hep_c_elisa--positive',   # no prior positive 3 or 5 or 6
        'lx--hep_c_riba--positive',    # "
        'lx--hep_c_rna--positive',     # "
        'dx--chronic_hep_b', # no ICD9 (070.54 or 070.70) ever prior to this encounter
        ],
    operator = 'and',
    )

hep_c_2 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (b)',
    patterns = [
        jaundice_alt400,    # (1 or 2)
        'lx--hep_c_rna--positive',    # 6 positive
        no_hep_a,           # (7 negative or 11 negative)
        no_hep_b,           # (8 negative or 9 non-reactive)
        ],
    exclude = [
        'lx--hep_c_signal_cutoff--negative', # 4 positive (if done)
        'lx--hep_c_riba--negative',          # 5 positive (if done)
        ],
    exclude_past = [
        'lx--hep_c_elisa--positive',   # no prior positive 3 or 5 or 6
        'lx--hep_c_riba--positive',    # "
        'lx--hep_c_rna--positive',     # "
        'dx--chronic_hep_b', # no ICD9 (070.54 or 070.70) ever prior to this encounter
        ],
    operator = 'and',
    )

hep_c_3 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (c)',
    patterns = ['lx--hep_c_rna--positive'],
    require_before = ['lx--hep_c_elisa--negative'],
    require_before_window = 365,
    operator = 'and',
    )

hep_c_4 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern (d)',
    patterns = ['lx--hep_c_elisa--positive'],
    require_before = ['lx--hep_c_elisa--negative'],
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


lyme_elisa_eia = ComplexEventPattern(
    patterns = ['lx--lyme_elisa--positive', 'lx--lyme_igg_eia--positive', 'lx--lyme_igm_eia--positive'],
    operator = 'or'
    )

lyme_elisa_eia_order = ComplexEventPattern(
    patterns = ['lx--lyme_elisa--order', 'lx--lyme_igg_eia--order', 'lx--lyme_igm_eia--order'],
    operator = 'or'
    )

lyme_diag_ab = ComplexEventPattern(
    patterns = ['dx--lyme', 'rx--doxycycline', 'rx--lyme_other_antibiotics'],
    operator = 'or'
    )

doxy_lyme_ab = ComplexEventPattern(
    patterns = ['rx--doxycycline', 'rx--lyme_other_antibiotics'],
    operator = 'or'
    )

lyme_1 = ComplexEventPattern(
    name = 'Lyme Disease definition 1',
    patterns = [lyme_elisa_eia, lyme_diag_ab],
    operator = 'and',
    )

lyme_2 = ComplexEventPattern(
    name = 'Lyme Disease definition 2',
    patterns = ['dx--lyme', doxy_lyme_ab],
    operator = 'and'
    )

lyme_3 = ComplexEventPattern(
    name = 'Lyme Disease Definition 3',
    patterns = ['dx--rash', 'rx--doxycycline', lyme_elisa_eia_order],
    operator = 'and'
    )

lyme_4 = ComplexEventPattern(
    patterns = ['lx--lyme_igg_wb--positive', 'lx--lyme_igm_wb--positive', 'lx--lyme_pcr--positive'],
    operator = 'or',
    )



lyme = Condition(
    name = 'lyme',
    patterns = [
        (lyme_1, 30),
        (lyme_2, 14),
        (lyme_3, 30),
        (lyme_4, 1),
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
    patterns = ['lx--chlamydia--positive', 'lx--gonorrhea--positive'],
    operator = 'or'
    )

pid_1 = ComplexEventPattern(
    patterns = [chlam_or_gon, 'dx--pelvic_inflamatory_disease'],
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
        'rx--pyrazinamide',
        ],
    operator = 'or'
    )

tb_diagnosis_before = ComplexEventPattern(
    patterns = ['lx--tuberculosis--order'],
    operator = 'and', # n/a
    require_before = ['dx--tuberculosis'],
    require_before_window = 14,
    )

tb_diagnosis_after = ComplexEventPattern(
    patterns = ['lx--tuberculosis--order'],
    operator = 'and', # n/a
    require_after = ['dx--tuberculosis'],
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
        'rx--penicillin_g',
        'rx--doxycycline_7_days',
        'rx--ceftriaxone_1g_2g',
        ],
    operator = 'or',
    )

# Definition (1)
syphilis_diagnosis_or_meds = ComplexEventPattern(
    patterns=[
        'dx--syphilis',
        syphilis_meds,
    ],
    operator = 'and',
    )

syphilis_tests = ComplexEventPattern(
    patterns = [
        'lx--syphilis_rpr--positive',
        'lx--syphilis_vdrl_serum--positive',
        ],
    operator = 'or',
    require_ever = [
        # Operator is 'OR'
        'lx--syphilis_tppa--positive',
        'lx--syphilis_fta_abs--positive',
        'lx--syphilis_tp_igg--positive',
        ],
    )

syphilis_vdrl_csf = ComplexEventPattern(
    patterns = ['lx--syphilis_vdrl_csf--positive'],
    operator = 'and' # n/a
    )


syphilis = Condition(
    name = 'syphilis',
    patterns = [
        (syphilis_diagnosis_or_meds, 14),
        (syphilis_tests, 14),
        (syphilis_vdrl_csf, 1), 
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
        'lx--giardiasis_antigen--positive',
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

gdm_fasting_glucose = ComplexEventPattern(
    name = 'GDM based on fasting glucose',
    patterns = ['lx--glucose_fasting--threshold--126.0',],
    operator = 'or',
    require_timespan = ['pregnancy']
    )

gdm_ogtt50 = ComplexEventPattern(
    name = 'GDM based on OGTT50',
    patterns = [
        'lx--ogtt50_1hr--threshold--190.0',
        'lx--ogtt50_random--threshold--190.0',
        ],
    operator = 'or',
    require_timespan = ['pregnancy']
    )

ogtt75_multi_intrapartum = MultipleEventPattern(
    events = [
        'lx--ogtt75_fasting--threshold--95.0',
        'lx--ogtt75_fasting_urine--positive',
        'lx--ogtt75_30min--threshold--200.0',
        'lx--ogtt75_1hr--threshold--180.0',
        'lx--ogtt75_90min--threshold--180.0',
        'lx--ogtt75_2hr--threshold--155.0',
        ],
    count = 2,
    require_timespan = ['pregnancy']
    )

ogtt75_multi = MultipleEventPattern(
    events = [
        'lx--ogtt75_fasting--threshold--126.0',
        'lx--ogtt75_30min--threshold--200.0',
        'lx--ogtt75_30min--threshold--200.0',
        'lx--ogtt75_90min--threshold--200.0',
        'lx--ogtt75_2hr--threshold--200.0',
        ],
    count = 2,
    require_timespan = ['pregnancy']
    )

gdm_ogtt75 = ComplexEventPattern(
    name = 'GDM based on OGTT75',
    patterns = [ogtt75_multi_intrapartum],
    operator = 'or',
    )

ogtt100_multi_intrapartum = MultipleEventPattern(
    events = [
        'lx--ogtt100_fasting_urine--positive',
        'lx--ogtt100_fasting--threshold--95.0',
        'lx--ogtt100_30min--threshold--200.0',
        'lx--ogtt100_1hr--threshold--180.0',
        'lx--ogtt100_90min--threshold--180.0',
        'lx--ogtt100_2hr--threshold--155.0',
        'lx--ogtt100_3hr--threshold--140.0',
        'lx--ogtt100_4hr--threshold--140.0',
        'lx--ogtt100_5hr--threshold--140.0',
        ],
    count = 2,
    require_timespan = ['pregnancy']
    )

gdm_ogtt100 = ComplexEventPattern(
    name = 'GDM based on OGTT100',
    patterns = [ogtt100_multi_intrapartum],
    operator = 'or',
    )

lancets_or_test_strips = ComplexEventPattern(
    name = 'Prescription for lancets or test strips',
    patterns = ['rx--lancets', 'rx--test_strips'],
    operator = 'or',
    )

gdm_lancets = ComplexEventPattern(
    name = 'GDM based on diagnosis and lancets/test strips prescription',
    patterns = ['dx--gestational_diabetes', lancets_or_test_strips],
    operator = 'and',
    require_timespan = ['pregnancy']
    )

gdm = Condition(
    name = 'gdm',
    patterns = [
        (gdm_lancets, 14),
        (gdm_fasting_glucose, 14),
        (gdm_ogtt50, 14),
        (gdm_ogtt75, 14),
        (gdm_ogtt100, 14),
        ],
    recur_after = 365, # New cases after 365 days
    test_name_search = ['glucose', 'OGTT'],
    )


#===============================================================================
#
# Pertussis
#
#-------------------------------------------------------------------------------


pertussis_diagnosis_or_lab_order = ComplexEventPattern(
    name = 'Positive result for Pertussis lab',
    patterns = [
        'dx--pertussis',
        'lx--pertussis_pcr--order',
        'lx--pertussis_culture--order',
        'lx--pertussis_serology--order',
        ],
    operator = 'or',
    )

pertussis_1 = ComplexEventPattern(
    #(ICD9 for pertussis or lab order for a pertussis test) and antibiotic prescription within 7 day window
    name = 'Pertussis definition 1',
    patterns = ['rx--pertussis', pertussis_diagnosis_or_lab_order],
    operator = 'and',
    )

pertussis_2 = ComplexEventPattern(
    # Positive culture or PCR for pertussis
    name = 'Pertussis definition 2',
    patterns = ['lx--pertussis_pcr--positive', 'lx--pertussis_culture--positive'],
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

diabetes_all_dx_twice = ComplexEventPattern(
    # A dm dx event now, plus a dm dx event in the past = 2 dm dx events
    patterns = ['dx--diabetes_all_types'],
    operator = 'and',
    require_before = ['dx--diabetes_all_types'],
    )

diabetes_type_2_dx_twice = ComplexEventPattern(
    # A dm dx event now, plus a dm dx event in the past = 2 dm dx events
    patterns = ['dx--diabetes_type_2'],
    operator = 'and',
    require_before = ['dx--diabetes_type_2'],
    )

insulin_outside_pregnancy = ComplexEventPattern(
    patterns = ['rx--insulin'],
    operator = 'and',
    exclude_timespan = ['pregnancy'],
    )


diabetes_both_types = ComplexEventPattern(
    name = 'diabetes_both_types',
    # FIXME: Incomplete pattern list!!!
    patterns = [
        'lx--a1c--threshold--6.5',
        'lx--glucose_fasting--threshold--126.0',
        'rx--diabetes',
        insulin_outside_pregnancy,
        diabetes_all_dx_twice,
        ],
    operator = 'or',
    )

diabetes_type_1_def_past_insulin = ComplexEventPattern(
    patterns = [
        diabetes_both_types,
        ],
    require_before = ['rx--insulin'],
    require_before_window = 365,
    require_ever = ['dx--diabetes_type_1'],
    operator = 'and',
    )

diabetes_type_1_def_future_insulin = ComplexEventPattern(
    patterns = [
        diabetes_both_types,
        ],
    require_after = ['rx--insulin'],
    require_after_window = 365,
    require_ever = ['dx--diabetes_type_1'],
    operator = 'and',
    )

diabetes_type_1 = Condition(
    name = 'diabetes_type_1',
    patterns = [
        (diabetes_type_1_def_past_insulin, 1),
        (diabetes_type_1_def_future_insulin, 1),
        ],
    recur_after = -1, # Does not recur
    test_name_search = [],
    )

diabetes_type_2_dx = ComplexEventPattern(
    patterns = [
        diabetes_both_types,
        diabetes_type_2_dx_twice,
        ],
    operator = 'and',
    )

diabetes_type_2_rx = ComplexEventPattern(
    patterns = [
        diabetes_both_types,
        'rx--diabetes'
        ],
    operator = 'and',
    )


diabetes_type_2 = Condition(
    name = 'diabetes_type_2',
    patterns = [
        (diabetes_type_2_dx, 1),
        (diabetes_type_2_rx, 1),
        ],
    recur_after = -1, # Does not recur
    test_name_search = [],
    )

