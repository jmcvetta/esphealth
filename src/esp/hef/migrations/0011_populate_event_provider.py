# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.contrib.contenttypes import generic

class Migration(DataMigration):
    
    depends_on = (
        ('emr', '0002_rename_source_system_id_num_fields'),
        )

    def forwards(self, orm):
        gfk = generic.GenericForeignKey()
        gfk.contribute_to_class(orm.EventRecordTag, "content_object")
        unbound_events = orm.Event.objects.filter(provider__isnull=True)
        total = unbound_events.count()
        count = 0
        for e in unbound_events:
            obj = e.tag_set.all()[0].content_object
            e.provider = orm['emr.Provider'].objects.get(pk=obj.provider.pk)
            e.save()
            count += 1
            print 'Populated Event.provider %20s / %s' % (count, total)


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
            'native_encounter_num': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
            'patient_id_num': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
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
        'hef.calculatedbilirubinheuristic': {
            'Meta': {'object_name': 'CalculatedBilirubinHeuristic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hef.datedimension': {
            'Meta': {'object_name': 'DateDimension'},
            'date': ('django.db.models.fields.DateField', [], {'primary_key': 'True'}),
            'day': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'quarter': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'week': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
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
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hef.EventType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Patient']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['emr.Provider']", 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'unique_together': "(['test', 'native_code'],)", 'object_name': 'LabTestMap'},
            'native_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'code_match_type': ('django.db.models.fields.CharField', [], {'default': "'exact'", 'max_length': '32'}),
            'excluded_indeterminate_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'excluded_indeterminate_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'excluded_negative_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'excluded_negative_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'excluded_positive_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'excluded_positive_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'extra_indeterminate_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'extra_indeterminate_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'extra_negative_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'extra_negative_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'extra_positive_strings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'extra_positive_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['hef.ResultString']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'output_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'output_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'record_type': ('django.db.models.fields.CharField', [], {'default': "'both'", 'max_length': '8'}),
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
            'Meta': {'ordering': "['value']", 'object_name': 'ResultString'},
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

    complete_apps = ['emr', 'hef']