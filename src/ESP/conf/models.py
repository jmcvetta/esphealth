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



class NativeCode(models.Model):
    '''
    A mapping from a native code (for a lab result, etc) to a Loinc number
    '''
    # This table and utilities making use of it assume only one external 
    # code table per ESP installation.  More work will be required if your 
    # installation must comprehend multiple, potentially overlapping, external 
    # code sources
    native_code = models.CharField(max_length=100, unique=True, blank=False)
    native_name = models.CharField(max_length=255, blank=True, null=True)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc = models.ForeignKey(Loinc, blank=True, null=True)
    ignore = models.BooleanField('Ignore in NLP report', blank=False, default=False)
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Native Code to LOINC Map'



class Vaccine(models.Model):
    '''
    A vaccine drug
    '''
    code = models.IntegerField(unique=True)
    short_name = models.CharField(max_length=60)
    name = models.CharField(max_length=300)
    
    @staticmethod
    def random():
        return Vaccine.objects.exclude(short_name='UNK').order_by('?')[0]

    @staticmethod
    def acceptable_mapping_values():
        return Vaccine.objects.exclude(short_name__in=['unknown', 'RESERVED - do not use', 'no vaccine administered'])

    def __unicode__(self):
        return u'%s (%s)'% (self.short_name, self.name)


class ImmunizationManufacturer(models.Model):
    code = models.CharField(max_length=3)
    full_name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    use_instead = models.ForeignKey('self', null=True)
    
    vaccines_produced = models.ManyToManyField(Vaccine)

    def __unicode__(self):
        return self.full_name


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


