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



# These definitions do not necessarily *need* to be assigned to variables.  The mere
# act of instantiating a BaseHeuristic instance causes that instance to be
# registered with the heuristics framework, and therefore to be called by
# BaseHeuristic.generate_all_events().  


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
    name = 'lyme_igg',
    long_name = 'Lyme IGG',
    )

WesternBlotHeuristic(
    name = 'lyme_igg_wb',
    long_name = 'Lyme Western Blot',
    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
    band_count = 5,
    )

LabResultHeuristic(
    name = 'lyme_igm',
    long_name = 'Lyme IGM (EIA)',
    )

LabResultHeuristic(
    name = 'lyme_pcr',
    long_name = 'Lyme PCR',
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
    name = 'tb_meds',
    long_name = 'Tuberculosis medications',
    drugs = [
        'Pyrazinamide',
        'PZA',
        #'RIFAMPIN',
        #'RIFAMATE',
        #'ISONARIF',
        ],
    exclude = ['CAPZA',]
    )

MedicationHeuristic(
    name = 'tb_secondary_meds',
    long_name = 'Tuberculosis secondary medications',
    drugs = [
        'Isoniazid',
        'Ethambutol', 
        'Rifampin', 
        'Rifabutin', 
        'Rifapentine', 
        'Pyrazinamide',
        'Streptomycin', 
        'Para-aminosalicyclic acid', 
        'Kanamycin', 
        'Capreomycin', 
        'Cycloserine', 
        'Ethionamide', 
        'Moxifloxacin', 
        ],
    exclude = ['CAPZA', 'INHAL', 'INHIB']
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
    name = 'ttpa',
    long_name = 'TTPA test',
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
        '1:1024',
        ]
    )
