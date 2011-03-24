# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'CodeMap', fields ['native_code', 'heuristic']
        db.delete_unique('conf_codemap', ['native_code', 'heuristic'])

        # Deleting field 'CodeMap.heuristic'
        db.rename_column('conf_codemap', 'heuristic', 'heuristic_uri')

        # Adding field 'CodeMap.heuristic_uri'
        db.alter_column('conf_codemap', 'heuristic_uri', self.gf('django.db.models.fields.SlugField')(default='legacy', max_length=255, db_index=True))

        # Adding unique constraint on 'CodeMap', fields ['native_code', 'heuristic_uri']
        db.create_unique('conf_codemap', ['native_code', 'heuristic_uri'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'CodeMap', fields ['native_code', 'heuristic_uri']
        db.delete_unique('conf_codemap', ['native_code', 'heuristic_uri'])

        # User chose to not deal with backwards NULL issues for 'CodeMap.heuristic'
        raise RuntimeError("Cannot reverse this migration. 'CodeMap.heuristic' and its values cannot be restored.")

        # Deleting field 'CodeMap.heuristic_uri'
        db.delete_column('conf_codemap', 'heuristic_uri')

        # Adding unique constraint on 'CodeMap', fields ['native_code', 'heuristic']
        db.create_unique('conf_codemap', ['native_code', 'heuristic'])


    models = {
        'conf.codemap': {
            'Meta': {'unique_together': "(['heuristic_uri', 'native_code'],)", 'object_name': 'CodeMap'},
            'heuristic_uri': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
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
