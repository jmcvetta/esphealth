'''
                                  ESP Health
                          Heuristic Events Framework
                               Event Definitions

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from ESP.hef.core import EncounterHeuristic, StringMatchLabHeuristic, HighNumericLabHeuristic
from ESP.hef.core import FeverHeuristic, CalculatedBilirubinHeuristic


# These definitions do not necessarily *need* to be assigned to variables.  The mere
# act of instantiating a BaseHeuristic instance causes that instance to be
# registered with the heuristics framework, and therefore to be called by
# BaseHeuristic.generate_all_events().  


#===============================================================================
#
#--- ~~~ Encounter Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



fever = FeverHeuristic()

jaundice = EncounterHeuristic(name='jaundice', 
                              verbose_name='Jaundice, not of newborn',
                              icd9s=['782.4'],
                              )

chronic_hep_b = EncounterHeuristic(name='chronic_hep_b',
                                   verbose_name='Chronic Hepatitis B',
                                   icd9s=['070.32'],
                                   )


#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


GONORRHEA_LOINCS = ['691-6', '23908-7', '24111-7', '36902-5'] # Re-used in disease definition
gonorrhea = StringMatchLabHeuristic(
    name =          'gonorrhea', 
    verbose_name =  'Gonorrhea', 
    loinc_nums =    GONORRHEA_LOINCS,
    strings =       ['positiv', 'detect'], 
    abnormal_flag = True, 
    match_type =    'istartswith',
    )

CHLAMYDIA_LOINCS = ['4993-2', '6349-5', '16601-7', '20993-2', '21613-5', '36902-5', ] # Re-used in disease definition
chlamydia = StringMatchLabHeuristic(
    name =          'chlamydia', 
    verbose_name =  'Chlamydia', 
    loinc_nums =    CHLAMYDIA_LOINCS,
    strings =       ['positiv', 'detect'], 
    abnormal_flag = True, 
    match_type =    'istartswith',
    )





alt_2x = HighNumericLabHeuristic(
    name='alt_2x',
    verbose_name='Alanine aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=2,
    default_high=132,
    )

alt_5x = HighNumericLabHeuristic(
    name='alt_5x',
    verbose_name='Alanine aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=5,
    default_high=330,
    )

ast_2x = HighNumericLabHeuristic(
    name='ast_2x',
    verbose_name='Aspartate aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=2,
    default_high=132,
    )

ast_5x = HighNumericLabHeuristic(
    name='ast_5x',
    verbose_name='Aspartate aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=5,
    default_high=330,
    )

hep_a_igm_ab = StringMatchLabHeuristic(
    name='hep_a_igm_ab',
    verbose_name='IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)',
    loinc_nums=['22314-9'],
    strings=['reactiv'],
    )

hep_b_igm_ab = StringMatchLabHeuristic(
    name='hep_b_igm_ab',
    verbose_name='IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['31204-1'],
    strings=['reactiv'],
    )

hep_b_surface = StringMatchLabHeuristic(
    name='hep_b_surface',
    verbose_name='Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['5195-3'],
    strings=['reactiv'],
    )

no_hep_b_surface = StringMatchLabHeuristic(
    # This is the exactly the same as hep_b_surface above, but with 'exclude'
    # flag set.
    name = 'no_hep_b_surface',
    verbose_name = 'EXCLUDE: Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['5195-3'],
    strings = ['reactiv'],
    exclude = True,
    )

hep_b_e_antigen = StringMatchLabHeuristic(
    name = 'hep_b_e_antigen',
    verbose_name = 'Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['13954-3'],
    strings=['reactiv'],
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
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['13126-8', '16934', '5009-6'],
    strings = ['positiv', 'detect'],
    )
hep_b_viral_dna_part2 = HighNumericLabHeuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['16934-2'],
    default_high = 100,
    allow_duplicate_name=True,
    )
hep_b_viral_dna_part3 = HighNumericLabHeuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['5009-6'],
    default_high = 160,
    allow_duplicate_name=True,
    )


hep_e_ab = StringMatchLabHeuristic(
    name = 'hep_a_ab',
    verbose_name = 'Hepatitis E antibody',
    loinc_nums = ['14212-5'],
    strings = ['reactiv'],
    )

hep_c_ab = StringMatchLabHeuristic(
    name = 'hep_c_ab',
    verbose_name = 'Hepatitis C antibody = "REACTIVE" (may be truncated)',
    loinc_nums = ['16128-1'],
    strings = ['reactiv'],
    )

total_bilirubin_high = HighNumericLabHeuristic(
    name = 'total_bilirubin_high',
    verbose_name = 'Total bilirubin > 1.5',
    loinc_nums = ['33899-6'],
    default_high = 1.5,
    )

high_calc_bilirubin = CalculatedBilirubinHeuristic()

hep_c_signal_cutoff = HighNumericLabHeuristic(
    name = 'hep_c_signal_cutoff',
    verbose_name = 'Hepatitis C Signal Cutoff Ratio',
    loinc_nums = ['MDPH-144',],
    default_high = 3.8,
    )

hep_c_riba = StringMatchLabHeuristic(
    name = 'hep_c_riba',
    verbose_name = 'Hepatitis C RIBA = "POSITIVE"',
    loinc_nums = ['5199-5'],
    strings = ['positiv'],
    )

hep_c_rna = StringMatchLabHeuristic(
    name = 'hep_c_rna',
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['6422-0'],
    strings = ['detected'],
    )
HighNumericLabHeuristic(
    name = 'hep_c_rna',
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['10676-5'],
    default_high = 100,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    name = 'hep_c_rna',
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['38180-6'],
    default_high = 2.79,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    name = 'hep_c_rna',
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['34704-7'],
    default_high = 50,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    name = 'hep_c_rna',
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['11259-9'],
    default_high = 10,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    name = 'hep_c_rna',
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['20416-4'],
    default_high = 0.70,
    allow_duplicate_name = True,
    )
HighNumericLabHeuristic(
    name = 'hep_c_rna',
    verbose_name = 'Hepatitis C RNA',
    loinc_nums = ['34703-9'],
    default_high = 500,
    allow_duplicate_name = True,
    )
