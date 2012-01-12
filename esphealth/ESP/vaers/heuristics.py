# Adverse events are indicated though reports of fever, lab results
# and icd9 codes that are present in patient encounters.
import sys
import pdb
import optparse
import datetime

from django.db.models import Q, F, Max
from django.contrib.contenttypes.models import ContentType

from ESP.hef.base import BaseHeuristic
from ESP.conf.common import EPOCH
from ESP.conf.models import LabTestMap # renamed from 2.2 codemap
from ESP.static.models import Icd9
from ESP.emr.models import Immunization, Encounter, LabResult
from ESP.vaers.models import AdverseEvent
from ESP.vaers.models import EncounterEvent, LabResultEvent
from ESP.vaers.models import DiagnosticsEventRule
from ESP.utils.utils import log

import rules

VAERS_CORE_URI = 'urn:x-esphealth:vaers:core:v1'
LAB_TESTS_NAMES = rules.VAERS_LAB_RESULTS.keys()

USAGE_MSG = '''\
%prog [options]

    One or more of '-lx', '-f', '-d' or '-a' must be specified.
    
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
        
     
    @property
    def core_uris(self):
        # Only this version of HEF is supported
        return [VAERS_CORE_URI]
    
    @property
    def short_name(self):
        return 'adverse event:%s' % self.name
        
            
class VaersFeverHeuristic(AdverseEventHeuristic):
    def __init__(self):
        self.category = 'auto'
        super(VaersFeverHeuristic, self).__init__(
            'VAERS Fever', verbose_name='Fever reaction to immunization')
        
    uri = 'urn:x-esphealth:heuristic:channing:vaersfever:v1'
      

    def matches(self, **kw):
        #raise NotImplementedError('Last run support no longer available.  This method must be refactored')
        incremental = kw.get('incremental', False)
        # TODO review with Jason about last run
        #last_run = Run.objects.filter(status='s').aggregate(ts=Max('timestamp'))['ts']
        
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
        
        encounter_type = ContentType.objects.get_for_model(EncounterEvent)

        counter = 0
        rule_explain = 'Patient had %3.1f fever after immunization(s)'

        for e in matches:
            date = e.date
            fever_message = rule_explain % float(e.temperature)

            try:
                # Create event instance
                ev, created = EncounterEvent.objects.get_or_create(
                    category = self.category, date=date, encounter=e, patient=e.patient,
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
                # Get time interval between immunization and event
                ev.gap = (e.date - min([i.date for i in immunizations])).days

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
        
        super(DiagnosisHeuristic, self).__init__(event_name, verbose_name=self.verbose_name)
            
    uri = 'urn:x-esphealth:heuristic:channing:vaersdx:v1'
            
    def matches(self, **kw):
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()

        return Encounter.objects.following_vaccination(rules.TIME_WINDOW_POST_EVENT).filter(
            date__gte=begin, date__lte=end, icd9_codes__in=self.icd9s).distinct()

    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0

        matches = self.matches(**kw)
        encounter_type = ContentType.objects.get_for_model(EncounterEvent)

        for e in matches:
            if self.ignore_period and e.is_reoccurrence(self.icd9s, int(self.ignore_period)): continue
            try:
                # Create event instance
                ev, created = EncounterEvent.objects.get_or_create(
                    encounter=e, date=e.date, category=self.category, patient=e.patient,
                    defaults={'matching_rule_explain':self.verbose_name,
                              'content_type':encounter_type}
                    )
                
                if created: counter +=1
                
                ev.save()
                ev.immunizations.clear()
                
                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(
                    e.patient, ev, self.time_post_immunization)
                
                assert len(immunizations) > 0
                # Get time interval between immunization and event
                ev.gap = (e.date - min([i.date for i in immunizations])).days

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

class Icd9CorrelatedHeuristic(DiagnosisHeuristic):
    def __init__(self, event_name, icd9s, category, ignore_period, discarding_icd9s):
        self.discarding_icd9s = discarding_icd9s
        super(Icd9CorrelatedHeuristic, self).__init__(event_name, icd9s, category, ignore_period)
        
    def matches(self, **kw):
        matches = super(Icd9CorrelatedHeuristic, self).matches(**kw)
        return [match for match in matches 
                if not match.patient.has_history_of(self.discarding_icd9s, end_date=match.date)]




class VaersLxHeuristic(AdverseEventHeuristic):
    def __init__(self, event_name, lab_codes, criterium):
        self.name = event_name
        self.lab_codes = lab_codes
        self.criterium = criterium
        self.time_post_immunization = rules.TIME_WINDOW_POST_EVENT

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
                
                lkv = lx.last_known_value()
                if not lkv: return False
                
                current_value = lx.result_float or lx.result_string or None
                
                assert float(current_value)
                assert float(lkv)
                
                equation = ' '.join([str(current_value), comparator, baseline.replace('LKV', str(lkv))])

                return eval(equation)
            except:
                return False

        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        days = rules.TIME_WINDOW_POST_EVENT
                
        trigger = self.criterium['trigger']
        comparator, baseline = self.criterium['exclude_if']

        candidates = LabResult.objects.following_vaccination(days).filter(
            native_code__in=self.lab_codes, date__gte=begin, date__lte=end).distinct()
        
        return [c for c in candidates if is_trigger_value(c, trigger) and not 
                excluded_due_to_history(c, comparator, baseline)]

    
    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        
        #begin_date = kw.get('begin_date', None) or EPOCH
        #end_date = kw.get('end_date', None) or datetime.date.today()

        matches = self.matches(**kw)

        lab_type = ContentType.objects.get_for_model(LabResultEvent)

        for lab_result in matches:
            try:
                result = lab_result.result_float or lab_result.result_string
                rule_explain = 'Lab Result for %s resulting in %s'% (self.name, result)


                try:
                    ev, created = LabResultEvent.objects.get_or_create(
                        lab_result=lab_result,
                        category=self.criterium['category'],
                        date=lab_result.date,
                        patient=lab_result.patient,
                        defaults = {
                            'name': self.vaers_heuristic_name(),
                            'matching_rule_explain': rule_explain,
                            'content_type':lab_type}
                        )
                except Exception, why:
                    pdb.set_trace()

                    
                if created: counter += 1

                ev.save()
                ev.immunizations.clear()

                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(lab_result.patient, ev, self.time_post_immunization)

                assert len(immunizations) > 0
                # Get time interval between immunization and event
                ev.gap = (lab_result.date - min([i.date for i in immunizations])).days


                for imm in immunizations:
                    ev.immunizations.add(imm)
                    

                
                ev.save()

            except AssertionError:
                log.error('No candidate immunization for LabResult %s' % lab_result)
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
    ignore_period = rule.ignored_if_past_occurrence

    discarding_icd9s = rule.heuristic_discarding_codes.all()

    if discarding_icd9s:
        return Icd9CorrelatedHeuristic(name, icd9s, category, ignore_period, discarding_icd9s)
    else:
        return DiagnosisHeuristic(name, icd9s, category, ignore_period)
    
def make_lab_heuristics(lab_type):
    rule = rules.VAERS_LAB_RESULTS[lab_type]

    def heuristic_name(criterium, lab_name):
        return '%s %s %s' % (lab_name, criterium['trigger'], criterium['unit'])

    return [VaersLxHeuristic(heuristic_name(criterium, lab_type), rule['codes'], criterium)
            for criterium in rule['criteria']]


def do_lab_codemapping(heuristics):
    for h in heuristics:
        for code in h.lab_codes:
            c, created = LabTestMap.objects.get_or_create(native_code=code, heuristic=h.name, 
                                                       native_name=h.vaers_heuristic_name())
            msg = ('New mapping %s' % c) if created else ('Mapping %s already on database' % c)
            log.info(msg)
    


        
def fever_heuristic():
    return VaersFeverHeuristic()

def diagnostic_heuristics():
    return [make_diagnosis_heuristic(v['name'])
            for v in rules.VAERS_DIAGNOSTICS.values()]

def lab_heuristics():
    hs = []

    for lab_type in rules.VAERS_LAB_RESULTS.keys():
        for heuristic in make_lab_heuristics(lab_type):
            hs.append(heuristic)

    return hs


def main():
    # 
    # TODO: We need a lockfile or some other means to prevent multiple 
    # instances running at once.
    #
    parser = optparse.OptionParser(usage=USAGE_MSG)
    
    parser.add_option('-f', '--fever', action='store_true', dest='fever', help='Run Fever Heuristics')
    parser.add_option('-l', '--lx', action='store_true', dest='lx', help='Run Lab Results Heuristics')
    parser.add_option('-d', '--diagnostics', action='store_true', dest='diagnostics', 
                      help='Run Diagnostics Heuristics')
    parser.add_option('-a', '--all', action='store_true', dest='all', 
                      help='Run all heuristics')
    parser.add_option('-m', '--mapping', action='store_true', dest='map', help='Build CodeMap for Lab Tests')
    parser.add_option('-e', '--events', action='store_true', dest='events', help='Generate Events')

    parser.add_option('--begin', action='store', dest='begin', type='string', 
                      metavar='DATE', help='Only events occurring after date')
    parser.add_option('--end', action='store', dest='end', type='string', 
                      metavar='DATE', help='Only events occurring before date')
    (options, args) = parser.parse_args()
    

    #
    # Date Parser
    #
    def parse_date(date_string):
        date_format = '%Y%m%d'
        return datetime.datetime.strptime(date_string, date_format).date()



    begin_date = parse_date(options.begin) if options.begin else EPOCH
    end_date = parse_date(options.end) if options.end else datetime.datetime.today()


    if options.all:
        options.fever = True
        options.diagnostics = True
        options.lx = True

    if not (options.fever or options.diagnostics or options.lx):
        parser.print_help()
        sys.exit()


    heuristics = []
    if options.fever: heuristics.append(fever_heuristic())
    if options.diagnostics: heuristics += diagnostic_heuristics()
    if options.lx: 
        lx_heuristics = lab_heuristics()
        heuristics += lx_heuristics
        if options.map:
            do_lab_codemapping(lx_heuristics)


    if options.events: 
        log.info('Generating events from %s to %s' % (begin_date, end_date))
        [h.generate(begin_date=begin_date, end_date=end_date) for h in heuristics]


if __name__ == '__main__':
    main()
    
        
