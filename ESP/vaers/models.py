import os, sys
sys.path.append(os.path.join(os.path.realpath(__file__), '../'))

import settings
sys.path.append(settings.TOPDIR)

from esp.models import Demog, Immunization, Enc, icd9


from django.db import models


class AdverseEvent(models.Model):
    patient = models.ForeignKey(Demog)
    immunization = models.ForeignKey(Immunization)
    encounter = models.ForeignKey(Encounter)
    icd9_code = models.ForeignKey(icd9)
    description = models.CharField(max_length=200)
    last_updated = models.DateTimeField(auto_now = True)
    

    
    
    
      
