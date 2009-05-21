# Adverse events are indicated though reports of fever, lab results
# and icd9 codes that are present in patient encounters.

import optparse
import datetime

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from ESP.hef.core import BaseHeuristic
from ESP.conf.common import EPOCH
from ESP.conf.models import Icd9
from ESP.esp.models import Demog, Immunization, Enc, Lx
from ESP.vaers.models import AdverseEvent
from ESP.vaers.models import EncounterEvent, LabResultEvent
from ESP.vaers.models import DiagnosticsEventRule
from ESP.utils.utils import log, date_from_str

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
        encounter_type = ContentType.objects.get_for_model(EncounterEvent)

        counter = 0
        rule_explain = 'Patient had %3.1f fever after immunization(s)'

        for e in matches:
            date = e.date
            fever_message = rule_explain % float(e.EncTemperature)

            try:
                # Create event instance
                ev, created = EncounterEvent.objects.get_or_create(
                    category = self.category, date = date, encounter=e,
                    defaults={'matching_rule_explain':fever_message,
                              'content_type': encounter_type}
                    )
            
                if created: counter += 1
            
                ev.save()

                ev.immunizations.clear()

                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(
                    e.EncPatient, ev, self.time_post_immunization)
                
                assert len(immunizations) > 0 


                for imm in immunizations:
                    ev.immunizations.add(imm)

                ev.save()

            except AssertionError:
                log.error('No candidate immunization for Encounter %s' % e)
                log.warn('Deleting event %s' % ev)
                ev.delete()
                counter -= 1
            

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
        encounter_type = ContentType.objects.get_for_model(EncounterEvent)

        for e in matches:
            try:

                # Create event instance
                ev, created = EncounterEvent.objects.get_or_create(
                    encounter=e, date=e.date, category=self.category,
                    defaults={'matching_rule_explain':self.verbose_name,
                              'content_type':encounter_type}
                    )

                if created: counter +=1

                ev.save()
                ev.immunizations.clear()

                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(
                    e.EncPatient, ev, self.time_post_immunization)
                
                assert len(immunizations) > 0
                for imm in immunizations:
                    ev.immunizations.add(imm)

                # All immunizations are ok.
                ev.save()

            except AssertionError:
                log.error('No candidate immunization for Encounter %s' % e)
                log.warn('Deleting event %s' % ev)
                ev.delete()
                counter -= 1
                
                

                            


        return counter

class VaersLxHeuristic(AdverseEventHeuristic):
    def __init__(self, name, loinc, criterium, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name
        self.loinc = loinc
        self.criterium = criterium
        self.verbose_name = verbose_name
        self._register(name)
        self.time_post_immunization = rules.TIME_WINDOW_POST_EVENT

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

        lab_type = ContentType.objects.get_for_model(LabResultEvent)

        for lab_result in matches:
            try:
                
                result = lab_result.result_float or lab_result.result_string
                date = date_from_str(lab_result.LxDate_of_result)
                rule_explain = 'Lab Result for %s resulting in %s'% (self.name, result)
            
                ev, created = LabResultEvent.objects.get_or_create(
                    lab_result=lab_result,
                    category=self.criterium['category'],
                    date=date,
                    defaults = {'matching_rule_explain': rule_explain,
                                'content_type':lab_type}
                    )
                
                if created: counter += 1

                ev.save()
                ev.immunizations.clear()

                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(
                    lab_result.LxPatient, ev, self.time_post_immunization)

                assert len(immunizations) > 0

                for imm in immunizations:
                    ev.immunizations.add(imm)
                
                ev.save()

            except AssertionError:
                log.error('No candidate immunization for LabResult %s' % lab_result)
                log.warn('Deleting event %s' % ev)
                ev.delete()
                counter -= 1

        return counter

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


def init_vaers_heuristics():
    '''Just a method to instantiate all of the heuristics'''
    fever_heuristic()
    diagnostic_heuristics()
    lab_heuristics()
    


if __name__ == '__main__':
    init_vaers_heuristics()
    today = datetime.datetime.today()
    a_month_ago = today - datetime.timedelta(days=30)
    BaseHeuristic.generate_all_events(begin_date=EPOCH, end_date=today)
    
    
        
