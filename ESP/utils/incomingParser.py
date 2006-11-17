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
logging = localconfig.getLogging('incomingParser.py_v0.1', debug=0)


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

###############################
def yieldlines(fname):
    """iterator to return delim split lines"""
    delim = '^'
    try:
        f = open(fname)
    except:
        logging.error('Can not read file:%s\n' % fname)
        return 
    returnl = []
    for line in f:
        try:
            returnl = line.split(delim)
            yield returnl
        except:
            logging.error('Split ERROR for %s:%s\n' % (fname,line))
            return 
        
    return 



################################
def parseProvider(incomdir, filename):
#    l = getlines(incomdir+'/%s' % filename)

    provdict={}
    lines = yieldlines(incomdir+'/%s' % filename)
    for items in lines:
        if not items or items[0]=='CONTROL TOTALS':
            continue
        
        try:
            phy,lname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone  = [x.strip() for x in items]
        except:
            logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
        if not fname:
            fname = 'Unknown'
        if not lname:
            lanme = 'Unknown'
        if phone:
            phone = string.replace(phone, '-','')
        if not phonearea: #fake one
            phonearea='999'
            
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
        provdict[phy] = prov

    movefile(incomdir, filename)
    return provdict

################################
def parseDemog(incomdir, filename):
#    l = getlines(incomdir+'/%s' % filename)

    demogdict={}
    n=1
    lines = yieldlines(incomdir+'/%s' % filename)
    for items in lines:
        if not items or items[0]=='CONTROL TOTALS':
            continue

        if n % 1000 == 0:
            logging.info('%s Demog records done' % n)
        n += 1
                                
        try:
            pid,mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,phy,mari,religion,alias,mom,death  = [x.strip() for x in items]
            
        except:
            logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
        pdb = Demog.objects.filter(DemogPatient_Identifier__exact=pid)
        if not pdb: #new record
            demog = Demog(DemogPatient_Identifier=pid)
        else: #update record
            demog = pdb[0]
        
        #fake sone
        if not fname:
            fname = 'Unknown'
        if not lname:
            lanme = 'Unknown'
        if not phonearea: #fake one
            phonearea='999'
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
        demogdict[pid]=demog
        

    movefile(incomdir, filename)
    return demogdict

################################
def parseEnc(incomdir, filename,demogdict,provdict):
   # l = getlines(incomdir+'/%s' % filename)
    n=1
    lines = yieldlines(incomdir+'/%s' % filename)
    for items in lines:
        if not items or items[0]=='CONTROL TOTALS':
            continue

        if n % 2000 == 0:
            logging.info('%s Enc records done' % n)
        n += 1
                              
        try:
            pid,mrn,encid,encd,close,closed,phy,deptid,dept,enctp,edc,temp,cpt,icd9  = [x.strip() for x in items]
        except:
            logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
            
        try:    
            patient = demogdict[pid]    
#        patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
        #if not patient:
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
           
        #prov=Provider.objects.filter(provCode__exact=phy)
        #prov = provdb.filter(provCode=phy)[0]
        try:
            prov =provdict[phy]
            enc.EncEncounter_Provider=prov
        except:
            pass


        enc.save()

    movefile(incomdir, filename)    
        
                
           
################################
def parseLxRes(incomdir,filename,demogdict, provdict):
#    l = getlines(incomdir+'/%s' % filename)
    n=1

    lines = yieldlines(incomdir+'/%s' % filename)
    for items in lines:
        if not items or items[0]=='CONTROL TOTALS':
            continue

        if n % 2000 == 0:
            logging.info('%s Lx records done' % n)
        n += 1


        try:
            pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,comp,compname,res,normalf,refl,refh,refu,status,note,accessnum,impre  = [x.strip() for x in items]
        except:
            try:
                pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,note,access,impre  = [x.strip() for x in items]
                comp=compname=res=normalf=refl=refh=refu=status=''
            except:
                logging.error('Parser %s: wrong size - %s' % (filename,str(items)))
                continue

        ##This is to double check if ESP identifies all cases
        if compname.upper().find('CHLAMYDIA')!=-1 or note.upper().find('CHLAMYDIA')!=-1:
            logging.info("CHLAMYDIA LX: %s\n"  % str(items))
            
        try:
            patient = demogdict[pid]
            #patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
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
        elif compname:
            if compname.upper().find('CHLAMYDIA')!=-1: ##log new CPT code which is not in esp_cptloincmap
                logging.error('NEW CHLAMYDIA CPT code: %s' % str(items))
                
        #prov=Provider.objects.filter(provCode__exact=phy)         
        #if prov:
        try:
            prov=provdict[phy]
            lx.LxOrdering_Provider=prov
        except:
            pass
        
        lx.save()
        

    movefile(incomdir, filename)   


           
################################
def parseRx(incomdir,filename,demogdict,provdict):
#    l = getlines(incomdir+'/%s' % filename)

    n=1
    lines = yieldlines(incomdir+'/%s' % filename)
    for items in lines:
        if not items or items[0]=='CONTROL TOTALS':
            continue
                
        if n % 2000 == 0:
            logging.info('%s Rx records done' % n)
        n += 1
                                
        try:
            pid,mrn,orderid,phy, orderd,status, med,ndc,meddesc,qua,ref,sdate,edate  = [x.strip() for x in items]
            route=''
        except:
            pid,mrn,orderid,phy, orderd,status, med,ndc,meddesc,qua,ref,sdate,edate,route  = [x.strip() for x in items]
            
           
        try:
            patient=demogdict[pid]
            #patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
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
        rx.RxDrugDesc=meddesc
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

        #prov=Provider.objects.filter(provCode__exact=phy)
        #if prov:
        try:
            prov=provdict[phy]
            rx.RxProvider=prov
        except:
            pass

        rx.save()
    movefile(incomdir, filename)   


################################
def parseImm(incomdir, filename,demogdict):
    
    #l = getlines(incomdir+'/%s' % filename)
    lines = yieldlines(incomdir+'/%s' % filename)
    for items in lines:
        if not items or items[0]=='CONTROL TOTALS':
            continue
                    
        pid, immtp, immname,immd,immdose,manf,lot,recid  = [x.strip() for x in items]
        
        try:
            patient = demogdict[pid]
            #patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
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

    movefile(incomdir, filename)   
    
################################
def movefile(incomdir, f):
    """file name format shold be ***.esp.MMDDYY
    YYYYMMDD_prov.txt
    """
    ##save the filename in DB
    dataf = DataFile()
    dataf.filename=f
    dataf.save()
    
    ##move file to processed directory
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

        from validator import getfilesByDay,validateOneday
        days = getfilesByDay(incomdir)
        parsedays = []
        for oneday in days:
            err = validateOneday(incomdir,oneday)
        
            if err: #not OK
                logging.error("Valitator - Files for day %s not OK, reject to process\n" % oneday)
            else: #OK
                logging.info("Validator - Files for day %s OK\n" % oneday)
                parsedays.append(oneday)
            

        ##start to parse by days
        logging.info('Validating is done, start to parse and sotre data\n')
        for oneday in parsedays:
                logging.info("Parser - parse day %s\n" % oneday)
                provf = 'epicpro.esp.'+oneday
                provdict = parseProvider(incomdir, provf)

                demogf =  'epicmem.esp.'+oneday 
                demogdict = parseDemog(incomdir, demogf)

                visf =  'epicvis.esp.'+oneday      
                parseEnc(incomdir , visf,demogdict,provdict)

       
                medf = 'epicmed.esp.'+oneday
                parseRx(incomdir , medf,demogdict,provdict)
        
                lxresf = 'epicres.esp.'+oneday
                parseLxRes(incomdir,lxresf, demogdict,provdict)

                
                immf = 'epicimm.esp.'+oneday  
                parseImm(incomdir , immf, demogdict)

        logging.info('Start: %s\n' %  startt)
        logging.info('End:   %s\n' % datetime.datetime.now())
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        logging.info(message+'\n')
    logging.shutdown() 
