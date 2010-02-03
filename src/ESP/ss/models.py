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
from django.db.models import Q, F

from ESP.emr.models import Encounter
from ESP.hef.models import Event

from definitions import AGE_GROUP_CAP, MAXIMUM_AGE


def age_group_filter(lower, upper):
    if lower is None: lower = 0
    if upper is None: upper = MAXIMUM_AGE
    oldest = Q(patient__date_of_birth__gte=F('date') - int(upper*365.25))
    youngest  = Q(patient__date_of_birth__lte=F('date') - int(lower*365.25))
    
    return oldest & youngest

class Site(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    zip_code = models.CharField(max_length=10, db_index=True)

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


    def similar_age_group(self, age_group_interval=5):
        '''
        returns a queryset representing all events that happened with
        patients at the same age group that the event's patient's age
        group.
        '''
        if not self.patient.date_of_birth: return

        age_group = self.patient.age_group(when=self.date)
        upper_bound_year = self.date.year - age_group

        # if somebody falls in the '85 and above' age group, we need
        # to assume that the patient's age is high enough to include
        # all patients that can fit into this group. So, we set
        # lower_bound_year to be 1800, so that we can check patients
        # even if they are 200+ years old.
        if age_group < (AGE_GROUP_CAP - age_group_interval):
            lower_bound_year = self.date.year - age_group - age_group_interval
        else:
            lower_bound_year = 1800

        month = self.patient.date_of_birth.month
        day = self.patient.date_of_birth.day

        # Need to check for leap years.
        if month == 2 and day > 28: day = 28

        # Edge case, youngest dob is lower than patient's dob if
        # patient is born on Feb 29 and 0 years old at time of
        # event.
        youngest_dob = max(
            datetime.date(year=upper_bound_year, month=month, day=day),
            self.patient.date_of_birth
            )
        oldest_dob = datetime.date(year=lower_bound_year, month=month, day=day)

        
        return NonSpecialistVisitEvent.objects.filter(
            name=self.name, 
            patient__date_of_birth__gte=oldest_dob, patient__date_of_birth__lte=youngest_dob
            )

