'''
                                  ESP Health
                          Heuristic Events Framework
                               Event Definitions

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from ESP.hef.hef import EncounterHeuristic, StringMatchLabHeuristic, HighNumericLabHeuristic
from ESP.hef.hef import FeverHeuristic, CalculatedBilirubinHeuristic



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
    event_name = 'esp-fever',
    def_name = 'ESP Fever Event Definition 1',
    version = 1,
    temperature = 100.4,
    icd9s = ['780.6A',],
    )

jaundice = EncounterHeuristic(
    event_name = 'jaundice', 
    def_name = 'Jaundice Event Definition 1',
    version = 1,
    verbose_name = 'Jaundice, not of newborn',
    icd9s = ['782.4'],
    )

chronic_hep_b = EncounterHeuristic(
    event_name = 'chronic_hep_b',
    def_name = 'Chronic Hep B Event Definition 1',
    version = 1,
    verbose_name = 'Chronic Hepatitis B',
    icd9s=['070.32'],
    )

chronic_hep_c = EncounterHeuristic(
    event_name='chronic_hep_c',
    def_name = 'Chronic Hep C Event Definition 1',
    version = 1,
    verbose_name='Chronic Hepatitis C',
    icd9s=['070.54', '070.70',],
    )


#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GONORRHEA_LOINCS = ['691-6', '23908-7', '24111-7', '36902-5'] # Re-used in disease definition
gonorrhea = StringMatchLabHeuristic(
    event_name = 'gonorrhea', 
    def_name = 'Gonorrhea Definition 1',
    version = 1,
    verbose_name =  'Gonorrhea', 
    loinc_nums = GONORRHEA_LOINCS,
    strings = POSITIVE_STRINGS,
    abnormal_flag = True, 
    match_type = 'istartswith',
    )

CHLAMYDIA_LOINCS = ['4993-2', '6349-5', '16601-7', '20993-2', '21613-5', '36902-5', ] # Re-used in disease definition
chlamydia = StringMatchLabHeuristic(
    event_name = 'chlamydia', 
    def_name = 'Chlamydia Event Definition 1',
    version = 1,
    verbose_name = 'Chlamydia', 
    loinc_nums = CHLAMYDIA_LOINCS,
    strings = POSITIVE_STRINGS,
    abnormal_flag = True, 
    match_type = 'istartswith',
    )

alt_2x = HighNumericLabHeuristic(
    event_name = 'alt_2x',
    def_name = 'ALT 2x Event Definition 1',
    version = 1,
    verbose_name='Alanine aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=2,
    default_high=132,
    )

alt_5x = HighNumericLabHeuristic(
    event_name = 'alt_5x',
    def_name = 'ALT 5x Event Definition 1',
    version = 1,
    verbose_name='Alanine aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=5,
    default_high=330,
    )

ast_2x = HighNumericLabHeuristic(
    event_name = 'ast_2x',
    def_name = 'AST 2x Event Definition 1',
    version = 1,
    verbose_name='Aspartate aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=2,
    default_high=132,
    )

ast_5x = HighNumericLabHeuristic(
    event_name = 'ast_5x',
    def_name = 'AST 5x Event Definition 1',
    version = 1,
    verbose_name='Aspartate aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=5,
    default_high=330,
    )

alt_400 = HighNumericLabHeuristic(
    event_name = 'alt_400',
    def_name = 'ALT >400 Event Definition 1',
    version = 1,
    verbose_name='Alanine aminotransferase (ALT) >400',
    loinc_nums=['1742-6'],
    default_high=400,
    )

hep_a_igm_ab = StringMatchLabHeuristic(
    event_name = 'hep_a_igm_ab',
    def_name = 'Hep A IgM Event Definition 1',
    version = 1,
    verbose_name='IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)',
    loinc_nums=['22314-9'],
    strings = POSITIVE_STRINGS,
    )

no_hep_a_igm_ab = StringMatchLabHeuristic(
    event_name = 'no_hep_a_igm_ab',
    def_name = 'No Hep A IgM Event Definition 1',
    version = 1,
    verbose_name='IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)',
    loinc_nums=['22314-9'],
    strings = NEGATIVE_STRINGS,
    )

hep_b_igm_ab = StringMatchLabHeuristic(
    event_name = 'hep_b_igm_ab',
    def_name = 'Hep B IgM Event Definition 1',
    version = 1,
    verbose_name='IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['31204-1'],
    strings = POSITIVE_STRINGS,
    )

no_hep_b_igm_ab = StringMatchLabHeuristic(
    event_name = 'no_hep_b_igm_ab',
    def_name = 'No Hep B IgM Event Definition 1',
    version = 1,
    verbose_name='IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['31204-1'],
    strings = NEGATIVE_STRINGS,
    )

no_hep_b_core_ab = StringMatchLabHeuristic(
    event_name = 'no_hep_b_core_ab',
    def_name = 'No Hep B Core Event Definition 1',
    version = 1,
    verbose_name='NEGATIVE: General antibody to Hepatitis B Core Antigen',
    loinc_nums = ['16933-4'],
    strings = NEGATIVE_STRINGS,
    )

hep_b_surface = StringMatchLabHeuristic(
    event_name = 'hep_b_surface',
    def_name = 'Hep B Surface Event Definition 1',
    version = 1,
    verbose_name='Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['5195-3'],
    strings = POSITIVE_STRINGS,
    )

no_hep_b_surface = StringMatchLabHeuristic(
    event_name = 'no_hep_b_surface',
    def_name = 'No Hep B Surface Event Definition 1',
    version = 1,
    verbose_name = 'EXCLUDE: Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['5195-3'],
    strings = NEGATIVE_STRINGS,
    )

hep_b_e_antigen = StringMatchLabHeuristic(
    event_name = 'hep_b_e_antigen',
    def_name = 'Hep B "e" Antigen Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)',
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
    event_name = 'hep_b_viral_dna',
    def_name = 'Hep B Viral DNA Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['13126-8', '16934', '5009-6'],
    strings = POSITIVE_STRINGS,
    )
HighNumericLabHeuristic(
    event_name = 'hep_b_viral_dna',
    def_name = 'Hep B Viral DNA Event Definition 2',
    version = 1,
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['16934-2'],
    default_high = 100,
    allow_duplicate_name=True,
    )
hep_b_viral_dna_part3 = HighNumericLabHeuristic(
    event_name = 'hep_b_viral_dna',
    def_name = 'Hep B Viral DNA Event Definition 3',
    version = 1,
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['5009-6'],
    default_high = 160,
    allow_duplicate_name=True,
    )

hep_e_ab = StringMatchLabHeuristic(
    event_name = 'hep_e_ab',
    def_name = 'Hep E Antibody Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis E antibody',
    loinc_nums = ['14212-5'],
    strings = POSITIVE_STRINGS,
    )

hep_c_ab = StringMatchLabHeuristic(
    event_name = 'hep_c_ab',
    def_name = 'Hep C AB Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C antibody = "REACTIVE" (may be truncated)',
    loinc_nums = ['16128-1'],
    strings = POSITIVE_STRINGS,
    )

total_bilirubin_high = HighNumericLabHeuristic(
    event_name = 'total_bilirubin_high',
    def_name = 'High Total Bilirubin Event Definition 1',
    version = 1,
    verbose_name = 'Total bilirubin > 1.5',
    loinc_nums = ['33899-6'],
    default_high = 1.5,
    )

high_calc_bilirubin = CalculatedBilirubinHeuristic()

hep_c_signal_cutoff = HighNumericLabHeuristic(
    event_name = 'hep_c_signal_cutoff',
    def_name = 'Hep C Signal Cutoff Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C Signal Cutoff Ratio',
    loinc_nums = ['MDPH-144',],
    default_high = 3.8,
    )

no_hep_c_signal_cutoff = HighNumericLabHeuristic(
    # This is the exactly the same as hep_c_signal_cutoff above, but with 'exclude'
    # flag set.
    event_name = 'hep_c_signal_cutoff',
    def_name = 'No Hep C Signal Cutoff Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C Signal Cutoff Ratio',
    loinc_nums = ['MDPH-144',],
    default_high = 3.8,
    exclude = True,
    )

hep_c_riba = StringMatchLabHeuristic(
    event_name = 'hep_c_riba',
    def_name = 'Hep C RIBA Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C RIBA = "POSITIVE"',
    loinc_nums = ['5199-5'],
    strings = POSITIVE_STRINGS,
    )

no_hep_c_riba = StringMatchLabHeuristic(
    event_name = 'no_hep_c_riba',
    def_name = 'No Hep C RIBA Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C RIBA = "POSITIVE"',
    loinc_nums = ['5199-5'],
    strings = NEGATIVE_STRINGS,
    )

hep_c_rna = StringMatchLabHeuristic(
    event_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['6422-0'],
    strings = POSITIVE_STRINGS,
    )
HighNumericLabHeuristic(
    event_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 2',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['10676-5'],
    default_high = 100,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    event_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 3',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['38180-6'],
    default_high = 2.79,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    event_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 4',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['34704-7'],
    default_high = 50,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    event_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 5',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['11259-9'],
    default_high = 10,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    event_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 6',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['20416-4'],
    default_high = 0.70,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    event_name = 'hep_c_rna',
    def_name = 'Hep C RNA Event Definition 7',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['34703-9'],
    default_high = 500,
    allow_duplicate_name = True,
    )

no_hep_c_rna = StringMatchLabHeuristic(
    event_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['6422-0'],
    strings = NEGATIVE_STRINGS,
    )
HighNumericLabHeuristic(
    event_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 2',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['10676-5'],
    default_high = 100,
    allow_duplicate_name = True,
    exclude = True,
    )
HighNumericLabHeuristic(
    event_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 3',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['38180-6'],
    default_high = 2.79,
    allow_duplicate_name = True,
    exclude = True,
    )
HighNumericLabHeuristic(
    event_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 4',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['34704-7'],
    default_high = 50,
    allow_duplicate_name = True,
    exclude = True,
    )
HighNumericLabHeuristic(
    event_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 5',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['11259-9'],
    default_high = 10,
    allow_duplicate_name = True,
    exclude = True,
    )
HighNumericLabHeuristic(
    event_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 6',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['20416-4'],
    default_high = 0.70,
    allow_duplicate_name = True,
    exclude = True,
    )
HighNumericLabHeuristic(
    event_name = 'no_hep_c_rna',
    def_name = 'No Hep C RNA Event Definition 7',
    version = 1,
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['34703-9'],
    default_high = 500,
    allow_duplicate_name = True,
    exclude = True,
    )

hep_c_elisa = StringMatchLabHeuristic(
    event_name = 'hep_c_elisa', 
    def_name = 'Hep C ELISA Event Definition 1',
    version = 1,
    verbose_name =  'Hepatitis C ELISA = "REACTIVE"', 
    loinc_nums = ['16128-1',],
    strings = POSITIVE_STRINGS,
    abnormal_flag = True,  # appropriate here?
    match_type = 'istartswith',
    )

no_hep_c_elisa = StringMatchLabHeuristic(
    event_name = 'no_hep_c_elisa', 
    def_name = 'No Hep C ELISA Event Definition 1',
    version = 1,
    verbose_name = 'Hepatitis C ELISA = "REACTIVE"', 
    loinc_nums = ['16128-1',],
    strings = POSITIVE_STRINGS,
    abnormal_flag = True,  # appropriate here?
    match_type = 'istartswith',
    exclude = True,
    )
