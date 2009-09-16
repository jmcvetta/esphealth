#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import unittest
import random
import pdb

from ESP.emr.models import Encounter, Patient
from ESP.ss.models import Site, NonSpecialistVisitEvent


DAY = datetime.date(2009, 07, 05)
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



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncounters)
    unittest.TextTestRunner(verbosity=2).run(suite)



    import pdb
    pdb.set_trace()
