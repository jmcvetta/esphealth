'''
                                  ESP Health
                              Site Configuration
                                  Data Models


@author: Jason McVetta <jason.mcvetta@gmail.com>
@author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>
'''


from django.db import models

from ESP.conf.choices import EMR_SOFTWARE
from ESP.conf.choices import FORMAT_TYPES
from ESP.conf.choices import DEST_TYPES
from ESP.conf.choices import WORKFLOW_STATES

from ESP.static.models import Loinc
from ESP.static.models import Vaccine
from ESP.static.models import ImmunizationManufacturer



class NativeCode(models.Model):
    '''
    A mapping from a native code (for a lab result, etc) to a Loinc number
    '''
    # This table and utilities making use of it assume only one external 
    # code table per ESP installation.  More work will be required if your 
    # installation must comprehend multiple, potentially overlapping, external 
    # code sources
    native_code = models.CharField(max_length=100, blank=False)
    native_name = models.CharField(max_length=255, blank=True, null=True)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc = models.ForeignKey(Loinc, blank=False)
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Native Code to LOINC Map'
        unique_together = ['native_code', 'loinc']
    
    def __str__(self):
        return '%s --> %s' % (self.native_code, self.loinc.loinc_num)


class IgnoredCode(models.Model):
    '''
    Codes to be ignored by nodis.core.Condition.find_unmapped_tests()
    '''
    native_code = models.CharField(max_length=100, blank=False, unique=True)



class NativeVaccine(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    canonical_code = models.ForeignKey(Vaccine, null=True)

    def __unicode__(self):
        return u'%s' % self.name


class NativeManufacturer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    canonical_code = models.ForeignKey(ImmunizationManufacturer, null=True)

    def __unicode__(self):
        return u'%s' % self.name


