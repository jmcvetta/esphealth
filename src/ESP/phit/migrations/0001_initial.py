# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PracticePatients'
        db.create_table('phit_practicepatients', (
            ('month', self.gf('django.db.models.fields.DateField')(primary_key=True)),
            ('patient_count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('phit', ['PracticePatients'])


    def backwards(self, orm):
        
        # Deleting model 'PracticePatients'
        db.delete_table('phit_practicepatients')


    models = {
        'phit.practicepatients': {
            'Meta': {'object_name': 'PracticePatients'},
            'month': ('django.db.models.fields.DateField', [], {'primary_key': 'True'}),
            'patient_count': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['phit']
