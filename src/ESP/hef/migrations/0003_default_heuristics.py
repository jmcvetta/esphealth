# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from ESP.utils import log


class Migration(DataMigration):

    def forwards(self, orm):
        AbstractLabTest = orm['hef.AbstractLabTest']
        Heuristic = orm['hef.Heuristic']
        ResultString = orm['hef.ResultString']
        # We have to add custom save() methods to the South orm objects -- they
        # are frozen models, and do not have any custom methods from the 
        # actual django models.
        LabOrderHeuristic = orm['hef.LabOrderHeuristic']
        def lab_order_save(self, *args, **kwargs):
            name = '%s--order' % self.test.name
            if self.name and not self.name == name:
                log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' % (self.name, name))
            self.name = name
            super(LabOrderHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
            obj, created = EventType.objects.get_or_create(
                name = self.name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
        LabOrderHeuristic.save = lab_order_save
        LabResultAnyHeuristic = orm['hef.LabResultAnyHeuristic']
        def lab_any_save(self, *args, **kwargs):
            name = '%s--any_result' % self.test.name
            if self.name and not self.name == name:
                log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' % (self.name, name))
            self.name = name
            super(LabResultAnyHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
            obj, created = EventType.objects.get_or_create(
                name = self.name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
        LabResultAnyHeuristic.save = lab_any_save
        LabResultPositiveHeuristic = orm['hef.LabResultPositiveHeuristic']
        def lab_positive_save(self, *args, **kwargs):
            name = '%s--positive' % self.test.name
            if self.name and not self.name == name:
                log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' % (self.name, name))
            self.name = name
            super(LabResultPositiveHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
            event_name_list = [
                self.name, 
                '%s--negative' % self.test.name,
                '%s--indeterminate' % self.test.name,
                ]
            for event_name in event_name_list:
                obj, created = EventType.objects.get_or_create(
                    name = event_name,
                    heuristic = self,
                    )
                if created:
                    log.debug('Added %s for %s' % (obj, self))
        LabResultPositiveHeuristic.save = lab_positive_save
        LabResultRatioHeuristic = orm['hef.LabResultRatioHeuristic']
        def lab_ratio_save(self, *args, **kwargs):
            name = '%s--ratio--%s' % (self.test.name, self.ratio)
            if self.name and not self.name == name:
                log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' %  (self.name, name))
            self.name = name
            super(LabResultRatioHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
            obj, created = EventType.objects.get_or_create(
                name = self.name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
        LabResultRatioHeuristic.save = lab_ratio_save
        LabResultFixedThresholdHeuristic = orm['hef.LabResultFixedThresholdHeuristic']
        def lab_fixed_save(self, *args, **kwargs):
            name = '%s--threshold--%s' % (self.test.name, self.threshold)
            if self.name and not self.name == name:
                log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' % (self.name, name))
            self.name = name
            super(LabResultFixedThresholdHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
            obj, created = EventType.objects.get_or_create(
                name = self.name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
        LabResultFixedThresholdHeuristic.save = lab_fixed_save
        EncounterHeuristic = orm['hef.EncounterHeuristic']
        def encounter_save(self, *args, **kwargs):
            super(EncounterHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
            obj, created = EventType.objects.get_or_create(
                name = self.name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
        EncounterHeuristic.save = encounter_save
        PrescriptionHeuristic = orm['hef.PrescriptionHeuristic']
        def prescription_save(self, *args, **kwargs):
            super(PrescriptionHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
            obj, created = EventType.objects.get_or_create(
                name = self.name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
        PrescriptionHeuristic.save = prescription_save
        Dose = orm['hef.Dose']
        EventType = orm['hef.EventType']
    
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
        # Legacy Event Support
        #
        #-------------------------------------------------------------------------------

        # All events created by previous version of HEF will be bound to this
        # heuristic.
        #
        # We are specifying pk of 0 to make manual db query results more
        # readable.  Since this will be created immediately after Heuristic
        # model is first created, there should never be a conflict with an
        # existing record.
        legacy_heuristic = Heuristic.objects.get_or_create(
            id = 0,
            name = 'Legacy Heuristic',
            )[0]

        #-------------------------------------------------------------------------------
        #
        # Doses
        #
        #-------------------------------------------------------------------------------
        dose_1g = Dose.objects.get_or_create(quantity = 1, units = 'g')[0]
        dose_2g = Dose.objects.get_or_create(quantity = 2, units = 'g')[0]


        #-------------------------------------------------------------------------------
        #
        # Gonorrhea
        #
        #-------------------------------------------------------------------------------

        gonorrhea_test = AbstractLabTest.objects.get_or_create(
            name = 'gonorrhea',
            defaults = {
                'verbose_name': 'Gonorrhea test',
                },
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = gonorrhea_test,
            )

        #-------------------------------------------------------------------------------
        #
        # Chlamydia
        #
        #-------------------------------------------------------------------------------

        chlamydia_test = AbstractLabTest.objects.get_or_create(
            name = 'chlamydia',
            defaults = {
                'verbose_name': 'Chlamydia test',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = chlamydia_test,
            )

        #-------------------------------------------------------------------------------
        #
        # ALT
        #
        #-------------------------------------------------------------------------------

        alt = AbstractLabTest.objects.get_or_create(
            name = 'alt',
            defaults = {
                'verbose_name': 'Alanine Aminotransferase blood test',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = alt,
            )

        LabResultRatioHeuristic.objects.get_or_create(
            test = alt,
            ratio = 2,
            )

        LabResultRatioHeuristic.objects.get_or_create(
            test = alt,
            ratio = 5,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = alt,
            threshold = 400,
            )


        #-------------------------------------------------------------------------------
        #
        # AST
        #
        #-------------------------------------------------------------------------------

        ast = AbstractLabTest.objects.get_or_create(
            name = 'ast',
            defaults = {
                'verbose_name': 'Aspartate Aminotransferase blood test',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = ast,
            )

        LabResultRatioHeuristic.objects.get_or_create(
            test = ast,
            ratio = 2,
            )

        LabResultRatioHeuristic.objects.get_or_create(
            test = ast,
            ratio = 5,
            )


        #-------------------------------------------------------------------------------
        #
        # Hepatitis A
        #
        #-------------------------------------------------------------------------------

        hep_a_igm_antibody = AbstractLabTest.objects.get_or_create(
            name = 'hep_a_igm_antibody',
            defaults = {
                'verbose_name': 'Hepatitis A IgM antibody',
                },
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_a_igm_antibody,
            )

        hep_a_tot_antibody = AbstractLabTest.objects.get_or_create(
            name = 'hep_a_tot_antibody',
            defaults = {
                'verbose_name': 'Hepatitis A Total Antibodies',
                },
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_a_tot_antibody,
            )


        #-------------------------------------------------------------------------------
        #
        # Hepatitis B
        #
        #-------------------------------------------------------------------------------

        hep_b_igm_antibody = AbstractLabTest.objects.get_or_create(
            name = 'hep_b_igm_antibody',
            defaults = {
                'verbose_name': 'Hepatitis B core IgM antibody',
                }
            )[0]

        LabOrderHeuristic.objects.get_or_create(
            test = hep_b_igm_antibody,
            )

        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_b_igm_antibody,
            )

        hep_b_core_antibody = AbstractLabTest.objects.get_or_create(
            name = 'hep_b_core_antibody',
            defaults = {
                'verbose_name': 'Hepatitis B core general antibody',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_b_core_antibody,
            )

        hep_b_surface_antigen = AbstractLabTest.objects.get_or_create(
            name = 'hep_b_surface_antigen',
            defaults = {
                'verbose_name': 'Hepatitis B surface antigen',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_b_surface_antigen,
            )


        hep_b_e_antigen = AbstractLabTest.objects.get_or_create(
            name = 'hep_b_e_antigen',
            defaults = {
                'verbose_name': 'Hepatitis B "e" antigen',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_b_e_antigen,
            )


        # NOTE:  See note in Hepatitis B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
        # portion of algorithm


        hep_b_viral_dna = AbstractLabTest.objects.get_or_create(
            name = 'hep_b_viral_dna',
            defaults = {
                'verbose_name': 'Hepatitis B viral DNA',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_b_viral_dna,
            )

        #-------------------------------------------------------------------------------
        #
        # Hepatitis E
        #
        #-------------------------------------------------------------------------------

        hep_e_antibody = AbstractLabTest.objects.get_or_create(
            name = 'hep_e_antibody',
            defaults = {
                'verbose_name': 'Hepatitis E antibody',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_e_antibody,
            )

        #-------------------------------------------------------------------------------
        #
        # Bilirubin
        #
        #-------------------------------------------------------------------------------

        bilirubin_total = AbstractLabTest.objects.get_or_create(
            name = 'bilirubin_total',
            defaults = {
                'verbose_name': 'Bilirubin glucuronidated + bilirubin non-glucuronidated',
                }
            )[0]
            
        bilirubin_direct = AbstractLabTest.objects.get_or_create(
            name = 'bilirubin_direct',
            defaults = {
                'verbose_name': 'Bilirubin glucuronidated',
                }
            )[0]
            
        bilirubin_indirect = AbstractLabTest.objects.get_or_create(
            name = 'bilirubin_indirect',
            defaults = {
                'verbose_name': 'Bilirubin non-glucuronidated',
                }
            )[0]
            
        #-------------------------------------------------------------------------------
        #
        # Hepatitis C
        #
        #-------------------------------------------------------------------------------

        hep_c_signal_cutoff = AbstractLabTest.objects.get_or_create(
            name = 'hep_c_signal_cutoff',
            defaults = {
                'verbose_name': 'Hepatitis C signal cutoff',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_c_signal_cutoff,
            )

        hep_c_riba = AbstractLabTest.objects.get_or_create(
            name = 'hep_c_riba',
            defaults = {
                'verbose_name': 'Hepatitis C RIBA',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_c_riba,
            )

        hep_c_rna = AbstractLabTest.objects.get_or_create(
            name = 'hep_c_rna',
            defaults = {
                'verbose_name': 'Hepatitis C RNA',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_c_rna,
            )

        hep_c_elisa = AbstractLabTest.objects.get_or_create(
            name = 'hep_c_elisa',
            defaults = {
                'verbose_name': 'Hepatitis C ELISA',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = hep_c_elisa,
            )


        #-------------------------------------------------------------------------------
        #
        # Lyme
        #
        #-------------------------------------------------------------------------------

        lyme_elisa = AbstractLabTest.objects.get_or_create(
            name = 'lyme_elisa',
            defaults = {
                'verbose_name': 'Lyme ELISA',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = lyme_elisa,
            )

        LabOrderHeuristic.objects.get_or_create(
            test = lyme_elisa,
            )

        lyme_igg_eia = AbstractLabTest.objects.get_or_create(
            name = 'lyme_igg_eia',
            defaults = {
                'verbose_name': 'Lyme IGG (EIA)',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = lyme_igg_eia,
            )

        LabOrderHeuristic.objects.get_or_create(
            test = lyme_igg_eia,
            )

        lyme_igm_eia = AbstractLabTest.objects.get_or_create(
            name = 'lyme_igm_eia',
            defaults = {
                'verbose_name': 'Lyme IGM (EIA)',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = lyme_igm_eia,
            )

        LabOrderHeuristic.objects.get_or_create(
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
        # TODO: This test needs a western blog heuristic!
        #
        lyme_igg_wb = AbstractLabTest.objects.get_or_create(
            name = 'lyme_igg_wb',
            defaults = {
                'verbose_name': 'Lyme IGG (Western Blot)',
                }
            )[0]
            
        lyme_igm_wb = AbstractLabTest.objects.get_or_create(
            name = 'lyme_igm_wb',
            defaults = {
                'verbose_name': 'Lyme IGM (Western Blot)',
                }
            )[0]
            
        # Despite being a western blot, this test is resulted pos/neg
        LabResultPositiveHeuristic.objects.get_or_create(
            test = lyme_igm_wb,
            )

        lyme_pcr = AbstractLabTest.objects.get_or_create(
            name = 'lyme_pcr',
            defaults = {
                'verbose_name': 'Lyme PCR',
                }
            )[0]
            
        LabResultPositiveHeuristic.objects.get_or_create(
            test = lyme_pcr,
            )

        LabOrderHeuristic.objects.get_or_create(
            test = lyme_pcr,
            )


        lyme_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'lyme_diagnosis',
            icd9_codes = '088.81',
            )[0]


        rash_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'rash_diagnosis',
            icd9_codes = '782.1',
            )

        doxycycline_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'doxycycline_rx',
            drugs = 'doxycycline',
            )[0]

        lyme_antibio_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'lyme_other_antibiotic_rx',
            drugs = 'Amoxicillin, Cefuroxime, Ceftriaxone, Cefotaxime',
            )[0]


        #-------------------------------------------------------------------------------
        #
        # Pelvic Inflamatory Disease (PID)
        #
        #-------------------------------------------------------------------------------

        EncounterHeuristic.objects.get_or_create(
            name = 'pid_diagnosis',
            icd9_codes = '614.0, 614.2, 614.3, 614.5, 614.9, 099.56',
            )[0]


        #-------------------------------------------------------------------------------
        #
        # Tuberculosis
        #
        #-------------------------------------------------------------------------------

        pyrazinamide_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'pyrazinamide_rx',
            drugs = 'Pyrazinamide, PZA',
            exclude = 'CAPZA'
            )[0]

        isoniazid_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'isoniazid_rx',
            drugs = 'Isoniazid',
            exclude = 'INHAL, INHIB',
            )[0]

        ethambutol_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'ethambutol_rx',
            drugs = 'Ethambutol',
            )[0]

        rifampin_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'rifampin_rx',
            drugs = 'rifampin',
            )[0]

        rifabutin_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'rifabutin_rx',
            drugs = 'rifabutin',
            )[0]

        rifapentine_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'rifapentine_rx',
            drugs = 'rifapentine',
            )[0]

        streptomycin_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'streptomycin_rx',
            drugs = 'streptomycin',
            )[0]

        para_aminosalicyclic_acid_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'para_aminosalicyclic_acid_rx',
            drugs = 'para-aminosalicyclic acid',
            )[0]

        kanamycin_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'kanamycin_rx',
            drugs = 'kanamycin',
            )[0]

        capreomycin_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'capreomycin_rx',
            drugs = 'capreomycin',
            )[0]

        cycloserine_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'cycloserine_rx',
            drugs = 'cycloserine',
            )[0]

        ethionamide_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'ethionamide_rx',
            drugs = 'ethionamide',
            )[0]

        moxifloxacin_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'moxifloxacin_rx',
            drugs = 'moxifloxacin_rx',
            )[0]

        tb_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'tb_diagnosis',
            icd9_codes = '010., 011., 012., 013., 014., 015., 016., 017., 018.',
            code_match_type = 'startswith',
            )[0]


        #-------------------------------------------------------------------------------
        #
        # Tuberculosis
        #
        #-------------------------------------------------------------------------------

        tb_lab = AbstractLabTest.objects.get_or_create(
            name = 'tb_lab',
            defaults = {
                'verbose_name': 'Tuberculosis lab test (several varieties)',
                }
            )[0]
            
        LabOrderHeuristic.objects.get_or_create(
            test = tb_lab,
            )



        #-------------------------------------------------------------------------------
        #
        # Syphilis 
        #
        #-------------------------------------------------------------------------------

        penicillin_g_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'penicillin_g_rx',
            drugs = 'penicillin g, pen g'
            )[0]

        doxycycline_7_days_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'doxycycline_7_days_rx',
            drugs = 'doxycycline',
            min_quantity = 14, # Need 14 pills for 7 days
            )[0]

        ceftriaxone_1g_2g_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'ceftriaxone_1g_2g_rx',
            drugs = 'ceftriaxone',
            )[0]
        ceftriaxone_1g_2g_rx.dose.add(dose_1g)
        ceftriaxone_1g_2g_rx.dose.add(dose_2g)

        syphilis_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'syphilis_diagnosis',
            icd9_codes = '090., 091., 092., 093., 094., 095., 096., 097.',
            code_match_type = 'startswith',
            )[0]

        syphilis_tppa = AbstractLabTest.objects.get_or_create(
            name = 'syphilis_tppa',
            defaults = {
                'verbose_name': 'Syphilis TP-PA',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = syphilis_tppa,
            )
            
        syphilis_fta_abs = AbstractLabTest.objects.get_or_create(
            name = 'syphilis_fta_abs',
            defaults = {
                'verbose_name': 'Syphilis FTA-ABS',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = syphilis_fta_abs,
            )

        syphilis_rpr = AbstractLabTest.objects.get_or_create(
            name = 'syphilis_rpr',
            defaults = {
                'verbose_name': 'Syphilis rapid plasma reagin (RPR)',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = syphilis_rpr,
            titer = 8, # 1:8 titer
            )

        syphilis_vdrl_serum = AbstractLabTest.objects.get_or_create(
            name = 'syphilis_vdrl_serum',
            defaults = {
                'verbose_name': 'Syphilis VDRL serum',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = syphilis_vdrl_serum,
            titer = 8, # 1:8 titer
            )

        syphilis_tp_igg = AbstractLabTest.objects.get_or_create(
            name = 'syphilis_tp_igg',
            defaults = {
                'verbose_name': 'Syphilis TP-IGG',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = syphilis_tp_igg,
            )

        syphilis_vdrl_csf = AbstractLabTest.objects.get_or_create(
            name = 'syphilis_vdrl_csf',
            defaults = {
                'verbose_name': 'Syphilis VDRL-CSF',
                }
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = syphilis_vdrl_csf,
            titer = 1, # 1:1 titer
            )


        #-------------------------------------------------------------------------------
        #
        # Glucose
        #
        #-------------------------------------------------------------------------------

        glucose_fasting = AbstractLabTest.objects.get_or_create(
            name = 'glucose_fasting',
            defaults = {
                'verbose_name':  'Fasting glucose (several variations)',
                }
            )[0]
        
        LabResultAnyHeuristic.objects.get_or_create(
            test = glucose_fasting,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = glucose_fasting,
            threshold = 126,
            date_field = 'result'
            )


        #-------------------------------------------------------------------------------
        #
        # Oral Glucose Tolerance Test 50g (OGTT50)
        #
        #-------------------------------------------------------------------------------

        ogtt50_fasting = AbstractLabTest.objects.get_or_create(
            name = 'ogtt50_fasting',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 50 gram Fasting',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt50_fasting,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt50_fasting,
            threshold = 95,
            date_field = 'result'
            )

        ogtt50_random = AbstractLabTest.objects.get_or_create(
            name = 'ogtt50_random',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 50 gram Random',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt50_random,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt50_random,
            threshold = 190,
            date_field = 'result'
            )

        ogtt50_1hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt50_1hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 50 gram 1 hour post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt50_1hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt50_1hr,
            threshold = 190,
            date_field = 'result'
            )

        #-------------------------------------------------------------------------------
        #
        # Oral Glucose Tolerance Test 75g (OGTT 75)
        #
        #-------------------------------------------------------------------------------

        ogtt75_series = AbstractLabTest.objects.get_or_create(
            name = 'ogtt75_series',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 75 gram Series',
                }
            )[0]

        LabOrderHeuristic.objects.get_or_create(
            test=ogtt75_series,
            )

        ogtt75_fasting = AbstractLabTest.objects.get_or_create(
            name = 'ogtt75_fasting',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 75 gram fasting',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt75_fasting,
            )

        LabOrderHeuristic.objects.get_or_create(
            test=ogtt75_fasting,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_fasting,
            threshold = 95,
            date_field = 'result'
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_fasting,
            threshold = 126,
            date_field = 'result'
            )

        ogtt75_fasting_urine = AbstractLabTest.objects.get_or_create(
            name = 'ogtt75_fasting_urine',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 75 gram fasting, urine',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt75_fasting_urine,
            )

        LabOrderHeuristic.objects.get_or_create(
            test=ogtt75_fasting_urine,
            )

        LabResultPositiveHeuristic.objects.get_or_create(
            test = ogtt75_fasting_urine,
            date_field = 'result'
            )

        ogtt75_30min = AbstractLabTest.objects.get_or_create(
            name = 'ogtt75_30min',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 75 gram 30 minutes post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt75_30min,
            )

        LabOrderHeuristic.objects.get_or_create(
            test=ogtt75_30min,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_30min,
            threshold = 200,
            date_field = 'result'
            )

        ogtt75_1hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt75_1hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 75 gram 1 hour post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt75_1hr,
            )

        LabOrderHeuristic.objects.get_or_create(
            test=ogtt75_1hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_1hr,
            threshold = 180,
            date_field = 'result'
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_1hr,
            threshold = 200,
            date_field = 'result'
            )

        ogtt75_90min = AbstractLabTest.objects.get_or_create(
            name = 'ogtt75_90min',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 75 gram 90 minutes post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt75_90min,
            )

        LabOrderHeuristic.objects.get_or_create(
            test=ogtt75_90min,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_90min,
            threshold = 180,
            date_field = 'result'
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_90min,
            threshold = 200,
            date_field = 'result'
            )

        ogtt75_2hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt75_2hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 75 gram 2 hour post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt75_2hr,
            )

        LabOrderHeuristic.objects.get_or_create(
            test=ogtt75_2hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_2hr,
            threshold = 155,
            date_field = 'result'
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt75_2hr,
            threshold = 200,
            date_field = 'result'
            )

        #-------------------------------------------------------------------------------
        #
        # Oral Gluclose Tolerance Test 100g (OGTT 100)
        #
        #-------------------------------------------------------------------------------

        ogtt100_fasting = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_fasting',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram fasting',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_fasting,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_fasting,
            threshold = 95,
            date_field = 'result'
            )

        ogtt100_fasting_urine = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_fasting_urine',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram fasting (urine)',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_fasting_urine,
            )

        LabResultPositiveHeuristic.objects.get_or_create(
            test = ogtt100_fasting_urine,
            date_field = 'result'
            )

        ogtt100_30min = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_30min',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram 30 minutes post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_30min,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_30min,
            threshold = 200,
            date_field = 'result'
            )

        ogtt100_1hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_1hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram 1 hour post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_1hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_1hr,
            threshold = 180,
            date_field = 'result'
            )

        ogtt100_90min = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_90min',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram 90 minutes post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_90min,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_90min,
            threshold = 180,
            date_field = 'result'
            )

        ogtt100_2hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_2hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram 2 hour post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_2hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_2hr,
            threshold = 155,
            date_field = 'result'
            )

        ogtt100_3hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_3hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram 3 hour post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_3hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_3hr,
            threshold = 140,
            date_field = 'result'
            )

        ogtt100_4hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_4hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram 4 hour post',
                }
            )[0]

        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_4hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_4hr,
            threshold = 140,
            date_field = 'result'
            )

        ogtt100_5hr = AbstractLabTest.objects.get_or_create(
            name = 'ogtt100_5hr',
            defaults = {
                'verbose_name':  'Oral Glucose Tolerance Test 100 gram 5 hour post',
                }
            )[0]
            
        LabResultAnyHeuristic.objects.get_or_create(
            test = ogtt100_5hr,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = ogtt100_5hr,
            threshold = 140,
            date_field = 'result'
            )


        #-------------------------------------------------------------------------------
        #
        # Glycated hemoglobin (A1C)
        #
        #-------------------------------------------------------------------------------

        a1c = AbstractLabTest.objects.get_or_create(
            name = 'a1c',
            defaults = {
                'verbose_name':  'Glycated hemoglobin (A1C)',
                }
            )[0]
            
        LabResultAnyHeuristic.objects.get_or_create(
            test = a1c,
            )

        LabOrderHeuristic.objects.get_or_create(
            test = a1c,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = a1c,
            threshold = 6.0,
            )

        LabResultFixedThresholdHeuristic.objects.get_or_create(
            test = a1c,
            threshold = 6.5,
            )


        pregnancy_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'pregnancy_diagnosis',
            icd9_codes = 'V22., V23.',
            code_match_type = 'startswith',
            )[0]

        #
        #
        ##--- pregnancy
        #PregnancyHeuristic() # No config needed
        #

        gdm_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'gdm_diagnosis',
            icd9_codes = '648.8',
            code_match_type = 'startswith',
            )[0]

        lancets_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'lancets_rx',
            drugs = 'lancets',
            )[0]

        test_strips_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'test_strips_rx',
            drugs = 'test strips',
            )

        insulin_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'insulin_rx',
            drugs = 'insulin',
            )

        #-------------------------------------------------------------------------------
        #
        # Giardiasis
        #
        #-------------------------------------------------------------------------------

        giardiasis_antigen = AbstractLabTest.objects.get_or_create(
            name = 'giardiasis_antigen',
            defaults = {
                'verbose_name': 'Giardiasis Antigen',
                },
            )[0]

        LabResultPositiveHeuristic.objects.get_or_create(
            test = giardiasis_antigen,
            )


        metronidazole_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'metronidazole_rx',
            drugs = 'metronidazole',
            )

        diahrrhea_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'diarrhea_diagnosis',
            icd9_codes = '787.91',
            )[0]


        #-------------------------------------------------------------------------------
        #
        # Pertussis
        #
        #-------------------------------------------------------------------------------

        pertussis_diagnosis = EncounterHeuristic.objects.get_or_create(
            name = 'pertussis_diagnosis',
            icd9_codes = '033.0, 033.9',
            )[0]

        #
        # Needs new functionality to examine comment string
        #
        pertussis_pcr = AbstractLabTest.objects.get_or_create(
            name = 'pertussis_pcr',
            defaults = {
                'verbose_name': 'Pertussis PCR',
                },
            )[0]

        LabOrderHeuristic.objects.get_or_create(
            test = pertussis_pcr,
            )

        LabResultPositiveHeuristic.objects.get_or_create(
            test = pertussis_pcr,
            )

        #
        # Needs new functionality to examine comment string
        #
        pertussis_culture = AbstractLabTest.objects.get_or_create(
            name = 'pertussis_culture',
            defaults = {
                'verbose_name': 'Pertussis Culture',
                },
            )[0]

        LabOrderHeuristic.objects.get_or_create(
            test = pertussis_culture,
            )

        LabResultPositiveHeuristic.objects.get_or_create(
            test = pertussis_culture,
            )

        pertussis_serology = AbstractLabTest.objects.get_or_create(
            name = 'pertussis_serology',
            defaults = {
                'verbose_name': 'Pertussis serology',
                },
            )[0]

        LabOrderHeuristic.objects.get_or_create(
            test = pertussis_serology,
            )

        LabResultPositiveHeuristic.objects.get_or_create(
            test = pertussis_culture,
            )

        pertussis_rx = PrescriptionHeuristic.objects.get_or_create(
            name = 'pertussis_rx',
            drugs =  'Erythromycin, Clarithromycin, Azithromycin, Trimethoprim-sulfamethoxazole',
            )



        legacy_heuristic = orm['hef.Heuristic'].objects.get(pk=0)
        for event_type_value in orm['hef.Event'].objects.values_list('event_type', flat=True).distinct():
            et, created = EventType.objects.get_or_create(
                name = event_type_value,
                defaults = {'heuristic': legacy_heuristic,},
                )
            if created:
                log.debug('Created legacy event type for %s' % event_type_value)

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'emr.encounter': {
            'Meta': {'ordering': "['date']", 'object_name': 'Encounter'},
            'bmi': ('django.db.models.fields.DecimalField', [], {'db_index': 'True', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'bp_diastolic': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'bp_systolic': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'closed_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'diagnosis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'edc': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'icd9_codes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['static.Icd9']", 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'native_encounter_num': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'native_site_num': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'o2_stat': ('django.db.models.fields.FloatField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'peak_flow': ('django.db.models.fields.FloatField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'pregnancy_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'temperature': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'emr.patient': {
            'Meta': {'object_name': 'Patient'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'aliases': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'areacode': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'home_language': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'marital_stat': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'mother_mrn': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'patient_id_num': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'pcp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'pregnant': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'tel_ext': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'zip5': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'db_index': 'True'})
        },
        'emr.provenance': {
            'Meta': {'unique_together': "(['timestamp', 'source', 'hostname'],)", 'object_name': 'Provenance'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'error_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'provenance_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '500', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valid_rec_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'emr.provider': {
            'Meta': {'object_name': 'Provider'},
            'area_code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dept': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dept_address_1': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dept_address_2': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dept_city': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dept_id_num': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dept_state': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dept_zip': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider_id_num': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'hef.abstractlabtest': {
            'Meta': {'ordering': "['name']", 'object_name': 'AbstractLabTest'},
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'output_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'output_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'reportable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'snomed_ind': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_neg': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_pos': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'})
        },
        'hef.dose': {
            'Meta': {'ordering': "['units', 'quantity']", 'unique_together': "(['quantity', 'units'],)", 'object_name': 'Dose'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.FloatField', [], {}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'hef.encounterheuristic': {
            'Meta': {'ordering': "['name']", 'unique_together': "(['icd9_codes', 'code_match_type'],)", 'object_name': 'EncounterHeuristic', '_ormbases': ['hef.Heuristic']},
            'code_match_type': ('django.db.models.fields.CharField', [], {'default': "'exact'", 'max_length': '32', 'db_index': 'True'}),
            'heuristic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hef.Heuristic']", 'unique': 'True', 'primary_key': 'True'}),
            'icd9_codes': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'hef.event': {
            'Meta': {'object_name': 'Event'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.EventType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'hef.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'heuristic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.Heuristic']"}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'primary_key': 'True', 'db_index': 'True'})
        },
        'hef.heuristic': {
            'Meta': {'object_name': 'Heuristic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'hef.laborderheuristic': {
            'Meta': {'object_name': 'LabOrderHeuristic', '_ormbases': ['hef.Heuristic']},
            'heuristic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hef.Heuristic']", 'unique': 'True', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.AbstractLabTest']", 'unique': 'True'})
        },
        'hef.labresultanyheuristic': {
            'Meta': {'ordering': "['test']", 'object_name': 'LabResultAnyHeuristic', '_ormbases': ['hef.Heuristic']},
            'heuristic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hef.Heuristic']", 'unique': 'True', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.AbstractLabTest']", 'unique': 'True'})
        },
        'hef.labresultfixedthresholdheuristic': {
            'Meta': {'ordering': "['test']", 'unique_together': "(['test', 'threshold'],)", 'object_name': 'LabResultFixedThresholdHeuristic', '_ormbases': ['hef.Heuristic']},
            'date_field': ('django.db.models.fields.CharField', [], {'default': "'order'", 'max_length': '32'}),
            'heuristic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hef.Heuristic']", 'unique': 'True', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.AbstractLabTest']"}),
            'threshold': ('django.db.models.fields.FloatField', [], {})
        },
        'hef.labresultpositiveheuristic': {
            'Meta': {'ordering': "['test']", 'object_name': 'LabResultPositiveHeuristic', '_ormbases': ['hef.Heuristic']},
            'date_field': ('django.db.models.fields.CharField', [], {'default': "'order'", 'max_length': '32'}),
            'heuristic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hef.Heuristic']", 'unique': 'True', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.AbstractLabTest']", 'unique': 'True'}),
            'titer': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'hef.labresultratioheuristic': {
            'Meta': {'ordering': "['test']", 'unique_together': "(['test', 'ratio'],)", 'object_name': 'LabResultRatioHeuristic', '_ormbases': ['hef.Heuristic']},
            'date_field': ('django.db.models.fields.CharField', [], {'default': "'order'", 'max_length': '32'}),
            'heuristic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hef.Heuristic']", 'unique': 'True', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ratio': ('django.db.models.fields.FloatField', [], {}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.AbstractLabTest']"})
        },
        'hef.labtestmap': {
            'Meta': {'unique_together': "(['test', 'code'],)", 'object_name': 'LabTestMap'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'code_match_type': ('django.db.models.fields.CharField', [], {'default': "'exact'", 'max_length': '32', 'db_index': 'True'}),
            'extra_negative_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'negative_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'extra_positive_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'positive_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'output_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'output_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'reportable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'snomed_ind': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_neg': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_pos': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.AbstractLabTest']"}),
            'threshold': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'hef.prescriptionheuristic': {
            'Meta': {'ordering': "['name']", 'object_name': 'PrescriptionHeuristic', '_ormbases': ['hef.Heuristic']},
            'dose': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['hef.Dose']", 'null': 'True', 'blank': 'True'}),
            'drugs': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'exclude': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'heuristic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hef.Heuristic']", 'unique': 'True', 'primary_key': 'True'}),
            'min_quantity': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'require': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'hef.resultstring': {
            'Meta': {'object_name': 'ResultString'},
            'applies_to_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicates': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'match_type': ('django.db.models.fields.CharField', [], {'default': "'istartswith'", 'max_length': '32'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'hef.timespan': {
            'Meta': {'object_name': 'Timespan'},
            'encounters': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['emr.Encounter']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'db_index': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']"}),
            'pattern': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'static.icd9': {
            'Meta': {'object_name': 'Icd9'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['hef']
