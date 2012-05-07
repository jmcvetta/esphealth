# Adverse events are indicated though reports of fever, lab results
# and icd9 codes that are present in patient encounters.
import sys
import pdb
import optparse
import datetime

from dateutil.relativedelta import relativedelta

from django.db.models import Q, F, Max, Min
from django.contrib.contenttypes.models import ContentType
from ESP.settings import DATE_FORMAT
from ESP.hef.base import BaseHeuristic, BaseEventHeuristic
from ESP.conf.common import EPOCH
from ESP.static.models import Icd9, Allergen
from ESP.emr.models import Immunization, Encounter, LabResult,  Allergy
from ESP.emr.models import Prescription, Problem
from ESP.vaers.models import AdverseEvent, Case, PrescriptionEvent, EncounterEvent, LabResultEvent, AllergyEvent
from ESP.vaers.models import DiagnosticsEventRule
from ESP.vaers.models import ExcludedICD9Code, Questionaire
from ESP.vaers.rules import TIME_WINDOW_POST_EVENT
from ESP.utils.utils import log

import rules

VAERS_CORE_URI = 'urn:x-esphealth:vaers:core:v1'
LAB_TESTS_NAMES = rules.VAERS_LAB_RESULTS.keys()

USAGE_MSG = '''\
%prog [options]

    One or more of '-lx', '-f', '-d', '-p', '-g' or '-a' must be specified.
    
    DATE variables are specified in this format: 'YYYYMMDD'
'''

class AdverseEventHeuristic(BaseHeuristic):
    def __init__(self, event_name, verbose_name=None):
        self.time_post_immunization = rules.TIME_WINDOW_POST_EVENT
        assert event_name
        assert verbose_name
        self.name = event_name
        self.long_name = verbose_name
    
        #super(AdverseEventHeuristic, self).__init__(event_name, verbose_name)
        
    def update_or_create_case(self, immunization_qs, this_imm, new_event):
        # if there is an existing case for this event (immunization
        # and attach to it if not created one
        #  add to the case the list of prior vaccines within 42 days 
        # and update the date of last event added 
       
        prior_immunizations =  immunization_qs.filter(date__lt = this_imm.date)
        
        this_case, case_created = Case.objects.get_or_create(
                 date = this_imm.date,
                 patient = this_imm.patient
                )
        this_case.save()
        
        this_case.immunizations.add(this_imm)
        this_case.adverse_event.add(new_event)
        
        this_case.prior_immunizations = prior_immunizations
        this_case.save()
        
        #create questionaires for every physician in the events
        #TODO questionaire logic may need tuning , just needs delay of 1 day?
        for ae in this_case.adverse_event.all():
            prov  = ae.content_object.provider 
            this_q, created = Questionaire.objects.get_or_create(provider = prov,
                  case= this_case)
            if not created:
                continue
            
            this_q.save()
            this_q.create_digest()
           
            
    @property
    def core_uris(self):
        # Only this version of HEF is supported
        return [VAERS_CORE_URI]
    
    @property
    def short_name(self):
        return 'adverse event:%s' % self.name
        
            
class VaersFeverHeuristic(AdverseEventHeuristic):
    def __init__(self):
        self.category = '1_common'
        super(VaersFeverHeuristic, self).__init__(
            'VAERS Fever', verbose_name='Fever reaction to immunization')
        
    uri = 'urn:x-esphealth:heuristic:channing:vaersfever:v1'
      
    def vaers_heuristic_name(self):
        return 'VAERS: ' + self.name

    def matches(self, **kw):
        #raise NotImplementedError('Last run support no longer available.  This method must be refactored')
        incremental = kw.get('incremental', False)
        #begin = (incremental and last_run) or kw.get('begin_date') or EPOCH
        begin = (incremental ) or kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()

        log.info('Finding fever events from %s to %s' % (begin, end))
        
        return Encounter.objects.following_vaccination(rules.TIME_WINDOW_POST_EVENT).filter(
            temperature__gte=rules.TEMP_TO_REPORT, date__gte=begin, date__lte=end).distinct()

                    

    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        matches = self.matches(**kw)
        
        log.info('Found %d matches' % matches.count())
        
        content_type = ContentType.objects.get_for_model(Encounter)

        counter = 0
        rule_explain = 'Patient had %3.1f fever after immunization(s)'

        for e in matches:
            fever_message = rule_explain % float(e.temperature)

            try:
                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(
                    e.patient, e.date, self.time_post_immunization)
                assert len(immunizations) > 0 
               
               
                # Create event instance
                ev, created = EncounterEvent.objects.get_or_create(
                     date=e.date, object_id =e.pk, 
                    content_type = content_type,
                    patient=e.patient,
                    defaults={
                            'name': self.vaers_heuristic_name(),
                            'matching_rule_explain':fever_message,
                            'category': self.category, }
                    )
                
                    
                ev.save()
                ev.immunizations.clear()
                
                # Get time interval between immunization and event
                ev.gap = (e.date - min([i.date for i in immunizations])).days

                for imm in immunizations:
                    ev.immunizations.add(imm)

                ev.save()
                
                if created: 
                    counter += 1
                    
                self.update_or_create_case(immunizations, imm, ev)
                

            except AssertionError:
                log.error('No candidate immunization for Encounter %s' % e)
                log.warn('Deleting event %s' % ev)
                ev.delete()
                counter -= 1

        return counter
        
class VaersAllergyHeuristic(AdverseEventHeuristic):
    
    def __init__(self, event_name, rule, category, risk_period):
        '''
        @type rule: [keywords,   ...]
        @type risk_period: int
        @type category: String
        @type event_name: string
        '''
                 
        self.name = event_name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.keywords = rule['keywords']
        self.category = category
        self.time_post_immunization = risk_period
        
        super(VaersAllergyHeuristic, self).__init__(event_name, verbose_name=self.verbose_name)
            
    uri = 'urn:x-esphealth:heuristic:channing:vaersallergies:v1'
    
    def vaers_heuristic_name(self):
        return 'VAERS: allergies to ' + self.name
            
    def matches(self, **kw):
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        allergy_qs = Allergy.objects.following_vaccination(self.time_post_immunization)
        allergy_qs = allergy_qs.filter(date__gte=begin, date__lte=end)
        # patient's immunization is same as self.name (rule's name)
        allergy_qs = allergy_qs.filter(patient__immunization__name = self.name)
        allergy_qs = allergy_qs.distinct()
        return allergy_qs

    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        content_type = ContentType.objects.get_for_model(Allergy)
        #TODO exclusion allergies with keyword in self.keyworkds, prior to vaccination
        for this_allergy in self.matches(**kw):
            #earliest = this_allergy.date - relativedelta(months=12)
            #  earliest could be patient's dob?
                
            prior_allergy_qs = Allergy.objects.filter(
                    date__lt = this_allergy.date, 
                    #date__gte = earliest, 
                    name__in = self.keywords, 
                    # or description field 
                    patient = this_allergy.patient, 
                    
                )
            if prior_allergy_qs:
                continue # Prior allergy so ignore 
            
            immunization_qs = Immunization.vaers_candidates(this_allergy.patient, this_allergy.date, self.time_post_immunization)
            assert immunization_qs
            
            # create a new event for each immunization date 
            for imm in immunization_qs:
                # Create event instance
                new_ae, created = AllergyEvent.objects.get_or_create(
                    
                    object_id = this_allergy.pk, 
                    content_type = content_type,
                    date = this_allergy.date, 
                    patient = this_allergy.patient,
                    defaults={
                        'name': self.vaers_heuristic_name(),
                        'matching_rule_explain': 'allergy to '+self.name,
                        'category' : self.category,
                        },
                    )
                        
                new_ae.save() # Must save before adding to ManyToManyField
                # Get time interval between immunization and event
                new_ae.gap = (this_allergy.date - imm.date).days
                new_ae.immunizations.add(imm)
                new_ae.save()
                
                if created: 
                    counter +=1
                self.update_or_create_case(immunization_qs, imm, new_ae)
                
        return counter

class VaersDiagnosisHeuristic(AdverseEventHeuristic):
    def __init__(self, event_name, icd9s, category, ignore_period):
        '''
        @type icd9s: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type discarding_icd9: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type ignore_period: int
        @type verbose_name: String
        '''
                 
        self.name = event_name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.icd9s = icd9s
        self.category = category
        self.ignore_period = ignore_period
        
        
        super(VaersDiagnosisHeuristic, self).__init__(event_name, verbose_name=self.verbose_name)
            
    uri = 'urn:x-esphealth:heuristic:channing:vaersdx:v1'
    
    def vaers_heuristic_name(self):
        
        return 'VAERS: ' + self.name
            
    def matches(self, **kw):
        # the reports of AE are per immunization 
        # TODO check what does it do.
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        enc_qs = Encounter.objects.following_vaccination(self.time_post_immunization)
        enc_qs = enc_qs.filter(icd9_codes__in=self.icd9s.all())
        enc_qs = enc_qs.filter(date__gte=begin, date__lte=end)
        enc_qs = enc_qs.distinct()
        return enc_qs

    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        content_type = ContentType.objects.get_for_model(Encounter)
        for this_enc in self.matches(**kw):
            if self.ignore_period:
                earliest = this_enc.date - relativedelta(months=self.ignore_period)
                
                prior_enc_qs = Encounter.objects.filter(
                    date__lt = this_enc.date, 
                    date__gte = earliest, 
                    priority__lt = this_enc.priority,
                    encounter_type = this_enc.encounter_type,
                    patient = this_enc.patient,                     
                    icd9_codes__in = self.icd9s.all(),
                )
                if prior_enc_qs:
                    continue # Prior diagnosis so ignore 
                
                prior_problem_qs = Problem.objects.filter(
                    date__lt = this_enc.date, 
                    icd9__code__in = this_enc.icd9_codes.all(),
                    patient = this_enc.patient, 
                )
                if prior_problem_qs:
                    continue # prior problem so ignore 
                
            immunization_qs = Immunization.vaers_candidates(this_enc.patient, this_enc.date, self.time_post_immunization)
            assert immunization_qs
            # Create event instance
            # TODO set breakpoint to 289 see if we ever hit it
            # check why are we doing get or create and not just new ???
           
            #find the adverse event icd9 codes
            for code in self.icd9s:
                if code in this_enc.icd9_codes.all():
                    for enc_code in this_enc.icd9_codes.all():
                        if enc_code == code and not self.name.__contains__(' '+enc_code.code):
                            self.name += ' '+enc_code.code
            
            # create a new event for each immunization date 
            for imm in immunization_qs:
                        
                new_ee, created = EncounterEvent.objects.get_or_create(
                    
                    object_id = this_enc.pk,
                    content_type = content_type,
                    date = this_enc.date, 
                    patient = this_enc.patient,
                    defaults={
                        'name': self.vaers_heuristic_name(),
                        'matching_rule_explain': self.name ,
                        'category' : self.category, 
                        }
                    )
                    
                new_ee.save() # Must save before adding to ManyToManyField
                # Get time interval between immunization and event
                new_ee.gap = (this_enc.date - imm.date).days
                new_ee.immunizations.add(imm)
                new_ee.save()
                
                if created: 
                    counter +=1
                    
                self.update_or_create_case(immunization_qs, imm, new_ee)
            
        return counter

class Icd9CorrelatedHeuristic(VaersDiagnosisHeuristic):
    def __init__(self, event_name, icd9s, category, ignore_period, discarding_icd9s):
        self.discarding_icd9s = discarding_icd9s
        super(Icd9CorrelatedHeuristic, self).__init__(event_name, icd9s, category, ignore_period)
        
    def matches(self, **kw):
        matches = super(Icd9CorrelatedHeuristic, self).matches(**kw)
        valid_matches = []
        for this_match in matches:
            relevancy_begin = this_match.date - relativedelta(months=12)
            history = this_match.patient.has_history_of(
                self.discarding_icd9s, 
                begin_date=relevancy_begin, 
                end_date=this_match.date)
            if history:
                continue # Patient has a history of this problem, so we will skip it.
            valid_matches.append(this_match)
        return valid_matches 

class AnyOtherDiagnosisHeuristic(VaersDiagnosisHeuristic):
    '''
    Any diagnosis not covered by another heuristic, or included in 
    the ExcludedICD9Code table. Exclude if:
    1.Same code on patient's current problem list prior to this encounter 
    2.Encounter with same code in past 36 months
    3.Past medical history list with same code 
    '''
    
    uri = 'urn:x-esphealth:heuristic:channing:vaersany_other_dx:v1'
    
    def __init__(self):
        self.name = ' any_other_dx' # This is the EVENT name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.category = '3_possible'
        self.ignore_period = 36 # months
        super(VaersDiagnosisHeuristic, self).__init__(self.name, verbose_name=self.verbose_name)
            
    @property
    def icd9s(self):
        '''
        All ICD9s that are not covered by another heuristic and are not 
        included in the ExcludedICD9Code table.
        @rtype: Icd9 QuerySet
        '''
        covered_icd9_codes = DiagnosticsEventRule.objects.filter(heuristic_defining_codes__isnull=False).values('heuristic_defining_codes')
        excluded_icd9_codes = ExcludedICD9Code.objects.values('code')
        
        # TODO: Ask Mike K about whether correlated ICD9 codes should be included in this ignore list
        icd9_qs = Icd9.objects.exclude(code__in=covered_icd9_codes)
        icd9_qs = icd9_qs.exclude(code__in=excluded_icd9_codes)
        return icd9_qs


class VaersLxHeuristic(AdverseEventHeuristic):
    lkv= None
    lkd = None
    def __init__(self, event_name, lab_codes, criterion, pediatric):
        '''
        @param pediatric: Apply this heuristic to prediatric patients rather than adults?
        @type pediatric:  Bool (if false, apply to adults only)
        '''
        self.name = event_name
        self.lab_codes = lab_codes
        self.criterion = criterion
        self.time_post_immunization = rules.TIME_WINDOW_POST_EVENT
        self.pediatric = pediatric
        super(VaersLxHeuristic, self).__init__(self.name, self.name)

    uri = 'urn:x-esphealth:heuristic:channing:vaerslx:v1'
    
    def vaers_heuristic_name(self):
        return 'VAERS: ' + self.name

    def matches(self, **kw):
        
        def is_trigger_value(lx, trigger):
            try:
                value = lx.result_float or lx.result_string or None
                v = float(value)
                to_compare = trigger.replace('X', str(v))
                return eval(to_compare)
            except:
                return False
            

        def excluded_due_to_history(lx, comparator, baseline):
            try:
                
                self.lkv, self.lkd = lx.last_known_value()
                
                if not self.lkv: return False
                
                # could set it in another object 
                current_value = lx.result_float or lx.result_string or None
                
                assert float(current_value)
                assert float(self.lkv)
                
                equation = ' '.join([str(current_value), comparator, baseline.replace('LKV', str(self.lkv))])

                return eval(equation)
            except:
                return False

        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        days = rules.TIME_WINDOW_POST_EVENT
                
        trigger = self.criterion['trigger']
        comparator, baseline = self.criterion['exclude_if']

        candidates = LabResult.objects.following_vaccination(days).filter(
            native_code__in=self.lab_codes, date__gte=begin, date__lte=end).distinct()
        #
        # Pediatric: 3mo - 18yrs
        # Adult 18yrs +
        #
        now = datetime.datetime.now()
        
        if self.pediatric:
            candidates = candidates.filter(patient__date_of_birth__gt = now - relativedelta(years=18))
            candidates = candidates.filter(patient__date_of_birth__lte = now - relativedelta(months=3))
        else: # adult
            candidates = candidates.filter(patient__date_of_birth__lte = now - relativedelta(years=18))
        return [c for c in candidates if is_trigger_value(c, trigger) and not 
                excluded_due_to_history(c, comparator, baseline)]

    
    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        content_type = ContentType.objects.get_for_model(LabResult)
                        
        for lab_result in self.matches(**kw):
            try:
                result = lab_result.result_float or lab_result.result_string
                rule_explain =  'Lab %s resulting in %s'% (self.name, result)
                
                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(lab_result.patient,lab_result.date, self.time_post_immunization)
                assert len(immunizations) > 0
                
                # create a new event for each immunization date 
                for imm in immunizations:
                    
                    # TODO remove immunization from ae and have case object have the vacc etc 
                    ev, created = LabResultEvent.objects.get_or_create(
                                object_id =lab_result.pk,
                                content_type = content_type,
                                date=lab_result.date,
                                patient=lab_result.patient,
                                defaults = {
                                    'name': self.vaers_heuristic_name(),
                                    'matching_rule_explain': rule_explain,
                                    'category' : self.criterion['category'],
                                    },
                                )
                                    
                    ev.last_known_value = self.lkv
                    ev.last_known_date = self.lkd                        
                        
                    ev.save()
                   
                    # Get time interval between immunization and event
                    ev.gap = (lab_result.date - imm.date).days
                    ev.immunizations.add(imm)
                    ev.save()
    
                    if created: 
                        counter += 1
                   
                    self.update_or_create_case(immunizations, imm, ev)
                
            except AssertionError:
                log.error('No candidate immunization for LabResult %s' % lab_result)
                log.warn('Deleting event %s' % ev)
                ev.delete()
                counter -= 1
            
        log.info('Created %d events' % counter)

        return counter

class VaersRxHeuristic(AdverseEventHeuristic):
    
    
    def __init__(self, event_name, criterion):
        
        self.name = event_name
        self.criterion = criterion
        self.time_post_immunization = criterion['risk_period_days']
        super(VaersRxHeuristic, self).__init__(self.name, self.name)

    uri = 'urn:x-esphealth:heuristic:channing:vaersrx:v1'
    
    def vaers_heuristic_name(self):
        return 'VAERS: ' + self.name

    def matches(self, **kw):
               
        def excluded_due_to_history(rx):
            
            earliest = rx.date - relativedelta(months=12)
            prior_rx_qs = Prescription.objects.filter(
                    date__lt = rx.date, 
                    date__gte = earliest, 
                    patient = rx.patient,
                    name__in=self.name,
                )
            if prior_rx_qs:
                return True
            else:
                return False
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        days = self.criterion['risk_period_days']
                        
        candidates = Prescription.objects.following_vaccination(days).filter(
            date__gte=begin, date__lte=end).distinct()
        #considering upper case and none
        candidatesUpper = candidates.filter(name__contains=self.name.upper())
        candidates = candidates.filter(name__contains=self.name)
        candidates = candidatesUpper | candidates
        return  [c for c in candidates if not excluded_due_to_history(c)]

    
    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        
        #begin_date = kw.get('begin_date', None) or EPOCH
        #end_date = kw.get('end_date', None) or datetime.date.today()

        matches = self.matches(**kw)

        content_type = ContentType.objects.get_for_model(Prescription)

        for rx in matches:
            try:
                
                rule_explain = 'Prescription for %s'% (self.name)
                
                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(rx.patient, rx.date, self.time_post_immunization)
                assert len(immunizations) > 0
                
                # create a new event for each immunization date 
                for imm in immunizations:
                
                    ev, created = PrescriptionEvent.objects.get_or_create(
                            object_id =rx.pk,
                            content_type = content_type,
                            date=rx.date,
                            patient=rx.patient,
                            defaults = {
                                'name': self.vaers_heuristic_name(),
                                'matching_rule_explain': rule_explain,
                                'category' :self.criterion['category'],
                               },
                            )
                                        
                    ev.save()
                    ev.immunizations.clear()
    
                    # Get time interval between immunization and event
                    ev.gap = (rx.date - imm.date).days
                    ev.immunizations.add(imm)
                    ev.save()
                    
                    if created: 
                        counter += 1
                        
                    self.update_or_create_case(immunizations, imm, ev)

            except AssertionError:
                log.error('No candidate immunization for Prescription %s' % rx)
                log.warn('Deleting event %s' % ev)
                ev.delete()
                counter -= 1

        log.info('Created %d events' % counter)

        return counter


def make_diagnosis_heuristic(name):
    '''
    @type name: string
    '''
    
    rule = DiagnosticsEventRule.objects.get(name=name)
    icd9s = rule.heuristic_defining_codes.all()
    category = rule.category
    ignore_period = rule.ignore_period
    

    discarding_icd9s = rule.heuristic_discarding_codes.all()

    if discarding_icd9s:
        return Icd9CorrelatedHeuristic(name, icd9s, category, ignore_period, discarding_icd9s)
    else:
        return VaersDiagnosisHeuristic(name, icd9s, category, ignore_period)
    
def make_lab_heuristics(lab_type):
    rule = rules.VAERS_LAB_RESULTS[lab_type]

    def heuristic_name(criterion, lab_name):
        return '%s %s %s' % (lab_name, criterion['trigger'], criterion['unit'])
    heuristic_list = []
    for criterion in rule['criteria_adult']:
        h = VaersLxHeuristic(heuristic_name(criterion, lab_type), rule['codes'], criterion, pediatric=False)
        heuristic_list.append(h)
    for criterion in rule['criteria_pediatric']:
        h = VaersLxHeuristic(heuristic_name(criterion, lab_type), rule['codes'], criterion, pediatric=True)
        heuristic_list.append(h)
    return heuristic_list

def make_rx_heuristics(rx_type):
    rule = rules.VAERS_PRESCRIPTION[rx_type]
    
    def heuristic_name(criterion, rx_name):
        # possibly expand this if we add more attributes to the criterion for rx vaers
        # use criterion later?
        return '%s' % (rx_name)
   
    heuristic_list = []
    h = VaersRxHeuristic(heuristic_name(rule, rx_type),  rule)
    heuristic_list.append(h)
    return heuristic_list

def make_allergy_heuristics(allergy_type):
    
    def heuristic_name( allergy_name):
        
        return '%s' % (allergy_name)
        
    risk_period = rules.TIME_WINDOW_POST_EVENT
    #rule = AllergyEventRule.objects.get(name=allergy_type)
    rule = rules.VAERS_ALLERGIES[allergy_type]
   
    category =  '3_possible'
    heuristic_list = []
    h = VaersAllergyHeuristic(heuristic_name(allergy_type),rule, category, risk_period)
    heuristic_list.append(h)
    return  heuristic_list
        
def fever_heuristic():
    return VaersFeverHeuristic()

def diagnostic_heuristics():
    heuristic_list = []
    for v in rules.VAERS_DIAGNOSTICS.values():
        heuristic_list.append( make_diagnosis_heuristic(v['name']) )
    any_other = AnyOtherDiagnosisHeuristic()
    heuristic_list.append(any_other)
    return heuristic_list

def lab_heuristics():
    hs = []

    for lab_type in rules.VAERS_LAB_RESULTS.keys():
        for heuristic in make_lab_heuristics(lab_type):
            hs.append(heuristic)

    return hs

def prescription_heuristics():
    hs = []

    for rx_type in rules.VAERS_PRESCRIPTION.keys():
        for heuristic in make_rx_heuristics(rx_type):
            hs.append(heuristic)

    return hs

def allergy_heuristics():
    hs = []

    for allergy_type in rules.VAERS_ALLERGIES.keys():
        for heuristic in make_allergy_heuristics(allergy_type):
            hs.append(heuristic)

    return hs

