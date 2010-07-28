# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Loinc'
        db.create_table('static_loinc', (
            ('dt_last_ch', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('exmpl_answers', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('reference', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order_obs', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('submitted_units', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('loinc_num', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('hl7_field_subfield_id', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('scale_typ', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('code_table', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('species', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('survey_quest_src', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('exact_cmp_sy', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inpc_percentage', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('answerlist', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('system', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('chng_type', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('norm_range', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('method_typ', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('example_units', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('survey_quest_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('scope', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('shortname', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('final', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('relat_nms', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('external_copyright_notice', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('relatednames2', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('panelelements', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('long_common_name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('component', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('map_to', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('formula', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('naaccr_id', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('loinc_class_field', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('time_aspct', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('base_name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ipcc_units', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('classtype', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('molar_mass', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('unitsrequired', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cdisc_common_tests', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('property', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('acssym', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('setroot', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('static', ['Loinc'])

        # Adding model 'Icd9'
        db.create_table('static_icd9', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('static', ['Icd9'])

        # Adding model 'Ndc'
        db.create_table('static_ndc', (
            ('trade_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('product_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=5, null=True, blank=True)),
            ('label_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=10, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('static', ['Ndc'])

        # Adding model 'Vaccine'
        db.create_table('static_vaccine', (
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('static', ['Vaccine'])

        # Adding model 'ImmunizationManufacturer'
        db.create_table('static_immunizationmanufacturer', (
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('use_instead', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['static.ImmunizationManufacturer'], null=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('static', ['ImmunizationManufacturer'])

        # Adding M2M table for field vaccines_produced on 'ImmunizationManufacturer'
        db.create_table('static_immunizationmanufacturer_vaccines_produced', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('immunizationmanufacturer', models.ForeignKey(orm['static.immunizationmanufacturer'], null=False)),
            ('vaccine', models.ForeignKey(orm['static.vaccine'], null=False))
        ))
        db.create_unique('static_immunizationmanufacturer_vaccines_produced', ['immunizationmanufacturer_id', 'vaccine_id'])

        # Adding model 'Allergen'
        db.create_table('static_allergen', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal('static', ['Allergen'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Loinc'
        db.delete_table('static_loinc')

        # Deleting model 'Icd9'
        db.delete_table('static_icd9')

        # Deleting model 'Ndc'
        db.delete_table('static_ndc')

        # Deleting model 'Vaccine'
        db.delete_table('static_vaccine')

        # Deleting model 'ImmunizationManufacturer'
        db.delete_table('static_immunizationmanufacturer')

        # Removing M2M table for field vaccines_produced on 'ImmunizationManufacturer'
        db.delete_table('static_immunizationmanufacturer_vaccines_produced')

        # Deleting model 'Allergen'
        db.delete_table('static_allergen')
    
    
    models = {
        'static.allergen': {
            'Meta': {'object_name': 'Allergen'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'})
        },
        'static.icd9': {
            'Meta': {'object_name': 'Icd9'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'static.immunizationmanufacturer': {
            'Meta': {'object_name': 'ImmunizationManufacturer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'use_instead': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static.ImmunizationManufacturer']", 'null': 'True'}),
            'vaccines_produced': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['static.Vaccine']", 'symmetrical': 'False'})
        },
        'static.loinc': {
            'Meta': {'object_name': 'Loinc'},
            'acssym': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'answerlist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'base_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cdisc_common_tests': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'chng_type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'classtype': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'code_table': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'component': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dt_last_ch': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'exact_cmp_sy': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'example_units': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'exmpl_answers': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'external_copyright_notice': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'final': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'formula': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hl7_field_subfield_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'inpc_percentage': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ipcc_units': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'loinc_class_field': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'loinc_num': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'long_common_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'map_to': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'method_typ': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'molar_mass': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'naaccr_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'norm_range': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'order_obs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'panelelements': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'property': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'relat_nms': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'relatednames2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scale_typ': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scope': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'setroot': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'shortname': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submitted_units': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'survey_quest_src': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'survey_quest_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'system': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'time_aspct': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'unitsrequired': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'static.ndc': {
            'Meta': {'object_name': 'Ndc'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'product_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'trade_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'static.vaccine': {
            'Meta': {'object_name': 'Vaccine'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        }
    }
    
    complete_apps = ['static']
