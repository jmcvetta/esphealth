#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import unittest
import random
import pdb

from ESP.utils.utils import date_from_str, str_from_date
from ESP.emr.models import Encounter, Patient
from ESP.ss.models import Site, NonSpecialistVisitEvent
from ESP.ss.reports import Report
from ESP.ss.heuristics import syndrome_heuristics



import legacy


DAY = datetime.date(2009, 07, 01)
ZIP = '02446'

encs = Encounter.objects.filter(date=DAY, patient__zip=ZIP)
ili_cases = NonSpecialistVisitEvent.objects.filter(date=DAY, heuristic='ILI')

class TestSites(unittest.TestCase):
    def testList_on_db(self):
        self.assert_(Site.objects.count() == 96, 'Non Specialty Sites not on list')


class TestEncounters(unittest.TestCase):
    def testEncounters_ok(self):

        self.assert_(encs.count() == 16, 'Encounter records from %s on %s do not match with mySQL version')

    def testAggregateILI(self):
        ili_on_zip = ili_cases.filter(patient_zip_code=ZIP)
        self.assert_(ili_on_zip.count() == 1, 'No ILI detected')


class TestReports(unittest.TestCase):
    def setUp(self):
        pass
        # self.report = Report(DAY)

    def testAggregateResidential(self):
#        for syndrome in syndrome_heuristics().values():

        for delta in xrange(7):
            day = DAY + datetime.timedelta(delta)
            report = Report(day)
            syndrome = syndrome_heuristics()['ili']
            results = report._compare_aggregate_residential(syndrome)
            
            if 'encounters' in results:
                for zip_code in results['encounters']: 
                    when = str_from_date(day)
                    sites = Site.site_ids(zip_code)
                    for enc in legacy.encounters_from_clinics_on(sites, when):
                        print enc


    def testAggregateSite(self):
        for delta in xrange(7):
            day = DAY + datetime.timedelta(delta)
            report = Report(day)

            for syndrome in syndrome_heuristics().values():
                results = report._compare_aggregate_site(syndrome)
            
                if 'encounters' in results:
                    for zip_code in results['encounters']: 
                        when = str_from_date(day)
                        sites = Site.site_ids(zip_code)
                        for enc in legacy.encounters_from_clinics_on(sites, when):
                            print enc
                        
    def testEncounterCounts(self):
        pass



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReports)
    unittest.TextTestRunner(verbosity=2).run(suite)


