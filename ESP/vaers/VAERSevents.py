## use this - NOT identifyVAERS.py
## VAERSevents.py for espvaers
## we can reuse the esp_condition_icd9/loinc preLoader
## infrastructure - but of course we'll need to translate
## all the interesting test cpt codes into loinc on the way in so
## we can find them
## I guess we need an updated list of cpt code names and codes for this
## codeLife.py does generate that - about 10k codes all up for Atrius
## mostly without names!
##
## started january 11 2008 rml
## copyright ross lazarus 2008
## released under the LGPL v2 or any later version
##
## Basic idea is to follow each subject for 30 (or n) days after
## an exposure (vaccination initially but eventually rx or procedure)
## and look for out of range lab values or vital signs
##
##
## Will need a mysql table with rules encoded as something like:
##
## item        triggervalue    units      exclusion    riskperiod actcat
## hemoglobin  "<10"           "g/L"    ">LKV*0.8"        30       3
##
## need to extend each vaccination record
## with vital signs, icd9s and labs over the follow up period
## to apply all the rules
## added v 1 rules from Mike's document
## data structures seem to be working
## how to report?
## for pcp need this patient's trigger event and citation to rule
## history of trigger event
## all other history display on time line?
## population event rate by age and immtype?
## hmm. each rule could be keyed to these things

## rule: title, url, description, eventType, eventName,
## eventIncludeIf, eventExcludeIf, eventInterval
## ruleMatch: demogId, ruleId, matchName, matchValue, matchDate, matchHistory,
## immName, immDate, pcpId, wfStatus, wfId, vaersId, eId,
## ruleWorkFlow: ruleMatchId, newStatus, newStatusDate, operator, comment
##
## the critical data to present are the trigger
## other non trigger historical values


import os, sys
import django, MySQLdb
import time, datetime
import copy, logging
import pdb

sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

progname = os.path.split(sys.argv[0])[-1]

import utils

from esp.models import Immunization
from esp.models import *
from django.db.models import Q
from django.db import connection

import rules

NOW = datetime.datetime.now()
EPOCH = NOW - datetime.timedelta(days=3*365)


cursor = connection.cursor()

EXCLUDESURNAME = 'XBALIDOCIOUS'
ONEYEARDT = datetime.timedelta(365.25)
ZERODT = datetime.timedelta(0)
RuleCatLookup = {'zero':'0', 'one':'1','two':'2','three':'3','four':'4'}
DAYSTOWATCH=30 # for now
MAXGAPDT = datetime.timedelta(days=DAYSTOWATCH)
TEMPTOREPORT = 100.4 # degrees are F in our records, 38C = 100.4F
TEMPGAPTOREPORT = 7 # temp reports only for 1 week post imm
DGAP = datetime.timedelta(days=DAYSTOWATCH)
TEMPGAP = datetime.timedelta(days=TEMPGAPTOREPORT) # for testing
ICD_KEY = 'icd9s'
FEVER_KEY = 'allfevers'
ENC_KEY = 'allenc'
LX_KEY = 'allLx'
LXCN_KEY = 'LxComponentName'
LXRES_KEY = 'LxTest_results'
LXDATE_KEY = 'LxDate_of_result'
IMMPATIENTID_KEY='ImmPatient_id'
IMMDATE_KEY = 'ImmDate'
IMMNAME_KEY = 'ImmName'
IMMCODE_KEY = 'ImmType'
IMMDOSE_KEY = 'ImmDose'
IMMMANUF_KEY = 'ImmManuf'
IMMLOT_KEY = 'ImmLot'
IMMID_KEY = 'ImmRecId'
IMMDATE_KEY = 'ImmDate'
DEMDOB_KEY = 'DemogDate_of_Birth'
DEMRACE_KEY = 'DemogRace'
DEMGEND_KEY = 'DemogGender'
DEMMRN_KEY = 'DemogMedical_Record_Number'
DEMSN_KEY = 'DemogLast_Name'
DEMFN_KEY = 'DemogFirst_Name'


ID_KEY = 'id'
ENCTEMP_KEY = 'EncTemperature'
ENCDATE_KEY = 'EncEncounter_Date'

espdb = MySQLdb.Connect(settings.DATABASE_HOST, settings.DATABASE_USER, settings.DATABASE_PASSWORD)
sql = 'use %s' % settings.DATABASE_NAME

curs = espdb.cursor() # use default cursor
dcurs = espdb.cursor(cursorclass=MySQLdb.cursors.DictCursor)
d2curs = espdb.cursor(cursorclass=MySQLdb.cursors.DictCursor)

d2curs.execute(sql)
curs.execute(sql)
dcurs.execute(sql)
# parse tables from Mike's rule spec document into internal tables
# this module provides rules as simple structures
#from vaersRules import *

# vaersRules.py
# parse tables from Mike's rule spec document into internal tables
# this module provides rules as simple structures
assert MySQLdb.apilevel == "2.0"

from MySQLdb.cursors import DictCursor
from MySQLdb.cursors import SSDictCursor,SSCursor

ntoinsert = 500



class iterCursor:
    '''Fake a cursor in MySQL
    Iterable results from a mysql connection
    this one doesn't suck (literally) the entire
    record set into ram - a stoopid thing to do when
    there are millions of records - and not much ram
    SSCursor is the thing it seems'''

    def __init__(self, connection, query, data = None):
            self._cursor = connection.cursor(SSCursor)
            if data:
                self._cursor.execute(query, data)
            else:
                self._cursor.execute(query)
                
    def __iter__(self):
            while True:
                    result = self._cursor.fetchone()
                    if not result: 
                        raise StopIteration
                    yield result


class AllFever:
    """iterator that returns any fevers with dates - are they seasonal?
    """
    def __init__(self,ps='01012007',pe='31122007'):
        """return a date for every fever in the period
        """
        self.ps = ps
        self.pe = pe


    def __iter__(self):
        """ setup and yield every matching instance
        """
        sql = """select EncEncounter_Date,EncTemperature from esp.esp_enc where EncEncounter_Date > '%s' and EncEncounter_Date <= '%s'
        and round(EncTemperature) > %f order by EncEncounter_Date""" % (self.ps,self.pe,TEMPTOREPORT)
        fevents = iterCursor(espdb,sql)
        for e in fevents:
            edate = e[0]          
            try:
                etemp = float(e[1].strip())          
            except:
                etemp = None
            if (etemp and len(edate) >= 8):
                if (etemp > TEMPTOREPORT): # any within gap?
                    yield edate,etemp
 
class AllImm:
    """iterator that returns any imms with dates - are they seasonal? 
    """
    def __init__(self,ps='01012007',pe='31122007'):
        """return a date for every fever in the period 
        """
        self.ps = ps
        self.pe = pe
        
    def __iter__(self):
        """ setup and yield every matching instance
        """
        sql = """select ImmDate from esp.esp_immunization where ImmDate > '%s' and ImmDate <= '%s'""" % (self.ps,self.pe)
        ievents = iterCursor(espdb,sql)
        for i in ievents:
            idate = i[0]          
            if (len(idate) >= 8):
                yield idate
 



class FeverEvents:
    """iterator that returns details ready for saving for each fever for a given patient and period 
    """
    def __init__(self,dId=None,iDate=None,lastDate=None,iD=None,iName=None,
                      encIdlist=[],
                      casedef="Fever >= 38.2C/102F within 1 week of any vaccination",
                      casename="VAERS/ESP Fever adverse event",demog={}):
        """return a list of event dicts containing the 
        """
        self.demog = demog
        self.dId = dId
        self.iDate = iDate
        self.lastDate = lastDate
        self.iD = iD
        self.iName = iName
        self.encIdlist=encIdlist
        self.casedef = casedef
        self.casename = casename
        self.curs = espdb.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = 'use %s' % settings.DATABASE_NAME
        self.curs.execute(sql)
        comment = """VAERS fever defined as temp >= %d within %d days of any vaccination was
        detected by %s at %s""" % (TEMPTOREPORT, TEMPGAPTOREPORT, progname, timenow())
        
    def __iter__(self):
        """ setup and yield every matching instance
        """
        sql = """select * from esp.esp_enc where EncPatient_id = %d
        and EncEncounter_Date > %s and EncEncounter_Date <= %s
        order by EncEncounter_Date""" % (self.dId,self.iDate,self.lastDate)
        caseComments = """ESP.VAERS report automatically created by %s on %s. Case of %s, defined
        as %s""" % (progname, timenow(),self.casename,self.casedef)
        self.curs.execute(sql) # get ALL temps for period of interest
        allenc = self.curs.fetchall()
        for e in allenc:
            edate = e[ENCDATE_KEY]
            try:
                etemp = float(e[ENCTEMP_KEY].strip())
            except:
                etemp = None
            if (etemp and len(edate) >= 8):
                edatetime = makeD(edate)
                igap = (edatetime - self.iD).days
                if (ZERODT < (edatetime - self.iD) <= TEMPGAP) and (etemp > TEMPTOREPORT): # any within gap?
                    yield edate,etemp,igap # these are added to the rest of the patient/imm details and in turn yielded to a simple file writer
 

class ICD9Events:
    """iterator that returns details ready for saving for each VAERS relevant ICD9 diagnosis for a given patient and period 
    returns erule,ecat,edate,ecode,ecodename,precedingdate and reasons for exclusion if any are found.
    """
    def __init__(self,dId=None,iDate=None,iD=None,iName=None,icdKeepdict=None):
        """return a list of icd9 details for matches to vaers rules
        """
        self.icdKeepdict = icdKeepdict
        self.RuleCatLookup = RuleCatLookup
        self.dId = dId
        self.iD = iD
        self.iDate = iDate
        ld = iD + MAXGAPDT # last icd9 to check is 30 days after vacc
        self.lastDate = '%04d%02d%02d' % (ld.year,ld.month,ld.day)
        fd = iD - ONEYEARDT # first is a year before vacc
        self.firstDate = '%04d%02d%02d' % (fd.year,fd.month,fd.day)
        self.iName = iName
        self.curs = espdb.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        
    def __iter__(self):
        """ setup and yield icds that match a vaers case criterion within 30 days of vaccination
        If multiples, report the first
        check for previous code before vaccination
        """
        print 'ICD9Events'
        
        icdKeepdict = self.icdKeepdict # local for quick access
        RuleCatLookup = self.RuleCatLookup
        sql = '''select icd9,encId,demogId,encDate from esp.icd9Fact where demogId = %d and 
        encDate <= '%s' order by encDate desc''' % (self.dId,self.lastDate) # do we want latest first
        self.curs.execute(sql) # get ALL encounters
        allicd9s = self.curs.fetchall() # post vaccination event icd9s
        allicd9s = list(allicd9s)
        keepcodes = {}
        allcodes = {}
        exclhits = {}
        trigger = {}
        for diag in allicd9s: # if desc, we have latest first
            code = diag['icd9']
            dDate = diag['encDate']
            allcodes.setdefault(code,[]) # we must check *all* icd9s for exclusions later for this patient
            allcodes[code].append((code,dDate)) # remember for exclusion checking
            icdtrans,excludes,cat,checksamelast12 = icdKeepdict.get(code,(None,None,None,None)) # only keep if found
            # TODO replace x == code with a regexp to deal with 400.3 matching 400*
            if icdtrans: # make a dict to be written if one is within period
                exclhits.setdefault(code,[]) # store reasons to exclude here as narrative and flag
                dD = makeD(dDate)
                if not dD:
                    logging.warn('##bad encounter date %s in ICD9events,  demogId %s,  date %s, diag=%s' % ('encDate',self.dId,self.iDate,diag))
                else:
                    if (ZERODT < (dD - self.iD) <= MAXGAPDT): # within maxgap AFTER imm
                        if not keepcodes.get(code,None): # in case is first within 30 days
                            keepcodes[code] = [] 
                            trigger[code] = dD # keep trigger encdate for checking last 12 months
                        keepcodes[code].append(diag) # retain all if any within 30 days to check for > 12 months
                    else: # not within watching period, but must be within past 12/12
                        if checksamelast12:
                            estring = '#********Nothing last 12/12'
                            if (ZERODT < (self.iD - dD) <= ONEYEARDT):
                                estring = 'SameWithinLastYearOn%s' % dDate
                                exclhits[code].append(estring)
                            logging.info(estring)
        for code in keepcodes.keys(): # now have list of diag records in encDate order
            icdtrans,excludes,cat,checksamelast12 = icdKeepdict.get(code,(None,None,None,None))
            dictexcl = dict(zip(excludes,excludes)) # for faster lookup
            exclhits[code] += ['%s_%s' % (x[0],x[1]) for x in allcodes[code] 
              if dictexcl.get(x[0],None)] # test all codes against exclude list 
            for diag in keepcodes[code]: # may be multiple within period
                dDate = diag['encDate']
                dD = makeD(dDate)
                igap = (dD - self.iD).days # gap to rule
                if len(exclhits[code]) == 0: # no reason to exclude
                    yield ('Diag_%s' % code, cat, dDate, code, icdtrans,'',igap) 
                # erule,ecat,edate,ecode,ecodename,precedingdate = icdevent
                else:
                    slog = '# *** Diag %s excluded %s for id %s %s on %s' % (icdtrans,';'.join(exclhits[code]),
                      self.dId,self.iName, self.iDate)
                    logging.info(slog)

class LxEvents:
    """iterator that returns details ready for saving for each VAERS relevant lab result for a given patient and period 
    returns erule,ecat,edate,ecode,ecodename,precedingdate and reasons for exclusion if any are found.

    """
    def __init__(self,dId=None,iDate=None,iD=None,iName=None,lxKeepdict=None):
        """return a list of Lx details for matches to vaers rules
        """
        self.lxKeepdict = lxKeepdict
        self.RuleCatLookup = RuleCatLookup
        self.dId = dId
        self.iD = iD
        self.iDate = iDate
        ld = iD + MAXGAPDT # last lab to check is 30 days after vacc
        self.lastDate = '%04d%02d%02d' % (ld.year,ld.month,ld.day)
        self.iName = iName
        self.curs = espdb.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        
    def __iter__(self):
        """ setup and yield icds that match a vaers case criterion within 30 days of vaccination
        store all previous values for same test to determine LKV - last known value before the vaccination (?)
        This makes sense I guess, but only if it's before vaccination since if a lab value changes during the 
        surveillance window in multiple tests before reaching the rule threshold, we really want to compare the trigger value
        with the value before the exposure I think...
        """
        lxKeepdict = self.lxKeepdict
        RuleCatLookup = self.RuleCatLookup
        sql = '''select * from esp.esp_lx where LxPatient_id = %d and 
        LxDate_of_result <= '%s' order by LxDate_of_result desc''' % (self.dId,self.lastDate) # do we want latest first
        self.curs.execute(sql) # get ALL encounters
        allrecs = self.curs.fetchall() # post vaccination event icd9s
        allrecs = list(allrecs)
        keepcodes = {}
        allcodes = {} # need to check for excludes
        trigger = {}
        exclhits = {}
        keeplx = []
        alldtvalues = {}
        lkv = {} # first pre-immunization for each n
        for lxrec in allrecs: # unpack each lx and add test/results to res
            n = lxrec[LXCN_KEY].lower()
            v = lxrec[LXRES_KEY]
            d = lxrec[LXDATE_KEY]
            if d.strip() > '':
                (thresh,excl,actcat) = lxKeepdict.get(n,(None,None,None)) # we store string tests eg >3
                ## TODO add rule/condition stuff here
                if thresh: # is one we're interested in
                    lxD = makeD(d)
                    if not lxD:
                        logging.warn('##bad lx date %s in lxres %s' % (d,lxrec))
                    else:
                        alldtvalues.setdefault(n,{}) # set up this codes dt dict empty
                        was = alldtvalues[n].get(lxD,None) # make sure not there yet for this date
                        if was:
                            logging.warn('### Duplicate value for demogid %s for lx code %s was %s on %s. Last will win' % (self.dId, n, v, d))
                            # updated
                        else:
                            alldtvalues[n][lxD] = (v,lxrec) # we complain, but take the first (latest!) one. Is this sane?
                        if not lkv.get(n): # not yet seen
                            if lxD < self.iD: # is first one before imm = LAST KNOWN VALUE -> lkv
                                try: # sometimes the values are at the start of a longer string
                                    fv = v.split()[0]
                                    lxval = float(fv) # deal with 3.7 H or whatever
                                    lkv[n] = (d,v,fv)
                                except:
                                    logging.warn('### Unable to test LKV for %s lxval=%s' % (n,v))
        for n in alldtvalues: # rerun all the interesting ones to check values and exclusions
            (thresh,excl,cat) = lxKeepdict.get(n,(None,None,None)) # we store string tests eg >3
            datek = alldtvalues[n].keys()
            datek.sort()
            datek.reverse() # start with latest records to find trigger first
            lkdate,lkvalue,lkfv = lkv.get(n,(None,None,None))
            triggerdtval = None
            for lxD in datek: # in descending order
                (v,lxrec) = alldtvalues[n][lxD]
                lxdate = '%04d%02d%02d' % (lxD.year,lxD.month,lxD.day)
                if ZERODT < (lxD - self.iD) <= MAXGAPDT: # within gap days of intervention
                    igap = (lxD - self.iD).days
                    try: # sometimes the values are at the start of a longer string
                        lxval = float(v.split()[0]) # deal with 3.7 H or whatever
                    except:
                        logging.warn('Unable to test lxval=%s' % v)
                        lxval = None
                    if lxval:
                        e = '%s %s' % (lxval,thresh) # add condition to value - eg -> "10 < 11"  - a python expression
                        if excl:
                            if lkvalue:
                                ex = excl.replace('LKV','%s' % lkfv) # so "LKV < 0.8X" becomes an expression
                                esl = ex.split()# get rid of 'X' and replace with lxval                            
                                esl[0] = '%s' % lxval # so expression makes sense - eg "0.7 < (0.9*0.8)" 
                                e = '%s and not (%s)' % (e,' '.join(esl))
                            else:
                                logging.warn('###missing LKV for testing %s for %s' % (excl,n))
                        if eval(e): # neat
                            s = 'Value %s for %s passed test %s' % (v,n,e)
                            if not lkvalue:
                                s = 'Value %s for %s passed test %s but no LKV available for testing' % (v,n,e)
                            yield ('Lx_%s' % n, cat, lxdate,n,n,s,igap) 
                            # erule,ecat,edate,ecode,ecodename,precedingdate = icdevent
                            # we seem to be getting multiple wbc's < 1 on the same date?
                        else:
                            s = 'Value %s for %s failed test %s exclude %s' % (v,n,thresh,e)
                            # yield ('Lx_%s excluded' % n, cat, lxdate, n, n, s, igap)
                            #logging.info(s)
  
            


def post_imm_events(start_date, end_date):
    # Find all patients vaccinated in the period defined by start/end date
    # For each patient, look for encounters with interesting icd9 codes
    # For each interesting icd9 code, check if exception rules apply.
    # If exception rules do NOT apply, add to list of reportable events
    patients = Immunization.patients_vaccinated_in_period(start_date, end_date)
    
    print patients


def match_icd9_expression(icd9_code, expression_to_match):
    '''
    considering icd9 rules to be:
    - A code: 558.3
    - An interval of codes: 047.0-047.1
    - A regexp to represent a family of codes: 320*
    
    this function verifies if icd9_code matches a rule
    '''

    def transform_expression(expression):
        if '-' in expression:
            # It's an expression to show a range of values
            low, high = expression.split('-')
            if '*' in low: low = low.replace('*', '.0')
            if '*' in high: high = high.replace('*', '.9')
            
        if '*' in expression and '-' not in expression:
            low, high = expression.replace('*', '.0'), expression.replace('*', '.9')
            
        if '*' not in expression and '-' not in expression:
            raise ValueError, 'not a valid icd9 expression'


    # We must get two regular codes in the end.
    ll, hh = float(low), float(high)    
    assert(type(ll) is float)
    assert(type(hh) is float)
    
    return ll, hh
            
    
    def match_precise(code, expression):
        return code == expression
    
    def match_range(code, lower_bound, greater_bound):
        return lower_bound <= code <= greater_bound

    def match_regexp(code, regexp):
        lower_bound, higher_bound = transform_expression(regexp)
        return match_range(code, lower_bound, greater_bound)


    try:
        target = float(icd9_code)
    except ValueError:
        raise ValueError, 'icd9_code is not valid'

    try:
        expression = float(expression_to_match)
        return match_precise(target, expression)
    except ValueError:
        # expression_to_match is not a code
        return match_regexp(target, expression_to_match)
        
        
    

    
        
        

def diagnosis_by_code(icd9_code):
    # Check all rules, to see if the code we have is a possible adverse event
    for key in rules.ADVERSE_EVENTS.DIAGNOSTICS.keys():
        codes = key.split(';')
        # for all the codes that indicate the diagnosis, we see if it matches
        # It it does, we have it.
        for code in codes:
            if match_icd9_expression(icd9_code, code):
                return rules.ADVERSE_EVENTS_DIAGNOSTICS[key]

    # Couldn't find a match
    return None
        

def diagnosis_codes():
    '''
    Returns a set of all the codes that are indicator of diagnosis
    that may be an adverse event.
    '''
    codes = []
    for key in rules.ADVERSE_EVENTS_DIAGNOSTICS.keys():
        codes.extend(key.split(';'))
    return set(codes)


def exclusion_codes(icd9_code):
    '''
    Given an icd9 code represented by event_code, returns a list of
    icd9 codes that indicate that the diagnosis is not an adverse
    event
    '''
    diagnosis = diagnosis_by_code(icd9_code)
    return (diagnosis and diagnosis.get('ignore_codes', None))

def vaers_encounters(start_date=None, end_date=None):
    import pdb
    start_date = start_date or EPOCH
    end_date = end_date or NOW
    all_vaers_encounters = []
    pdb.set_trace()
    for code in diagnosis_codes():
        encounters = Enc.objects.filter(EncEncounter_Date__gte=start_date,
                                        EncEncounter_Date__lte=end_date,
                                        EncICD9_Codes__icontains=code)
        if encounters: all_vaers_encounters.extend(encounters)
            
    return all_vaers_encounters
    

        
class PostImmEvents:

    """return interesting icd9, lx and vitals from encounters within MAXGAP days of a
    vaccination date adding to the res dict for each subject
    Also need previous 12/12 or last known value for some rules

    TODO: change over to use the icd9Fact table after ensuring it's always
    being updated when new encounters arrive
    
    out for every record
    immdate, immcode, immname, immbatch, immman,
    demogid, age, gender, race, 
    rule, category, ruledate, rulecode, rulename
    
    for lx, 
    precedingdate, precedingvalue
    for icd
    precedingdate
    """


    def __init__ (self, sps=None, spe=None, delim='\t', missval=''):
        self.sps = sps if type(sps) is str else datetime.datetime.strftime(sps, '%Y%m%d')
        self.spe = spe if type(spe) is str else datetime.datetime.strftime(spe, '%Y%m%d')

        self.missval = missval
        self.outhead = ['immdate','immcode','immname','immbatch','immmanuf', 'demogid','age','gender','race','rule',
        'category', 'ruledate','idaysafter','rulecode','rulecodename','precedingdate','precedingvalue']
        self.imm_events = Immunization.manager.patients_vaccinated_in_period(self.sps, self.spe)


    def __iter__(self):
        """ iterator yields records to be written as rows 
        Finds all immunizations for a period, groups them by patient_date, and checks each one against all the
        icd9, lx and fever based case criteria, yielding a complete record for a simple file writer.
        """


        outheader = self.outhead
        icdrec,icdKeepdict, lxcat, lxKeepdict = getRules() # TODO from db eventually

        try:
            ps = makeD(self.sps) # period start string to datetime
            pe = makeD(self.spe)
        except:
            s = '#!!! Bad period start %s or period end %s in getPostImmDetails' % (self.sps,self.spe)
            logging.critical(s)
            raise StopIteration



        idImmDate = {}
        logging.info('got %d imm records for period %s to %s' % (len(self.imm_events), self.sps, self.spe))

        for event in self.imm_events: # create a dict in case subject has multiple imms on one date for vaers
            iId = event.ImmRecId # imm recid
            dId = int(event.ImmPatient.id) # demogId
            iDate = event.ImmDate
            iName = event.ImmName
#            iCode = nr[IMMCODE_KEY]
            
            iBatch = event.ImmLot
            iManuf = event.ImmManuf
            iD = event.ImmDate
            k = '%d_%s' % (dId,iDate) # hash key for each record - but may be multiple imms on a given visit
            idImmDate.setdefault(k,[])
            idImmDate[k].append((dId,iDate,iId,iName,iD,iCode,iBatch,iManuf)) # often multiple
        currentdId = None
        for nr,immlist in enumerate(idImmDate.values()): # list of imms by id
            # gives a list of imms on that date for that subject
            if (nr+1) % 1000 == 0:
                logging.info('#@@@@ At id_date %d of %d' % (nr,len(idImmDate.values()))) 
            dId,iDate,iId,iName,iD,iCode,iBatch,iManuf = immlist[0] # deal with others in loops below
            # get demog record
            if currentdId <> dId: # need new demog - lookup
                sql = '''select * from esp_demog where id = %d''' % (dId)
                d2curs.execute(sql)
                idrec = d2curs.fetchall()
                if len(idrec) > 0:
                    currentdId = dId
                    mrn = idrec[0][DEMMRN_KEY]
                    demog = idrec[0]
                    gender = demog[DEMGEND_KEY]
                    race = demog[DEMRACE_KEY]
                    dobdt = makeD(demog[DEMDOB_KEY])
                    sn = demog[DEMSN_KEY]
                    if sn.upper()[:2] == EXCLUDESURNAME[:2]:
                        fn = demog[DEMFN_KEY]
                        logging.info('#$$$$ patient id %s surname %s %s excluded - assumed to be a test case starting with %s' % (dId,
                        sn,fn,EXCLUDESURNAME))
                    if dobdt:
                        age = '%d' % int((iD - dobdt).days/365.25)
                else:
                    logging.warn('### unable to find demog record id %d' % dId)
                    mrn = '?'
                    age = '?'
                    race = gender = '?'
                    break # stop processing - no demog so cannot report anything..
            ld = iD + MAXGAPDT
            lastDate = '%04d%02d%02d' % (ld.year,ld.month,ld.day) 
            ld = iD + TEMPGAP
            lasttDate = '%04d%02d%02d' % (ld.year,ld.month,ld.day)
            if not iD:
                logging.critical('##bad %s in r=%s' % (IMMDATE_KEY,r))
            else:
                event = dict(zip(outheader,[self.missval for x in outheader])) # new dict for this person's events
                #  ['immdate','immcode','immname','immbatch','immmanuf', 'demogid','age','gender','race','rule',
                # 'category', 'ruledate','rulecode','rulecodename','precedingdate','precedingvalue']

                event['demogid'] = mrn
                event['age'] = age
                event['gender'] = gender
                event['race'] = race
                
                # find and report any ICD9 based cases
                icdIter = ICD9Events(dId=dId, iDate=iDate, iD=iD, iName=iName,icdKeepdict=icdKeepdict) 
                for icdevent in icdIter:
                    erule,ecat,edate,ecode,ecodename,precedingdate,igap = icdevent
                    event['ruledate'] = edate
                    event['rulecode'] = ecode
                    event['rulecodename'] = ecodename
                    event['category'] = ecat
                    event['rule'] = erule
                    event['precedingdate'] = precedingdate
                    event['idaysafter'] = '%d' % igap
                    for ilist in immlist: # for each patient_date - often multiple
                        dId,iDate,iId,iName,iD,iCode,iBatch,iManuf = ilist
                        event['immdate'] = iDate
                        event['immcode'] = iCode
                        event['immname'] = iName
                        event['immbatch'] = iBatch
                        event['immmanuf'] = iManuf
                        row = [event.get(hname,self.missval) for hname in outheader]
                        yield row
                
                # find and report any Lx based cases
                LxIter = LxEvents(dId=dId, iDate=iDate, iD=iD, iName=iName,lxKeepdict=lxKeepdict)
                for lxevent in LxIter:
                    erule,ecat,edate,ecode,ecodename,precedingdate,igap = lxevent
                    event['ruledate'] = edate
                    event['rulecode'] = ecode
                    event['rulecodename'] = ecodename
                    event['category'] = ecat
                    event['rule'] = erule
                    event['precedingdate'] = precedingdate
                    event['idaysafter'] = '%d' % igap
                    for ilist in immlist: # for each patient_date - often multiple
                        dId,iDate,iId,iName,iD,iCode,iBatch,iManuf = ilist
                        event['immdate'] = iDate
                        event['immcode'] = iCode
                        event['immname'] = iName
                        event['immbatch'] = iBatch
                        event['immmanuf'] = iManuf
                        row = [event.get(hname,self.missval) for hname in outheader]
                        yield row
                
                # find and report any fever based cases
                event['precedingdate'] = ''
                event['rulecodename'] = 'Temperature'
                event['category'] = 'zero'
                event['rule'] = 'Fever'
                feventIter = FeverEvents(dId=dId, iDate=iDate,lastDate=lasttDate, iD=makeD(iDate), iName=iName,
                               demog = idrec) # list of fever event dicts for this subject
                for fevent in feventIter:
                    fdate,fval,igap = fevent
                    event['ruledate'] = fdate
                    event['rulecode'] = '%4.2f' % fval
                    event['idaysafter'] = '%d' % igap
                    for ilist in immlist: # for each patient_date - often multiple
                        dId,iDate,iId,iName,iD,iCode,iBatch,iManuf = ilist
                        event['immdate'] = iDate
                        event['immcode'] = iCode
                        event['immname'] = iName
                        event['immbatch'] = iBatch
                        event['immmanuf'] = iManuf
                        row = [event.get(hname,self.missval) for hname in outheader]
                        yield row

def timenow():
    """return current time as a string
    """
    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))


def setLogging(appname=''):
    """setup a logger
    """
    logdir = './'
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
    today=datetime.datetime.now().strftime('%Y%m%d')
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=os.path.join(logdir,'%s_%s.log' % (appname,today)),
                filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-4s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def getRules(): # setup some rule structures
    """this will eventually be done with conditions - rules - one
    per set of criteria.

    """

    # match_lxs contains the indicators of lab results that, given the values of interest, result in a report action.
    
    # The table comes from spec in 
    # http://esphealth.org/trac/ESP/attachment/wiki/VaccineAdverseEventCriteria/ESP-VAERS%20algorithm%20v1%20_2007-11-05_-1.pdf

    matchlxs = """item	triggervalue	units	exclusion	actcat
Hemoglobin	<10	g/L	X > (LKV*0.8)	Three
HB	<10	g/L	X > (LKV*0.8)	Three
WBC	<3.5	x109/L	X > (LKV*0.7)	Three
white blood	<3.5	x109/L	X > (LKV*0.7)	Three
Neutrophil	< 2000	x109/L	X > (LKV*0.7)	Three
Eos	> 600	x109/L	X < (LKV*1.2)	Three
Lymph	< 1000	x109/L	X > (LKV*0.7)	Three
Platelet	< 150	x109/L	X > (LKV*0.7)	Three
plt count	< 100	x109/L	X > (LKV*0.7)	Two
Creatinine	> 1.5	mg/dL	X < (LKV*1.3)	Three
ALT	>120	IU/L	X < (LKV*1.3)	Three
alanine	>120	IU/L	X < (LKV*1.3)	Three
SGPT	>120	IU/L	X < (LKV*1.3)	Three
AST	>100	IU/L	X < (LKV*1.3)	Three
aspartate	>100	IU/L	X < (LKV*1.3)	Three
SGOT	>100	IU/L	X < (LKV*1.3)	Three
Bili	>2.0	mg/dL	X < (LKV*1.2)	Three
ALK	>200	IU/L	X < (LKV*1.3)	Three
PTT	>60	s	X < (LKV*1.3)	Three
Thromboplastin	>60	s	X < (LKV*1.3)	Three
Creatine kinase	>500	U/L	X < (LKV*1.3)	Three
ck	>500	U/L	X < (LKV*1.3)	Three
Glucose	>200	mg/dL	X < (LKV*2.0)	Three
Potassium	>5.5	mmol/L	X < (LKV + 0.5)	Three
Sodium	>150	mmol/L	X < (LKV + 5)	Three
Sodium	<130	mmol/L	X > (LKV - 5)	Three"""


    # FIXME: Why not turn the whole matchlxs directly into the proper
    # data structure and put in a separate module?? Less code to maintain...
    m = matchlxs.split('\n')
    m = [x.strip().split('\t') for x in m]
    

    lxheader = m[0]
    lxheader.append('ImmName')

    # matchme contains the list of lab results that are of interest.
    matchme = m[1:]


    matchlist = []
    for row in matchme:
        if len(row) >= 5:
            matchlist.append(row)
        else:
            logging.critical('### lx config row short - %s' % row)
    matchlist = [[x[0],x[1],x[2],x[3],RuleCatLookup.get(x[4].lower(),0),'*'] for x in matchlist] # add any imm
    
    lab_item_names = [x[0].lower() for x in matchlist] # get names we need

    
    
    lab_item_thresholds = [x[1] for x in matchlist] # for eval later

    lab_item_exclusion_criteria = [x[3] for x in matchlist] # for eval later
    lxcat = dict(zip([x[0] for x in matchlist],[x[4] for x in matchlist])) # lookup
    
    lxlookup = [(x[1],x[3],x[0]) for x in matchlist] 
    lxKeepdict = dict(zip(lab_item_names,lxlookup)) 


    
    logging.info('# note lxkeep = %s' % ','.join(lxKeepdict.keys()))

    matchicds = """RuleTranslation	RuleICD9	RuleExcludes	RuleCategory	Rulesource
Guillain-Barre	357.0	Same code within past 12 months	Two	Menactra
Bell's palsy	351.0	Same code within past 12 months	Two	Menactra
Seizures	345.*; 780.3	None	Two	Menactra
Seizures (RotaTeq)	779.0; 333.2	None	Two	RotaTeq
Febrile seizure 	780.31	None	Two	MMR-V
Ataxia	052.7; 334.4; 781.2; 781.3	Same code within past 12 months	Two	MMR-V
Encephalitis	323.9; 323.5; 055.0; 052.0	Same code within past 12 months	Two	MMR-V
Arthritis	714.9; 716.9; 056.71	Same code within past 12 months	Two	MMR-V
Allergic urticaria	708.0	Same code within past 12 months	Two	MMR-V
Angioneurotic edema	995.1	Same code within past 12 months	Two	MMR-V
Anaphylactic shock due to serum	999.4	Same code within past 12 months	Two	MMR-V
Intussusception	543.9; 560.0	Same code within past 12 months	Two	RotaTeq
GI bleeding	569.3; 578.1; 578.9 004*, 008*, 204-208*, 286*, 287*, 558.3, 800-998* ever or same code within past 12 months   Two	RotaTeq
Meningitis / encephalitis	047.8; 047.9; 049.9;321.2; 322*;323.5;323.9	047.0-047.1, 048*, 049.0-049.8, 053-056*, 320* ever or same code within past 12 months	Two	RotaTeq
Myocarditis	429.0; 422*	Same code within past 12 months	Two	RotaTeq
Hypersensitivity - drug, unspec	995.20	None	Three
Pneumonitis - hypersensitivity	495.9	None	Three
Upper respiratory tract hypersensitivity reaction	478.8	None	Three
Poisoning - bacterial vaccine	978.8	None	Three
Poisoning - mixed bacterial (non-pertussis) vaccine	978.9	None	Three
Infection due to vaccine	999.39	None	Three
Post-immunization reaction	999.5	None	Three
Myelitis - post immunization	323.52	None	Three
Encephalitis / encephalomyelitis - post immunization	323.51	None	Three"""

# matching '008*' becomes re.match('008.*',x) and is easy
# matching '047.0-047.1' implies a range, so probably need something like
# 47.0 < float(x) < 47.1 which assumes that the decimals are in all icd9 codes

    sb4='Same code within past 12 months'

    m = matchicds.split('\n')
    matchmelist = [x.strip().split('\t') for x in m]
    #print '## matchmelist = ',matchmelist[:5]
    icdheader = matchmelist[0]
    matchText = matchmelist[1:]
    matchlist = []
    for i,row in enumerate(matchText):
        if len(row) >= 4:
            if 4 <= len(row) < 5:
                row.append('') # some have no last field from this cut'n'paste out of word :)
            matchlist.append([row[0],row[1],row[2],RuleCatLookup.get(row[3].lower(),row[3]),row[4]])
    keepme = []
    excludeme = []
    #print '## matchlist = ',matchlist[:5]
    for i,row in enumerate(matchlist): # deal with ranges and such for matches TODO do same for exclusions
        excludeme = row[2].split(',')
        checkSameLast12 = 0
        if excludeme[-1].lower().find('same code within past 12 months') <> -1:
            checkSameLast12 = 1
            if len(excludeme) == 1:
                excludeme = []
            else: # hack - works for now as all with codes have >1
                excludeme[-1] = excludeme[-1].split()[0] # get rid of all but first part of very last one
        icdkeeplist = row[1].split(';')
        if len(icdkeeplist) > 1:
            for icd in icdkeeplist: # add a record for each code
                newrow = copy.copy(row)
                newrow[2] = excludeme
                newrow[1] = icd.strip()
                newrow.append(checkSameLast12)
                keepme.append(newrow)
        elif len(icdkeeplist) == 1:
            newrow = copy.copy(row)
            newrow[1] = icdkeeplist[0]
            newrow[2] = excludeme
            newrow.append(checkSameLast12)
            keepme.append(newrow)

    icdkeepmatch = [x[1] for x in keepme] # get names we need
    
    # row has 
    # RuleTranslation  RuleICD9    RuleExcludes RuleCategory    Rulesource
    icdrec = [(x[0],x[2],x[3],x[-1]) for x in keepme] # icdtrans,excludes,cat,checksamelast12 
    icdKeepdict = dict(zip(icdkeepmatch,icdrec)) # list of diags we need to store - no point storing all
    logging.debug('keepicd = ',','.join(icdKeepdict.keys()))


    return icdrec,icdKeepdict, lxcat, lxKeepdict





def makeD(d='20070101'):
    # Creates a date if given a string in the YYYYMMDD format
    if len(d) <> 8:
        logging.error('### duff date %s in makeD' % d)
        return None
    else:
        yy,mm,dd = map(int,[d[:4],d[4:6],d[6:8]])
        d = datetime.date(yy,mm,dd)
    return d

def getDemog():
    """see how bad this is
    """
    d = {}
    esp = MySQLdb.Connect('localhost', settings.DATABASE_USER, settings.DATABASE_PASSWORD)
    s = '''select Demog_id from esp.esp_demog'''
    n = 0
    started = time.time()
    ids = iterCursor(connection=esp,query=s)
    for idrec in ids:
        id = idrec[0][ID_KEY]
        mrn = idrec[0]['DemogMedical_Record_Number']
        if d.get(id,None):
            s = '### duplicate id %s, mrn=%s in getDemog - panic please' % (id,mrn)
            print s
        else:
            d[id] = mrn
    s = 'getDemog got %d records in %f sec' % ()
    return d # dict instead of demog mrns

def makeNewCase(cond, onedemogid,lxids,relatedrxids ,relatedencids,relatedicd9,
                relatedimid, caseComments):
    """ create a new case record
    """
    p = Demog.objects.get(id__exact=onedemogid)
    ##encounter
    encidstr = ','.join([str(i) for i in relatedencids])
    ##lab result
    lxidstr = ','.join([str(i) for i in lxids])
    ##Rx
    rxidstr = ','.join([str(i) for i in relatedrxids])
    ##ICD
    relatedicd9str = ','.join(relatedicd9)
    ## imm
    immIdstr = ','.join(relatedimid)
    ##Create a new record
    wf = None
    rule = Rule.objects.filter(ruleName__icontains=cond)[0]
    wf = rule.ruleInitCaseStatus
    if not wf:
        wf = 'AR'
    if rule.ruleinProd: # TODO add immunization ids to case?
        c = Case(caseWorkflow=wf,caseDemog=p,caseRule=rule, caseImmID=immIdstr,
                 caseEncID=encidstr, caseLxID=lxidstr,caseRxID=rxidstr,caseICD9=relatedicd9str,
                 caseComments=caseComments)
    else:
        c = TestCase(caseWorkflow=wf,caseDemog=p,caseRule=rule, caseImmID=immIdstr,
            caseEncID=encidstr, caseLxID=lxidstr,caseRxID=rxidstr,caseICD9=relatedicd9,
            caseComments=caseComments)

    if p.DemogProvider:
        c.caseProvider=p.DemogProvider

    c.save()
    if rule.ruleinProd:
        updateCaseWF(c,changedby='ESP VAERS Auto',note='Create New Case')
        logging.info('New Vaers Case-%s: DemogPID%s' % (cond,p.DemogPatient_Identifier))
        ##need send email
        if case_dict.has_key(cond):
            case_dict[cond]=case_dict[cond]+1
        else:
            case_dict[cond]=1
    else:
        logging.info('New Vaers TestCase-%s: DemogPID%s' % (cond,p.DemogPatient_Identifier))


def test(ps = '20071201', pe = '20071205', delim='\t', missval=''): 
    """
    """
    outfname = 'vaerstest_%s_%s.xls' % (ps,pe)
    outf = file(outfname,'w')
    eventIter = PostImmEvents(sps=ps,spe=pe)
    outf.write('%s\n' % '\t'.join(eventIter.outhead)) # header row
    for row in eventIter:
        print 'iter gave', row
        outf.write('%s\n' % delim.join(row)) # write result as tab delim eg 
    outf.close()

def feverBymonth(outfname='vaersfeverbymonth.xls',ps='20060101',pe='20081231'):
    allfever = AllFever(ps=ps,pe=pe)
    fres = {}
    for (fdate,fval) in allfever:
        k = fdate[:6]
        n = fres.setdefault(k,0)
        fres[k] = n+1
    allimm = AllImm(ps=ps,pe=pe)
    ires = {}
    for idate in allimm:
        k = idate[:6]
        n = ires.setdefault(k,0)
        ires[k] = n+1
    outf = file(outfname,'w')
    outf.write('month\tnfever\tnimmunizations\n')
    rk = ires.keys()
    rk.sort()
    for k in rk:
        outf.write('%s01\t%d\t%d\n' % (k,fres.get(k,0),ires.get(k,0)))
    outf.close()


    
if __name__ == "__main__":
    #feverBymonth()
    prog = os.path.split(sys.argv[0])[-1]
    setLogging(appname=prog)
    sd = '20070101'
    ed = '20070131'
    if len(sys.argv) >= 3:
        sd = sys.argv[1]
        ed = sys.argv[2]
        print 'using supplied sd %s, ed %s' % (sd,ed)
    else:
        print 'using default sd %s, ed %s' % (sd,ed)
    test(ps=sd,pe=ed)
    logging.shutdown()



