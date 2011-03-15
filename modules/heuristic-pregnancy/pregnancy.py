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

from django.db.models import Q
from django.db.models import Min

from ESP.utils import log
from ESP.utils import log_query
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.hef.core import BaseTimespanHeuristic
from ESP.hef.models import Timespan


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The VERSION_URI string uniquely describes this heuristic.
# It MUST be incremented whenever any functionality is changed!
VERSION_URI = 'https://esphealth.org/reference/hef/heuristic/pregnancy/1.0'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


PREG_START_MARGIN = datetime.timedelta(days=20)
PREG_END_MARGIN = datetime.timedelta(days=20)


class PregnancyHeuristic(BaseTimespanHeuristic):
    
    name = 'pregnancy'
    
    uri = VERSION_URI
    
    core_uris = [
        'https://esphealth.org/reference/hef/core/1.0',
        ]
    
    
    def generate_timespans(self):
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #
        # Initialize
        #
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        preg_icd9_q = Q(icd9_codes__code__startswith='V22.') | Q(icd9_codes__code__startswith='V23.')
        self.ignore_bound_q = ~Q(timespan__name='pregnancy')
        has_edd_q = Q(edd__isnull=False)
        self.edd_encounters = Encounter.objects.filter(has_edd_q).order_by('date')
        log_query('Pregnancy encounters by edd', self.edd_encounters)
        preg_icd9_q = Q(icd9_codes__code__startswith='V22.') | Q(icd9_codes__code__startswith='V23.')
        self.icd9_encounters = Encounter.objects.filter(~has_edd_q & preg_icd9_q).order_by('date')
        log_query('Pregnancy encounters by ICD9', self.icd9_encounters)
        all_preg_q = preg_icd9_q | has_edd_q
        self.all_preg_encounters = Encounter.objects.filter(all_preg_q).order_by('date')
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #
        # Build End of Pregnancy query
        #
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
        #
        self.preg_end_encounters = Encounter.objects.filter(preg_end_q).order_by('date')
        #-------------------------------------------------------------------------------
        #
        # Generate pregnancies
        #
        #-------------------------------------------------------------------------------
        log.info('Generating pregnancy events')
        #
        # EDD
        #
        q_obj = Q(encounter__edd__isnull=False) & ~Q(encounter__timespan__name='pregnancy')
        patient_qs = Patient.objects.filter(q_obj).distinct().order_by('pk')
        log_query('Patients to consider for EDD pregnancy', patient_qs)
        pat_count = patient_qs.count()
        index = 0
        for patient in patient_qs:
            index += 1
            log.debug('Patient %s [%6s/%6s]' % (patient.pk, index, pat_count))
            self.pregnancy_from_edd(patient)
        #
        # ICD9
        #
        q_obj = Q(encounter__icd9_codes__code__startswith='V22.') | Q(encounter__icd9_codes__code__startswith='V23.')
        q_obj &= Q(encounter__edd__isnull=True) 
        q_obj &= ~Q(encounter__timespan__name='pregnancy')
        patient_qs = Patient.objects.filter(q_obj).distinct().order_by('pk')
        log_query('Patients to consider for ICD9 pregnancy', patient_qs)
        pat_count = patient_qs.count()
        index = 0
        for patient in patient_qs:
            index += 1
            log.debug('Patient %s [%6s/%6s]' % (patient.pk, index, pat_count))
            self.pregnancy_from_icd9(patient)
        return Timespan.objects.filter(name='pregnancy').count()
    
    def check_existing(self, enc):
        '''
        If enc overlaps an existing pregnancy timespan, attach it and return the timespan object; 
        else return False
        '''
        if enc.edd:
            comp_date = enc.edd
        else:
            comp_date = enc.date
        start_comp_date = comp_date + PREG_START_MARGIN
        end_comp_date = comp_date - PREG_END_MARGIN
        q_obj = Q(name='pregnancy')
        q_obj &= Q(patient=enc.patient)
        q_obj &= Q(start_date__lte=start_comp_date)
        q_obj &= Q(end_date__gte=end_comp_date)
        spans = Timespan.objects.filter(q_obj)
        if spans:
            ts = spans[0]
            ts.encounters.add(enc)
            ts.save()
            log.debug('Added %s to %s' % (enc, ts))
            return ts
        else:
            return False
    
    def pregnancy_from_edd(self, patient):
        '''
        Generates pregnancy timespans for a given patient, based on encounters with edd value
        '''
        pregnancies = Timespan.objects.filter(name='pregnancy', patient=patient).order_by('start_date')
        #
        # edd
        #
        for enc in self.edd_encounters.filter(patient=patient).filter(self.ignore_bound_q):
            if self.check_existing(enc): # Oops, this one overlaps an existing pregnancy
                continue
            # edd is the taken from the chronologically most recent encounter that falls within 
            # the tentative pregnancy window established by the first encounter and its edd, thereby
            # (hopefully) capturing any revisions made to the edd over the course of pregnancy.
            low_edd = enc.edd - PREG_END_MARGIN
            high_edd = enc.edd + PREG_END_MARGIN
            edd = self.edd_encounters.filter(patient=patient, edd__gte=low_edd, edd__lte=high_edd).order_by('-date')[0].edd
            start_date = edd - datetime.timedelta(days=280)
            #
            # Create a new pregnancy timespan
            #
            new_preg = Timespan(
                name = 'pregnancy',
                patient = enc.patient,
                start_date = start_date,
                end_date = edd,
                pattern = 'EDD',
                )
            new_preg.save() # Must save before adding M2M relations
            # Attach encounters
            if start_date > enc.date:
                enc_start = enc.date
            else:
                enc_start = start_date
            enc_end = edd + PREG_END_MARGIN
            new_preg.encounters = self.all_preg_encounters.filter(patient=patient, date__gte=enc_start, date__lte=enc_end)
            new_preg.encounters.add(enc) # Add this one, in case it is dated after edd
            new_preg.save()
            #
            # New postpartum timespan
            #
            new_postpartum = Timespan(
                name = 'postpartum',
                patient = enc.patient,
                start_date = edd,
                end_date = edd + datetime.timedelta(days=120),
                pattern = 'EDD_+_120_days',
                )
            new_postpartum.save()
            log.debug('New pregnancy %s by EDD (patient %s):  %s - %s' % (new_preg.pk, patient.pk, new_preg.start_date, new_preg.end_date))
        return
    
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
            
pregnancy_heuristic = PregnancyHeuristic()