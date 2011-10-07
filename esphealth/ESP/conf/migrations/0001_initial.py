# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CodeMap'
        db.create_table('conf_codemap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('heuristic', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('native_code', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('native_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('threshold', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('output_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('output_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('reportable', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('snomed_pos', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_neg', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_ind', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('conf', ['CodeMap'])

        # Adding unique constraint on 'CodeMap', fields ['native_code', 'heuristic']
        db.create_unique('conf_codemap', ['native_code', 'heuristic'])

        # Adding model 'IgnoredCode'
        db.create_table('conf_ignoredcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('native_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('conf', ['IgnoredCode'])

        # Adding model 'VaccineCodeMap'
        db.create_table('conf_vaccinecodemap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('native_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('native_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('canonical_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['static.Vaccine'], null=True)),
        ))
        db.send_create_signal('conf', ['VaccineCodeMap'])

        # Adding model 'VaccineManufacturerMap'
        db.create_table('conf_vaccinemanufacturermap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('native_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('canonical_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['static.ImmunizationManufacturer'], null=True)),
        ))
        db.send_create_signal('conf', ['VaccineManufacturerMap'])

        # Adding model 'ConditionConfig'
        db.create_table('conf_conditionconfig', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('initial_status', self.gf('django.db.models.fields.CharField')(default='AR', max_length=8)),
            ('lab_days_before', self.gf('django.db.models.fields.IntegerField')(default=28)),
            ('lab_days_after', self.gf('django.db.models.fields.IntegerField')(default=28)),
            ('icd9_days_before', self.gf('django.db.models.fields.IntegerField')(default=28)),
            ('icd9_days_after', self.gf('django.db.models.fields.IntegerField')(default=28)),
            ('med_days_before', self.gf('django.db.models.fields.IntegerField')(default=28)),
            ('med_days_after', self.gf('django.db.models.fields.IntegerField')(default=28)),
        ))
        db.send_create_signal('conf', ['ConditionConfig'])

        # Adding model 'ReportableLab'
        db.create_table('conf_reportablelab', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('condition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conf.ConditionConfig'])),
            ('native_code', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('native_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('output_code', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('snomed_pos', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_neg', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_ind', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('conf', ['ReportableLab'])

        # Adding unique constraint on 'ReportableLab', fields ['native_code', 'condition']
        db.create_unique('conf_reportablelab', ['native_code', 'condition_id'])

        # Adding model 'ReportableIcd9'
        db.create_table('conf_reportableicd9', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('condition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conf.ConditionConfig'])),
            ('icd9', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['static.Icd9'])),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('conf', ['ReportableIcd9'])

        # Adding unique constraint on 'ReportableIcd9', fields ['icd9', 'condition']
        db.create_unique('conf_reportableicd9', ['icd9_id', 'condition_id'])

        # Adding model 'ReportableMedication'
        db.create_table('conf_reportablemedication', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('condition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conf.ConditionConfig'])),
            ('drug_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('conf', ['ReportableMedication'])

        # Adding unique constraint on 'ReportableMedication', fields ['drug_name', 'condition']
        db.create_unique('conf_reportablemedication', ['drug_name', 'condition_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ReportableMedication', fields ['drug_name', 'condition']
        db.delete_unique('conf_reportablemedication', ['drug_name', 'condition_id'])

        # Removing unique constraint on 'ReportableIcd9', fields ['icd9', 'condition']
        db.delete_unique('conf_reportableicd9', ['icd9_id', 'condition_id'])

        # Removing unique constraint on 'ReportableLab', fields ['native_code', 'condition']
        db.delete_unique('conf_reportablelab', ['native_code', 'condition_id'])

        # Removing unique constraint on 'CodeMap', fields ['native_code', 'heuristic']
        db.delete_unique('conf_codemap', ['native_code', 'heuristic'])

        # Deleting model 'CodeMap'
        db.delete_table('conf_codemap')

        # Deleting model 'IgnoredCode'
        db.delete_table('conf_ignoredcode')

        # Deleting model 'VaccineCodeMap'
        db.delete_table('conf_vaccinecodemap')

        # Deleting model 'VaccineManufacturerMap'
        db.delete_table('conf_vaccinemanufacturermap')

        # Deleting model 'ConditionConfig'
        db.delete_table('conf_conditionconfig')

        # Deleting model 'ReportableLab'
        db.delete_table('conf_reportablelab')

        # Deleting model 'ReportableIcd9'
        db.delete_table('conf_reportableicd9')

        # Deleting model 'ReportableMedication'
        db.delete_table('conf_reportablemedication')


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
