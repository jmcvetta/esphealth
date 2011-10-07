# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LabTestMap'
        db.create_table('conf_labtestmap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('native_code', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('code_match_type', self.gf('django.db.models.fields.CharField')(default='exact', max_length=32)),
            ('record_type', self.gf('django.db.models.fields.CharField')(default='both', max_length=8)),
            ('threshold', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('reportable', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('output_code', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('output_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_pos', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_neg', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_ind', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('conf', ['LabTestMap'])

        # Adding M2M table for field extra_positive_strings on 'LabTestMap'
        db.create_table('conf_labtestmap_extra_positive_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['conf.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['conf.resultstring'], null=False))
        ))
        db.create_unique('conf_labtestmap_extra_positive_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding M2M table for field excluded_positive_strings on 'LabTestMap'
        db.create_table('conf_labtestmap_excluded_positive_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['conf.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['conf.resultstring'], null=False))
        ))
        db.create_unique('conf_labtestmap_excluded_positive_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding M2M table for field extra_negative_strings on 'LabTestMap'
        db.create_table('conf_labtestmap_extra_negative_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['conf.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['conf.resultstring'], null=False))
        ))
        db.create_unique('conf_labtestmap_extra_negative_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding M2M table for field excluded_negative_strings on 'LabTestMap'
        db.create_table('conf_labtestmap_excluded_negative_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['conf.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['conf.resultstring'], null=False))
        ))
        db.create_unique('conf_labtestmap_excluded_negative_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding M2M table for field extra_indeterminate_strings on 'LabTestMap'
        db.create_table('conf_labtestmap_extra_indeterminate_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['conf.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['conf.resultstring'], null=False))
        ))
        db.create_unique('conf_labtestmap_extra_indeterminate_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding M2M table for field excluded_indeterminate_strings on 'LabTestMap'
        db.create_table('conf_labtestmap_excluded_indeterminate_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['conf.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['conf.resultstring'], null=False))
        ))
        db.create_unique('conf_labtestmap_excluded_indeterminate_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding unique constraint on 'LabTestMap', fields ['test_name', 'native_code', 'code_match_type', 'record_type']
        db.create_unique('conf_labtestmap', ['test_name', 'native_code', 'code_match_type', 'record_type'])

        # Adding model 'ResultString'
        db.create_table('conf_resultstring', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('indicates', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('match_type', self.gf('django.db.models.fields.CharField')(default='istartswith', max_length=32)),
            ('applies_to_all', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('conf', ['ResultString'])


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
