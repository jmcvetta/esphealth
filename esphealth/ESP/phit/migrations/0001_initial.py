# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MonthlyStatistics'
        db.create_table('phit_monthlystatistics', (
            ('month', self.gf('django.db.models.fields.DateField')(primary_key=True)),
            ('practice_patients', self.gf('django.db.models.fields.IntegerField')()),
            ('total_encounters', self.gf('django.db.models.fields.IntegerField')()),
            ('patients_with_encounter', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('phit', ['MonthlyStatistics'])


    def backwards(self, orm):
        
        # Deleting model 'MonthlyStatistics'
        db.delete_table('phit_monthlystatistics')


    models = {
        'phit.monthlystatistics': {
            'Meta': {'object_name': 'MonthlyStatistics'},
            'month': ('django.db.models.fields.DateField', [], {'primary_key': 'True'}),
            'patients_with_encounter': ('django.db.models.fields.IntegerField', [], {}),
            'practice_patients': ('django.db.models.fields.IntegerField', [], {}),
            'total_encounters': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['phit']
