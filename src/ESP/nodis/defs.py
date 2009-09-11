'''
                                  ESP Health
                         Notifiable Diseases Framework
                              Disease Defintions


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import pprint

from django.db import connection

from ESP.settings import DEFAULT_REPORTABLE_ICD9S
from ESP.hef import events # Load events
from ESP.hef.events import CHLAMYDIA_LOINCS
from ESP.hef.events import GONORRHEA_LOINCS
from ESP.hef.core import BaseHeuristic
from ESP.nodis.core import ComplexEventPattern
from ESP.nodis.core import Condition
from ESP.emr.models import Patient


#-------------------------------------------------------------------------------
#
# Chlamydia
#
#-------------------------------------------------------------------------------

chlamydia_1 = ComplexEventPattern(
    name = 'Chlamydia pattern #1',
    patterns = [
        'chlamydia_pos',
        ],
    operator = 'and',
    )

chlamydia = Condition(
    name = 'chlamydia',
    patterns = [chlamydia_1,],
    match_window = 1, # Irrelevant -- single test is match
    recur_after = 28, # New cases after 28 days
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
    # Report both Chlamydia and Gonorrhea labs
    lab_loinc_nums = CHLAMYDIA_LOINCS + GONORRHEA_LOINCS,
    lab_days_before = 30,
    )



#-------------------------------------------------------------------------------
#
# Gonorrhea
#
#-------------------------------------------------------------------------------

gonorrhea_1 = ComplexEventPattern(
    name = 'Gonorrhea pattern #1',
    patterns = [
        'gonorrhea_pos',
        ],
    operator = 'and',
    )

gonorrhea = Condition(
    name = 'gonorrhea',
    patterns = [gonorrhea_1,],
    match_window = 1, # Irrelevant -- single test is match
    recur_after = 28, # New cases after 28 days
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
    fever = True,
    lab_loinc_nums = GONORRHEA_LOINCS, 
    lab_days_before = 28,
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
    )


#-------------------------------------------------------------------------------
#
# Hepatitis A/B/C
#
#-------------------------------------------------------------------------------

jaundice_alt400 = ComplexEventPattern(
    patterns = [
        'jaundice',
        'alt_400',
        ],
    operator = 'or'
    )
    
no_hep_b_surf = ComplexEventPattern(
    patterns = [
        'hep_b_surface_neg',
        ],
    operator = 'and',
    exclude = [
        'hep_b_igm_order',
        ]
    )

no_hep_b = ComplexEventPattern(
    patterns = [
        'hep_b_igm_neg',
        'hep_b_core_neg',
        no_hep_b_surf,
        ],
    operator = 'or'
    )

hep_c_1 = ComplexEventPattern(
    name = 'Acute Hepatitis C pattern #1', # Name is optional, but desirable on top-level patterns
    patterns = [
        jaundice_alt400,    # (1 or 2)
        'hep_c_elisa_pos',  # 3 positive
        'hep_a_igm_neg',    # 7 negative
        no_hep_b,           # (8 negative or 9 non-reactive)
        ],
    exclude = [
        'hep_c_signal_cutoff_neg', # 4 positive (if done)
        'hep_c_riba_neg',          # 5 positive (if done)
        'hep_c_rna_neg',           # 6 positive (if done)
        ],
    exclude_past = [
        'hep_c_elisa_pos',   # no prior positive 3 or 5 or 6
        'hep_c_riba_pos',    # "
        'hep_c_rna_pos',     # "
        'chronic_hep_b', # no ICD9 (070.54 or 070.70) ever prior to this encounter
        ],
    operator = 'and',
    )


hep_c = Condition(
    name = 'acute_hep_c',
    patterns = [hep_c_1, ],
    match_window = 28, # days
    recur_after = -1, # Never recur
    icd9s = DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
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
    )


