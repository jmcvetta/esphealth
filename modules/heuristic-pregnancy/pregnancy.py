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
from decimal import Decimal
from functools import partial
from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.db.models import Q
from django.db.models import Min
from django.db.models import Max

from ESP.settings import HEF_THREAD_COUNT
from ESP.utils import log
from ESP.utils import log_query
from ESP.utils.utils import wait_for_threads
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.hef.base import BaseTimespanHeuristic
from ESP.hef.models import Timespan


#PREG_START_MARGIN = datetime.timedelta(days=20)
PREG_MARGIN = relativedelta(days=30)


class PregnancyHeuristic(BaseTimespanHeuristic):
    
    short_name = 'timespan:pregnancy'
    
    uri = 'urn:x-esphealth:heuristic:channing:timespan:pregnancy:v1'
    
    core_uris = ['urn:x-esphealth:hef:core:v1']
    
    timespan_names = ['pregnancy', 'postpartum',]
    
    
    def __init__(self):
        #-------------------------------------------------------------------------------
        #
        # EDD Encounters
        #
        #-------------------------------------------------------------------------------
        self.edd_qs = Encounter.objects.all()
        #-------------------------------------------------------------------------------
        #
        # ICD9 Encounters
        #
        #-------------------------------------------------------------------------------
        onset_q_obj = (
            Q(icd9_codes__code__startswith='V22.') | 
            Q(icd9_codes__code__startswith='V23.')
            )
        self.preg_icd9_qs = Encounter.objects.filter(onset_q_obj)
        #-------------------------------------------------------------------------------
        #
        # Onset
        #
        #-------------------------------------------------------------------------------
        self.onset_qs = Encounter.objects.filter(onset_q_obj)
        #-------------------------------------------------------------------------------
        #
        # End of Pregnancy
        #
        #-------------------------------------------------------------------------------
        #
        # Postpartum care
        #
        self.postpartum_q = Q(icd9_codes__code__startswith='V24.')  
        #
        # Ectopic & molar pregnancy
        #
        self.ectopic_molar_q = (
            Q(icd9_codes__code__startswith='630.') |
            Q(icd9_codes__code__startswith='631.') |
            Q(icd9_codes__code__startswith='632.') |
            Q(icd9_codes__code__startswith='633.')
            )
        #
        # Abortion
        #
        self.spontaneous_abortion_q = Q(icd9_codes__code__startswith='634.')
        self.abortion_q = (
            Q(icd9_codes__code__startswith='635.') |
            Q(icd9_codes__code__startswith='636.') |
            Q(icd9_codes__code__startswith='637.') |
            Q(icd9_codes__code__startswith='639.')
            )
        #
        # Complications of pregnancy with delivery
        #
        self.delivery_complications_q = (
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
        self.delivery_normal_q = (
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
        self.complications_q = (
            Q(icd9_codes__code__startswith='660.') |
            Q(icd9_codes__code__startswith='661.') |
            Q(icd9_codes__code__startswith='662.') |
            Q(icd9_codes__code__startswith='663.') |
            Q(icd9_codes__code__startswith='664.') |
            Q(icd9_codes__code__startswith='665.') |
            Q(icd9_codes__code__startswith='666.') |
            Q(icd9_codes__code__startswith='667.') |
            Q(icd9_codes__code__startswith='668.') |
            Q(icd9_codes__code__startswith='669.') 
            )
        #
        # Outcome of Delivery
        #
        self.delivery_outcome_q = Q(icd9_codes__code__startswith='V27.')  
        #
        # End of Pregnancy (EoP)
        #
        #self.eop_qs = Encounter.objects.filter(preg_end_q)
        #
        # Relevant encounters
        #
        self.all_eop_qs = Encounter.objects.filter(
            self.postpartum_q
            | self.ectopic_molar_q
            | self.spontaneous_abortion_q
            | self.abortion_q
            | self.delivery_complications_q
            | self.delivery_normal_q
            | self.delivery_outcome_q
            | self.complications_q
            )
        self.relevant_enc_qs = self.edd_qs | self.preg_icd9_qs | self.all_eop_qs
        
    def generate(self):
        log.info('Generating pregnancy events')
        #
        # Get possible patients
        #
        unbound_onset_qs = self.onset_qs.exclude(timespan__name='pregnancy')
        patient_pks = unbound_onset_qs.order_by('patient').values_list('patient', flat=True).distinct()
        log_query('Pregnant patient PKs', patient_pks)
        funcs = [partial(self.pregnancies_for_patient, patient_pk) for patient_pk in patient_pks]
        ts_count = wait_for_threads(funcs)
        return ts_count
    
    @transaction.commit_on_success
    def pregnancies_for_patient(self, patient_pk):
        log.debug('Examining patient #%s for pregnancy' % patient_pk)
        patient = Patient.objects.get(pk=patient_pk)
        counter = 0
        today = datetime.date.today()
        while True:
            onset_date = None
            eop_date = None
            pattern = None
            #
            # Find the first encounter with an ICD9 for pregnancy, that is not already
            # bound to a pregnancy timespan.
            #
            preg_qs = self.preg_icd9_qs.filter(patient=patient)
            preg_qs = preg_qs.exclude(timespan__name='pregnancy')
            preg_qs = preg_qs.order_by('date')
            #
            # If there are no unbound pregnancy encounters, we are done with this patient
            #
            if not preg_qs:
                break
            first_preg_event = preg_qs[0]
            #
            # Determine if there is a plausible EDD within 280 days after 
            # first pregnancy ICD9 date
            #
            first_preg_icd9_date = first_preg_event.date
            edd_qs = self.edd_qs.filter(patient=patient)
            edd_qs = edd_qs.exclude(timespan__name='pregnancy')
            edd_qs = edd_qs.filter(edd__gte=first_preg_icd9_date)
            edd_qs = edd_qs.filter( edd__lte = first_preg_icd9_date + relativedelta(days=280) )
            min_edd = edd_qs.aggregate(Min('edd'))['edd__min']
            #
            # Pregnancy onset is earliest plausible EDD minus 280 days.  If 
            # no EDD, then it is 30 days prior to first ICD9 for pregnancy.
            #
            if min_edd:
                onset_date = min_edd - relativedelta(days=280)
                pattern = 'onset:edd '
            else:
                onset_date = first_preg_icd9_date - relativedelta(days=30)
                pattern = 'onset:icd9 '
            #
            # Is patient currently pregnant?  If so, we should not expect to
            # find an EoP event just yet.
            #
            
            #
            # Find an End of Pregnancy event.  
            #
            eop_event_date = None
            eop_date_limit = onset_date + relativedelta(days=280) + relativedelta(days=30)
            eop_qs = self.all_eop_qs.filter(
                patient = patient,
                date__gte = onset_date,
                date__lte = eop_date_limit,
                ).order_by('-date')
            #
            # Sometimes EoP evenets are unreliabe; and some event types are 
            # known to be less reliable than others.  We will roll thru each
            # potential EoP event and see if there is a pregnancy ICD9 immediately
            # following it, which would suggest it's bogus.
            #
            for enc in eop_qs:
                #
                # It may be necessary to examine reliable and unreliable 
                # events differently.  However we will first try examining
                # them the same way, and change the code if need be.
                #
                subsequent_preg_icd9 = self.preg_icd9_qs.filter(
                    patient = patient,
                    date__gte = enc.date,
                    date__lte = enc.date + relativedelta(days=30)
                    )
                if subsequent_preg_icd9:
                    # If so, this EoP event is bogus, so we continue to the 
                    # next one
                    continue 
                else:
                    # This EoP event seems plausible.  Let's use its date.
                    eop_event_date = enc.date
                    eop_pattern = 'eop:eop_event'
                    break
            #
            # If plausible EoP event was found, use that for EoP date.
            if eop_event_date:
                eop_date = eop_event_date
                pattern += eop_pattern
            # Use EDD if available
            elif min_edd:
                eop_date = min_edd
                pattern += 'eop:min_edd '
            # Is this patient currently pregnant?  If so, null eop_date
            elif onset_date > (today - relativedelta(days=280)):
                eop_date = None
                pattern += 'eop:currently_pregnant'
            else:
                max_icd9_date = first_preg_icd9_date + relativedelta(days=280)
                this_preg_qs = preg_qs.filter(date__gte=onset_date)
                this_preg_qs = this_preg_qs.filter(date__lte=max_icd9_date)
                eop_date = this_preg_qs.aggregate(Max('date'))['date__max']
                pattern += 'eop:max_icd9 '
            #-------------------------------------------------------------------------------
            #
            # New Pregnancy
            #
            #-------------------------------------------------------------------------------
            #
            overlap_qs = Timespan.objects.filter(name='pregnancy')
            overlap_qs = overlap_qs.filter(patient=patient)
            if eop_date:
                overlap_qs = overlap_qs.filter( 
                    ( Q(start_date__lte=onset_date) & Q(end_date__gte=onset_date) ) 
                    |
                    ( Q(start_date__lte=eop_date) & Q(end_date__gte=eop_date) )
                    )
            else:
                overlap_qs = overlap_qs.filter( 
                    ( Q(start_date__lte=onset_date) & Q(end_date__gte=onset_date) ) 
                    |
                    ( Q(start_date__lte=today) & Q(end_date__gte=today) )
                    )
            overlap_qs = overlap_qs.order_by('pk')
            if overlap_qs:
                msg = 'Overlapping pregnancies!\n'
                msg += '    encounter: %s\n' % first_preg_event.verbose_str
                msg += '    proposed onset: %s\n' % onset_date
                msg += '    proposed eop: %s\n' % eop_date
                msg += '    proposed pattern: %s\n' % pattern
                for ts in overlap_qs:
                    msg += '    existing:  %s\n' % ts
                    for e in ts.encounters.all().order_by('date', 'pk'):
                        msg += '        %s\n' % e.verbose_str
                log.warning(msg)
                existing_preg = overlap_qs[0]
                existing_preg.encounters.add(first_preg_event)
                existing_preg.save()
                log.debug('Added overlap event %s to existing pregnancy %s' % (first_preg_event, existing_preg))
            else:
                new_preg = Timespan(
                    patient = patient,
                    name = 'pregnancy',
                    start_date = onset_date,
                    end_date = eop_date,
                    pattern = pattern,
                    source = self.uri,
                    )
                new_preg.save() # Must save before populating M2M
                relevant_encounters = self.relevant_enc_qs.filter(patient=patient)
                relevant_encounters = relevant_encounters.filter(date__gte=onset_date)
                if eop_date:
                    relevant_encounters = relevant_encounters.filter( date__lte=(eop_date + relativedelta(months=6)) )
                else:
                    relevant_encounters = relevant_encounters.filter( date__lte=today )
                new_preg.encounters = relevant_encounters
                new_preg.save()
                counter += 1
                log.info('Created new pregnancy: %s (%s)' % (new_preg, pattern))
        return counter
                

def get_timespan_heuristics():
    return [
        PregnancyHeuristic(),
        ]
