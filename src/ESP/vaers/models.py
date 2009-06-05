#-*- coding:utf-8 -*-
import datetime

from django.db import models
from django.db.models import signals, Q
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ESP.emr.models import Patient, Immunization, Encounter, LabResult, Provider
from ESP.esp.choices import WORKFLOW_STATES
from ESP.conf.models import Icd9, Loinc


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
        should_be_fake = any(
            [imm.is_fake() for imm in self.immunizations.all()])
        really_fake = all(
            [imm.is_fake() for imm in self.immunizations.all()])

        if should_be_fake and not really_fake:
            raise ValueError, 'Not all immunizations in this encounter are fake. Why?'

        return really_fake

    def patient(self):
        return self.immunizations.all()[0].patient

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
            'default':'email_messages/notify_case.txt',
            'confirm':'email_messages/notify_category_three.txt'
            }

        
        msg = get_template(templates[self.category]).render(Context(params))


        # In case it is a fake event, the notification should include
        # a warning.  That message is in the template notify_demo.txt
        # and is prepended to the real message.
        if self.is_fake(): 
            demo_warning_msg = get_template('email_messages/notify_demo.txt').render({}) 
            msg = demo_warning_msg + msg
            
        send_mail(settings.EMAIL_SUBJECT, msg,
                  settings.EMAIL_SENDER, 
                  [recipient],
                  fail_silently=False)


            

    @staticmethod
    def fakes():
        return AdverseEvent.objects.filter(AdverseEvent.fake_q)

    @staticmethod
    def delete_fakes():
        AdverseEvent.fakes().delete()

    

    
class EncounterEvent(AdverseEvent):
    encounter = models.ForeignKey(Encounter)

    @staticmethod
    def write_fever_clustering_file_report():
        fever_events = EncounterEvent.objects.filter(
            matching_rule_explain__startswith='Patient had')

        make_clustering_event_report_file(
            'clustering_fever_events.txt', fever_events)

    @staticmethod
    def write_diagnostics_clustering_file_report():
        diagnostics_events = EncounterEvent.objects.exclude(
            matching_rule_explain__startswith='Patient had')

        make_clustering_event_report_file(
            'clustering_diagnostics_events.txt', diagnostics_events)


        

            

    def __unicode__(self):
        return u"Encounter Event %s: Patient %s, %s on %s" % (
            self.id, self.encounter.patient.full_name(), 
            self.matching_rule_explain, self.date)


class LabResultEvent(AdverseEvent):
    lab_result = models.ForeignKey(LabResult)

    @staticmethod
    def write_clustering_file_report():
        make_clustering_event_report_file(
            'clustering_lx_events.txt', LabResultEvent.objects.all())
    
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
