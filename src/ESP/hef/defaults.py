'''
                                  ESP Health
                          Heuristic Events Framework
                        Default Lab & Event Definitions

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL
'''

from ESP.hef.models import AbstractLabTest
from ESP.hef.models import Heuristic
from ESP.hef.models import LabOrderHeuristic
from ESP.hef.models import LabResultAnyHeuristic
from ESP.hef.models import LabResultPositiveHeuristic
from ESP.hef.models import LabResultRatioHeuristic
from ESP.hef.models import LabResultFixedThresholdHeuristic
from ESP.hef.models import Icd9Query
from ESP.hef.models import DiagnosisHeuristic
from ESP.hef.models import PrescriptionHeuristic
from ESP.hef.models import Dose
from ESP.hef.models import ResultString
from ESP.hef.models import CalculatedBilirubinHeuristic

#-------------------------------------------------------------------------------
#
# Legacy Event Support
#
#-------------------------------------------------------------------------------

# All events created by previous version of HEF will be bound to this heuristic.
legacy_heuristic = Heuristic.objects.get_or_create(
    id = 0,
    #name = 'Legacy Heuristic',
    )[0]


#-------------------------------------------------------------------------------
#
# Doses
#
#-------------------------------------------------------------------------------

dose_1g = Dose.objects.get_or_create(quantity = 1, units = 'g')[0]
dose_2g = Dose.objects.get_or_create(quantity = 2, units = 'g')[0]


#-------------------------------------------------------------------------------
#
# Result Strings
#
#-------------------------------------------------------------------------------
ResultString.objects.get_or_create(
    value = 'reactiv',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'pos',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'detec',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'confirm',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'non',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'neg',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'not det',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'nr',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'indeterminate',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'not done',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'tnp',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )


#-------------------------------------------------------------------------------
#
# Gonorrhea
#
#-------------------------------------------------------------------------------

gonorrhea_test = AbstractLabTest.objects.get_or_create(
    name = 'gonorrhea',
    defaults = {
        'verbose_name': 'Gonorrhea test',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = gonorrhea_test,
    )


#-------------------------------------------------------------------------------
#
# Chlamydia
#
#-------------------------------------------------------------------------------

chlamydia_test = AbstractLabTest.objects.get_or_create(
    name = 'chlamydia',
    defaults = {
        'verbose_name': 'Chlamydia test',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = chlamydia_test,
    )


#-------------------------------------------------------------------------------
#
# ALT
#
#-------------------------------------------------------------------------------

alt = AbstractLabTest.objects.get_or_create(
    name = 'alt',
    defaults = {
        'verbose_name': 'Alanine Aminotransferase blood test',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = alt,
    )

LabResultRatioHeuristic.objects.get_or_create(
    test = alt,
    ratio = 2,
    )

LabResultRatioHeuristic.objects.get_or_create(
    test = alt,
    ratio = 5,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = alt,
    threshold = 400,
    )


#-------------------------------------------------------------------------------
#
# AST
#
#-------------------------------------------------------------------------------

ast = AbstractLabTest.objects.get_or_create(
    name = 'ast',
    defaults = {
        'verbose_name': 'Aspartate Aminotransferase blood test',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = ast,
    )

LabResultRatioHeuristic.objects.get_or_create(
    test = ast,
    ratio = 2,
    )

LabResultRatioHeuristic.objects.get_or_create(
    test = ast,
    ratio = 5,
    )


#-------------------------------------------------------------------------------
#
# Hepatitis A
#
#-------------------------------------------------------------------------------

hep_a_igm_antibody = AbstractLabTest.objects.get_or_create(
    name = 'hep_a_igm_antibody',
    defaults = {
        'verbose_name': 'Hepatitis A IgM antibody',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_a_igm_antibody,
    )

hep_a_tot_antibody = AbstractLabTest.objects.get_or_create(
    name = 'hep_a_total_antibody',
    defaults = {
        'verbose_name': 'Hepatitis A Total Antibodies',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_a_tot_antibody,
    )


#-------------------------------------------------------------------------------
#
# Hepatitis B
#
#-------------------------------------------------------------------------------

jaundice_dx = DiagnosisHeuristic.objects.get_or_create(
    name = 'jaundice'
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = jaundice_dx,
    icd9_exact = '782.4'
    )

chronic_hep_c = DiagnosisHeuristic.objects.get_or_create(
    name = 'chronic_hep_c'
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = chronic_hep_c,
    icd9_exact = '070.54',
    )

Icd9Query.objects.get_or_create(
    heuristic = chronic_hep_c,
    icd9_exact = '070.70',
    )

chronic_hep_b = DiagnosisHeuristic.objects.get_or_create(
    name = 'chronic_hep_b'
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = chronic_hep_b,
    icd9_exact = '070.32',
    )

hep_b_igm_antibody = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_igm_antibody',
    defaults = {
        'verbose_name': 'Hepatitis B core IgM antibody',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test = hep_b_igm_antibody,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_igm_antibody,
    )

hep_b_core_antibody = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_core_antibody',
    defaults = {
        'verbose_name': 'Hepatitis B core general antibody',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_core_antibody,
    )

hep_b_surface_antigen = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_surface_antigen',
    defaults = {
        'verbose_name': 'Hepatitis B surface antigen',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_surface_antigen,
    )


hep_b_e_antigen = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_e_antigen',
    defaults = {
        'verbose_name': 'Hepatitis B "e" antigen',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_e_antigen,
    )


# NOTE:  See note in Hepatitis B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm


hep_b_viral_dna = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_viral_dna',
    defaults = {
        'verbose_name': 'Hepatitis B viral DNA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_viral_dna,
    )

#-------------------------------------------------------------------------------
#
# Hepatitis E
#
#-------------------------------------------------------------------------------

hep_e_antibody = AbstractLabTest.objects.get_or_create(
    name = 'hep_e_antibody',
    defaults = {
        'verbose_name': 'Hepatitis E antibody',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_e_antibody,
    )

#-------------------------------------------------------------------------------
#
# Bilirubin
#
#-------------------------------------------------------------------------------

bilirubin_total = AbstractLabTest.objects.get_or_create(
    name = 'bilirubin_total',
    defaults = {
        'verbose_name': 'Bilirubin glucuronidated + bilirubin non-glucuronidated',
        }
    )[0]

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = bilirubin_total,
    threshold = 1.5,
    )
    
bilirubin_direct = AbstractLabTest.objects.get_or_create(
    name = 'bilirubin_direct',
    defaults = {
        'verbose_name': 'Bilirubin glucuronidated',
        }
    )[0]
    
bilirubin_indirect = AbstractLabTest.objects.get_or_create(
    name = 'bilirubin_indirect',
    defaults = {
        'verbose_name': 'Bilirubin non-glucuronidated',
        }
    )[0]

CalculatedBilirubinHeuristic.objects.get_or_create(
    threshold = 1.5,
    )[0]

    
#-------------------------------------------------------------------------------
#
# Hepatitis C
#
#-------------------------------------------------------------------------------

hep_c_signal_cutoff = AbstractLabTest.objects.get_or_create(
    name = 'hep_c_signal_cutoff',
    defaults = {
        'verbose_name': 'Hepatitis C signal cutoff',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_c_signal_cutoff,
    )

hep_c_riba = AbstractLabTest.objects.get_or_create(
    name = 'hep_c_riba',
    defaults = {
        'verbose_name': 'Hepatitis C RIBA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_c_riba,
    )

hep_c_rna = AbstractLabTest.objects.get_or_create(
    name = 'hep_c_rna',
    defaults = {
        'verbose_name': 'Hepatitis C RNA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_c_rna,
    )

hep_c_elisa = AbstractLabTest.objects.get_or_create(
    name = 'hep_c_elisa',
    defaults = {
        'verbose_name': 'Hepatitis C ELISA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_c_elisa,
    )


#-------------------------------------------------------------------------------
#
# Lyme
#
#-------------------------------------------------------------------------------

lyme_elisa = AbstractLabTest.objects.get_or_create(
    name = 'lyme_elisa',
    defaults = {
        'verbose_name': 'Lyme ELISA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = lyme_elisa,
    )

LabOrderHeuristic.objects.get_or_create(
    test = lyme_elisa,
    )

lyme_igg_eia = AbstractLabTest.objects.get_or_create(
    name = 'lyme_igg_eia',
    defaults = {
        'verbose_name': 'Lyme IGG (EIA)',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = lyme_igg_eia,
    )

LabOrderHeuristic.objects.get_or_create(
    test = lyme_igg_eia,
    )

lyme_igm_eia = AbstractLabTest.objects.get_or_create(
    name = 'lyme_igm_eia',
    defaults = {
        'verbose_name': 'Lyme IGM (EIA)',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = lyme_igm_eia,
    )

LabOrderHeuristic.objects.get_or_create(
    test = lyme_igm_eia,
    )

# Western blot IGG is resulted in bands, some of which are significant; but western 
# blot IGM is resulted as a standard lab test with POSTIVE result string.

#WesternBlotHeuristic(
#    name = 'lyme_igg_wb',
#    long_name = 'Lyme Western Blot IGG',
#    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
#    band_count = 5,
#    )

#
# TODO: This test needs a western blog heuristic!
#
lyme_igg_wb = AbstractLabTest.objects.get_or_create(
    name = 'lyme_igg_wb',
    defaults = {
        'verbose_name': 'Lyme IGG (Western Blot)',
        }
    )[0]
    
lyme_igm_wb = AbstractLabTest.objects.get_or_create(
    name = 'lyme_igm_wb',
    defaults = {
        'verbose_name': 'Lyme IGM (Western Blot)',
        }
    )[0]
    
# Despite being a western blot, this test is resulted pos/neg
LabResultPositiveHeuristic.objects.get_or_create(
    test = lyme_igm_wb,
    )

# 
LabResultPositiveHeuristic.objects.get_or_create(
    test = lyme_igg_wb,
    )

lyme_pcr = AbstractLabTest.objects.get_or_create(
    name = 'lyme_pcr',
    defaults = {
        'verbose_name': 'Lyme PCR',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = lyme_pcr,
    )

LabOrderHeuristic.objects.get_or_create(
    test = lyme_pcr,
    )


lyme_dx = DiagnosisHeuristic.objects.get_or_create(
    name = 'lyme',
    )[0]

foo = Icd9Query.objects.get_or_create(
    heuristic = lyme_dx,
    icd9_exact = '088.81',
    )[0]


rash_dx = DiagnosisHeuristic.objects.get_or_create(
    name = 'rash',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = rash_dx,
    icd9_exact = '782.1',
    )

doxycycline_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'doxycycline',
    drugs = 'doxycycline',
    )[0]

lyme_antibio_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'lyme_other_antibiotics',
    drugs = 'Amoxicillin, Cefuroxime, Ceftriaxone, Cefotaxime',
    )[0]


#-------------------------------------------------------------------------------
#
# Pelvic Inflamatory Disease (PID)
#
#-------------------------------------------------------------------------------

pelvic_inflamatory_disease = DiagnosisHeuristic.objects.get_or_create(
    name = 'pelvic_inflamatory_disease',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = pelvic_inflamatory_disease,
    icd9_exact = '614.0',
    )

Icd9Query.objects.get_or_create(
    heuristic = pelvic_inflamatory_disease,
    icd9_exact = '614.0',
    )

Icd9Query.objects.get_or_create(
    heuristic = pelvic_inflamatory_disease,
    icd9_exact = '614.2',
    )

Icd9Query.objects.get_or_create(
    heuristic = pelvic_inflamatory_disease,
    icd9_exact = '614.3',
    )

Icd9Query.objects.get_or_create(
    heuristic = pelvic_inflamatory_disease,
    icd9_exact = '614.5',
    )

Icd9Query.objects.get_or_create(
    heuristic = pelvic_inflamatory_disease,
    icd9_exact = '614.9',
    )

Icd9Query.objects.get_or_create(
    heuristic = pelvic_inflamatory_disease,
    icd9_exact = '099.56',
    )

#-------------------------------------------------------------------------------
#
# Tuberculosis
#
#-------------------------------------------------------------------------------

pyrazinamide_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'pyrazinamide',
    drugs = 'Pyrazinamide, PZA',
    exclude = 'CAPZA'
    )[0]

isoniazid_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'isoniazid',
    drugs = 'Isoniazid',
    exclude = 'INHAL, INHIB',
    )[0]

ethambutol_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'ethambutol',
    drugs = 'Ethambutol',
    )[0]

rifampin_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'rifampin',
    drugs = 'rifampin',
    )[0]

rifabutin_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'rifabutin',
    drugs = 'rifabutin',
    )[0]

rifapentine_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'rifapentine',
    drugs = 'rifapentine',
    )[0]

streptomycin_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'streptomycin',
    drugs = 'streptomycin',
    )[0]

para_aminosalicyclic_acid_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'para_aminosalicyclic_acid',
    drugs = 'para-aminosalicyclic acid',
    )[0]

kanamycin_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'kanamycin',
    drugs = 'kanamycin',
    )[0]

capreomycin_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'capreomycin',
    drugs = 'capreomycin',
    )[0]

cycloserine_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'cycloserine',
    drugs = 'cycloserine',
    )[0]

ethionamide_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'ethionamide',
    drugs = 'ethionamide',
    )[0]

moxifloxacin_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'moxifloxacin',
    drugs = 'moxifloxacin',
    )[0]

tb_diagnosis = DiagnosisHeuristic.objects.get_or_create(
    name = 'tuberculosis',
    )[0]
    
Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '010.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '011.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '012.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '013.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '014.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '015.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '016.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '017.',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = tb_diagnosis,
    icd9_starts_with = '018.',
    )[0]


#-------------------------------------------------------------------------------
#
# Tuberculosis
#
#-------------------------------------------------------------------------------

tb_lab = AbstractLabTest.objects.get_or_create(
    name = 'tuberculosis',
    defaults = {
        'verbose_name': 'Tuberculosis lab test (several varieties)',
        }
    )[0]
    
LabOrderHeuristic.objects.get_or_create(
    test = tb_lab,
    )



#-------------------------------------------------------------------------------
#
# Syphilis 
#
#-------------------------------------------------------------------------------

penicillin_g_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'penicillin_g',
    drugs = 'penicillin g, pen g'
    )[0]

doxycycline_7_days_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'doxycycline_7_days',
    drugs = 'doxycycline',
    min_quantity = 14, # Need 14 pills for 7 days
    )[0]

ceftriaxone_1g_2g_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'ceftriaxone_1g_2g',
    drugs = 'ceftriaxone',
    )[0]
ceftriaxone_1g_2g_rx.dose.add(dose_1g)
ceftriaxone_1g_2g_rx.dose.add(dose_2g)

syphilis_diagnosis = DiagnosisHeuristic.objects.get_or_create(
    name = 'syphilis',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '090.',
    )

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '091.',
    )

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '092.',
    )

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '093.',
    )

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '094.',
    )

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '095.',
    )

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '096.',
    )

Icd9Query.objects.get_or_create(
    heuristic = syphilis_diagnosis,
    icd9_starts_with = '097.',
    )

syphilis_tppa = AbstractLabTest.objects.get_or_create(
    name = 'syphilis_tppa',
    defaults = {
        'verbose_name': 'Syphilis TP-PA',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = syphilis_tppa,
    )
    
syphilis_fta_abs = AbstractLabTest.objects.get_or_create(
    name = 'syphilis_fta_abs',
    defaults = {
        'verbose_name': 'Syphilis FTA-ABS',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = syphilis_fta_abs,
    )

syphilis_rpr = AbstractLabTest.objects.get_or_create(
    name = 'syphilis_rpr',
    defaults = {
        'verbose_name': 'Syphilis rapid plasma reagin (RPR)',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = syphilis_rpr,
    titer = 8, # 1:8 titer
    )

syphilis_vdrl_serum = AbstractLabTest.objects.get_or_create(
    name = 'syphilis_vdrl_serum',
    defaults = {
        'verbose_name': 'Syphilis VDRL serum',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = syphilis_vdrl_serum,
    titer = 8, # 1:8 titer
    )

syphilis_tp_igg = AbstractLabTest.objects.get_or_create(
    name = 'syphilis_tp_igg',
    defaults = {
        'verbose_name': 'Syphilis TP-IGG',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = syphilis_tp_igg,
    )

syphilis_vdrl_csf = AbstractLabTest.objects.get_or_create(
    name = 'syphilis_vdrl_csf',
    defaults = {
        'verbose_name': 'Syphilis VDRL-CSF',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = syphilis_vdrl_csf,
    titer = 1, # 1:1 titer
    )


#-------------------------------------------------------------------------------
#
# Glucose
#
#-------------------------------------------------------------------------------

glucose_fasting = AbstractLabTest.objects.get_or_create(
    name = 'glucose_fasting',
    defaults = {
        'verbose_name':  'Fasting glucose (several variations)',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = glucose_fasting,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = glucose_fasting,
    threshold = 126,
    date_field = 'result'
    )


#-------------------------------------------------------------------------------
#
# Oral Glucose Tolerance Test 50g (OGTT50)
#
#-------------------------------------------------------------------------------

ogtt50_fasting = AbstractLabTest.objects.get_or_create(
    name = 'ogtt50_fasting',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 50 gram Fasting',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt50_fasting,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt50_fasting,
    threshold = 95,
    date_field = 'result'
    )

ogtt50_random = AbstractLabTest.objects.get_or_create(
    name = 'ogtt50_random',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 50 gram Random',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt50_random,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt50_random,
    threshold = 190,
    date_field = 'result'
    )

ogtt50_1hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt50_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 50 gram 1 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt50_1hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt50_1hr,
    threshold = 190,
    date_field = 'result'
    )

#-------------------------------------------------------------------------------
#
# Oral Glucose Tolerance Test 75g (OGTT 75)
#
#-------------------------------------------------------------------------------

ogtt75_series = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_series',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram Series',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_series,
    )

ogtt75_fasting = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_fasting',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram fasting',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_fasting,
    )

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt75_fasting,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_fasting,
    threshold = 95,
    date_field = 'result'
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_fasting,
    threshold = 126,
    date_field = 'result'
    )

ogtt75_fasting_urine = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_fasting_urine',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram fasting, urine',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt75_fasting_urine,
    )

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_fasting_urine,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = ogtt75_fasting_urine,
    date_field = 'result'
    )

ogtt75_30min = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_30min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 30 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt75_30min,
    )

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_30min,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_30min,
    threshold = 200,
    date_field = 'result'
    )

ogtt75_1hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 1 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt75_1hr,
    )

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_1hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_1hr,
    threshold = 180,
    date_field = 'result'
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_1hr,
    threshold = 200,
    date_field = 'result'
    )

ogtt75_90min = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_90min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 90 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt75_90min,
    )

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_90min,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_90min,
    threshold = 180,
    date_field = 'result'
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_90min,
    threshold = 200,
    date_field = 'result'
    )

ogtt75_2hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_2hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 2 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt75_2hr,
    )

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_2hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_2hr,
    threshold = 155,
    date_field = 'result'
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_2hr,
    threshold = 200,
    date_field = 'result'
    )

#-------------------------------------------------------------------------------
#
# Oral Gluclose Tolerance Test 100g (OGTT 100)
#
#-------------------------------------------------------------------------------

ogtt100_fasting = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_fasting',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram fasting',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_fasting,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_fasting,
    threshold = 95,
    date_field = 'result'
    )

ogtt100_fasting_urine = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_fasting_urine',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram fasting (urine)',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_fasting_urine,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = ogtt100_fasting_urine,
    date_field = 'result'
    )

ogtt100_30min = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_30min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 30 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_30min,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_30min,
    threshold = 200,
    date_field = 'result'
    )

ogtt100_1hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 1 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_1hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_1hr,
    threshold = 180,
    date_field = 'result'
    )

ogtt100_90min = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_90min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 90 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_90min,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_90min,
    threshold = 180,
    date_field = 'result'
    )

ogtt100_2hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_2hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 2 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_2hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_2hr,
    threshold = 155,
    date_field = 'result'
    )

ogtt100_3hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_3hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 3 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_3hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_3hr,
    threshold = 140,
    date_field = 'result'
    )

ogtt100_4hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_4hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 4 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_4hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_4hr,
    threshold = 140,
    date_field = 'result'
    )

ogtt100_5hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_5hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 5 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create(
    test = ogtt100_5hr,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_5hr,
    threshold = 140,
    date_field = 'result'
    )


#-------------------------------------------------------------------------------
#
# Glycated hemoglobin (A1C)
#
#-------------------------------------------------------------------------------

a1c = AbstractLabTest.objects.get_or_create(
    name = 'a1c',
    defaults = {
        'verbose_name':  'Glycated hemoglobin (A1C)',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create(
    test = a1c,
    )

LabOrderHeuristic.objects.get_or_create(
    test = a1c,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = a1c,
    threshold = 6.0,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = a1c,
    threshold = 6.5,
    )


pregnancy_diagnosis = DiagnosisHeuristic.objects.get_or_create(
    name = 'pregnancy',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = pregnancy_diagnosis,
    icd9_starts_with = 'V22.',
    )

Icd9Query.objects.get_or_create(
    heuristic = pregnancy_diagnosis,
    icd9_starts_with = 'V23.',
    )

#
#
##--- pregnancy
#PregnancyHeuristic() # No config needed
#

gdm_diagnosis = DiagnosisHeuristic.objects.get_or_create(
    name = 'gestational_diabetes',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = gdm_diagnosis,
    icd9_starts_with = '648.8',
    )

lancets_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'lancets',
    drugs = 'lancets',
    )[0]

test_strips_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'test_strips',
    drugs = 'test strips',
    )

insulin_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'insulin',
    drugs = 'insulin',
    )

#-------------------------------------------------------------------------------
#
# Giardiasis
#
#-------------------------------------------------------------------------------

giardiasis_antigen = AbstractLabTest.objects.get_or_create(
    name = 'giardiasis_antigen',
    defaults = {
        'verbose_name': 'Giardiasis Antigen',
        },
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = giardiasis_antigen,
    )


metronidazole_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'metronidazole',
    drugs = 'metronidazole',
    )

diahrrhea_diagnosis = DiagnosisHeuristic.objects.get_or_create(
    name = 'diarrhea',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = diahrrhea_diagnosis,
    icd9_exact = '787.91',
    )


#-------------------------------------------------------------------------------
#
# Pertussis
#
#-------------------------------------------------------------------------------

pertussis_dx = DiagnosisHeuristic.objects.get_or_create(
    name = 'pertussis',
    )[0]
    
Icd9Query.objects.get_or_create(
    heuristic = pertussis_dx,
    icd9_exact = '033.0',
    )

Icd9Query.objects.get_or_create(
    heuristic = pertussis_dx,
    icd9_exact = '033.9',
    )

#
# Needs new functionality to examine comment string
#
pertussis_pcr = AbstractLabTest.objects.get_or_create(
    name = 'pertussis_pcr',
    defaults = {
        'verbose_name': 'Pertussis PCR',
        },
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test = pertussis_pcr,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = pertussis_pcr,
    )

#
# Needs new functionality to examine comment string
#
pertussis_culture = AbstractLabTest.objects.get_or_create(
    name = 'pertussis_culture',
    defaults = {
        'verbose_name': 'Pertussis Culture',
        },
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test = pertussis_culture,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = pertussis_culture,
    )

pertussis_serology = AbstractLabTest.objects.get_or_create(
    name = 'pertussis_serology',
    defaults = {
        'verbose_name': 'Pertussis serology',
        },
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test = pertussis_serology,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = pertussis_culture,
    )

pertussis_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'pertussis',
    drugs =  'Erythromycin, Clarithromycin, Azithromycin, Trimethoprim-sulfamethoxazole',
    )[0]


#-------------------------------------------------------------------------------
#
# Diabetes
#
#-------------------------------------------------------------------------------

diabetes_rx = PrescriptionHeuristic.objects.get_or_create(
    name = 'diabetes',
    drugs =  'glyburide, gliclazide, glipizide, glimepiride,pioglitazone, rosiglitazone, repaglinide, nateglinide, meglitinide, sitagliptin, exenatide, pramlintide',
    )[0]

diabetes_dx = DiagnosisHeuristic.objects.get_or_create(
    name = 'diabetes_all_types',
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = diabetes_dx,
    icd9_starts_with = '250.',
    )

diabetes_type_1_dx = DiagnosisHeuristic.objects.get_or_create(
    name = 'diabetes_type_1'
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = diabetes_type_1_dx,
    icd9_starts_with = '250.',
    icd9_ends_with = '1',
    )

Icd9Query.objects.get_or_create(
    heuristic = diabetes_type_1_dx,
    icd9_starts_with = '250.',
    icd9_ends_with = '3',
    )

diabetes_type_2_dx = DiagnosisHeuristic.objects.get_or_create(
    name = 'diabetes_type_2'
    )[0]

Icd9Query.objects.get_or_create(
    heuristic = diabetes_type_2_dx,
    icd9_starts_with = '250.',
    icd9_ends_with = '0',
    )

Icd9Query.objects.get_or_create(
    heuristic = diabetes_type_2_dx,
    icd9_starts_with = '250.',
    icd9_ends_with = '2',
    )