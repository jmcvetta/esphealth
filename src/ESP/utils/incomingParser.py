'''
                                  ESP Health
                                Incoming Parser

Uses a generator to load large delimited ETL files, as produced by Epic Care, 
into database.

@author: Ross Lazarus <ross.lazarus@channing.harvard.edu>
@author: Xuanlin Hou <rexua@channing.harvard.edu>
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

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
import optparse
import pprint

import django, datetime, time
from django.db.models import Q, Max
from django.db import connection

from ESP.localsettings import LOCALSITE
from ESP.settings import TOPDIR
from ESP.esp.models import Enc, Lx, Lxo, Demog, Provider, Rx, Immunization
from ESP.esp.models import SocialHistory, Problem, Icd9Fact
from ESP.esp.models import LabComponent, DataFile
from ESP.conf.models import NativeToLoincMap, Rule
from ESP.utils import utils
from ESP.utils import update_loincs
from ESP.utils.utils import log


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
    '''
    Generator to return delimiter split lines
    '''
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


def parseProvider(incomdir, filename):
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
        prov, created = Provider.objects.get_or_create(provCode=phy)
        prov.provLast_Name = lname
        prov.provFirst_Name = fname
        prov.provMiddle_Initial = mname
        prov.provTitle = title
        prov.provPrimary_Dept_Id = depid
        prov.provPrimary_Dept = depname
        prov.provPrimary_Dept_Address_1=addr1
        prov.provPrimary_Dept_Address_2=addr2
        prov.provPrimary_Dept_City=city
        prov.provPrimary_Dept_State=state
        prov.provPrimary_Dept_Zip=zip
        prov.provTelAreacode=phonearea
        prov.provTel=phone
        prov.lastUpDate=DBTIMESTR
        prov.save()
        provdict[phy]=prov.pk
    movefile(incomdir, filename,filelines)
    return provdict


def parseDemog(incomdir, filename):
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
        #fake some
        if not fname:
            fname = 'Unknown'
        if not lname:
            lname = 'Unknown'
        #if not phonearea: #fake one
        #    phonearea='999'
        if phone:
            phone = re.sub('\D', '', phone)
        if not cty:
            cty='Unknown'                
        try:
            providerid = Provider.objects.get(provCode=phy).pk
        except Provider.DoesNotExist:
            providerid = None
        dem, created = Demog.objects.get_or_create(DemogPatient_Identifier=pid)
        dem.DemogMedical_Record_Number=mrn
        dem.DemogLast_Name=lname
        dem.DemogFirst_Name=fname
        dem.DemogMiddle_Initial=mname
        dem.DemogAddress1=addr1
        dem.DemogAddress2=addr2
        dem.DemogCity=city
        dem.DemogState=state
        dem.DemogZip=zip
        dem.DemogCountry=cty
        dem.DemogAreaCode=phonearea
        dem.DemogTel=phone
        dem.DemogExt=ext
        dem.DemogDate_of_Birth=dob
        dem.DemogGender=gender
        dem.DemogRace=race
        dem.DemogHome_Language=lang
        dem.DemogSSN=ssn
        dem.DemogMaritalStat=mari
        dem.DemogReligion=religion
        dem.DemogAliases=alias
        dem.DemogMotherMRN=mom
        dem.DemogDeath_Date=death
        dem.DemogProvider_id=providerid
        dem.lastUpDate=DBTIMESTR
        dem.save()
        demogdict[pid] = dem.pk
        

    movefile(incomdir, filename,filelines)
    return demogdict

                    
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

        
def parseEnc(incomdir, filename,demogdict,provdict):
    '''
    Load Encounter data
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
            provid = None
        patient, created = Demog.objects.get_or_create(DemogPatient_Identifier=demogid)
        e, created = Enc.objects.get_or_create(EncPatient=patient, EncEncounter_ID=encid)
        e.EncMedical_Record_Number=mrn
        e.EncEncounter_Date=encd
        e.EncEncounter_Status=close
        e.EncEncounter_ClosedDate=closed
        e.EncEncounter_Site=deptid
        e.EncEncounter_SiteName=dept
        e.EncEvent_Type=enctp
        e.EncTemperature=temp
        e.EncCPT_codes=cpt
        e.EncICD9_Codes=icd9
        e.EncWeight=weight
        e.EncHeight=height
        e.EncBPSys=bpsys
        e.EncBPDias=bpdias
        e.EncO2stat=o2stat
        e.EncPeakFlow=peakflow
        e.EncEncounter_Provider_id=provid
        e.EncEDC=edc
        e.EncPregnancy_Status=pregstatus
        e.lastUpDate=DBTIMESTR
        e.save()
        clist = icd9.split()
        for onec in clist:
            i, created = Icd9Fact.objects.get_or_create(icd9Patient=patient,
                icd9Enc=e,
                icd9Code=onec)
            if not created:
                pass # Already exists
            else: ##new one
                i.icd9encDate = encd
                i.lastUpDate = DBTIMESTR
                i.created = DBTIMESTR
                i.save()
    movefile(incomdir, filename,filelines)    


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
        if demogdict:
            demogid = demogdict[pid]
        else:
            try:
                demogid = Demog.objects.get(DemogPatient_Identifier=pid).pk
            except:
                log.warning('Parser In LXORD: NO patient found: %s\n' % str(items))
                continue
        #always create a new record, since no good way to identify unique tuple
        if not string.strip(orderid): orderid = today  ##since when passing HL7 msg, this is required
        #
        # Get loinc
        #
        native_code = utils.native_code_from_cpt(cpt, '')
        try:
            mapping = NativeToLoincMap.objects.get(native_code=native_code)
            loinc = mapping.loinc
            lxloinc = loinc.loinc_num
        except NativeToLoincMap.DoesNotExist:
            loinc = None
            lxloinc = None
        if provdict:
            provid=provdict[phy]
        else:
            try:
                provid = Provider.objects.get(provCode=phy).pk
            except Provider.DoesNotExist:
                provid = None
        patient = Demog.objects.get(pk=demogid)
        lx, created = Lx.objects.get_or_create(
            LxPatient = patient, 
            LxMedical_Record_Number = mrn, 
            LxOrder_Id_Num=orderid,
            LxHVMA_Internal_Accession_number = accessnum,
            LxTest_Code_CPT = cpt,
            LxOrderDate = orderd,
            LxOrderType = ordertp
            )
        lx.LxTest_Code_CPT_mod = modi
        lx.LxLoinc = lxloinc
        lx.LxOrdering_Provider_id = provid
        lx.lastUpdate = DBTIMESTR
        lx.loinc = loinc
        lx.native_code = native_code
        lx.save()
    movefile(incomdir, filename,filelines)
                                                                                                                                                                                                                                                                                                                                            
                
           
################################
def parseLxRes(incomdir,filename,demogdict, provdict):
    """
    """
    #log.debug('Parsing file %s' % filename)
    log.info('Parsing file %s' % filename)
    log.info('=' * 100)
    log.info('Parsing Lx!')
    log.info('=' * 100)
    ##get all exclude code list
    exclude_l=[]
    rules = Rule.objects.all()
    # 
    # NLP: Codes to exclude
    #
    for i in rules:
        if i.ruleExcludeCode:
            exclist=eval(i.ruleExcludeCode)
            exclude_l=exclude_l+exclist
    #
    # TODO: Include codes from mapping table in ignore list!
    #
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
        if demogdict:
            demogid = demogdict[pid]
        else:
            try:
                demogid = Demog.objects.get(DemogPatient_Identifier=pid).pk
            except:
                log.warning('Parser In LXRES: NO patient found: %s\n' % str(items))
                continue
        log.debug('demogid: %s' % demogid)
        if not string.strip(orderid):
            orderid = today  ##since when passing HL7 msg, this is required
        if not string.strip(resd):
            resd = today
        if not refu:
            refu = None
        #get loinc
        #c = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=comp)
        native_code = utils.native_code_from_cpt(cpt, None)
        m = NativeToLoincMap.objects.filter(native_code=native_code)
        lxloinc = None
        if m:
            lxloinc=(m[0].loinc.loinc_num).strip()
        elif compname:
            # 
            # NOTE: This is where we do NLP code search.  It should really be 
            # done in a separate tool.
            #
            if codeSearch(compname)  and not excdict.has_key(('%s' % cpt,'%s' % comp)) and (cpt,comp,compname.upper()) not in alertcode: ##log new CPT code which is not in esp_cptloincmap
                alertcode.append((cpt,comp,compname.upper()))

        ##if need to insert into labcomponent table
        if compname:
            newLabcompoent(compname, cpt, comp)
        if provdict:
            provid=provdict[phy]
        else:
            try:
                provid = Provider.objects.get(provCode=phy).pk
            except Provider.DoesNotExist:
                provid = None
        log.debug('provid: %s' % provid)
        Lx(LxPatient_id=demogid,
            LxMedical_Record_Number=mrn, 
            LxOrder_Id_Num=orderid,
            LxHVMA_Internal_Accession_number=accessnum,
            LxTest_Code_CPT=cpt,
            LxComponent=comp,
            LxComponentName=compname,
            LxTest_results=res,
            LxOrderDate=orderd,
            LxOrderType=ordertp,
            LxDate_of_result=resd,
            LxNormalAbnormal_Flag=normalf,
            LxReference_Low=refl,
            LxReference_High=refh,
            LxReference_Unit=refu,
            LxTest_status=status,
            LxComment=note,
            LxImpression=impre,
            loinc=lxloinc,
            LxOrdering_Provider_id=provid,
            lastUpDate=DBTIMESTR,
            native_code = native_code,
            native_name = compname,
            ).save()
    movefile(incomdir, filename,filelines)   


def newLabcompoent(compname, cpt, comp):
    labc = LabComponent.objects.filter(componentName__iexact=compname, CPT__iexact=cpt,CPTCompt__iexact=comp)
    if not labc: ##need insert
        labc = LabComponent(componentName=string.upper(compname))
        labc.CPT=cpt
        labc.CPTCompt = comp
        labc.save()

                                                                                    
def codeSearch(compname):
    '''
    Primitive natural language processing (NLP) to detect new lab 
    test with interesting names.
    '''
    # The search string list should probably be moved to settings.
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
    '''
    Load Prescription data
    '''
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
        if not string.strip(orderid): 
            orderid = today  ##since when passing HL7 msg, this is required
        if provdict:
            provid=provdict[phy]
        else:
            try:
                provid = Provider.objects.get(provCode=phy).pk
            except Provider.DoesNotExist:
                provid = None
        if not route: route='N/A'       
        patient, created = Demog.objects.get_or_create(DemogPatient_Identifier=demogid)
        r, created = Rx.objects.get_or_create(RxPatient=patient, RxOrder_Id_Num=orderid)
        r.RxMedical_Record_Number=mrn
        r.RxOrderDate=orderd
        r.RxStatus=status
        r.RxDrugDesc=meddesc
        r.RxDrugName=med
        r.RxNational_Drug_Code=ndc
        r.RxQuantity=qua
        r.RxRefills=ref
        r.RxRoute=route
        r.RxDose = 'N/A' # Why?
        r.RxFrequency='N/A' # Why?
        r.RxStartDate=sdate
        r.RxEndDate=edate
        r.RxProvider_id=provid
        r.lastUpDate=DBTIMESTR
        r.save()
    movefile(incomdir, filename,filelines)   


################################
def parseImm(incomdir, filename,demogdict):
    '''
    Load Immunization data
    '''
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
            patient = Demog.objects.get(pk=demogid)
        except:
            log.warning('Parser In Imm: NO patient found: %s\n' % str(items))
            continue
        i, created = Immunization.objects.get_or_create(ImmPatient=patient, ImmRecId=recid)
        i.ImmType = immtp
        i.ImmName = immname
        i.ImmDate = immd
        i.ImmDose = immdose
        i.ImmManuf = manf
        i.ImmLot = lot
        i.lastUpDate = DBTIMESTR
        i.save()
    movefile(incomdir, filename,filelines)   


def parseSoc(incomdir, filename,demogdict):
    '''
    Load SocialHistory data
    '''
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
        # Always create a new record
        SocialHistory(SocPatient_id=demogid,
            SocMRN=mrn,
            SocTobUse=smoke,
            SocAlcoUse=drink,
            lastUpDate=DBTIMESTR,
            createdDate=DBTIMESTR
            ).save()
                
        
def parsePrb(incomdir, filename,demogdict):
    '''
    Parse 'Problem' data
    '''
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
        # Always create a new record
        Problem(PrbPatient_id=demogid,
            PrbMRN=mrn,
            PrbID=probid,
            PrbDateNoted=datenoted,
            PrbICD9Code=icd9,
            PrbStatus=status,
            PrbNote=note,
            lastUpDate=DBTIMESTR,
            createdDate=DBTIMESTR
            ).save()
                                
################################################################################
#
# Is this deprecated?  I don't see us using it anywhere
#
################################################################################
#
#def parseAll(incomdir, filename,demogdict):
#    fname = os.path.join(incomdir,'%s' % filename)
#    for (items, linenum) in splitfile(fname,'^'):
#        
#        if not items or items[0]=='CONTROL TOTALS':
#            filelines = linenum
#            continue
#        try:
#            pid, mrn,probid, datenoted,allgid, allgname,status, desc,dateentered  = items #[x.strip() for x in items]
#        except:
#            log.error('Parser %s: wrong size - %s' % (filename,str(items)))
#            continue
#        try:
#            demogid = demogdict[pid]
#        except:
#            log.warning('Parser In Allergies: NO patient found: %s\n' % str(items))
#            continue
#        # Always create a new record
#        all_str = """insert into esp_allergies
#        (AllPatient_id, AllMRN, AllPrbID,AllDateNoted,AllCode,AllName,AllStatus,AllDesc,AllDateEntered,lastUpDate,createdDate)
#        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#        """
#        values = (demogid, mrn,probid, datenoted,allgid, allgname,status, desc,dateentered,DBTIMESTR,DBTIMESTR)
#        runSql(all_str,values)

                                                                                                                                                    
                                                                                                                    
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




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#--- ~~~ Main Logic ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main(opts=None):
    '''
    @param options: Used for calling this function from another python script.  
        If specified, optparse will not be run.
    @type opts: optparse.Values or interface-compatible
    '''
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
    parser.add_option('--input-folder', action='store', dest='input', type='string', metavar='FOLDER')
    global options # So we don't need to explicitly pass to every function
    if opts:
        options = opts
    else:
        (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    try: 
        
        startt = datetime.datetime.now()
        #
        # We are not going to automatically update LOINC codes -- this is an 
        # intensive operation, and need not be performed unless the external 
        # to LOINC map table has been updated.
        #
        #update_loincs.main()
        ##get incoming files and do validations
        if options.input:
            assert os.path.isdir(options.input) # Sanity check -- did user specify a real folder?
            incomdir = options.input
        else:
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
            if options.all or options.enc:
                visf =  FILEBASE+'vis.esp.'+oneday      
                parseEnc(incomdir , visf,demogdict,provdict)
            if options.all or options.med:
                medf = FILEBASE+'med.esp.'+oneday
                parseRx(incomdir , medf,demogdict,provdict)
            if options.all or options.ord:
                lxordf = FILEBASE+'ord.esp.'+oneday
                parseLxOrd(incomdir,lxordf, demogdict,provdict)
            if options.all or options.res:
                lxresf = FILEBASE+'res.esp.'+oneday
                parseLxRes(incomdir,lxresf, demogdict,provdict)
            if options.all or options.imm:
                immf = FILEBASE+'imm.esp.'+oneday  
                parseImm(incomdir , immf, demogdict)
            if options.all or options.prb:
                prbf = FILEBASE+'prb.esp.'+ oneday
                parsePrb(incomdir , prbf, demogdict)
            if options.all or options.soc:
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
