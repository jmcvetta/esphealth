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

#--- gonorrhea_pos 
LabResultHeuristic(
    name = 'gonorrhea',
    long_name = 'Gonorrhea test',
    ratio = None, # This test should never have numeric results
    )

#--- chlamydia_pos 
LabResultHeuristic(
    name = 'chlamydia',
    long_name = 'Chlamydia test',
    ratio = None, # This test should never have numeric results
    )

#--- alt_2x 
LabResultHeuristic(
    name = 'alt_2x',
    long_name = 'Blood ALT level 2x threshold',
    ratio = 2,
    )

#--- alt_5x 
LabResultHeuristic(
    name = 'alt_5x',
    long_name = 'Blood ALT level 5x threshold',
    ratio = 5,
    )

#--- alt_400 
LabResultHeuristic(
    name = 'alt_400',
    long_name = 'Blood ALT level >400',
    ratio = None,
    )

#--- ast_2x 
LabResultHeuristic(
    name = 'ast_2x',
    long_name = 'Blood AST level 2x threshold',
    ratio = 2,
    )

#--- ast_5x 
LabResultHeuristic(
    name = 'ast_5x',
    long_name = 'Blood AST level 5x threshold',
    ratio = 5,
    )

#--- hep_a_igm
LabResultHeuristic(
    name = 'hep_a_igm',
    long_name = 'Hepatitis A IgM',
    negative_events = True,
    )

#--- hep_b_igm
LabResultHeuristic(
    name = 'hep_b_igm',
    long_name = 'Hepatitis B IgM',
    negative_events = True,
    order_events = True,
    )

#--- hep_b_core
LabResultHeuristic(
    name = 'hep_b_core',
    long_name = 'Hepatitis B core antibody',
    negative_events = True,
    )

#--- hep_b_surface
LabResultHeuristic(
    name = 'hep_b_surface',
    long_name = 'Hepatitis B surface antibody',
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
# Lyme Disease
#

#--- lyme_elisa_pos 
LabResultHeuristic(
    name = 'lyme_elisa',
    long_name = 'Lyme ELISA',
    order_events = True,
    )

#--- lyme_igg 
LabResultHeuristic(
    name = 'lyme_igg',
    long_name = 'Lyme IGG',
    )

#--- lyme_igg_wb
WesternBlotHeuristic(
    name = 'lyme_igg_wb',
    long_name = 'Lyme Western Blot',
    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
    band_count = 5,
    )

#--- lyme_igm 
LabResultHeuristic(
    name = 'lyme_igm',
    long_name = 'Lyme IGM (EIA)',
    )

#--- lyme_pcr 
LabResultHeuristic(
    name = 'lyme_pcr',
    long_name = 'Lyme PCR',
    )

#--- lyme_diagnosis 
EncounterHeuristic(
    name = 'lyme_diagnosis',
    long_name = 'Lyme diagnosis',
    icd9s = ['088.81'],
    )

#--- rash 
EncounterHeuristic(
    name = 'rash',
    long_name = 'Rash',
    icd9s = ['782.1'],
    )

#--- doxycycline 
MedicationHeuristic(
    name = 'doxycycline',
    long_name = 'Doxycycline',
    drugs = ['doxycycline'],
    )

#--- lyme_other_antibiotics 
MedicationHeuristic(
    name = 'lyme_other_antibiotics',
    long_name = 'Lyme disease antibiotics other than Doxycycline',
    drugs = ['Amoxicillin', 'Cefuroxime', 'Ceftriaxone', 'Cefotaxime'],
    )


# 
# Pelvic Inflamatory Disease (PID)
#


#--- pid_diagnosis
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

#--- tb_meds
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

#--- tb_diagnosis
EncounterHeuristic(
    name = 'tb_diagnosis',
    long_name = 'Tuberculosis diagnosis',
    icd9s = [
        '010.',
        '018.',
        ],
    match_style = 'startswith',
    )

#--- tb_lab
LabResultHeuristic(
    name = 'tb_lab',
    long_name = 'Tuberculosis lab order',
    order_events = True,
    )

