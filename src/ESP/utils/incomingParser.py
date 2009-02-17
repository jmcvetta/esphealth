# incoming parser
# uses a generator for large file processing
# of delimited files

import os
import sys
import string
import re
import copy
import shutil
import StringIO
import traceback
import smtplib
import logging
import exceptions
import MySQLdb
import optparse
import pprint

import django, datetime,time
from django.db.models import Q
from django.db import connection

from ESP.settings import *
from ESP.esp.models import *
import ESP.utils.utils as utils
from ESP import settings
from ESP.utils.utils import log
from ESP.esp import models


cursor = connection.cursor()


VERSION = '0.2'
DO_VALIDATE = 1 # set to zero to avoid the validation step
REJECT_INVALID = 1 # don't process if any errors - usually are missing provider so ignore


today=datetime.datetime.now().strftime('%Y%m%d')

DBTIMESTR = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
FILEBASE='epic' ##'epic' or 'test'


##store the new CPT code for Chlamydia
alertcode =[]


###############################
hasEnc=1
hasMem=1
hasProv=1
hasOrd=1
hasRes=1
hasMed=1
hasImm=1
hasPrb=0
hasSoc=0
hasAll=0


###############################
def getlines(fname):
    """uses ram - not a great idea for million line files
    """
    try:
        lines = file(fname).readlines()
    except:
        log.error('Can not read file:%s\n' % fname)
        return []
    returnl = [x.split('^') for x in lines[:-1] if len(x.split('^')) > 1]
    log.info('Parser Process %s: %s records\n' % (fname, len(returnl)))
    return returnl

###############################

def splitfile(fname=None,delim='^',validate=False):
    """ generator to return delim split lines
    ross lazarus nov 21 2006
    """
    f = file(fname,'r')
    r = []
    more = 1
    n = 0
    while more:
       try:
          r = f.next()
       except:
          more = 0
          raise StopIteration
       n += 1
       
       if not validate:
          ll = r.split(delim) # use original file.next!
          r=[re.sub("'", "''", x.strip()) for x in ll]


       if n % 1000000 == 0:
           log.info('At line %d in file %s' % (n,fname))

       if validate or len(r) > 2: # ignore lines without delimiters if not validation phase
           yield (r, n)
                      
###################################
def runSql(stmt,values=None):
    log.debug('Running SQL query "%s" with values "%s".' % (stmt, values))
    try:
        if not values:
            cursor.execute(stmt)
        else:
            cursor.execute(stmt,values)
    except exceptions.BaseException, e: # FIXME: It is a bad idea to catch *all* exceptions
        errmsg = "ERROR: %s; VALUES == %s\n" % (stmt,str(values))
        # Yeah, it's ugly the way I have two logging sytems running at once.
        # That's something to clean up in the future.
        log.error(errmsg)
        log.error(e)
        #cursor.execute("rollback;")
       # sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg='SQL loading errors when running incomingParse.py;\n%s' % errmsg)
        
    #    sys.exit(1)
        
################################
def parseProvider(incomdir, filename):
    """
    """

    provdict={}
    fname = os.path.join(incomdir,'%s' % filename)
    f = splitfile(fname,'^')
    for (items,line) in f:

        if not items or items[0]=='CONTROL TOTALS':
            filelines = line
            continue
        
        try:
            phy,lname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone  = items #[x.strip() for x in items]
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
        if not fname:
            fname = 'Unknown'
        if not lname:
            lname = 'Unknown'
        if phone:
            phone = re.sub('\D', '', phone)

        provid = searchId('select id from esp_provider where provCode=%s', (phy,))
        if provid: ##need update
            prov_str = """update esp_provider set
                            provCode=%s,
                            provLast_Name=%s,
                            provFirst_Name=%s,
                            provMiddle_Initial =%s,
                            provTitle=%s,
                            provPrimary_Dept_Id=%s,
                            provPrimary_Dept=%s,
                            provPrimary_Dept_Address_1=%s,
                            provPrimary_Dept_Address_2=%s,
                            provPrimary_Dept_City=%s,
                            provPrimary_Dept_State=%s,
                            provPrimary_Dept_Zip=%s,
                            provTelAreacode=%s,
                            provTel=%s,
                            lastUpDate=%s
                            where id =%s
                       """
            values = (phy,lname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone, DBTIMESTR, provid)
            runSql(prov_str,values)
        elif not provid: #new record
            prov_str = """insert into esp_provider
            (provCode,provLast_Name,provFirst_Name,provMiddle_Initial,provTitle, provPrimary_Dept_Id,provPrimary_Dept,provPrimary_Dept_Address_1,provPrimary_Dept_Address_2,provPrimary_Dept_City,provPrimary_Dept_State,provPrimary_Dept_Zip,provTelAreacode,provTel,lastUpDate,createdDate)
            values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s)
                       """
            values = (phy,lname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone, DBTIMESTR,DBTIMESTR)
            runSql(prov_str,values)
            provid = cursor.lastrowid

        provdict[phy]=provid    
        
    movefile(incomdir, filename,filelines)
    return provdict

################################
def parseDemog(incomdir, filename):
    """
    """
    demogdict={}
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue                                
        try:
            pid,mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,phy,mari,religion,alias,mom,death  = items #[x.strip() for x in items]            
        except:
            log.error('Parser %s: wrong size - %s at line# %d' % (filename,str(items),linenum)) # 25 needed
            continue

        
        #fake sone
        if not fname:
            fname = 'Unknown'
        if not lname:
            lname = 'Unknown'
        #if not phonearea: #fake one
        #    phonearea='999'
        if phone:
            phone = re.sub('\D', '', phone)

        if not cty:
            cty='USA'                
        providerid = searchId('select id from esp_provider where provCode=%s', (phy,))

        if not providerid:
            providerid='NULL'

        demogid = searchId('select id from esp_demog where DemogPatient_Identifier=%s', (pid,))
        if demogid: #update
            demog_str= """update esp_demog
            set DemogPatient_Identifier=%s,
                DemogMedical_Record_Number=%s,
                DemogLast_Name=%s,
                DemogFirst_Name=%s,
                DemogMiddle_Initial=%s,
                DemogAddress1=%s,
                DemogAddress2=%s,
                DemogCity=%s,
                DemogState=%s,
                DemogZip=%s,
                DemogCountry=%s,
                DemogAreaCode=%s,
                DemogTel=%s,
                DemogExt=%s,
                DemogDate_of_Birth=%s,
                DemogGender=%s,
                DemogRace=%s,
                DemogHome_Language =%s,
                DemogSSN=%s,
                DemogMaritalStat=%s,
                DemogReligion =%s,
                DemogAliases=%s,
                DemogMotherMRN=%s,
                DemogDeath_Date=%s,
                DemogProvider_id=%s,
                lastUpDate=%s
                where id =%s
            """
            values = (pid, mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,mari,religion,alias,mom,death,providerid,DBTIMESTR,demogid)
            runSql(demog_str,values)
        else:
            demog_str= """insert into esp_demog
             (DemogPatient_Identifier,DemogMedical_Record_Number,DemogLast_Name,DemogFirst_Name,DemogMiddle_Initial,DemogAddress1,DemogAddress2,DemogCity,DemogState,DemogZip,DemogCountry,DemogAreaCode,DemogTel,DemogExt,DemogDate_of_Birth,DemogGender,DemogRace,DemogHome_Language ,DemogSSN,DemogMaritalStat,DemogReligion ,DemogAliases,DemogMotherMRN,DemogDeath_Date,DemogProvider_id,lastUpDate,createdDate)
                         values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)
                       """
            values = (pid, mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,mari,religion,alias,mom,death,providerid,DBTIMESTR,DBTIMESTR)
            runSql(demog_str,values)
            demogid = cursor.lastrowid
#        demogid = updateDB('esp_demog',demog_str,values, demogid)
        
        demogdict[pid]=demogid
        

    movefile(incomdir, filename,filelines)
    return demogdict

###################################
def searchId(stmt, values ):
#    stmt = """select id from %s where %s """ % (table, whereclause)
    runSql(stmt,values)
    res = cursor.fetchall()
    if res:
        return res[0][0]
    else:
        return None
                    
###################################
###################################
def convertWgHg(wghg,unit,factor,factor2):
    """convert wghg (weight or height) from lbs to KG or from feet to cm
    assume weight/height always includes the unit 'lbs' or '\''
    """
    
    import re
    wghg =wghg.upper().strip()
    lbft_list=[i.strip() for i in wghg.split(unit) if i]
    lbft=lbft_list[0]
    if not lbft:
        lbft='0'
        
    if len(lbft_list)>1:
        p=re.compile('[A-Z"]')
        ozinch=[i.strip() for i in p.split(lbft_list[1]) if i][0]
    else:
        ozinch='0'
        
    new_wghg=(float(lbft.strip())*factor+float(ozinch.strip()))*factor2
    #if '%.2f' % weight=='0.00':
    #    print w
    return '%.2f' % new_wghg


###################################
###################################
def getEDC(espencid,edc,pregstatus,encdate):
    period = 300
    enc = Enc.objects.filter(id=espencid)[0]
    if edc=='' and enc.EncEDC =='':
        return (edc,pregstatus)
    elif edc=='' and enc.EncEDC !='':
        if utils.getPeriod(encdate, enc.EncEDC)>period:
            log.info("EDCFile is Null: espId=%s, EncID=%s, Encdate=%s, edcDB=%s*edcfile=%s-->%s" % (enc.id,enc.EncEncounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc,edc) )
            
            return (edc, pregstatus)
        else:
            return (enc.EncEDC, 'Y')
    elif edc!='' and enc.EncEDC=='':
        if utils.getPeriod(encdate, edc)<=period:
            return (edc, pregstatus)
        else:
            log.info("EDCDB is Null: espId=%s, EncID=%s, Encdate=%s, edcDB=%s*edcfile=%s-->%s" % (enc.id,enc.EncEncounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc,enc.EncEDC) )
            return (enc.EncEDC, '')
    elif edc!='' and enc.EncEDC!='':
        if  enc.EncEDC!=edc:
            if utils.getPeriod(encdate, edc)>period and  utils.getPeriod(encdate, enc.EncEDC)>period:
                newedc=''
                newst = ''
            elif  utils.getPeriod(encdate, edc)<=period and utils.getPeriod(encdate, enc.EncEDC)>period:
                newedc = edc
                newst=pregstatus
            elif utils.getPeriod(encdate, edc)>period and utils.getPeriod(encdate, enc.EncEDC)<=period:
                newedc =enc.EncEDC
                newst='Y'
            elif utils.getPeriod(encdate, edc)<=period and utils.getPeriod(encdate, enc.EncEDC)<=period:
                newedc =edc
                newst=pregstatus
                
            log.info("DIFF: espId=%s, EncID=%s, Encdate=%s, edcDB=%s*edcfile=%s-->%s" % (enc.id,enc.EncEncounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc,newedc) )
            return (newedc,newst)

    return (edc, pregstatus)

        
        
################################
################################
def parseEnc(incomdir, filename,demogdict,provdict):
    '''
    Load Encounter data from ETL files
    '''
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):

        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue
        try:
            pid,mrn,encid,encd,close,closed,phy,deptid,dept,enctp,edc,temp,cpt,weight,height,bpsys,bpdias,o2stat,peakflow,icd9  = items #[x.strip() for x in items]
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue

        if edc:
            pregstatus='Y'
        else:
            pregstatus=''
                        
        try:    
            demogid = demogdict[pid]    
        except:
            log.warning('Parser In ENC: NO patient found: %s\n' % str(items))
            continue

        if weight:
            try:
                weight= '%s kg' % convertWgHg(weight,'LBS',16,0.02835)
            except:
                log.error('Parser %s: Convert weight : %s for Patient %s' % (filename,weight,mrn))
        if height:
            try:
                height= convertWgHg(height,'\'',12,2.54)
            except:
                log.error('Parser %s: Convert height : %s for Patient %s' % (filename,height,mrn))
            
        if o2stat:
            try:
                o2stat=int(o2stat)
            except:
                log.error('Parser %s: NonInt O2stat: %s for Patient %s' % (filename,o2stat,mrn))

        if peakflow:
            try:
                peakflow =int(peakflow)
            except:
                log.error('Parser %s: NonInt PeakFlow: %s for Patient %s' % (filename,peakflow,mrn))
            
        try:
            provid =provdict[phy]
        except:
            provid = 'NULL'

        espencid = searchId('select id from esp_enc where EncPatient_id=%s and EncEncounter_ID=%s', (demogid, encid))
        if espencid: #Update
            ##
            (edc, pregstatus) = getEDC(espencid,edc, pregstatus, encd)
            enc_str = """update esp_enc set
            EncEncounter_ID=%s,
            EncPatient_id=%s,
            EncMedical_Record_Number=%s,
            EncEncounter_Date=%s,
            EncEncounter_Status=%s,
            EncEncounter_ClosedDate=%s,
            EncEncounter_Site =%s,
            EncEncounter_SiteName=%s,
            EncEvent_Type=%s,
            EncTemperature=%s,
            EncCPT_codes=%s,
            EncICD9_Codes=%s,
            EncWeight=%s,
            EncHeight=%s,
            EncBPSys=%s,
            EncBPDias=%s,
            EncO2stat=%s,
            EncPeakFlow=%s,
            EncEncounter_Provider_id=%s,
            EncEDC=%s,
            EncPregnancy_Status=%s,
            lastUpDate=%s
            where id =%s
            """
            values = (encid,demogid,mrn,encd,close,closed,deptid,dept,enctp,temp,cpt,icd9,weight,height,bpsys,bpdias,o2stat,peakflow,provid,edc, pregstatus, DBTIMESTR,espencid)
            runSql(enc_str,values)
        else: #new
            enc_str = """insert into esp_enc
            (EncEncounter_ID,EncPatient_id,EncMedical_Record_Number,EncEncounter_Date,EncEncounter_Status,EncEncounter_ClosedDate,EncEncounter_Site,EncEncounter_SiteName,EncEvent_Type,EncTemperature,EncCPT_codes,EncICD9_Codes,EncWeight,EncHeight,EncBPSys,EncBPDias,EncO2stat,EncPeakFlow,EncEncounter_Provider_id,EncEDC,EncPregnancy_Status,lastUpDate,createdDate)
            values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)
            """
            values = (encid,demogid,mrn,encd,close,closed,deptid,dept,enctp,temp,cpt,icd9,weight,height,bpsys,bpdias,o2stat,peakflow,provid,edc, pregstatus,DBTIMESTR,DBTIMESTR)

            runSql(enc_str,values)
            espencid = cursor.lastrowid

        
        updateIcd9Fact(espencid, demogid, encd, icd9)

#        espencid = updateDB('esp_enc',enc_str,values, espencid)

    movefile(incomdir, filename,filelines)    

###################################
###################################
def updateIcd9Fact(espencid, demogid, encdate, icd9):
    clist = icd9.split()
    
    for onec in clist:
        icd9factid = searchId("""select id from esp_icd9fact where icd9Patient_Id=%s and icd9Enc_Id=%s and icd9Code=%s""", (demogid, espencid,onec))
        if icd9factid: ##already exists
            pass
        else: ##new one
            newrec = (onec,espencid,demogid,encdate, DBTIMESTR,DBTIMESTR)
            insertsql = """insert into esp.esp_icd9fact (icd9Code,icd9Enc_Id,icd9Patient_Id,icd9encDate, lastUpDate,createdDate)
                   values (%s,%s,%s,%s, %s, %s)""" 
            runSql(insertsql,newrec)



###################################
###################################
def updateDB(table,setclause,values, id):
    if not id: ##new record
        if USESQLITE==1:
            stmt ="""insert into %s set %s,  lastUpDate=datetime('now'), createdDate=datetime('now')""" % (table,setclause)
        else:
            stmt ="""insert into %s set %s,  lastUpDate=sysdate(), createdDate=sysdate()""" % (table,setclause)
        runSql(stmt,values)
        id = cursor.lastrowid
    else: #update
        if USESQLITE==1:
            stmt ="""update %s set %s,lastUpDate=datetime('now') """ % (table,setclause)
        else:
            stmt ="""update %s set %s,lastUpDate=sysdate() """ % (table,setclause)
        stmt = stmt + "where id =%s"
        runSql(stmt,values+(id,))

    if USESQLITE!=1:
        cursor.execute("commit;")
    
    return id


                                                        
def parseLxOrd(incomdir,filename,demogdict, provdict):
    #
    # This is bogus --  parseLxOrd populates esp_lx, not esp_lxo.  That cannot 
    # be right.
    #
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue
        try:
            pid,mrn,orderid,cpt,modi,accessnum,orderd, ordertp, phy = items
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
        try:
            if demogdict:
                demogid = demogdict[pid]
            else:
                demogid = searchId('select id from esp_demog where DemogPatient_Identifier=%s', (pid,))
                #demogid = searchId('esp_demog',"DemogPatient_Identifier='%s'" % pid) 
        except:
            log.warning('Parser In LXORD: NO patient found: %s\n' % str(items))
            continue
        #always create a new record, since no good way to identify unique tuple
        if not string.strip(orderid): orderid = today  ##since when passing HL7 msg, this is required
        #
        # Get loinc
        #
        ext_code = utils.ext_code_from_cpt(cpt, '')
        mapping = models.External_To_Loinc_Map.objects.get(ext_code=ext_code)
        loinc = mapping.loinc
        lxloinc = loinc.loinc_num
        try:
            if provdict:
                provid=provdict[phy]
            else:
                provid = searchId('select id from esp_provider where provCode=%s', (phy,))
                #provid= searchId('esp_provider',"provCode__exact='%s'" % phy)
        except:
            provid = 'NULL'
        lx, created = Lx.objects.get_or_create(LxPatient_id=demogid, 
            LxMedical_Record_Number=mrn, 
            LxOrder_Id_Num=orderid,
            LxHVMA_Internal_Accession_number=accessnum,
            LxTest_Code_CPT=cpt,
            LxOrderDate=orderd,
            LxOrderType=ordertp)
        lx.LxTest_Code_CPT_mod = modi
        lx.LxLoinc = lxloinc
        lx.LxOrdering_Provider_id = provid
        lx.lastUpdate = DBTIMESTR
        lx.loinc = loinc
        lx.save()
    movefile(incomdir, filename,filelines)
                                                                                                                                                                                                                                                                                                                                            
                
           
################################
def parseLxRes(incomdir,filename,demogdict, provdict):
    """
    """
    ##get all exclude code list
    exclude_l=[]
    rules = Rule.objects.all()
    for i in rules:
        if i.ruleExcludeCode:
            exclist=eval(i.ruleExcludeCode)
            exclude_l=exclude_l+exclist
    excdict = dict(map(lambda x:((x[0],x[1]), 1), exclude_l))

        
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        log.debug('line %s: %s' % (linenum, items))
        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue
        try:
            pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,comp,compname,res,normalf,refl,refh,refu,status,note,accessnum,impre  = items #[x.strip() for x in items]
        except:
            try:
                pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,note,access,impre  = items #[x.strip() for x in items]
                comp=compname=res=normalf=refl=refh=refu=status=''
            except:
                log.error('Parser %s: wrong size - %s' % (filename,str(items)))
                continue

        try:
            if demogdict:
                demogid = demogdict[pid]
            else:
                demogid = searchId('select id from esp_demog where DemogPatient_Identifier=%s', (pid,))
#                demogid = searchId('esp_demog',"DemogPatient_Identifier='%s'" % pid)
        except:
            log.warning('Parser In LXRES: NO patient found: %s\n' % str(items))
            continue
        log.debug('demogid: %s' % demogid)
        if not string.strip(orderid):
            orderid = today  ##since when passing HL7 msg, this is required
        if not string.strip(resd):
            resd =today
                                        

        if not refu:
            refu = 'N/A'          
            
        #get loinc
        c = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=comp)
        ext_code = utils.ext_code_from_cpt(cpt, '')
        m = models.External_To_Loinc_Map.objects.filter(ext_code=ext_code)
        lxloinc=''
        if m:
            lxloinc=(c[0].loinc.loinc_num).strip()
        elif compname:
            # 
            # NOTE: This is where we do NLP code search
            #
            if codeSearch(compname)  and not excdict.has_key(('%s' % cpt,'%s' % comp)) and (cpt,comp,compname.upper()) not in alertcode: ##log new CPT code which is not in esp_cptloincmap
                alertcode.append((cpt,comp,compname.upper()))

        ##if need to insert into labcomponent table
        if compname:
            newLabcompoent(compname, cpt, comp)

        try:
            if provdict:
                provid=provdict[phy]
            else:
                provid = searchId('select id from esp_provider where provCode=%s', (phy,))
                
                #provid= searchId('esp_provider',"provCode__exact='%s'" % phy)

        except:
            provid = 'NULL'
        log.debug('provid: %s' % provid)
        lxid = searchId('select id from esp_lx where LxPatient_id=%s and LxMedical_Record_Number=%s and LxOrder_Id_Num=%s and LxHVMA_Internal_Accession_number=%s and LxTest_Code_CPT=%s and LxComponent=%s and LxComponentName=%s and LxTest_results=%s and LxOrderDate=%s and LxOrderType=%s and LxDate_of_result=%s', (demogid,mrn,orderid,accessnum,cpt,comp,compname,res,orderd,ordertp,resd))
        if lxid: #update
            log.debug('updating record')
            lx_str = """update esp_lx set
             LxPatient_id=%s,
             LxOrder_Id_Num=%s,
             LxMedical_Record_Number =%s,
             LxTest_Code_CPT=%s,
             LxHVMA_Internal_Accession_number=%s,
             LxOrderDate=%s,
             LxOrderType=%s,
             LxDate_of_result=%s,
             LxComponent=%s,
             LxComponentName=%s,
             LxTest_results=%s,
             LxNormalAbnormal_Flag=%s,
             LxReference_Low=%s,
             LxReference_High=%s,
             LxReference_Unit=%s,
             LxTest_status=%s,
             LxComment=%s,
             LxImpression=%s,
             LxLoinc=%s,
             LxOrdering_Provider_id=%s,
             lastUpDate=%s
             where id =%s
             """
            values=(demogid,orderid,mrn,cpt,accessnum,orderd,ordertp,resd,comp,compname,res,normalf,refl,refh,refu,status,note,impre,lxloinc,provid, DBTIMESTR,lxid)
        else: #new
            log.debug('inserting record')
            lx_str = """insert into esp_lx
            (LxPatient_id,LxOrder_Id_Num,LxMedical_Record_Number,LxTest_Code_CPT,LxHVMA_Internal_Accession_number,LxOrderDate,LxOrderType,LxDate_of_result,LxComponent,LxComponentName,LxTest_results,LxNormalAbnormal_Flag,LxReference_Low,LxReference_High,LxReference_Unit,LxTest_status,LxComment,LxImpression,LxLoinc,LxOrdering_Provider_id,lastUpDate,createdDate)
            values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)
            """
            values=(demogid,orderid,mrn,cpt,accessnum,orderd,ordertp,resd,comp,compname,res,normalf,refl,refh,refu,status, note,impre,lxloinc,provid, DBTIMESTR,DBTIMESTR)
        
        runSql(lx_str,values)
        #lxid = updateDB('esp_lx',lx_str,values,lxid)

                 

    movefile(incomdir, filename,filelines)   


###################################
def newLabcompoent(compname, cpt, comp):
    labc = LabComponent.objects.filter(componentName__iexact=compname, CPT__iexact=cpt,CPTCompt__iexact=comp)
    if not labc: ##need insert
        labc = LabComponent(componentName=string.upper(compname))
        labc.CPT=cpt
        labc.CPTCompt = comp
        labc.save()

                                                                                    
###################################
def codeSearch(compname):
                    
    searchstr = ['CHLAM','TRACH', 'GC','GON','HEP','HBV','ALT','SGPT','AST','SGOT','AMINOTRANS','BILI', 'HAV','HCV','RIBA']
    notsearch = ['CAST', 'FASTING','YEAST','URINE','URO']
    for i in searchstr:
        if compname.upper().find(i)!=-1:
            for n in notsearch:
                if compname.upper().find(n)!=-1:
                    return 0
            return 1
    return 0
           
################################
def parseRx(incomdir,filename,demogdict,provdict):

    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue                                
        try:
            if len(items) == 13:
                pid,mrn,orderid,phy, orderd,status, med,ndc,meddesc,qua,ref,sdate,edate  = items #[x.strip() for x in items]
                route=''
            else:
                pid,mrn,orderid,phy, orderd,status, med,ndc,meddesc,qua,ref,sdate,edate,route  = items #[x.strip() for x in items]
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
                         
           
        try:
            demogid = demogdict[pid]
        except:
            log.warning('Parser In RX: NO patient found: %s\n' % str(items))
            continue

        if not string.strip(orderid): orderid = today  ##since when passing HL7 msg, this is required

        try:
            if provdict:
                provid=provdict[phy]
            else:
                provid = searchId('select id from esp_provider where provCode=%s', (phy,))
                
#                provid= searchId('esp_provider',"provCode__exact='%s'" % phy)
        except:
            provid = 'NULL'
                                                                    
        if not route: route='N/A'       

        rxid = searchId('select id from esp_rx where RxPatient_id=%s and RxOrder_Id_Num=%s', (demogid, orderid))
        if rxid: ##update
            rx_str=""" update esp_rx set
             RxPatient_id=%s,
             RxOrder_Id_Num=%s,
             RxMedical_Record_Number=%s,
             RxOrderDate=%s,
             RxStatus=%s,
             RxDrugDesc=%s,
             RxDrugName=%s,
             RxNational_Drug_Code=%s,
             RxQuantity=%s,
             RxRefills=%s,
             RxRoute=%s,
             RxDose = 'N/A',
             RxFrequency='N/A',
             RxStartDate=%s,
             RxEndDate=%s,
             RxProvider_id=%s,
             lastUpDate=%s
             where id =%s
             """
            values = (demogid, orderid,mrn,orderd,status,meddesc,med,ndc,qua,ref,route,sdate,edate,provid,DBTIMESTR,rxid)
        else: #new
            rx_str=""" insert into esp_rx
             (RxPatient_id,RxOrder_Id_Num,RxMedical_Record_Number,RxOrderDate,RxStatus,RxDrugDesc,RxDrugName,RxNational_Drug_Code,RxQuantity,RxRefills,RxRoute,RxDose,RxFrequency,RxStartDate,RxEndDate,RxProvider_id,lastUpDate,createdDate)
             values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)
            """
            values = (demogid, orderid,mrn,orderd,status,meddesc,med,ndc,qua,ref,route,'N/A','N/A',sdate,edate,provid,DBTIMESTR,DBTIMESTR)
        runSql(rx_str,values)

#        rxid = updateDB('esp_rx',rx_str,values,rxid)
    movefile(incomdir, filename,filelines)   


################################
def parseImm(incomdir, filename,demogdict):
    
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):

        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue
        try:
            pid, immtp, immname,immd,immdose,manf,lot,recid  = items #[x.strip() for x in items]
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
                                    
        try:
            demogid = demogdict[pid]
        except:
            log.warning('Parser In Imm: NO patient found: %s\n' % str(items))
            continue


        immid = searchId('select id from esp_immunization where ImmPatient_id=%s and ImmRecId=%s', (demogid, recid))
        if immid:  #update
            imm_str = """ update  esp_immunization set
            ImmPatient_id=%s,
            ImmRecId=%s,
            ImmType=%s,
            ImmName =%s,
            ImmDate =%s,
            ImmDose=%s,
            ImmManuf=%s,
            ImmLot=%s,
            lastUpDate=%s
            where id =%s
            """
            values = (demogid, recid,immtp,immname,immd,immdose,manf,lot,DBTIMESTR,immid)
        else: #new
            imm_str = """insert into esp_immunization
            (ImmPatient_id,ImmRecId,ImmType,ImmName,ImmDate,ImmDose,ImmManuf,ImmLot,lastUpDate,createdDate)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            values = (demogid, recid,immtp,immname,immd,immdose,manf,lot,DBTIMESTR,DBTIMESTR)

        runSql(imm_str,values)
#        try:
#            immid = searchId('select id from esp_immunization where ImmPatient_id=%s and ImmRecId=%s', (demogid, recid))
#            immid = updateDB('esp_immunization',imm_str,values,immid)
#        except:
#            log.error('Parser In IMM: error when save: %s\n' % (str(items)))

    movefile(incomdir, filename,filelines)   

###################################
def parseSoc(incomdir, filename,demogdict):

    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        
        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue
        try:
            pid, mrn,smoke,drink  = items #[x.strip() for x in items]
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue

        try:
            demogid = demogdict[pid]
        except:
            log.warning('Parser In SocialHistory: NO patient found: %s\n' % str(items))
            continue


        ##always new record
        soc_str = """insert into esp_socialhistory
                  (SocPatient_id, SocMRN, SocTobUse,SocAlcoUse,lastUpDate,createdDate)
                  values (%s,%s,%s,%s,%s,%s)
        """
        values = (demogid, mrn,smoke,drink,DBTIMESTR,DBTIMESTR)

        runSql(soc_str,values)
                
        
###################################
def parsePrb(incomdir, filename,demogdict):

    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        
        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue
        try:
            pid, mrn,probid, datenoted,icd9, status, note  = items #[x.strip() for x in items]
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
        
        try:
            demogid = demogdict[pid]
        except:
            log.warning('Parser In ProblemList: NO patient found: %s\n' % str(items))
            continue
        
        ##always new record
        prb_str = """insert into esp_problems
        (PrbPatient_id, PrbMRN, PrbID,PrbDateNoted,PrbICD9Code,PrbStatus,PrbNote,lastUpDate,createdDate)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values = (demogid, mrn,probid, datenoted,icd9, status, note,DBTIMESTR,DBTIMESTR)
        runSql(prb_str,values)
                                

###################################
def parseAll(incomdir, filename,demogdict):

    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        
        if not items or items[0]=='CONTROL TOTALS':
            filelines = linenum
            continue
        try:
            pid, mrn,probid, datenoted,allgid, allgname,status, desc,dateentered  = items #[x.strip() for x in items]
        except:
            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue

        try:
            demogid = demogdict[pid]
        except:
            log.warning('Parser In Allergies: NO patient found: %s\n' % str(items))
            continue

        ##always new record
        all_str = """insert into esp_allergies
        (AllPatient_id, AllMRN, AllPrbID,AllDateNoted,AllCode,AllName,AllStatus,AllDesc,AllDateEntered,lastUpDate,createdDate)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values = (demogid, mrn,probid, datenoted,allgid, allgname,status, desc,dateentered,DBTIMESTR,DBTIMESTR)
        runSql(all_str,values)

                                                                                                                                                    
                                                                                                                    
################################
def movefile(incomdir, f, linenum):
    """file name format shoUld be ***.esp.MMDDYY
    YYYYMMDD_prov.txt
    """
    ##save the filename in DB
    dataf = DataFile()
    dataf.filename=f
    dataf.numrecords = linenum-1
    dataf.save()
    
    ##move file to processed directory
    mmddyy =f[f.find('esp.')+4:]
    if len(mmddyy)==6:
        year = '20'+mmddyy[-2:]
    elif mmddyy.find('_')!= -1: #monthly or weekly update
        year = mmddyy[-6:-2]
    else:
        year = mmddyy[-4:]
        
    mon = mmddyy[:2]

    curdir = os.path.join(TOPDIR,LOCALSITE, 'processedData/%s/' % year)
    if not os.path.isdir(curdir):
        os.makedirs(curdir)

    subdir = os.path.join(curdir, 'MONTH_%s/' % mon)
    if not os.path.isdir(subdir):
        os.makedirs(subdir)
    if options.move:
	    log.info('Moving file %s from %s to %s\n' % (f, incomdir, subdir))
	    shutil.move(incomdir+'/%s' % f, subdir)


################################
def getfilesByDay(incomdir):
    files=os.listdir(incomdir)
    files.sort()
    dayfiles={}
    returndays=[]
    ##filename shoule be: epic***.esp.MMDDYY or epic***.esp.MMDDYYYY
    for f in files:
        if f.lower().find('test')!=-1 and FILEBASE!='test': ##test file
            log.info('Ignoring test file %s' % f)
            continue
            
        mmddyy =f[f.find('esp.')+4:]
        if len(mmddyy)==6: ##DDMMYY
            newdate='20'+mmddyy[-2:]+mmddyy[:4]
        elif mmddyy.find('_')!= -1: #monthly or weekly update, formart is epic***.esp.MMDDYYYY_m or epic***.esp.MMDDYYYY_w
            newdate=mmddyy[-6:-2]+mmddyy[:4]
        else:
            newdate=mmddyy[-4:]+mmddyy[:4]

            
        if (newdate,mmddyy) not in returndays:
            returndays.append((newdate,mmddyy))

    returndays.sort(key=lambda x:x[0])
    return returndays


################################
def validateOnefile(incomdir, fname,delimiternum,needidcolumn,datecolumn=[],required=[],returnids=[],checkids=[]):
    
    returnd={}
    errors=0
    fname = os.path.join(incomdir,'%s' % fname)

    hascontrolline=0
    for (l, linenum) in splitfile(fname,'^',True):
        l = l.strip()

        if l.find('CONTROL TOTALS')>-1:
            hascontrolline=1
                            
        if not l or l.find('CONTROL TOTALS')>-1:
            continue
        
        fnum=len(re.findall("\^",l))

        #check delimit number
        if int(delimiternum) != fnum:
            msg ='Validator - %s: wrong number of delimiter, should be %s, in file=%s\n=========LINE%s: %s\n' % (fname,delimiternum,fnum,linenum,l)
            errors = 1
            log.error(msg)

            
        items = l.split('^')
        if items == ['']* (int(delimiternum)+1):
            continue
        
        #check required fileds
        for r in required:
            if len(items)>= r+1 and not string.strip(items[r]):
                col = r+1
                msg = 'Validator - %s, LINE%s: Empty for Required filed in column %s\n' % (fname,linenum, col )
                errors = 1
                log.error(msg)
                
                
        ##check patientID
        curpatientId = items[needidcolumn[0]].strip()
        if checkids and needidcolumn and not checkids[0].has_key(curpatientId): #checkids[0]={PatiendID:None, PatientID:None...}
            msg = """Validator - %s: LINE%s-Patient =%s= not in mem file\n""" % (fname, linenum, items[needidcolumn[0]])
            log.error(msg)
            errors=1
            

        ##check providerID 
        if checkids and len(needidcolumn)==2:
            try: # bail if line is too short
                curproviderId = items[needidcolumn[1]].strip()
                if not checkids[1].has_key(curproviderId): #checkids[1]={ProviderID:None, ProviderID:None...}
                   msg = """Validator - %s: LINE%s-Provider =%s= not in provider file\n""" % (fname, linenum, items[needidcolumn[1]])
                   log.error(msg)
                   if items[needidcolumn[1]]: ###ignore missing provider
                       errors=1
            except:
                   msg = """Validator - %s: LINE%s- not enough fields to check Provider\n""" % (fname, linenum)
                   log.error(msg)
                   errors=1

        #build return dictionary for patientID and providerID
        for n in returnids:
            returnd[items[n].strip()]=None

        #check date
        try: # if line is b0rked, need to bail
          for d in datecolumn:               
            if items[d] and len(items[d])!=8 or re.search('\D', items[d]):
                msg = 'Validator - %s: wrong Date format: %s\n=========LINE%s: %s\n'  % (fname,items[d],linenum, l)
                errors = 1
                log.error(msg)
        except:
                msg = 'Validator - %s: Insufficient fields to check date formats:\n=========LINE%s: %s\n'  % (fname,linenum, l)            
                errors = 1
                log.error(msg)


    if not hascontrolline:
        msg = 'Validator - %s: There is no control line\n'
        errors = 1
        log.error(msg)
                                        

    return  (errors,returnd)                                                                                                                                                                                                                                                                                                                                                      


################################
def validateOneday(incomdir, oneday):
    """validate one day files
    """
    for i in utils.filenlist:
        fname = i+oneday
        fname = os.path.join(incomdir,'%s' % fname)
        if not os.path.exists(fname):
            log.error('Validator - Non-exsiting file:%s\n' % (fname))
            return 1
                                                

    finalerr=0
    pids={}
    #patient
    if hasMem:
        demogf = FILEBASE+'mem.esp.'+oneday
        log.info('Validator - Process %s' % demogf)
        (err,tempd) = validateOnefile(incomdir,demogf,24,[0],datecolumn=[14],required=[0,1],returnids=[0])
        pids = tempd
        if err:
            finalerr = 1
        
    #provider
    if hasProv:
        providerf = FILEBASE+'pro.esp.'+oneday
        log.info('Validator -Process %s' % providerf)
        err,tempd = validateOnefile(incomdir,providerf,13,[0],required=[0],returnids=[0] )
        provids= tempd
        if err:
            finalerr = 1

                            

        
    #encounter
    if hasEnc:
        visf = FILEBASE+'vis.esp.'+oneday
        log.info('Validator -Process %s' % visf)
        err,tempd = validateOnefile(incomdir,visf,19,[0,6], datecolumn=[3,5,10],required=[0,1],checkids=[pids,provids])
        if err:
            finalerr = 1
        
    #lxord
    if hasOrd:
        lxordf = FILEBASE+'ord.esp.'+oneday
        log.info('Validator - Process %s' % lxordf)
        err, tempd = validateOnefile(incomdir,lxordf,8,[0,8],datecolumn=[6],required=[0,1],checkids=[pids,provids])
        if err:
            finalerr = 1

    #lxres
    if hasRes:
        lxresf = FILEBASE+'res.esp.'+oneday
        log.info('Validator - Process %s' % lxresf)
        err, tempd = validateOnefile(incomdir,lxresf,18,[0,5],datecolumn=[3,4],required=[0,1],checkids=[pids,provids])
        if err :
            finalerr = 1

    #med
    if hasMed:
        medf = FILEBASE+'med.esp.'+oneday
        log.info('Validator - Process %s' % medf)
        err,tempd = validateOnefile(incomdir,medf,13,[0,3],datecolumn=[4,11,12],required=[0,1],checkids=[pids,provids])
        if err:
            finalerr = 1

    #imm
    if hasImm:
        mmf = FILEBASE+'imm.esp.'+oneday
        log.info('Validator - Process %s' % mmf)
        err,tempd = validateOnefile(incomdir,mmf,7,[0],datecolumn=[3],checkids=[pids,provids])
        if err :
            finalerr = 1

    #prb
    if hasPrb:
        prbf = FILEBASE+'prb.esp.'+oneday
        log.info('Validator - Process %s' % prbf)
        err,tempd = validateOnefile(incomdir,prbf,6,[0],datecolumn=[3],required=[0,1],checkids=[pids])
        if err :
            finalerr = 1
    #soc
    if hasSoc:
        socf = FILEBASE+'soc.esp.'+oneday
        log.info('Validator - Process %s' % socf)
        err,tempd = validateOnefile(incomdir,socf,3,[0],datecolumn=[],required=[0,1],checkids=[pids])
        if err :
            finalerr = 1

    ##Allergics
    if hasAll:
        allf = FILEBASE+'all.esp.'+oneday
        log.info('Validator - Process %s' % allf)
        err,tempd = validateOnefile(incomdir,allf,8,[0],datecolumn=[3],required=[0,1],checkids=[pids])
        if err :
            finalerr = 1
                                
                                                
    return finalerr
                                                                                      
    
################################
def doValidation(incomdir,days):

    parsedays = []
    errordays=[]
    for oneday in days:
        err = validateOneday(incomdir,oneday)

        if err:
            errordays.append(oneday)
                
        if REJECT_INVALID and err: #not OK
            log.error("Validator - Files for day %s not OK, rejected - not  processed\n" % oneday)
        elif err and not REJECT_INVALID:
            log.info("Validator - Files for day %s NOT OK, but still process\n" % oneday)
            parsedays.append(oneday)
        else: #OK
            log.info("Validator - Files for day %s OK\n" % oneday)
            parsedays.append(oneday)

    if errordays:
        msg = 'Found validation errors when running incomingParse.py; Error days are:%s; Please go to log file for detail;' % (str(errordays))
#        print msg
        if options.mail:
            utils.sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg=msg)
        
    return parsedays




###################################
###################################
def updateLoinc_lx():
    log.info('Start to update cptloinc map in esp_cptloincmap table and esp_lx table')
    from ESP.utils.preLoader import load2cptloincmap, addNewcptloincmap, correctcptloincmap_lx
    from ESP.utils.preLoader import getlines as preloadgetlines

    preloadf = os.path.join(TOPDIR,LOCALSITE, 'preLoaderData','esp_cptloincmap.txt')
    filetime= time.localtime(os.path.getmtime(preloadf))
    file_lastmodtime = datetime.datetime(filetime[0],filetime[1],filetime[2])
    cursor.execute("""select max(lastupdate) from esp_demog""")
    dbtime = cursor.fetchall()[0][0]
    print '##got dbtime=%s, type=%s' % (dbtime,type(dbtime))
    if type(dbtime) == type(unicode('x')): # sqlite returns a unicode str
           dbd = str(dbtime).split(' ')[0].split('-') # sqlite returns '2008-08-03 06:13:22'
           dbtime = datetime.datetime(int(dbd[0]),int(dbd[1]),int(dbd[2]))
    if dbtime and dbtime<file_lastmodtime:
        log.info('Need do updating cptloinc map in esp_cptloincmap & esp_lx tables')
        table='esp_cptloincmap'
        load2cptloincmap(table, preloadgetlines(preloadf), cursor)
        addNewcptloincmap(cursor)
        correctcptloincmap_lx(table,cursor)
        log.info('Done on updating esp_lx table')
    else:
        log.info('No need updating cptloinc map in esp_cptloincmap & esp_lx tables')
            
            
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#--- ~~~ Main Logic ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    parser = optparse.OptionParser()
    parser.add_option('-n', '--no-move', action='store_false', dest='move', default=True,
        help='Do not move files after processing')
    parser.add_option('--mail', action='store_true', dest='mail', default=False,
        help='Send notifications by email')
    parser.add_option('-a', '--all', action='store_true', dest='all', default=False)
    parser.add_option('--prov', action='store_true', dest='prov', default=False)
    parser.add_option('--res', action='store_true', dest='res', default=False)
    parser.add_option('--ord', action='store_true', dest='ord', default=False)
    parser.add_option('--med', action='store_true', dest='med', default=False)
    parser.add_option('--enc', action='store_true', dest='enc', default=False)
    parser.add_option('--imm', action='store_true', dest='imm', default=False)
    parser.add_option('--soc', action='store_true', dest='soc', default=False)
    parser.add_option('--prb', action='store_true', dest='prb', default=False)
    global options # So we don't need to explicitly pass to every function
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    try: 
        
        startt = datetime.datetime.now()
        ###try to update esp_lx
        updateLoinc_lx()
        ##get incoming files and do validations
        incomdir = os.path.join(TOPDIR, LOCALSITE,'incomingData/')
        allf = os.listdir(incomdir)
        days= utils.getfilesByDay(allf)  #days are sorted list
        log.info('Days are: %s; \n' % str(days))
        
        if DO_VALIDATE:
            parsedays = doValidation(incomdir,map(lambda x:x[1],days))
	else:
            parsedays = copy.copy(map(lambda x:x[1],days))
        log.info('Validating is done. Parsed days are %s\n' % str(parsedays))

        ##start to parse by days
        ##always load files no matter it passed validator or not
        for oneday in parsedays:
            log.info("Parser - parse day %s\n" % oneday)
            provf = FILEBASE+'pro.esp.'+oneday
            provdict = parseProvider(incomdir, provf)
            demogf =  FILEBASE+'mem.esp.'+oneday 
            demogdict = parseDemog(incomdir, demogf)
            if options.enc or options.all:
                visf =  FILEBASE+'vis.esp.'+oneday      
                parseEnc(incomdir , visf,demogdict,provdict)
            if options.med or options.all:
                medf = FILEBASE+'med.esp.'+oneday
                parseRx(incomdir , medf,demogdict,provdict)
            if options.ord or options.all:
                lxordf = FILEBASE+'ord.esp.'+oneday
                parseLxOrd(incomdir,lxordf, demogdict,provdict)
            if options.res or options.all:
                lxresf = FILEBASE+'res.esp.'+oneday
                parseLxRes(incomdir,lxresf, demogdict,provdict)
            if options.imm or options.all:
                immf = FILEBASE+'imm.esp.'+oneday  
                parseImm(incomdir , immf, demogdict)
            if options.prb or options.all:
                prbf = FILEBASE+'prb.esp.'+ oneday
                parsePrb(incomdir , prbf, demogdict)
            if options.soc or options.all:
                socf = FILEBASE+'soc.esp.'+ oneday
                if os.path.exists(socf):
                    parseSoc(incomdir , socf, demogdict)
                else:
                    log.info('No soc file; skipping.')

#            if hasAll:
#                socf = FILEBASE+'all.esp.'+ oneday
#                parseAll(incomdir , socf, demogdict)
                                                
        ##send email
        log.warning('New CPT/COMPT code: %s\n' % str(alertcode))
        if alertcode and options.mail:
            utils.sendoutemail(towho=['MKLOMPAS@PARTNERS.ORG','Julie_Dunn@harvardpilgrim.org', 'rexua@channing.harvard.edu','rerla@channing.harvard.edu'],msg='New (CPT,COMPT,ComponentName): %s' % str(alertcode))
        
        log.info('Start: %s\n' %  startt)
        log.info('End:   %s\n' % datetime.datetime.now())
        
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        log.info(message+'\n')

            
if __name__ == "__main__":
    main()


