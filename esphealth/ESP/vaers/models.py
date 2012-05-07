#-*- coding:utf-8 -*-
import datetime
import random
import os
import pickle
import time
import hashlib

from django.db import models
from django.db.models import signals, Q
from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ESP.emr.choices import WORKFLOW_STATES # FIXME: 'esp' module is deprecated
from ESP.emr.models import Patient, Immunization,Prescription,Allergy,  Encounter, LabResult, Provider
from ESP.static.models import Icd9
from ESP.conf.common import DEIDENTIFICATION_TIMEDELTA, EPOCH
from ESP.utils.utils import log, make_date_folders
from ESP.settings import DATA_DIR

from rules import TEMP_TO_REPORT, TIME_WINDOW_POST_EVENT
from utils import make_clustering_event_report_file
import settings


CLUSTERING_REPORTS_DIR = os.path.join(DATA_DIR, 'vaers', 'clustering_reports')
HL7_MESSAGES_DIR = os.path.join(DATA_DIR, 'vaers', 'hl7_messages')

#types of action types 
# 1_common: (auto) Common, well described, non-serious, adverse event
# 2_rare: (default) Rare, severe adverse event on VSD list
# 3_possible: (confirm) Possible novel adverse event not previously associated with vaccine
# 4_unlikely: (discard) Routine health visit highly unlikely to be adverse event

#TODO use this later for header in report for suggested action
ADVERSE_EVENT_CATEGORY_ACTION = [
     ('1_common', 'Automatically confirmed, common AE well described, non-serious, adverse event'),
     ('2_rare','Automatically confirmed, rare, severe adverse event associated with vaccine.'),
     ('3_possible', 'Confirm, Possible novel adverse event not previously associated with vaccine'),
     ('4_unlikely', 'Discard, Routine health visit highly unlikely to be adverse event')
    ]

ADVERSE_EVENT_CATEGORIES = [
    ('1_common', '1_common'),
    ('2_rare', '2_rare'),
    ('3_possible', '3_possible'),
    ('4_unlikely', '4_unlikely')
]


class AdverseEventManager(models.Manager):
    def cases_to_report(self):
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        # TODO use the state instead of this
        auto = Q(category='1_common')
        confirmed = Q(category='3_possible', state='Q')
        to_report_by_default = Q(category='2_rare', state='AR', created_on__lte=week_ago)

        return self.filter(auto | confirmed | to_report_by_default)


class EncounterEventManager(models.Manager):
    #TODO change this to check if it is fever some other way, use a boolean flag in encounter event
    def fevers(self):
        return self.filter(matching_rule_explain__startswith='Patient had')
    
    def icd9_events(self):
        return self.exclude(matching_rule_explain__startswith='Patient had')
    
class AdverseEvent(models.Model):

    objects = AdverseEventManager()
    # Model Fields
    patient = models.ForeignKey(Patient)
    immunizations = models.ManyToManyField(Immunization)
    name = models.CharField(max_length=100)
    date = models.DateField()
    gap = models.IntegerField(null=True)
    matching_rule_explain = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=ADVERSE_EVENT_CATEGORIES)
    digest = models.CharField(max_length=200, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Generic foreign key - any kind of EMR record can be tagged
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'events')
    VAERS_FEVER_TEMPERATURE = TEMP_TO_REPORT
    last_known_value = models.FloatField('Last known Numeric Test Result', blank=True, null=True)
    last_known_date  = models.DateField(blank=True, null=True)
    
    @staticmethod
    def fakes():
        return AdverseEvent.objects.filter(AdverseEvent.fake_q)

    @staticmethod
    def delete_fakes():
        AdverseEvent.fakes().delete()

    @staticmethod    
    def by_id(id):
        try:
            klass = AdverseEvent.objects.get(id=id).content_type
            return klass.model_class().objects.get(id=id)
        except:
            return None

    @staticmethod    
    def by_digest(key):
        try:
            klass = AdverseEvent.objects.get(digest=key).content_type
            return klass.model_class().objects.get(digest=key)
        except:
            return None

    @staticmethod
    def paginated(page=1, results_per_page=100):
        # Set limits for query
        floor = max(page-1, 0)*results_per_page
        ceiling = floor+results_per_page

        #We are only getting the fake ones. There is no possible case
        #in our application where we need paginated results for real
        #cases.
        return AdverseEvent.fakes()[floor:ceiling]

    @staticmethod
    def make_deidentified_fixtures():
        for ev in AdverseEvent.objects.all():
            event = AdverseEvent.by_id(ev.id)
            event.make_deidentified_fixture()


    @staticmethod
    def build_from_fixture():
        import simplejson
        event_dir = AdverseEvent.FIXTURE_DIR

        for f in [os.path.join(event_dir, f) for f in os.listdir(event_dir) 
                  if os.path.basename(f).startswith('vaers')]:
            fixture_file = open(f, 'rb')
            data = simplejson.loads(fixture_file.read().strip())
            event_data, patient_data = data['event'], data['patient']
            immunizations = data['immunizations']
            encounter = data.get('encounter')
            lab_result = data.get('lab_result')

            if not (encounter or lab_result): 
                raise ValueError, 'Not an Encounter Event nor LabResultEvent'
            
            
            patient = Patient(
                natural_key=patient_data['identifier'],
                first_name=patient_data['first_name'],
                last_name=patient_data['last_name'],
                date_of_birth=patient_data['date_of_birth']
                )
                
            patient.save()

            if encounter: 
                raw_encounter_type = ContentType.objects.get_for_model(EncounterEvent)
                event = EncounterEvent(content_type=raw_encounter_type)
                event_encounter = Encounter(
                    patient=patient, date = encounter['date'],
                    temperature = encounter['temperature'])
                event_encounter.save()
                event.encounter = event_encounter

                for code in encounter['icd9_codes']:
                    icd9_code = Icd9.objects.get(code=code['code'])
                    event.encounter.icd9_codes.add(icd9_code)
                
            if lab_result: 
                lx_type = ContentType.objects.get_for_model(LabResultEvent)
                event = LabResultEvent(content_type=lx_type)
                event_lx = LabResult(patient=patient, date=lab_result['date'],
                                     result_float=lab_result['result_float'],
                                     result_string=lab_result['result_string'],
                                     ref_unit=lab_result['unit'])
                event_lx.loinc = lab_result['loinc']
                event_lx.save()
                event.lab_result = event_lx

            event.date = event_data['date']
            event.category = event_data['category']
            event.matching_rule_explain = event_data['matching_rule_explain']
            event.save()
            

            for immunization in [Immunization.objects.create(
                    patient=patient, date=imm['date']) for imm in immunizations]:
                event.immunizations.add(immunization)

            fixture_file.close()

        
                
    @staticmethod
    def send_notifications():
        now = datetime.datetime.now()
        three_days_ago = now - datetime.timedelta(days=3)

        # Category 3 (cases that need clinicians confirmation for report)
        must_confirm = Q(category='3_possible') 

        # Category 2 (cases that are reported by default, i.e, no comment
        # from the clinician after 72 hours since the detection.
        may_receive_comments = Q(category='2_rare', created_on__gte=three_days_ago)
        # TODO work based on cases not events .. 
        cases_to_notify = AdverseEvent.objects.filter(must_confirm|may_receive_comments)

        for case in cases_to_notify:
            try:
                case.mail_notification()
            except Exception, why:
                print 'Failed to send in case %s.\nReason: %s' % (case.id, why)
                
    def make_deidentified_fixture(self):
        outfile = open(os.path.join(AdverseEvent.FIXTURE_DIR, 'vaers_event.%s.json' % self.id), 'w')
        outfile.write(self.render_json_fixture())
        outfile.close()

    fake_q = Q(immunizations__name='FAKE')

    def temporal_report(self):
        results = []
        for imm in self.immunizations.all():
            patient = imm.patient
            results.append({
                    'id':imm.natural_key,
                    'vaccine_date': imm.date, 
                    'event_date':self.date,
                    'days_to_event':(self.date - imm.date).days,
                    'immunization_name':imm.name, 
                    'event_description':self.matching_rule_explain,
                    'patient_age':patient._get_age_str(),
                    'patient_gender':patient.gender
                    })

        return results
    
    def render_temporal_report(self):
        buf = []
        for result in self.temporal_report():
            buf.append(
                '\t'.join([str(x) for x in [
                            result['id'], result['vaccine_date'], 
                            result['event_date'], result['days_to_event'],
                            result['immunization_name'], 
                            result['event_description'],  
                            result['patient_age'], result['patient_gender']
                            ]]))

        return '\n'.join(buf)

    def is_fake(self):
        return self.patient.is_fake()

    def provider(self):
        return self.patient.pcp

    def verification_url(self):
        return reverse('verify_case', kwargs={'key':self.digest})

    def mail_notification(self, email_address=None):
        from django.contrib.sites.models import Site
        from ESP.settings import ADMINS, DEBUG

        current_site = Site.objects.get_current()

        recipient = email_address or settings.EMAIL_RECIPIENT

        if DEBUG:
            admins_address = [x[1] for x in ADMINS]
            who_to_send = admins_address + [recipient]
        else:
            who_to_send = [recipient]

        params = {
            'case': self,
            'provider': self.provider(),
            'patient': self.patient,
            'url':'http://%s%s' % (current_site, self.verification_url()),
            'misdirected_email_contact':settings.EMAIL_SENDER
            }

        templates = {
            '2_rare':'email_messages/notify_category_two',
            '3_possible':'email_messages/notify_category_three'
            }
        
        html_template = templates[self.category] + '.html'
        #text_template = templates[self.category] + '.txt'
        
        html_msg = get_template(html_template).render(Context(params))
        #text_msg = get_template(text_template).render(Context(params))       
        
        msg = EmailMessage(settings.EMAIL_SUBJECT, html_msg, settings.EMAIL_SENDER, who_to_send)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        
    def _deidentify_patient(self, days_to_shift):
        # From patient personal data, we can get rid of
        # everything, except for date of birth. Vaers Reports are
        # dependant on the patient's age.
        
        fake_patient = Patient.make_mock(save_on_db=False)
        new_dob = self.patient.date_of_birth - datetime.timedelta(days=days_to_shift)
        fake_patient.date_of_birth = new_dob
        return fake_patient

        
        
    def _deidentified_immunizations(self, patient, days_to_shift):
        assert days_to_shift > 0
        assert patient.is_fake()

        deidentified = []
        for imm in self.immunizations.all():
            new_date = imm.date - datetime.timedelta(days=days_to_shift)
            fake_imm = Immunization.make_mock(imm.vaccine, patient, new_date)
            deidentified.append(fake_imm)

        return deidentified


    def deidentified(self):
        '''
        Returns an event that is derived from "real" data, but
        containing no identifiable information about patients. 
        '''
        # A patient's date of birth is crucial in identification, but
        # is necessary for VAERS reports (age). To keep information
        # accurate, we shift the patient date of birth by a random
        # delta (DEIDENTIFICATION_TIMEDELTA), and do the same to all
        # date-related information in the event.
        

        days_to_shift = random.randrange(1, DEIDENTIFICATION_TIMEDELTA)
        deidentified_patient = self._deidentify_patient(days_to_shift)
        

        my_content_type = ContentType.objects.get_for_model(self.__class__)
        date = self.date - datetime.timedelta(days=days_to_shift)
        immunizations = self._deidentified_immunizations(
            deidentified_patient, days_to_shift)
        
        data = {
            'event':{
                'type': str(my_content_type),
                'category': self.category,
                'date': str(date),
                'matching_rule_explain':self.matching_rule_explain
                },
            'patient':{
                'first_name': deidentified_patient.first_name,
                'last_name': deidentified_patient.last_name,
                'date_of_birth':str(deidentified_patient.date_of_birth),
                'identifier':deidentified_patient.natural_key
                },
            'provider':{
                'first_name':deidentified_patient.pcp.first_name,
                'last_name':deidentified_patient.pcp.last_name,
                'identifier':deidentified_patient.pcp.natural_key
                },
            'immunizations': [{
                    'date':str(i.date)
                    } for i in immunizations]
            }

        return self.complete_deidentification(data, 
                                              days_to_shift=days_to_shift)


    def render_json_fixture(self):
        import simplejson
        return simplejson.dumps(self.deidentified())

    def render_hl7_message(self):
        from hl7_report import AdverseReactionReport
        return AdverseReactionReport(self).render()

    def save_hl7_message_file(self, folder=None):
        #TODO maybe gen the notification message here.
        folder = folder or HL7_MESSAGES_DIR
        outfile = open(os.path.join(folder, 'report.%07d.hl7' % self.id), 'w')
        outfile.write(self.render_hl7_message())
        outfile.close()
        
    class Meta:
        permissions = [ ('view_phi', 'Can view protected health information'), ]
        ordering = ['id']
        # from hef unique_together = [('content_type', 'object_id')]
    
# TODO clean up by moving all methods to adverse event and rename the ones that share the name
# later consolidate them 
            
class EncounterEvent(AdverseEvent):
    objects = EncounterEventManager()
    
    @staticmethod
    def write_fever_clustering_report(**kw):
        begin_date = kw.pop('begin_date', None) or EPOCH
        end_date = kw.pop('end_date', None) or datetime.datetime.today()

        root_folder = kw.pop('folder', CLUSTERING_REPORTS_DIR)
        folder = make_date_folders(begin_date, end_date, root=root_folder)
        gap = kw.pop('max_interval', TIME_WINDOW_POST_EVENT)

        fever_events = EncounterEvent.objects.fevers().filter(date__gte=begin_date, date__lte=end_date, 
                                                              gap__lte=7)

        within_interval = [e for e in fever_events 
                           if (e.date - max([i.date for i in e.immunizations.all()])).days <= gap]

        log.info('Writing report for %d fever events between %s and %s' % (
                len(within_interval), begin_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        make_clustering_event_report_file(os.path.join(folder, 'fever_events.txt'), within_interval)

    @staticmethod
    def write_diagnostics_clustering_report(**kw):
        begin_date = kw.pop('begin_date', None) or EPOCH
        end_date = kw.pop('end_date', None) or datetime.datetime.today()

        root_folder = kw.pop('folder', CLUSTERING_REPORTS_DIR)
        folder = make_date_folders(begin_date, end_date, root=root_folder)
        gap = kw.pop('max_interval', TIME_WINDOW_POST_EVENT)

        icd9_events = EncounterEvent.objects.icd9_events().filter(date__gte=begin_date, 
                                                                  date__lte=end_date, gap__lte=30)

        within_interval = [e for e in icd9_events 
                           if (e.date - max([i.date for i in e.immunizations.all()])).days <= gap]

        log.info('Writing report for %d icd9 events between %s and %s' % (
                len(within_interval), begin_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))


        make_clustering_event_report_file(os.path.join(folder, 'icd9_events.txt'), within_interval)

    def _deidentified_encounter(self, days_to_shift):
        codes = [{'code':x.code} for x in self.content_object.icd9_codes.all()]
        date = self.content_object.date - datetime.timedelta(days=days_to_shift)
        return {
            'date':str(date),
            'temperature':self.content_object.temperature,
            'icd9_codes':codes
            }
    
    def complete_deidentification(self, data, **kw):
        days_to_shift = kw.pop('days_to_shift', None)
        if not days_to_shift: 
            raise ValueError, 'Must indicate days_to_shift'
        
        data['encounter'] = self._deidentified_encounter(days_to_shift)

        return data


    def __unicode__(self):
        
        return u"Encounter Event %s: Patient %s, %s on %s" % (
            self.id, self.content_object.patient.full_name, 
            self.matching_rule_explain, self.date)

class PrescriptionEvent(AdverseEvent):
    
    @staticmethod
    def write_clustering_report(**kw):
        begin_date = kw.pop('begin_date', None) or EPOCH
        end_date = kw.pop('end_date', None) or datetime.datetime.today()
        
        root_folder = kw.pop('folder', CLUSTERING_REPORTS_DIR)
        folder = make_date_folders(begin_date, end_date, root=root_folder)
        gap = kw.pop('max_interval', TIME_WINDOW_POST_EVENT)

        rx_events = PrescriptionEvent.objects.filter(date__gte=begin_date, date__lte=end_date)
        within_interval = [e for e in rx_events 
                           if (e.date - max([i.date for i in e.immunizations.all()])).days <= gap]

        log.info('Writing report for %d Prescription events between %s and %s' % (
                len(within_interval), begin_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        make_clustering_event_report_file(os.path.join(folder, 'rx_events.txt'), within_interval)

    def _deidentified_rx(self, days_to_shift):
        date = self.content_object.date - datetime.timedelta(days=days_to_shift)
        return {
            'med':self.content_object.name,
            'date':str(date),
            'dose':self.content_object.dose,
            'quantity':self.content_object.quantity
            }

    def complete_deidentification(self, data, **kw):
        days_to_shift = kw.pop('days_to_shift', None)
        if not days_to_shift: 
            raise ValueError, 'Must indicate days_to_shift'
        
        data['prescription'] = self._deidentified_rx(days_to_shift)
        return data
    
    def __unicode__(self):
        return u'Prescription Event %s: Patient %s, %s on %s' % (
            self.id, self.content_object.patient.full_name, 
            self.matching_rule_explain, self.date)

class AllergyEvent(AdverseEvent):
    
    @staticmethod
    def write_clustering_report(**kw):
        begin_date = kw.pop('begin_date', None) or EPOCH
        end_date = kw.pop('end_date', None) or datetime.datetime.today()
        
        root_folder = kw.pop('folder', CLUSTERING_REPORTS_DIR)
        folder = make_date_folders(begin_date, end_date, root=root_folder)
        gap = kw.pop('max_interval', TIME_WINDOW_POST_EVENT)

        allergy_events = AllergyEvent.objects.filter(date__gte=begin_date, date__lte=end_date)
        within_interval = [e for e in allergy_events 
                           if (e.date - max([i.date for i in e.immunizations.all()])).days <= gap]

        log.info('Writing report for %d Allergy events between %s and %s' % (
                len(within_interval), begin_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        make_clustering_event_report_file(os.path.join(folder, 'allergy_events.txt'), within_interval)

    def _deidentified_allergy(self, days_to_shift):
        date = self.content_object.date - datetime.timedelta(days=days_to_shift)
        return {
            'med':self.content_object.name,
            'date':str(date)
            }

    def complete_deidentification(self, data, **kw):
        days_to_shift = kw.pop('days_to_shift', None)
        if not days_to_shift: 
            raise ValueError, 'Must indicate days_to_shift'
        
        data['allergy'] = self._deidentified_allergy(days_to_shift)
        return data
    
    def __unicode__(self):
        return u'Allergy Event %s: Patient %s, %s on %s' % (
            self.id, self.content_object.patient.full_name, 
            self.matching_rule_explain, self.date)
               
class LabResultEvent(AdverseEvent):

    @staticmethod
    def write_clustering_report(**kw):
        begin_date = kw.pop('begin_date', None) or EPOCH
        end_date = kw.pop('end_date', None) or datetime.datetime.today()
        
        root_folder = kw.pop('folder', CLUSTERING_REPORTS_DIR)
        folder = make_date_folders(begin_date, end_date, root=root_folder)
        gap = kw.pop('max_interval', TIME_WINDOW_POST_EVENT)

        lx_events = LabResultEvent.objects.filter(date__gte=begin_date, date__lte=end_date)
        within_interval = [e for e in lx_events 
                           if (e.date - max([i.date for i in e.immunizations.all()])).days <= gap]

        log.info('Writing report for %d Lab Result events between %s and %s' % (
                len(within_interval), begin_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        make_clustering_event_report_file(os.path.join(folder, 'lx_events.txt'), within_interval)

    def _deidentified_lx(self, days_to_shift):
        date = self.content_object.date - datetime.timedelta(days=days_to_shift)
        return {
            'loinc':self.content_object.loinc.loinc_num,
            'date':str(date),
            'result_float':self.content_object.result_float,
            'result_string':self.content_object.result_string,
            'unit': self.content_object.ref_unit
            }

    def complete_deidentification(self, data, **kw):
        days_to_shift = kw.pop('days_to_shift', None)
        if not days_to_shift: 
            raise ValueError, 'Must indicate days_to_shift'
        
        data['lab_result'] = self._deidentified_lx(days_to_shift)
        return data
    
    def __unicode__(self):
        if self.content_object:
            return u'LabResult Event %s: Patient %s, %s on %s' % (
                self.id, self.content_object.patient.full_name, 
                self.matching_rule_explain, self.date)
        else:
            return u'LabResult Event %s:  %s on %s' % (
                self.id, self.matching_rule_explain, self.date)

class Sender(models.Model):
    provider= models.ForeignKey(Provider, verbose_name='Physician', blank=True, null=True) 

    def _get_name(self):
        return u'%s, %s ' % (self.provider.last_name,  self.provider.first_name)
    name = property(_get_name)
    
    def __unicode__(self):
        return u'%s %s' % (self.provider_id, self.name)

class Case (models.Model):  
    
    date = models.DateTimeField(auto_now=True, db_index=True)  
    adverse_event = models.ManyToManyField(AdverseEvent, db_index=True)
    immunizations = models.ManyToManyField(Immunization,related_name='all_immunizations', db_index=True)
    patient = models.ForeignKey(Patient,related_name='vaers_cases', blank=False, db_index=True)
    prior_immunizations = models.ManyToManyField(Immunization,related_name='prior_immunizations', )
    last_update = models.DateTimeField(auto_now=True, db_index=True)  
    
    @staticmethod    
    def immunization_by_id(id):
        try:
            klass = ContentType.objects.get_for_model(Immunization)
            return klass.model_class().objects.get(id=id)
        except:
            return None
        
    def __unicode__(self):
        return u'AE Case %s: Patient %s, on %s' % (
            self.id, self.patient.full_name, self.date)

class Questionaire (models.Model):
    comment = models.TextField()
    provider = models.ForeignKey(Provider)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    message_ishelpful = models.NullBooleanField()
    interrupts_work = models.NullBooleanField()
    satisfaction_num_msg = models.CharField(max_length=10, db_index=True)
    case = models.ForeignKey(Case)
    # HL7 ‘transcription interface’ email for logging/debugging
    inbox_message = models.TextField()
    digest = models.CharField(max_length=200, null=True)
    state = models.SlugField(max_length=2, choices=WORKFLOW_STATES, default='AR')
    
    def create_digest(self):
        
        if self.digest:
            return
        clear_msg = '%s%s%s' % (self.id, self.case.date, int(time.time()))
        self.digest = hashlib.sha224(clear_msg).hexdigest()
        self.save()
 
class Report_Sent (models.Model):
    date = models.DateTimeField(auto_now_add=True)
    case = models.ForeignKey(Case)
    #raw hl7 vaers report as sent
    vaers_report = models.TextField()


class ExcludedICD9Code(models.Model):
    '''
    Codes to be excluded by vaers diagnosis heuristics
    '''
    code = models.CharField(max_length=20, blank=False, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=False )
    
    def __str__(self):  
        return self.code
    
    class Meta:
        verbose_name = 'Excluded icd9 code'


class Rule(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=60, choices=ADVERSE_EVENT_CATEGORIES)
    in_use = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
    
    def activate(self):
        if not self.in_use:
            self.in_use = True
            self.save()

    def deactivate(self):
        if self.in_use:
            self.in_use = False
            self.save()
    
    @classmethod
    def deactivate_all(cls):
        cls.objects.all().update(in_use=False)
        
                
class DiagnosticsEventRule(Rule):

    source = models.CharField(max_length=30, null=True)
    ignore_period = models.PositiveIntegerField(null=True)
    heuristic_defining_codes = models.ManyToManyField(Icd9, related_name='defining_icd9_code_set')
    heuristic_discarding_codes = models.ManyToManyField(Icd9, related_name='discarding_icd9_code_set')
    risk_period = models.IntegerField(blank=False, null=False, 
        help_text='Risk period in days following vaccination')
    
    @staticmethod
    def all_active():
        return DiagnosticsEventRule.objects.filter(in_use=True)
    
    @staticmethod
    def by_name(name, only_if_active=True):
        q = DiagnosticsEventRule.objects.filter(name=name)
        if only_if_active: q = q.filter(in_use=True)
        return q

    @staticmethod
    def random():
        return DiagnosticsEventRule.objects.order_by('?')[0]
 
    def __unicode__(self):
        return unicode(self.name)
