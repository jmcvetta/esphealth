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
    def_name = 'ESP Fever Event Definition 1',
    def_version = 1,
    temperature = 100.4,
    icd9s = ['780.6A', ],
    )

#--- jaundice 
EncounterHeuristic(
    name = 'jaundice',
    def_name = 'Jaundice Event Definition 1',
    def_version = 1,
    icd9s = ['782.4'],
    )

#--- chronic_hep_b 
EncounterHeuristic(
    name = 'chronic_hep_b',
    def_name = 'Chronic Hep B Event Definition 1',
    def_version = 1,
    icd9s = ['070.32'],
    )

#--- chronic_hep_c 
EncounterHeuristic(
    name = 'chronic_hep_c',
    def_name = 'Chronic Hep C Event Definition 1',
    def_version = 1,
    icd9s = ['070.54', '070.70', ],
    )


#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#--- gonorrhea_pos 
LabResultHeuristic(
    name = 'gonorrhea_pos',
    def_name = 'Gonorrhea Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- chlamydia_pos 
LabResultHeuristic(
    name = 'chlamydia_pos',
    def_name = 'Chlamydia Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- alt_2x 
LabResultHeuristic(
    name = 'alt_2x',
    def_name = 'ALT 2x Event Definition 1',
    def_version = 1,
    ratio = 2,
    result_type = 'positive',
    )

#--- alt_5x 
LabResultHeuristic(
    name = 'alt_5x',
    def_name = 'ALT 5x Event Definition 1',
    def_version = 1,
    ratio = 5,
    result_type = 'positive',
    )

#--- ast_2x 
LabResultHeuristic(
    name = 'ast_2x',
    def_name = 'AST 2x Event Definition 1',
    def_version = 1,
    ratio = 2,
    result_type = 'positive',
    )

#--- ast_5x 
LabResultHeuristic(
    name = 'ast_5x',
    def_name = 'AST 5x Event Definition 1',
    def_version = 1,
    ratio = 5,
    result_type = 'positive',
    )

#--- alt_400 
LabResultHeuristic(
    name = 'alt_400',
    def_name = 'ALT >400 Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- hep_a_igm_pos 
LabResultHeuristic(
    name = 'hep_a_igm_pos',
    def_name = 'Hep A IgM Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- hep_a_igm_neg 
LabResultHeuristic(
    name = 'hep_a_igm_neg',
    def_name = 'Hep A IgM Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )

#--- hep_b_igm_pos 
LabResultHeuristic(
    name = 'hep_b_igm_pos',
    def_name = 'Hep B IgM Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- hep_b_igm_neg 
LabResultHeuristic(
    name = 'hep_b_igm_neg',
    def_name = 'No Hep B IgM Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )

#--- hep_b_igm_order 
LabOrderedHeuristic(
    name = 'hep_b_igm_order',
    def_name = 'Hep B IgM Order Event Definition 1',
    def_version = 1,
    )

#--- hep_b_core_pos 
LabResultHeuristic(
    name = 'hep_b_core_pos',
    def_name = 'No Hep B Core Positive Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- hep_b_core_neg 
LabResultHeuristic(
    name = 'hep_b_core_neg',
    def_name = 'Hep B Core Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )

#--- hep_b_surface_pos 
LabResultHeuristic(
    name = 'hep_b_surface_pos',
    def_name = 'Hep B Surface Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- hep_b_surface_pos 
LabResultHeuristic(
    name = 'hep_b_surface_neg',
    def_name = 'Hep B Surface Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )

#--- hep_b_e_antigen_pos 
LabResultHeuristic(
    name = 'hep_b_e_antigen_pos',
    def_name = 'Hep B "e" Antigen Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#
# Hep B Viral DNA
#
# There are three different heuristics here, a string match and a two numeric
# comparisons, all of which indicate the same condition.  Thus I have assigned
# them all the same name, so they will be identical in searches of heuristic
# events.  I think this is an okay scheme, but it doesn't quite feel elegant;
# so let me know if you can think of a better way to do it
#
#
# NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm


#--- hep_b_viral_dna
LabResultHeuristic(
    name = 'hep_b_viral_dna_pos',
    def_name = 'Hep B Viral DNA Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )


#--- hep_e_ab 
LabResultHeuristic(
    name = 'hep_e_ab_pos',
    def_name = 'Hep E Antibody Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- total_bilirubin_high 
LabResultHeuristic(
    name = 'total_bilirubin_high',
    def_name = 'High Total Bilirubin Event Definition 1',
    def_version = 1,
    loinc_nums = ['33899-6'],
    default_high = 1.5,
    result_type = 'positive',
    )

#--- high_calc_bilirubin 
CalculatedBilirubinHeuristic()

#--- hep_c_signal_cutoff 
LabResultHeuristic(
    name = 'hep_c_signal_cutoff_pos',
    def_name = 'Hep C Signal Cutoff Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

LabResultHeuristic(
    name = 'hep_c_signal_cutoff_neg',
    def_name = 'Hep C Signal Cutoff Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )

#--- hep_c_riba 
LabResultHeuristic(
    name = 'hep_c_riba_pos',
    def_name = 'Hep C RIBA Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

LabResultHeuristic(
    name = 'hep_c_riba_neg',
    def_name = 'Hep C RIBA Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )

#--- hep_c_rna 
LabResultHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- no_hep_c_rna 
LabResultHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )

#--- hep_c_elisa 
LabResultHeuristic(
    name = 'hep_c_elisa_pos',
    def_name = 'Hep C ELISA Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

LabResultHeuristic(
    name = 'hep_c_elisa_neg',
    def_name = 'Hep C ELISA Negative Event Definition 1',
    def_version = 1,
    result_type = 'negative',
    )


#
# Lyme Disease
#

#--- lyme_elisa_pos 
LabResultHeuristic(
    name = 'lyme_elisa_pos',
    def_name = 'Lyme ELISA Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- lyme_elisa_ordered 
LabOrderedHeuristic(
    name = 'lyme_elisa_ordered',
    def_name = 'Lyme ELISA Test Order Event Definition 1',
    def_version = 1,
    )

#--- lyme_igg 
LabResultHeuristic(
    name = 'lyme_igg_pos',
    def_name = 'Lyme IGG Event Positive Definition 1 (EIA)',
    def_version = 1,
    result_type = 'positive',
    )
WesternBlotHeuristic(
    name = 'lyme_igg_pos',
    def_name = 'Lyme Western Blot Positive Event Definition 1',
    def_version = 1,
    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
    band_count = 5,
    )

#--- lyme_igm 
LabResultHeuristic(
    name = 'lyme_igm_pos',
    def_name = 'Lyme IGM Positive Event Definition 1 (EIA)',
    def_version = 1,
    result_type = 'positive',
    )

#--- lyme_pcr 
LabResultHeuristic(
    name = 'lyme_pcr_pos',
    def_name = 'Lyme PCR Positive Event Definition 1',
    def_version = 1,
    result_type = 'positive',
    )

#--- lyme_diagnosis 
EncounterHeuristic(
    name = 'lyme_diagnosis',
    def_name = 'Lyme Disease Diagnosis Event Definition 1',
    def_version = 1,
    icd9s = ['088.81'],
    )

#--- rash 
EncounterHeuristic(
    name = 'rash',
    def_name = 'Rash Event Definition 1',
    def_version = 1,
    icd9s = ['782.1'],
    )

#--- doxycycline 
MedicationHeuristic(
    name = 'doxycycline',
    def_name = 'Doxycycline Event Definition 1',
    def_version = 1,
    drugs = ['doxycycline'],
    )

#--- lyme_other_antibiotics 
MedicationHeuristic(
    name = 'lyme_other_antibiotics',
    def_name = 'Lyme Disease Non - Doxycycline Antibiotics Event Definition 1',
    def_version = 1,
    drugs = ['Amoxicillin', 'Cefuroxime', 'Ceftriaxone', 'Cefotaxime'],
    )


# 
# Pelvic Inflamatory Disease (PID)
#


#--- pid_diagnosis
EncounterHeuristic(
    name = 'pid_diagnosis',
    def_name = 'PID Diagnosis Event Definition 1',
    def_version = 1,
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
    def_name = 'Tuberculosis Medications',
    def_version = 1,
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
    def_name = 'Tuberculosis Diagnosis Event Definition 1',
    def_version = 1,
    icd9s = [
        '010.',
        '018.',
        ],
    match_style = 'istartswith',
    )

#--- tb_lab_order 
LabOrderedHeuristic(
    name = 'tb_lab_order',
    def_name = 'Tuberculosis Lab Order Event Definition 1',
    def_version = 1,
    )

