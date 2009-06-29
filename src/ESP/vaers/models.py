#-*- coding:utf-8 -*-
import datetime
import random
import os
import pickle

from django.db import models
from django.db.models import signals, Q
from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ESP.emr.models import Patient, Immunization, Encounter, LabResult, Provider
from ESP.esp.choices import WORKFLOW_STATES
from ESP.conf.models import Icd9, Loinc
from ESP.conf.common import DEIDENTIFICATION_TIMEDELTA

from utils import make_clustering_event_report_file
import settings

ADVERSE_EVENT_CATEGORIES = [
    ('auto', 'report automatically to CDC'),
    ('default', 'report case to CDC if no comment from clinician within 72 hours'),
    ('confirm', 'report to CDC only if confirmed by clinician'),
    ('discard', 'discard')
]

def adverse_event_digest(**kw):
    import hashlib
    event = kw.get('instance')

    if not event.digest:
        clear_msg = '%s%s%s%s' % (event.id, event.immunizations, 
                                  event.matching_rule_explain, 
                                  event.category)
        event.digest = hashlib.sha224(clear_msg).hexdigest()
        event.save()


class AdverseEventManager(models.Manager):
    def cases_to_report(self):
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        
        auto = Q(category='auto')
        confirmed = Q(category='confirm', state='Q')
        to_report_by_default = Q(category='default', state='AR', 
                                 created_on__lte=week_ago)

        return self.filter(auto | confirmed | to_report_by_default)


class AdverseEvent(models.Model):

    # Model Fields
    immunizations = models.ManyToManyField(Immunization)
    matching_rule_explain = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=ADVERSE_EVENT_CATEGORIES)
    digest = models.CharField(max_length=200, null=True)
    state = models.SlugField(max_length=2, choices=WORKFLOW_STATES, default='AR')
    date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # To provide polymorphic lookups. Take a look at:
    # http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    content_type = models.ForeignKey(ContentType)

    PICKLE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'pickle')
   
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
    def pickle_deidentified():
        for ev in AdverseEvent.objects.all():
            event = AdverseEvent.by_id(ev.id)
            deidentified_ev = event.deidentified()['event']
            deidentified_ev.to_pickle_fixture(ev.id)

    @staticmethod
    def unpickled():
        event_dir = AdverseEvent.PICKLE_DIR
        files = [os.path.join(event_dir, f) for f in os.listdir(event_dir)]

        events = []
        for f in files:
            event_file = open(f, 'rb')
            events.append(pickle.load(event_file))
            event_file.close()

        return events
                
        
        


    @staticmethod
    def send_notifications():
        now = datetime.datetime.now()
        three_days_ago = now - datetime.timedelta(days=3)

        # Category 3 (cases that need clinicians confirmation for report)
        must_confirm = Q(category='confirm') 

        # Category 2 (cases that are reported by default, i.e, no comment
        # from the clinician after 72 hours since the detection.
        may_receive_comments = Q(category='default', created_on__gte=three_days_ago)
        cases_to_notify = AdverseEvent.objects.filter(must_confirm|may_receive_comments)


        for case in cases_to_notify:
            try:
                case.mail_notification()
            except Exception, why:
                print 'Failed to send in case %s.\nReason: %s' % (case.id, why)
                
    def to_pickle_fixture(self, key):
        outfile = open(os.path.join(AdverseEvent.PICKLE_DIR, 'vaers_event.%s.py' % key), 'w')
        pickle.dump(self, outfile, protocol=pickle.HIGHEST_PROTOCOL)
        outfile.close()



    fake_q = Q(immunizations__name='FAKE')

    def temporal_report(self):
        results = []
        for imm in self.immunizations.all():
            patient = imm.patient
            results.append({
                    'id':imm.imm_id_num,
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
        return self.patient().is_fake()

    def provider(self):
        return self.patient().pcp

    def verification_url(self):
        return reverse('verify_case', kwargs={'key':self.digest})

    def mail_notification(self, email_address=None):
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()

        recipient = email_address or settings.EMAIL_RECIPIENT

        params = {
            'case': self,
            'provider': self.provider(),
            'patient': self.patient(),
            'url':'http://%s%s' % (current_site, self.verification_url()),
            'misdirected_email_contact':settings.EMAIL_SENDER
            }

        templates = {
            'default':'email_messages/notify_category_two',
            'confirm':'email_messages/notify_category_three'
            }
        
        html_template = templates[self.category] + '.html'
        text_template = templates[self.category] + '.txt'
        
        html_msg = get_template(html_template).render(Context(params))
        text_msg = get_template(text_template).render(Context(params))

        msg = EmailMessage(settings.EMAIL_SUBJECT, html_msg, 
                           settings.EMAIL_SENDER, 
                           [recipient])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        
    def _deidentify_patient(self, days_to_shift):
        # From patient personal data, we can get rid of
        # everything, except for date of birth. Vaers Reports are
        # dependant on the patient's age.
        
        fake_patient = Patient.make_mock(save_on_db=False)
        new_dob = self.patient().date_of_birth - datetime.timedelta(days=days_to_shift)
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

    

    
class EncounterEvent(AdverseEvent):
    encounter = models.ForeignKey(Encounter)

    @staticmethod
    def write_fever_clustering_file_report(folder):
        fever_events = EncounterEvent.objects.filter(
            matching_rule_explain__startswith='Patient had')

        make_clustering_event_report_file(
            os.path.join(folder, 'clustering_fever_events.txt'), fever_events)

    @staticmethod
    def write_diagnostics_clustering_file_report(folder):
        diagnostics_events = EncounterEvent.objects.exclude(
            matching_rule_explain__startswith='Patient had')

        make_clustering_event_report_file(
            os.path.join(folder, 'clustering_diagnostics_events.txt'), diagnostics_events)

    def _deidentified_encounter(self, patient, days_to_shift):
        fake_encounter = Encounter.make_mock(patient, save_on_db=False)
        fake_encounter.date = self.encounter.date - datetime.timedelta(days=days_to_shift)
        fake_encounter.temperature = self.encounter.temperature        
        fake_encounter.pk = self.encounter.pk
        return fake_encounter, self.encounter.icd9_codes.all()

    def patient(self):
        return self.encounter.patient


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

        fake_ev = EncounterEvent()
        fake_ev.category = self.category
        fake_ev.matching_rule_explain = self.matching_rule_explain
        fake_ev.content_type = ContentType.objects.get_for_model(EncounterEvent)
        fake_ev.encounter, icd9_codes = self._deidentified_encounter(
            deidentified_patient, days_to_shift)
        fake_ev.date = self.date - datetime.timedelta(days=days_to_shift)
        immunizations = self._deidentified_immunizations(deidentified_patient, 
                                                    days_to_shift)
        return {
            'event': fake_ev, 
            'immunizations':immunizations, 
            'encounter_codes':icd9_codes
            }
            

    def __unicode__(self):
        return u"Encounter Event %s: Patient %s, %s on %s" % (
            self.id, self.encounter.patient.full_name, 
            self.matching_rule_explain, self.date)


class LabResultEvent(AdverseEvent):
    lab_result = models.ForeignKey(LabResult)

    @staticmethod
    def write_clustering_file_report(folder):
        make_clustering_event_report_file(
            os.path.join(folder, 'clustering_lx_events.txt'), LabResultEvent.objects.all())

    def patient(self):
        return self.lab_result.patient


    def _deidentified_lx(self, patient, days_to_shift):
        fake_lx = LabResult.make_mock(save_on_db=False)
        fake_lx.date = self.lab_result.date - datetime.timedelta(days=days_to_shift)
        fake_lx.result_float = self.lab_result.result_float
        fake_lx.result_string = self.lab_result.result_string
        fake_lx.unit = self.lab_result.unit
        fake_lx.patient = patient
        return fake_lx

    def deidentified(self):
        '''
        Returns an event that is derived from "real" data, but
        containing no identifiable information about patients. 
        '''
        # A patient's date of birth is crucial in identification, but
        # is necessary for VAERS reports (age). To keep information
        # accurate, we shift the patient date of birth by a random
        # delta ( DEIDENTIFICATION_TIMEDELTA), and do the same to all
        # date-related information in the event.
        
        fake_ev = LabResultEvent()
        fake_ev.content_type = ContentType.objects.get_for_model(LabResultEvent)
        days_to_shift = random.randrange(1, DEIDENTIFICATION_TIMEDELTA)
        deidentified_patient = self._deidentify_patient(days_to_shift)

        fake_ev.lab_result = self._deidentified_lx(deidentified_patient, 
                                                   days_to_shift)
        immunizations = self._deidentified_immunizations(deidentified_patient, 
                                                         days_to_shift)
        
        return {
            'event':fake_ev,
            'immunzations':immunizations
            }


    
    def __unicode__(self):
        return u"LabResult Event %s: Patient %s, %s on %s" % (
            self.id, self.lab_result.patient.full_name(), 
            self.matching_rule_explain, self.date)




class ProviderComment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Provider)
    event = models.ForeignKey(AdverseEvent)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)



signals.post_save.connect(adverse_event_digest, sender=EncounterEvent)
signals.post_save.connect(adverse_event_digest, sender=LabResultEvent)



class Rule(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=60, choices=ADVERSE_EVENT_CATEGORIES)
    in_use = models.BooleanField(default=False)
    
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
 
    source = models.CharField(max_length=30, null=True)
    ignored_if_past_occurrence = models.PositiveIntegerField(null=True)
    heuristic_defining_codes = models.ManyToManyField(
        Icd9, related_name='defining_icd9_code_set')
    heuristic_discarding_codes = models.ManyToManyField(
        Icd9, related_name='discarding_icd9_code_set')
    
    def __unicode__(self):
        return unicode(self.name)


class LabResultEventRule(Rule):
    @staticmethod
    def all_active():
        return LabResultEventRule.objects.filter(in_use=True)
    
    @staticmethod
    def by_name(name, only_if_active=True):
        q = LabResultEventRule.objects.filter(name=name)
        if only_if_active: q = q.filter(in_use=True)
        return q

    @staticmethod
    def random():
        return LabResultEventRule.objects.order_by('?')[0]

    loinc = models.ForeignKey(Loinc)
