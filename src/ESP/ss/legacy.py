#!/usr/bin/python
# -*- coding: utf-8 -*-

from web import database
from web.db import sqlwhere

from ESP.localsettings import LEGACY_DB_USER, LEGACY_DB_PASSWORD, LEGACY_DB_NAME, LEGACY_DB_ENGINE

db = database(dbn=LEGACY_DB_ENGINE, user=LEGACY_DB_USER, pw=LEGACY_DB_PASSWORD, db=LEGACY_DB_NAME)

def encounters_from_clinics_on(site_list, date_str):
    l = len(site_list)
    if l == 0: site_filter = '0=1'
    elif l ==1: site_filter = "EncEncounter_Site = '%s'" % str(site_list[0])
    else: site_filter = 'EncEncounter_Site IN (%s)' % ', '.join(["'%s'" % x for x in site_list])

    return db.select('esp_enc', what='id', where=' AND '.join([site_filter, "EncEncounter_Date = '%s'" % date_str]))
    
