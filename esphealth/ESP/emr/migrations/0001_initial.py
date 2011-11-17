# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Provenance'
        db.create_table('emr_provenance', (
            ('provenance_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=500, db_index=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('valid_rec_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('error_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['Provenance'])

        # Adding unique constraint on 'Provenance', fields ['timestamp', 'source', 'hostname']
        db.create_unique('emr_provenance', ['timestamp', 'source', 'hostname'])

        # Adding model 'EtlError'
        db.create_table('emr_etlerror', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('line', self.gf('django.db.models.fields.IntegerField')()),
            ('err_msg', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('emr', ['EtlError'])

        # Adding model 'LabTestConcordance'
        db.create_table('emr_labtestconcordance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('native_code', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('native_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, db_index=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('emr', ['LabTestConcordance'])

        # Adding model 'Provider'
        db.create_table('emr_provider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('natural_key', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, unique=True, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('dept_id_num', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('dept', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('dept_address_1', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('dept_address_2', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('dept_city', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('dept_state', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('dept_zip', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('area_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['Provider'])

        # Adding model 'Patient'
        db.create_table('emr_patient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('natural_key', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, unique=True, null=True, blank=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=199, null=True, blank=True)),
            ('pcp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('zip5', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, db_index=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('areacode', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tel', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('tel_ext', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_of_death', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('pregnant', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('home_language', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ssn', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('marital_stat', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('religion', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('aliases', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mother_mrn', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('occupation', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['Patient'])

        # Adding model 'LabResult'
        db.create_table('emr_labresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('native_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=30, null=True, blank=True)),
            ('native_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('order_num', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('result_date', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('collection_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('result_num', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('ref_high_string', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('ref_low_string', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('ref_high_float', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('ref_low_float', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('ref_unit', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('abnormal_flag', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('result_float', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('result_string', self.gf('django.db.models.fields.TextField')(db_index=True, max_length=2000, null=True, blank=True)),
            ('specimen_num', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('specimen_source', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('impression', self.gf('django.db.models.fields.TextField')(max_length=2000, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('procedure_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['LabResult'])

        # Adding model 'LabOrder'
        db.create_table('emr_laborder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('order_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('procedure_master_num', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('modifier', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('specimen_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('order_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, blank=True)),
            ('procedure_name', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('specimen_source', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['LabOrder'])

        # Adding model 'Prescription'
        db.create_table('emr_prescription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('order_num', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.TextField')(max_length=3000, db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('directions', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
            ('dose', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('frequency', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('quantity', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('quantity_float', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('refills', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('route', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['Prescription'])

        # Adding model 'Encounter'
        db.create_table('emr_encounter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('closed_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('native_site_num', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('natural_key', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('event_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('pregnancy_status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('edc', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('temperature', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('bp_systolic', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('bp_diastolic', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('o2_stat', self.gf('django.db.models.fields.FloatField')(max_length=50, null=True, blank=True)),
            ('peak_flow', self.gf('django.db.models.fields.FloatField')(max_length=50, null=True, blank=True)),
            ('diagnosis', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('bmi', self.gf('django.db.models.fields.DecimalField')(db_index=True, null=True, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('emr', ['Encounter'])

        # Adding M2M table for field icd9_codes on 'Encounter'
        db.create_table('emr_encounter_icd9_codes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('encounter', models.ForeignKey(orm['emr.encounter'], null=False)),
            ('icd9', models.ForeignKey(orm['static.icd9'], null=False))
        ))
        db.create_unique('emr_encounter_icd9_codes', ['encounter_id', 'icd9_id'])

        # Adding model 'Immunization'
        db.create_table('emr_immunization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('imm_id_num', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('imm_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('dose', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('manufacturer', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('lot', self.gf('django.db.models.fields.TextField')(max_length=500, null=True, blank=True)),
            ('visit_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['Immunization'])

        # Adding model 'SocialHistory'
        db.create_table('emr_socialhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tobacco_use', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('alcohol_use', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['SocialHistory'])

        # Adding model 'Allergy'
        db.create_table('emr_allergy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('problem_id', self.gf('django.db.models.fields.IntegerField')(null=True, db_index=True)),
            ('date_noted', self.gf('django.db.models.fields.DateField')(null=True, db_index=True)),
            ('allergen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['static.Allergen'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_index=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('emr', ['Allergy'])

        # Adding model 'Problem'
        db.create_table('emr_problem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provenance'])),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Patient'], null=True, blank=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emr.Provider'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('problem_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('icd9', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['static.Icd9'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_index=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('emr', ['Problem'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Provenance', fields ['timestamp', 'source', 'hostname']
        db.delete_unique('emr_provenance', ['timestamp', 'source', 'hostname'])

        # Deleting model 'Provenance'
        db.delete_table('emr_provenance')

        # Deleting model 'EtlError'
        db.delete_table('emr_etlerror')

        # Deleting model 'LabTestConcordance'
        db.delete_table('emr_labtestconcordance')

        # Deleting model 'Provider'
        db.delete_table('emr_provider')

        # Deleting model 'Patient'
        db.delete_table('emr_patient')

        # Deleting model 'LabResult'
        db.delete_table('emr_labresult')

        # Deleting model 'LabOrder'
        db.delete_table('emr_laborder')

        # Deleting model 'Prescription'
        db.delete_table('emr_prescription')

        # Deleting model 'Encounter'
        db.delete_table('emr_encounter')

        # Removing M2M table for field icd9_codes on 'Encounter'
        db.delete_table('emr_encounter_icd9_codes')

        # Deleting model 'Immunization'
        db.delete_table('emr_immunization')

        # Deleting model 'SocialHistory'
        db.delete_table('emr_socialhistory')

        # Deleting model 'Allergy'
        db.delete_table('emr_allergy')

        # Deleting model 'Problem'
        db.delete_table('emr_problem')


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
            'native_site_num': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
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
            'order_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
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
            'collection_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impression': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'native_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'native_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order_num': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
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
            'order_num': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
            'dept_id_num': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
