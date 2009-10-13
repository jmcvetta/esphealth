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
from ESP.hef.core import StringMatchLabHeuristic
from ESP.hef.core import NumericLabHeuristic
from ESP.hef.core import MedicationHeuristic
from ESP.hef.core import FeverHeuristic
from ESP.hef.core import CalculatedBilirubinHeuristic
from ESP.hef.core import WesternBlotHeuristic
from ESP.hef.core import LabOrderedHeuristic



POSITIVE_STRINGS = ['reactiv', 'pos', 'detec']
NEGATIVE_STRINGS = ['non', 'neg', 'not', 'nr']


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
GONORRHEA_LOINCS = ['691-6', '23908-7', '24111-7', '36902-5'] # Re-used in disease definition
StringMatchLabHeuristic(
    name = 'gonorrhea_pos',
    def_name = 'Gonorrhea Definition 1',
    def_version = 1,
    loinc_nums = GONORRHEA_LOINCS,
    strings = POSITIVE_STRINGS,
    abnormal_flag = True,
    match_type = 'istartswith',
    )

#--- chlamydia_pos 
CHLAMYDIA_LOINCS = ['4993-2', '6349-5', '16601-7', '20993-2', '21613-5', '36902-5', ] # Re-used in disease definition
StringMatchLabHeuristic(
    name = 'chlamydia_pos',
    def_name = 'Chlamydia Event Definition 1',
    def_version = 1,
    loinc_nums = CHLAMYDIA_LOINCS,
    strings = POSITIVE_STRINGS,
    abnormal_flag = True,
    match_type = 'istartswith',
    )

#--- alt_2x 
NumericLabHeuristic(
    name = 'alt_2x',
    def_name = 'ALT 2x Event Definition 1',
    def_version = 1,
    loinc_nums = ['1742-6'],
    comparison = '>',
    ratio = 2,
    default_high = 132,
    )

#--- alt_5x 
NumericLabHeuristic(
    name = 'alt_5x',
    def_name = 'ALT 5x Event Definition 1',
    def_version = 1,
    loinc_nums = ['1742-6'],
    comparison = '>',
    ratio = 5,
    default_high = 330,
    )

#--- ast_2x 
NumericLabHeuristic(
    name = 'ast_2x',
    def_name = 'AST 2x Event Definition 1',
    def_version = 1,
    loinc_nums = ['1920-8'],
    comparison = '>',
    ratio = 2,
    default_high = 132,
    )

#--- ast_5x 
NumericLabHeuristic(
    name = 'ast_5x',
    def_name = 'AST 5x Event Definition 1',
    def_version = 1,
    loinc_nums = ['1920-8'],
    comparison = '>',
    ratio = 5,
    default_high = 330,
    )

#--- alt_400 
NumericLabHeuristic(
    name = 'alt_400',
    def_name = 'ALT >400 Event Definition 1',
    def_version = 1,
    loinc_nums = ['1742-6'],
    comparison = '>',
    default_high = 400,
    )

#--- hep_a_igm_pos 
StringMatchLabHeuristic(
    name = 'hep_a_igm_pos',
    def_name = 'Hep A IgM Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['22314-9'],
    strings = POSITIVE_STRINGS,
    )

#--- hep_a_igm_neg 
StringMatchLabHeuristic(
    name = 'hep_a_igm_neg',
    def_name = 'Hep A IgM Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['22314-9'],
    strings = NEGATIVE_STRINGS,
    )

#--- hep_b_igm_pos 
StringMatchLabHeuristic(
    name = 'hep_b_igm_pos',
    def_name = 'Hep B IgM Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['31204-1'],
    strings = POSITIVE_STRINGS,
    )

#--- hep_b_igm_neg 
StringMatchLabHeuristic(
    name = 'hep_b_igm_neg',
    def_name = 'No Hep B IgM Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['31204-1'],
    strings = NEGATIVE_STRINGS,
    )

#--- hep_b_igm_order 
LabOrderedHeuristic(
    name = 'hep_b_igm_order',
    def_name = 'Hep B IgM Order Event Definition 1',
    def_version = 1,
    loinc_nums = ['31204-1'],
    )

#--- hep_b_core_pos 
StringMatchLabHeuristic(
    name = 'hep_b_core_pos',
    def_name = 'No Hep B Core Positive Definition 1',
    def_version = 1,
    loinc_nums = ['16933-4'],
    strings = POSITIVE_STRINGS,
    )

#--- hep_b_core_neg 
StringMatchLabHeuristic(
    name = 'hep_b_core_neg',
    def_name = 'Hep B Core Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['16933-4'],
    strings = NEGATIVE_STRINGS,
    )

#--- hep_b_surface_pos 
StringMatchLabHeuristic(
    name = 'hep_b_surface_pos',
    def_name = 'Hep B Surface Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['5195-3'],
    strings = POSITIVE_STRINGS,
    )

#--- hep_b_surface_pos 
StringMatchLabHeuristic(
    name = 'hep_b_surface_neg',
    def_name = 'Hep B Surface Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['5195-3'],
    strings = NEGATIVE_STRINGS,
    )

#--- hep_b_e_antigen_pos 
StringMatchLabHeuristic(
    name = 'hep_b_e_antigen_pos',
    def_name = 'Hep B "e" Antigen Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['13954-3'],
    strings = POSITIVE_STRINGS,
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
StringMatchLabHeuristic(
    name = 'hep_b_viral_dna_pos',
    def_name = 'Hep B Viral DNA Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['13126-8', '16934', '5009-6'],
    strings = POSITIVE_STRINGS,
    )
NumericLabHeuristic(
    name = 'hep_b_viral_dna_pos',
    def_name = 'Hep B Viral DNA Positive Event Definition 2',
    def_version = 1,
    loinc_nums = ['16934-2'],
    comparison = '>',
    default_high = 100,
    )
NumericLabHeuristic(
    name = 'hep_b_viral_dna_pos',
    def_name = 'Hep B Viral DNA Positive Event Definition 3',
    def_version = 1,
    loinc_nums = ['5009-6'],
    comparison = '>',
    default_high = 160,
    )


#--- hep_e_ab 
StringMatchLabHeuristic(
    name = 'hep_e_ab_pos',
    def_name = 'Hep E Antibody Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['14212-5'],
    strings = POSITIVE_STRINGS,
    )

#--- total_bilirubin_high 
NumericLabHeuristic(
    name = 'total_bilirubin_high',
    def_name = 'High Total Bilirubin Event Definition 1',
    def_version = 1,
    loinc_nums = ['33899-6'],
    comparison = '>',
    default_high = 1.5,
    )

#--- high_calc_bilirubin 
CalculatedBilirubinHeuristic()

#--- hep_c_signal_cutoff 
NumericLabHeuristic(
    name = 'hep_c_signal_cutoff_pos',
    def_name = 'Hep C Signal Cutoff Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['MDPH-144', ],
    comparison = '>',
    default_high = 3.8,
    )

NumericLabHeuristic(
    # This is the exactly the same as hep_c_signal_cutoff above, but with 'exclude'
    # flag set.
    name = 'hep_c_signal_cutoff_neg',
    def_name = 'Hep C Signal Cutoff Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['MDPH-144', ],
    comparison = '<=',
    default_high = 3.8,
    )

#--- hep_c_riba 
StringMatchLabHeuristic(
    name = 'hep_c_riba_pos',
    def_name = 'Hep C RIBA Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['5199-5'],
    strings = POSITIVE_STRINGS,
    )

StringMatchLabHeuristic(
    name = 'hep_c_riba_neg',
    def_name = 'Hep C RIBA Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['5199-5'],
    strings = NEGATIVE_STRINGS,
    )

#--- hep_c_rna 
StringMatchLabHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Event Definition 1',
    def_version = 1,
    loinc_nums = ['6422-'],
    strings = POSITIVE_STRINGS,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Event Definition 2',
    def_version = 1,
    loinc_nums = ['10676-5'],
    comparison = ' > ',
    default_high = 100,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Event Definition 3',
    def_version = 1,
    loinc_nums = ['38180-6'],
    comparison = ' > ',
    default_high = 2.79,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Event Definition 4',
    def_version = 1,
    loinc_nums = ['34704-7'],
    comparison = ' > ',
    default_high = 50,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Event Definition 5',
    def_version = 1,
    loinc_nums = ['11259-9'],
    comparison = ' > ',
    default_high = 10,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Event Definition 6',
    def_version = 1,
    loinc_nums = ['20416-4'],
    comparison = ' > ',
    default_high = 0.70,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_pos',
    def_name = 'Hep C RNA Positive Event Definition 7',
    def_version = 1,
    loinc_nums = ['34703-9'],
    comparison = '>',
    default_high = 500,
    )

#--- no_hep_c_rna 
StringMatchLabHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['6422-0'],
    strings = NEGATIVE_STRINGS,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 2',
    def_version = 1,
    loinc_nums = ['10676-5'],
    comparison = '<=',
    default_high = 100,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 3',
    def_version = 1,
    loinc_nums = ['38180-6'],
    comparison = '<=',
    default_high = 2.79,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 4',
    def_version = 1,
    loinc_nums = ['34704-7'],
    comparison = ' <= ',
    default_high = 50,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 5',
    def_version = 1,
    loinc_nums = ['11259-9'],
    comparison = '<=',
    default_high = 10,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 6',
    def_version = 1,
    loinc_nums = ['20416-4'],
    comparison = '<=',
    default_high = 0.70,
    )
NumericLabHeuristic(
    name = 'hep_c_rna_neg',
    def_name = 'Hep C RNA Negative Event Definition 7',
    def_version = 1,
    loinc_nums = ['34703-9'],
    comparison = '<=',
    default_high = 500,
    )

#--- hep_c_elisa 
StringMatchLabHeuristic(
    name = 'hep_c_elisa_pos',
    def_name = 'Hep C ELISA Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['16128-1', ],
    strings = POSITIVE_STRINGS,
    abnormal_flag = True, # appropriate here?
    match_type = 'istartswith',
    )

StringMatchLabHeuristic(
    name = 'hep_c_elisa_neg',
    def_name = 'Hep C ELISA Negative Event Definition 1',
    def_version = 1,
    loinc_nums = ['16128-1', ],
    strings = NEGATIVE_STRINGS,
    abnormal_flag = True, # appropriate here?
    match_type = 'istartswith',
    )


#
# Lyme Disease
#

#--- lyme_elisa_pos 
NumericLabHeuristic(
    name = 'lyme_elisa_pos',
    def_name = 'Lyme ELISA Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['5061-7'],
    comparison = ' >= ',
    default_high = 1.1,
    )
StringMatchLabHeuristic(
    name = 'lyme_elisa_pos',
    def_name = 'Lyme ELISA Positive Event Definition 2',
    def_version = 1,
    loinc_nums = ['31155-5'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
    )

#--- lyme_elisa_ordered 
LabOrderedHeuristic(
    name = 'lyme_elisa_ordered',
    def_name = 'Lyme ELISA Test Order Event Definition 1',
    def_version = 1,
    loinc_nums = ['5061-7', '31155-5'],
    )

#--- lyme_igg 
NumericLabHeuristic(
    name = 'lyme_igg_pos',
    def_name = 'Lyme IGG Event Positive Definition 1 (EIA)',
    def_version = 1,
    loinc_nums = ['16481-4'],
    comparison = ' >= ',
    default_high = 1,
    )
StringMatchLabHeuristic(
    name = 'lyme_igg_pos',
    def_name = 'Lyme IGG Positive Event Definition 2 (WB)',
    def_version = 1,
    loinc_nums = ['29898-4'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
    )
WesternBlotHeuristic(
    name = 'lyme_igg_pos',
    def_name = 'Lyme Western Blot Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['29898-4', ], # Can we get a different LOINC for this, not used by string tests?
    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
    band_count = 5,
    )

#--- lyme_igm 
NumericLabHeuristic(
    name = 'lyme_igm_pos',
    def_name = 'Lyme IGM Positive Event Definition 1 (EIA)',
    def_version = 1,
    loinc_nums = ['16482-2'],
    comparison = ' >= ',
    default_high = 1,
    )
StringMatchLabHeuristic(
    name = 'lyme_igm_pos',
    def_name = 'Lyme IGM Positive Event Definition 2 (WB)',
    def_version = 1,
    loinc_nums = ['23982-2'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
    )

#--- lyme_pcr 
StringMatchLabHeuristic(
    name = 'lyme_pcr_pos',
    def_name = 'Lyme PCR Positive Event Definition 1',
    def_version = 1,
    loinc_nums = ['4991-6'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
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
        'RIFAMPIN',
        'RIFAMATE',
        'ISONARIF',
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
    loinc_nums = ['11475-1', '11545-1', '17296-5'],
    )

