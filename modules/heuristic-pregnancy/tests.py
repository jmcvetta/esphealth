'''
                                  ESP Health
                              Pregnancy Heuristic
                                  Unit Tests


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2012 Channing Laboratory
@license: LGPL
'''

import datetime

from dateutil.relativedelta import relativedelta

from ESP.utils import log
from ESP.utils.testing import EspTestCase
from ESP.hef.base import BaseTimespanHeuristic
from ESP.hef.base import BaseEventHeuristic


'''
Run me with:
    time ./bin/esp test -v 2 --noinput --where=/home/jason/work/esphealth-trunk/src/heuristic-pregnancy
'''


class PregnancyTest(EspTestCase):
    '''
    Unit tests for pregnancy heuristic 
    '''     
    
    def test_single_edd(self):
        '''
        Suzy's pregnancy is indicated by a single Encounter record with a valid EDD.
        '''
        log.info('Testing pregnancy algorithm for single EDD event')
        dr_spock = self.create_provider(last='Spock', first='Benjamin')
        suzy = self.create_patient(last='Q', first='Suzy', pcp=dr_spock)
        edd_date = datetime.date(year=2010, month=2, day=15)
        edd_enc = Encounter(
            provenance = self.provenance,
            provider = dr_spock,
            patient = suzy,
            date = edd_date - relativedelta(months=7),
            edd = edd_date,
            )
        edd_enc.save()
        preg_heuristic = BaseTimespanHeuristic.get_heuristic_by_name('timespan:pregnancy')
        BaseTimespanHeuristic.generate_all(heuristic_list=[preg_heuristic], dependencies=True)
        event_qs = BaseEventHeuristic.get_events_by_name('enc:pregnancy:edd')
        self.assertEqual(event_qs.count(), 1, 'One and only one EDD event should be generated')
        preg_qs = BaseTimespanHeuristic.get_timespans_by_name(name='pregnancy')
        preg_qs = preg_qs.filter(patient=suzy)
        self.assertEqual(preg_qs.count(), 1, 'One and only one pregnancy timespan should be generated')
        suzy_preg = preg_qs[0]
        self.assertEqual(suzy_preg.start_date, edd_date - relativedelta(days=280))
        self.assertEqual(suzy_preg.end_date, edd_date)

    
        
        
        
