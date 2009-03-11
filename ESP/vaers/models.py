#-*- coding:utf-8 -*-

import os, sys
sys.path.append(os.path.realpath('..'))

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
    encounter = models.ForeignKey(Enc)
    matching_rule_explain = models.CharField(max_length=200)
    last_updated = models.DateTimeField(auto_now = True)


    

    
    
    
      
