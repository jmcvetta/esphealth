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
import optparse

from django.db.models import Q
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.utils import log
from ESP.utils import log_query
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.hef.models import Timespan


PREG_END_MARGIN = datetime.timedelta(days=20)


class Command(BaseCommand):
    
    help = 'Generate pregnancy timespans'
    
    def handle(self, *args, **options):
        #-------------------------------------------------------------------------------
        #
        # Initialize
        #
        #-------------------------------------------------------------------------------
        preg_icd9_q = Q(icd9_codes__code__startswith='V22.') | Q(icd9_codes__code__startswith='V23.')
        self.ignore_bound_q = ~Q(timespan__name='pregnancy')
        has_edc_q = Q(edc__isnull=False)
        self.edc_encounters = Encounter.objects.filter(has_edc_q).order_by('date')
        log_query('Pregnancy encounters by EDC', self.edc_encounters)
        preg_icd9_q = Q(icd9_codes__code__startswith='V22.') | Q(icd9_codes__code__startswith='V23.')
        self.icd9_encounters = Encounter.objects.filter(~has_edc_q & preg_icd9_q).order_by('date')
        log_query('Pregnancy encounters by ICD9', self.icd9_encounters)
        all_preg_q = preg_icd9_q | has_edc_q
        self.all_preg_encounters = Encounter.objects.filter(all_preg_q).order_by('date')
        preg_end_q = Q(icd9_codes__code__startswith='V24.')  # Postpartum care
        preg_end_q |= Q(icd9_codes__code__startswith='630.') # Ectopic & molar pregnancy
        preg_end_q |= Q(icd9_codes__code__startswith='631.') #  "
        preg_end_q |= Q(icd9_codes__code__startswith='632.') #  "
        preg_end_q |= Q(icd9_codes__code__startswith='633.') #  "
        preg_end_q |= Q(icd9_codes__code__startswith='634.') # Abortion
        preg_end_q |= Q(icd9_codes__code__startswith='635.') #  "
        preg_end_q |= Q(icd9_codes__code__startswith='636.') #  "
        preg_end_q |= Q(icd9_codes__code__startswith='637.') #  "
        preg_end_q |= Q(icd9_codes__code__startswith='639.') #  "
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
        q_obj = Q(encounter__edc__isnull=False) & ~Q(encounter__timespan__name='pregnancy')
        patient_qs = Patient.objects.filter(q_obj).distinct().order_by('pk')
        log_query('Patients to consider for EDD pregnancy', patient_qs)
        pat_count = patient_qs.count()
        index = 0
        for patient in patient_qs:
            index += 1
            log.debug('Patient %s [%6s/%6s]' % (patient.pk, index, pat_count))
            self.pregnancy_from_edc(patient)
        #
        # ICD9
        #
        q_obj = Q(encounter__icd9_codes__code__startswith='V22.') | Q(encounter__icd9_codes__code__startswith='V23.')
        q_obj &= Q(encounter__edc__isnull=True) 
        q_obj &= ~Q(encounter__timespan__name='pregnancy')
        patient_qs = Patient.objects.filter(q_obj).distinct().order_by('pk')
        log_query('Patients to consider for ICD9 pregnancy', patient_qs)
        pat_count = patient_qs.count()
        index = 0
        for patient in patient_qs:
            index += 1
            log.debug('Patient %s [%6s/%6s]' % (patient.pk, index, pat_count))
            self.pregnancy_from_icd9(patient)
        return Timespan.objects.filter(name__in='pregnancy').count()
    
    def check_existing(self, enc):
        '''
        If enc overlaps an existing pregnancy timespan, attach it and return the timespan object; 
        else return False
        '''
        if enc.edc:
            comp_date = enc.edc
        else:
            comp_date = enc.date
        q_obj = Q(name__in='pregnancy')
        q_obj = ~Q(pattern='ICD9_ONLY')
        q_obj &= Q(patient=enc.patient)
        q_obj &= Q(start_date__lte=comp_date)
        q_obj &= Q(end_date__gte=comp_date)
        spans = Timespan.objects.filter(q_obj)
        if spans:
            ts = spans[0]
            ts.encounters.add(enc)
            ts.save()
            log.debug('Added %s to %s' % (enc, ts))
            return ts
        else:
            return False
    
    def pregnancy_from_edc(self, patient):
        '''
        Generates pregnancy timespans for a given patient, based on encounters with EDC value
        '''
        pregnancies = Timespan.objects.filter(name='pregnancy', patient=patient).order_by('start_date')
        #
        # EDC
        #
        for enc in self.edc_encounters.filter(patient=patient).filter(self.ignore_bound_q):
            if self.check_existing(enc): # Oops, this one overlaps an existing pregnancy
                continue
            # EDC is the taken from the chronologically most recent encounter that falls within 
            # the tentative pregnancy window established by the first encounter and its EDC, thereby
            # (hopefully) capturing any revisions made to the EDC over the course of pregnancy.
            low_edc = enc.edc - PREG_END_MARGIN
            high_edc = enc.edc + PREG_END_MARGIN
            edc = self.edc_encounters.filter(patient=patient, edc__gte=low_edc, edc__lte=high_edc).order_by('-date')[0].edc
            start_date = edc - datetime.timedelta(days=280)
            if start_date > enc.date:
                enc_start = enc.date
            else:
                enc_start = start_date
            enc_end = edc + PREG_END_MARGIN
            #
            # Create a new pregnancy timespan
            #
            new_preg = Timespan(
                name = 'pregnancy',
                patient = enc.patient,
                start_date = start_date,
                end_date = edc,
                pattern = 'EDD',
                )
            new_postpartum = Timespan(
                name = 'postpartum',
                patient = enc.patient,
                start_date = edc,
                end_date = edc + datetime.timedelta(days=120),
                pattern = 'EDD_+_120_days',
                )
            new_preg.save() # Must save before adding M2M relations
            new_preg.encounters = self.all_preg_encounters.filter(patient=patient, date__gte=enc_start, date__lte=enc_end)
            new_preg.encounters.add(enc) # Add this one, in case it is dated after EDC
            new_preg.save()
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
            if end_encs: # If there is no plausible end date for this pregnancy, so we create 
                name = 'pregnancy'
                end_date = end_encs.aggregate(end_date=Min('date'))['end_date']
                start_date = end_date - datetime.timedelta(days=280)
                pattern = 'ICD9_EOP' # EOP = End of Pregnancy
                enc_start = enc.date # Attach encounters from this date or later
                enc_end = end_date + PREG_END_MARGIN # Attach encounters up until this date
                new_postpartum = Timespan(
                    name = 'postpartum',
                    patient = enc.patient,
                    start_date = end_date,
                    end_date = end_date + datetime.timedelta(days=120),
                    pattern = 'ICD9_EOP_+_120_days',
                    )
            else: # There is no plausible end date for this pregnancy, so we create a mini-pregnancy
                name = 'pregnancy'
                start_date = enc.date - datetime.timedelta(days=15)
                end_date =  enc.date + datetime.timedelta(days=15)
                pattern = 'ICD9_ONLY'
                enc_start = enc.date # Attach only encounters that are stricly within the mini-preg window
                enc_end = end_date     #  "
                new_postpartum = None
            new_preg = Timespan(
                name = name,
                patient = enc.patient,
                start_date = start_date,
                end_date = end_date,
                pattern = pattern,
                )
            new_preg.save() # Must save before adding many-to-many objects
            new_preg.encounters = self.all_preg_encounters.filter(patient=patient, date__gte=enc_start, date__lte=enc_end)
            new_preg.encounters.add(enc) # Add this one, in case it is dated after EDD
            new_preg.save() 
            if new_postpartum:
                new_postpartum.save()
            log.debug('New pregnancy %s by %s (patient %s):  %s - %s' % (new_preg.pk, pattern, patient.pk, new_preg.start_date, new_preg.end_date))
        return 
            