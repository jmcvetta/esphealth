'''
                                  ESP Health
                         Notifiable Diseases Framework
                              Disease Defintions


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from ESP.settings import DEFAULT_REPORTABLE_ICD9S
from ESP.nodis.core import DiseaseDefinition
from ESP.nodis.core import Disease
from ESP.hef.events import jaundice
from ESP.hef.events import fever
from ESP.hef.events import alt_2x
from ESP.hef.events import ast_2x
from ESP.hef.events import alt_5x
from ESP.hef.events import ast_5x
from ESP.hef.events import alt_400
from ESP.hef.events import hep_b_igm_ab
from ESP.hef.events import hep_b_surface
from ESP.hef.events import hep_b_viral_dna
from ESP.hef.events import hep_b_igm_ab
from ESP.hef.events import hep_b_core_ab
from ESP.hef.events import chronic_hep_b
from ESP.hef.events import no_hep_b_surface
from ESP.hef.events import high_calc_bilirubin
from ESP.hef.events import total_bilirubin_high
from ESP.hef.events import gonorrhea as gonorrhea_event
from ESP.hef.events import chlamydia as chlamydia_event
from ESP.hef.events import CHLAMYDIA_LOINCS
from ESP.hef.events import GONORRHEA_LOINCS
from ESP.hef.events import hep_a_igm_ab
from ESP.hef.events import hep_c_elisa
from ESP.hef.events import hep_c_signal_cutoff
from ESP.hef.events import no_hep_c_signal_cutoff
from ESP.hef.events import no_hep_c_riba
from ESP.hef.events import no_hep_c_rna
from ESP.hef.events import no_hep_a_igm_ab
from ESP.hef.events import no_hep_b_igm_ab
from ESP.hef.events import no_hep_b_core_ab
from ESP.hef.events import hep_c_elisa
from ESP.hef.events import hep_c_riba
from ESP.hef.events import hep_c_rna
from ESP.hef.events import no_hep_c_elisa
#
# Lyme Disease
#
from ESP.hef.events import lyme_elisa_pos
from ESP.hef.events import lyme_elisa_ordered
from ESP.hef.events import lyme_igg
from ESP.hef.events import lyme_igm
from ESP.hef.events import lyme_pcr
from ESP.hef.events import lyme_diagnosis
from ESP.hef.events import rash
from ESP.hef.events import doxycycline
from ESP.hef.events import lyme_other_antibiotics



#===============================================================================
#
# Chlamydia
#
#-------------------------------------------------------------------------------

chlamydia_def_1 = DiseaseDefinition(
    name = 'Chlamydia Definition 1',
    version = 1,
    window = 30, # Not applicable, since only one primary event
    require = [
        (chlamydia_event,),
        ],
    )

chlamydia = Disease(
    name = 'chlamydia',
    definitions = [chlamydia_def_1,],
    icd9s = [
        '788.7',
        '099.40',
        '597.80',
        '780.6A',
        '616.0',
        '616.10',
        '623.5',
        '789.07',
        '789.04',
        '789.09',
        '789.03',
        '789.00',
        ],
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    med_names = [
        'azithromycin',
        'levofloxacin',
        'ofloxacin',
        'ciprofloxacin',
        'doxycycline',
        'eryrthromycin',
        'amoxicillin',
        'EES',
        ],
    med_days_before = 7,
    med_days_after = 14,
    # Report both Chlamydia and Gonorrhea labs
    lab_loinc_nums = CHLAMYDIA_LOINCS + GONORRHEA_LOINCS,
    lab_days_before = 30,
    lab_days_after = 30,
    )


#===============================================================================
#
# Gonorrhea
#
#-------------------------------------------------------------------------------

gonorrhea_def_1 = DiseaseDefinition(
    name = 'Gonorrhea Definition 1',
    version = 1,
    window = 30,
    require = [
        (gonorrhea_event,),
        ],
    )

gonorrhea = Disease(
    name = 'gonorrhea',
    definitions = [gonorrhea_def_1,],
    icd9s = [
        '788.7',
        '099.40',
        '597.80',
        '616.0',
        '616.10',
        '623.5',
        '789.07',
        '789.04',
        '789.09',
        '789.03',
        '789.00',
        ],
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = GONORRHEA_LOINCS, 
    lab_days_before = 28,
    lab_days_after = 28,
    med_names = [
        'amoxicillin',
        'cefixime',
        'cefotaxime',
        'cefpodoxime',
        'ceftizoxime',
        'ceftriaxone',
        'gatifloxacin',
        'levofloxacin',
        'ofloxacin',
        'spectinomycin',
        'moxifloxacin',
        ],
    med_days_before = 7,
    med_days_after = 14
    )



#===============================================================================
#
# Hepatitis A
#
#-------------------------------------------------------------------------------

hep_a_def_1 = DiseaseDefinition(
    name = 'Acute Hepatitis A Definition 1',
    version = 1,
    window = 30,
    require = [
        (hep_a_igm_ab, ),
        (jaundice, alt_2x, ast_2x),
        ]
    )
 
acute_hep_a = Disease(
    name = 'acute_hep_a',
    definitions = [hep_a_def_1,],
    icd9s = DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = ['1742-6', '1920-8', '22314-9', '14212-5', '16128-1'],
    lab_days_before = 30,
    lab_days_after = 30,
    )



#===============================================================================
#
# Hepatitis B
#
#-------------------------------------------------------------------------------


'''
Acute Hepatitis B definitions:
1)  (jaundice OR alt_5x OR ast_5x) 
    AND hep_b_igm_ab 
    WITHIN 14 days
2)  (jaundice OR alt_5x OR ast_5x) 
    AND (total_bilirubin_high OR high_calc_bilirubin)
    AND (hep_b_surface OR hep_b_viral_dna)
    WITHIN 21 days
    AND NOT (chronic_hep_b OR hep_b_surface OR hep_b_viral_dna) EVER IN PAST
3)  hep_b_surface
    AND NOT (hep_b_surface OR hep_b_viral_dna OR jaundice) EVER IN PAST
'''
    
hep_b_1 = DiseaseDefinition(
    name = 'Acute Hepatitis B Definition 1',
    version = 1,
    window = 14, # days
    require = [
        (jaundice, alt_5x, ast_5x),
        (hep_b_igm_ab,),
        ]
    )

hep_b_2 = DiseaseDefinition(
    name = 'Acute Hepatitis B Definition 2',
    version = 1,
    window = 21, # days
    require = [
        (jaundice, alt_5x, ast_5x),
        (total_bilirubin_high, high_calc_bilirubin),
        (hep_b_surface, hep_b_viral_dna),
    ],
    exclude = [
        (chronic_hep_b,),
        ],
    exclude_past = [
        (chronic_hep_b, hep_b_surface, hep_b_viral_dna),
        ],
    )

hep_b_3 = DiseaseDefinition(
    name = 'Hepatitis B Definition 3',
    version = 1,
    window = 1, # Not applicable, since only one primary event
    require = [
        (hep_b_surface,),
        ],
    require_past = [
        (no_hep_b_surface,),
        ],
    require_past_window = 365, # 1 year
    exclude = [
        (chronic_hep_b,),
        ],
    exclude_past = [
        (chronic_hep_b, hep_b_surface, hep_b_viral_dna),
        ],
    )


hep_b = Disease(
    name = 'acute_hep_b',
    definitions = [hep_b_1, hep_b_2, hep_b_3],
    icd9s = DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = [
        '1742-6', 
        '1920-8', 
        '31204-1', 
        '5195-3',
        '13954-3',
        '13126-8',
        '5009-6',
        '16943-2',
        '14212-5',
        '22314-9',
        '16128-1',
        ],
    lab_days_before = 14,
    lab_days_after = 14,
    )


#===============================================================================
#
# Hepatitis C
#
#-------------------------------------------------------------------------------

hep_c_1 = DiseaseDefinition(
    name = 'Acute Hepatitis C Definition 1',
    version = 1,
    window = 28, # 28 days
    require = [
        (jaundice, alt_400,), # "(1 or 2)"
        (hep_c_elisa,),       # "3 positive"
        (no_hep_a_igm_ab,),   # "7 negative"
        (no_hep_b_igm_ab, no_hep_b_core_ab,) # "(8 negative or 9 non-reactive)"
        ],
    exclude = [
        (no_hep_c_signal_cutoff,), # "4 positive (if done)"
        (no_hep_c_riba,), # "5 positive (if done)"
        (no_hep_c_rna,), # "6 positive (if done)"
        ],
    exclude_past = [
        (hep_c_elisa, hep_c_riba, hep_c_rna,),  # "no prior positive 3 or 5 or 6"
        (chronic_hep_b,), # "no ICD9 (070.54 or 070.70) ever prior to this encounter"
        ]
    )

hep_c_2 = DiseaseDefinition(
    name = 'Acute Hepatitis C Definition 2',
    version = 1,
    window = 28, # 28 days
    require = [
        (jaundice, alt_400,), # "(1 or 2)"
        (hep_c_rna,),         # "6 positive"
        (no_hep_a_igm_ab,),   # "7 negative"
        (no_hep_b_igm_ab, no_hep_b_core_ab,) # "(8 negative or 9 non-reactive)"
        ],
    exclude = [
        (no_hep_c_signal_cutoff,), # "4 positive (if done)"
        (no_hep_c_riba,), # "5 positive (if done)"
        ],
    exclude_past = [
        (hep_c_elisa, hep_c_riba, hep_c_rna,),  # "no prior positive 3 or 5 or 6"
        (chronic_hep_b,), # "no ICD9 (070.54 or 070.70) ever prior to this encounter"
        ]
    )

hep_c_3 = DiseaseDefinition(
    name = 'Acute Hepatitis C Definition 3',
    version = 1,
    window = 1, # Not relevant, since only 1 require
    require = [
        (hep_c_rna,), # "6 positive"
        ],
    require_past_window = 365, # 12 months
    require_past = [
        (no_hep_c_elisa,) # "record of (3 negative within the prior 12 months)"
        ]
    )

hep_c_4 = DiseaseDefinition(
    name = 'Acute Hepatitis C Definition 4',
    version = 1,
    window = 1, # Not relevant, since only 1 require
    require = [
        (hep_c_elisa,), # "3 positive"
        ],
    require_past_window = 365, # 12 months
    require_past = [
        (no_hep_c_elisa,) # "record of (3 negative within the prior 12 months)"
        ]
    )

hep_c = Disease(
    name = 'acute_hep_c',
    definitions = [hep_c_1, hep_c_2, hep_c_3, hep_c_4],
    icd9s = DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = [
        '16128-1',
        'MDPH-144',
        '6422-0',
        '10676-5',
        '34704-7',
        '38180-6',
        '5012-0',
        '11259-9',
        '20416-4',
        '34703-9',
        '1742-6',
        '31204-1',
        '22314-9',
        ],
    lab_days_before = 28,
    lab_days_after = 28,
    )


#===============================================================================
#
# Lyme Disease
#
#-------------------------------------------------------------------------------

lyme_1 = DiseaseDefinition(
    name = 'Lyme Disease Definition 1',
    version = 1,
    window = 30,
    require = [
        (lyme_elisa_pos, lyme_igg, lyme_igm, lyme_pcr),
        (lyme_diagnosis, doxycycline, lyme_other_antibiotics),
        ],
    )

lyme_2 = DiseaseDefinition(
    name = 'Lyme Disease Definition 2',
    version = 1,
    window = 14,
    require = [
        (lyme_diagnosis,),
        (doxycycline, lyme_other_antibiotics),
        ],
    )

lyme_3 = DiseaseDefinition(
    name = 'Lyme Disease Definition 3',
    version = 1,
    window = 14,
    require = [
        (rash,),
        (lyme_elisa_ordered,),
        (doxycycline,),
        ],
    )


lyme = Disease(
    name = 'lyme',
    definitions = [lyme_1, lyme_2, lyme_3,],
    icd9s = [
        '782.1',
        '711.8',
        '320.7',
        '351.0',
        '723.4',
        '724.4',
        '422.0',
        '426.0',
        '426.12',
        '426.13',
        '780.6',
        ],
    icd9_days_before = 30,
    icd9_days_after = 30,
    fever = True,
    lab_loinc_nums = [
        '5061-7',
        '31155-5',
        '16481-4',
        '16482-2',
        '23982-2',
        '29898-4',
        '4991-6',
        ],
    lab_days_before = 30,
    lab_days_after = 30,
    med_names = [
        'doxycycline',
        'amoxicillin',
        'cefuroxime',
        'ceftriaxone',
        'cefotaxime',
        ],
    med_days_before = 30,
    med_days_after = 30,
    )


#===============================================================================
#
# REVISED EXPERIMENTAL Hepatitis C
#
#-------------------------------------------------------------------------------

exp_hep_c_1 = DiseaseDefinition(
    name = 'Experimental Acute Hepatitis C Definition 1',
    version = 1,
    window = 28, # 28 days
    require = [
        (jaundice, alt_400,), # Symptoms
        (hep_c_elisa, hep_c_rna, hep_c_riba, hep_c_signal_cutoff ), # Blood tests
        ],
    exclude = [
        (hep_a_igm_ab, hep_b_igm_ab, hep_b_core_ab,), # Hep A & B
        (chronic_hep_b,), # If you have chronic, you don't have acute
        ],
    exclude_past = [
        (hep_a_igm_ab, hep_b_igm_ab, hep_b_core_ab,), # Hep A & B
        (chronic_hep_b, hep_c_elisa, hep_c_riba, hep_c_rna,),  # Indicators of chronic Hep C
        ]
    )

exp_hep_c_2 = DiseaseDefinition(
    name = 'Experimental Acute Hepatitis C Definition 2',
    version = 1,
    window = 1, # Not relevant, since only 1 require
    require = [
        (hep_c_elisa, hep_c_rna, hep_c_riba, hep_c_signal_cutoff ), # Blood tests positive
        ],
    require_past_window = 365, # 12 months
    require_past = [
        (no_hep_c_elisa, no_hep_c_rna, no_hep_c_riba, no_hep_c_signal_cutoff ), # Blood tests negative
        ]
    )

exp_hep_c = Disease(
    name = 'exp_acute_hep_c',
    definitions = [exp_hep_c_1, exp_hep_c_2],
    icd9s = DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = [
        '16128-1',
        'MDPH-144',
        '6422-0',
        '10676-5',
        '34704-7',
        '38180-6',
        '5012-0',
        '11259-9',
        '20416-4',
        '34703-9',
        '1742-6',
        '31204-1',
        '22314-9',
        ],
    lab_days_before = 28,
    lab_days_after = 28,
    )

