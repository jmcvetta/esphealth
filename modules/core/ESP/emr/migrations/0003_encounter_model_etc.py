# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Encounter.status'
        db.alter_column('emr_encounter', 'status', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Encounter.site_name'
        db.alter_column('emr_encounter', 'site_name', self.gf('django.db.models.fields.TextField')(null=True))

        # Adding index on 'Prescription', fields ['dose']
        db.create_index('emr_prescription', ['dose'])

        # Deleting field 'Patient.pregnant'
        db.delete_column('emr_patient', 'pregnant')

        # Adding index on 'Patient', fields ['date_of_birth']
        db.create_index('emr_patient', ['date_of_birth'])

        # Adding index on 'Patient', fields ['race']
        db.create_index('emr_patient', ['race'])

        # Adding index on 'Patient', fields ['gender']
        db.create_index('emr_patient', ['gender'])

        # Deleting field 'Encounter.edc'
        db.delete_column('emr_encounter', 'edc')

        # Deleting field 'Encounter.event_type'
        db.delete_column('emr_encounter', 'event_type')

        # Deleting field 'Encounter.closed_date'
        db.delete_column('emr_encounter', 'closed_date')

        # Deleting field 'Encounter.diagnosis'
        db.delete_column('emr_encounter', 'diagnosis')

        # Deleting field 'Encounter.pregnancy_status'
        db.delete_column('emr_encounter', 'pregnancy_status')

        # Adding field 'Encounter.encounter_type'
        db.add_column('emr_encounter', 'encounter_type', self.gf('django.db.models.fields.TextField')(db_index=True, null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.date_closed'
        db.add_column('emr_encounter', 'date_closed', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.pregnant'
        db.add_column('emr_encounter', 'pregnant', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True), keep_default=False)

        # Adding field 'Encounter.edd'
        db.add_column('emr_encounter', 'edd', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_date'
        db.add_column('emr_encounter', 'raw_date', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_date_closed'
        db.add_column('emr_encounter', 'raw_date_closed', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_edd'
        db.add_column('emr_encounter', 'raw_edd', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_temperature'
        db.add_column('emr_encounter', 'raw_temperature', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_weight'
        db.add_column('emr_encounter', 'raw_weight', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_height'
        db.add_column('emr_encounter', 'raw_height', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_bp_systolic'
        db.add_column('emr_encounter', 'raw_bp_systolic', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_bp_diastolic'
        db.add_column('emr_encounter', 'raw_bp_diastolic', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_o2_stat'
        db.add_column('emr_encounter', 'raw_o2_stat', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_peak_flow'
        db.add_column('emr_encounter', 'raw_peak_flow', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_bmi'
        db.add_column('emr_encounter', 'raw_bmi', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.raw_diagnosis'
        db.add_column('emr_encounter', 'raw_diagnosis', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding index on 'Encounter', fields ['status']
        db.create_index('emr_encounter', ['status'])

        # Changing field 'Encounter.bmi'
        db.alter_column('emr_encounter', 'bmi', self.gf('django.db.models.fields.FloatField')(null=True))

        # Adding index on 'Encounter', fields ['site_name']
        db.create_index('emr_encounter', ['site_name'])

        # Adding index on 'Encounter', fields ['bp_systolic']
        db.create_index('emr_encounter', ['bp_systolic'])

        # Adding index on 'Encounter', fields ['bp_diastolic']
        db.create_index('emr_encounter', ['bp_diastolic'])

        # Changing field 'Encounter.native_encounter_num'
        db.alter_column('emr_encounter', 'native_encounter_num', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Encounter.o2_stat'
        db.alter_column('emr_encounter', 'o2_stat', self.gf('django.db.models.fields.FloatField')(null=True))

        # Adding index on 'Encounter', fields ['o2_stat']
        db.create_index('emr_encounter', ['o2_stat'])

        # Changing field 'Encounter.peak_flow'
        db.alter_column('emr_encounter', 'peak_flow', self.gf('django.db.models.fields.FloatField')(null=True))

        # Adding index on 'Encounter', fields ['peak_flow']
        db.create_index('emr_encounter', ['peak_flow'])

        # Changing field 'Encounter.native_site_num'
        db.alter_column('emr_encounter', 'native_site_num', self.gf('django.db.models.fields.TextField')(null=True))

        # Adding index on 'Encounter', fields ['native_site_num']
        db.create_index('emr_encounter', ['native_site_num'])


    def backwards(self, orm):
        
        # Removing index on 'Encounter', fields ['native_site_num']
        db.delete_index('emr_encounter', ['native_site_num'])

        # Removing index on 'Encounter', fields ['peak_flow']
        db.delete_index('emr_encounter', ['peak_flow'])

        # Removing index on 'Encounter', fields ['o2_stat']
        db.delete_index('emr_encounter', ['o2_stat'])

        # Removing index on 'Encounter', fields ['bp_diastolic']
        db.delete_index('emr_encounter', ['bp_diastolic'])

        # Removing index on 'Encounter', fields ['bp_systolic']
        db.delete_index('emr_encounter', ['bp_systolic'])

        # Removing index on 'Encounter', fields ['site_name']
        db.delete_index('emr_encounter', ['site_name'])

        # Removing index on 'Encounter', fields ['status']
        db.delete_index('emr_encounter', ['status'])

        # Removing index on 'Patient', fields ['gender']
        db.delete_index('emr_patient', ['gender'])

        # Removing index on 'Patient', fields ['race']
        db.delete_index('emr_patient', ['race'])

        # Removing index on 'Patient', fields ['date_of_birth']
        db.delete_index('emr_patient', ['date_of_birth'])

        # Removing index on 'Prescription', fields ['dose']
        db.delete_index('emr_prescription', ['dose'])

        # Adding field 'Patient.pregnant'
        db.add_column('emr_patient', 'pregnant', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.edc'
        db.add_column('emr_encounter', 'edc', self.gf('django.db.models.fields.DateField')(blank=True, null=True, db_index=True), keep_default=False)

        # Adding field 'Encounter.event_type'
        db.add_column('emr_encounter', 'event_type', self.gf('django.db.models.fields.CharField')(blank=True, max_length=20, null=True, db_index=True), keep_default=False)

        # Adding field 'Encounter.closed_date'
        db.add_column('emr_encounter', 'closed_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.diagnosis'
        db.add_column('emr_encounter', 'diagnosis', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Encounter.pregnancy_status'
        db.add_column('emr_encounter', 'pregnancy_status', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'Encounter.encounter_type'
        db.delete_column('emr_encounter', 'encounter_type')

        # Deleting field 'Encounter.date_closed'
        db.delete_column('emr_encounter', 'date_closed')

        # Deleting field 'Encounter.pregnant'
        db.delete_column('emr_encounter', 'pregnant')

        # Deleting field 'Encounter.edd'
        db.delete_column('emr_encounter', 'edd')

        # Deleting field 'Encounter.raw_date'
        db.delete_column('emr_encounter', 'raw_date')

        # Deleting field 'Encounter.raw_date_closed'
        db.delete_column('emr_encounter', 'raw_date_closed')

        # Deleting field 'Encounter.raw_edd'
        db.delete_column('emr_encounter', 'raw_edd')

        # Deleting field 'Encounter.raw_temperature'
        db.delete_column('emr_encounter', 'raw_temperature')

        # Deleting field 'Encounter.raw_weight'
        db.delete_column('emr_encounter', 'raw_weight')

        # Deleting field 'Encounter.raw_height'
        db.delete_column('emr_encounter', 'raw_height')

        # Deleting field 'Encounter.raw_bp_systolic'
        db.delete_column('emr_encounter', 'raw_bp_systolic')

        # Deleting field 'Encounter.raw_bp_diastolic'
        db.delete_column('emr_encounter', 'raw_bp_diastolic')

        # Deleting field 'Encounter.raw_o2_stat'
        db.delete_column('emr_encounter', 'raw_o2_stat')

        # Deleting field 'Encounter.raw_peak_flow'
        db.delete_column('emr_encounter', 'raw_peak_flow')

        # Deleting field 'Encounter.raw_bmi'
        db.delete_column('emr_encounter', 'raw_bmi')

        # Deleting field 'Encounter.raw_diagnosis'
        db.delete_column('emr_encounter', 'raw_diagnosis')

        # Changing field 'Encounter.status'
        db.alter_column('emr_encounter', 'status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Encounter.bmi'
        db.alter_column('emr_encounter', 'bmi', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2))

        # Changing field 'Encounter.site_name'
        db.alter_column('emr_encounter', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Encounter.native_encounter_num'
        db.alter_column('emr_encounter', 'native_encounter_num', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Encounter.o2_stat'
        db.alter_column('emr_encounter', 'o2_stat', self.gf('django.db.models.fields.FloatField')(max_length=50, null=True))

        # Changing field 'Encounter.peak_flow'
        db.alter_column('emr_encounter', 'peak_flow', self.gf('django.db.models.fields.FloatField')(max_length=50, null=True))

        # Changing field 'Encounter.native_site_num'
        db.alter_column('emr_encounter', 'native_site_num', self.gf('django.db.models.fields.CharField')(max_length=30, null=True))


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'emr.allergy': {
            'Meta': {'object_name': 'Allergy'},
            'allergen': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static.Allergen']"}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'date_noted': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'db_index': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'problem_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_index': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'emr.encounter': {
            'Meta': {'ordering': "['date']", 'object_name': 'Encounter'},
            'bmi': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'bp_diastolic': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'bp_systolic': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'date_closed': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'edd': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'encounter_type': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'icd9_codes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['static.Icd9']", 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'native_encounter_num': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'native_site_num': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'o2_stat': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'peak_flow': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'pregnant': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'raw_bmi': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_bp_diastolic': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_bp_systolic': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_date': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_date_closed': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_diagnosis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_edd': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_height': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_o2_stat': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_peak_flow': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_temperature': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'raw_weight': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'temperature': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'emr.etlerror': {
            'Meta': {'object_name': 'EtlError'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'err_msg': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.IntegerField', [], {}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'emr.immunization': {
            'Meta': {'ordering': "['date']", 'object_name': 'Immunization'},
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'dose': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imm_id_num': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'imm_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'lot': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'visit_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'emr.laborder': {
            'Meta': {'object_name': 'LabOrder'},
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'order_id_num': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'order_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'procedure_master_num': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'procedure_name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'specimen_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'specimen_source': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'emr.labresult': {
            'Meta': {'ordering': "['date']", 'object_name': 'LabResult'},
            'abnormal_flag': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'collection_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impression': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'native_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order_id_num': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'procedure_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'ref_high_float': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'ref_high_string': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ref_low_float': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'ref_low_string': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ref_unit': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'result_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'result_float': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'result_id_num': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'result_string': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'specimen_num': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'specimen_source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'emr.labtestconcordance': {
            'Meta': {'object_name': 'LabTestConcordance'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'native_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'})
        },
        'emr.patient': {
            'Meta': {'object_name': 'Patient'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'aliases': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'areacode': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'home_language': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'marital_stat': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'mother_mrn': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'patient_id_num': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'pcp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'race': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '199', 'null': 'True', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tel_ext': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'zip5': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'db_index': 'True'})
        },
        'emr.prescription': {
            'Meta': {'ordering': "['date']", 'object_name': 'Prescription'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'directions': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'dose': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'db_index': 'True'}),
            'order_id_num': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'quantity_float': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'refills': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'emr.problem': {
            'Meta': {'object_name': 'Problem'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'icd9': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static.Icd9']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'problem_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_index': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
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
            'area_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dept': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'dept_address_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'dept_address_2': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'dept_city': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'dept_id_num': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dept_state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'dept_zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider_id_num': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'emr.socialhistory': {
            'Meta': {'object_name': 'SocialHistory'},
            'alcohol_use': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'tobacco_use': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'hef.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.EventType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'hef.eventrecordtag': {
            'Meta': {'unique_together': "[('event', 'content_type', 'object_id')]", 'object_name': 'EventRecordTag'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tag_set'", 'to': "orm['hef.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'hef.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'heuristic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.Heuristic']"}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'primary_key': 'True', 'db_index': 'True'})
        },
        'hef.heuristic': {
            'Meta': {'object_name': 'Heuristic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'static.allergen': {
            'Meta': {'object_name': 'Allergen'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'})
        },
        'static.icd9': {
            'Meta': {'object_name': 'Icd9'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['emr']
