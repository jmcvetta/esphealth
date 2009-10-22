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
from ESP.hef.core import LabResultHeuristic
from ESP.hef.core import MedicationHeuristic
from ESP.hef.core import FeverHeuristic
from ESP.hef.core import CalculatedBilirubinHeuristic
from ESP.hef.core import WesternBlotHeuristic
from ESP.hef.core import LabOrderedHeuristic



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
    long_name = 'ESP Fever Event Definition 1',
    temperature = 100.4,
    icd9s = ['780.6A', ],
    )

#--- jaundice 
EncounterHeuristic(
    name = 'jaundice',
    long_name = 'Jaundice Event Definition 1',
    icd9s = ['782.4'],
    )

#--- chronic_hep_b 
EncounterHeuristic(
    name = 'chronic_hep_b',
    long_name = 'Chronic Hep B Event Definition 1',
    icd9s = ['070.32'],
    )

#--- chronic_hep_c 
EncounterHeuristic(
    name = 'chronic_hep_c',
    long_name = 'Chronic Hep C Event Definition 1',
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
    long_name = 'Gonorrhea Test',
    ratio = None, # This test should never have numeric results
    )

#--- chlamydia_pos 
LabResultHeuristic(
    name = 'chlamydia',
    long_name = 'Chlamydia Test',
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
    long_name = 'Hepatitis B Core AB',
    negative_events = True,
    )

#--- hep_b_surface
LabResultHeuristic(
    name = 'hep_b_surface',
    long_name = 'Hepatitis B Surface AB',
    negative_events = True,
    )

#--- hep_b_e_antigen
LabResultHeuristic(
    name = 'hep_b_e_antigen',
    long_name = 'Hep B "e" Antigen',
    )


# NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm

#--- hep_b_viral_dna
LabResultHeuristic(
    name = 'hep_b_viral_dna',
    long_name = 'Hep B Viral DNA',
    )

#--- hep_e_ab 
LabResultHeuristic(
    name = 'hep_e_ab',
    long_name = 'Hep E Antibody',
    )

#--- total_bilirubin_high 
LabResultHeuristic(
    name = 'total_bilirubin_high',
    long_name = 'High Total Bilirubin',
    )

#--- high_calc_bilirubin 
CalculatedBilirubinHeuristic()

#--- hep_c_signal_cutoff 
LabResultHeuristic(
    name = 'hep_c_signal_cutoff',
    long_name = 'Hep C Signal Cutoff',
    negative_events = True,
    )

#--- hep_c_riba 
LabResultHeuristic(
    name = 'hep_c_riba',
    long_name = 'Hep C RIBA',
    negative_events = True,
    )

#--- hep_c_rna 
LabResultHeuristic(
    name = 'hep_c_rna',
    long_name = 'Hep C RNA',
    negative_events = True,
    )

#--- hep_c_elisa 
LabResultHeuristic(
    name = 'hep_c_elisa',
    long_name = 'Hep C ELISA',
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
    long_name = 'Lyme IGG Test',
    )

#--- lyme_igg_wb
WesternBlotHeuristic(
    name = 'lyme_igg_wb',
    long_name = 'Lyme Western Blot Positive Event Definition 1',
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
    long_name = 'Lyme Disease Diagnosis Event Definition 1',
    icd9s = ['088.81'],
    )

#--- rash 
EncounterHeuristic(
    name = 'rash',
    long_name = 'Rash Event Definition 1',
    icd9s = ['782.1'],
    )

#--- doxycycline 
MedicationHeuristic(
    name = 'doxycycline',
    long_name = 'Doxycycline Event Definition 1',
    drugs = ['doxycycline'],
    )

#--- lyme_other_antibiotics 
MedicationHeuristic(
    name = 'lyme_other_antibiotics',
    long_name = 'Lyme Disease Non - Doxycycline Antibiotics Event Definition 1',
    drugs = ['Amoxicillin', 'Cefuroxime', 'Ceftriaxone', 'Cefotaxime'],
    )


# 
# Pelvic Inflamatory Disease (PID)
#


#--- pid_diagnosis
EncounterHeuristic(
    name = 'pid_diagnosis',
    long_name = 'PID Diagnosis Event Definition 1',
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
    long_name = 'Tuberculosis Medications',
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
    long_name = 'Tuberculosis Diagnosis Event Definition 1',
    icd9s = [
        '010.',
        '018.',
        ],
    match_style = 'istartswith',
    )

#--- tb_lab
LabResultHeuristic(
    name = 'tb_lab',
    long_name = 'Tuberculosis Lab Order Event Definition 1',
    order_events = True,
    )

