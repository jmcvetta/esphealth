# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Pattern'
        db.create_table('nodis_pattern', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('pattern', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('nodis', ['Pattern'])

        # Adding model 'Case'
        db.create_table('nodis_case', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'])),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'])),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('pattern', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodis.Pattern'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='AR', max_length=10)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('sent_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodis', ['Case'])

        # Adding unique constraint on 'Case', fields ['patient', 'condition', 'date']
        db.create_unique('nodis_case', ['patient_id', 'condition', 'date'])

        # Adding M2M table for field events on 'Case'
        db.create_table('nodis_case_events', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('case', models.ForeignKey(orm['nodis.case'], null=False)),
            ('event', models.ForeignKey(orm['hef.event'], null=False))
        ))
        db.create_unique('nodis_case_events', ['case_id', 'event_id'])

        # Adding M2M table for field events_before on 'Case'
        db.create_table('nodis_case_events_before', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('case', models.ForeignKey(orm['nodis.case'], null=False)),
            ('event', models.ForeignKey(orm['hef.event'], null=False))
        ))
        db.create_unique('nodis_case_events_before', ['case_id', 'event_id'])

        # Adding M2M table for field events_after on 'Case'
        db.create_table('nodis_case_events_after', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('case', models.ForeignKey(orm['nodis.case'], null=False)),
            ('event', models.ForeignKey(orm['hef.event'], null=False))
        ))
        db.create_unique('nodis_case_events_after', ['case_id', 'event_id'])

        # Adding M2M table for field events_ever on 'Case'
        db.create_table('nodis_case_events_ever', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('case', models.ForeignKey(orm['nodis.case'], null=False)),
            ('event', models.ForeignKey(orm['hef.event'], null=False))
        ))
        db.create_unique('nodis_case_events_ever', ['case_id', 'event_id'])

        # Adding model 'CaseStatusHistory'
        db.create_table('nodis_casestatushistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodis.Case'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('old_status', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('new_status', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('changed_by', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodis', ['CaseStatusHistory'])

        # Adding model 'ReportRun'
        db.create_table('nodis_reportrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('nodis', ['ReportRun'])

        # Adding model 'Report'
        db.create_table('nodis_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodis.ReportRun'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('nodis', ['Report'])

        # Adding M2M table for field cases on 'Report'
        db.create_table('nodis_report_cases', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('report', models.ForeignKey(orm['nodis.report'], null=False)),
            ('case', models.ForeignKey(orm['nodis.case'], null=False))
        ))
        db.create_unique('nodis_report_cases', ['report_id', 'case_id'])

        # Adding model 'ReferenceCaseList'
        db.create_table('nodis_referencecaselist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodis', ['ReferenceCaseList'])

        # Adding model 'ReferenceCase'
        db.create_table('nodis_referencecase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodis.ReferenceCaseList'])),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('ignore', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodis', ['ReferenceCase'])

        # Adding model 'ValidatorRun'
        db.create_table('nodis_validatorrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodis.ReferenceCaseList'])),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('related_margin', self.gf('django.db.models.fields.IntegerField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodis', ['ValidatorRun'])

        # Adding model 'ValidatorResult'
        db.create_table('nodis_validatorresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodis.ValidatorRun'])),
            ('ref_case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodis.ReferenceCase'], null=True, blank=True)),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('disposition', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('nodis', ['ValidatorResult'])

        # Adding M2M table for field events on 'ValidatorResult'
        db.create_table('nodis_validatorresult_events', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('validatorresult', models.ForeignKey(orm['nodis.validatorresult'], null=False)),
            ('event', models.ForeignKey(orm['hef.event'], null=False))
        ))
        db.create_unique('nodis_validatorresult_events', ['validatorresult_id', 'event_id'])

        # Adding M2M table for field cases on 'ValidatorResult'
        db.create_table('nodis_validatorresult_cases', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('validatorresult', models.ForeignKey(orm['nodis.validatorresult'], null=False)),
            ('case', models.ForeignKey(orm['nodis.case'], null=False))
        ))
        db.create_unique('nodis_validatorresult_cases', ['validatorresult_id', 'case_id'])

        # Adding M2M table for field lab_results on 'ValidatorResult'
        db.create_table('nodis_validatorresult_lab_results', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('validatorresult', models.ForeignKey(orm['nodis.validatorresult'], null=False)),
            ('labresult', models.ForeignKey(orm['emr.labresult'], null=False))
        ))
        db.create_unique('nodis_validatorresult_lab_results', ['validatorresult_id', 'labresult_id'])

        # Adding M2M table for field encounters on 'ValidatorResult'
        db.create_table('nodis_validatorresult_encounters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('validatorresult', models.ForeignKey(orm['nodis.validatorresult'], null=False)),
            ('encounter', models.ForeignKey(orm['emr.encounter'], null=False))
        ))
        db.create_unique('nodis_validatorresult_encounters', ['validatorresult_id', 'encounter_id'])

        # Adding M2M table for field prescriptions on 'ValidatorResult'
        db.create_table('nodis_validatorresult_prescriptions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('validatorresult', models.ForeignKey(orm['nodis.validatorresult'], null=False)),
            ('prescription', models.ForeignKey(orm['emr.prescription'], null=False))
        ))
        db.create_unique('nodis_validatorresult_prescriptions', ['validatorresult_id', 'prescription_id'])

        # Adding model 'Gdm'
        db.create_table(u'gdm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('alogrithm', self.gf('django.db.models.fields.TextField')()),
            ('patient_id', self.gf('django.db.models.fields.IntegerField')()),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=199)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=199)),
            ('native_code', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('native_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('result_string', self.gf('django.db.models.fields.TextField')()),
            ('event_id', self.gf('django.db.models.fields.IntegerField')()),
            ('event_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('nodis', ['Gdm'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Case', fields ['patient', 'condition', 'date']
        db.delete_unique('nodis_case', ['patient_id', 'condition', 'date'])

        # Deleting model 'Pattern'
        db.delete_table('nodis_pattern')

        # Deleting model 'Case'
        db.delete_table('nodis_case')

        # Removing M2M table for field events on 'Case'
        db.delete_table('nodis_case_events')

        # Removing M2M table for field events_before on 'Case'
        db.delete_table('nodis_case_events_before')

        # Removing M2M table for field events_after on 'Case'
        db.delete_table('nodis_case_events_after')

        # Removing M2M table for field events_ever on 'Case'
        db.delete_table('nodis_case_events_ever')

        # Deleting model 'CaseStatusHistory'
        db.delete_table('nodis_casestatushistory')

        # Deleting model 'ReportRun'
        db.delete_table('nodis_reportrun')

        # Deleting model 'Report'
        db.delete_table('nodis_report')

        # Removing M2M table for field cases on 'Report'
        db.delete_table('nodis_report_cases')

        # Deleting model 'ReferenceCaseList'
        db.delete_table('nodis_referencecaselist')

        # Deleting model 'ReferenceCase'
        db.delete_table('nodis_referencecase')

        # Deleting model 'ValidatorRun'
        db.delete_table('nodis_validatorrun')

        # Deleting model 'ValidatorResult'
        db.delete_table('nodis_validatorresult')

        # Removing M2M table for field events on 'ValidatorResult'
        db.delete_table('nodis_validatorresult_events')

        # Removing M2M table for field cases on 'ValidatorResult'
        db.delete_table('nodis_validatorresult_cases')

        # Removing M2M table for field lab_results on 'ValidatorResult'
        db.delete_table('nodis_validatorresult_lab_results')

        # Removing M2M table for field encounters on 'ValidatorResult'
        db.delete_table('nodis_validatorresult_encounters')

        # Removing M2M table for field prescriptions on 'ValidatorResult'
        db.delete_table('nodis_validatorresult_prescriptions')

        # Deleting model 'Gdm'
        db.delete_table(u'gdm')


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
            'event_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'icd9_codes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['static.Icd9']", 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'natural_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_natural_key': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'o2_stat': ('django.db.models.fields.FloatField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'}),
            'peak_flow': ('django.db.models.fields.FloatField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'pregnancy_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'temperature': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'emr.labresult': {
            'Meta': {'ordering': "['date']", 'object_name': 'LabResult'},
            'abnormal_flag': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'collection_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impression': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'native_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order_natural_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
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
            'result_num': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'result_string': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'specimen_num': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'specimen_source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
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
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'home_language': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'marital_stat': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'mother_mrn': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'natural_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'pcp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
            'pregnant': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
            'dose': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'db_index': 'True'}),
            'natural_key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
            'dept_natural_key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'dept_state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'dept_zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provenance']"}),
            'natural_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'hef.event': {
            'Meta': {'ordering': "['date', 'patient', 'name']", 'unique_together': "(['name', 'date', 'patient', 'content_type', 'object_id'],)", 'object_name': 'Event'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']"}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.Run']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'hef.run': {
            'Meta': {'object_name': 'Run'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'r'", 'max_length': '1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'nodis.case': {
            'Meta': {'ordering': "['id']", 'unique_together': "(['patient', 'condition', 'date'],)", 'object_name': 'Case'},
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hef.Event']", 'symmetrical': 'False'}),
            'events_after': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'case_after'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.Event']"}),
            'events_before': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'case_before'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.Event']"}),
            'events_ever': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'case_ever'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']"}),
            'pattern': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodis.Pattern']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']"}),
            'sent_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'AR'", 'max_length': '10'}),
            'updated_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'nodis.casestatushistory': {
            'Meta': {'object_name': 'CaseStatusHistory'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodis.Case']"}),
            'changed_by': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'old_status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'nodis.gdm': {
            'Meta': {'object_name': 'Gdm', 'db_table': "u'gdm'"},
            'alogrithm': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'event_id': ('django.db.models.fields.IntegerField', [], {}),
            'event_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '199'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '199'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'native_code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'native_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'patient_id': ('django.db.models.fields.IntegerField', [], {}),
            'result_string': ('django.db.models.fields.TextField', [], {})
        },
        'nodis.pattern': {
            'Meta': {'object_name': 'Pattern'},
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'nodis.referencecase': {
            'Meta': {'object_name': 'ReferenceCase'},
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodis.ReferenceCaseList']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']", 'null': 'True', 'blank': 'True'})
        },
        'nodis.referencecaselist': {
            'Meta': {'object_name': 'ReferenceCaseList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'nodis.report': {
            'Meta': {'object_name': 'Report'},
            'cases': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['nodis.Case']", 'symmetrical': 'False'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodis.ReportRun']"}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'nodis.reportrun': {
            'Meta': {'object_name': 'ReportRun'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'nodis.validatorresult': {
            'Meta': {'object_name': 'ValidatorResult'},
            'cases': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['nodis.Case']", 'null': 'True', 'blank': 'True'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'disposition': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'encounters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['emr.Encounter']", 'null': 'True', 'blank': 'True'}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['hef.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lab_results': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['emr.LabResult']", 'null': 'True', 'blank': 'True'}),
            'prescriptions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['emr.Prescription']", 'null': 'True', 'blank': 'True'}),
            'ref_case': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodis.ReferenceCase']", 'null': 'True', 'blank': 'True'}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodis.ValidatorRun']"})
        },
        'nodis.validatorrun': {
            'Meta': {'object_name': 'ValidatorRun'},
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodis.ReferenceCaseList']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'related_margin': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'static.icd9': {
            'Meta': {'object_name': 'Icd9'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['nodis']
