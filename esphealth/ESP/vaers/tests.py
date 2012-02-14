'''
                                  ESP Health
Vaccine Adverse Events Response Surveillance (VAERS) system
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
from ESP.static.models import Icd9
from ESP.emr.models import Encounter
from ESP.emr.models import Immunization
from ESP.emr.models import Problem
from ESP.vaers.models import EncounterEvent
from ESP.vaers.management.commands.vaers import Command as VaersCommand
from ESP.vaers.management.commands.set_rules import Command as SetRulesCommand


class VaersTestCase(EspTestCase):
    
    def setUp(self):
        '''
        The DiagnosticsEventRule table must be set up before running tests.
        '''
        cmnd = SetRulesCommand()
        cmnd.run_from_argv([None, None ])
        super(VaersTestCase, self).setUp()
    
    def test_any_other_dx(self):
        log.info('Testing VAERS')
        mccoy = self.create_provider(last='McCoy', first='Leonard')
        kirk = self.create_patient(last='Kirk', first='James', pcp=mccoy)
        spock = self.create_patient(last='Spock', first='Mister', pcp=mccoy)
        uhura = self.create_patient(last='Spock', first='Nyota', pcp=mccoy)
        #-------------------------------------------------------------------------------
        #
        # Potential Adverse Events
        #
        #-------------------------------------------------------------------------------
        # All of our crew will be given a vaccine on the same day, and 
        # diagnosed with an unusual ICD9 code on the same day.
        #
        # The actual meaning of this ICD9 is not important here. The 
        # vaccines and diagnoses occur on the same day for programming
        # convenience; but that will not effect the outcome, as the 
        # patients are considered separately.
        #
        vaccine_date = datetime.date(year=2010, month=2, day=15)
        dx_date = vaccine_date + relativedelta(days=7)
        unusual_icd9_str = '555.55' 
        unusual_icd9_obj, created = Icd9.objects.get_or_create(code=unusual_icd9_str)
        for crew_member in [kirk, spock, uhura]:
            # TODO: Does the vaccine code matter to VAERS algo?
            new_imm = Immunization(
                provenance = self.provenance,
                provider = mccoy,
                patient = crew_member,
                date = vaccine_date,
                imm_type = 'foobar_immtype',
                name = 'foobar_name',
                dose = 'foobar_dose',
                manufacturer = 'foobar_manufacturer',
                )
            new_imm.save()
            new_enc = self.create_diagnosis(
                provider = mccoy, 
                patient = crew_member, 
                date = dx_date,
                codeset = 'icd9', 
                diagnosis_code = unusual_icd9_str,
                )
            #
            # Set aside Kirk's diagnosis encounter for later use
            #
            if crew_member == kirk:
                kirk_enc = new_enc
        #-------------------------------------------------------------------------------
        #
        # Excluding events
        #
        #-------------------------------------------------------------------------------
        # 
        # Spock has unusual_icd9_code in his problem list prior to
        # his vaccination.
        #
        spock_prob = Problem(
            provenance = self.provenance,
            provider = mccoy,
            patient = spock,
            date = vaccine_date - relativedelta(years=1),
            icd9 = unusual_icd9_obj,
            )
        spock_prob.save()
        #
        # Uhura had an encounter with this ICD9 code prior to her
        # vaccination.
        #
        self.create_diagnosis(
            provider = mccoy, 
            patient = uhura, 
            date = vaccine_date - relativedelta(months=6),
            codeset = 'icd9', 
            diagnosis_code = unusual_icd9_str,
            )
        #-------------------------------------------------------------------------------
        #
        # Run VAERS
        #
        #-------------------------------------------------------------------------------
        cmnd = VaersCommand()
        cmnd.run_from_argv([None, None, '-c', '-a'])
        #-------------------------------------------------------------------------------
        #
        # Check results
        #
        #-------------------------------------------------------------------------------
        #
        # Spock and Uhura do NOT have an adverse event.
        #
        self.assertEquals(EncounterEvent.objects.filter(patient=spock).count(), 0)
        self.assertEquals(EncounterEvent.objects.filter(patient=uhura).count(), 0)
        #
        # Kirk DOES have an adverse event.
        #
        kirk_qs = EncounterEvent.objects.filter(patient=kirk)
        self.assertEquals(kirk_qs.count(), 1)
        kirk_event = kirk_qs[0]
        self.assertEquals(kirk_event.provider, mccoy)
        self.assertEquals(kirk_event.date, dx_date)
        self.assertEquals(kirk_event.encounter, kirk_enc)
