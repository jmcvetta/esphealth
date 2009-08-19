'''
                                  ESP Health
                          Syndromic Surveillance Tables
                                  Data Models

@author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>

'''

from django.db import models

from ESP.emr.models import Encounter
from ESP.hef.models import HeuristicEvent

    
class Site(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    zip_code = models.CharField(max_length=10)

    def encounters(self, **kw):
        ''' 
        Returns a list of all encounters that took place at this Site.
        kw may contain specific filters, like icd9 codes or dates.
        '''

        date = kw.pop('date', None)
        at_site = Encounter.objects.filter(
            native_site_num = str(self.code))

        encounters = at_site        
        if date:
            encounters = encounters.filter(date=date)

        return encounters

    def volume(self, date):
        ''' total count of encounters had at clinic on a given day '''
        return self.encounters(date=date).count()


class Locality(models.Model):
    zip_code = models.CharField(max_length=9, db_index=True)
    locality = models.CharField(max_length=50, db_index=True)
    city = models.CharField(max_length=50, db_index=True)
    state = models.CharField(max_length=2)
    region_code = models.CharField(max_length=5)
    region_name = models.CharField(max_length=20)
    is_official = models.BooleanField(default=True)

    def encounters(self, **kw):
        ''' 
        Returns a list of all encounters that took place at this Site.
        kw may contain specific filters, like icd9 codes or dates.
        '''

        date = kw.pop('date', None)
        at_locality = Encounter.objects.filter(
            patient__zip=self.zip_code)

        encounters = at_locality
        if date:
            encounters = encounters.filter(date=date)

        return encounters

    def volume(self, date):
        ''' total count of encounters had at locality on a given day '''
        return self.encounters(date=date).count()

    
    def __unicode__(self):
        return u'%s - %s, %s (%s)' % (self.locality, self.city, self.state, self.zip_code)

class NonSpecialistVisitEvent(HeuristicEvent):
    reporting_site = models.ForeignKey(Site, null=True)
    patient_zip_code = models.CharField(max_length=10, null=True)
