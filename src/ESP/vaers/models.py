#-*- coding:utf-8 -*-

from django.db import models
from django.db.models import signals, Q
from django.contrib.contenttypes.models import ContentType


from ESP.esp.models import Demog, Immunization, Enc, Lx, Provider
from ESP.esp.choices import WORKFLOW_STATES
from ESP.conf.models import Icd9


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
        clear_msg = '%s%s%s%s' % (event.id, event.patient, 
                                  event.immunization.id, event.category)
        event.digest = hashlib.sha224(clear_msg).hexdigest()
        event.save()



class AdverseEventManager(models.Manager):

    def by_id(self, key):
        try:
            return self.get(id=key)
        except:
            return None
        
    def by_digest(self, key):
        try:
            return self.get(digest=key)
        except:
            return None

class AdverseEvent(models.Model):
    content_type = models.ForeignKey(ContentType, editable=False, null=True)
    immunization = models.ForeignKey(Immunization)
    matching_rule_explain = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=ADVERSE_EVENT_CATEGORIES)
    digest = models.CharField(max_length=200, null=True)
    state = models.SlugField(max_length=2, choices=WORKFLOW_STATES, default='AR')

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    fake_q = Q(immunization__ImmPatient__DemogFirst_Name__startswith='FAKE')

    @classmethod
    def fakes(cls):
        return cls.objects.filter(AdverseEvent.fake_q)

    @classmethod
    def delete_fakes(cls):
        cls.objects.filter(AdverseEvent.fake_q).delete()


    def save(self):
        if(not self.content_type):
            klass = self.__class__
            self.content_type = ContentType.objects.get_for_model(klass)
        self.save_base()



class FeverEvent(AdverseEvent):
    temperature = models.FloatField('Temperature')
    encounter = models.ForeignKey(Enc)

    explain_string = 'Patient with %3.1fF fever'

    @staticmethod
    def make_fake(immunization, encounter):

        assert encounter.is_fake()
        assert immunization.is_fake()
        assert immunization.ImmPatient.is_fake()

        temp = randomizer.fever_temperature() 
        
        return FeverEvent.objects.create(
            immunization=immunization,
            temperature=temp, 
            matching_rule_explain = FeverEvent.explain_string % temp
            )
            

class DiagnosticsEvent(AdverseEvent):
    encounter = models.ForeignKey(Enc)
    icd9 = models.ForeignKey(Icd9)   

    explain_string = 'Patient diagnosed with %s'

    @staticmethod
    def make_fake(immunization, encounter, icd9):

        assert encounter.is_fake()
        assert immunization.is_fake()
        assert immunization.ImmPatient.is_fake()
        
        explain_rule = DiagnosticsEvent.explain_string % icd9.name

        return DiagnosticsEvent.objects.create(
            immunization=immunization, matching_rule_explain = explain_rule,
            encounter=encounter, icd9=icd9
            )



class LabResultEvent(AdverseEvent):
    lab_result = models.ForeignKey(Lx)


ADVERSE_EVENT_CLASSES = {
    'fever':FeverEvent,
    'diagnostics':DiagnosticsEvent,
    'lab_result': LabResultEvent
    }





class ProviderComment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Provider)
    event = models.ForeignKey(AdverseEvent)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)



signals.post_save.connect(adverse_event_digest, sender=DiagnosticsEvent)
signals.post_save.connect(adverse_event_digest, sender=FeverEvent)
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
    



class DiagnosticsEventManager(models.Manager):
    def deactivate_all(self):
        self.all().update(in_use=False)
        
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
 
    objects = DiagnosticsEventManager()
    source = models.CharField(max_length=30, null=True)
    ignored_if_past_occurrence = models.PositiveIntegerField(null=True)
    heuristic_defining_codes = models.ManyToManyField(
        Icd9, related_name='defining_icd9_code_set')
    heuristic_discarding_codes = models.ManyToManyField(
        Icd9, related_name='discarding_icd9_code_set')

    
    

class LxEventRule(Rule):
    lab_result = models.ForeignKey(Lx)

