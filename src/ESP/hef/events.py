'''
                                  ESP Health
                          Heuristic Events Framework
                               Event Definitions

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from ESP.hef.core import EncounterHeuristic
from ESP.hef.core import LabResultHeuristic
from ESP.hef.core import MedicationHeuristic
from ESP.hef.core import FeverHeuristic
from ESP.hef.core import CalculatedBilirubinHeuristic
from ESP.hef.core import WesternBlotHeuristic
from ESP.hef.core import PregnancyHeuristic


#===============================================================================
#
#--- ~~~ Encounter Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#--- fever 
FeverHeuristic(
    name = 'esp-fever',
    long_name = 'Fever (ESP definition)',
    temperature = 100.4,
    icd9s = ['780.6A', ],
    )

#--- jaundice 
EncounterHeuristic(
    name = 'jaundice',
    long_name = 'Jaundice diagnosis',
    icd9s = ['782.4'],
    )

#--- chronic_hep_b 
EncounterHeuristic(
    name = 'chronic_hep_b',
    long_name = 'Chronic Hepatitis B diagnosis',
    icd9s = ['070.32'],
    )

#--- chronic_hep_c 
EncounterHeuristic(
    name = 'chronic_hep_c',
    long_name = 'Chronic Hepatitis C diagnosis',
    icd9s = ['070.54', '070.70', ],
    )


#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#--- gonorrhea
LabResultHeuristic(
    name = 'gonorrhea',
    long_name = 'Gonorrhea test',
    )

#--- chlamydia
LabResultHeuristic(
    name = 'chlamydia',
    long_name = 'Chlamydia test',
    )

#--- alt
LabResultHeuristic(
    name = 'alt',
    long_name = 'Blood ALT level',
    positive_events = False,
    ratio_events = [2, 5],
    fixed_threshold_events = [400],
    )

#--- alt_400 
#LabResultHeuristic(
    #name = 'alt_400',
    #long_name = 'Blood ALT level >400',
    #ratio = None,
    #)

#--- ast
LabResultHeuristic(
    name = 'ast',
    long_name = 'Blood AST level',
    positive_events = False,
    ratio_events = [2, 5],
    )

#--- hep_a_igm
LabResultHeuristic(
    name = 'hep_a_igm',
    long_name = 'Hepatitis A IgM antibody',
    negative_events = True,
    )

LabResultHeuristic(
    name = 'hav_tot',
    long_name = 'Hepatitis A Total Antibodies',
    positive_events = False,
    negative_events = True,
    )

#--- hep_b_igm
LabResultHeuristic(
    name = 'hep_b_igm',
    long_name = 'Hepatitis B core IgM antibody',
    negative_events = True,
    order_events = True,
    )

#--- hep_b_core
LabResultHeuristic(
    name = 'hep_b_core',
    long_name = 'Hepatitis B core general antibody',
    negative_events = True,
    )

#--- hep_b_surface
LabResultHeuristic(
    name = 'hep_b_surface',
    long_name = 'Hepatitis B surface antigen',
    negative_events = True,
    )

#--- hep_b_e_antigen
LabResultHeuristic(
    name = 'hep_b_e_antigen',
    long_name = 'Hep B "e" antigen',
    )


# NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm

#--- hep_b_viral_dna
LabResultHeuristic(
    name = 'hep_b_viral_dna',
    long_name = 'Hep B viral DNA',
    )

#--- hep_e_ab 
LabResultHeuristic(
    name = 'hep_e_ab',
    long_name = 'Hepatitis E antibody',
    )

#--- total_bilirubin_high 
LabResultHeuristic(
    name = 'total_bilirubin_high',
    long_name = 'High total bilirubin',
    )

#--- high_calc_bilirubin 
CalculatedBilirubinHeuristic()

#--- hep_c_signal_cutoff 
LabResultHeuristic(
    name = 'hep_c_signal_cutoff',
    long_name = 'Hepatitis C signal cutoff',
    negative_events = True,
    )

#--- hep_c_riba 
LabResultHeuristic(
    name = 'hep_c_riba',
    long_name = 'Hepatitis C RIBA',
    negative_events = True,
    )

#--- hep_c_rna 
LabResultHeuristic(
    name = 'hep_c_rna',
    long_name = 'Hepatitis C RNA',
    negative_events = True,
    )

#--- hep_c_elisa 
LabResultHeuristic(
    name = 'hep_c_elisa',
    long_name = 'Hepatitis C ELISA',
    negative_events = True,
    )


#
#--- Lyme Disease
#

LabResultHeuristic(
    name = 'lyme_elisa',
    long_name = 'Lyme ELISA',
    order_events = True,
    )

LabResultHeuristic(
    name = 'lyme_igg_eia',
    long_name = 'Lyme IGG (EIA)',
    order_events = True,
    )

LabResultHeuristic(
    name = 'lyme_igm_eia',
    long_name = 'Lyme IGM (EIA)',
    order_events = True,
    )


# Western blot IGG is resulted in bands, some of which are significant; but western 
# blot IGM is resulted as a standard lab test with POSTIVE result string.

WesternBlotHeuristic(
    name = 'lyme_igg_wb',
    long_name = 'Lyme Western Blot IGG',
    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
    band_count = 5,
    )

LabResultHeuristic(
    name = 'lyme_igm_wb',
    long_name = 'Lyme Western Blot IGM',
    )

LabResultHeuristic(
    name = 'lyme_pcr',
    long_name = 'Lyme PCR',
    order_events = True,
    )

EncounterHeuristic(
    name = 'lyme_diagnosis',
    long_name = 'Lyme diagnosis',
    icd9s = ['088.81'],
    )

EncounterHeuristic(
    name = 'rash',
    long_name = 'Rash',
    icd9s = ['782.1'],
    )

MedicationHeuristic(
    name = 'doxycycline',
    long_name = 'Doxycycline',
    drugs = ['doxycycline'],
    )

MedicationHeuristic(
    name = 'lyme_other_antibiotics',
    long_name = 'Lyme disease antibiotics other than Doxycycline',
    drugs = ['Amoxicillin', 'Cefuroxime', 'Ceftriaxone', 'Cefotaxime'],
    )


# 
#--- Pelvic Inflamatory Disease (PID)
#


EncounterHeuristic(
    name = 'pid_diagnosis',
    long_name = 'PID diagnosis',
    icd9s = [
        '614.0',
        '614.2',
        '614.3',
        '614.5',
        '614.9',
        '099.56',
        ],
    )

#
#--- Tuberculosis
#

MedicationHeuristic(
    name = 'pyrazinamide',
    long_name = 'Pyrazinamide prescription',
    drugs = [
        'Pyrazinamide',
        'PZA',
        ],
    exclude = ['CAPZA',]
    )

MedicationHeuristic(
    name = 'isoniazid',
    long_name = 'Isoniazid prescription',
    drugs = ['Isoniazid'],
    exclude = ['INHAL', 'INHIB']
    )

MedicationHeuristic(
    name = 'ethambutol',
    long_name = 'Ethambutol prescription',
    drugs = ['Ethambutol'],
    )

MedicationHeuristic(
    name = 'rifampin',
    long_name = 'Rifampin prescription',
    drugs = ['Rifampin'],
    )

MedicationHeuristic(
    name = 'rifabutin',
    long_name = 'Rifabutin prescription',
    drugs = ['Rifabutin'],
    )

MedicationHeuristic(
    name = 'rifapentine',
    long_name = 'Rifapentine prescription',
    drugs = ['Rifapentine'],
    )

MedicationHeuristic(
    name = 'streptomycin',
    long_name = 'Streptomycin prescription',
    drugs = ['Streptomycin'],
    )

MedicationHeuristic(
    name = 'para_aminosalicyclic_acid',
    long_name = 'Para-aminosalicyclic acid prescription',
    drugs = ['Para-aminosalicyclic acid'],
    )

MedicationHeuristic(
    name = 'kanamycin',
    long_name = 'Kanamycin prescription',
    drugs = ['Kanamycin'],
    )

MedicationHeuristic(
    name = 'capreomycin',
    long_name = 'Capreomycin prescription',
    drugs = ['capreomycin'],
    )

MedicationHeuristic(
    name = 'cycloserine',
    long_name = 'Cycloserine prescription',
    drugs = ['Cycloserine', ],
    )

MedicationHeuristic(
    name = 'ethionamide',
    long_name = 'Ethionamide prescription',
    drugs = [ 'Ethionamide',  ],
    )

MedicationHeuristic(
    name = 'moxifloxacin',
    long_name = 'Moxifloxacin prescription',
    drugs = ['Moxifloxacin', ],
    )

EncounterHeuristic(
    name = 'tb_diagnosis',
    long_name = 'Tuberculosis diagnosis',
    icd9s = [
        '010.',
        '011.',
        '012.',
        '013.',
        '014.',
        '015.',
        '016.',
        '017.',
        '018.',
        ],
    match_style = 'startswith',
    )

LabResultHeuristic(
    name = 'tb_lab',
    long_name = 'Tuberculosis lab order',
    order_events = True,
    )


#
#--- Syphilis 
#

MedicationHeuristic(
    name = 'penicillin_g',
    long_name = 'Pennicilin G',
    drugs = [
        'PENICILLIN G',
        'PEN G',
        ]
	)

MedicationHeuristic(
    name = 'doxycycline_7_days',
    long_name = 'Doxycycline for >= 7 days',
    drugs = ['doxycycline'],
    min_quantity = 14, # Need 14 pills for 7 days
    )

MedicationHeuristic(
    name = 'ceftriaxone_1g',
    long_name = 'Ceftriaxone dosage >= 1g',
    drugs = ['ceftriaxone'],
    require = [
        '1g',
        '2g',
        ]
    )

EncounterHeuristic(
    name = 'syphilis_diagnosis',
    long_name = 'Syphilis Diagnosis',
    icd9s = [
        '090',
        '091',
        '092',
        '093',
        '094',
        '095',
        '096',
        '097',
        ],
    match_style = 'startswith'
    )

LabResultHeuristic(
    name = 'tppa',
    long_name = 'TPPA test',
    )

LabResultHeuristic(
    name = 'fta_abs',
    long_name = 'FTA-ABS test',
    )


LabResultHeuristic(
    name = 'rpr',
    long_name = 'RPR test',
    extra_positive_strings = [
        '1:8',
        '1:16',
        '1:32',
        '1:64',
        '1:128',
        '1:256',
        '1:512',
        '1:1024', ]
    )

LabResultHeuristic(
    name = 'vdrl_serum',
    long_name = 'VDRL serum test',
    extra_positive_strings = [
        '1:8',
        '1:16',
        '1:32',
        '1:64',
        '1:128',
        '1:256',
        '1:512',
        '1:1024', ]
    )

LabResultHeuristic(
    name = 'tp_igg',
    long_name = 'TP-IGG test',
    )

LabResultHeuristic(
    name = 'vdrl_csf',
    long_name = 'VDRL-CSF test',
    extra_positive_strings = [
        '1:1',
        '1:2',
        '1:4',
        '1:8',
        '1:16',
        '1:32',
        '1:64',
        '1:128',
        '1:256',
        '1:512',
        '1:1024', ]
    )


#--- Glucose Fasting

LabResultHeuristic(
    name = 'glucose_fasting',
    long_name = 'GLUCOSE FASTING (and variants)',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [126],
    )


#--- OGTT 50

LabResultHeuristic(
    name = 'ogtt50_fasting',
    long_name = 'OB GLUCOSE CHALLENGE, FASTING',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [95],
    )

LabResultHeuristic(
    name = 'ogtt50_random',
    long_name = 'OB GLUCOSE CHALLENGE, RANDOM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [190],
    )

LabResultHeuristic(
    name = 'ogtt50_1hr',
    long_name = 'GLUCOSE 1 HR POST CHAL.',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [190],
    )


#--- OGTT 75

# We have intra- and postpartum OGTT75 fasting heuristics, because default threshold is different for each
LabResultHeuristic(
    name = 'ogtt75_fasting',
    long_name = 'GLUCOSE FASTING PRE 75 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [95, 126],
    order_events = True,
    )
    
LabResultHeuristic(
    name = 'ogtt75_fasting_urine',
    long_name = 'GLUCOSE FASTING, UR',
    date_field = 'result',
    positive_events = True,
    order_events = True,
    )
    
LabResultHeuristic(
    name = 'ogtt75_30m',
    long_name = 'GLUCOSE 1/2 HR POST 75 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [200],
    order_events = True,
    )

LabResultHeuristic(
    name = 'ogtt75_1hr',
    long_name = 'GLUCOSE 1 HR POST 75 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [180, 200],
    order_events = True,
    )

LabResultHeuristic(
    name = 'ogtt75_90m',
    long_name = 'GLUCOSE 1 1/2 HR POST 75 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [180, 200],
    order_events = True,
    )

LabResultHeuristic(
    name = 'ogtt75_2hr',
    long_name = 'GLUCOSE 2 HR POST 75 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [155, 200],
    order_events = True,
    )


#--- OGTT 100

LabResultHeuristic(
    name = 'ogtt100_fasting',
    long_name = 'GLUCOSE FASTING PRE 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [95],
    )

LabResultHeuristic(
    name = 'ogtt100_fasting_urine',
    long_name = 'GLUCOSE FASTING PRE 100 GM',
    date_field = 'result',
    positive_events = True,
    )

LabResultHeuristic(
    name = 'ogtt100_30m',
    long_name = 'GLUCOSE 1/2 HR POST 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [200],
    )

LabResultHeuristic(
    name = 'ogtt100_1hr',
    long_name = 'GLUCOSE 1 HR POST 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [180],
    )

LabResultHeuristic(
    name = 'ogtt100_90m',
    long_name = 'GLUCOSE 1 1/2 HR POST 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [180],
    )

LabResultHeuristic(
    name = 'ogtt100_2hr',
    long_name = 'GLUCOSE 2 HR POST 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [155],
    )

LabResultHeuristic(
    name = 'ogtt100_3hr',
    long_name = 'GLUCOSE 3 HR POST 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [140],
    )

LabResultHeuristic(
    name = 'ogtt100_4hr',
    long_name = 'GLUCOSE 4 HR POST 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [140],
    )

LabResultHeuristic(
    name = 'ogtt100_5hr',
    long_name = 'GLUCOSE 5 HR POST 100 GM',
    date_field = 'result',
    positive_events = False,
    fixed_threshold_events = [140],
    )

#
#-- Gestational Diabetes
#

LabResultHeuristic(
    name = 'a1c',
    long_name = 'Hemoglobin A1C',
    positive_events = False,
    fixed_threshold_events = [6.0, 6.5],
    )

EncounterHeuristic(
    name = 'pregnancy_diagnosis',
    long_name = 'Pregnancy (by ICD9)',
    icd9s = ['V22.', 'V23.'],
    match_style = 'startswith',
    )


#--- pregnancy
PregnancyHeuristic() # No config needed


EncounterHeuristic(
    name = 'gdm_diagnosis',
    long_name = 'ABN GLUCOSE (several variants)',
    icd9s = ['648.8',],
    match_style = 'startswith',
    )

MedicationHeuristic(
    name = 'lancets_rx',
    long_name = 'Lancets Prescription',
    drugs = ['lancets'],
    )

MedicationHeuristic(
    name = 'test_strips_rx',
    long_name = 'Test Strips Prescription',
    drugs = ['test strips'],
    )

MedicationHeuristic(
    name = 'insulin_rx',
    long_name = 'Insulin Prescription',
    drugs = ['insulin'],
    )


#
#--- Giardiasis
#

LabResultHeuristic(
    name = 'giardiasis_antigen',
    long_name = 'Giardiasis Antigen',
    )

MedicationHeuristic(
    name = 'metronidazole',
    long_name = 'Metronidazole',
    drugs = ['metronidazole'],
    )

EncounterHeuristic(
    name = 'diarrhea',
    long_name = 'Diarrhea',
    icd9s = ['787.91'],
    )


#
#--- Pertussis
#

EncounterHeuristic(
    name = 'pertussis_diagnosis',
    long_name = 'Pertussis diagnosis by ICD9',
    icd9s = ['033.0', '033.9'],
    )

#
# Needs new functionality to examine comment string
#
LabResultHeuristic(
    name = 'pertussis_pcr',
    long_name = 'Pertussis PCR test',
    order_events = True,
    )
    
#
# Needs new functionality to examine comment string
#
LabResultHeuristic(
    name = 'pertussis_culture',
    long_name = 'Culture for pertussis',
    order_events = True,
    )
    
LabResultHeuristic(
    name = 'pertussis_serology',
    long_name = 'Pertussis serology',
    order_events = True,
    )

MedicationHeuristic(
    name = 'pertussis_rx',
    long_name = 'Prescription for Pertussis antibiotics',
    drugs = [
        'Erythromycin',
        'Clarithromycin',
        'Azithromycin',
        'Trimethoprim-sulfamethoxazole',
        ],
    )
