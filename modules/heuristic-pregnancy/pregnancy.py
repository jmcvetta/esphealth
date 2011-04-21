'''
                                  ESP Health
                          Heuristic Events Framework
Pregnancy Timespan Detector


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''

import datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import Min

from ESP.utils import log
from ESP.utils import log_query
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.hef.base import BaseTimespanHeuristic
from ESP.hef.models import Timespan


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The VERSION_URI string uniquely describes this heuristic.
# It MUST be incremented whenever any functionality is changed!
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#PREG_START_MARGIN = datetime.timedelta(days=20)
PREG_MARGIN = relativedelta(days=30)


class PregnancyHeuristic(BaseTimespanHeuristic):
    
    short_name = 'timespan:pregnancy'
    
    uri = 'urn:x-esphealth:heuristic:channing:timespan:pregnancy:v1'
    
    core_uris = ['urn:x-esphealth:hef:core:v1']
    
    timespan_names = ['pregnancy', 'postpartum',]
    
    
    def __init__(self):
        #
        self.timespan_names = [
            'pregnancy:edd',
            'pregnancy:icd9-eop',
            'pregnancy:icd9-only',
            ]
        #-------------------------------------------------------------------------------
        #
        # EDD Encounters
        #
        #-------------------------------------------------------------------------------
        edd_enc_qs = Encounter.objects.all()
        edd_enc_qs = edd_enc_qs.filter(edd__isnull=False)
        edd_enc_qs = edd_enc_qs.exclude(timespan__name__in=self.timespan_names)
        self.edd_enc_qs = edd_enc_qs
        #-------------------------------------------------------------------------------
        #
        # ICD9 Encounters
        #
        #-------------------------------------------------------------------------------
        preg_icd9_q = Q(icd9_codes__code__startswith='V22.') | Q(icd9_codes__code__startswith='V23.')
        icd9_enc_qs = Encounter.objects.all()
        icd9_enc_qs = icd9_enc_qs.filter(preg_icd9_q)
        icd9_enc_qs = icd9_enc_qs.filter(edd__isnull=True)
        icd9_enc_qs = icd9_enc_qs.exclude(timespan__name='pregnancy')
        self.icd9_enc_qs = icd9_enc_qs
        #-------------------------------------------------------------------------------
        #
        # End of Pregnancy
        #
        #-------------------------------------------------------------------------------
        #
        # Postpartum care
        #
        preg_end_q = Q(icd9_codes__code__startswith='V24.')  
        #
        # Ectopic & molar pregnancy
        #
        preg_end_q |= Q(icd9_codes__code__startswith='630.') 
        preg_end_q |= Q(icd9_codes__code__startswith='631.')
        preg_end_q |= Q(icd9_codes__code__startswith='632.')
        preg_end_q |= Q(icd9_codes__code__startswith='633.')
        #
        # Abortion
        #
        preg_end_q |= Q(icd9_codes__code__startswith='634.')
        preg_end_q |= Q(icd9_codes__code__startswith='635.')
        preg_end_q |= Q(icd9_codes__code__startswith='636.')
        preg_end_q |= Q(icd9_codes__code__startswith='637.')
        preg_end_q |= Q(icd9_codes__code__startswith='639.')
        #
        # Complications of pregnancy with delivery
        #
        preg_end_q |= (
            Q(icd9_codes__code__startswith='640.') |
            Q(icd9_codes__code__startswith='641.') |
            Q(icd9_codes__code__startswith='642.') |
            Q(icd9_codes__code__startswith='643.') |
            Q(icd9_codes__code__startswith='644.') |
            Q(icd9_codes__code__startswith='645.') |
            Q(icd9_codes__code__startswith='646.') |
            Q(icd9_codes__code__startswith='647.') |
            Q(icd9_codes__code__startswith='648.') |
            Q(icd9_codes__code__startswith='649.') 
            ) & (
            Q(icd9_codes__code__endswith='1') |
            Q(icd9_codes__code__endswith='2') |
            Q(icd9_codes__code__endswith='4')
            )
        #
        # Normal delivery
        #
        preg_end_q |= (
            Q(icd9_codes__code__startswith='650.') |
            Q(icd9_codes__code__startswith='651.') |
            Q(icd9_codes__code__startswith='652.') |
            Q(icd9_codes__code__startswith='653.') |
            Q(icd9_codes__code__startswith='654.') |
            Q(icd9_codes__code__startswith='655.') |
            Q(icd9_codes__code__startswith='656.') |
            Q(icd9_codes__code__startswith='657.') |
            Q(icd9_codes__code__startswith='658.') |
            Q(icd9_codes__code__startswith='659.')
            ) & (
            Q(icd9_codes__code__endswith='1') |
            Q(icd9_codes__code__endswith='2') |
            Q(icd9_codes__code__endswith='4')
            )
        #
        # Complications of labor
        #
        preg_end_q |= Q(icd9_codes__code__startswith='660.') 
        preg_end_q |= Q(icd9_codes__code__startswith='661.') 
        preg_end_q |= Q(icd9_codes__code__startswith='662.') 
        preg_end_q |= Q(icd9_codes__code__startswith='663.') 
        preg_end_q |= Q(icd9_codes__code__startswith='664.') 
        preg_end_q |= Q(icd9_codes__code__startswith='665.') 
        preg_end_q |= Q(icd9_codes__code__startswith='666.') 
        preg_end_q |= Q(icd9_codes__code__startswith='667.') 
        preg_end_q |= Q(icd9_codes__code__startswith='668.') 
        preg_end_q |= Q(icd9_codes__code__startswith='669.') 
        #
        # Encounter QS
        #
        eop_qs = Encounter.objects.all() # EoP = End of Pregnancy
        eop_qs = eop_qs.filter(preg_end_q)
        self.eop_qs = eop_qs
        #
        # All relevant encounters
        #
        self.relevant_enc_qs = edd_enc_qs | icd9_enc_qs | eop_qs
        
    def generate(self):
        log.info('Generating pregnancy events')
        ts_count = 0 # Counter for new timespans generated
        #
        # EDD
        #
        edd_patient_qs = self.edd_enc_qs.values_list('patient', flat=True).distinct()
        log_query('Patients to consider for EDD pregnancy', edd_patient_qs)
        pat_count = edd_patient_qs.count()
        index = 0
        for patient in edd_patient_qs:
            index += 1
            log.debug('Patient %s [%6s/%6s]' % (patient, index, pat_count))
            ts_count += self.pregnancy_from_edd(patient)
        #
        # ICD9
        #
        log_query('Patients to consider for ICD9 pregnancy', icd9_patient_qs)
        icd9_patient_qs = self
        pat_count = icd9_patient_qs.count()
        index = 0
        for patient in icd9_patient_qs:
            index += 1
            log.debug('Patient %s [%6s/%6s]' % (patient.pk, index, pat_count))
            ts_count += self.pregnancy_from_icd9(patient)
        return ts_count
    
    def overlaps_existing(self, enc):
        '''
        If enc overlaps an existing pregnancy timespan, attach it and return the timespan object; 
        else return False
        '''
        spans = Timespan.objects.filter(
            name__in = self.timespan_names,
            patient = enc.patient,
            start_date__lte = enc.date,
            end_date__gte = enc.edd - PREG_MARGIN,
            ).order_by('start_date')
        if not spans.count():
            return False
        if spans.count() > 1:
            log.warning('Something is wrong - encounter %s overlaps more than one pregnancy timespan!' % enc)
        ts = spans[0]
        ts.encounters.add(enc)
        ts.save()
        log.debug('Added %s to %s' % (enc, ts))
        return ts
    
    def pregnancy_from_edd(self, patient):
        '''
        Generates pregnancy timespans for a given patient, based on encounters with edd value
        '''
        counter = 0
        pat_edd_encs = self.edd_enc_qs.filter(patient=patient)
        next_preg_min_edd = None
        for enc in pat_edd_encs.order_by('edd'):
            # When we create a new pregnancy timespan we attach all relevant 
            # encounters.  So we do not need to individuall re-attach each of 
            # those encounters as we iterate through them.
            if next_preg_min_edd and (enc.edd < next_preg_min_edd):
                continue
            # This encounter *should* fall outside any existing timespan.  Just
            # to be sure, we check with a db query.
            if self.overlaps_existing(enc):
                continue
            # "If patient has multiple qualifying events for preg_start and
            # preg_end that generate overlapping periods of pregnancy, use the
            # minimum for each of preg_start and preg_end"
            #
            # "Patient can have multiple episodes of pregnancy - define minimum
            # interval between pregnancy end and start of new pregnancy as 3
            # months."
            onset = enc.edd - relativedelta(days=280)
            new_preg = Timespan(
                name = 'pregnancy:edd',
                patient = enc.patient,
                start_date = onset,
                end_date = enc.edd,
                source = self.uri,
                )
            new_preg.save() # Must save before adding M2M relations
            counter += 1
            log.debug('Created timespan: %s' % new_preg)
            #
            # Attach encounters
            #
            if onset > enc.date:
                start_date = enc.date
            else:
                start_date = onset
            # The next new pregnancy cannot start until EDD + 30 days.  First valid
            # EDD for a subsequent pregnancy is therefore this EDD + 30 days + 280 days.
            next_preg_min_edd = enc.edd + PREG_MARGIN + relativedelta(days=280)
            new_preg.encounters = self.relevant_enc_qs.filter(patient=patient, 
                date__gte=start_date, 
                edd__lt=next_preg_min_edd)
            new_preg.save()
        return counter
    
    def get_end_date(self, ):
        '''
        Ret
        '''
        
        
    def pregnancy_from_icd9(self, patient):
        '''
        Generates pregnancy timespans for a given patient, based on a
        combination of encounters with pregnancy ICD9s and end-of-pregnancy ICD9s
        '''
        for enc in self.icd9_encounters.filter(patient=patient).filter(self.ignore_bound_q):
            if self.check_existing(enc): # Oops, this one overlaps an existing pregnancy
                continue
            #
            # Are there any pregnancy-end events? (postnatal care, stillbirth, abortion)
            #
            end_encs = self.preg_end_encounters.filter(patient=patient, date__gte=enc.date, 
                date__lte=(enc.date + datetime.timedelta(days=300)) )
            if end_encs: # Plausible end date, so start 280 days before that
                end_date = end_encs.aggregate(end_date=Min('date'))['end_date']
                start_date = end_date - datetime.timedelta(days=280)
                pattern = 'ICD9_EOP' # EOP = End of Pregnancy
            else: # No plausible end date, so assume 280 days after start date
                start_date = enc.date - datetime.timedelta(days=15)
                end_date =  start_date + datetime.timedelta(days=280)
                pattern = 'ICD9_ONLY'
            #
            # Create Timespans
            #
            new_preg = Timespan(
                name = 'pregnancy',
                patient = enc.patient,
                start_date = start_date,
                end_date = end_date,
                pattern = pattern,
                )
            new_preg.save() # Must save before adding many-to-many objects
            # Attach encounters
            if start_date > enc.date:
                enc_start = enc.date
            else:
                enc_start = start_date
            enc_end = start_date + PREG_END_MARGIN
            new_preg.encounters = self.all_preg_encounters.filter(patient=patient, date__gte=enc_start, date__lte=enc_end)
            new_preg.encounters.add(enc) # Add this one, in case it is dated after end date
            new_preg.save()
            log.debug('New pregnancy %s by %s (patient %s):  %s - %s' % (new_preg.pk, pattern, patient.pk, new_preg.start_date, new_preg.end_date))
            #
            # New postpartum timespan
            #
            new_postpartum = Timespan(
                name = 'postpartum',
                patient = enc.patient,
                start_date = end_date,
                end_date = end_date + datetime.timedelta(days=120),
                pattern = '%s+_120_days' % pattern,
                )
            new_postpartum.save()
        return 
            

def get_timespan_heuristics():
    return [
        PregnancyHeuristic(),
        ]
