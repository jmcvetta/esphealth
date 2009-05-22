#-*- coding:utf-8 -*-

from django.db import models
from django.db.models import signals, Q
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ESP.esp.models import Demog, Immunization, Enc, Lx, Provider
from ESP.esp.choices import WORKFLOW_STATES
from ESP.conf.models import Icd9, Loinc

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

    

    fake_q = Q(immunizations__ImmName='FAKE')

    def is_fake(self):
        should_be_fake = any(
            [imm.is_fake() for imm in self.immunizations.all()])
        really_fake = all(
            [imm.is_fake() for imm in self.immunizations.all()])

        if should_be_fake and not really_fake:
            raise ValueError, 'Not all immunizations in this encounter are fake. Why?'

        return really_fake

    def patient(self):
        return self.immunizations.all()[0].ImmPatient

    def provider(self):
        return self.patient().DemogProvider

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
        
        t = get_template('email_messages/notify_case.txt')
        msg = t.render(Context(params))
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
    encounter = models.ForeignKey(Enc)


class LabResultEvent(AdverseEvent):
    lab_result = models.ForeignKey(Lx)




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
    category = models.CharField(max_length=60,
                                choices=ADVERSE_EVENT_CATEGORIES)
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
