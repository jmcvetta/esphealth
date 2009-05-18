# Adverse events are indicated though reports of fever, lab results
# and icd9 codes that are present in patient encounters.

import optparse
import datetime

from django.db.models import Q

from ESP.hef.core import BaseHeuristic
from ESP.conf.common import EPOCH
from ESP.conf.models import Icd9
from ESP.esp.models import Demog, Immunization, Enc, Lx
from ESP.vaers.models import AdverseEvent
from ESP.vaers.models import EncounterEvent, LabResultEvent
from ESP.vaers.models import DiagnosticsEventRule
from ESP.utils.utils import log

import rules


LAB_TESTS_NAMES = rules.VAERS_LAB_RESULTS.keys()


class AdverseEventHeuristic(BaseHeuristic):
    def __init__(self, name, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name
        self.time_post_immunization = rules.TIME_WINDOW_POST_EVENT
        self._register(name)            
            
    


class VaersFeverHeuristic(AdverseEventHeuristic):
    def __init__(self):
        self.category = 'default'
        super(VaersFeverHeuristic, self).__init__(
            'VAERS Fever', verbose_name='Fever reaction to immunization')



    def matches(self, begin_date=None, end_date=None):
        # log.info('Getting matches for %s' % self.name)
        begin_date = begin_date or EPOCH
        end_date = end_date or datetime.date.today()

        # Can't use string to compare temperature
        encounters = Enc.objects.following_vaccination(
            rules.TIME_WINDOW_POST_EVENT, begin_date=begin_date, 
            end_date=end_date).exclude(EncTemperature='')

        return [e for e in encounters if 
                float(e.EncTemperature) >= rules.TEMP_TO_REPORT]
                    
            
            

    def generate_events(self, begin_date=None, end_date=None):
        log.info('Generating events for %s' % self.name)
        matches = self.matches(begin_date=begin_date, end_date=end_date)

        counter = 0
        rule_explain = 'Patient had %3.1f fever after immunization(s)'

        for e in matches:
            date = e.date
            fever_message = rule_explain % float(e.EncTemperature)
            # Create event instance
            ev, created = EncounterEvent.objects.get_or_create(
                category = self.category, date = date, encounter=e,
                defaults={'matching_rule_explain':fever_message}
                )
            
            if created: counter += 1

            # Register which immunizations may be responsible for the event
            for imm in Immunization.vaers_candidates(e.EncPatient, ev, 
                                                     self.time_post_immunization):
                ev.immunizations.add(imm)
                
                
            ev.save()

        return counter
        

class DiagnosisHeuristic(AdverseEventHeuristic):
    def __init__(self, name, icd9s, category, verbose_name=None, **kwargs):
        '''
        @type icd9s: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type discarding_icd9: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type ignored_if_past_occurrence: int
        @type verbose_name: String
        '''
                 
        self.icd9s = icd9s
        self.category = category
        self.discarding_icd9s = kwargs.pop('discarding_icd9s', [])
        self.ignored_if_past_occurrence = kwargs.pop(
            'ignored_if_past_occurrence', None)
        
        super(DiagnosisHeuristic, self).__init__(name, verbose_name=verbose_name)
            
    def matches(self, begin_date=None, end_date=None):
 #       log.info('Getting matches for %s' % self.name)
        begin_date = begin_date or EPOCH
        end_date = end_date or datetime.date.today()
        
        candidates = Enc.objects.following_vaccination(
            rules.TIME_WINDOW_POST_EVENT, 
            begin_date=begin_date, end_date=end_date).filter(
            reported_icd9_list__in=self.icd9s)


        if self.discarding_icd9s:
            candidates = [x for x in candidates if not 
                          x.EncPatient.has_history_of(self.discarding_icd9s, 
                                                      end_date=end_date)]

        if self.ignored_if_past_occurrence:
            months = self.ignored_if_past_occurrence
            candidates = [x for x in candidates 
                          if not x.is_reoccurrence(month_period=months)]

        return candidates


    def generate_events(self, begin_date=None, end_date=None):
        log.info('Generating events for %s' % self.name)
        counter = 0
        matches = self.matches(begin_date=begin_date, end_date=end_date)
        for e in matches:
            # Create event instance
            ev, created = EncounterEvent.objects.get_or_create(
                encounter=e, date=e.date, category=self.category,
                defaults={'matching_rule_explain':self.verbose_name}
                )

            if created: counter +=1

            # Register which immunizations may be responsible for the event
            for imm in Immunization.vaers_candidates(e.EncPatient, ev, 
                                                     self.time_post_immunization):
                ev.immunizations.add(imm)
                            
            ev.save()

        return counter

class VaersLxHeuristic(AdverseEventHeuristic):
    def __init__(self, name, loinc, criterium, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name
        self.loinc = loinc
        self.criterium = criterium
        self.verbose_name = verbose_name
        self._register(name)

    def matches(self, begin_date=None, end_date=None):
        
        begin = (begin_date or EPOCH).strftime('%Y%m%d')
        end = (end_date or datetime.date.today()).strftime('%Y%m%d')
        days = rules.TIME_WINDOW_POST_EVENT

        def is_trigger_value(lx, trigger):
            try:
                value = lx.result_float or lx.result_string or None
                v = float(value)
                to_compare = trigger.replace('X', str(v))
                return eval(to_compare)
            except:
#                log.warning('Lab Result %s has no value to be analyzed' % lx)
                return False
            

        def excluded_due_to_history(lx, comparator, baseline):
            try:
                
                lkv = lx.last_known_value(self.loinc)
                if not lkv: return False
                
                current_value = lx.result_float or lx.result_string or None
                
                assert float(current_value)
                assert float(lkv)
                
                equation = ' '.join(
                    [str(current_value), comparator, baseline.replace('LKV', str(lkv))])

                return eval(equation)
            except:
#                log.warning('Could not find LKV for Lab Result %s' % lx)
                return False
                
                
        trigger = self.criterium['trigger']
        comparator, baseline = self.criterium['exclude_if']

     

        candidates = Lx.objects.following_vaccination(days, loinc=self.loinc).filter(
            LxDate_of_result__gte=begin, LxDate_of_result__lte=end)
        
        

        return [c for c in candidates if is_trigger_value(c, trigger) and not 
                excluded_due_to_history(c, comparator, baseline)]

    
    def generate_events(self, begin_date=None, end_date=None):
        log.info('Generating events for %s' % self.name)
        counter = 0

        matches = self.matches(begin_date=begin_date, end_date=end_date)

        for lab_result in matches:
            result = lab_result.result_float or lab_result.result_string
            
            date = utils.date_from_str(lab_result.LxDate_of_result)
            rule_explain = 'Lab Result for %s resulting in %s'% (self.name, result)
            
            ev, created = LabResultEvent.objects.get_or_create(
                lab_result=lab_result,
                category=self.criterium['category'],
                date=date,
                defaults = {'matching_rule_explain': rule_explain}
                )
            
            if created: counter += 1
            
            # Register which immunizations may be responsible for the event
            for imm in Immunization.vaers_candidates(
                lab_result.LxPatient, ev, self.time_post_immunization):
                ev.immunizations.add(imm)
                
            ev.save()


        return counter


 

def detect_lab_results(immunization, time_window):
    patient = immunization.ImmPatient
    end_date = datetime.datetime.strptime(immunization.ImmDate, '%Y%m%d') + time_window

    def is_trigger_value(component_name, value, unit):
        # rules.VAERS_LAB_RESULTS is a dictionary with the information
        # that defines what constitutes a Adverse Event. 

        lab_test = rules.VAERS_LAB_RESULTS.get(component_name.lower(), [])
        for rule in lab_test:
            # The value from "trigger" is a equation from the
            # thresold. We take this equation and eval it, to see if the
            # value in the Lx is good or not.
            to_compare = rule['trigger'].replace('X', str(value))
            passes_trigger = eval(to_compare)
            if passes_trigger and (unit.lower() == rule['unit'].lower()):
                return rule
        
        return None

    def excluding_lkv_rule(lx):
        # Some values may be out of the safe thresolds, but we discard
        # the case as an adverse event if we have a previous lx that
        # shows that the component value has already been "worse". 

        # "exclude_if" is a entry in rules.VAERS_LAB_RESULTS that has
        # is tipically in the form "X cmp LKV factor", cmp being a
        # comparison operator, and factor being a multiplier or addition.

        lab_test = rules.VAERS_LAB_RESULTS.get(lx.LxComponentName.lower(),
                                               [])

        return any([lx.compared_to_lkv(*r['exclude_if']) for r in lab_test])

    lab_results = Lx.objects.filter(
        LxPatient=patient,
        LxOrderDate__gte=immunization.ImmDate,
        LxOrderDate__lte=end_date.strftime('%Y%m%d'),
        LxComponentName__in=[name.upper() for name in LAB_TESTS_NAMES]
        )


    detected = []
    for lx in lab_results:
        cpt = lx.LxComponentName
        v, unit = float(lx.LxTest_results), lx.LxReference_Unit
        trigger_rule = is_trigger_value(cpt, v, unit)
        if trigger_rule and not excluding_lkv_rule(lx):
            explanation = 'Lx for %s resulting in %s%s' % (cpt, v, unit)
            ev, new = LabResultEvent.objects.get_or_create(
                patient=patient,
                lab_result=lx,
                immunization=immunization,
                category=trigger_rule['category'],
                defaults = {'matching_rule_explain': explanation}
                )
            
            detected.append(ev)
        
    return detected


def events_caused(immunizations, only=None):
    # Given a list of immunization objects, returns a list of all Events 
    # that were caused by them.
    
    interval = datetime.timedelta(days=rules.TIME_WINDOW_POST_EVENT)
    
    actions = { 'fevers':detect_fevers,
                'diagnostics':detect_diagnostics,
                'lab_results':detect_lab_results
                }

    all_events = []

    for imm in immunizations:
        if only in actions:
            imm_events = actions[only](imm, interval)
        else:
            imm_events = detect_fevers(imm, interval) + detect_diagnostics(imm, interval) + detect_lab_results(imm, interval)


        if imm_events:
            all_events.extend(imm_events)
        

    return all_events




def make_diagnosis_heuristic(name):
    '''
    @type name: string
    '''
    
    rule = DiagnosticsEventRule.objects.get(name=name)
    verbose_name = '%s as an adverse reaction to immunization' % name
    icd9s = rule.heuristic_defining_codes.all()
    category = rule.category

    d = {'ignored_if_past_occurrence':rule.ignored_if_past_occurrence,
         'discarding_icd9s': rule.heuristic_discarding_codes.all(),
        }

    return DiagnosisHeuristic(name, icd9s, category, verbose_name, **d)

def make_lab_heuristics(loinc):
    rule = rules.VAERS_LAB_RESULTS[loinc]

    name = rule['name']
    verbose_name = 'Lab Result testing for %s showing adverse reaction to immunization' % name

    return [
        VaersLxHeuristic(name, loinc, criterium, verbose_name=verbose_name)
        for criterium in rule['criteria']]
        


        
def fever_heuristic():
    return VaersFeverHeuristic()

def diagnostic_heuristics():
    return [make_diagnosis_heuristic(v['name'])
            for v in rules.VAERS_DIAGNOSTICS.values()]

def lab_heuristics():
    hs = []
    for loinc in rules.VAERS_LAB_RESULTS.keys():
        for heuristic in make_lab_heuristics(loinc):
            hs.append(heuristic)

    return hs



if __name__ == '__main__':
    all_heuristics = vaers_heuristics()
    today = datetime.datetime.today()
    a_month_ago = today - datetime.timedelta(days=30)
    BaseHeuristic.generate_all_events(begin_date=a_month_ago, end_date=today)
    
    
        
