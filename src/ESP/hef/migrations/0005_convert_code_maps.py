# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        CodeMap = orm['conf.CodeMap']
        AbstractLabTest = orm['hef.AbstractLabTest']
        LabTestMap = orm['hef.LabTestMap']
        
        
        for item in self.ABSTRACT_LAB_TESTS:
            obj, created = AbstractLabTest.objects.get_or_create(
                name=item[0],
			    defaults = {
			        'verbose_name': item[1],
			        },
                )
            if created:
                print 'Created AbstractLabTest: %s' % obj
        
        test_names = AbstractLabTest.objects.values_list('name', flat=True)
        for cm in CodeMap.objects.all():
            heuristic = str(cm.heuristic)
            if heuristic in self.TRANSLATION:
                heuristic = self.TRANSLATION[heuristic]
            if heuristic == 'high_calc_bilirubin':
                if cm.native_name.lower().find('indirect') == -1: # Direct
                    heuristic = 'bilirubin_direct'
                else: # Indirect
                    heuristic = 'bilirubin_indirect'
            if not heuristic in test_names:
                print 'No AbstractLabTest found matching "%s"' % heuristic
                continue
            test = AbstractLabTest.objects.get(name=heuristic)
            ltm, created = LabTestMap.objects.get_or_create(
                test = test,
                native_code = cm.native_code,
                defaults = {
                    'code_match_type': 'exact',
                    'record_type': 'result',
                    'threshold': cm.threshold,
                    'reportable': cm.reportable,
                    'output_code': cm.output_code,
                    'output_name': cm.output_name,
                    'snomed_pos': cm.snomed_pos,
                    'snomed_neg': cm.snomed_neg,
                    'snomed_ind': cm.snomed_ind,
                    'notes': cm.notes,
                    }
                )
            if created:
                print 'Created new LabTestMap for %s, %s' % (test.verbose_name, cm.native_code)
            else:
                print 'LabTestMap for %s, %s already exists' % (test.verbose_name, cm.native_code)

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")


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
            'Meta': {'unique_together': "(['test', 'native_code'],)", 'object_name': 'LabTestMap'},
            'native_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
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
    
    TRANSLATION = {
        'rpr': 'syphilis_rpr',
        'vdrl_serum': 'syphilis_vdrl_serum',
        'vdrl_csf': 'syphilis_vdrl_csf',
        'hep_b_surface': 'hep_b_surface_antigen',
        'tppa': 'syphilis_tppa',
        'hep_b_core': 'hep_b_core_antibody',
        'tp_igg': 'syphilis_tp_igg',
        'hep_e_ab': 'hep_e_antibody',
        'hep_a_igm': 'hep_a_igm_antibody',
        'hav_tot': 'hep_a_tot_antibody',
        'fta_abs': 'syphilis_fta_abs',
        'hep_b_igm': 'hep_b_igm_antibody',
        'lyme_igg': 'lyme_igg_eia',
        'lyme_igm': 'lyme_igm_eia',
        'ttpa': 'syphilis_tppa',
        'ogtt75_30m': 'ogtt75_30min',
        'ogtt75_90m': 'ogtt75_90min',
        'ogtt100_30m': 'ogtt100_30min',
        'ogtt100_90m': 'ogtt100_90min',
        'total_bilirubin_high': 'bilirubin_total',
        'high_calc_bilirubin': 'bilirubin_calculated',
        }
        
    ABSTRACT_LAB_TESTS = [
        ('a1c', 'Glycated hemoglobin (A1C)'),
        ('alt', 'Alanine Aminotransferase blood test'),
        ('ast', 'Aspartate Aminotransferase blood test'),
        ('bilirubin_direct', 'Bilirubin glucuronidated'),
        ('bilirubin_indirect', 'Bilirubin non-glucuronidated'),
        ('bilirubin_total', 'Bilirubin glucuronidated + bilirubin non-glucuronidated'),
        ('chlamydia', 'Chlamydia test'),
        ('giardiasis_antigen', 'Giardiasis Antigen'),
        ('glucose_fasting', 'Fasting glucose (several variations)'),
        ('gonorrhea', 'Gonorrhea test'),
        ('hep_a_igm_antibody', 'Hepatitis A IgM antibody'),
        ('hep_a_tot_antibody', 'Hepatitis A Total Antibodies'),
        ('hep_b_core_antibody', 'Hepatitis B core general antibody'),
        ('hep_b_e_antigen', 'Hepatitis B "e" antigen'),
        ('hep_b_igm_antibody', 'Hepatitis B core IgM antibody'),
        ('hep_b_surface_antigen', 'Hepatitis B surface antigen'),
        ('hep_b_viral_dna', 'Hepatitis B viral DNA'),
        ('hep_c_elisa', 'Hepatitis C ELISA'),
        ('hep_c_riba', 'Hepatitis C RIBA'),
        ('hep_c_rna', 'Hepatitis C RNA'),
        ('hep_c_signal_cutoff', 'Hepatitis C signal cutoff'),
        ('hep_e_antibody', 'Hepatitis E antibody'),
        ('lyme_elisa', 'Lyme ELISA'),
        ('lyme_igg_eia', 'Lyme IGG (EIA)'),
        ('lyme_igg_wb', 'Lyme IGG (Western Blot)'),
        ('lyme_igm_eia', 'Lyme IGM (EIA)'),
        ('lyme_igm_wb', 'Lyme IGM (Western Blot)'),
        ('lyme_pcr', 'Lyme PCR'),
        ('ogtt100_1hr', 'Oral Glucose Tolerance Test 100 gram 1 hour post'),
        ('ogtt100_2hr', 'Oral Glucose Tolerance Test 100 gram 2 hour post'),
        ('ogtt100_30min', 'Oral Glucose Tolerance Test 100 gram 30 minutes post'),
        ('ogtt100_3hr', 'Oral Glucose Tolerance Test 100 gram 3 hour post'),
        ('ogtt100_4hr', 'Oral Glucose Tolerance Test 100 gram 4 hour post'),
        ('ogtt100_5hr', 'Oral Glucose Tolerance Test 100 gram 5 hour post'),
        ('ogtt100_90min', 'Oral Glucose Tolerance Test 100 gram 90 minutes post'),
        ('ogtt100_fasting', 'Oral Glucose Tolerance Test 100 gram fasting'),
        ('ogtt100_fasting_urine', 'Oral Glucose Tolerance Test 100 gram fasting (urine)'),
        ('ogtt50_1hr', 'Oral Glucose Tolerance Test 50 gram 1 hour post'),
        ('ogtt50_fasting', 'Oral Glucose Tolerance Test 50 gram Fasting'),
        ('ogtt50_random', 'Oral Glucose Tolerance Test 50 gram Random'),
        ('ogtt75_1hr', 'Oral Glucose Tolerance Test 75 gram 1 hour post'),
        ('ogtt75_2hr', 'Oral Glucose Tolerance Test 75 gram 2 hour post'),
        ('ogtt75_30min', 'Oral Glucose Tolerance Test 75 gram 30 minutes post'),
        ('ogtt75_90min', 'Oral Glucose Tolerance Test 75 gram 90 minutes post'),
        ('ogtt75_fasting', 'Oral Glucose Tolerance Test 75 gram fasting'),
        ('ogtt75_fasting_urine', 'Oral Glucose Tolerance Test 75 gram fasting, urine'),
        ('ogtt75_series', 'Oral Glucose Tolerance Test 75 gram Series'),
        ('pertussis_culture', 'Pertussis Culture'),
        ('pertussis_pcr', 'Pertussis PCR'),
        ('pertussis_serology', 'Pertussis serology'),
        ('syphilis_fta_abs', 'Syphilis FTA-ABS'),
        ('syphilis_rpr', 'Syphilis rapid plasma reagin (RPR)'),
        ('syphilis_tp_igg', 'Syphilis TP-IGG'),
        ('syphilis_tppa', 'Syphilis TP-PA'),
        ('syphilis_vdrl_csf', 'Syphilis VDRL-CSF'),
        ('syphilis_vdrl_serum', 'Syphilis VDRL serum'),
        ('tb_lab', 'Tuberculosis lab test (several varieties)'),
        ]
