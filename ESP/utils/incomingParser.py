import os,sys
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR
import localconfig 

import string
import shutil
import StringIO
import traceback

today=datetime.datetime.now().strftime('%Y%m%d')

########For logging
logging = localconfig.getLogging('incomingParser.py v0.1', debug=0)


###############################
def getlines(fname):
    try:
        lines = file(fname).readlines()
    except:
        logging.error('Can not read file:%s\n' % fname)
        return []
    returnl = [x.split('^') for x in lines[:-1] if len(x.split('^')) > 1]
    logging.info('Parser Process %s: %s records\n' % (fname, len(returnl)))
    return returnl


################################
def parseProvider(incomdir, filename):
    l = getlines(incomdir+'/%s' % filename)
    for items in l:
        try:
            phy,lname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone = items
        except:
            logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
        prov=Provider.objects.filter(provCode__exact=phy)
        if prov: #update
            prov=prov[0]
        else: #new record
            prov=Provider(provCode = phy) 
            
        prov.provLast_Name=lname
        prov.provFirst_Name=fname
        prov.provMiddle_Initial =mname
        prov.provTitle=title
        prov.provPrimary_Dept_Id =depid
        prov.provPrimary_Dept=depname
        prov.provPrimary_Dept_Address_1=addr1
        prov.provPrimary_Dept_Address_2=addr2
        prov.provPrimary_Dept_City=city
        prov.provPrimary_Dept_State=state
        prov.provPrimary_Dept_Zip=zip
        prov.provTelAreacode=phonearea
        prov.provTel=phone
        prov.save()
    if l:
        movefile(incomdir, filename)
        
################################
def parseDemog(incomdir, filename):
    l = getlines(incomdir+'/%s' % filename)
    n=1
    for items in l:
        if n % 1000 == 0:
            logging.info('%s records done' % n)
        n += 1
                                
        try:
            pid,mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,phy,mari,religion,alias,mom,death=items
        except:
            logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
        pdb = Demog.objects.filter(DemogPatient_Identifier__exact=pid)
        if not pdb: #new record
            demog = Demog(DemogPatient_Identifier=pid)
        else: #update record
            demog = pdb[0]
        if phone:
            phone = string.replace(phone, '-','')
        if not cty:
            cty='USA'
            
        demog.DemogMedical_Record_Number=mrn
        demog.DemogLast_Name=lname
        demog.DemogFirst_Name=fname
        demog.DemogMiddle_Initial=mname
        demog.DemogAddress1=addr1
        demog.DemogAddress2=addr2
        demog.DemogCity=city
        demog.DemogState=state
        demog.DemogZip=zip
        demog.DemogCountry=cty
        demog.DemogAreaCode=phonearea
        demog.DemogTel=phone
        demog.DemogExt=ext
        demog.DemogDate_of_Birth=dob
        demog.DemogGender=gender
        demog.DemogRace=race
        demog.DemogHome_Language =lang
        demog.DemogSSN=ssn
        demog.DemogMaritalStat=mari
        demog.DemogReligion =religion
        demog.DemogAliases=alias
        demog.DemogMotherMRN=mom
        demog.DemogDeath_Date=death

        prov=Provider.objects.filter(provCode__exact=phy)        
        if prov:
            demog.DemogProvider=prov[0]
        demog.save()

    if l:
        movefile(incomdir, filename)
        
################################
def parseEnc(incomdir, filename):
    l = getlines(incomdir+'/%s' % filename)
    n=1
    for items in l:
        if n % 1000 == 0:
            logging.info('%s Enc records done' % n)
        n += 1
                              
        try:
            pid,mrn,encid,encd,close,closed,phy,deptid,dept,enctp,edc,temp,cpt,icd9=items
        except:
            logging.error('Parser %s: wrong size - %s' % (filename,str(items)))

        patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]           
        if not patient:
            logging.warning('Parser In ENC: NO patient found: %s\n' % str(items))
            continue
            
        encdb = Enc.objects.filter(EncPatient__DemogPatient_Identifier__exact=pid,EncEncounter_ID__exact=encid)
        if not encdb: #new record
            enc = Enc(EncPatient=patient,EncEncounter_ID=encid)
        else: #update record
            enc = encdb[0]    
           
        enc.EncMedical_Record_Number=mrn
        enc.EncEncounter_Date=encd  
        enc.EncEncounter_Status=close
        enc.EncEncounter_ClosedDate=closed
        enc.EncEncounter_Site =deptid
        enc.EncEncounter_SiteName=dept
        enc.EncEvent_Type=enctp           
        enc.EncEDC=edc
        if edc:
            enc.EncPregnancy_Status='Y'
        enc.EncTemperature=temp
        enc.EncCPT_codes=cpt
        enc.EncICD9_Codes=icd9
           
        prov=Provider.objects.filter(provCode__exact=phy)
        if prov:
            enc.EncEncounter_Provider=prov[0]

        enc.save()
    if l:
        movefile(incomdir, filename)    
        

################################
def parseLxOrd(incomdir, filename):
    l = getlines(incomdir+'/%s' % filename)
    for items in l:
        try:
            pid,mrn,orderid,cpt,modi,accessnum,orderd,ordertp,phy = items
        except:
            logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
                   
        if not string.strip(orderid):
             orderid = today ##since when passing HL7 msg, this is required
        try:            
             patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
             logging.warning('Parser In LXORD: NO patient found: %s\n' % str(items))
             continue
        if not orderid: orderid = today 

        lxdb =Lx.objects.filter(LxOrder_Id_Num__exact=orderid,LxPatient__DemogPatient_Identifier__exact=pid)

        if not lxdb: #new record
           lx = Lx(LxPatient=patient,LxOrder_Id_Num=orderid)
        else: #update record
           lx = lxdb[0]
                   
        lx.LxMedical_Record_Number =mrn
        lx.LxTest_Code_CPT=cpt
        lx.LxTest_Code_CPT_mod =modi
        lx.LxHVMA_Internal_Accession_number=accessnum
        lx.LxOrderDate=orderd
        lx.LxOrderType=ordertp
        prov=Provider.objects.filter(provCode__exact=phy)
        if prov:
            lx.LxOrdering_Provider=prov[0]

        lx.save()
    if l:
        movefile(incomdir, filename)
                
           
################################
def parseLxRes(incomdir,filename):
    l = getlines(incomdir+'/%s' % filename)
    n=1
    for items in l:
        if n % 1000 == 0:
            logging.info('%s Lx records done' % n)
        n += 1
                                
        try:
            pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,comp,compname,res,normalf,refl,refh,refu,status,note,accessnum,impre = items
        except:
            try:
                pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,note,access,impre = items
                comp=compname=res=normalf=refl=refh=refu=status=''
            except:
                logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
                continue

                
        try:            
            patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
            logging.warning('Parser In LXRES: NO patient found: %s\n' % str(items))
            continue
            
          
        #always create a new record, since no good way to identify unique tuple

        if not string.strip(orderid): orderid = today  ##since when passing HL7 msg, this is required
        if not string.strip(resd): resd =today
           
        lx = Lx(LxPatient=patient,LxOrder_Id_Num=orderid)

        lx.LxMedical_Record_Number =mrn
        lx.LxTest_Code_CPT=cpt
        lx.LxHVMA_Internal_Accession_number=accessnum
        lx.LxOrderDate=orderd
        lx.LxOrderType=ordertp     
        lx.LxDate_of_result=resd
        lx.LxComponent=comp
        lx.LxComponentName=compname
        lx.LxTest_results=res
        lx.LxNormalAbnormal_Flag=normalf
        lx.LxReference_Low=refl
        lx.LxReference_High=refh

        if not refu: refu = 'N/A'          

        lx.LxReference_Unit=refu
        lx.LxTest_status=status
        lx.LxComment=note
        lx.LxImpression=impre

        #get loinc
        c = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=comp)
        if c:
            lx.LxLoinc=(c[0].Loinc).strip()

        prov=Provider.objects.filter(provCode__exact=phy)         
        if prov:
            lx.LxOrdering_Provider=prov[0]
        lx.save()
        
    if l:
        movefile(incomdir, filename)   


           
################################
def parseRx(incomdir,filename):
    l = getlines(incomdir+'/%s' % filename)
    n=1
    for items in l:
        if n % 1000 == 0:
            logging.info('%s Rx records done' % n)
        n += 1
                                
        try:
            pid,mrn,orderid,phy, orderd,status, meddirect,ndc,med,qua,ref,sdate,edate=items
            route=''
        except:
            pid,mrn,orderid,phy, orderd,status, meddirect,ndc,med,qua,ref,sdate,edate,route=items
           
        try:            
            patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
            logging.warning('Parser In RX: NO patient found: %s\n' % str(items))
            continue

                      
        rxdb =Rx.objects.filter(RxOrder_Id_Num__exact=orderid,RxPatient__DemogPatient_Identifier__exact=pid)
        if not string.strip(orderid): orderid = today  ##since when passing HL7 msg, this is required
        if not rxdb: #new record
            rx = Rx(RxPatient=patient,RxOrder_Id_Num=orderid)
        else: #update record
            rx = rxdb[0]
               
        rx.RxMedical_Record_Number=mrn
        rx.RxOrderDate=orderd
        rx.RxStatus=status
        rx.RxDrugDirect=meddirect
        rx.RxDrugName=med
        rx.RxNational_Drug_Code=ndc
        #if not qua: #dose
        #    qua='NA'
        rx.RxQuantity=qua
        rx.RxRefills=ref
        if not route: route='N/A'
        rx.RxRoute=route
        rx.RxDose = 'N/A'
        rx.RxFrequency='N/A'
        rx.RxStartDate=sdate
        rx.RxEndDate=edate
        prov=Provider.objects.filter(provCode__exact=phy)
        if prov:
            rx.RxProvider=prov[0]
        rx.save()
    if l:
        movefile(incomdir, filename)   


################################
def parseImm(incomdir, filename):
    
    l = getlines(incomdir+'/%s' % filename)
    for items in l:
 
        pid, immtp, immname,immd,immdose,manf,lot,recid = items
        
        try:            
            patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
            logging.warning('Parser In IMM: NO patient found: %s\n' % str(items))
            continue

        imm = Immunization.objects.filter(ImmPatient__DemogPatient_Identifier__exact=pid,ImmRecId=recid)
        if not imm:
            imm = Immunization(ImmPatient=patient,ImmRecId=recid)
        else:
            imm = imm[0]
        imm.ImmType=immtp
        imm.ImmName =immname
        imm.ImmDate =immd
        imm.ImmDose=immdose
        imm.ImmManuf=manf
        imm.ImmLot=lot
       # imm.ImmVisDate=vdate
        try:
            imm.save()
        except:
            logging.error('Parser In IMM: error when save: %s\n' % (str(items)))

    if l:
        movefile(incomdir, filename)   
    
################################
def movefile(incomdir, f):
    """file name format shold be ***.esp.MMDDYY
    YYYYMMDD_prov.txt
    """
    mmddyy = f[-6:]
    year = '20'+mmddyy[-2:]
    mon = mmddyy[:2]

    curdir = os.path.join(TOPDIR,localconfig.LOCALSITE, 'processedData/%s/' % year)
    if not os.path.isdir(curdir):
        os.mkdir(curdir)

    subdir = os.path.join(curdir, 'MONTH_%s/' % mon)
    if not os.path.isdir(subdir):
        os.mkdir(subdir)

    try:
        shutil.move(incomdir+'/%s' % f, subdir)
        logging.info('Parser Moving file %s from %s to %s' % (f, incomdir, subdir))
    except:
        logging.warning('Parser No this file: %s' % f)
    
################################
################################
if __name__ == "__main__":
    try: 
        startt = datetime.datetime.now()
       
        ##get incoming files    
        incomdir = os.path.join(TOPDIR, localconfig.LOCALSITE,'incomingData/')
        #incomdir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/','realData/real_20061023/')
        from validator import getfilesByDay,validateOneday
        days = getfilesByDay(incomdir)
        parsedays = []
#        for oneday in days:
#            err = validateOneday(incomdir,oneday)
        
#            if err: #not OK
#                logging.error("Valitator - Files for day %s not OK, reject to process\n" % oneday)
#            else: #OK
#                logging.info("Validator - Files for day %s OK\n" % oneday)
#                parsedays.append(oneday)
            

        ##start to parse by days
        logging.info('Validating is done, start to parse and sotre data\n')
        for oneday in days: #parsedays:
                logging.info("Parser - parse day %s\n" % oneday)
                provf = 'epicpro.esp.'+oneday
                parseProvider(incomdir, provf)
                #movefile(incomdir, provf) 

                demogf =  'epicmem.esp.'+oneday 
                parseDemog(incomdir, demogf)
                #movefile(incomdir, demogf)

                visf =  'epicvis.esp.'+oneday      
                parseEnc(incomdir , visf)
               # movefile(incomdir, visf)
       
                medf = 'epicmed.esp.'+oneday
                parseRx(incomdir , medf)
              #  movefile(incomdir, medf)
        
                lxresf = 'epicres.esp.'+oneday
                parseLxRes(incomdir,lxresf)
              #  movefile(incomdir, lxresf)
                
                immf = 'epicimm.esp.'+oneday  
                parseImm(incomdir , immf)
               # movefile(incomdir, immf)
        logging.info('Start: %s\n' %  startt)
        logging.info('End:   %s\n' % datetime.datetime.now())
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        logging.info(message+'\n')
    logging.shutdown() 
