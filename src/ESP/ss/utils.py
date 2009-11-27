#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from ESP.emr.models import Patient
from ESP.ss.models import Site, NonSpecialistVisitEvent
from ESP.ss.definitions import btzip, localSiteSites


def report_folder(begin_date, end_date):
    folder = os.path.join(os.path.dirname(__file__), 'assets')

    same_year = (begin_date.year == end_date.year)
    same_month = same_year and (begin_date.month == end_date.month)
    same_day = same_month and (begin_date.day == end_date.day)

    if same_year: folder = os.path.join(folder, '%04d' % begin_date.year)
    if same_month: folder = os.path.join(folder, '%02d' % begin_date.month)
    if same_day: folder = os.path.join(folder, '%02d' % begin_date.day)

    if not os.path.isdir(folder): os.makedirs(folder)
    return folder

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
            ev.reporting_site = Site.objects.get(code=ev.encounter.native_site_num)
            ev.save()
            missed += 1
        except Exception, why:
            null +=1

    print 'Missed %s, None %s' % (missed, null)
    
        
if __name__ == '__main__':
    rebuild_site_relation()
#    make_non_specialty_clinics()
    
