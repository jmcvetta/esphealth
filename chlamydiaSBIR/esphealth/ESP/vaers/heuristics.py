# Adverse events are indicated though reports of  lab results, prescriptions, allergies
# and dx codes that are present in patient encounters.
import datetime, itertools

from dateutil.relativedelta import relativedelta

from django.db.models import F, Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from ESP.hef.base import BaseHeuristic
from ESP.conf.common import EPOCH
from ESP.static.models import Dx_code
from ESP.emr.models import Immunization, Encounter, LabResult,  Allergy
from ESP.emr.models import Prescription, Problem, Hospital_Problem
from ESP.vaers.models import Case, PrescriptionEvent, EncounterEvent, LabResultEvent, AllergyEvent, ProblemEvent, HospProblemEvent
from ESP.vaers.models import DiagnosticsEventRule
from ESP.vaers.models import ExcludedDx_Code, Questionnaire
from ESP.utils.utils import log
from ESP.conf.models import LabTestMap, VaccineCodeMap 
from ESP.hef.base import LabResultAnyHeuristic
import rules

VAERS_CORE_URI = 'urn:x-esphealth:vaers:core:v1'
LAB_TESTS_NAMES = rules.VAERS_LAB_RESULTS.keys()

USAGE_MSG = '''\
%prog [options]

    One or more of '-lx',  '-d', '-p', '-g' or '-a' must be specified.
    
    DATE variables are specified in this format: 'YYYYMMDD'
'''

class AdverseEventHeuristic(BaseHeuristic):
    
    lkv = None
    lkd = None
    
    def __init__(self, event_name, verbose_name=None):
        self.time_post_immunization = rules.MAX_TIME_WINDOW_POST_EVENT
        assert event_name
        assert verbose_name
        self.name = event_name
        self.long_name = verbose_name
    
    
    def update_or_create_case(self, clin_event, this_imm, this_event):
        # if there is an existing case for this event (immunization
        # and attach to it if not created one
        #  add to the case the list of prior vaccines within 28 days 
        # and update the date of last event added 
        # Register any prior immunizations
        prior_immunizations = Immunization.vaers_candidates(clin_event.patient,clin_event.date, 
                 rules.MAX_TIME_WINDOW_PRIOR_EVENT,['ALL']).filter(date__lt = this_imm.date)
        
        this_case, case_created = Case.objects.get_or_create(
                 date = this_imm.date,
                 patient = this_imm.patient
                )
        this_case.save()
        
        this_case.immunizations.add(this_imm)
        this_case.adverse_events.add(this_event)
        
        for prior in prior_immunizations:
            this_case.prior_immunizations.add(prior)
        this_case.save()
        
        #create questionnaires for every physician in the events
        for ae in this_case.adverse_events.all():
            #if the ae is from an encounter with a physician, wait a day in case labs show up, then generate the questionnaire record
            if ContentType.objects.get_for_id(ae.content_type_id).model.startswith('encounter') and ae.date+datetime.timedelta(days=1)>datetime.date.today():
                continue
            prov  = ae.content_object.provider 
            this_q, created = Questionnaire.objects.get_or_create(provider = prov,
                  case= this_case)
            if not created:
                continue
            
            this_q.save()
            this_q.create_digest()
    
    #TODO fix for icd10 need to join with static_dx_code table where dx_code_id = combotypecode
    def exclude_at_3dig(self, qSet, type, this_diag):
        '''
        takes a qSet of prior diagnosis records 
        then depending on qSet type (encounter, problem or hospitalproblem)
        keeps only those that match self.dx_codes at the 3 digit level
        For Any other Diagnosis heuristics, filters slef.dx_codes to only those matching current diagnosis record
        '''
        #this is a quick method to provide Mike and Meghan with data
        #on how prior-occurrence exclusion would look if we broaden exclusion
        #to all diagnoses at the 3-digit level.  
        dx_code_3dig = self.dx_codes.extra(select={'dx_code3dig': "case when position('.' in code) > 0 then substring(code from 1 for position('.' in code)-1 ) else code end"}).values_list('dx_code3dig')
        dx_code_3dig = sorted(dx_code_3dig.distinct())
        if self.name=="Any other Diagnosis":
            subset=[]
            for x in dx_code_3dig:
                for y in this_diag:
                    if x[0] in y:
                        subset.append(x)
            dx_code_3dig=subset
        if not dx_code_3dig:
            return qSet.extra(where=[' 1=2 '])
        elif type=='encounter':
            for i, x in enumerate(dx_code_3dig):
                if i == 0:
                    xquery="emr_encounter.id=emr_encounter_dx_codes.encounter_id and ( position('"+str(x[0])+"' in emr_encounter_dx_codes.dx_code_id) > 0"
                else:
                   
                    xquery=xquery+" or position('"+str(x[0])+"' in emr_encounter_dx_codes.dx_code_id) > 0"
            xquery = xquery + ")"
            return qSet.extra(tables=["emr_encounter_dx_codes"], where=[xquery])
        else:
            for i, x in enumerate(dx_code_3dig):
                if i == 0:
                    xquery=" (position('"+str(x[0])+"' in dx_code_id) > 0"
                else:
                    xquery=xquery+" or position('"+str(x[0])+"' in dx_code_id) > 0"
            xquery = xquery + ")"
            return qSet.extra(where=[xquery])            

            
    @property
    def core_uris(self):
        # Only this version of HEF is supported
        return [VAERS_CORE_URI]
    
    @property
    def short_name(self):
        return 'adverse event:%s' % self.name
        
            
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
        self.risk_period_start =0 
        
        super(VaersAllergyHeuristic, self).__init__(event_name, verbose_name=self.verbose_name)
            
    uri = 'urn:x-esphealth:heuristic:channing:vaersallergies:v1'
    
    def vaers_heuristic_name(self):
        return 'VAERS: allergies to ' + self.name
            
    def matches(self, **kw):
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        #these convulsions are needed to account for prior vaccine matches to allergies.  See the various conf and static tables involved
        rawQuery= ("SELECT  distinct t0.id, t0.provenance_id, t0.natural_key, t0.created_timestamp, t0.updated_timestamp, " + 
             "t0.patient_id, t0.provider_id, t0.date, t0.mrn, t0.date_noted, t0.allergen_id, t0.name, t0.status, t0.description " + 
             "FROM emr_allergy as t0 " + 
             "INNER JOIN emr_patient as t1 ON (t0.patient_id = t1.id) " + 
             "INNER JOIN emr_immunization as t2 ON (t1.id = t2.patient_id) " + 
             "INNER JOIN static_allergen_vaccines as t3 ON (t0.allergen_id=t3.allergen_id) " +
             "INNER JOIN conf_vaccinecodemap as t4 on (t3.vaccine_id = t4.canonical_code_id ) " +
             "WHERE t2.isvaccine = True  AND t2.imm_status = '1'  AND t0.date >=  t2.date AND t0.status='Active' " +
             "AND t0.date <=  t2.date + interval '30 days' and t2.imm_type = t4.native_code " +
             "AND t0.date >= '" + str(begin) + "'::date AND t0.date <= '" + str(end) + "'::date " )
        if self.keywords:
            for idx, keyword in enumerate(self.keywords):
                if idx==0:
                    rawQuery = rawQuery + " AND (position(upper('" + keyword + "') in upper(t0.name))>0 "
                else:
                    rawQuery = rawQuery + " OR position(upper('" + keyword + "') in upper(t0.name))>0 "
            rawQuery = rawQuery + ")"
        
        allergy_qs = Allergy.objects.raw(rawQuery)
        
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
                    name__icontains = self.keywords, 
                    # or description field 
                    patient = this_allergy.patient, 
                    
                )
            if prior_allergy_qs:
                continue # Prior allergy so ignore 
            
            rawQuery = ("SELECT distinct t0.id, t0.native_code FROM conf_vaccinecodemap as t0 INNER JOIN static_allergen_vaccines as t1 " +
                        "ON (t1.vaccine_id = t0.canonical_code_id ) INNER JOIN static_allergen t2 ON (t1.allergen_id=t2.code) ") 
            for idx, keyword in enumerate(self.keywords):
                if idx==0:
                    rawQuery = rawQuery + " WHERE (position(upper('" + keyword + "') in upper(t2.name))>0 "
                else:
                    rawQuery = rawQuery + " OR position(upper('" + keyword + "') in upper(t2.name))>0 "
            rawQuery = rawQuery + ")"
            immtypes = VaccineCodeMap.objects.raw(rawQuery)
            types=[]
            for immtype in immtypes:
                types.append(immtype.native_code)
            
            immunization_qs = Immunization.vaers_candidates(this_allergy.patient, this_allergy.date, self.time_post_immunization, types)
            assert immunization_qs
            
            # create a new event for each immunization date 
            for imm in immunization_qs:
                # Create event instance
                new_ae, created = AllergyEvent.objects.get_or_create(
                    gap = (this_allergy.date - imm.date).days,
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
                
                new_ae.version = rules.VAERS_VERSION
                        
                new_ae.save() # Must save before adding to ManyToManyField
                
                if created: 
                    counter +=1
                self.update_or_create_case(this_allergy, imm, new_ae)
                
        return counter
        
class VaersDiagnosisHeuristic(AdverseEventHeuristic):
    def __init__(self, event_name, dx_codes, rule):
        '''
        @type dx_codes: [<Dx_code>, <Dx_code>, <Dx_code>, ...]
        @type discarding_dx_code: [<Dx_code>, <Dx_code>, <Dx_code>, ...]
        @type verbose_name: String
        @type rule: object diagnosis event rule
        '''
                 
        self.name = event_name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.dx_codes = dx_codes
        self.category = rule.category
        self.source = rule.source
        self.ignore_period = rule.ignore_period  
        self.risk_period = rule.risk_period
        self.risk_period_start = rule.risk_period_start      
        
        super(VaersDiagnosisHeuristic, self).__init__(event_name, verbose_name=self.verbose_name)
            
    uri = 'urn:x-esphealth:heuristic:channing:vaersdx:v1'
    
    def vaers_heuristic_name(self):
        
        return 'VAERS: ' + self.name
            
    def matches(self, **kw):
        # the reports of AE are per immunization 
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        enc_qs = Encounter.objects.following_vaccination(self.risk_period,self.risk_period_start)
        
        enc_qs = enc_qs.filter(dx_codes__in=self.dx_codes.all())
        enc_qs = enc_qs.filter(date__gte=begin, date__lte=end)
        enc_qs = enc_qs.distinct()
        return enc_qs

    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        content_type = ContentType.objects.get_for_model(Encounter)
        
        #TODO find the encounter that has a date <= this enc date and close date => this enc date
        # or close date is null is same as start one day hospitalization
        # dont add the event if the priority is >
        
        if self.source==None:
            types=['ALL']
        else:
            rawQuery = ("SELECT distinct t0.id, t0.native_code FROM conf_vaccinecodemap as t0 INNER JOIN static_vaccine as t1 " +
                        "ON (t1.id = t0.canonical_code_id ) where position(%s in lower(t1.name))>0") 
            immtypes = VaccineCodeMap.objects.raw(rawQuery,[self.source])
            types=[]
            for immtype in immtypes:
                types.append(immtype.native_code)
        
        for this_enc in self.matches(**kw):
            #check_priors is created because self.dx_codes is a @property method for any other diagnosis heuristic
            if self.name=="Any other Diagnosis":
                check_priors = self.dx_codes.filter(combotypecode__in=this_enc.dx_codes.all())
            else:
                check_priors = self.dx_codes
            if self.ignore_period:
                earliest = this_enc.date - relativedelta(months=self.ignore_period)
                prior_enc_qs = Encounter.objects.filter(
                    date__lt = this_enc.date, 
                    date__gte = earliest, 
                    #priority__lte = this_enc.priority,
                    patient = this_enc.patient,                     
                    #dx_codes__in = check_priors.all(),
                )
                prior_enc_qs = self.exclude_at_3dig(prior_enc_qs,'encounter',this_enc.dx_codes.values_list('code', flat=True))

                if prior_enc_qs:
                    continue # Prior diagnosis so ignore 
                
                prior_problem_qs = Problem.objects.filter(
                    date__lt = this_enc.date, 
                    #dx__code__in = check_priors.all(),
                    patient = this_enc.patient, 
                )
                prior_problem_qs = self.exclude_at_3dig(prior_problem_qs,'problem',this_enc.dx_codes.values_list('code'))
                if prior_problem_qs:
                    continue # prior problem so ignore 
                
                prior_hproblem_qs = Hospital_Problem.objects.filter(
                    date__lt = this_enc.date, 
                    #dx__code__in = check_priors.all(),
                    patient = this_enc.patient, 
                )
                prior_hproblem_qs = self.exclude_at_3dig(prior_hproblem_qs,'hospitalproblem',this_enc.dx_codes.values_list('code'))
                if prior_hproblem_qs:
                    continue # prior problem so ignore 
                
            #find the adverse event dx codes           
            thisname = self.name
            for code in this_enc.dx_codes.filter(combotypecode__in=self.dx_codes).distinct():
                thisname += ' '+code.combotypecode

            immunization_qs = Immunization.vaers_candidates(this_enc.patient, this_enc.date, self.risk_period, types)
            if not immunization_qs.exists():
                continue # no immunizations of the type we're looking for
            
            # create a new event for each immunization date 
            for imm in immunization_qs:
                        
                new_ee, created = EncounterEvent.objects.get_or_create(
                    gap = (this_enc.date - imm.date).days,
                    object_id = this_enc.pk,
                    content_type = content_type,
                    date = this_enc.date, 
                    patient = this_enc.patient,
                    defaults={
                        'name': self.vaers_heuristic_name(),
                        'matching_rule_explain': thisname ,
                        'category' : self.category, 
                        }
                    )
                
                new_ee.version = rules.VAERS_VERSION
                    
                new_ee.save() # Must save before adding to ManyToManyField
                
                if created: 
                    counter +=1
                    
                self.update_or_create_case(this_enc, imm, new_ee)
            
        return counter

class VaersProblemHeuristic(AdverseEventHeuristic):
    def __init__(self, event_name, dx_codes, rule):
        '''
        @type dx_codes: [<Dx_code>, <Dx_code>, <Dx_code>, ...]
        @type discarding_dx_code: [<Dx_code>, <Dx_code>, <Dx_code>, ...]
        @type verbose_name: String
        @type rule: object diagnosis event rule
        '''
                 
        self.name = event_name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.dx_codes = dx_codes
        self.category = rule.category
        self.source=rule.source
        self.ignore_period = rule.ignore_period  
        self.risk_period = rule.risk_period
        self.risk_period_start = rule.risk_period_start      
        
        super(VaersProblemHeuristic, self).__init__(event_name, verbose_name=self.verbose_name)
            
    uri = 'urn:x-esphealth:heuristic:channing:vaersdx:v1'
    
    def vaers_heuristic_name(self):
        
        return 'VAERS: (Problem) ' + self.name
            
    def matches(self, **kw):
        # the reports of AE are per immunization 
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        prb_qs = Problem.objects.following_vaccination(self.risk_period,self.risk_period_start)
        
        prb_qs = prb_qs.filter(dx_code__in=self.dx_codes.all())
        prb_qs = prb_qs.filter(date__gte=begin, date__lte=end)
        prb_qs = prb_qs.exclude(status='Deleted')
        prb_qs = prb_qs.distinct()
        return prb_qs

    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        content_type = ContentType.objects.get_for_model(Problem)
        
        #TODO find the encounter that has a date <= this enc date and close date => this enc date
        # or close date is null is same as start one day hospitalization
        # dont add the event if the priority is >
        
        for this_prb in self.matches(**kw):
            if self.name=="Any other Diagnosis":
                #TODO add type or? is the dx_code_id
                check_priors = self.dx_codes.filter(combotypecode__in=[this_prb.dx_code_id])
            else:
                check_priors = self.dx_codes
            if self.ignore_period:
                earliest = this_prb.date - relativedelta(months=self.ignore_period)
                prior_enc_qs = Encounter.objects.filter(
                    date__lt = this_prb.date, 
                    date__gte = earliest, 
                    #priority__lte = this_enc.priority,
                    patient = this_prb.patient,                     
                    #dx_codes__in = check_priors.all(),
                )
                prior_enc_qs = self.exclude_at_3dig(prior_enc_qs,'encounter',[this_prb.dx_code_id])
                if prior_enc_qs:
                    continue # Prior diagnosis so ignore 
                
                prior_problem_qs = Problem.objects.filter(
                    date__lt = this_prb.date, 
                    #dx_code__in=check_priors.all(),
                    patient = this_prb.patient, 
                )
                prior_problem_qs = self.exclude_at_3dig(prior_problem_qs,'problem',[this_prb.dx_code_id])
                if prior_problem_qs:
                    continue # prior problem so ignore 
                
                prior_hproblem_qs = Hospital_Problem.objects.filter(
                    date__lt = this_prb.date, 
                    #dx_code__in=check_priors.all(),
                    patient = this_prb.patient, 
                )
                prior_hproblem_qs = self.exclude_at_3dig(prior_hproblem_qs,'hospitalproblem',[this_prb.dx_code_id])
                if prior_hproblem_qs:
                    continue # prior problem so ignore 
                
            #find the adverse event dx codes           
            thisname = self.name + ' ' + str(this_prb.dx_code)

            immunization_qs = Immunization.vaers_candidates(this_prb.patient, this_prb.date, self.risk_period,['ALL'])
            assert immunization_qs
            
            # create a new event for each immunization date 
            for imm in immunization_qs:
                        
                new_ee, created = ProblemEvent.objects.get_or_create(
                    gap = (this_prb.date - imm.date).days,
                    object_id = this_prb.pk,
                    content_type = content_type,
                    date = this_prb.date, 
                    patient = this_prb.patient,
                    defaults={
                        'name': self.vaers_heuristic_name(),
                        'matching_rule_explain': thisname ,
                        'category' : self.category, 
                        }
                    )
                
                new_ee.version = rules.VAERS_VERSION
                    
                new_ee.save() # Must save before adding to ManyToManyField
                
                if created: 
                    counter +=1
                    
                self.update_or_create_case(this_prb, imm, new_ee)
            
        return counter

class VaersHospProbHeuristic(AdverseEventHeuristic):
    def __init__(self, event_name, dx_codes, rule):
        '''
        @type dx_codes: [<Dx_code>, <Dx_code>, <Dx_code>, ...]
        @type discarding_dx_code: [<Dx_code>, <Dx_code>, <Dx_code>, ...]
        @type verbose_name: String
        @type rule: object diagnosis event rule
        '''
                 
        self.name = event_name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.dx_codes = dx_codes
        self.category = rule.category
        self.source = rule.source
        self.ignore_period = rule.ignore_period  
        self.risk_period = rule.risk_period
        self.risk_period_start = rule.risk_period_start      
        
        super(VaersHospProbHeuristic, self).__init__(event_name, verbose_name=self.verbose_name)
            
    uri = 'urn:x-esphealth:heuristic:channing:vaersdx:v1'
    
    def vaers_heuristic_name(self):
        
        return 'VAERS: (Problem) ' + self.name
            
    def matches(self, **kw):
        # the reports of AE are per immunization 
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        hprb_qs = Hospital_Problem.objects.following_vaccination(self.risk_period,self.risk_period_start)
        
        hprb_qs = hprb_qs.filter(dx_code__in=self.dx_codes.all())
        hprb_qs = hprb_qs.filter(date__gte=begin, date__lte=end)
        hprb_qs = hprb_qs.exclude(status='Deleted')
        hprb_qs = hprb_qs.distinct()
        return hprb_qs

    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        content_type = ContentType.objects.get_for_model(Hospital_Problem)
        
        #TODO find the encounter that has a date <= this enc date and close date => this enc date
        # or close date is null is same as start one day hospitalization
        # dont add the event if the priority is >

        if self.source==None:
            types=['ALL']
        else:
            rawQuery = ("SELECT distinct t0.id, t0.native_code FROM conf_vaccinecodemap as t0 INNER JOIN static_vaccine as t1 " +
                        "ON (t1.id = t0.canonical_code_id ) where position(%s in lower(t1.name))>0") 
            immtypes = VaccineCodeMap.objects.raw(rawQuery,[self.source])
            types=[]
            for immtype in immtypes:
                types.append(immtype.native_code)
        
        
        for this_hprb in self.matches(**kw):
            if self.name=="Any other Diagnosis":
                check_priors = self.dx_codes.filter(combotypecode__in=[this_hprb.dx_code_id])
            else:
                check_priors = self.dx_codes
            if self.ignore_period:
                earliest = this_hprb.date - relativedelta(months=self.ignore_period)
                prior_enc_qs = Encounter.objects.filter(
                    date__lt = this_hprb.date, 
                    date__gte = earliest, 
                    #priority__lte = this_enc.priority,
                    patient = this_hprb.patient,                     
                    #dx_codes__in = check_priors.all(),
                )
                prior_enc_qs = self.exclude_at_3dig(prior_enc_qs,'encounter',[this_hprb.dx_code_id])
                if prior_enc_qs:
                    continue # Prior diagnosis so ignore 
                
                prior_problem_qs = Problem.objects.filter(
                    date__lt = this_hprb.date, 
                    #dx_code__in=check_priors.all(),
                    patient = this_hprb.patient, 
                )
                prior_problem_qs = self.exclude_at_3dig(prior_problem_qs,'problem',[this_hprb.dx_code_id])
                if prior_problem_qs:
                    continue # prior problem so ignore 
                
                prior_hproblem_qs = Hospital_Problem.objects.filter(
                    date__lt = this_hprb.date, 
                    #dx_code__in=check_priors.all(),
                    patient = this_hprb.patient, 
                )
                prior_hproblem_qs = self.exclude_at_3dig(prior_hproblem_qs,'hospitalproblem',[this_hprb.dx_code_id])
                if prior_hproblem_qs:
                    continue # prior problem so ignore 
                
            #find the adverse event dx codes           
            thisname = self.name + ' ' + str(this_hprb.dx_code_id)

            immunization_qs = Immunization.vaers_candidates(this_hprb.patient, this_hprb.date, self.risk_period,types)
            if not immunization_qs.exists():
                continue # no immunizations of the type we're looking for

            
            # create a new event for each immunization date 
            for imm in immunization_qs:
                        
                new_ee, created = HospProblemEvent.objects.get_or_create(
                    gap = (this_hprb.date - imm.date).days,
                    object_id = this_hprb.pk,
                    content_type = content_type,
                    date = this_hprb.date, 
                    patient = this_hprb.patient,
                    defaults={
                        'name': self.vaers_heuristic_name(),
                        'matching_rule_explain': thisname ,
                        'category' : self.category, 
                        }
                    )
                
                new_ee.version = rules.VAERS_VERSION
                    
                new_ee.save() # Must save before adding to ManyToManyField
                
                if created: 
                    counter +=1
                    
                self.update_or_create_case(this_hprb, imm, new_ee)
            
        return counter

class Dx_CodeCorrelatedHeuristic(VaersDiagnosisHeuristic):
    def __init__(self, event_name, dx_codes, rule, discarding_dx_codes):
        self.discarding_dx_codes = discarding_dx_codes
        super(Dx_CodeCorrelatedHeuristic, self).__init__(event_name, dx_codes, rule)
        
    def matches(self, **kw):
        matches = super(Dx_CodeCorrelatedHeuristic, self).matches(**kw)
        valid_matches = []
        for this_match in matches:
            relevancy_begin = this_match.date - relativedelta(months=12)
            history = this_match.patient.has_history_of(
                self.discarding_dx_codes, 
                begin_date=relevancy_begin, 
                end_date=this_match.date)
            if history:
                continue # Patient has a history of this problem, so we will skip it.
            valid_matches.append(this_match)
        return valid_matches 

class AnyOtherDiagnosisHeuristic(VaersDiagnosisHeuristic):
    '''
    Any diagnosis not covered by another heuristic, or included in 
    the ExcludedDx_Code table. Exclude if:
    1.Same code on patient's current problem list prior to this encounter 
    2.Encounter with same code in past 36 months
    3.Past medical history list with same code 
    '''
    
    uri = 'urn:x-esphealth:heuristic:channing:vaersany_other_dx:v1'
    
    def __init__(self):
        self.name = 'Any other Diagnosis' # This is the EVENT name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.category = '2_possible'
        self.ignore_period =  rules.MAX_TIME_WINDOW_POST_ANY_EVENT # months
        self.risk_period = rules.MAX_TIME_WINDOW_POST_EVENT
        self.source=None
        self.risk_period_start = 1
        super(VaersDiagnosisHeuristic, self).__init__(self.name, verbose_name=self.verbose_name)
            
    @property
    def dx_codes(self):
        
        '''
        All dx codes that are not covered by another heuristic and are not 
        included in the ExcludedDx_Code table.
        @rtype: Dx_code QuerySet
        '''
        covered_dx_codes = DiagnosticsEventRule.objects.filter(heuristic_defining_codes__isnull=False).values('heuristic_defining_codes')
        excluded_dx_codes = ExcludedDx_Code.objects.values('code')
        #TODO fix icd10 patched for now
        dx_codes_qs = Dx_code.objects.exclude(combotypecode__in=covered_dx_codes)
        dx_codes_qs = dx_codes_qs.exclude(code__in=excluded_dx_codes, type = 'ICD9')
        return dx_codes_qs

class Dx_codePCorrelatedHeuristic(VaersProblemHeuristic):
    def __init__(self, event_name, dx_codes, rule, discarding_dx_codes):
        self.discarding_dx_codes = discarding_dx_codes
        super(Dx_codePCorrelatedHeuristic, self).__init__(event_name, dx_codes, rule)
        
    def matches(self, **kw):
        matches = super(Dx_codePCorrelatedHeuristic, self).matches(**kw)
        valid_matches = []
        for this_match in matches:
            relevancy_begin = this_match.date - relativedelta(months=12)
            history = this_match.patient.has_history_of(
                self.discarding_dx_codes, 
                begin_date=relevancy_begin, 
                end_date=this_match.date)
            if history:
                continue # Patient has a history of this problem, so we will skip it.
            valid_matches.append(this_match)
        return valid_matches 

class AnyOtherProblemHeuristic(VaersProblemHeuristic):
    '''
    Any diagnosis not covered by another heuristic, or included in 
    the ExcludedDx_Code table. Exclude if:
    1.Same code on patient's current problem list prior to this encounter 
    2.Encounter with same code in past 36 months
    3.Past medical history list with same code 
    '''
    
    uri = 'urn:x-esphealth:heuristic:channing:vaersany_other_dx:v1'
    
    def __init__(self):
        self.name = 'Any other Diagnosis' # This is the EVENT name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.category = '2_possible'
        self.source=None
        self.ignore_period =  rules.MAX_TIME_WINDOW_POST_ANY_EVENT # months
        self.risk_period = rules.MAX_TIME_WINDOW_POST_EVENT
        self.risk_period_start = 1
        super(VaersProblemHeuristic, self).__init__(self.name, verbose_name=self.verbose_name)
            
    @property
    def dx_codes(self):
        '''
        All dx codes that are not covered by another heuristic and are not 
        included in the ExcludedDx_Code table.
        @rtype: Dx_codes QuerySet
        '''
        covered_dx_codes = DiagnosticsEventRule.objects.filter(heuristic_defining_codes__isnull=False).values('heuristic_defining_codes')
        excluded_dx_codes = ExcludedDx_Code.objects.values('code')
        #TODO fix icd10 patched  for now
        dx_codes_qs = Dx_code.objects.exclude(combotypecode__in=covered_dx_codes)
        dx_codes_qs = dx_codes_qs.exclude(code__in=excluded_dx_codes, type = 'ICD9')
        return dx_codes_qs
    
class Dx_CodeHCorrelatedHeuristic(VaersHospProbHeuristic):
    def __init__(self, event_name, dx_codes, rule, discarding_dx_codes):
        self.discarding_dx_codes = discarding_dx_codes
        super(Dx_CodeHCorrelatedHeuristic, self).__init__(event_name, dx_codes, rule)
        
    def matches(self, **kw):
        matches = super(Dx_CodeHCorrelatedHeuristic, self).matches(**kw)
        valid_matches = []
        for this_match in matches:
            relevancy_begin = this_match.date - relativedelta(months=12)
            history = this_match.patient.has_history_of(
                self.discarding_dx_codes, 
                begin_date=relevancy_begin, 
                end_date=this_match.date)
            if history:
                continue # Patient has a history of this problem, so we will skip it.
            valid_matches.append(this_match)
        return valid_matches 

class AnyOtherHospProbHeuristic(VaersHospProbHeuristic):
    '''
    Any diagnosis not covered by another heuristic, or included in 
    the ExcludedDx_Code table. Exclude if:
    1.Same code on patient's current problem list prior to this encounter 
    2.Encounter with same code in past 36 months
    3.Past medical history list with same code 
    '''
    
    uri = 'urn:x-esphealth:heuristic:channing:vaersany_other_dx:v1'
    
    def __init__(self):
        self.name = 'Any other Diagnosis' # This is the EVENT name
        self.verbose_name = '%s as an adverse reaction to immunization' % self.name
        self.category = '2_possible'
        self.source = None
        self.ignore_period =  rules.MAX_TIME_WINDOW_POST_ANY_EVENT # months
        self.risk_period = rules.MAX_TIME_WINDOW_POST_EVENT
        self.risk_period_start = 1
        super(VaersHospProbHeuristic, self).__init__(self.name, verbose_name=self.verbose_name)
            
    @property
    def dx_codes(self):
        '''
        All dx codes that are not covered by another heuristic and are not 
        included in the ExcludedDx_Code table.
        @rtype: Dx_codes QuerySet
        '''        
        
        covered_dx_codes = DiagnosticsEventRule.objects.filter(heuristic_defining_codes__isnull=False).values('heuristic_defining_codes')
        excluded_dx_codes = ExcludedDx_Code.objects.values('code')
       
        dx_codes_qs = Dx_code.objects.exclude(combotypecode__in=covered_dx_codes)
        #TODO fix icd10 patched  for now
        dx_codes_qs = dx_codes_qs.exclude(code__in=excluded_dx_codes, type = 'ICD9')
        return dx_codes_qs

class VaersLxHeuristic(AdverseEventHeuristic):
    
    test_name_search_strings = [
            'hemog',
            'haemog',
            'hg',
            'hb',
            'white bl',
            'leuk',
            'leuc',
            'wbc',
            'neut',
            'pmn',
            'poly',
            'eo',
            'lymph',
            'plat',
            'plt',
            'thromboc',
            'cr',
            'bilirubin',
            'alk',
            'alp',
            'ptt',
            'plastin',
            'creat',
            'ck',
            'kinase',
            'cpk',
            'pot',
            'k',
            'sod',
            'na',
            'ca',

        ]
    
        
    def __init__(self, event_name, lab_type, criterion, pediatric):
        '''
        @param pediatric: Apply this heuristic to pediatric patients rather than adults?
        @type pediatric:  Bool (if false, apply to adults only)
        '''
        self.name = event_name
        self.lab_type = lab_type
        self.criterion = criterion
        if criterion:
            self.time_post_immunization = criterion['risk_period']
        else:
            self.time_post_immunization = rules.MAX_TIME_WINDOW_POST_LX
        self.pediatric = pediatric
        self.risk_period_start = 1
        super(VaersLxHeuristic, self).__init__(self.name, self.name)

    uri = 'urn:x-esphealth:heuristic:channing:vaerslx:v1'
    
    def event_heuristics(self):
        heuristics = []
        #
        # Any Result Tests
        #
        for test_name in [
            'hemoglobin',
            'wbc',
            'neutrophils',
            'eosinophils',
            'lymphocytes',
            'platelet_count',
            'creatinine',
            'alk',
            'ptt',
            'creatinine_kinase',
            'potassium',
            'sodium',
            'calcium',
            #'alt',
            #'ast',
            'bilirubin_total',
            
            ]:
            #AbstractLabTest
            heuristics.append(LabResultAnyHeuristic(test_name=test_name))
            
        return heuristics
      
    def get_all_names(self):
        '''
        Returns the set of all known Abstract Lab Test names, sorted alphabetically.
        '''
        
        names = set()
        h = self.event_heuristics()
        for heuristic in h :
            names.add(heuristic.alt.name)
        names = list(names)
        names.sort()
        return names
    
    
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
                
                
                self.lkv, self.lkd = lx.last_known_value(self.lab_codes, comparator)
                
                if not self.lkv: return False
                
                # could set it in another object 
                current_value = lx.result_float or lx.result_string or None
                
                assert float(current_value)
                assert float(self.lkv)
                
                equation = ' '.join([str(current_value), comparator, baseline.replace('LKV', str(self.lkv))])

                return eval(equation)
            except:
                self.lkv=None
                self.lkd=None
                return False

        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        trigger = self.criterion['trigger']
        comparator, baseline = self.criterion['exclude_if']
        
        # overwrite the lab codes with the codes in the mapping table
        self.lab_codes = LabTestMap.objects.filter(test_name__icontains=self.lab_type).values('native_code')
        
        candidates = LabResult.objects.following_vaccination(self.time_post_immunization,self.risk_period_start).filter(
            native_code__in=self.lab_codes,
            date__gte=begin, date__lte=end).distinct()
        #
        # Pediatric: 3mo - 18yrs
        # Adult 18yrs +
        
        if self.pediatric:
            candidates = candidates.filter(patient__date_of_birth__gt = F('date') - datetime.timedelta(days=6575))
            candidates = candidates.filter(patient__date_of_birth__lte = F('date') - datetime.timedelta(days=90))
        else: # adult
            candidates = candidates.filter(patient__date_of_birth__lte = F('date') - datetime.timedelta(days=6575))
        return [c for c in candidates if is_trigger_value(c, trigger) and not 
                excluded_due_to_history(c, comparator, baseline)]
    
    def generate(self, **kw):
        log.info('Generating events for %s' % self.name)
        counter = 0
        content_type = ContentType.objects.get_for_model(LabResult)
        comparator, baseline = self.criterion['exclude_if']
                        
        for lab_result in self.matches(**kw):
            try:
                result = lab_result.result_float or lab_result.result_string
                rule_explain =  'Lab %s resulting in %s'% (self.name, result)
                
                
                # Register which immunizations may be responsible for the event
                immunizations = Immunization.vaers_candidates(lab_result.patient,lab_result.date, self.time_post_immunization,['ALL'])
                assert len(immunizations) > 0
                
                # create a new event for each immunization date 
                # update if repeating labs
                for imm in immunizations:
                    try:
                        if Case.objects.get(date = imm.date,
                            patient = imm.patient).adverse_events.filter(matching_rule_explain__startswith='Lab %s'% (self.name)).exists():
                            #if there are, jump out of this iteration of the event generation loop -- one lab per type per case is sufficient
                            continue
                    except ObjectDoesNotExist:
                        ev, created = LabResultEvent.objects.get_or_create(
                                    gap = (lab_result.date - imm.date).days,                                       
                                    object_id =lab_result.pk,
                                    content_type = content_type,
                                    name = self.vaers_heuristic_name(),
                                    patient=lab_result.patient,
                                    defaults = {
                                        'matching_rule_explain': rule_explain,
                                        'category' : self.criterion['category'],
                                        'date' : lab_result.date,
                                        },
                                    )
                        
                        ev.version = rules.VAERS_VERSION
    
                        if lab_result.date < ev.date:
                            ev.date = lab_result.date
                        #calculating the last known value with value prior to vaccine
                        #self.lkv, self.lkd = has regular last known value  
                        ev.last_known_value, ev.last_known_date = lab_result.last_known_value(self.lab_codes, comparator, True,imm.date) 
                        #last_known_value will return a float or a string, depending  on the last known value.  
                        #but events require a float result
                        try:
                            float(ev.last_known_value)
                        except:
                            ev.last_known_value = None
                            ev.last_known_date = None                   
                            
                        ev.save()
                           
                        if created: 
                            counter += 1
                        
                        self.update_or_create_case(lab_result, imm, ev)
                
            except AssertionError:
                log.error('No candidate immunization for LabResult %s' % lab_result)
                #if we get an assertion error, ev can't have been initialized
                #log.warn('Deleting event %s' % ev)
                #ev.delete()
                #counter -= 1
            
        log.info('Created %d events' % counter)

        return counter

class VaersRxHeuristic(AdverseEventHeuristic):
    
    
    def __init__(self, event_name, criterion):
        
        self.name = event_name
        self.criterion = criterion
        self.risk_period_start = 0
        self.time_post_immunization = criterion['risk_period_days']
        super(VaersRxHeuristic, self).__init__(self.name, self.name)

    uri = 'urn:x-esphealth:heuristic:channing:vaersrx:v1'
    
    def vaers_heuristic_name(self):
        return 'VAERS: ' + self.name

    def matches(self, **kw):
               
        def excluded_due_to_history(rx):
            # some prescriptions do not require to exclude due to history
            if not self.criterion['exclude_due_to_history']:
                return False
            earliest = rx.date - relativedelta(months=12)
            prior_rx_qs = Prescription.objects.filter(
                    date__lt = rx.date, 
                    date__gte = earliest, 
                    patient = rx.patient,
                    name__icontains=self.name.split()[0], #just get the first word of the name, which is the drug itself.  
                    #This breaks if drug is two or more words, but current vaers prescriptions are all single compound single word drugs
                )
            
            if prior_rx_qs:
                return True
            else:
                return False
        
        begin = kw.get('begin_date') or EPOCH
        end = kw.get('end_date') or datetime.date.today()
        
        # risk period start is 0 so include same day                
        candidates = Prescription.objects.following_vaccination(self.time_post_immunization,self.risk_period_start).filter(
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
                immunizations = Immunization.vaers_candidates(rx.patient, rx.date, self.time_post_immunization,['ALL'])
                assert len(immunizations) > 0
                
                # create a new event for each immunization date 
                for imm in immunizations:
                
                    ev, created = PrescriptionEvent.objects.get_or_create(
                            gap = (rx.date - imm.date).days,
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
                    
                    ev.version = rules.VAERS_VERSION
                    
                    ev.save()
                    
                    if created: 
                        counter += 1
                        
                    self.update_or_create_case(rx, imm, ev)

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
    dx_codes = rule.heuristic_defining_codes.all()

    discarding_dx_codes = rule.heuristic_discarding_codes.all()

    if discarding_dx_codes:
        return Dx_CodeCorrelatedHeuristic(name, dx_codes, rule, discarding_dx_codes)
    else:
        return VaersDiagnosisHeuristic(name, dx_codes, rule)
    
def make_problem_heuristic(name):
    '''
    @type name: string
    '''
    
    rule = DiagnosticsEventRule.objects.get(name=name)
    dx_codes = rule.heuristic_defining_codes.all()

    discarding_dx_codes = rule.heuristic_discarding_codes.all()

    if discarding_dx_codes:
        return Dx_codePCorrelatedHeuristic(name, dx_codes, rule, discarding_dx_codes)
    else:
        return VaersProblemHeuristic(name, dx_codes, rule)
    
def make_hospprob_heuristic(name):
    '''
    @type name: string
    '''
    
    rule = DiagnosticsEventRule.objects.get(name=name)
    dx_codes = rule.heuristic_defining_codes.all()

    discarding_dx_codes = rule.heuristic_discarding_codes.all()

    if discarding_dx_codes:
        return Dx_CodeHCorrelatedHeuristic(name, dx_codes, rule, discarding_dx_codes)
    else:
        return VaersHospProbHeuristic(name, dx_codes, rule)
    
def make_lab_heuristics(lab_type):
    rule = rules.VAERS_LAB_RESULTS[lab_type]

    def heuristic_name(criterion, lab_name):
        return '%s %s %s' % (lab_name, criterion['trigger'], criterion['unit'])
    
    heuristic_list = []
    for criterion in rule['criteria_adult']:
        h = VaersLxHeuristic(heuristic_name(criterion, lab_type), lab_type,  criterion, pediatric=False)
        heuristic_list.append(h)
    for criterion in rule['criteria_pediatric']:
        h = VaersLxHeuristic(heuristic_name(criterion, lab_type), lab_type, criterion, pediatric=True)
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
        
    risk_period = rules.MAX_TIME_WINDOW_POST_EVENT
    #rule = AllergyEventRule.objects.get(name=allergy_type)
    rule = rules.VAERS_ALLERGIES[allergy_type]
   
    category =  '2_possible'
    heuristic_list = []
    h = VaersAllergyHeuristic(heuristic_name(allergy_type),rule, category, risk_period)
    heuristic_list.append(h)
    return  heuristic_list
        
def diagnostic_heuristics():
    heuristic_list = []
    for v in rules.VAERS_DIAGNOSTICS.values():
        heuristic_list.append( make_diagnosis_heuristic(v['name']) )
    any_other = AnyOtherDiagnosisHeuristic()
    heuristic_list.append(any_other)
    return heuristic_list

def problem_heuristics():
    heuristic_list = []
    for v in rules.VAERS_DIAGNOSTICS.values():
        heuristic_list.append( make_problem_heuristic(v['name']) )
    any_other = AnyOtherProblemHeuristic()
    heuristic_list.append(any_other)
    return heuristic_list

def hospprob_heuristics():
    heuristic_list = []
    for v in rules.VAERS_DIAGNOSTICS.values():
        heuristic_list.append( make_hospprob_heuristic(v['name']) )
    any_other = AnyOtherHospProbHeuristic()
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

