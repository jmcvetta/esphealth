# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting field 'Event.run'
        db.delete_column('hef_event', 'run_id')

        # Deleting field 'Timespan.run'
        db.delete_column('hef_timespan', 'run_id')
        
        # Deleting model 'Run'
        db.delete_table('hef_run')

        # Adding model 'EventType'
        db.create_table('hef_eventtype', (
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=128, primary_key=True, db_index=True)),
            ('heuristic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hef.Heuristic'])),
        ))
        db.send_create_signal('hef', ['EventType'])

        # Adding model 'ResultString'
        db.create_table('hef_resultstring', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('indicates', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('match_type', self.gf('django.db.models.fields.CharField')(default='istartswith', max_length=32)),
            ('applies_to_all', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('hef', ['ResultString'])

        # Adding model 'LabTestMap'
        db.create_table('hef_labtestmap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hef.AbstractLabTest'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
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
        db.send_create_signal('hef', ['LabTestMap'])

        # Adding M2M table for field extra_positive_strings on 'LabTestMap'
        db.create_table('hef_labtestmap_extra_positive_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['hef.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['hef.resultstring'], null=False))
        ))
        db.create_unique('hef_labtestmap_extra_positive_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding M2M table for field extra_negative_strings on 'LabTestMap'
        db.create_table('hef_labtestmap_extra_negative_strings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('labtestmap', models.ForeignKey(orm['hef.labtestmap'], null=False)),
            ('resultstring', models.ForeignKey(orm['hef.resultstring'], null=False))
        ))
        db.create_unique('hef_labtestmap_extra_negative_strings', ['labtestmap_id', 'resultstring_id'])

        # Adding model 'LabResultFixedThresholdHeuristic'
        db.create_table('hef_labresultfixedthresholdheuristic', (
            ('heuristic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hef.Heuristic'], unique=True, primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hef.AbstractLabTest'])),
            ('threshold', self.gf('django.db.models.fields.FloatField')()),
            ('date_field', self.gf('django.db.models.fields.CharField')(default='order', max_length=32)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['LabResultFixedThresholdHeuristic'])

        # Adding model 'EncounterHeuristic'
        db.create_table('hef_encounterheuristic', (
            ('heuristic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hef.Heuristic'], unique=True, primary_key=True)),
            ('icd9_codes', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('code_match_type', self.gf('django.db.models.fields.CharField')(default='exact', max_length=32, db_index=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['EncounterHeuristic'])

        # Adding model 'AbstractLabTest'
        db.create_table('hef_abstractlabtest', (
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, primary_key=True, db_index=True)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, db_index=True)),
            ('reportable', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('output_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('output_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_pos', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_neg', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('snomed_ind', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['AbstractLabTest'])

        # Adding model 'PrescriptionHeuristic'
        db.create_table('hef_prescriptionheuristic', (
            ('heuristic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hef.Heuristic'], unique=True, primary_key=True)),
            ('drugs', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('min_quantity', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('require', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('exclude', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['PrescriptionHeuristic'])

        # Adding M2M table for field dose on 'PrescriptionHeuristic'
        db.create_table('hef_prescriptionheuristic_dose', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('prescriptionheuristic', models.ForeignKey(orm['hef.prescriptionheuristic'], null=False)),
            ('dose', models.ForeignKey(orm['hef.dose'], null=False))
        ))
        db.create_unique('hef_prescriptionheuristic_dose', ['prescriptionheuristic_id', 'dose_id'])

        # Adding model 'LabOrderHeuristic'
        db.create_table('hef_laborderheuristic', (
            ('heuristic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hef.Heuristic'], unique=True, primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hef.AbstractLabTest'], unique=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['LabOrderHeuristic'])

        # Adding model 'LabResultPositiveHeuristic'
        db.create_table('hef_labresultpositiveheuristic', (
            ('heuristic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hef.Heuristic'], unique=True, primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hef.AbstractLabTest'], unique=True)),
            ('titer', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('date_field', self.gf('django.db.models.fields.CharField')(default='order', max_length=32)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['LabResultPositiveHeuristic'])

        # Adding model 'Heuristic'
        db.create_table('hef_heuristic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
        ))
        db.send_create_signal('hef', ['Heuristic'])

        # Adding model 'Dose'
        db.create_table('hef_dose', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quantity', self.gf('django.db.models.fields.FloatField')()),
            ('units', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('hef', ['Dose'])

        # Adding model 'LabResultRatioHeuristic'
        db.create_table('hef_labresultratioheuristic', (
            ('heuristic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hef.Heuristic'], unique=True, primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hef.AbstractLabTest'])),
            ('ratio', self.gf('django.db.models.fields.FloatField')()),
            ('date_field', self.gf('django.db.models.fields.CharField')(default='order', max_length=32)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['LabResultRatioHeuristic'])

        # Removing unique constraint on 'Event', fields ['date', 'patient', 'name', 'content_type', 'object_id']
        db.delete_unique('hef_event', ['date', 'patient_id', 'name', 'content_type_id', 'object_id'])
        
        # Rename field 'Event.name' to 'Event.event_type_id'
        db.rename_column('hef_event', 'name', 'event_type_id')
        
        # Adding model 'LabResultAnyHeuristic'
        db.create_table('hef_labresultanyheuristic', (
            ('heuristic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hef.Heuristic'], unique=True, primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hef.AbstractLabTest'], unique=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hef', ['LabResultAnyHeuristic'])



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
            'record_type': ('django.db.models.fields.CharField', [], {'default': "'both'", 'max_length': '8'}),
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
