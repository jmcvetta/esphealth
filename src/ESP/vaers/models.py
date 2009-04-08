#-*- coding:utf-8 -*-

from django.db import models
from django.db.models import signals

from ESP.esp.models import Demog, Immunization, Enc, Lx, Provider
from ESP.esp.choices import WORKFLOW_STATES
from ESP.conf.models import Icd9


def adverse_event_digest(**kw):
    import hashlib
    event = kw.get('instance')
    if not event.digest:
        clear_msg = '%s%s%s%s' % (event.id, event.patient, 
                                  event.immunization.id, event.category)
        event.digest = hashlib.sha224(clear_msg).hexdigest()
        event.save()
        
        


ADVERSE_EVENT_CATEGORIES = [
    ('auto', 'report automatically to CDC'),
    ('default', 'report case to CDC if no comment from clinician within 72 hours'),
    ('confirm', 'report to CDC only if confirmed by clinician'),
    ('discard', 'discard')
]

class AdverseEventManager(models.Manager):

    @staticmethod
    def _children():
        return [FeverEvent, DiagnosticsEvent, LabResultEvent]

    def by_id(self, key):
        for klass in AdverseEventManager._children():
            try:
                obj = klass.objects.get(id=key)
                return obj
            except: pass
        return None

    def by_digest(self, key):
        for klass in AdverseEventManager._children():
            try:
                obj = klass.objects.get(digest=key)
                return obj
            except: pass
        return None

    def all(self):
        return [self.by_id(ev.id) for ev in AdverseEvent.objects.all()]
            
    

class Rule(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=60,
                                choices=ADVERSE_EVENT_CATEGORIES)
    
    
class FeverEventRule(Rule):
    trigger_value = models.FloatField()
    

class DiagnosticsEventRule(Rule):
    icd9_codes = models.ManyToManyField(Icd9)
    
class LxEventRule(Rule):
    lab_result = models.ForeignKey(Lx)

class AdverseEvent(models.Model):
    objects = models.Manager()
    manager = AdverseEventManager()
    patient = models.ForeignKey(Demog)
    immunization = models.ForeignKey(Immunization)
    matching_rule_explain = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=ADVERSE_EVENT_CATEGORIES)
    digest = models.CharField(max_length=200, null=True)
    state = models.SlugField(max_length=2, choices=WORKFLOW_STATES, default='AR')
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class FeverEvent(AdverseEvent):
    temperature = models.FloatField('Temperature')
    encounter = models.ForeignKey(Enc)

class DiagnosticsEvent(AdverseEvent):
    encounter = models.ForeignKey(Enc)
    icd9 = models.ForeignKey(Icd9)
    

class LabResultEvent(AdverseEvent):
    lab_result = models.ForeignKey(Lx)


class ProviderComment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Provider)
    event = models.ForeignKey(AdverseEvent)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)



signals.post_save.connect(adverse_event_digest, sender=DiagnosticsEvent)
signals.post_save.connect(adverse_event_digest, sender=FeverEvent)
signals.post_save.connect(adverse_event_digest, sender=LabResultEvent)
