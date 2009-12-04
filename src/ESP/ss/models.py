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
        patients = Encounter.objects.syndrome_care_visits(sites=Site.site_ids(zip_code)).values_list(
            'patient').filter(date=date)
        return patients.distinct().count() if exclude_duplicates else patients.count()
        
    @staticmethod
    def encounters_by_zip(zip_code):
        ''' 
        Returns a QuerySet for encounters from all sites with a given zip code
        '''
        return Encounter.objects.syndrome_care_visits(
            sites=Site.site_ids(zip_code)).select_related('patient')

    @staticmethod
    def age_group_aggregate(zip_code, date, lower, upper=90):
        return Site.encounters_by_zip(zip_code).filter(age_group_filter(lower, upper)).filter(
            date=date).count()

    @staticmethod
    def site_ids(zip_code=None):
        sites = Site.objects.filter(zip_code=zip_code) if zip_code else Site.objects.all() 
        return sites.values_list('code', flat=True)


class NonSpecialistVisitEvent(Event):
    reporting_site = models.ForeignKey(Site, null=True)
    patient_zip_code = models.CharField(max_length=10, null=True)
    encounter = models.ForeignKey(Encounter)

    @staticmethod
    def counts_by_site(start_date, end_date):
        return NonSpecialistVisitEvent.objects.filter(date__gte=start_date, date__lte=end_date).values(
            'date', 'heuristic', 'reporting_site__zip_code').annotate(count=Count('heuristic'))
        
        
