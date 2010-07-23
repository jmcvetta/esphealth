'''
                                  ESP Health
                          Heuristic Events Framework
                               Event Definitions

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from ESP.new_hef.models import AbstractLabTest, LabOrderHeuristic
from ESP.new_hef.models import LabOrderHeuristic
from ESP.new_hef.models import LabResultPositiveHeuristic
from ESP.new_hef.models import LabResultRatioHeuristic
from ESP.new_hef.models import LabResultFixedThresholdHeuristic
from ESP.new_hef.models import EncounterHeuristic


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

hep_a_igm = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_igm',
    defaults = {
        'verbose_name': 'Hepatitis A IgM antibody',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_a_igm,
    )

hep_a_tot_ab = AbstractLabTest.objects.get_or_create(
    name = 'hep_a_tot_ab',
    defaults = {
        'verbose_name': 'Hepatitis A Total Antibodies',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_a_tot_ab,
    )


#-------------------------------------------------------------------------------
#
# Hepatitis B
#
#-------------------------------------------------------------------------------

hep_b_igm_ab = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_igm_ab',
    defaults = {
        'verbose_name': 'Hepatitis B core IgM antibody',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test = hep_b_igm_ab,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_igm_ab,
    )

hep_b_core_ab = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_core_ab',
    defaults = {
        'verbose_name': 'Hepatitis B core general antibody',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_core_ab,
    )

hep_b_surface_ag = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_surface_antigen',
    defaults = {
        'verbose_name': 'Hepatitis B surface antigen',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_surface_ag,
    )


hep_b_e_ag = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_e_ag',
    defaults = {
        'verbose_name': 'Hep B "e" antigen',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_b_e_ag,
    )


# NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm


hep_b_viral_dna = AbstractLabTest.objects.get_or_create(
    name = 'hep_b_viral_dna',
    defaults = {
        'verbose_name': 'Hep B viral DNA',
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

hep_e_ab = AbstractLabTest.objects.get_or_create(
    name = 'hep_e_ab',
    defaults = {
        'verbose_name': 'Hepatitis E antibody',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create(
    test = hep_e_ab,
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


lyme_diagnosis = EncounterHeuristic.objects.get_or_create(
    name = 'lyme_diagnosis',
    icd9_codes = '088.81',
    )[0]


rash = EncounterHeuristic.objects.get_or_create(
    name = 'rash',
    icd9_codes = '782.1',
    )

#MedicationHeuristic(
#    name = 'doxycycline',
#    long_name = 'Doxycycline',
#    drugs = ['doxycycline'],
#    )
#
#MedicationHeuristic(
#    name = 'lyme_other_antibiotics',
#    long_name = 'Lyme disease antibiotics other than Doxycycline',
#    drugs = ['Amoxicillin', 'Cefuroxime', 'Ceftriaxone', 'Cefotaxime'],
#    )
#
#


#-------------------------------------------------------------------------------
#
# Pelvic Inflamatory Disease (PID)
#
#-------------------------------------------------------------------------------

EncounterHeuristic.objects.get_or_create(
    name = 'pid_diagnosis',
    icd9_codes = '614.0, 614.2, 614.3, 614.5, 614.9, 099.56',
    )[0]

#
#--- Tuberculosis
#

#MedicationHeuristic(
#    name = 'pyrazinamide',
#    long_name = 'Pyrazinamide prescription',
#    drugs = [
#        'Pyrazinamide',
#        'PZA',
#        ],
#    exclude = ['CAPZA',]
#    )
#
#MedicationHeuristic(
#    name = 'isoniazid',
#    long_name = 'Isoniazid prescription',
#    drugs = ['Isoniazid'],
#    exclude = ['INHAL', 'INHIB']
#    )
#
#MedicationHeuristic(
#    name = 'ethambutol',
#    long_name = 'Ethambutol prescription',
#    drugs = ['Ethambutol'],
#    )
#
#MedicationHeuristic(
#    name = 'rifampin',
#    long_name = 'Rifampin prescription',
#    drugs = ['Rifampin'],
#    )
#
#MedicationHeuristic(
#    name = 'rifabutin',
#    long_name = 'Rifabutin prescription',
#    drugs = ['Rifabutin'],
#    )
#
#MedicationHeuristic(
#    name = 'rifapentine',
#    long_name = 'Rifapentine prescription',
#    drugs = ['Rifapentine'],
#    )
#
#MedicationHeuristic(
#    name = 'streptomycin',
#    long_name = 'Streptomycin prescription',
#    drugs = ['Streptomycin'],
#    )
#
#MedicationHeuristic(
#    name = 'para_aminosalicyclic_acid',
#    long_name = 'Para-aminosalicyclic acid prescription',
#    drugs = ['Para-aminosalicyclic acid'],
#    )
#
#MedicationHeuristic(
#    name = 'kanamycin',
#    long_name = 'Kanamycin prescription',
#    drugs = ['Kanamycin'],
#    )
#
#MedicationHeuristic(
#    name = 'capreomycin',
#    long_name = 'Capreomycin prescription',
#    drugs = ['capreomycin'],
#    )
#
#MedicationHeuristic(
#    name = 'cycloserine',
#    long_name = 'Cycloserine prescription',
#    drugs = ['Cycloserine', ],
#    )
#
#MedicationHeuristic(
#    name = 'ethionamide',
#    long_name = 'Ethionamide prescription',
#    drugs = [ 'Ethionamide',  ],
#    )
#
#MedicationHeuristic(
#    name = 'moxifloxacin',
#    long_name = 'Moxifloxacin prescription',
#    drugs = ['Moxifloxacin', ],
#    )

tb_diagnosis = EncounterHeuristic.objects.get_or_create(
    name = 'tb_diagnosis',
    icd9_codes = '010., 011., 012., 013., 014., 015., 016., 017., 018.',
    code_match_type = 'startswith',
    )[0]


#-------------------------------------------------------------------------------
#
# Tuberculosis
#
#-------------------------------------------------------------------------------

tb_lab = AbstractLabTest.objects.get_or_create(
    name = 'tb_lab',
    defaults = {
        'verbose_name': 'Tuberculosis lab test (several varieties)',
        }
    )[0]
    
LabOrderHeuristic.objects.get_or_create(
    test = tb_lab,
    )



#
#--- Syphilis 
#

#MedicationHeuristic(
#    name = 'penicillin_g',
#    long_name = 'Pennicilin G',
#    drugs = [
#        'PENICILLIN G',
#        'PEN G',
#        ]
#	)
#
#MedicationHeuristic(
#    name = 'doxycycline_7_days',
#    long_name = 'Doxycycline for >= 7 days',
#    drugs = ['doxycycline'],
#    min_quantity = 14, # Need 14 pills for 7 days
#    )
#
#MedicationHeuristic(
#    name = 'ceftriaxone_1g',
#    long_name = 'Ceftriaxone dosage >= 1g',
#    drugs = ['ceftriaxone'],
#    require = [
#        '1g',
#        '2g',
#        ]
#    )

syphilis_diagnosis = EncounterHeuristic.objects.get_or_create(
    name = 'syphilis_diagnosis',
    icd9_codes = '090., 091., 092., 093., 094., 095., 096., 097.',
    code_match_type = 'startswith',
    )[0]


#-------------------------------------------------------------------------------
#
# Syphilis
#
#-------------------------------------------------------------------------------

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

syphilis_vrdl_csf = AbstractLabTest.objects.get_or_create(
    name = 'syphilis_vrdl_csf',
    defaults = {
        'verbose_name': 'Syphilis VDRL-CSF',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create(
    test = syphilis_vrdl_csf,
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
        'verbose_name':  'Fasting glucose (several OGTT variations)',
        }
    )[0]

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

ogtt75_fasting = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_fasting',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram fasting',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_fasting,
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

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_fasting_urine,
    )

LabResultPositiveHeuristic.objects.get_or_create(
    test = ogtt75_fasting_urine,
    date_field = 'result'
    )

ogtt75_30m = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_30m',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 30 minutes post',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_30m,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_30m,
    threshold = 200,
    date_field = 'result'
    )

ogtt75_1hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 1 hour post',
        }
    )[0]

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

ogtt75_90m = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_90m',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 90 minutes post',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create(
    test=ogtt75_90m,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_90m,
    threshold = 180,
    date_field = 'result'
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt75_90m,
    threshold = 200,
    date_field = 'result'
    )

ogtt75_2hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_2hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 2 hour post',
        }
    )[0]

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

LabResultPositiveHeuristic.objects.get_or_create(
    test = ogtt100_fasting_urine,
    date_field = 'result'
    )

ogtt100_30m = AbstractLabTest.objects.get_or_create(
    name = 'ogtt75_2hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 30 minutes post',
        }
    )[0]

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_30m,
    threshold = 200,
    date_field = 'result'
    )

ogtt100_1hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 1 hour post',
        }
    )[0]

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_1hr,
    threshold = 180,
    date_field = 'result'
    )

ogtt100_90m = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_90m',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 90 minutes post',
        }
    )[0]

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = ogtt100_90m,
    threshold = 180,
    date_field = 'result'
    )

ogtt100_2hr = AbstractLabTest.objects.get_or_create(
    name = 'ogtt100_2hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 2 hour post',
        }
    )[0]

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

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = a1c,
    threshold = 6.0,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create(
    test = a1c,
    threshold = 6.5,
    )


pregnancy_diagnosis = EncounterHeuristic.objects.get_or_create(
    name = 'pregnancy_diagnosis',
    icd9_codes = 'V22., V23.',
    code_match_type = 'startswith',
    )[0]

#
#
##--- pregnancy
#PregnancyHeuristic() # No config needed
#

gdm_diagnosis = EncounterHeuristic.objects.get_or_create(
    name = 'gdm_diagnosis',
    icd9_codes = '648.8',
    code_match_type = 'startswith',
    )[0]

#MedicationHeuristic(
#    name = 'lancets_rx',
#    long_name = 'Lancets Prescription',
#    drugs = ['lancets'],
#    )
#
#MedicationHeuristic(
#    name = 'test_strips_rx',
#    long_name = 'Test Strips Prescription',
#    drugs = ['test strips'],
#    )
#
#MedicationHeuristic(
#    name = 'insulin_rx',
#    long_name = 'Insulin Prescription',
#    drugs = ['insulin'],
#    )
#
#
##
##--- Giardiasis
##
#
#LabResultHeuristic(
#    name = 'giardiasis_antigen',
#    long_name = 'Giardiasis Antigen',
#    )
#
#MedicationHeuristic(
#    name = 'metronidazole',
#    long_name = 'Metronidazole',
#    drugs = ['metronidazole'],
#    )

diahrrhea_diagnosis = EncounterHeuristic.objects.get_or_create(
    name = 'diarrhea_diagnosis',
    icd9_codes = '787.91',
    )[0]


##
##--- Pertussis
##

pertussis_diagnosis = EncounterHeuristic.objects.get_or_create(
    name = 'pertussis_diagnosis',
    icd9_codes = '033.0, 033.9',
    )[0]

##
## Needs new functionality to examine comment string
##
#LabResultHeuristic(
#    name = 'pertussis_pcr',
#    long_name = 'Pertussis PCR test',
#    order_events = True,
#    )
#    
##
## Needs new functionality to examine comment string
##
#LabResultHeuristic(
#    name = 'pertussis_culture',
#    long_name = 'Culture for pertussis',
#    order_events = True,
#    )
#    
#LabResultHeuristic(
#    name = 'pertussis_serology',
#    long_name = 'Pertussis serology',
#    order_events = True,
#    )
#
#MedicationHeuristic(
#    name = 'pertussis_rx',
#    long_name = 'Prescription for Pertussis antibiotics',
#    drugs = [
#        'Erythromycin',
#        'Clarithromycin',
#        'Azithromycin',
#        'Trimethoprim-sulfamethoxazole',
#        ],
#    )
