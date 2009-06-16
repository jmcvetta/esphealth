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

fever = FeverHeuristic(
    heuristic_name = 'esp-fever',
    def_name = 'ESP Fever Event Definition 1',
    def_version = 1,
    temperature = 100.4,
    icd9s = ['780.6A',],
    )

jaundice = EncounterHeuristic(
    heuristic_name = 'jaundice', 
    def_name = 'Jaundice Event Definition 1',
    def_version = 1,
    icd9s = ['782.4'],
    )

chronic_hep_b = EncounterHeuristic(
    heuristic_name = 'chronic_hep_b',
    def_name = 'Chronic Hep B Event Definition 1',
    def_version = 1,
    icd9s=['070.32'],
    )

chronic_hep_c = EncounterHeuristic(
    heuristic_name='chronic_hep_c',
    def_name = 'Chronic Hep C Event Definition 1',
    def_version = 1,
    icd9s=['070.54', '070.70',],
    )


#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GONORRHEA_LOINCS = ['691-6', '23908-7', '24111-7', '36902-5'] # Re-used in disease definition
gonorrhea = StringMatchLabHeuristic(
    heuristic_name = 'gonorrhea', 
    def_name = 'Gonorrhea Definition 1',
    def_version = 1,
    loinc_nums = GONORRHEA_LOINCS,
    strings = POSITIVE_STRINGS,
    abnormal_flag = True, 
    match_type = 'istartswith',
    )

CHLAMYDIA_LOINCS = ['4993-2', '6349-5', '16601-7', '20993-2', '21613-5', '36902-5', ] # Re-used in disease definition
chlamydia = StringMatchLabHeuristic(
    heuristic_name = 'chlamydia', 
    def_name = 'Chlamydia Event Definition 1',
    def_version = 1,
    loinc_nums = CHLAMYDIA_LOINCS,
    strings = POSITIVE_STRINGS,
    abnormal_flag = True, 
    match_type = 'istartswith',
    )

alt_2x = NumericLabHeuristic(
    heuristic_name = 'alt_2x',
    def_name = 'ALT 2x Event Definition 1',
    def_version = 1,
    loinc_nums=['1742-6'],
    comparison = '>',
    ratio=2,
    default_high=132,
    )

alt_5x = NumericLabHeuristic(
    heuristic_name = 'alt_5x',
    def_name = 'ALT 5x Event Definition 1',
    def_version = 1,
    loinc_nums=['1742-6'],
    comparison = '>',
    ratio=5,
    default_high=330,
    )

ast_2x = NumericLabHeuristic(
    heuristic_name = 'ast_2x',
    def_name = 'AST 2x Event Definition 1',
    def_version = 1,
    loinc_nums=['1920-8'],
    comparison = '>',
    ratio=2,
    default_high=132,
    )

ast_5x = NumericLabHeuristic(
    heuristic_name = 'ast_5x',
    def_name = 'AST 5x Event Definition 1',
    def_version = 1,
    loinc_nums=['1920-8'],
    comparison = '>',
    ratio=5,
    default_high=330,
    )

alt_400 = NumericLabHeuristic(
    heuristic_name = 'alt_400',
    def_name = 'ALT >400 Event Definition 1',
    def_version = 1,
    loinc_nums=['1742-6'],
    comparison = '>',
    default_high=400,
    )

hep_a_igm_ab = StringMatchLabHeuristic(
    heuristic_name = 'hep_a_igm_ab',
    def_name = 'Hep A IgM Event Definition 1',
    def_version = 1,
    loinc_nums=['22314-9'],
    strings = POSITIVE_STRINGS,
    )

no_hep_a_igm_ab = StringMatchLabHeuristic(
    heuristic_name = 'no_hep_a_igm_ab',
    def_name = 'No Hep A IgM Event Definition 1',
    def_version = 1,
    loinc_nums=['22314-9'],
    strings = NEGATIVE_STRINGS,
    )

hep_b_igm_ab = StringMatchLabHeuristic(
    heuristic_name = 'hep_b_igm_ab',
    def_name = 'Hep B IgM Event Definition 1',
    def_version = 1,
    loinc_nums = ['31204-1'],
    strings = POSITIVE_STRINGS,
    )

no_hep_b_igm_ab = StringMatchLabHeuristic(
    heuristic_name = 'no_hep_b_igm_ab',
    def_name = 'No Hep B IgM Event Definition 1',
    def_version = 1,
    loinc_nums = ['31204-1'],
    strings = NEGATIVE_STRINGS,
    )

no_hep_b_core_ab = StringMatchLabHeuristic(
    heuristic_name = 'no_hep_b_core_ab',
    def_name = 'No Hep B Core Event Definition 1',
    def_version = 1,
    loinc_nums = ['16933-4'],
    strings = NEGATIVE_STRINGS,
    )

hep_b_surface = StringMatchLabHeuristic(
    heuristic_name = 'hep_b_surface',
    def_name = 'Hep B Surface Event Definition 1',
    def_version = 1,
    loinc_nums = ['5195-3'],
    strings = POSITIVE_STRINGS,
    )

no_hep_b_surface = StringMatchLabHeuristic(
    heuristic_name = 'no_hep_b_surface',
    def_name = 'No Hep B Surface Event Definition 1',
    def_version = 1,
    loinc_nums = ['5195-3'],
    strings = NEGATIVE_STRINGS,
    )

hep_b_e_antigen = StringMatchLabHeuristic(
    heuristic_name = 'hep_b_e_antigen',
    def_name = 'Hep B "e" Antigen Event Definition 1',
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
#
hep_b_viral_dna = StringMatchLabHeuristic(
    heuristic_name = 'hep_b_viral_dna',
    def_name = 'Hep B Viral DNA Event Definition 1',
    def_version = 1,
    loinc_nums = ['13126-8', '16934', '5009-6'],
    strings = POSITIVE_STRINGS,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_b_viral_dna',
    def_name = 'Hep B Viral DNA Event Definition 2',
    def_version = 1,
    loinc_nums = ['16934-2'],
    comparison = '>',
    default_high = 100,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_b_viral_dna',
    def_name = 'Hep B Viral DNA Event Definition 3',
    def_version = 1,
    loinc_nums = ['5009-6'],
    comparison = '>',
    default_high = 160,
    )

hep_e_ab = StringMatchLabHeuristic(
    heuristic_name = 'hep_e_ab',
    def_name = 'Hep E Antibody Event Definition 1',
    def_version = 1,
    loinc_nums = ['14212-5'],
    strings = POSITIVE_STRINGS,
    )

hep_c_ab = StringMatchLabHeuristic(
    heuristic_name = 'hep_c_ab',
    def_name = 'Hep C AB Event Definition 1',
    def_version = 1,
    loinc_nums = ['16128-1'],
    strings = POSITIVE_STRINGS,
    )

total_bilirubin_high = NumericLabHeuristic(
    heuristic_name = 'total_bilirubin_high',
    def_name = 'High Total Bilirubin Event Definition 1',
    def_version = 1,
    loinc_nums = ['33899-6'],
    comparison = '>',
    default_high = 1.5,
    )

high_calc_bilirubin = CalculatedBilirubinHeuristic()

hep_c_signal_cutoff = NumericLabHeuristic(
    heuristic_name = 'hep_c_signal_cutoff',
    def_name = 'Hep C Signal Cutoff Event Definition 1',
    def_version = 1,
    loinc_nums = ['MDPH-144',],
    comparison = '>',
    default_high = 3.8,
    )

no_hep_c_signal_cutoff = NumericLabHeuristic(
    # This is the exactly the same as hep_c_signal_cutoff above, but with 'exclude'
    # flag set.
    heuristic_name = 'hep_c_signal_cutoff',
    def_name = 'No Hep C Signal Cutoff Event Definition 1',
    def_version = 1,
    loinc_nums = ['MDPH-144',],
    comparison = '>',
    default_high = 3.8,
    exclude = True,
    )

hep_c_riba = StringMatchLabHeuristic(
    heuristic_name = 'hep_c_riba',
    def_name = 'Hep C RIBA Event Definition 1',
    def_version = 1,
    loinc_nums = ['5199-5'],
    strings = POSITIVE_STRINGS,
    )

no_hep_c_riba = StringMatchLabHeuristic(
    heuristic_name = 'no_hep_c_riba',
    def_name = 'No Hep C RIBA Event Definition 1',
    def_version = 1,
    loinc_nums = ['5199-5'],
    strings = NEGATIVE_STRINGS,
    )

hep_c_rna = StringMatchLabHeuristic(
    heuristic_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 1',
    def_version = 1,
    loinc_nums = ['6422-0'],
    strings = POSITIVE_STRINGS,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 2',
    def_version = 1,
    loinc_nums = ['10676-5'],
    comparison = '>',
    default_high = 100,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 3',
    def_version = 1,
    loinc_nums = ['38180-6'],
    comparison = '>',
    default_high = 2.79,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 4',
    def_version = 1,
    loinc_nums = ['34704-7'],
    comparison = '>',
    default_high = 50,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 5',
    def_version = 1,
    loinc_nums = ['11259-9'],
    comparison = '>',
    default_high = 10,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 6',
    def_version = 1,
    loinc_nums = ['20416-4'],
    comparison = '>',
    default_high = 0.70,
    )
NumericLabHeuristic(
    heuristic_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 7',
    def_version = 1,
    loinc_nums = ['34703-9'],
    comparison = '>',
    default_high = 500,
    )

no_hep_c_rna = StringMatchLabHeuristic(
    heuristic_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 1',
    def_version = 1,
    loinc_nums = ['6422-0'],
    strings = NEGATIVE_STRINGS,
    )
NumericLabHeuristic(
    heuristic_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 2',
    def_version = 1,
    loinc_nums = ['10676-5'],
    comparison = '>',
    default_high = 100,
    exclude = True,
    )
NumericLabHeuristic(
    heuristic_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 3',
    def_version = 1,
    loinc_nums = ['38180-6'],
    comparison = '>',
    default_high = 2.79,
    exclude = True,
    )
NumericLabHeuristic(
    heuristic_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 4',
    def_version = 1,
    loinc_nums = ['34704-7'],
    comparison = '>',
    default_high = 50,
    exclude = True,
    )
NumericLabHeuristic(
    heuristic_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 5',
    def_version = 1,
    loinc_nums = ['11259-9'],
    comparison = '>',
    default_high = 10,
    exclude = True,
    )
NumericLabHeuristic(
    heuristic_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 6',
    def_version = 1,
    loinc_nums = ['20416-4'],
    comparison = '>',
    default_high = 0.70,
    exclude = True,
    )
NumericLabHeuristic(
    heuristic_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 7',
    def_version = 1,
    loinc_nums = ['34703-9'],
    comparison = '>',
    default_high = 500,
    exclude = True,
    )

hep_c_elisa = StringMatchLabHeuristic(
    heuristic_name = 'hep_c_elisa', 
    def_name = 'Hep C ELISA Event Definition 1',
    def_version = 1,
    loinc_nums = ['16128-1',],
    strings = POSITIVE_STRINGS,
    abnormal_flag = True,  # appropriate here?
    match_type = 'istartswith',
    )

no_hep_c_elisa = StringMatchLabHeuristic(
    heuristic_name = 'no_hep_c_elisa', 
    def_name = 'No Hep C ELISA Event Definition 1',
    def_version = 1,
    loinc_nums = ['16128-1',],
    strings = POSITIVE_STRINGS,
    abnormal_flag = True,  # appropriate here?
    match_type = 'istartswith',
    exclude = True,
    )


#
# Lyme Disease  --  experimental
#

lyme_elisa_pos = NumericLabHeuristic(
    heuristic_name='lyme_elisa_pos', 
    def_name='Lyme ELISA Event Definition 1',
    def_version = 1,
    loinc_nums = ['5061-7'],
    comparison = '>=',
    default_high = 1.1,
    )
StringMatchLabHeuristic(
    heuristic_name='lyme_elisa_pos', 
    def_name='Lyme ELISA Event Definition 2',
    def_version = 1,
    loinc_nums = ['31155-5'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
    )

lyme_elisa_ordered = LabOrderedHeuristic(
    heuristic_name = 'lyme_elisa_ordered',
    def_name = 'Lyme ELISA Test Order Event Definition 1',
    def_version = 1,
    loinc_nums = ['5061-7', '31155-5'],
    )

#
# TODO: lyme_igg will also need a new event class for "IMBLOT B.BURG 49736" lab
#
lyme_igg = NumericLabHeuristic(
    heuristic_name = 'lyme_igg',
    def_name = 'Lyme IGG Event Definition 1 (EIA)',
    def_version = 1,
    loinc_nums = ['16481-4'],
    comparison = '>=',
    default_high = 1,
    )
StringMatchLabHeuristic(
    heuristic_name='lyme_igg',
    def_name = 'Lyme IGG Event Definition 2 (WB)',
    def_version = 1,
    loinc_nums = ['29898-4'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
    )
WesternBlotHeuristic(
    heuristic_name = 'lyme_igg',
    def_name = 'Lyme Western Blot Event Definition 1',
    def_version = 1,
    loinc_nums = ['29898-4',], # Can we get a different LOINC for this, not used by string tests?
    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
    band_count = 5,
    )

lyme_igm = NumericLabHeuristic(
    heuristic_name = 'lyme_igm',
    def_name = 'Lyme IGM Event Definition 1 (EIA)',
    def_version = 1,
    loinc_nums = ['16482-2'],
    comparison = '>=',
    default_high = 1,
    )
StringMatchLabHeuristic(
    heuristic_name = 'lyme_igm',
    def_name = 'Lyme IGM Event Definition 2 (WB)',
    def_version = 1,
    loinc_nums = ['23982-2'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
    )

lyme_pcr = StringMatchLabHeuristic(
    heuristic_name = 'lyme_pcr',
    def_name = 'Lyme PCR Event Definition 1',
    def_version = 1,
    loinc_nums = ['4991-6'],
    strings = POSITIVE_STRINGS,
    match_type = 'istartswith',
    )
    
lyme_diagnosis = EncounterHeuristic(
    heuristic_name = 'lyme_diagnosis', 
    def_name = 'Lyme Disease Diagnosis Event Definition 1',
    def_version = 1,
    icd9s = ['088.81'],
    )

rash = EncounterHeuristic(
    heuristic_name = 'rash', 
    def_name = 'Rash Event Definition 1',
    def_version = 1,
    icd9s = ['782.1'],
    )

doxycycline = MedicationHeuristic(
    heuristic_name = 'doxycycline',
    def_name = 'Doxycycline Event Definition 1',
    def_version = 1,
    drugs = ['doxycycline'],
    )

lyme_other_antibiotics = MedicationHeuristic(
    heuristic_name = 'lyme_other_antibiotics',
    def_name = 'Lyme Disease Non-Doxycycline Antibiotics Event Definition 1',
    def_version = 1,
    drugs = ['Amoxicillin', 'Cefuroxime', 'Ceftriaxone', 'Cefotaxime'],
    )
