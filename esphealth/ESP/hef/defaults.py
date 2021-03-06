'''
                                  ESP Health
                          Heuristic Events Framework
                        Default Lab & Event Definitions

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL
'''

from ESP.hef.base import AbstractLabTest
from ESP.hef.base import BaseHeuristic
from ESP.hef.base import LabOrderHeuristic
from ESP.hef.base import LabResultAnyHeuristic
from ESP.hef.base import LabResultPositiveHeuristic
from ESP.hef.base import LabResultRatioHeuristic
from ESP.hef.base import LabResultFixedThresholdHeuristic
from ESP.hef.base import LabResultRangeHeuristic
from ESP.hef.base import Dx_CodeQuery
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import PrescriptionHeuristic
from ESP.hef.base import Dose
from ESP.hef.base import ResultString
from ESP.hef.base import CalculatedBilirubinHeuristic

#-------------------------------------------------------------------------------
#
# Legacy Event Support
#
#-------------------------------------------------------------------------------

# All events created by previous version of HEF will be bound to this heuristic.
legacy_heuristic = BaseHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    id = 0,
    #name = 'Legacy Heuristic',
    )[0]


#-------------------------------------------------------------------------------
#
# Doses
#
#-------------------------------------------------------------------------------

dose_1g = Dose.objects.get_or_create(quantity = 1, units = 'g')[0] # @UndefinedVariable. Eclipse static code analysis can't see objects
dose_2g = Dose.objects.get_or_create(quantity = 2, units = 'g')[0] # @UndefinedVariable. Eclipse static code analysis can't see objects


#-------------------------------------------------------------------------------
#
# Result Strings
#
#-------------------------------------------------------------------------------
ResultString.objects.get_or_create(
    value = 'reactiv',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'pos',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'detec',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'confirm',
    indicates = 'pos',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'non',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'neg',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'not det',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'nr',
    indicates = 'neg',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'indeterminate',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'not done',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )
ResultString.objects.get_or_create(
    value = 'tnp',
    indicates = 'ind',
    match_type = 'istartswith',
    applies_to_all = True,
    )

#-------------------------------------------------------------------------------
#
#  Vaers labs 
#
#-------------------------------------------------------------------------------
hemoglobin_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hemoglobin',
    defaults = {
        'verbose_name': 'Hemoglobin test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hemoglobin_test,
    )

wbc_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'wbc',
    defaults = {
        'verbose_name': 'wbc test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = wbc_test,
    )

neutrophils_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'neutrophils',
    defaults = {
        'verbose_name': 'Neutrophils test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = neutrophils_test,
    )

eosinophils_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'eosinophils',
    defaults = {
        'verbose_name': 'Eosinophils test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = eosinophils_test,
    )

lymphocytes_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lymphocytes',
    defaults = {
        'verbose_name': 'Lymphocytes test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lymphocytes_test,
    )

platelet_count_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'platelet_count',
    defaults = {
        'verbose_name': 'Platelet count test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = platelet_count_test,
    )

creatinine_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'creatinine',
    defaults = {
        'verbose_name': 'Creatinine test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = creatinine_test,
    )

alk_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'alk',
    defaults = {
        'verbose_name': 'ALK test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = alk_test,
    )

ptt_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ptt',
    defaults = {
        'verbose_name': 'PTT test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ptt_test,
    )

creatinine_kinase_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'creatinine_kinase',
    defaults = {
        'verbose_name': 'Creatinine kinase test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = creatinine_kinase_test,
    )

potassium_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'potassium',
    defaults = {
        'verbose_name': 'Potassium test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = potassium_test,
    )

sodium_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'sodium',
    defaults = {
        'verbose_name': 'Sodium test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = sodium_test,
    )

calcium_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'calcium',
    defaults = {
        'verbose_name': 'Calcium test',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = calcium_test,
    )
#-------------------------------------------------------------------------------
#
# Gonorrhea
#
#-------------------------------------------------------------------------------

gonorrhea_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'gonorrhea',
    defaults = {
        'verbose_name': 'Gonorrhea test',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = gonorrhea_test,
    )

#-------------------------------------------------------------------------------
#
# Pertussis
#
#-------------------------------------------------------------------------------

pertussis_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pertussis_dx,
    dx_code_exact = '033.0'
    )

cough_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'cough'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = cough_dx,
    dx_code_exact = '033.9'
    )
#
# Prescriptions
#
pertussis_antibiotics = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_antibiotics',
    drugs = 'erythromyciin','clarithromycin','azithromycin','trimethoprim-sulfamethoxazole', 
    )[0]

pertussis_culture = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_culture',
    defaults = {
        'verbose_name': 'pertussis culture',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_culture,
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_culture,
    )

pertussis_pcr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_pcr',
    defaults = {
        'verbose_name': 'pertussis pcr',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_pcr,
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_pcr,
    )

pertussis_serology = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_serology',
    defaults = {
        'verbose_name': 'pertussis serology',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_serology,
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_serology,
    )
#-------------------------------------------------------------------------------
#
# Chlamydia
#
#-------------------------------------------------------------------------------

chlamydia_test = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'chlamydia',
    defaults = {
        'verbose_name': 'Chlamydia test',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = chlamydia_test,
    )


#-------------------------------------------------------------------------------
#
# ALT
#
#-------------------------------------------------------------------------------

alt = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'alt',
    defaults = {
        'verbose_name': 'Alanine Aminotransferase blood test',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = alt,
    )

LabResultRatioHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = alt,
    ratio = 2,
    )

LabResultRatioHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = alt,
    ratio = 5,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = alt,
    threshold = 400,
    )

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = alt,
    )
#-------------------------------------------------------------------------------
#
# AST
#
#-------------------------------------------------------------------------------

ast = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ast',
    defaults = {
        'verbose_name': 'Aspartate Aminotransferase blood test',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ast,
    )

LabResultRatioHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ast,
    ratio = 2,
    )

LabResultRatioHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ast,
    ratio = 5,
    )

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ast,
    )
#-------------------------------------------------------------------------------
#
# Hepatitis A
#
#-------------------------------------------------------------------------------

hep_a_igm_antibody = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_a_igm_antibody',
    defaults = {
        'verbose_name': 'Hepatitis A IgM antibody',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_a_igm_antibody,
    )

hep_a_tot_antibody = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_a_total_antibody',
    defaults = {
        'verbose_name': 'Hepatitis A Total Antibodies',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_a_tot_antibody,
    )


#-------------------------------------------------------------------------------
#
# Hepatitis B
#
#-------------------------------------------------------------------------------

jaundice_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'jaundice'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = jaundice_dx,
    dx_code_exact = '782.4'
    )

chronic_hep_c = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'chronic_hep_c'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = chronic_hep_c,
    dx_code_exact = '070.54',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = chronic_hep_c,
    dx_code_exact = '070.70',
    )

chronic_hep_b = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'chronic_hep_b'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = chronic_hep_b,
    dx_code_exact = '070.32',
    )

hep_b_igm_antibody = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_b_igm_antibody',
    defaults = {
        'verbose_name': 'Hepatitis B core IgM antibody',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_b_igm_antibody,
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_b_igm_antibody,
    )

hep_b_core_antibody = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_b_core_antibody',
    defaults = {
        'verbose_name': 'Hepatitis B core general antibody',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_b_core_antibody,
    )

hep_b_surface_antigen = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_b_surface_antigen',
    defaults = {
        'verbose_name': 'Hepatitis B surface antigen',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_b_surface_antigen,
    )


hep_b_e_antigen = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_b_e_antigen',
    defaults = {
        'verbose_name': 'Hepatitis B "e" antigen',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_b_e_antigen,
    )


# NOTE:  See note in Hepatitis B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm


hep_b_viral_dna = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_b_viral_dna',
    defaults = {
        'verbose_name': 'Hepatitis B viral DNA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_b_viral_dna,
    )

#-------------------------------------------------------------------------------
#
# Hepatitis E
#
#-------------------------------------------------------------------------------

hep_e_antibody = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_e_antibody',
    defaults = {
        'verbose_name': 'Hepatitis E antibody',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_e_antibody,
    )

#-------------------------------------------------------------------------------
#
# Bilirubin
#
#-------------------------------------------------------------------------------

bilirubin_total = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'bilirubin_total',
    defaults = {
        'verbose_name': 'Bilirubin glucuronidated + bilirubin non-glucuronidated',
        }
    )[0]

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = bilirubin_total,
    threshold = 1.5,
    )
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = bilirubin_total,
    )

    
bilirubin_direct = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'bilirubin_direct',
    defaults = {
        'verbose_name': 'Bilirubin glucuronidated',
        }
    )[0]
    
bilirubin_indirect = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'bilirubin_indirect',
    defaults = {
        'verbose_name': 'Bilirubin non-glucuronidated',
        }
    )[0]

CalculatedBilirubinHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    threshold = 1.5,
    )[0]

    
#-------------------------------------------------------------------------------
#
# Hepatitis C
#
#-------------------------------------------------------------------------------

hep_c_signal_cutoff = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_c_signal_cutoff',
    defaults = {
        'verbose_name': 'Hepatitis C signal cutoff',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_c_signal_cutoff,
    )

hep_c_riba = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_c_riba',
    defaults = {
        'verbose_name': 'Hepatitis C RIBA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_c_riba,
    )

hep_c_rna = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_c_rna',
    defaults = {
        'verbose_name': 'Hepatitis C RNA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_c_rna,
    )

hep_c_elisa = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'hep_c_elisa',
    defaults = {
        'verbose_name': 'Hepatitis C ELISA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = hep_c_elisa,
    )


#-------------------------------------------------------------------------------
#
# Lyme
#
#-------------------------------------------------------------------------------

lyme_elisa = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme_elisa',
    defaults = {
        'verbose_name': 'Lyme ELISA',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_elisa,
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_elisa,
    )

lyme_igg_eia = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme_igg_eia',
    defaults = {
        'verbose_name': 'Lyme IGG (EIA)',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_igg_eia,
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_igg_eia,
    )

lyme_igm_eia = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme_igm_eia',
    defaults = {
        'verbose_name': 'Lyme IGM (EIA)',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_igm_eia,
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_igm_eia,
    )

# Western blot IGG is resulted in bands, some of which are significant; but western 
# blot IGM is resulted as a standard lab test with POSTIVE result string.

#WesternBlotHeuristic(
#    name = 'lyme_igg_wb',
#    long_name = 'Lyme Western Blot IGG',
#    interesting_bands = [18, 21, 28, 30, 39, 41, 45, 58, 66, 93],
#    band_count = 5,
#    )

#
# TODO: issue 336 This test needs a western blot heuristic see above !
#
lyme_igg_wb = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme_igg_wb',
    defaults = {
        'verbose_name': 'Lyme IGG (Western Blot)',
        }
    )[0]
    
lyme_igm_wb = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme_igm_wb',
    defaults = {
        'verbose_name': 'Lyme IGM (Western Blot)',
        }
    )[0]
    
# Despite being a western blot, this test is resulted pos/neg
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_igm_wb,
    )

# 
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_igg_wb,
    )

lyme_pcr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme_pcr',
    defaults = {
        'verbose_name': 'Lyme PCR',
        }
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_pcr,
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = lyme_pcr,
    )


lyme_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme',
    )[0]

foo = Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = lyme_dx,
    dx_code_exact = '088.81',
    )[0]


rash_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'rash',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = rash_dx,
    dx_code_exact = '782.1',
    )

doxycycline_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'doxycycline',
    drugs = 'doxycycline',
    )[0]

lyme_antibio_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lyme_other_antibiotics',
    drugs = 'Amoxicillin, Cefuroxime, Ceftriaxone, Cefotaxime',
    )[0]


#-------------------------------------------------------------------------------
#
# Pelvic Inflamatory Disease (PID)
#
#-------------------------------------------------------------------------------

pelvic_inflamatory_disease = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pelvic_inflamatory_disease',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pelvic_inflamatory_disease,
    dx_code_exact = '614.0',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pelvic_inflamatory_disease,
    dx_code_exact = '614.1',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pelvic_inflamatory_disease,
    dx_code_exact = '614.2',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pelvic_inflamatory_disease,
    dx_code_exact = '614.3',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pelvic_inflamatory_disease,
    dx_code_exact = '614.5',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pelvic_inflamatory_disease,
    dx_code_exact = '614.9',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pelvic_inflamatory_disease,
    dx_code_exact = '099.56',
    )

#-------------------------------------------------------------------------------
#
# Tuberculosis
#
#-------------------------------------------------------------------------------

pyrazinamide_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pyrazinamide',
    drugs = 'Pyrazinamide, PZA',
    exclude = ['CAPZA',],
    )[0]

isoniazid_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'isoniazid',
    drugs = 'Isoniazid',
    exclude = ['INHAL', 'INHIB',],
    )[0]

ethambutol_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ethambutol',
    drugs = 'Ethambutol',
    )[0]

rifampin_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'rifampin',
    drugs = 'rifampin',
    )[0]

rifabutin_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'rifabutin',
    drugs = 'rifabutin',
    )[0]

rifapentine_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'rifapentine',
    drugs = 'rifapentine',
    )[0]

streptomycin_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'streptomycin',
    drugs = 'streptomycin',
    )[0]

para_aminosalicyclic_acid_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'para_aminosalicyclic_acid',
    drugs = 'para-aminosalicyclic-acid',
    )[0]

kanamycin_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'kanamycin',
    drugs = 'kanamycin',
    )[0]

capreomycin_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'capreomycin',
    drugs = 'capreomycin',
    )[0]

cycloserine_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'cycloserine',
    drugs = 'cycloserine',
    )[0]

ethionamide_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ethionamide',
    drugs = 'ethionamide',
    )[0]

moxifloxacin_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'moxifloxacin',
    drugs = 'moxifloxacin',
    )[0]

# 010.00-018.99
tb_diagnosis = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'tuberculosis',
    )[0]
    
Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '010.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '011.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '012.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '013.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '014.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '015.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '016.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '017.',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = tb_diagnosis,
    dx_code_starts_with = '018.',
    )[0]

# lab orders for tb  
tb_pcr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'tuberculosis_prc',
    defaults = {
        'verbose_name': 'Tuberculosis PCR',
        }
    )[0]
      
LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = tb_pcr,
    )

tb_afb = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'tuberculosis_afb',
    defaults = {
        'verbose_name': 'Tuberculosis afb',
        }
    )[0]
    
LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = tb_afb,
    )

tb_culture = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'tuberculosis_culture',
    defaults = {
        'verbose_name': 'Tuberculosis culture',
        }
    )[0]
    
LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = tb_culture,
    )

#-------------------------------------------------------------------------------
#
# Syphilis 
#
#-------------------------------------------------------------------------------

penicillin_g_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'penicillin_g',
    drugs = 'penicillin g, pen g'
    )[0]

doxycycline_7_days_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'doxycycline_7_days',
    drugs = 'doxycycline',
    min_quantity = 14, # Need 14 pills for 7 days
    )[0]

ceftriaxone_1g_2g_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ceftriaxone_1g_2g',
    drugs = 'ceftriaxone',
    )[0]
ceftriaxone_1g_2g_rx.dose.add(dose_1g)
ceftriaxone_1g_2g_rx.dose.add(dose_2g)

syphilis_diagnosis = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'syphilis',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '090.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '091.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '092.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '093.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '094.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '095.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '096.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = syphilis_diagnosis,
    dx_code_starts_with = '097.',
    )

syphilis_tppa = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'syphilis_tppa',
    defaults = {
        'verbose_name': 'Syphilis TP-PA',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = syphilis_tppa,
    )
    
syphilis_fta_abs = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'syphilis_fta_abs',
    defaults = {
        'verbose_name': 'Syphilis FTA-ABS',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = syphilis_fta_abs,
    )

syphilis_rpr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'syphilis_rpr',
    defaults = {
        'verbose_name': 'Syphilis rapid plasma reagin (RPR)',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = syphilis_rpr,
    titer = 8, # 1:8 titer
    )

syphilis_vdrl_serum = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'syphilis_vdrl_serum',
    defaults = {
        'verbose_name': 'Syphilis VDRL serum',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = syphilis_vdrl_serum,
    titer = 8, # 1:8 titer
    )

syphilis_tp_igg = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'syphilis_tp_igg',
    defaults = {
        'verbose_name': 'Syphilis TP-IGG',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = syphilis_tp_igg,
    )

syphilis_vdrl_csf = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'syphilis_vdrl_csf',
    defaults = {
        'verbose_name': 'Syphilis VDRL-CSF',
        }
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = syphilis_vdrl_csf,
    titer = 1, # 1:1 titer
    )


#-------------------------------------------------------------------------------
#
# Glucose
#
#-------------------------------------------------------------------------------

glucose_fasting = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glucose_fasting',
    defaults = {
        'verbose_name':  'Fasting glucose (several variations)',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = glucose_fasting,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = glucose_fasting,
    threshold = 126,
    date_field = 'result'
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = glucose_fasting,
    minimum = 100,
    minimum_match_type = 'gte',
    maximum = 125,
    maximum_match_type = 'lte',
    )

glucose_random = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glucose-random',
    defaults = {
        'verbose_name':  'Random glucose (several variations)',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = glucose_random,
    )

gcrf_result = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glucose_compound_random_fasting_result',
    defaults = {
        'verbose_name':  'Compound Random/Fasting glucose test, result component',
        }
    )[0]
    
gcrf_flag = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glucose_compound_random_fasting_flag',
    defaults = {
        'verbose_name':  'Compound Random/Fasting glucose test, flag component',
        }
    )[0]

#-------------------------------------------------------------------------------
#
# Oral Glucose Tolerance Test 50g (OGTT50)
#
#-------------------------------------------------------------------------------

ogtt50_fasting = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt50_fasting',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 50 gram Fasting',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_fasting,
    date_field = 'result'
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_fasting,
    date_field = 'result'
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_fasting,
    date_field = 'result',
    threshold = 95,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_fasting,
    date_field = 'result',
    threshold = 126,
    )

ogtt50_random = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt50_random',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 50 gram Random',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_random,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_random,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_random,
    date_field = 'result',
    threshold = 190,
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_random,
    minimum = 140,
    minimum_match_type = 'gte',
    maximum = 200,
    maximum_match_type = 'lt',
    )

ogtt50_1hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt50_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 50 gram 1 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_1hr,
    date_field = 'result'
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_1hr,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt50_1hr,
    date_field = 'result',
    threshold = 190,
    )

#-------------------------------------------------------------------------------
#
# Oral Glucose Tolerance Test 75g (OGTT 75)
#
#-------------------------------------------------------------------------------

ogtt75_series = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt75_series',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram Series',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_series,
    )

ogtt75_fasting = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt75_fasting',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram fasting',
        }
    )[0]

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_fasting,
    )

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting,
    date_field = 'result'
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting,
    date_field = 'result'
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting,
    minimum = 100,
    minimum_match_type = 'gte',
    maximum = 125,
    maximum_match_type = 'lt',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting,
    date_field = 'result',
    threshold = 92,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting,
    date_field = 'result',
    threshold = 95,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting,
    date_field = 'result',
    threshold = 126,
    )

ogtt75_fasting_urine = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt75_fasting_urine',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram fasting, urine',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting_urine,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting_urine,
    date_field = 'result',
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_fasting_urine,
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_fasting_urine,
    date_field = 'result'
    )

ogtt75_30min = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt75_30min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 30 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_30min,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_30min,
    date_field = 'result',
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_30min,
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_30min,
    minimum = 140,
    minimum_match_type = 'gte',
    maximum = 200,
    maximum_match_type = 'lt',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_30min,
    date_field = 'result',
    threshold = 200,
    )

ogtt75_1hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt75_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 1 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_1hr,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_1hr,
    date_field = 'result',
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_1hr,
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_1hr,
    minimum = 140,
    minimum_match_type = 'gte',
    maximum = 200,
    maximum_match_type = 'lt',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_1hr,
    date_field = 'result',
    threshold = 180,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_1hr,
    date_field = 'result',
    threshold = 200,
    )

ogtt75_90min = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt75_90min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 90 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_90min,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_90min,
    date_field = 'result',
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_90min,
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_90min,
    minimum = 140,
    minimum_match_type = 'gte',
    maximum = 200,
    maximum_match_type = 'lt',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_90min,
    date_field = 'result',
    threshold = 180,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_90min,
    date_field = 'result',
    threshold = 200,
    )

ogtt75_2hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt75_2hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 75 gram 2 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_2hr,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_2hr,
    date_field = 'result',
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_2hr,
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test=ogtt75_2hr,
    minimum = 140,
    minimum_match_type = 'gte',
    maximum = 200,
    maximum_match_type = 'lt',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_2hr,
    date_field = 'result',
    threshold = 153,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_2hr,
    date_field = 'result',
    threshold = 155,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt75_2hr,
    date_field = 'result',
    threshold = 200,
    )

#-------------------------------------------------------------------------------
#
# Oral Gluclose Tolerance Test 100g (OGTT 100)
#
#-------------------------------------------------------------------------------

ogtt100_fasting = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_fasting',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram fasting',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_fasting,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_fasting,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_fasting,
    date_field = 'result',
    threshold = 95,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_fasting,
    date_field = 'result',
    threshold = 126,
    )

ogtt100_fasting_urine = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_fasting_urine',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram fasting (urine)',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_fasting_urine,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_fasting_urine,
    date_field = 'result',
    )

ogtt100_30min = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_30min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 30 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_30min,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_30min,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_30min,
    date_field = 'result',
    threshold = 200,
    )

ogtt100_1hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_1hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 1 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_1hr,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_1hr,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_1hr,
    date_field = 'result',
    threshold = 180,
    )

ogtt100_90min = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_90min',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 90 minutes post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_90min,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_90min,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_90min,
    date_field = 'result',
    threshold = 180,
    )

ogtt100_2hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_2hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 2 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_2hr,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_2hr,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_2hr,
    date_field = 'result',
    threshold = 155,
    )

ogtt100_3hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_3hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 3 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_3hr,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_3hr,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_3hr,
    date_field = 'result',
    threshold = 140,
    )

ogtt100_4hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_4hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 4 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_4hr,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_4hr,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_4hr,
    date_field = 'result',
    threshold = 140,
    )

ogtt100_5hr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ogtt100_5hr',
    defaults = {
        'verbose_name':  'Oral Glucose Tolerance Test 100 gram 5 hour post',
        }
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_5hr,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_5hr,
    date_field = 'result',
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ogtt100_5hr,
    date_field = 'result',
    threshold = 140,
    )


#-------------------------------------------------------------------------------
#
# Glycated hemoglobin (A1C)
#
#-------------------------------------------------------------------------------

a1c = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'a1c',
    defaults = {
        'verbose_name':  'Glycated hemoglobin (A1C)',
        }
    )[0]
    
LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = a1c,
    date_field = 'result',
    )

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = a1c,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = a1c,
    date_field = 'result',
    threshold = 6.0,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = a1c,
    date_field = 'result',
    threshold = 6.5,
    )

LabResultRangeHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = a1c,
    minimum = 5.7,
    minimum_match_type = 'gte',
    maximum = 6.4,
    maximum_match_type = 'lte',
    )

pregnancy_diagnosis = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pregnancy',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pregnancy_diagnosis,
    dx_code_starts_with = 'V22.',
    )

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pregnancy_diagnosis,
    dx_code_starts_with = 'V23.',
    )

#
#
##--- pregnancy
#PregnancyHeuristic() # No config needed
#

gdm_diagnosis = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'gestational_diabetes',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = gdm_diagnosis,
    dx_code_starts_with = '648.8',
    )

lancets_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'lancets',
    drugs = 'lancets',
    )[0]

test_strips_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'test_strips',
    drugs = 'test strips',
    )

insulin_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'insulin',
    defaults = {
	    'drugs': 'insulin',
	    'exclude': 'syringe',
	    }
    )

#-------------------------------------------------------------------------------
#
# Giardiasis
#
#-------------------------------------------------------------------------------

giardiasis_antigen = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'giardiasis_antigen',
    defaults = {
        'verbose_name': 'Giardiasis Antigen',
        },
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = giardiasis_antigen,
    )


metronidazole_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'metronidazole',
    drugs = 'metronidazole',
    )

diahrrhea_diagnosis = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'diarrhea',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = diahrrhea_diagnosis,
    dx_code_exact = '787.91',
    )


#-------------------------------------------------------------------------------
#
# Pertussis
#
#-------------------------------------------------------------------------------

pertussis_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis',
    )[0]
    
Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = pertussis_dx,
    dx_code_exact = '033.0',
    )

cough_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'cough',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = cough_dx,
    dx_code_exact = '033.9',
    )

#
# Needs new functionality to examine comment string
#
pertussis_pcr = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_pcr',
    defaults = {
        'verbose_name': 'Pertussis PCR',
        },
    )[0]

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_pcr,
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_pcr,
    )

#
# Needs new functionality to examine comment string
#
pertussis_culture = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_culture',
    defaults = {
        'verbose_name': 'Pertussis Culture',
        },
    )[0]

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_culture,
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_culture,
    )

pertussis_serology = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_serology',
    defaults = {
        'verbose_name': 'Pertussis serology',
        },
    )[0]

LabOrderHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_serology,
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = pertussis_culture,
    )

pertussis_rx = PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pertussis_med',
    drugs =  'Erythromycin, Clarithromycin, Azithromycin, Trimethoprim-sulfamethoxazole',
    )[0]


#-------------------------------------------------------------------------------
#
#--- Diabetes Drugs
#
#-------------------------------------------------------------------------------

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glyburide',
    drugs =  'glyburide',
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'gliclazide',
    drugs =  'gliclazide'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glipizide',
    drugs =  'glipizide'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glimepiride',
    drugs =  'glimepiride'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pioglitazone',
    drugs =  'pioglitazone'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'rosiglitazone',
    drugs =  'rosiglitazone'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'repaglinide',
    drugs =  'repaglinide'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'nateglinide',
    drugs =  'nateglinide'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'meglitinide',
    drugs =  'meglitinide'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'sitagliptin',
    drugs =  'sitagliptin'
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'exenatide',
    drugs =  'exenatide, pramlintide',
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pramlintide',
    drugs =  'pramlintide',
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'pramlintide',
    drugs =  'pramlintide',
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'metformin',
    drugs =  'metformin',
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'glucagon',
    drugs =  'glucagon',
    )

PrescriptionHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'acetone',
    drugs =  'acetone',
    )


#-------------------------------------------------------------------------------
#
#--- Diabetes Diagnoses
#
#-------------------------------------------------------------------------------

diabetes_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'diabetes_all_types',
    )[0]
    
Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = diabetes_dx,
    dx_code_starts_with = '250.',
    )

diabetes_type_1_ns_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'diabetes_type_1_not_stated'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = diabetes_type_1_ns_dx,
    dx_code_starts_with = '250.',
    dx_code_ends_with = '1',
    )

diabetes_type_1_uncont_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'diabetes_type_1_uncontrolled'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = diabetes_type_1_uncont_dx,
    dx_code_starts_with = '250.',
    dx_code_ends_with = '3',
    )

diabetes_type_2_ns_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'diabetes_type_2_not_stated'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = diabetes_type_2_ns_dx,
    dx_code_starts_with = '250.',
    dx_code_ends_with = '0',
    )

diabetes_type_2_uncont_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'diabetes_type_2_uncontrolled'
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = diabetes_type_2_uncont_dx,
    dx_code_starts_with = '250.',
    dx_code_ends_with = '2',
    )

abnormal_glucose_dx = DiagnosisHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'abnormal_glucose',
    )[0]

Dx_CodeQuery.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    heuristic = abnormal_glucose_dx,
    dx_code_starts_with = '648.8',
    )


#-------------------------------------------------------------------------------
#
#--- Diabetes Lab Tests
#
#-------------------------------------------------------------------------------

gad65 = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'gad65',
    defaults = {
        'verbose_name': 'Glutamic Acid Decarboxylase (GAD65) Antibodies',
        },
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = gad65,
    )


ica512 = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'ica512',
    defaults = {
        'verbose_name': 'Islet cell autoantigen (ICA) 512',
        },
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ica512,
    )


ic_ab_screen = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'islet_cell_antibody',
    defaults = {
        'verbose_name': 'Islet cell antibody screen',
        },
    )[0]

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = ic_ab_screen,
    titer = 4, # 1:4 titer
    )


insulin_ab = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'insulin_antibody',
    defaults = {
        'verbose_name': 'Insulin Antibody',
        },
    )[0]
    
LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = insulin_ab,
    )


c_peptide = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'c_peptide',
    defaults = {
        'verbose_name': 'C-Peptide',
        },
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = c_peptide,
    )

LabResultFixedThresholdHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = c_peptide,
    date_field = 'result',
    threshold = 1,
    )

cholesterol_hdl = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'cholesterol_hdl',
    defaults = {
        'verbose_name': 'High Density Lipoprotein cholesterol',
        },
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = cholesterol_hdl,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = cholesterol_hdl,
    date_field = 'result',
    )


cholesterol_ldl = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'cholesterol_ldl',
    defaults = {
        'verbose_name': 'Low Density Lipoprotein cholesterol',
        },
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = cholesterol_ldl,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = cholesterol_ldl,
    date_field = 'result',
    )


cholesterol_total = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'cholesterol_total',
    defaults = {
        'verbose_name': 'Total Cholesterol',
        },
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = cholesterol_total,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = cholesterol_total,
    date_field = 'result',
    )


triglycerides = AbstractLabTest.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    name = 'triglycerides',
    defaults = {
        'verbose_name': 'Triglycerides',
        },
    )[0]

LabResultAnyHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = triglycerides,
    date_field = 'result',
    )

LabResultPositiveHeuristic.objects.get_or_create( # @UndefinedVariable. Eclipse static code analysis can't see objects
    test = triglycerides,
    date_field = 'result',
    )

