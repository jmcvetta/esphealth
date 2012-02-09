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
from ESP.hef.base import Event
from ESP.hef.base import BaseEventHeuristic
from ESP.hef.base import BaseTimespanHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import Icd9Query
from ESP.hef.models import Timespan


from ESP.utils.utils import TODAY

#PREG_START_MARGIN = datetime.timedelta(days=20)
PREG_MARGIN = relativedelta(days=30)


class EDDHeuristic(BaseEventHeuristic):
    
    event_names = ['enc:pregnancy:edd',]
    
    uri = 'urn:x-esphealth:heuristic:channing:encounter:edd:v1'
    
    core_uris = ['urn:x-esphealth:hef:core:v1']
    
    short_name = 'enc:pregnancy:edd'
    
    def generate(self):
        counter = 0
        enc_qs = Encounter.objects.filter(edd__isnull=False)
        enc_qs = enc_qs.exclude(events__name__in=self.event_names)
        log_query('EDD Encounters for %s' % self.uri, enc_qs)
        for this_enc in enc_qs:
            Event.create(
                name = 'enc:pregnancy:edd',
                source = self.uri, 
                date = this_enc.date, 
                patient = this_enc.patient, 
                provider = this_enc.provider,
                emr_record = this_enc
                )
            counter += 1
        log.info('Generated %s new %s events' % (counter, self.uri))
        return counter

    

class PregnancyHeuristic(BaseTimespanHeuristic):
    
    short_name = 'timespan:pregnancy'
    
    uri = 'urn:x-esphealth:heuristic:channing:timespan:pregnancy:v1'
    
    core_uris = ['urn:x-esphealth:hef:core:v1']
    
    timespan_names = ['pregnancy', 'postpartum',]
    
    today = datetime.date.today()
    
    @property
    def event_heuristics(self):
        heuristics = []
        #-------------------------------------------------------------------------------
        #
        # Onset
        #
        #-------------------------------------------------------------------------------
        #
        # EDD
        #
        heuristics.append( EDDHeuristic() )
        #
        # ICD9
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:onset',
            icd9_queries = [
                Icd9Query(starts_with = 'V22.'),
                Icd9Query(starts_with = 'V23.'),
                ]
            ) )
        #-------------------------------------------------------------------------------
        #
        # End of Pregnancy
        #
        #-------------------------------------------------------------------------------
        #
        # Postpartum care
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:postpartum-care',
            icd9_queries = [
                Icd9Query(starts_with = 'V24.'),
                ]
            ) )
        #
        # Ectopic & molar pregnancy
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:ectopic-molar',
            icd9_queries = [
                Icd9Query(starts_with = '630.'),
                Icd9Query(starts_with = '631.'),
                Icd9Query(starts_with = '632.'),
                Icd9Query(starts_with = '633.'),
                ]
            ) )
        #
        # Abortion
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:abortion-spontaneous',
            icd9_queries = [
                Icd9Query(starts_with = '634.'),
                ]
            ) )
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:abortion',
            icd9_queries = [
                Icd9Query(starts_with = '635.'),
                Icd9Query(starts_with = '636.'),
                Icd9Query(starts_with = '637.'),
                # No 638.?
                Icd9Query(starts_with = '639.'),
                ]
            ) )
        #
        # Complications of pregnancy with delivery
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:delivery-complications',
            icd9_queries = [
                Icd9Query(starts_with = '640.', ends_with = '1'),
                Icd9Query(starts_with = '641.', ends_with = '1'),
                Icd9Query(starts_with = '642.', ends_with = '1'),
                Icd9Query(starts_with = '643.', ends_with = '1'),
                Icd9Query(starts_with = '644.', ends_with = '1'),
                Icd9Query(starts_with = '645.', ends_with = '1'),
                Icd9Query(starts_with = '646.', ends_with = '1'),
                Icd9Query(starts_with = '647.', ends_with = '1'),
                Icd9Query(starts_with = '648.', ends_with = '1'),
                Icd9Query(starts_with = '649.', ends_with = '1'),
                Icd9Query(starts_with = '640.', ends_with = '2'),
                Icd9Query(starts_with = '641.', ends_with = '2'),
                Icd9Query(starts_with = '642.', ends_with = '2'),
                Icd9Query(starts_with = '643.', ends_with = '2'),
                Icd9Query(starts_with = '644.', ends_with = '2'),
                Icd9Query(starts_with = '645.', ends_with = '2'),
                Icd9Query(starts_with = '646.', ends_with = '2'),
                Icd9Query(starts_with = '647.', ends_with = '2'),
                Icd9Query(starts_with = '648.', ends_with = '2'),
                Icd9Query(starts_with = '649.', ends_with = '2'),
                Icd9Query(starts_with = '640.', ends_with = '4'),
                Icd9Query(starts_with = '641.', ends_with = '4'),
                Icd9Query(starts_with = '642.', ends_with = '4'),
                Icd9Query(starts_with = '643.', ends_with = '4'),
                Icd9Query(starts_with = '644.', ends_with = '4'),
                Icd9Query(starts_with = '645.', ends_with = '4'),
                Icd9Query(starts_with = '646.', ends_with = '4'),
                Icd9Query(starts_with = '647.', ends_with = '4'),
                Icd9Query(starts_with = '648.', ends_with = '4'),
                Icd9Query(starts_with = '649.', ends_with = '4'),
                ]
            ) )
        #
        # Normal delivery
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:delivery-normal',
            icd9_queries = [
                Icd9Query(starts_with = '650.', ends_with = '1'),
                Icd9Query(starts_with = '651.', ends_with = '1'),
                Icd9Query(starts_with = '652.', ends_with = '1'),
                Icd9Query(starts_with = '653.', ends_with = '1'),
                Icd9Query(starts_with = '654.', ends_with = '1'),
                Icd9Query(starts_with = '655.', ends_with = '1'),
                Icd9Query(starts_with = '656.', ends_with = '1'),
                Icd9Query(starts_with = '657.', ends_with = '1'),
                Icd9Query(starts_with = '658.', ends_with = '1'),
                Icd9Query(starts_with = '659.', ends_with = '1'),
                Icd9Query(starts_with = '650.', ends_with = '2'),
                Icd9Query(starts_with = '651.', ends_with = '2'),
                Icd9Query(starts_with = '652.', ends_with = '2'),
                Icd9Query(starts_with = '653.', ends_with = '2'),
                Icd9Query(starts_with = '654.', ends_with = '2'),
                Icd9Query(starts_with = '655.', ends_with = '2'),
                Icd9Query(starts_with = '656.', ends_with = '2'),
                Icd9Query(starts_with = '657.', ends_with = '2'),
                Icd9Query(starts_with = '658.', ends_with = '2'),
                Icd9Query(starts_with = '659.', ends_with = '2'),
                Icd9Query(starts_with = '650.', ends_with = '4'),
                Icd9Query(starts_with = '651.', ends_with = '4'),
                Icd9Query(starts_with = '652.', ends_with = '4'),
                Icd9Query(starts_with = '653.', ends_with = '4'),
                Icd9Query(starts_with = '654.', ends_with = '4'),
                Icd9Query(starts_with = '655.', ends_with = '4'),
                Icd9Query(starts_with = '656.', ends_with = '4'),
                Icd9Query(starts_with = '657.', ends_with = '4'),
                Icd9Query(starts_with = '658.', ends_with = '4'),
                Icd9Query(starts_with = '659.', ends_with = '4'),
                ]
            ) )
        #
        # Complications of labor
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:labor-complications',
            icd9_queries = [
                Icd9Query(starts_with = '660.'),
                Icd9Query(starts_with = '661.'),
                Icd9Query(starts_with = '662.'),
                Icd9Query(starts_with = '663.'),
                Icd9Query(starts_with = '664.'),
                Icd9Query(starts_with = '665.'),
                Icd9Query(starts_with = '666.'),
                Icd9Query(starts_with = '667.'),
                Icd9Query(starts_with = '668.'),
                Icd9Query(starts_with = '669.'),
                ]
            ) )
        #
        # Outcome of Delivery
        #
        heuristics.append( DiagnosisHeuristic(
            name = 'pregnancy:delivery-outcome',
            icd9_queries = [
                Icd9Query(starts_with = 'V27.'),
                ]
            ) )
        return heuristics
    
    def __init__(self):
        #
        # EDD Encounters
        #
        self.edd_qs = Event.objects.filter(name='enc:pregnancy:edd')
        #
        # Onset
        #
        self.onset_qs = Event.objects.filter(name='dx:pregnancy:onset')
        #
        # End of Pregnancy
        #
        self.all_eop_qs = Event.objects.filter(name__in=[
            'dx:pregnancy:postpartum',
            'dx:pregnancy:ectopic-molar',
            'dx:pregnancy:abortion-spontaneous',
            'dx:pregnancy:abortion',
            'dx:pregnancy:delivery-complications',
            'dx:pregnancy:delivery-normal',
            'dx:pregnancy:delivery-outcome',
            'dx:pregnancy:complications',
            ])
        #
        # All Relevant Events
        self.relevant_event_qs = self.edd_qs | self.onset_qs | self.all_eop_qs
        
    @transaction.commit_on_success
    def generate(self):
        self._update_currently_pregnant()
        return self._generate_new_pregnanies()
    
    def _update_currently_pregnant(self):
        '''
        Update currently-pregnant timespans.
        @return: Count of timespans updated
        @retype: Integer
        '''
        counter = 0
        log.info('Checking currently-pregnant patients for EoP')
        cur_preg_qs = Timespan.objects.filter(name='pregnancy', end_date=None)
        unbound_eop_patients = self.all_eop_qs.exclude(timespan__name='pregnancy').values('patient').distinct()
        cur_preg_qs = cur_preg_qs.filter(patient__in=unbound_eop_patients)
        log_query('Currently pregnant patients with an unbound EoP event', cur_preg_qs)
        total = cur_preg_qs.count()
        counter = 0
        for ts in cur_preg_qs:
            counter += 1
            log.debug('Checking currently pregnant patient %20s / %s' % (counter, total))
            eop_event = self._get_eop_event(ts.patient, ts.start_date)
            edd = self._get_edd(ts.patient, ts.start_date)
            if eop_event:
                ts.end_date = eop_event.date
                ts.events.add(eop_event)
                pattern = 'eop:eop_event'
            elif edd:
                ts.end_date = edd
                pattern = 'eop:edd'
            elif ts.start_date < ( self.today - relativedelta(days=280) ):
                ts.end_date = self._get_latest_preg_event_date(ts.patient, ts.start_date)
                pattern = 'eop:max_icd9'
            else:
                continue # Nothing to do here, let's move on
            ts.pattern = ts.pattern + ' ' + pattern
            ts.save()
            counter += 1
            log.debug('Updated %s with end_date %s' % (ts, ts.end_date))
            self._attach_relevant_events(ts)
        log.info('Updated %s currently-pregnant timespans with end dates.' % counter)
        return counter
        
    def _generate_new_pregnanies(self):
        log.info('Generating new pregnancy timespans')
        #
        # Get possible patients for new pregnancies
        #
        # Potential pregnancies require either an onset event, or an EDD encounter (from 
        # which an implied onset date can be calculated).
        preg_indicator_qs = self.onset_qs | self.edd_qs
        preg_indicator_qs = preg_indicator_qs.exclude(timespan__name='pregnancy')
        patient_pks = preg_indicator_qs.order_by('patient').values_list('patient', flat=True).distinct()
        log_query('Pregnant patient PKs', patient_pks)
        total = len(patient_pks)
        counter = 0
        funcs = []
        for patient_pk in patient_pks:
            counter += 1
            f = partial(self.pregnancies_for_patient, patient_pk, counter, total) 
            funcs.append(f)
        ts_count = wait_for_threads(funcs)
        return ts_count
    
    def _get_eop_event(self, patient, onset_date):
        '''
        Finds a plausible End of Pregnancy event, given a patient and the 
            date of pregnancy onset.
        @param patient: The patient to be considered
        @type patient: ESP.emr.models.Patient
        @param onset_date: Onset date for this episode of pregnancy
        @type onset_date: Date
        @return: The first plausible EoP event for this pregnancy if 
            found; or None if no plausible EoP found
        @rtype: Event or None
        '''
        #
        # Find an End of Pregnancy event.  
        #
        eop_event_date = None
        eop_date_limit = onset_date + relativedelta(days=280) + relativedelta(days=30)
        eop_event_qs = self.all_eop_qs.filter(
            patient = patient,
            date__gte = onset_date,
            date__lte = eop_date_limit,
            ).order_by('date')
        #
        # Sometimes EoP events are unreliable; and some event types are 
        # known to be less reliable than others.  We will roll thru each
        # potential EoP event and see if there is a pregnancy ICD9 immediately
        # following it, which would suggest it's bogus.
        #
        for this_event in eop_event_qs:
            #
            # It may be necessary to examine reliable and unreliable 
            # events differently.  However we will first try examining
            # them the same way, and change the code if need be.
            #
            subsequent_preg_event_qs = self.relevant_event_qs.filter(
                patient = patient,
                date__gte = this_event.date,
                date__lte = this_event.date + relativedelta(days=30)
                )
            if subsequent_preg_event_qs:
                # If so, this EoP event is bogus, so we continue to the 
                # next one
                continue 
            else:
                # This EoP event seems plausible.  Let's use its date.
                return this_event
        return None
    
    def _get_edd(self, patient, start_date):
        '''
        Finds a plausible Estimated Date of Delivery given a patient and a 
            date to start looking.
        @param patient: Patient to consider
        @type patient: ESP.emr.models.Patient
        @param start_date: Look for EDD encounters after this date
        @type start_date: Date
        @return: A plausible EDD, if one exists
        @rtype: Date or None
        '''
        # TODO: kissue 348 Check with Mike Klompas about whether min EDD (as returned by 
        # existing code) or EDD of chronologically latest EDD-encounter is desired.
        edd_event_qs = Event.objects.filter(name='enc:pregnancy:edd')
        edd_event_qs = edd_event_qs.filter(patient=patient)
        edd_event_qs = edd_event_qs.exclude(timespan__name='pregnancy')
        edd_enc_qs = Encounter.objects.filter(events__in=edd_event_qs)
        edd_enc_qs = edd_enc_qs.filter(patient=patient)
        edd_enc_qs = edd_enc_qs.filter(edd__gte=start_date)
        edd_enc_qs = edd_enc_qs.filter( edd__lte = start_date + relativedelta(days=280) )
        aggregate_info_dict = edd_enc_qs.aggregate(Min('edd'))
        min_edd = aggregate_info_dict['edd__min']
        return min_edd
    
    def _get_latest_preg_event_date(self, patient, start_date):
        '''
        Finds a (probably not very reliable) end of pregnancy date based on
            the last pregnancy-relevant event that could reasonably be 
            attributed to a pregnancy starting at the given date
            date to start looking.
        @param patient: Patient to consider
        @type patient: ESP.emr.models.Patient
        @param start_date: Start of pregnancy
        @type start_date: Date
        @return: End of pregnancy date
        @rtype: Date
        '''
        max_icd9_date = start_date + relativedelta(days=280)
        preg_qs = self.relevant_event_qs.filter(patient=patient)
        preg_qs = preg_qs.exclude(timespan__name='pregnancy')
        preg_qs = preg_qs.filter(date__gte=start_date)
        preg_qs = preg_qs.filter(date__lte=max_icd9_date)
        max_icd9_date = preg_qs.aggregate(Max('date'))['date__max']
        return max_icd9_date
    
    @transaction.commit_on_success
    def pregnancies_for_patient(self, patient_pk, serial, total):
        '''
        Generate new pregnancy timespans for a given patient
        @param patient_pk: Primary key of Patient to be examined
        @type patient_pk: Integer
        @param serial: Serial counter for logging
        @type serial: Integer
        @param total: Total count of patients for logging
        @type total: Integer
        @return: Count of new pregnancies generated
        @rtype: Integer
        '''
        log.debug('Examining patient #%s for pregnancy (%20s / %s)' % (patient_pk, serial, total))
        patient = Patient.objects.get(pk=patient_pk)
        counter = 0
        while True:
            onset_date = None
            eop_date = None
            pattern = None
            #
            # Find the first encounter with an ICD9 for pregnancy, that is not already
            # bound to a pregnancy timespan.
            #
            preg_qs = self.relevant_event_qs.filter(patient=patient) 
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
            min_edd = self._get_edd(patient, first_preg_event.date)
            #
            # Pregnancy onset is earliest plausible EDD minus 280 days.  If 
            # no EDD, then it is 30 days prior to first ICD9 for pregnancy.
            #
            if min_edd:
                onset_date = min_edd - relativedelta(days=280)
                pattern = 'onset:edd '
            else:
                onset_date = first_preg_event.date - relativedelta(days=30)
                pattern = 'onset:icd9 '
            #
            # Find an End of Pregnancy event.  
            #
            # If patient is currently pregnant, we should not expect to
            # find an EoP event just yet.
            #
            eop_event = self._get_eop_event(patient, onset_date)
            if eop_event:
                eop_date = eop_event.date
                pattern += 'eop:eop_event'
            # Is this patient currently pregnant?  If so, null eop_date
            elif onset_date > (TODAY - relativedelta(days=280)):
                eop_date = None
                pattern += 'eop:currently_pregnant'
            # Use EDD if available
            elif min_edd:
                eop_date = min_edd
                pattern += 'eop:min_edd '
            #
            # Patient has no EoP event, is not currently pregnant, and has no EDD in
            # any encounter,  We know pregnancy has ended, but have no real way to 
            # infer the end of pregnancy date.  Therefore we look for the 
            # chronologically latest pregnancy-related ICD9 that falls within a 
            # plausible time window for this pregnancy, and use its date as the
            # end of pregnancy date.
            #
            else:
                max_icd9_date = first_preg_event.date + relativedelta(days=280)
                this_preg_qs = preg_qs.filter(date__gte=onset_date)
                this_preg_qs = this_preg_qs.filter(date__lte=max_icd9_date)
                eop_date = self._get_latest_preg_event_date(patient, onset_date)
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
                    ( Q(start_date__lte=TODAY) & Q(end_date__gte=TODAY) )
                    )
            overlap_qs = overlap_qs.order_by('pk')
            if overlap_qs:
                msg = 'Overlapping pregnancies!\n'
                msg += '    event: %s\n' % first_preg_event.verbose_str
                msg += '    proposed onset: %s\n' % onset_date
                msg += '    proposed eop: %s\n' % eop_date
                msg += '    proposed pattern: %s\n' % pattern
                for ts in overlap_qs:
                    msg += '    existing:  %s\n' % ts
                    for e in ts.events.all().order_by('date', 'pk'):
                        msg += '        %s\n' % e.verbose_str
                log.warning(msg)
                existing_preg = overlap_qs[0]
                existing_preg.events.add(first_preg_event)
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
                self._attach_relevant_events(new_preg)
                log.info('Created new timespan: #%s' % new_preg.pk)
                counter += 1
        return counter
    
    def _attach_relevant_events(self, preg_ts):
        relevant_events = self.relevant_event_qs.filter(patient=preg_ts.patient)
        relevant_events = relevant_events.filter(date__gte=preg_ts.start_date)
        if preg_ts.end_date:
            relevant_events = relevant_events.filter( date__lte=(preg_ts.end_date + relativedelta(months=6)) )
        else:
            relevant_events = relevant_events.filter( date__lte=self.today )
        preg_ts.events = preg_ts.events.all() | relevant_events
        preg_ts.save()
        return preg_ts
                
                
preg_heuristic = PregnancyHeuristic()

def timespan_heuristics():
    return [ preg_heuristic, ]


def event_heuristics():
    return preg_heuristic.event_heuristics

