#-*- coding:utf-8 -*-

import os, sys

#Standard boilerplate code that we put to put the settings file in the
#python path and make the Django environment have access to it.
PWD = os.path.dirname(__file__)
PARENT_DIR = os.path.realpath(os.path.join(PWD, '..'))
if PARENT_DIR not in sys.path: sys.path.append(PARENT_DIR)


import settings
from django.db import models

from esp.models import Demog, Immunization, Enc, icd9, Lx


ADVERSE_EVENT_CATEGORIES = [
    ('auto', 'Report automatically'),
    ('default', 'Message CDC if no comment from clinician within 72 hours'),
    ('confirm', 'Message clinician to confirm or decline'),
    ('discard', 'Discard')
]



class Rule(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=60,
                                choices=ADVERSE_EVENT_CATEGORIES)
    
    
class FeverEventRule(Rule):
    trigger_value = models.FloatField()
    

class DiagnosticsEventRule(Rule):
    icd9_codes = models.ManyToManyField(icd9)
    
class LxEventRule(Rule):
    lab_result = models.ForeignKey(Lx)


class AdverseEvent(models.Model):
    patient = models.ForeignKey(Demog)
    immunization = models.ForeignKey(Immunization)
    matching_rule_explain = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=ADVERSE_EVENT_CATEGORIES)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class FeverEvent(AdverseEvent):
    temperature = models.FloatField('Temperature')
    encounter = models.ForeignKey(Enc)

class DiagnosticsEvent(AdverseEvent):
    encounter = models.ForeignKey(Enc)
    icd9 = models.ForeignKey(icd9)
    

class LabResultEvent(AdverseEvent):
    lab_result = models.ForeignKey(Lx)
