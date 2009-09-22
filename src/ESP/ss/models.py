'''
                                  ESP Health
                          Syndromic Surveillance Tables
                                  Data Models

@author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>

'''

import datetime

from django.db import models
from django.db.models import Q

from ESP.emr.models import Encounter
from ESP.hef.models import Event


def age_group_filter(lower, upper=150):
    today = datetime.date.today()
    younger_patient_date = datetime.date(year=(today.year - abs(lower)), 
                                         month=today.month, day=today.day)
    older_patient_date = datetime.date(year=(today.year - abs(upper)), 
                                       month=today.month, day=today.day)
    
    born_before = Q(patient__date_of_birth__gte=older_patient_date)
    born_after = Q(patient__date_of_birth__lt=younger_patient_date)
    
    return born_before & born_after

class Site(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    zip_code = models.CharField(max_length=10, db_index=True)

    @staticmethod
    def volume_by_zip(zip_code, date, exclude_duplicates=True):
        ''' 
        Returns the volume in a given day in the clinics that have a
        given zip code, by checking how many encounters were
        recorded. If exclude_duplicates is True, the count is reduced
        to only the number of patients.
        '''
        count = Encounter.objects.filter(
            date=date, native_site_num__in=Site.site_ids(zip_code)).values_list('patient')
        return count.distinct().count() if exclude_duplicates else count.count()
        
    @staticmethod
    def encounters_by_zip(zip_code):
        ''' 
        Returns a QuerySet for encounters from all sites with a given zip code
        '''
        return Encounter.objects.filter(
            native_site_num__in=Site.site_ids(zip_code))

    @staticmethod
    def age_group_aggregate(zip_code, date, lower, upper=90):
        return Site.encounters_by_zip(zip_code).filter(
            age_group_filter(lower, upper)
            ).filter(date=date).count()

    @staticmethod
    def site_ids(zip_code=None):
        sites = Site.objects.filter(zip_code=zip_code) if zip_code else Site.objects.all() 
        return sites.values_list('code', flat=True)


    def encounters(self, acute_only=True, **kw):
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

        if acute_only:
            encounters = encounters.filter(native_site_num__in=Site.site_ids())

        return encounters


class Locality(models.Model):
    zip_code = models.CharField(max_length=10, db_index=True)
    locality = models.CharField(max_length=50, db_index=True)
    city = models.CharField(max_length=50, db_index=True)
    state = models.CharField(max_length=2)
    region_code = models.CharField(max_length=5, null=True)
    region_name = models.CharField(max_length=20, null=True)
    is_official = models.BooleanField(default=True)
    
    def __unicode__(self):
        return u'%s - %s, %s (%s)' % (self.locality, self.city, self.state, self.zip_code)


class NonSpecialistVisitEvent(Event):
    reporting_site = models.ForeignKey(Site, null=True)
    patient_zip_code = models.CharField(max_length=10, null=True)
    encounter = models.ForeignKey(Encounter)
