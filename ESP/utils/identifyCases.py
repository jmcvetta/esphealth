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
from ESP.settings import *
from django.db import connection
cursor = connection.cursor()

import utils
import copy


###For logging
iclogging = getLogging('identifyCases.py_v0.1', debug=0)

case_dict={}

#################################
def makeNewCase(cond, onedemogid,lxids,relatedrxids ,relatedencids,relatedicd9str):
    """ create a new case record
    """ 


    p = Demog.objects.get(id__exact=onedemogid)

    ##encounter
    encidstr = ','.join([str(i) for i in relatedencids])
        
    ##lab result
    lxidstr = ','.join([str(i) for i in lxids])
    
    ##Rx
    rxidstr = ','.join([str(i) for i in relatedrxids])
    
    ##Create a new record
    rule = Rule.objects.filter(ruleName__icontains=cond)[0]
    wf = rule.ruleInitCaseStatus
    if not wf: wf = 'AR'
    
    if rule.ruleinProd:
        c = Case(caseWorkflow=wf,caseDemog=p,caseComments='',caseRule=rule, 
                 caseEncID=encidstr, caseLxID=lxidstr,caseRxID=rxidstr,caseICD9=relatedicd9str)
    else:
        c = TestCase(caseWorkflow=wf,caseDemog=p,caseComments='',caseRule=rule,
                                  caseEncID=encidstr, caseLxID=lxidstr,caseRxID=rxidstr,caseICD9=relatedicd9str)
        
    if p.DemogProvider:
        c.caseProvider=p.DemogProvider

    c.save()

    
                                
    if rule.ruleinProd:
        updateCaseWF(c,changedby='ESP Auto',note='Create New Case')
        iclogging.info('NewCase-%s: DemogPID%s' % (cond,p.DemogPatient_Identifier))
        ##need send email
        if case_dict.has_key(cond):
            case_dict[cond]=case_dict[cond]+1
        else:
            case_dict[cond]=1
    else:
        iclogging.info('New TestCase-%s: DemogPID%s' % (cond,p.DemogPatient_Identifier))
        


################################
################################
def getRelatedLx(condition,defines=[],demog=None):
    """based on case definition to get all Lab tests with positive results
    """
    #import time
    if not defines:
        defines = ConditionLOINC.objects.filter(CondiRule__ruleName__icontains=condition,CondiDefine=True)

    loincs = map(lambda x:x.CondiLOINC, defines)
    

    if demog:
        lxs = Lx.objects.filter(Q(LxPatient=demog),
                                Q(LxLoinc__in=loincs))
    else:
        lxs = Lx.objects.filter(Q(LxLoinc__in=loincs))

    returnl=[]
    for onedefine in defines:
        if string.upper(onedefine.CondiOperator) == 'CONTAIN':
            queryl = ["""Q(LxNormalAbnormal_Flag__istartswith='Y')"""]
            for v in onedefine.CondiValue.split(','):
                queryl.append("""Q(LxTest_results__istartswith='%s') """ % v)
            querystr ='|'.join(queryl)
            lxs2 = lxs.filter(Q(LxLoinc__exact=onedefine.CondiLOINC), eval(querystr))
        elif string.upper(onedefine.CondiOperator) == '>':
            lxs2 = lxs.filter(Q(LxLoinc__exact=onedefine.CondiLOINC),
                             (Q(LxTest_results__gt=float(onedefine.CondiValue)) | Q(LxTest_results__contains='>'))
                              )
        else:
            lxs2 = lxs
        returnl = returnl+list(lxs2)
        
            
    
    #ignore any lab result date *before* 05/2006 (See 3/1/2007 email)
    #if string.upper(condition) != 'ACUTE HEPATITIS A':

    lxs = filterOldLxs(returnl, cutoffd = datetime.date(2006,4,30) )
    lxs =Lx.objects.filter(id__in=[l.id for l in lxs])
    #else:
    #    lxs =Lx.objects.filter(id__in=[l.id for l in returnl])
        
    return lxs


###################################
###################################
def filterOldLxs(lxs, cutoffd = datetime.date(2006,4,30) ):
    returnlxs=[]
    for l in lxs:
        if len(l.LxDate_of_result)==8:
            if datetime.date(int(l.LxDate_of_result[:4]),int(l.LxDate_of_result[4:6]),int(l.LxDate_of_result[6:8]))>cutoffd:
                returnlxs.append(l)
        else:
            returnlxs.append(l)
            
            
    return returnlxs



###################################
###################################
def sortLx(lxs):
    ##sort by Result date
    recl = [(l.LxPatient.id,int(l.id),l.LxDate_of_result) for l in lxs]
    recl.sort(key=lambda x:x[2]) ##sort by LxDate_of_result
    recl = map(lambda x:(x[0],x[1]), recl)

    #logstr = [(l.LxPatient.DemogPatient_Identifier,int(l.LxOrder_Id_Num)) for l in lxs]

    return recl


################################              
################################
def buildCaseData(recl):
    returndict={}
    for pid,recid in recl:
        if returndict.get(pid) and recid not in returndict[pid]:
            returndict[pid].append(recid)
        else:
            returndict[pid]=[recid]

    return returndict

    
###################################
def getEncids4dayrange(onedemogid, lxids, condicd9s, cond, afterday=14,beforeday=-14):

    ##Pertinent ICD9 codes should only be indicated & reported if they appear in the period from 14 days before test order date until 14 days after test result date
    maxdate=''
    mindate=''
    if lxids:
        lxs = Lx.objects.filter(id__in=lxids).order_by('LxDate_of_result')
        ##get lastest LX record = max resultdate
        try:
            maxrec=lxs[len(lxs)-1].LxDate_of_result
        except:
            maxrec = ''

        ##get min orderdate
        if string.upper(cond)=='PID':
            try:
                minrec=lxs[0].LxDate_of_result
            except:
                minrec = ''
        else:
            lxs = Lx.objects.filter(id__in=lxids).order_by('LxOrderDate')
            try:
                minrec=lxs[0].LxOrderDate
            except:
                minrec = ''

        if maxrec and minrec:
            maxdate =getAnotherdate(maxrec,afterday)
            mindate =getAnotherdate(minrec,beforeday)
            
    return getRelatedEncids(onedemogid,condicd9s,mindate, maxdate)


###################################
###################################
def getRx_MinMaxDate(rxids,afterday,beforeday):
    maxdate=''
    mindate=''

    rxs = Rx.objects.filter(id__in=rxids).order_by('RxOrderDate')
    ##get lastest RX record = max resultdate
    try:
        maxrec=rxs[len(rxs)-1].RxOrderDate
        minrec = rxs[0].RxOrderDate
    except:
        maxrec = ''
        minrec=''
            

    if maxrec and minrec:
        maxdate =getAnotherdate(maxrec,afterday)
        mindate =getAnotherdate(minrec,beforeday)
    return (mindate,maxdate)


###################################
def getRelatedEncids(onedemogid,condicd9s,mindate, maxdate):                       
    returnl=[]
    icd9List=[]
    distincticd9List=[]
    returnicd9str = ''

#    r = Rule.objects.filter(id=condicd9s[0].CondiRule_id)
#    if rand r[0].ruleName== 'Syphilis':  ###need modify
    if  condicd9s and Rule.objects.filter(id=condicd9s[0].CondiRule_id)[0].ruleName== 'Syphilis':  ###need modify
        tmp = map(lambda x:x.CondiICD9.strip(), condicd9s)
        ruleicd9s=[]
        for i in tmp:
            for j in range(10):
                ruleicd9s.append('%s%s' % (i,j))
        for i in tmp:
            ruleicd9s.append('%s' % i[:-1])
    else:        
        ruleicd9s = map(lambda x:x.CondiICD9.strip(), condicd9s)
    encs = Enc.objects.filter(EncPatient__id =onedemogid).order_by('EncEncounter_Date')
    for enc in encs:
        icd9str=''
        flag=0
        encdate = enc.EncEncounter_Date
        if encdate:
            encdate = datetime.date(int(encdate[:4]),int(encdate[4:6]),int(encdate[6:8]))
        
        if not encdate or not maxdate or not mindate or (encdate>=mindate and encdate<=maxdate):
            ##Pertinent ICD9 codes should only be indicated & reported if they appear in the period from 14 days before test order date until 14 days after test result date
            icd9ids = string.split(enc.EncICD9_Codes, ' ')
            for  oneicd9 in icd9ids:
                oneicd9 = oneicd9.strip()
                if oneicd9  in ruleicd9s and  oneicd9 not in distincticd9List: ##find a new ICD9
                    icd9str = icd9str + ' ' +oneicd9
                    distincticd9List.append(oneicd9)
                    flag=1

            if flag==1:
                returnl.append(int(enc.id))
                icd9List.append(icd9str.strip())
                
    if icd9List:
        ## use ',' to separate different encounter
        returnicd9str= ','.join(icd9List)

    return (returnl,returnicd9str)

                
###################################
###################################
def getRxids4dayrange(demogid,curlids,drugmaps, cond,afterday=14,beforeday=0,firstuseonly=0,exclude_dict={}):

    maxrec=''
    minrec=''
    returnl=[]

        
    if string.upper(cond)=='PID' and curlids:
        encs = Enc.objects.filter(id__in=curlids).order_by('EncEncounter_Date')
        try:
            maxrec=encs[len(encs)-1].EncEncounter_Date
            minrec=encs[0].EncEncounter_Date
        except:
            pass

    elif curlids:
        try:
            lxs = Lx.objects.filter(id__in=curlids).order_by('LxDate_of_result')
            ##get lastest Lx record
            maxrec=lxs[len(lxs)-1].LxDate_of_result
            ##Report all of the drugs from the list below given any time from lab order date until lab result date + 14 days
            lxs = Lx.objects.filter(id__in=curlids).order_by('LxOrderDate')
            minrec=lxs[0].LxOrderDate
        except:
            pass
                         
    if maxrec and minrec:
        maxdate = getAnotherdate(maxrec,afterday)
        mindate = getAnotherdate(minrec,beforeday)

    for onedrug in drugmaps:

         rxs = Rx.objects.filter(RxPatient__id=demogid, RxDrugName__icontains=onedrug.CondiDrugName, RxRoute__icontains=onedrug.CondiDrugRoute).order_by('RxOrderDate','RxOrder_Id_Num')

         if exclude_dict.has_key(onedrug.CondiDrugName):
             for excn in exclude_dict[onedrug.CondiDrugName]:
                 rxs=rxs.exclude(RxDrugName__icontains=excn)
             rxs =rxs.order_by('RxOrderDate','RxOrder_Id_Num')

         
         if firstuseonly==1 and rxs:
             returnl.append(int(rxs[0].id))
         else:
             for rx in rxs:
                 rxdate =  rx.RxOrderDate
                 if rxdate:
                     rxdate = datetime.date(int(rxdate[:4]),int(rxdate[4:6]),int(rxdate[6:8]))

                 if not rxdate or not curlids or not maxrec or not minrec or (rxdate>=mindate and rxdate<=maxdate):
                     if int(rx.id) not in returnl:
                         returnl.append(int(rx.id))

    returnl.sort()
    return returnl

###################################
def getLxids4dayrange(demogid,curlids,cond,afterday=30,beforeday=-30):
    
    maxrec=''
    minrec=''
    returnl=[]


    try:
        lxs = Lx.objects.filter(id__in=curlids).order_by('LxDate_of_result')
        ##get lastest Lx record
        maxrec=lxs[len(lxs)-1].LxDate_of_result
        lxs = Lx.objects.filter(id__in=curlids).order_by('LxOrderDate')
        minrec=lxs[0].LxOrderDate
    except:
        pass

    if maxrec and minrec:
        maxdate = getAnotherdate(maxrec,afterday)
        mindate = getAnotherdate(minrec,beforeday)
                        
                                                                                                                                        
    sends = ConditionLOINC.objects.filter(CondiRule__ruleName__icontains=cond,CondiSend=True)
    loincs = map(lambda x:x.CondiLOINC, sends)

    for oneloinc in loincs:
    
        lxs = Lx.objects.filter(Q(LxPatient__id=demogid),
                                Q(LxLoinc__in=[oneloinc]))

        #lxs = lxs.exclude(id__in =curlids)
        lxs = lxs.order_by('LxDate_of_result')
        if oneloinc in ('1742-6','1920-8','5009-6','16934-2'): ##ALT/AST
            try:
                lxs = map(lambda x:(float(x.LxTest_results), x), lxs)
            except:
                lxs = map(lambda x:(x.LxTest_results, x), lxs)
                
            lxs.sort()
            lxs = map(lambda x:x[1], lxs)
        lxs = list(lxs)
        lxs.reverse()  ##report all the following arising within 30 days of the order date for Hepatitis A IgM; if a single test was done multiple times then report the highest value or most positive value

        for lx in lxs:
            lxdate = lx.LxOrderDate
            lxdate = datetime.date(int(lxdate[:4]),int(lxdate[4:6]),int(lxdate[6:8]))

            if not lxdate or not curlids or not maxrec or not minrec or (lxdate>=mindate and lxdate<=maxdate):
                if lx.id in curlids:
                    break
                
                if int(lx.id) not in returnl:
                    returnl.append(int(lx.id))
                    break
                
    returnl.sort()
    return returnl
                                     

###################################
###################################
def getAnotherdate(date1, dayrange):
    try:
        return datetime.date(int(date1[:4]),int(date1[4:6]),int(date1[6:8]))+datetime.timedelta(dayrange)
    except:
        iclogging.error('Error when get another date: date1=%s,range=%s' % (date1,dayrange))
        return ''
    

###################################
def getLxduration(lxid1, lxid2, useorderdate=0):
    lx1 = Lx.objects.filter(id=lxid1)[0]
    lx2 = Lx.objects.filter(id=lxid2)[0]
    if useorderdate==1:
        if lx1.LxOrderDate and lx2.LxOrderDate and lx1.LxDate_of_result and lx2.LxDate_of_result:
            return min(utils.getPeriod(lx1.LxOrderDate,lx2.LxOrderDate),utils.getPeriod(lx1.LxDate_of_result,lx2.LxDate_of_result))
        else:
            return 0
    elif lx1.LxDate_of_result and lx2.LxDate_of_result:
        return utils.getPeriod(lx1.LxDate_of_result,lx2.LxDate_of_result)
    else:
        return 0

    
###################################
def updateSentCase(onecase):
    ##get all sent cases <28 days
    ##if there is any new Rx, Enc record then need resend HL7 msg, but not create new case
    ##update caseworkflow history with new text notes with timedate stamp, what was added
    cond = Rule.objects.filter(id=onecase.caseRule.id)[0].ruleName
    pid = onecase.caseDemog.id

    newlx_list = [i for i in onecase.caseLxID.split(',') if i.strip()]
        
    (iscase, relatedencids,relatedicd9str,relatedrxids) = getReportedRec(cond,pid,newlx_list)
    if not iscase:
        return
                                
    note=''
    newencids = ','.join([str(i) for i in relatedencids])
    newrxids=','.join([str(i) for i in relatedrxids])
    if onecase.caseICD9 != relatedicd9str:
        note=note+'Updated due to new ICD9:old=%s; new=%s; ' % ( onecase.caseICD9,relatedicd9str)
        onecase.caseICD9=relatedicd9str
        onecase.save()
        
    if onecase.caseEncID != newencids:
        note = note+'Updated due to new Enc: old=%s; new=%s; ' % (onecase.caseEncID,newencids)
        onecase.caseEncID=newencids
        onecase.save()
        
    if onecase.caseRxID != newrxids:
        note = note+'Updated due to reporting Rx logic changes: old=%s; new=%s; ' % (onecase.caseRxID,newrxids)
        onecase.caseRxID=newrxids
        onecase.save()
        
    if note and onecase.caseWorkflow=='S':
        note = 'CaseID-%s: Already sent. Set to re-send; ' % onecase.id + note
        onecase.caseWorkflow='Q'
        onecase.save()

    if note:
        iclogging.info('\n\nUpdate case: %s' % onecase.id)
        updateCaseWF(onecase,note = note)
            
            
            

###################################
def updateCaseWF(case,changedby='ESP Auto',note=''):
    #if note != 'Create New Case':  ##for Repair only
    #    return
    
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    wfr = CaseWorkflow(workflowCaseID=case,
                       workflowDate=now,
                       workflowState=case.caseWorkflow,
                       workflowChangedBy=changedby,
                       workflowComment=note)
    wfr.save()


                
###################################
def getReportedRec(cond,demogid,lxids):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=cond,CondiSend=True)
    drugmaps = ConditionDrugName.objects.filter(CondiRule__ruleName__icontains=cond,CondiSend=True)
    if string.upper(cond)=='PID':
        relatedencids,relatedicd9str = getEncids4dayrange(demogid,lxids, condicd9s, cond,afterday=28,beforeday=-28)

        if relatedencids: ##this is a PID case
            #2. get related Rx
            relatedrxids = getRxids4dayrange(demogid,relatedencids,drugmaps,cond,afterday=30,beforeday=-30)
        else: #not a PID case
            return (0, [],'',[])
    elif string.upper(cond)=='ACTIVE TUBERCULOSIS':
        exclude_dict = {'INH': ['INHALE','INHIB'], 'PZA':['CAPZA']}
        relatedencids,relatedicd9str = getEncids4dayrange(demogid,lxids,condicd9s,cond,afterday=14,beforeday=-14)
        relatedrxids = getRxids4dayrange(demogid,[],drugmaps, cond,afterday=None,beforeday=None,firstuseonly=1,exclude_dict=exclude_dict)
    else:  ##other conditions
        #1. get related Enc
        relatedencids,relatedicd9str = getEncids4dayrange(demogid,lxids,condicd9s,cond,afterday=14,beforeday=-14)

        #2. get related Rx
        relatedrxids = getRxids4dayrange(demogid,lxids,drugmaps, cond,afterday=14,beforeday=-7)

    return (1, relatedencids,relatedicd9str,relatedrxids)
                                                                                                                                                            

###################################
###################################
def divide2groups(relatedlxids,dayrange=28):
    groupids = []

    ##relatedlxids is a list of lxids which is sorted by result date
    for onel in relatedlxids:
        if not groupids:
            groupids.append([onel])
        else:
            basel = groupids[-1][0]
            pr = getLxduration(basel, onel)
            if pr <dayrange:
                 groupids[-1].append(onel)
            else:
                groupids.append([onel])

    return groupids

###################################
###################################
def processoneCondition(cond):

    ##recordl=[(l.LxPatient.id,int(l.id),..], sorted by date of result
    newlxs = getRelatedLx(cond)
    recordl = sortLx(newlxs)
    demog_lx = buildCaseData(recordl)
    
    rule = Rule.objects.filter(ruleName__icontains=cond)[0]
    if rule.ruleinProd:
        condinProd=1
    else:
        condinProd=0
        
    for onedemogid in demog_lx.keys():
        relatedlxids = demog_lx[onedemogid]
        lxidgroups =divide2groups(relatedlxids,dayrange=28)
        for onegroup in lxidgroups:
            incase=0

            if condinProd:
                cases = Case.objects.filter(caseDemog__id__exact=onedemogid,caseRule__ruleName__icontains=cond)
            else:
                cases = TestCase.objects.filter(caseDemog__id__exact=onedemogid,caseRule__ruleName__icontains=cond)
                
            if not cases: ##new case
                (iscase, relatedencids,relatedicd9str,relatedrxids) = getReportedRec(cond,onedemogid,onegroup)
                if not iscase:
                    continue
                makeNewCase(cond, onedemogid,onegroup,relatedrxids ,relatedencids,relatedicd9str)
            elif cases:
                onegroup2 = copy.deepcopy(onegroup)
                curLxids = [(c.caseLxID,c.id) for c in cases]
                lx_caseid={}
                for lxidstr, caseid in curLxids:
                    lxids = lxidstr.split(',')
                    for onelid in lxids:
                        lx_caseid[int(onelid)]=caseid
                        
                flag=0

                for onelid in onegroup:
                    if onelid in lx_caseid.keys(): ##already in the case
                        flag=1
                        ##may need update corresponding case
                        if condinProd:
                            c = Case.objects.filter(id=lx_caseid[onelid])[0]
                        else:
                            c = TestCase.objects.filter(id=lx_caseid[onelid])[0]
                            
                        oldcaselxid = c.caseLxID
                        caselxid = [int(i) for i in c.caseLxID.split(',')]
                        caselxid.sort()
                        onegroup2.sort()
                        if caselxid  == onegroup2:
                            ##same, not need update
                            pass
                        else:
                            if  c.caseWorkflow !='S' or (c.caseWorkflow =='S' and (datetime.datetime.today()-c.casecreatedDate).days<28):
                                ##update caseworkflow history with new text notes with timedate stamp, what was added
                                (iscase, relatedencids,relatedicd9str,relatedrxids) = getReportedRec(cond,onedemogid,onegroup)
                                if not iscase:
                                    continue
                                
                                c.caseEncID=','.join([str(i) for i in relatedencids])
                                c.caseLxID=','.join([str(i) for i in onegroup])
                                c.caseICD9=relatedicd9str
                                c.caseRxID=','.join([str(i) for i in relatedrxids])
                                c.save()
                                    
                                if condinProd and c.caseWorkflow != 'AR':
                                    updateCaseWF(c,note = 'CaseID-%s:Updated due to new Lx:old=%s; new=%s; ' % (c.id, oldcaselxid, c.caseLxID))
                                    
                                iclogging.info('%s update: oldCaseID%s,DemogPID%s,NewLx%s' % (cond,c.id,c.caseDemog.DemogPatient_Identifier,c.caseLxID))                                                     
                            if condinProd and c.caseWorkflow =='S' and (datetime.datetime.today()-c.casecreatedDate).days<28:
                                ##need resend HL7 msg, but not create new case
                                c.caseWorkflow ='Q'
                                c.save()
                                updateCaseWF(c,note = 'CaseID-%s: Already sent. Set to re-send due to new Lx:old=%s; new=%s; ' % (c.id, oldcaselxid,c.caseLxID))
                        break    
                            
                if flag==0:
                    (iscase, relatedencids,relatedicd9str,relatedrxids) = getReportedRec(cond,onedemogid,onegroup)
                    if not iscase:
                        continue
                    makeNewCase(cond, onedemogid,onegroup,relatedrxids ,relatedencids,relatedicd9str)
                                                                      



###################################
def haspriorEnc(onelxid,icd9='',dayrange=-3650):
    """if has prious Encounter
    """
    onelx = Lx.objects.get(id=onelxid)
    if dayrange<=0:
        start_date=getAnotherdate(onelx.LxDate_of_result,dayrange)
        end_date = getAnotherdate(onelx.LxDate_of_result,0)
    else:
        start_date=getAnotherdate(onelx.LxDate_of_result,0)
        end_date = getAnotherdate(onelx.LxDate_of_result,dayrange)
        
    encs = Enc.objects.filter(Q(EncPatient__id =onelx.LxPatient.id),
                              Q(EncICD9_Codes__icontains=icd9))
    for enc in encs:
        curdate = getAnotherdate(enc.EncEncounter_Date,0)
        if curdate>=start_date and curdate<=end_date:
            return 1
    return 0

                    
###################################
def haspriorLx(onelxid,cond, loinc=[],dayrange=-3650):
    onelx = Lx.objects.get(id=onelxid)
    if dayrange<=0:
        start_date=getAnotherdate(onelx.LxDate_of_result,dayrange)
        end_date = getAnotherdate(onelx.LxDate_of_result,0)
    else:
        start_date=getAnotherdate(onelx.LxDate_of_result,0)
        end_date =getAnotherdate(onelx.LxDate_of_result,dayrange)
        

    defines = ConditionLOINC.objects.filter(Q(CondiRule__ruleName__icontains=cond),
                                            Q(CondiLOINC__in=loinc))
    returnlx = getRelatedLx(cond,defines=defines,demog=onelx.LxPatient)
    lx = returnlx.exclude(id=onelx.id)
    
    for l in lx:
        curdate = getAnotherdate(l.LxDate_of_result,0)
        if curdate>=start_date and curdate<=end_date:
            return 1
    return 0



###################################
def haspriorNegaLx(onelxid, negaloinc=[],dayrange=-365,negvalues=[]):
    onelx = Lx.objects.get(id=onelxid)
    if dayrange<=0:
        start_date=getAnotherdate(onelx.LxOrderDate,dayrange)
        end_date = getAnotherdate(onelx.LxOrderDate,0)
    else:
        start_date=getAnotherdate(onelx.LxOrderDate,0)
        end_date = getAnotherdate(onelx.LxOrderDate,dayrange)
                
    all_lxs = Lx.objects.filter(Q(LxPatient=onelx.LxPatient),
                                Q(LxLoinc__in=negaloinc))

    nega_lxs=[]
    if negvalues:
        for onenegvalue in negvalues:
            nega_lxs=nega_lxs+list(all_lxs.filter(LxTest_results__istartswith ='%s' % onenegvalue))
    else:
        posi_lxs = all_lxs.filter(LxTest_results__istartswith='REACTI')
        if posi_lxs:
            nega_lxs = all_lxs.exclude(id__in =map(lambda x:x.id, posi_lxs))
        elif all_lxs:
            nega_lxs = all_lxs
            

    if not nega_lxs:
        return []

    returnl=[]
    for l in nega_lxs:
        curdate = getAnotherdate(l.LxOrderDate,0)
        if curdate>=start_date and curdate<=end_date:
            returnl.append(l.id)
    return returnl
   
###################################
def checkICD_ALTAST(demog_lx,altloinc=['1742-6','1920-8'],dayrange=15):
    """check (ICD9 or ALT or AST)
    """
    newcases={}
    for onedemogid in demog_lx.keys():
        relatedlxids = demog_lx[onedemogid]
        altlx = getALTAST(onedemogid,cond,altloinc)
        if altlx: ##2 or 3
            for onelx in relatedlxids: ##need within 14 days period
                for onealtlx in altlx:
                    if getLxduration(onelx,onealtlx.id) <dayrange and not newcases.has_key(onedemogid):
                        newcases[onedemogid]=[onelx,onealtlx.id]

        ##check ICD9
        returnencs = getEnc4ICD9(onedemogid,cond)
        if returnencs:
            for onelxid in relatedlxids: ##need within 14 days period
                onelx = Lx.objects.filter(id=onelxid)[0]
                for oneenc in returnencs:
                    if not newcases.has_key(onedemogid) and utils.getPeriod(onelx.LxDate_of_result, oneenc.EncEncounter_Date)<dayrange:
                        newcases[onedemogid]=[onelxid]
    return newcases


###################################
def isPositive_givenLx(cond,CondiLOINCids):

    defines = ConditionLOINC.objects.filter(Q(CondiRule__ruleName__icontains=cond),
                                            Q(CondiLOINC__in=CondiLOINCids))
    newlxs = getRelatedLx(cond,defines=defines)

    ################### For (87517,7285)=5009-6 * Result field says .SEE BELOW..
    ###################Comment field has the result in the following format:.Result: 421 IU/ml (2.62 log IU/ml).
    ###################A positive result for us is >50 IU/ml.
    newids = [l.id for l in newlxs]
    if string.find(string.upper(cond), 'HEPATITIS B')>-1 and '5009-6' in CondiLOINCids:
        lxs = Lx.objects.filter(Q(LxLoinc='5009-6'),
                                Q(LxTest_Code_CPT='87517'),
                                Q(LxComponent='7285')).exclude(LxTest_results__icontains="Negative")

#                                Q(LxTest_results__icontains='SEE BELOW'))

        for i in lxs:
            notes =string.upper(i.LxComment).split('NORMAL RANGE')
            if string.find(notes[0], '<')>-1:  ##normal result
                pass
            else:  #positive result
                newids.append(i.id)


    newlxs =Lx.objects.filter(id__in=newids)
    ###########################################################
                                                                           

    casedemogids = getCasedemogids(cond)
    if casedemogids: ##only report the first time
        newlxs= newlxs.exclude(LxPatient__id__in=casedemogids)
    recordl= sortLx(newlxs) ##sort by date of result
    demog_lx = buildCaseData(recordl)


    return demog_lx
                            

    
###################################
def getEnc4ICD9(demogid,cond):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=cond,CondiDefine=True)
    ruleicd9s = map(lambda x:x.CondiICD9.strip(), condicd9s)
    encids = []
    returnencs=[]
    for oneicd9 in ruleicd9s:
        if demogid:
            encs = Enc.objects.filter(Q(EncPatient__id =demogid),
                                  Q(EncICD9_Codes__icontains=oneicd9))
        else:
            encs = Enc.objects.filter(EncICD9_Codes__icontains=oneicd9)
            
        encids = encids + [i.id for i in encs]
        if encids:
            returnencs = Enc.objects.filter(id__in=encids)
    return returnencs

            
###################################    
def getALTAST(demogid,cond,loinclist = ['1742-6','1920-8']):
    defines = ConditionLOINC.objects.filter(Q(CondiRule__ruleName__icontains=cond),
                                            Q(CondiLOINC__in=loinclist))
    returnlx = getRelatedLx(cond,defines=defines,demog=Demog.objects.get(id=demogid))
    return returnlx
    


###################################
def getCasedemogids(condition):
    rule = Rule.objects.filter(ruleName__icontains=condition)[0]
    if rule.ruleinProd:
        curcases=Case.objects.filter(caseRule__ruleName__icontains=condition)
    else:
        curcases=TestCase.objects.filter(caseRule__ruleName__icontains=condition)
    casedemogids = [c.caseDemog.id for c in curcases]

    return casedemogids



###################################
###################################
def processAcuteHepA(condition):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)

    ##HepA definition a)
    demog_lx=isPositive_givenLx(condition,CondiLOINCids=['22314-9'])

    newcases = checkICD_ALTAST(demog_lx,dayrange=15)
    for onedemogid in  newcases.keys():
        caselxids =newcases[onedemogid]
        relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
        sendlxids = getLxids4dayrange(onedemogid, caselxids,condition,afterday=30,beforeday=-30)
        totallxids =  caselxids+sendlxids    
        makeNewCase(condition, onedemogid,totallxids,[],relatedencids,relatedicd9str)

                                            
###################################
###################################
def processAcuteHepB(condition):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)
    
    ##HepB definition a) #4='31204-1'
    demog_lx=isPositive_givenLx(condition,CondiLOINCids=['31204-1'])
    newcases = checkICD_ALTAST(demog_lx)
    for onedemogid in  newcases.keys():
        caselxids =newcases[onedemogid]
        relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
        makeNewCase(condition, onedemogid,caselxids,[],relatedencids,relatedicd9str)


    ###d)
    demog_lx=isPositive_givenLx(condition,CondiLOINCids=['5195-3'])
    for onedemogid in demog_lx.keys():
        caselxids = demog_lx[onedemogid]
        nonlx = haspriorNegaLx(caselxids[0], negaloinc=['5195-3'],dayrange=-365,negvalues=['NON-REACTIVE','NEGATIVE','NON-REAC','NEG'])
            
        if nonlx:
             if not haspriorLx(caselxids[0],condition,loinc=['5195-3'],dayrange=-3650) or not haspriorLx(caselxids[0],condition, loinc=['13126-8','5009-6','16934-2'],dayrange=-3650): ##no prior positive result for #5 or #7
                  if not haspriorEnc(caselxids[0],'070.32'): ## or not haspriorEnc(caselxids[0],'070.32',##no prior 070.32
                      relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
                      totallxids =  caselxids+nonlx
                      makeNewCase(condition, onedemogid,totallxids,[],relatedencids,relatedicd9str)

                                     
        

    ##HepB definition b) and c)
    demog_lx=isPositive_givenLx(condition,CondiLOINCids=['5195-3','13126-8','5009-6','16934-2'])
    newcases = checkICD_ALTAST(demog_lx, dayrange=22)
    for onedemogid in  newcases.keys():
        caselxids =newcases[onedemogid]
        ##check bilirubin
        bili_id = cal_bilirubin(onedemogid,caselxids)
        if not bili_id:
            continue
        elif bili_id:
            caselxids = caselxids+[bili_id]


        templxs = Lx.objects.filter(id__in=caselxids).order_by('LxOrderDate')
        caselxids = map(lambda x:x.id, templxs)
#        print 'caselxids=', `caselxids`
        
        if not haspriorLx(caselxids[0],condition,loinc=['5195-3'],dayrange=-3650) or not haspriorLx(caselxids[0],condition, loinc=['13126-8','5009-6','16934-2'],dayrange=-3650): ##no prior positive result for #5 or #7
            if not haspriorEnc(caselxids[0],'070.32'): ## or not haspriorEnc(caselxids[0],'070.32',15) : ##no prior 070.32
                
                relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
                if haspriorEnc(caselxids[0],'070.32',31) or haspriorEnc(caselxids[-1],'070.32',31):  ###Chronic HepB
#                    print '========================================================CHRONIC HEPATITIS B====', onedemogid
                    tempcondition = 'CHRONIC HEPATITIS B'
                    makeNewCase(tempcondition, onedemogid,caselxids,[],relatedencids,relatedicd9str)
                else:
                    makeNewCase(condition, onedemogid,caselxids,[],relatedencids,relatedicd9str)


###################################
def cal_bilirubin(demogid,caselxids, dayrange=22):

    
    ##bilirubin total
    stmt1 = """select id,LxTest_results
    from esp_lx
    where lxpatient_id=%s and LxLoinc='33899-6' and (LxTest_results>1.5 or LxTest_results like '%s>%s');
    """ % (demogid, '%%','%%')
    
    stmt2 = """select l1.LxOrderDate, l1.id, l2.id
        from esp_lx l1,  esp_lx l2
        where l1.lxpatient_id=%s and l2.lxpatient_id=%s and l1.LxLoinc='29760-6' and l2.LxLoinc='14630-8'
        and l1.LxOrderDate=l2.LxOrderDate and (l1.LxTest_results+l2.LxTest_results)>1.5
        """ % (demogid,demogid)
    for stmt in [stmt1, stmt2]:
        try:
            cursor.execute(stmt)
        except:
            print stmt
            sys.exit(1)
            
        res = cursor.fetchall()
        if res:
            for i in res:
                lxid = i[0]
                testids = [int(id) for id in caselxids + [lxid]]
            
                stmt3= """select min(LxOrderDate),max(LxOrderDate)
                from esp_lx
                where id in %s
                """ % str(tuple(testids))
                #print stmt3
                cursor.execute(stmt3)
                res3 = cursor.fetchall()
                dayrange= utils.getPeriod(res3[0][0],res3[0][1])
                if dayrange<=21:
                    return lxid
        
    return None
            



#    for l in loinc_l:
#        lxs = Lx.objects.filter(Q(LxPatient__id=demogid),
#                                Q(LxLoinc__in=list(l)))


        
    
###################################
###################################                
def processChronicHepB(condition):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)
     
    rule = Rule.objects.filter(ruleName__icontains=cond)[0]
    acutehepb = Rule.objects.filter(ruleName__icontains='ACUTE HEPATITIS B')[0]
   # returnencs = getEnc4ICD9('',condition)
   # if returnencs:
   #     for enc in returnencs:
            
  #          onedemogid = enc.EncPatient_id

  #          if rule.ruleinProd:
  #              c = Case.objects.filter(caseRule=acutehepb, caseDemog=Demog.objects.filter(id=onedemogid)[0])
  #          else:
  #              c = TestCase.objects.filter(caseRule=acutehepb, caseDemog=Demog.objects.filter(id=onedemogid)[0])
            
  #          if c: ##
  #              pass
  #          else: ##Chronic HepB
   #             relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, [], condicd9s,condition, afterday=14,beforeday=-14)
   #             makeNewCase(condition, onedemogid,[],[],relatedencids+[enc.id],relatedicd9str)

                                                                                        
    ##b) (#4='5195-3' or #5='13954-3' or #6='13126-8','16934-2','5009-6') positive and (#4/#5/#6)positive>6 months prior to the current positive result
    demog_lx=isPositive_givenLx(condition,CondiLOINCids=['5195-3','13954-3','13126-8','16934-2','5009-6'])
    for onedemogid in  demog_lx.keys():
        caselxids =demog_lx[onedemogid]
        if rule.ruleinProd:
            c = Case.objects.filter(caseRule=acutehepb, caseDemog=Demog.objects.filter(id=onedemogid)[0])
        else:
            c = TestCase.objects.filter(caseRule=acutehepb, caseDemog=Demog.objects.filter(id=onedemogid)[0])
            
        if c: ##
            ##need check date range>12 months
            c = c[0]
            clxids = [i for i in c.caseLxID.split(',') if i.strip()]
            lxs = Lx.objects.filter(id__in=clxids).order_by('LxOrderDate')
            maxdate= getAnotherdate(lxs[0].LxOrderDate, 365)
            for caselxid in caselxids:
                curdate = getAnotherdate(Lx.objects.filter(id=caselxid)[0].LxOrderDate,0)
                if curdate>maxdate:  ###Chronic HepB
                    relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
                    makeNewCase(condition, onedemogid,clxids+[caselxid],[],relatedencids,relatedicd9str)
                    break
        else: ##Chronic HepB

            relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
            makeNewCase(condition, onedemogid,caselxids,[],relatedencids,relatedicd9str)

                                 

###################################
###################################            
def processHepBPreg(condition):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)
    
    demog_lx=isPositive_givenLx(condition,CondiLOINCids=['5195-3','13954-3','13126-8','16934-2','5009-6'])

    errs=[]
    for onedemogid in  demog_lx.keys():
        caselxids =demog_lx[onedemogid]
        encs = Enc.objects.filter(EncPatient__id =onedemogid, EncPregnancy_Status='Y').order_by('EncEncounter_Date')
        if not encs:
            continue


        for  caselxid in caselxids:
            curdate = getAnotherdate(Lx.objects.filter(id=caselxid)[0].LxOrderDate,0)
            maxdate = getAnotherdate(Lx.objects.filter(id=caselxid)[0].LxOrderDate,29)
            #minencdate = getAnotherdate(encs[0].EncEncounter_Date, 0)
            for enc in encs:
                date1 = enc.EncEDC
                date2 = enc.EncEncounter_Date
                try:
                    if utils.getPeriod(date1,date2)>290:
                        ##do not use this enc
                        continue
                    else:
                        thisenc = enc
                        break
                except:
                    continue
                    
            if thisenc.EncEDC:
                minencdate = getAnotherdate(thisenc.EncEDC, -280)
                maxencdate = getAnotherdate(thisenc.EncEDC, 0)
                if (curdate>=minencdate and curdate<=maxencdate) or (maxdate>=minencdate and maxdate<=maxencdate): ##is a case
                    relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, [caselxid], condicd9s,condition, afterday=14,beforeday =-14)
                    makeNewCase(condition, onedemogid,[caselxid],[],relatedencids+[thisenc.id],relatedicd9str)
                    break
                                                                
            elif not thisenc.EncEDC:
                msg = "ERROR: Patient: %s, EncID: %s, EncDate: %s\n" % (onedemogid, thisenc.EncEncounter_ID, thisenc.EncEncounter_Date)
                if msg not in errs:
                    errs.append(msg)
                continue 

    if errs:
        errstr = '\n'.join(errs)
        iclogging.error('Error for  HepB with Pregnancy: %s' % errstr)
        try:
            utils.sendoutemail(towho=['rexua@channing.harvard.edu', 'rerla@channing.harvard.edu'],msg=errstr, subject='ESP ERROR - HepB with Pregnancy')
        except:
            pass
            
            
###################################
def Hepc_posi(cond, onecrit, caselxid, onedemogid, dayrange=29):

    patient = Demog.objects.get(id__exact=onedemogid)

    crit_lxs =Lx.objects.filter(Q(LxPatient__id=onedemogid),
                                Q(LxLoinc__in=onecrit))
    if crit_lxs:
        defines = ConditionLOINC.objects.filter(Q(CondiRule__ruleName__icontains=cond),
                                                Q(CondiLOINC__in=onecrit))
        returnlx = getRelatedLx(cond,defines=defines,demog=patient)

        for posi_lx in returnlx:
            if getLxduration(caselxid, posi_lx.id,1) <dayrange:
                return (1, [posi_lx.id])
        return (0, [])
    else:
        return (1,[])
                                                                   
            
###################################
###################################
def processAcuteHepC(condition):


    casedemogids = getCasedemogids(condition)

    ##HepC definition a),b):(1 0r 2) and [3)16128-1 or 5)'5199-5' positive] 
    for oneloinc in ['16128-1','6422-0','34704-7','10676-5','38180-6','5012-0','11259-9','20416-4']:
        condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)
        demog_lx=isPositive_givenLx(condition,[oneloinc])
        newcases = checkICD_ALTAST(demog_lx,['1742-6'],dayrange=29)
        for onedemogid in  newcases.keys():
            if onedemogid in casedemogids:
                continue
            
            caselxids =newcases[onedemogid][:1]

            ##a),b): no ICD9 070.54 before
            if haspriorEnc(caselxids[0],'070.54',-3650):
                continue
            if haspriorEnc(caselxids[0],'070.70',-3650):
                continue
                            
            ##need check 7)22314-9 and 8)31204-1 are negative
            isnegaA = isNegative(onedemogid,'22314-9',caselxids, dayrange=29)
            isnegaB = isNegative(onedemogid,'31204-1',caselxids, dayrange=29)

            ###need check 9) 16933-4 is non-reactive
            isnegaC = isNegative(onedemogid,'16933-4',caselxids, dayrange=29, negvalues=['NON-REAC', 'NEG', 'NON- REAC'])

                                    
            ##

            if isnegaA and (isnegaB or  isnegaC):
                isposi4,critlxid4=Hepc_posi(condition, ['MDPH-144'], caselxids[0], onedemogid, dayrange=29)
                isposi5,critlxid5=Hepc_posi(condition, ['5199-5'], caselxids[0], onedemogid, dayrange=29)
                isposi6,critlxid6=Hepc_posi(condition, ['6422-0','34704-7','10676-5','38180-6','5012-0','11259-9','20416-4'], caselxids[0], onedemogid, dayrange=29)
                
                if (oneloinc=='16128-1' and isposi4 and isposi5 and isposi6) or (oneloinc!='16128-1' and isposi4 and isposi5): ##meet case requirement
                    pass
                else:
                    continue
                
                if not haspriorLx(caselxids[0],condition,loinc=['16128-1'],dayrange=-3650) or haspriorLx(caselxids[0],condition,loinc=['5199-5'],dayrange=-3650) or not haspriorLx(caselxids[0],condition, loinc=['6422-0','34704-7','10676-5','38180-6','5012-0','11259-9','20416-4'],dayrange=-3650): ##no prior positive result for #3 or #5 or #6 ever
                      
                    relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
                    sendlxids = getLxids4dayrange(onedemogid, caselxids,condition,afterday=15,beforeday=-15)
                    totallxids =  caselxids+sendlxids
                    makeNewCase(condition, onedemogid,totallxids,[],relatedencids,relatedicd9str)
            
    ##HepC, c)&d): [3)'16128-1' or 6) positive] and 3)'16128-1' negative within the prior 12 months
    for oneloinc in ['16128-1', '6422-0','34704-7','10676-5','38180-6','5012-0','11259-9','20416-4']:
        demog_lx=isPositive_givenLx(condition,[oneloinc])
        for onedemogid in  demog_lx.keys():
            caselxids =demog_lx[onedemogid]

            ##need check 3)'16128-1' negative within the prior 12 months
            negalxids = haspriorNegaLx(caselxids[0], negaloinc=['16128-1'],dayrange=-365)
            if negalxids:
                relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=14,beforeday=-14)
                sendlxids = getLxids4dayrange(onedemogid, caselxids,condition,afterday=15,beforeday=-15)
                totallxids =  caselxids+sendlxids+negalxids
                makeNewCase(condition, onedemogid,totallxids,[],relatedencids,relatedicd9str)

###################################
###################################
def  checkepisode(onedemogid, cond, date1,dayrange=730):
    cases = Case.objects.filter(caseDemog__id__exact=onedemogid,caseRule__ruleName__icontains=cond).order_by('id')
    if cases:
        onecase = cases[len(cases)-1]
        if onecase.caseRxID:
            onerx = Rx.objects.filter(id=onecase.caseRxID.split(',')[0])[0]
            date2 = onerx.RxOrderDate
            if utils.getPeriod(date1, date2) > dayrange: ##need report again
                return 1
            else:
                return 0
        elif onecase.caseLxID:
            onelx = Lx.objects.filter(id=onecase.caseLxID.split(',')[0])[0]
            date2 = onelx.LxOrderDate
            if utils.getPeriod(date1, date2) > dayrange: ##need report again
                return 1
            else:
                return 0
        else:
            return 1
    elif not cases:
        return 1
                                                                
###################################                            
###################################
def processTB(condition):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)
    drugmaps = ConditionDrugName.objects.filter(CondiRule__ruleName__icontains=condition,CondiSend=True)
    exclude_dict = {'INH': ['INHALE','INHIB'], 'PZA':['CAPZA']}

    ##1: prescription for PZA or Pyrazinnamide
    totaldemogids = []
    for med in ['Pyrazinamide','PZA']:
        rxs = Rx.objects.filter(RxDrugName__icontains=med)
        if med in exclude_dict.keys():
            for onemed in exclude_dict[med]:
                rxs=rxs.exclude(RxDrugName__icontains=onemed)
            
        demogids = map(lambda x:(x.RxPatient.id, None), rxs)
        totaldemogids = totaldemogids+demogids
    demogids = dict(totaldemogids).keys()

    for onedemogid in demogids:
        caselxids=[]
        relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, caselxids, condicd9s,condition, afterday=None,beforeday=None)
        sendlxids = getLxids4dayrange(onedemogid, caselxids,condition,afterday=None,beforeday=None)
        totallxids =  caselxids+sendlxids
        relatedrxids = getRxids4dayrange(onedemogid,[],drugmaps, condition,afterday=None,beforeday=None,firstuseonly=1,exclude_dict=exclude_dict)

        ##Let's set the episode length for TB at 2 years meaning report only once in a two year period but possible to have a new episode after that
        rxdate = Rx.objects.filter(id=relatedrxids[0])[0].RxOrderDate
        if checkepisode(onedemogid, condition,rxdate,730):
            makeNewCase(condition, onedemogid,totallxids,relatedrxids,relatedencids,relatedicd9str)
                                                    
    casedemogids = getCasedemogids(condition)

    ##2: Lx and ICD9 14 days before Lx or 60 days after Lx
    newlxs = getRelatedLx(condition)
    if casedemogids: ##only report the first time
        newlxs= newlxs.exclude(LxPatient__id__in=casedemogids)
    recordl = sortLx(newlxs)
    demog_lx = buildCaseData(recordl)
    for onedemogid in demog_lx.keys():
        relatedlxids = demog_lx[onedemogid]
        relatedencids,relatedicd9str = getEncids4dayrange(onedemogid, relatedlxids, condicd9s,condition, afterday=61,beforeday=15)
        if relatedicd9str: ##is a case
            relatedrxids = getRxids4dayrange(onedemogid,[],drugmaps, condition,afterday=None,beforeday=None,firstuseonly=1,exclude_dict=exclude_dict)
            lxdate = Lx.objects.filter(id=relatedlxids[0])[0].LxOrderDate
            if checkepisode(onedemogid, condition,lxdate,730):
                makeNewCase(condition, onedemogid,relatedlxids,relatedrxids,relatedencids,relatedicd9str)

    casedemogids = getCasedemogids(condition)
     
    ##3: Drugs and ICD9 within 60 days
    define_drugmaps = ConditionDrugName.objects.filter(CondiRule__ruleName__icontains=condition,CondiDefine=True)

    ###The TB logic must be coded as INH but not INHALE*
    rx_dict = getPids4Drugs(define_drugmaps, exclude_dict = exclude_dict)
    relatedlxids=[]

    for onedemogid in rx_dict.keys():
        if onedemogid  in casedemogids:  ###only report the first time????
            continue
        relatedrxids = rx_dict[onedemogid]
        mindate,maxdate =  getRx_MinMaxDate(relatedrxids,afterday=61,beforeday=-61)
        relatedencids,relatedicd9str = getRelatedEncids(onedemogid,condicd9s,mindate, maxdate)
        if relatedicd9str: ##is a case
            rxdate = Rx.objects.filter(id=relatedrxids[0])[0].RxOrderDate
            if checkepisode(onedemogid, condition,rxdate,730):
                makeNewCase(condition, onedemogid,relatedlxids,relatedrxids,relatedencids,relatedicd9str)
        

###################################
###################################
def processSyphilis(cond):
    final_dict={}
    #1) ICD-9 code 090-097
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=cond,CondiDefine=True)
    ruleicd9s = map(lambda x:x.CondiICD9.strip(), condicd9s)
    demog_dict={}
    for oneicd9 in ruleicd9s:
        res = icd9Fact.objects.filter(icd9Code__icontains=oneicd9)
        for onerec in res:
            encpid = onerec.icd9Patient_id
            onevalue = (onerec.icd9Enc_id, onerec.icd9Code,onerec.icd9EncDate) 
            if demog_dict.has_key(encpid) and onevalue not in demog_dict[encpid]:
                demog_dict[encpid].append(onevalue)
            else:
                demog_dict[encpid]=[onevalue]

    stmt = """ select distinct esp_demog.id,esp_rx.id, RxStartDate, RxDrugName, RxQuantity, RxDrugDesc
               from esp_rx, esp_demog
               where esp_rx.RxPatient_id=esp_demog.id
               and esp_demog.id in %s
               and upper(RxDrugName) like '%s%s%s'
               """
    if len(demog_dict.keys())>1:
        icd9demogids = str(tuple(map(lambda x: int(x), demog_dict.keys())))
    elif len(demog_dict.keys())==1:
        icd9demogids = '(%s)' % int(demog_dict.keys()[0])
    else:
        icd9demogids=''
        
    for m,temp in [  ("CEFTRIAXONE%%1G", ""),  ("CEFTRIAXONE%%2G", ""), ("1G%%CEFTRIAXONE", ""), ("2G%%CEFTRIAXONE", ""), ("DOXYCYCLINE", " and  RxQuantity>13"), ("PENICILLIN G", ""), ("PEN G", "")]:
        if icd9demogids=='':
            break
        
        if not temp:
            cursor.execute(stmt % (icd9demogids, '%%', m,  '%%'))
        else:
            newstmt = stmt % (icd9demogids, '%%',m, '%%') + temp
            cursor.execute(newstmt)
            
        res = cursor.fetchall()

        for onerow in res:
            (rxpid, rxid,rxdate,rxname,quan, rxdesc) = onerow
            if not demog_dict.has_key(rxpid):
                continue
            ###icd9 code is in (090 - 097)
            for encid, icd9,encorderdate in demog_dict[rxpid]:
                if utils.getPeriod(encorderdate,rxdate)< 15:
                    if final_dict.has_key(rxpid):
                        if encid not in final_dict[rxpid][0]:
                            final_dict[rxpid][0].append(encid)
                        if rxid not in final_dict[rxpid][1]:    
                            final_dict[rxpid][1].append(rxid)
                        if icd9 not in final_dict[rxpid][2]:
                            final_dict[rxpid][2].append(icd9)
                    else:
                        final_dict[rxpid] = [[encid], [rxid], [icd9]]


    casedemogids = getCasedemogids(cond)
    for rxpid in final_dict.keys():
        (encids,rxids,icd9s) = final_dict[rxpid]
        if rxpid in casedemogids:  #only report once in life time
            ##update case
            continue
       
        icd9str = ','.join(icd9s)
        rpr_lxs = Lx.objects.filter(Q(LxPatient__id=rxpid),
                                    Q(LxLoinc__in=['20507-0']))
        recordl = sortLx(rpr_lxs)
        recl = map(lambda x:x[1], recordl)
        recl.sort()

        makeNewCase(cond, rxpid,recl,rxids, encids,icd9str)



    ###
    syphilis_2(cond)
    updatingSyphilis(cond)

###################################
####Update cases
def updatingSyphilis(cond):

    rule = Rule.objects.filter(ruleName__icontains=cond)[0]
    
    if rule.ruleinProd:
        curcases=Case.objects.filter(caseRule__ruleName__icontains=cond)
    else:
        curcases=TestCase.objects.filter(caseRule__ruleName__icontains=cond)


    curc = curcases.filter(caseWorkflow__exact='S')

    for c in curc:

        rpr_lxs = Lx.objects.filter(Q(LxPatient__id=c.caseDemog_id),
                                    Q(LxLoinc__in=['20507-0']))
        lxindb = c.caseLxID.split(',')
        if rpr_lxs and lxindb:
            lxdb = Lx.objects.filter(id__in=lxindb).order_by('LxDate_of_result')
            maxrec=lxdb[len(lxdb)-1].LxDate_of_result
            newlx = filterOldLxs(rpr_lxs, cutoffd = datetime.date(int(maxrec[:4]),int(maxrec[4:6]),int(maxrec[6:8])) )
        elif rpr_lxs:
            newlx = rpr_lxs
        else:
            newlx=None

        if newlx:
            newids = [i.id for i in newlx]
            note = 'CaseID-%s: Already sent. Set to re-send due to new Lx tests. ' % c.id 
            c.caseWorkflow='Q'
            finallxids = ','.join(dict(map(lambda x: ('%s' % x, None), lxindb+newids)).keys())
            c.caseLxID=finallxids
            c.save()
            iclogging.info('\n\nUpdate case: %s' % c.id)
            updateCaseWF(c,note = note)
        

                                
    
###################################    
def syphilis_2(cond):
    condicd9s = ConditionIcd9.objects.filter(CondiRule__ruleName__icontains=cond,CondiSend=True)
    drugmaps = ConditionDrugName.objects.filter(CondiRule__ruleName__icontains=cond,CondiSend=True)
            
    ###process Syphilis 2nd criteria
    casedemogids = getCasedemogids(cond)

    defines = ConditionLOINC.objects.filter(Q(CondiRule__ruleName__icontains=cond),
                                            Q(CondiLOINC__in=['11597-2','34147-9']))
    returnlx = getRelatedLx(cond,defines=defines)
    demog_lx = buildCaseData(sortLx(returnlx))
    for onedemogid in demog_lx.keys():
        if onedemogid in casedemogids:  #only report once in life time
            continue
        
        relatedlxids=[]
        rpr_lxs = Lx.objects.filter(Q(LxPatient__id=onedemogid),
                                Q(LxLoinc__in=['20507-0']) ,
                                Q(LxTest_results__contains='1:'))
        for onerpr in rpr_lxs:
            denominator = string.split(onerpr.LxTest_results, ':')[1].strip()
            if int(denominator)>=8:
                ##it is a case
                relatedlxids.append(onerpr.id)

        if len(relatedlxids)>0: ##it is a case
            relatedlxids =relatedlxids+demog_lx[onedemogid]
            #1. get related Enc
            relatedencids,relatedicd9str = getEncids4dayrange(onedemogid,relatedlxids,condicd9s,cond,afterday=29,beforeday=-29)
             
            #2. get related Rx
            relatedrxids = getRxids4dayrange(onedemogid,relatedlxids,drugmaps, cond,afterday=29,beforeday=-29)
            makeNewCase(cond,onedemogid,relatedlxids, relatedrxids,relatedencids,relatedicd9str)

    

            
###################################
###################################
def getPids4Drugs(define_drugmaps, exclude_dict={}):
    """rx_dict={pid: {DrugName:[(date,name,desc,rxid), ...],  ...},
             ...}
    """
    rx_dict={}
    return_dict={}
    for onedrug in define_drugmaps:
        medname = onedrug.CondiDrugName
        rxs = Rx.objects.filter(RxDrugName__icontains=medname)
        if exclude_dict.has_key(medname):
            for excname in exclude_dict[medname]:
                rxs=rxs.exclude(RxDrugName__icontains=excname)
       # print 'MED=', medname, ' Rxs=', len(rxs), '\n'
        for onerow in rxs:
            pid = int(onerow.RxPatient_id)
            if rx_dict.has_key(pid):
                if rx_dict[pid].has_key(medname):
                    rx_dict[pid][medname].append(onerow.id)
                else:
                    rx_dict[pid][medname]=[onerow.id]
            else: ##no key: pid
                rx_dict[pid]={medname:[onerow.id]}

    for pt in rx_dict.keys():
        if len(rx_dict[pt])>1: ##have 2 or more of the medications
            totalrx=[]
            for rxl in rx_dict[pt].values():
                totalrx=totalrx+rxl
            rxids = dict(map(lambda x:(x,None), totalrx)).keys()
            rxids.sort()
            return_dict[pt] =  rxids

    return return_dict

                                                                                                                            
###################################
#################################
def isNegative(onedemogid,oneloinc,caselxids, dayrange=29,  negvalues=None):
    """check if this demog have negative lx for a given loinc withion a certain period
    """
    relatedlxs = []
    if negvalues:
        for i in negvalues:
            neg_lxs = Lx.objects.filter(Q(LxPatient__id=onedemogid),
                                        Q(LxLoinc__in=[oneloinc]),
                                        Q(LxTest_results__istartswith='%s' % i))
            if neg_lxs:
                relatedlxs = relatedlxs+ list(neg_lxs)

    else:
                                                
        ##see if any positive one
        posi_lxs = Lx.objects.filter(Q(LxPatient__id=onedemogid),
                            Q(LxLoinc__in=[oneloinc]),
                            Q(LxTest_results__istartswith='REACTI'))

        relatedlxs=relatedlxs+list(posi_lxs)

    posil=[]
    if relatedlxs:
        for caselxid in caselxids:
            for posi_lx in relatedlxs:
                if int(caselxid)!=int(posi_lx.id) and getLxduration(caselxid, posi_lx.id) <dayrange:
                    posil.append(posi_lx)

    if negvalues and posil:
        return 1
    elif negvalues:
        return 0
    elif not negvalues and posil:
        return 0
    else:
        return 1

    

################################
################################
if __name__ == "__main__":

    TEST=1
    iclogging.info('==================\n')

    TestCase.objects.all().delete()
    iclogging.info('Delete all cases in Test cases\n')

    conditions = Rule.objects.all().order_by('ruleName')
    for c in conditions:
        cond = c.ruleName
        iclogging.info('process %s\n' % cond)

        if TEST==1:
            if string.find(string.upper(cond), 'ACUTE HEPATITIS B')>-1:
                processAcuteHepB(cond)
            else:
                continue
            
        if string.upper(cond) in ('ACUTE HEPATITIS A'):
            processAcuteHepA(cond)
        elif string.upper(cond) in ('ACUTE HEPATITIS B'):
            processAcuteHepB(cond)
        elif string.upper(cond) in ('ACUTE HEPATITIS C'):
            processAcuteHepC(cond)
        elif string.upper(cond) in ('CHRONIC HEPATITIS B'):
            processChronicHepB(cond)
        elif string.upper(cond) in ('ACTIVE HEPATITIS B IN PREGNANCY'):
            processHepBPreg(cond)
                        
        elif string.upper(cond) in ('ACTIVE TUBERCULOSIS'):
            processTB(cond)
        elif string.upper(cond) in ('SYPHILIS'):
            processSyphilis(cond)
        elif  string.upper(cond) in ('VAERS FEVER', 'FEBRILE SEIZURE'):
            pass
        else: #other conditions
            processoneCondition(cond)

    ########
    iclogging.info('Start to check cases for updating')
    allcases = Case.objects.filter(casecreatedDate__gt=datetime.datetime.today()-datetime.timedelta(28))
    indx=1
    for onecase in allcases:
        updateSentCase(onecase)
        if indx%50==0:
            iclogging.info('Checked %s of %s cases' % (indx, len(allcases)))
        indx=indx+1


    ##send out email for daily summary
    k=case_dict.keys()
    k.sort()
    msg='Date: %s\n' % datetime.datetime.now().strftime('%Y%m%d')
    if not k:
        msg = msg+'There is no new case detected\n'
        
    for i in k:
        msg = msg+ '%s:\t\t%s\n' % (i, case_dict[i])

    if TEST==1:
        utils.sendoutemail(towho=['ross.lazarus@channing.harvard.edu'],msg=msg, subject='lkenpesp2 new server Testing ESP - Daily summary of all detected cases')
    else:    
        utils.sendoutemail(towho=['rexua@channing.harvard.edu', 'MKLOMPAS@PARTNERS.ORG'],msg=msg, subject='ESP - Daily summary of all detected cases')
     
    
    iclogging.shutdown()
