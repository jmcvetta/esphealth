# Adverse events are indicated though reports of fever, lab results
# and icd9 codes that are present in patient encounters.

import optparse
import datetime

from django.db.models import Q, Max
from django.contrib.contenttypes.models import ContentType

from ESP.hef.core import BaseHeuristic
from ESP.hef.models import Run
from ESP.conf.common import EPOCH
from ESP.static.models import Icd9
from ESP.emr.models import Immunization, Encounter, LabResult
from ESP.vaers.models import AdverseEvent
from ESP.vaers.models import EncounterEvent, LabResultEvent
from ESP.vaers.models import DiagnosticsEventRule
from ESP.utils.utils import log

import rules


LAB_TESTS_NAMES = rules.VAERS_LAB_RESULTS.keys()

USAGE_MSG = '''\
%prog [options]

    One or more of '-lx', '-f', '-d' or '-a' must be specified.
    
    DATE variables are specified in this format: '17-Mar-2009'
'''

class AdverseEventHeuristic(BaseHeuristic):
    def __init__(self, event_name, verbose_name=None):
        self.time_post_immunization = rules.TIME_WINDOW_POST_EVENT
        super(AdverseEventHeuristic, self).__init__(event_name, verbose_name)

        
            
class VaersFeverHeuristic(AdverseEventHeuristic):
    def __init__(self):
        self.category = 'auto'
        super(VaersFeverHeuristic, self).__init__(
            'VAERS Fever', verbose_name='Fever reaction to immunization')

    def matches(self, **kw):
        incremental = kw.get('incremental', False)
        
        last_run = Run.objects.filter(
            def_name=self.def_name, 
            status='s').aggregate(ts=Max('timestamp'))['ts']
        
        begin = (incremental and last_run) or kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()

        # Can't use string to compare temperature
        return Encounter.objects.following_vaccination(
            rules.TIME_WINDOW_POST_EVENT, begin_date=begin, 
            end_date=end).filter(temperature__gte=rules.TEMP_TO_REPORT)

                    

    def generate_events(self, **kw):
        log.info('Generating events for %s' % self.heuristic_name)
        matches = self.matches(**kw)
        encounter_type = ContentType.objects.get_for_model(EncounterEvent)

        counter = 0
        rule_explain = 'Patient had %3.1f fever after immunization(s)'

        for e in matches:
            date = e.date
            fever_message = rule_explain % float(e.temperature)

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
                    e.patient, ev, self.time_post_immunization)
                
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
    def __init__(self, event_name, icd9s, category, verbose_name=None, **kwargs):
        '''
        @type icd9s: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type discarding_icd9: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type ignored_if_past_occurrence: int
        @type verbose_name: String
        '''
                 
        self.heuristic_name = event_name
        self.icd9s = icd9s
        self.category = category
        self.discarding_icd9s = kwargs.pop('discarding_icd9s', [])
        self.ignored_if_past_occurrence = kwargs.pop(
            'ignored_if_past_occurrence', None)
        
        super(DiagnosisHeuristic, self).__init__(event_name, verbose_name=verbose_name)
            
    def matches(self, **kw):
        incremental = kw.get('incremental', False)
        
        last_run = Run.objects.filter(
            def_name=self.def_name, 
            status='s').aggregate(ts=Max('timestamp'))['ts']

        
        begin = (incremental and last_run) or kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()

        candidates = Encounter.objects.following_vaccination(
            rules.TIME_WINDOW_POST_EVENT, 
            begin_date=begin, end_date=end).filter(
            icd9_codes__in=self.icd9s)


        if self.discarding_icd9s:
            candidates = [x for x in candidates if not 
                          x.patient.has_history_of(self.discarding_icd9s, 
                                                      end_date=end)]

        if self.ignored_if_past_occurrence:
            months = self.ignored_if_past_occurrence
            candidates = [x for x in candidates 
                          if not x.is_reoccurrence(month_period=months)]

        return candidates


    def generate_events(self, **kw):
        log.info('Generating events for %s' % self.heuristic_name)
        counter = 0

        matches = self.matches(**kw)
        encounter_type = ContentType.objects.get_for_model(EncounterEvent)

        for e in matches:
            try:
                # Create event instance
                ev, created = EncounterEvent.objects.get_or_create(
                    encounter=e, date=e.date, category=self.category,
                    defaults={'matching_rule_explain':self.def_name,
                              'content_type':encounter_type}
                    )
                
                if created: counter +=1
                
                ev.save()
                ev.immunizations.clear()
                
                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(
                    e.patient, ev, self.time_post_immunization)
                
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
    def __init__(self, event_name, loinc, criterium, verbose_name=None):
        self.heuristic_name = event_name
        self.def_name = verbose_name
        self.loinc = loinc
        self.criterium = criterium
        self.def_name = verbose_name
        self.time_post_immunization = rules.TIME_WINDOW_POST_EVENT

        super(VaersLxHeuristic, self).__init__(event_name, verbose_name=verbose_name)

    def matches(self, **kw):
        
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

        
        
        incremental = kw.get('incremental', False)
        
        last_run = Run.objects.filter(
            def_name=self.def_name, 
            status='s').aggregate(ts=Max('timestamp'))['ts']
        
        begin = (incremental and last_run) or kw.get('begin_date') or EPOCH
        end = kw.get('end_date', None) or datetime.date.today()

        days = rules.TIME_WINDOW_POST_EVENT

                
        trigger = self.criterium['trigger']
        comparator, baseline = self.criterium['exclude_if']

        candidates = LabResult.objects.following_vaccination(
            days, loinc=self.loinc).filter(date__gte=begin, date__lte=end)
        
        return [c for c in candidates if is_trigger_value(c, trigger) and not 
                excluded_due_to_history(c, comparator, baseline)]

    
    def generate_events(self, **kw):
        log.info('Generating events for %s' % self.heuristic_name)
        counter = 0

        incremental = kw.get('incremental', False)
        
        if incremental:
            last_run = Run.objects.filter(
                def_name=self.def_name, status='s').aggregate(
                ts=Max('timestamp'))['ts']
        else:
            last_run = EPOCH

        begin_date = kw.get('begin_date', None) or last_run
        end_date = kw.get('end_date', None) or datetime.date.today()

        matches = self.matches(**kw)

        lab_type = ContentType.objects.get_for_model(LabResultEvent)

        for lab_result in matches:
            try:
                result = lab_result.result_float or lab_result.result_string
                rule_explain = 'Lab Result for %s resulting in %s'% (self.heuristic_name, result)
            
                ev, created = LabResultEvent.objects.get_or_create(
                    lab_result=lab_result,
                    category=self.criterium['category'],
                    date=lab_result.date,
                    defaults = {'matching_rule_explain': rule_explain,
                                'content_type':lab_type}
                    )
                
                if created: counter += 1

                ev.save()
                ev.immunizations.clear()

                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(
                    lab_result.patient, ev, self.time_post_immunization)

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

    def verbose_name(criterium):
        return 'Lab Result for %s with value above/below the trigger of %s %s' % (name, criterium['trigger'], criterium['unit'])

    return [
        VaersLxHeuristic(name + criterium['trigger'], loinc, criterium, verbose_name=verbose_name(criterium))
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


def main():
    # 
    # TODO: We need a lockfile or some othermeans to prevent multiple 
    # instances running at once.
    #
    parser = optparse.OptionParser(usage=USAGE_MSG)
    
    parser.add_option('-f', '--fever', action='store_true', dest='fever', help='Run Fever Heuristics')
    parser.add_option('-l', '--lx', action='store_true', dest='lx', help='Run Lab Results Heuristics')
    parser.add_option('-d', '--diagnostics', action='store_true', dest='diagnostics', 
                      help='Run Diagnostics Heuristics')
    parser.add_option('-a', '--all', action='store_true', dest='all', 
                      help='Generate new patients and immunization history')



    parser.add_option('--begin', action='store', dest='begin', type='string', 
                      metavar='DATE', help='Only events occurring after date')
    parser.add_option('--end', action='store', dest='end', type='string', 
                      metavar='DATE', help='Only events occurring before date')
    (options, args) = parser.parse_args()
    

    #
    # Date Parser
    #
    def parse_date(date_string):
        date_format = '%d-%b-%Y'
        return datetime.datetime.strptime(date_string, date_format).date()

    begin_date = parse_date(options.begin) if options.begin else datetime.datetime.today()

    end_date = parse_date(options.end) if options.end else EPOCH


    if options.all:
        options.fever = True
        options.diagnostics = True
        options.lx = True

    if not (options.fever or options.diagnostics or options.lx):
        parser.print_help()
        import sys
        sys.exit()


    if options.fever: fever_heuristic()
    if options.diagnostics: diagnostic_heuristics()
    if options.lx: lab_heuristics()


    BaseHeuristic.generate_all_events(incremental=True)



if __name__ == '__main__':
    main()
    
        
