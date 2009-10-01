#!/usr/bin/python
# -*- coding: utf-8 -*-

from ESP.emr.models import Patient

from ESP.ss.models import Site
from ESP.ss.definitions import btzip, localSiteSites

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
        
if __name__ == '__main__':
    make_non_specialty_clinics()
    
