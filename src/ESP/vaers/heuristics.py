# Adverse events are indicated though reports of fever, lab results
# and icd9 codes that are present in patient encounters.

import optparse
import datetime

from django.db.models import Q, F

from ESP.hef.core import EncounterHeuristic
from ESP.conf.common import EPOCH
from ESP.conf.models import Icd9
from ESP.esp.models import Immunization, Enc, Lx
from ESP.vaers.models import AdverseEvent
from ESP.vaers.models import FeverEvent, DiagnosticsEvent, LabResultEvent
from ESP.vaers.models import DiagnosticsEventRule

import rules
import diagnostics

LAB_TESTS_NAMES = rules.VAERS_LAB_RESULTS.keys()


class DiagnosisHeuristic(EncounterHeuristic):
    def __init__(self, name, icd9s, verbose_name=None, **kwargs):
        '''
        @type icd9s: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type discarding_icd9: [<Icd9>, <Icd9>, <Icd9>, ...]
        @type ignored_if_past_occurrance: int
        @type verbose_name: String
        '''
        self.discarding_icd9s = kwargs.pop('discarding_icd9s', [])
        self.ignored_if_past_occurrance = kwargs.pop(
            'ignored_if_past_occurrance', None)

        super(DiagnosisHeuristic, 
              self).__init__(name, icd9s, verbose_name, **kwargs)


    

    def matches(self, begin_date=None, end_date=None):
        begin_date = begin_date or EPOCH
        end_date = end_date or datetime.date.today()

        

        possible = Enc.objects.filter(
            reported_icd9_list__in=self.icd9s,
            EncEncounter_Date__gte=begin_date.strftime('%Y%m%d'),
            EncEncounter_Date__lte=end_date.strftime('%Y%m%d')
            ).only('id', 'EncPatient')
        
        
        return possible

        


    


# The detect_* functions below determine if a given immunization has
# caused a adverse event. time_window is the time that after the
# immunization that is considered for the event to be a consequence of
# the immunization.

# Immunization is an instance from models.Immunization, which contains
# information about the patient, dose, date taken, etc

def detect_fevers(immunization, time_window):

    patient = immunization.ImmPatient
    date = datetime.datetime.strptime(immunization.ImmDate, '%Y%m%d')        
    patient_encounters = Enc.objects.filter(
        EncPatient=patient, 
        EncEncounter_Date__gte=date.strftime('%Y%m%d'),
        EncEncounter_Date__lte=(date+time_window).strftime('%Y%m%d')
        )

    fever_encounters = []
    for e in patient_encounters:
        try:
            temperature = float(e.EncTemperature)
            if temperature >= rules.TEMP_TO_REPORT: 
                fever_encounters.append(e)
            e.temperature = temperature
        except:
            pass
    

    detected = []
    for e in fever_encounters:
        rule='Patient with %3.1fF fever' % e.temperature
        ev, new = FeverEvent.objects.get_or_create(
            patient=patient,
            temperature=e.temperature,
            immunization=immunization,
            category='auto',
            defaults = {'matching_rule_explain': rule,
                        'encounter':e}
            )
        detected.append(ev)

    return detected
        

def detect_diagnostics(immunization, time_window):
    patient = immunization.ImmPatient
    date = datetime.datetime.strptime(immunization.ImmDate, '%Y%m%d')
    patient_encounters = Enc.objects.filter(
        EncPatient=patient,
        EncEncounter_Date__gte=date.strftime('%Y%m%d'),
        EncEncounter_Date__lte=(date+time_window).strftime('%Y%m%d')
        )
        
    detected = []
    for e in patient_encounters:
        vaers_codes = [x for x in e.EncICD9_Codes.split(',') 
                       if (x.strip() and diagnostics.is_match(x))]

        for code in vaers_codes:
            diag = diagnostics.by_code(code)

            # FIXME: icd9Code matching could be exact, but some
            # strings on the table are not trimmed. Instead of using
            # objects.get, I'm forced to use the a query with LIKE
            # operator, hence objects.filter(__startswith)

            icd9_code = icd9.objects.filter(icd9Code__startswith=code)[:1]
            if icd9_code:    
                rule='Patient diagnosed with %s' % diag['name']
                ev, new = DiagnosticsEvent.objects.get_or_create(
                    patient=patient,
                    immunization=immunization,
                    category=diag['category'],
                    encounter=e,
                    icd9=icd9_code[0],
                    defaults = {'matching_rule_explain': rule}
                    )

                detected.append(ev)

    return detected
 

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

    d = {
        'ignored_if_past_occurrance':rule.ignored_if_past_occurrance,
        'discarding_icd9s': rule.heuristic_discarding_codes.all(),
        'category':rule.category
        }

    return DiagnosisHeuristic(name, icd9s, verbose_name, **d)
        



if __name__ == '__main__':
    import datetime

    heuristics = [make_diagnosis_heuristic(v['name'])
                  for v in rules.VAERS_DIAGNOSTICS.values()]

    for h in heuristics:
        print h.matches(begin_date=datetime.date(year=2006, month=01, day=02),
                        end_date=datetime.date(year=2006, month=02, day=02)
                        )
    
    
        
