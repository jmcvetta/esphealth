#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from ESP.emr.models import Patient
from ESP.ss.models import Site, NonSpecialistVisitEvent
from ESP.ss.definitions import btzip, localSiteSites
from ESP.settings import DATA_DIR

def report_folder(begin_date, end_date, subfolder=None, resolution='day'):
    folder = os.path.join(DATA_DIR, 'ss')
    
    if subfolder: folder = os.path.join(folder, subfolder)
    resolution = resolution if resolution in [None, 'year', 'month', 'day'] else 'day'
    
    same_year = (begin_date.year == end_date.year) and resolution in ['year', 'month', 'day']
    same_month = same_year and (begin_date.month == end_date.month) and resolution in ['month', 'day']
    same_day = same_month and (begin_date.day == end_date.day) and resolution == 'day'

    if same_year: folder = os.path.join(folder, '%04d' % begin_date.year)
    if same_month: folder = os.path.join(folder, '%02d' % begin_date.month)
    if same_day: folder = os.path.join(folder, '%02d' % begin_date.day)

    if not os.path.isdir(folder): os.makedirs(folder)
    return folder

def age_identifier(age_group):
    if age_group:
        lower = age_group[0] if type(age_group[0]) is int else 'under'
        upper = (age_group[1] - 1) if type(age_group[1]) is int else 'plus'
        return '-age-%s-%s' % (lower, upper)
    else:
        return '-all'


def make_non_specialty_clinics():
    # Some really twisted list comprehension magic to get a
    # tab-demilited file turned into a a list of lists, each list
    # representing the data from about the relevant sites.

    # According to the file, a relevant site is one where the line
    # does not start with an asterisk.
    relevant_sites = [x for x in localSiteSites if not x.split('|')[0].startswith('*')][2:-1]
    site_matrix = [x.split('|') for x in relevant_sites]
    site_clean = [[x.strip() for x in entry] for entry in site_matrix]

    for site in site_matrix:
        Site.objects.create(
            code = site[3].strip(),
            name = site[2].strip(),
            zip_code = site[0].strip()[:5]
            )


def rebuild_site_relation():
    missed = 0
    null = 0
    for ev in NonSpecialistVisitEvent.objects.filter(reporting_site__isnull=True):
        try:
            ev.reporting_site = Site.objects.get(code=ev.encounter.site_natural_key)
            ev.save()
            missed += 1
        except Exception, why:
            null +=1

    print 'Missed %s, None %s' % (missed, null)
    
        
if __name__ == '__main__':
    rebuild_site_relation()
#    make_non_specialty_clinics()
    
