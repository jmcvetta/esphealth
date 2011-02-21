#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import unittest
import random
import pdb

from esp.utils.utils import date_from_str, str_from_date
from esp.emr.models import Encounter, Patient
from esp.ss.models import Site, NonSpecialistVisitEvent
from esp.ss.reports import Report
from esp.ss.heuristics import syndrome_heuristics



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

            
            if 'disparities' in results:
                for zip_code, d in results['disparities'].items():
                    sites = Site.site_ids()
                    encounters = d.get('encounters', None)
                    if encounters:
                        new_query = Encounter.objects.values_list('id', flat=True).filter(
                            date=day, patient__zip5=zip_code, native_site_num__in=sites)
                        if not new_query.count() == int(encounters['new']):
                            print 'Different values in total count on %s for zip %s' % (day, zip_code)
                            print new_query.count()
                            print encounters['new']
                            print encounters['old']

                        old_ids = set(list(legacy.encounters_from_clinics_on(sites, day)))

                        for item in (set(new_query) - old_ids):
                            try:
                                enc = Encounter.objects.get(id=item)
                                print 'Encounter found only on new db: %s' % enc
                            except Exception, why:
                                pass
                            
                        for item in (old_ids - set(new_query)):
                            try:
                                enc = Encounter.objects.get(id=item)
                                print 'Encounter found only on old db: %s' % enc
                            except Exception, why:
                                pass


        
            


    def testAggregateSite(self):
        for delta in xrange(7):
            day = DAY + datetime.timedelta(delta)
            report = Report(day)
            syndrome = syndrome_heuristics()['ili']
            results = report._compare_aggregate_site(syndrome)

            
            if 'disparities' in results:
                for zip_code, d in results['disparities'].items():
                    sites = Site.site_ids(zip_code)
                    encounters = d.get('encounters', None)
                    if encounters:
                        new_query = Encounter.objects.values_list('id', flat=True).filter(
                            date=day, native_site_num__in=Site.site_ids(zip_code))

                        if not new_query.count() == int(encounters['new']):
                            print 'Different values in total count on %s for zip %s' % (day, zip_code)
                            print new_query.count()
                            print encounters['new']
                            print encounters['old']


                        
                        old_ids = set(list(legacy.encounters_from_clinics_on(sites, day)))

                        for item in (set(new_query) - old_ids):
                            try:
                                enc = Encounter.objects.get(id=item)
                                print 'Encounter found only on new db: %s' % enc
                            except Exception, why:
                                pass

                        for item in (old_ids - set(new_query)):
                            try:
                                enc = Encounter.objects.get(id=item)
                                print 'Encounter found only on old db: %s' % enc
                            except Exception, why:
                                pass




        for delta in xrange(7):
            day = DAY + datetime.timedelta(delta)
            report = Report(day)

            # for syndrome in syndrome_heuristics().values():
            #     results = report._compare_aggregate_site(syndrome)
            
            #     if 'encounters' in results:
            #         for zip_code in results['encounters']: 
            #             when = str_from_date(day)
            #             sites = Site.site_ids(zip_code)
            #             print legacy.encounters_from_clinics_on(sites, when)

                        
    def testEncounterCounts(self):
        pass



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReports)
    unittest.TextTestRunner(verbosity=2).run(suite)


