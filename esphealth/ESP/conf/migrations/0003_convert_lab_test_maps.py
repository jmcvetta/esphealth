# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    
        
    # old: new
    TEST_NAME_MAP  = {
        'a1c': 'a1c',
        'alt': 'alt',
        'ast': 'ast',
        'chlamydia': 'chlamydia',
        'fta_abs': 'fta-abs',
        'giardiasis_antigen': 'giardiasis-antigen',
        'glucose_fasting': 'glucose-fasting',
        'gonorrhea': 'gonorrhea',
        'hav_tot': 'hav-tot',
        'hep_a_igm': 'hep-a-igm',
        'hep_b_core': 'hep-b-core',
        'hep_b_e_antigen': 'hep-b-e-antigen',
        'hep_b_igm': 'hep-b-igm',
        'hep_b_surface': 'hep-b-surface',
        'hep_b_viral_dna': 'hep-b-viral-dna',
        'hep_c_elisa': 'hep-c-elisa',
        'hep_c_riba': 'hep-c-riba',
        'hep_c_rna': 'hep-c-rna',
        'hep_c_signal_cutoff': 'hep-c-signal-cutoff',
        'hep_e_ab': 'hep-e-ab',
        'high_calc_bilirubin': 'high-calc-bilirubin',
        'lyme_elisa': 'lyme-elisa',
        'lyme_igg': 'lyme-igg',
        'lyme_igg_wb': 'lyme-igg-wb',
        'lyme_igm': 'lyme-igm',
        'lyme_pcr': 'lyme-pcr',
        'ogtt100_1hr': 'ogtt100-1hr',
        'ogtt100_2hr': 'ogtt100-2hr',
        'ogtt100_30m': 'ogtt100-30m',
        'ogtt100_3hr': 'ogtt100-3hr',
        'ogtt100_4hr': 'ogtt100-4hr',
        'ogtt100_5hr': 'ogtt100-5hr',
        'ogtt100_90m': 'ogtt100-90m',
        'ogtt100_fasting': 'ogtt100-fasting',
        'ogtt100_fasting_urine': 'ogtt100-fasting-urine',
        'ogtt50_1hr': 'ogtt50-1hr',
        'ogtt50_fasting': 'ogtt50-fasting',
        'ogtt50_random': 'ogtt50-random',
        'ogtt75_1hr': 'ogtt75-1hr',
        'ogtt75_2hr': 'ogtt75-2hr',
        'ogtt75_30m': 'ogtt75-30m',
        'ogtt75_90m': 'ogtt75-90m',
        'ogtt75_fasting': 'ogtt75-fasting',
        'ogtt75_fasting_urine': 'ogtt75-fasting-urine',
        'pertussis_culture': 'pertussis-culture',
        'pertussis_pcr': 'pertussis-pcr',
        'pertussis_serology': 'pertussis-serology',
        'rpr': 'rpr',
        'tb_lab': 'tb-lab',
        'total_bilirubin_high': 'total-bilirubin-high',
        'ttpa': 'ttpa',
        }
    
    def forwards(self, orm):
        for codemap in orm.Codemap.objects.order_by('pk'):
            ltm = orm.LabTestMap(
                test_name = self.TEST_NAME_MAP[codemap.heuristic],
                native_code = codemap.native_code,
                record_type = 'result',
                threshold = codemap.threshold,
			    reportable = codemap.reportable,
			    output_code = codemap.output_code,
			    output_name = codemap.output_name,
			    snomed_pos = codemap.snomed_pos,
			    snomed_neg = codemap.snomed_neg,
			    snomed_ind = codemap.snomed_ind,
                )
            ltm.save()
            print 'Created new LabTestMap: %s' % ltm
        


    def backwards(self, orm):
        raise RuntimeError("Reverse migration is not supported")


    models = {
        'conf.codemap': {
            'Meta': {'unique_together': "(['native_code', 'heuristic'],)", 'object_name': 'CodeMap'},
            'heuristic': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'native_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'output_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'output_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'reportable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'snomed_ind': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_neg': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_pos': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'threshold': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'conf.conditionconfig': {
            'Meta': {'object_name': 'ConditionConfig'},
            'icd9_days_after': ('django.db.models.fields.IntegerField', [], {'default': '28'}),
            'icd9_days_before': ('django.db.models.fields.IntegerField', [], {'default': '28'}),
            'initial_status': ('django.db.models.fields.CharField', [], {'default': "'AR'", 'max_length': '8'}),
            'lab_days_after': ('django.db.models.fields.IntegerField', [], {'default': '28'}),
            'lab_days_before': ('django.db.models.fields.IntegerField', [], {'default': '28'}),
            'med_days_after': ('django.db.models.fields.IntegerField', [], {'default': '28'}),
            'med_days_before': ('django.db.models.fields.IntegerField', [], {'default': '28'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'conf.ignoredcode': {
            'Meta': {'object_name': 'IgnoredCode'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'conf.labtestmap': {
            'Meta': {'unique_together': "(['test_name', 'native_code', 'code_match_type', 'record_type'],)", 'object_name': 'LabTestMap'},
            'code_match_type': ('django.db.models.fields.CharField', [], {'default': "'exact'", 'max_length': '32'}),
            'excluded_indeterminate_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'excluded_indeterminate_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['conf.ResultString']"}),
            'excluded_negative_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'excluded_negative_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['conf.ResultString']"}),
            'excluded_positive_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'excluded_positive_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['conf.ResultString']"}),
            'extra_indeterminate_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'extra_indeterminate_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['conf.ResultString']"}),
            'extra_negative_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'extra_negative_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['conf.ResultString']"}),
            'extra_positive_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'extra_positive_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['conf.ResultString']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'output_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'output_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'record_type': ('django.db.models.fields.CharField', [], {'default': "'both'", 'max_length': '8'}),
            'reportable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'snomed_ind': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_neg': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_pos': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'test_name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'threshold': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'conf.reportableicd9': {
            'Meta': {'unique_together': "(['icd9', 'condition'],)", 'object_name': 'ReportableIcd9'},
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conf.ConditionConfig']"}),
            'icd9': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static.Icd9']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'conf.reportablelab': {
            'Meta': {'unique_together': "(['native_code', 'condition'],)", 'object_name': 'ReportableLab'},
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conf.ConditionConfig']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'native_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'output_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'snomed_ind': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_neg': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snomed_pos': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'conf.reportablemedication': {
            'Meta': {'unique_together': "(['drug_name', 'condition'],)", 'object_name': 'ReportableMedication'},
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conf.ConditionConfig']"}),
            'drug_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'conf.resultstring': {
            'Meta': {'ordering': "['value']", 'object_name': 'ResultString'},
            'applies_to_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicates': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'match_type': ('django.db.models.fields.CharField', [], {'default': "'istartswith'", 'max_length': '32'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'conf.vaccinecodemap': {
            'Meta': {'object_name': 'VaccineCodeMap'},
            'canonical_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static.Vaccine']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'native_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'conf.vaccinemanufacturermap': {
            'Meta': {'object_name': 'VaccineManufacturerMap'},
            'canonical_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static.ImmunizationManufacturer']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'static.icd9': {
            'Meta': {'object_name': 'Icd9'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'static.immunizationmanufacturer': {
            'Meta': {'object_name': 'ImmunizationManufacturer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'use_instead': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static.ImmunizationManufacturer']", 'null': 'True'}),
            'vaccines_produced': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['static.Vaccine']", 'symmetrical': 'False'})
        },
        'static.vaccine': {
            'Meta': {'object_name': 'Vaccine'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        }
    }

    complete_apps = ['conf']
