# prototype ESP case maker
# run after new data inserted
#
# writes new case and AR workflow records for all newly identified cases in the database
# selects patients with any of icd9s on the case definition icd list and any one of lx_list
# To save time, remembers all of the associated lx records, rx records, enc records
# and (for hl7 construction) remembers the icd9_list icd9 codes from each encounter
# (tuples of those codes from each encounter in the
# same order as the encounters)
# this saves us having to do much work at display or message format time
#
# Likely that each condition will need a separate version of this logic
# some patterns may be reuseable with any luck.
#
# Each condition not only has criteria, but also elements which should be
# supplied as part of any notification. Prescriptions are particularly
# important to see if the case was appropriately treated
#
# Most of the logic is amazingly simple when using the django ORM
#

import os, sys, django, datetime
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from django.db.models import Q
import localconfig
import logging


###For logging
logging = localconfig.getLogging('identifyCases.py v0.1', debug=0)

#################################
def makeNewCase(condition, pid):
    """ create a new case record
    """ 
    wf = 'AR'
    p = Demog.objects.get(id__exact=pid)
    ##encounter
    encids = pids[pid][2]
    encids.sort()
    encidstr = str(encids)[1:-1]
    icd9str=getRelatedIcd9(condition, encids)
   
        
    ##lab result    
    lxids = pids[pid][0]
    lxids.sort()
    lxidstr = str(lxids)[1:-1]
    
    ##Rx
    rxids = pids[pid][1]
    rxids.sort()
    rxidstr = str(rxids)[1:-1]
    
    ##Create a new record
    rule = Rule.objects.filter(ruleName__icontains=condition)[0]
    priors = Case.objects.filter(caseDemog = pid,caseRule=rule)
    
    c = Case(caseWorkflow=wf,caseDemog=p,caseComments='',caseRule=rule, 
      caseEncID=encidstr, caseLxID=lxidstr,caseRxID=rxidstr,caseICD9=icd9str)
    
    if p.DemogProvider:
        c.caseProvider=p.DemogProvider
    c.save()
    logging.info('Creating %s: NEWCASE%s' % (condition,c.id))
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    wfr = CaseWorkflow(workflowCaseID=c,workflowDate=now,workflowState=wf)
    wfr.save()

################################
def getRelatedLx(condition):
    """based on case definition to get all Lab tests with positive results
    """
    
    defines = ConditionLOINC.objects.filter(CondiRule__ruleName__icontains=condition,CondiDefine=True)
    loincs = map(lambda x:x.CondiLOINC, defines)
    logging.info('Condition-%s: LxLoinc: %s' % (condition, str(loincs))) 
    lxs = Lx.objects.filter(
               Q(LxLoinc__in=loincs),
               Q(LxTest_results__istartswith='positiv') | Q(LxTest_results__istartswith='detect') | Q(LxNormalAbnormal_Flag__istartswith='Y')
                )
    return lxs

################################
def findcaseByLx(condition):
    """lx_list: [(cpt, compoent), ]
    """
    lxs = getRelatedLx(condition)
    
    recl = [(l.LxPatient.id,int(l.id)) for l in lxs]  
    logging.info('Found %s for LX: (patientId, Lxid) -%s' % (condition, str(recl)) )
   
    return recl

###############################
def findcaseByIcd9(condition, lxs):

    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiDefine=True)
    encl=[]
    if condicd9s:
        encl = getrelatedEnc(condition, condicd9s)
    
    return encl


#################################
def getRelatedIcd9(condition, encids):
    """icd9str: Enc1_ICD91 Enc1_ICD91, Enc2_ICD91,
    """
    icd9List=[]
    icd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)
    ruleicd9s = map(lambda x:x.CondiICD9, icd9s)
    for i in encids:
        enc = Enc.objects.get(id__exact=i)
        icd9ids = string.split(enc.EncICD9_Codes, ' ')
        icd9str = ' '.join([j.strip() for j in icd9ids if j in ruleicd9s]) # 

        ## use ',' to separate different encounter        
        icd9List.append(icd9str)
    icd9str = ','.join(icd9List) # much more efficient and clean I think
    return icd9str
 


################################
# TODO fix me ! There's something wierd about the ndc codes we get from hvma
# appear to have last 2 digit fill leaving only 9 digits
# I've adjusted preLoader to futz, right padding with 0 as needed
def getrelatedRx(condition,condndcs):
    """snarf all prescriptions to be sent for this condition
    the Django ORM makes this ridiculously easy
    it's slower than direct sql but that's of no importance here 
    for the ESP model.
    """
    # a list of the codes we should send
    # rxs = Rx.objects.filter(RxPatient__id__in=pids.keys(),RxNational_Drug_Code__in=map(lambda x:x.CondiNdc, ndcs))
    sendndcs = [x.CondiNdc for x in condndcs] # cleaned up - replaced * and spaces in preloader
    sendndcs.sort()
    rxs = Rx.objects.filter(RxPatient__id__in=pids.keys()) # all rx for this patient
    recl = [(r.RxPatient.id,int(r.id)) for r in rxs if str(r.RxNational_Drug_Code)[:9] in sendndcs]
    # kludge for bogus last 2 chars in hvma ndc codes
    if len(recl) > 0:
       logging.info('####GOT one!!')
    logging.info('Cond: %s. Looking for sendndcs=%s. matched rxs = %s from patient rxs=%s' % (condition,sendndcs,recl,rxs))
    return recl
    

################################
def getrelatedEnc(condition,condicd9s):
 
    ruleicd9s = map(lambda x:x.CondiICD9, condicd9s)
    encs = Enc.objects.filter(EncPatient__id__in=pids.keys())
    recl=[]
    for enc in encs:
        codes = string.strip(enc.EncICD9_Codes)
        if codes:
            temp = string.split(codes, ' ')
            for i in temp:
                if i in ruleicd9s: #need record
                    recl.append((enc.EncPatient.id,int(enc.id)))
    return recl
        

################################
def buildCaseData(recl,indx):
    for pid,recid in recl:
        if pids.has_key(pid):
            if recid not in pids[pid][indx]:
                pids[pid][indx].append(recid)
        else:
            pids[pid]=([],[],[])
            pids[pid][indx].append(recid)


################################
def getEncduration(casedb, cureid):
    ##get max(date) from last_case.encId
    encdb = Enc.objects.filter(id__in=[int(i) for i in string.split(casedb.caseEncID,',')])

    encdbl =[(datetime.date(int(i.EncEncounter_Date[:4]),int(i.EncEncounter_Date[4:6]),int(i.EncEncounter_Date[6:8])), i.id) for i in encdb]
    encdbl.sort()
    
    ##get max(date) from current encid
    curenc = Enc.objects.filter(id__in=cureid)
    curencl =[(datetime.date(int(i.EncEncounter_Date[:4]),int(i.EncEncounter_Date[4:6]),int(i.EncEncounter_Date[6:8])), i.id) for i in curenc]
    curencl.sort()

    timeperiod = curencl[-1][0] -encdbl[-1][0]
    return timeperiod.days


################################
def getLxduration(casedb, curlid):
    ##get max(date) from last_case.LxId
    lxids = [int(i) for i in string.split(casedb.caseLxID,',') if i]
    lxdbl=[]
    
    if not curlid: return 0
    elif not lxids: return 29
    
    if lxids:
        lxdb = Lx.objects.filter(id__in=[int(i) for i in string.split(casedb.caseLxID,',') if i])

        for i in lxdb:
            if  i.LxDate_of_result:
                lxdbl.append((datetime.date(int(i.LxDate_of_result[:4]),int(i.LxDate_of_result[4:6]),int(i.LxDate_of_result[6:8])), i.id))
            else:
                lxdbl.append((datetime.datetime.now(),i.id))
        lxdbl.sort()
    
    ##get max(date) from current Lxid
    curlxl=[]
    if curlid:
        curlx = Lx.objects.filter(id__in=curlid)
        for i in curlx:
            if  i.LxDate_of_result:
                curlxl.append((datetime.date(int(i.LxDate_of_result[:4]),int(i.LxDate_of_result[4:6]),int(i.LxDate_of_result[6:8])), i.id))
            else:
                curlxl.append((datetime.datetime.now(),i.id))
        #curlxl =[(datetime.date(int(i.LxDate_of_result[:4]),int(i.LxDate_of_result[4:6]),int(i.LxDate_of_result[6:8])), i.id) for i in curlx]
        curlxl.sort()

    timeperiod = curlxl[-1][0] -lxdbl[-1][0]
    return timeperiod.days


################################
def checkLxEncDuration(before=-31, after=31):
    """For PID only: ICD9 codes within 21 days prior the positive lab resutl or in the subsequent 60 days follosing positive lab result
    """
    logging.info('PID: for LX only: %s' % str(pids))
    removepid = []
    for pid in pids.keys():
        pidyes=0
        lxidl = pids[pid][0]
        encidl = pids[pid][2]
        for lxid in lxidl:
            print lxid
            for encid in encidl:
                curlx = Lx.objects.filter(id__in=[lxid])[0]
                curenc = Enc.objects.filter(id__in=[encid])[0]
                if curlx.LxDate_of_result and curenc.EncEncounter_Date:
                    curdur = datetime.date(int(curenc.EncEncounter_Date[:4]),int(curenc.EncEncounter_Date[4:6]),int(curenc.EncEncounter_Date[6:8]))- datetime.date(int(curlx.LxDate_of_result[:4]),int(curlx.LxDate_of_result[4:6]),int(curlx.LxDate_of_result[6:8]))
                    numdays = curdur.days
                    if (numdays>0 and numdays<after) or (numdays<0 and numdays>before):
                        pidyes=1
                        break
            if pidyes==1:
                break
            
        if pidyes==0 and pid not in removepid:
            removepid.append(pid)

    for p in removepid:
        pids.pop(p)
    logging.info('PID: for LX and ICD9: %s' % str(pids))

    
################################
################################
if __name__ == "__main__":
    ##based on case definition
    ###filter Lab results
    logging.info('==================\n')
    conditions = Rule.objects.all()
    for c in conditions:
        cond = c.ruleName
        
        logging.info('\n\nStart to inentify case %s' % cond)

        ###pids: store case info
        ##pids = {pid: ([esp_lx.id, ..],[esp_rx.id, ..],[esp_enc.id, ..]), 
        ###      }
        pids={}

        
        ##identify each case
        recordl = findcaseByLx(cond)
        buildCaseData(recordl,0)
        if string.upper(cond)=='PID':
            ##need check ICD9 also
            if recordl:
                record_icd9l = findcaseByIcd9(cond,recordl)
                print  record_icd9l
                if not record_icd9l: #not a PID case
                    pids={}
                else:
                    buildCaseData(record_icd9l,2)
                    checkLxEncDuration(before=-31, after=31)
                   
        if not pids: #no case found
            logging.info('No cases of %s found' % cond)
            continue
        
        ### store rxids,encids for this condition
        condndcs = ConditionNdc.objects.filter(CondiRule__ruleName__icontains=cond,CondiSend=True)
        recl = getrelatedRx(cond,condndcs)
        buildCaseData(recl,1)
        
        condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=cond,CondiSend=True)
        recl = getrelatedEnc(cond, condicd9s)    
        buildCaseData(recl,2)
        
        ### get all cases: pids
        for pid in pids.keys():    
            cases = Case.objects.filter(caseDemog__id__exact=pid,caseRule__ruleName__icontains=cond)
            if not cases: ##a new case
                logging.info('NewCase - %s: DemogID-%s' % (cond,pid))
                makeNewCase(cond, pid)
            else:#this patient is in the esp_case table
                logging.info('This patient has old case - %s, DemogID%s' % (cond,pid)) 
                cases.order_by('id')
                c = cases[len(cases)-1]
                lid,rid,eid = pids[pid][:3]
                eid.sort()
                lid.sort()
                rid.sort()
                encids = str(eid)[1:-1]
                lxids = str(lid)[1:-1]
                rxids = str(rid)[1:-1]
            
                if getLxduration(c, lid) > 28:
                    #new case
                    logging.info('New Lx for existing case -%s: CaseID%s, DemogID%s\n' % (cond,c.id,pid))
                    makeNewCase(cond, pid)
                else:##still old case
                    icd9str=getRelatedIcd9(cond, eid)
                    #check if case has been sent or not
                    if c.caseWorkflow =='S':
                        ##do nothing
                        pass
                    else: ##update case
                        logging.info('Update unsend case - %s: CaseID%s' % (cond,c.id))
                        c.caseEncID=encids
                        c.caseLxID=lxids
                        c.caseICD9=icd9str
                        c.caseRxID=rxids
                        c.save()
            
            
