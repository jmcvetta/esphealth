# incoming parser
# uses a generator for large file processing
# of delimited files

import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESPNew/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR
import localconfig 

import string,re,copy
import shutil
import StringIO
import traceback

VERSION = '0.2'
DO_VALIDATE = 1 # set to zero to avoid the validation step
REJECT_INVALID = 0 # don't process if any errors - usually are missing provider so ignore

today=datetime.datetime.now().strftime('%Y%m%d')

########For logging
iplogging= localconfig.getLogging('incomingParser.py_%s' % VERSION, debug=0)

##store the new CPT code for Chlamydia
chlamydia =[]

###############################
def getlines(fname):
    """uses ram - not a great idea for million line files
    """
    try:
        lines = file(fname).readlines()
    except:
        iplogging.error('Can not read file:%s\n' % fname)
        return []
    returnl = [x.split('^') for x in lines[:-1] if len(x.split('^')) > 1]
    iplogging.info('Parser Process %s: %s records\n' % (fname, len(returnl)))
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
          n += 1
       except:
          more = 0
          raise StopIteration
       if not validate: # when validating, we just want the line - otherwise split
          ll = r.split(delim) 
          r = [x.strip() for x in ll]
          n += 1
          if n % 1000000 == 0:
             iplogging.info('At line %d in file %s' % (n,fname))
       if validate or r > 2: # ignore lines without delimiters if not validation phase
           yield (r, n)


################################
def parseProvider(incomdir, filename):
    """
    """

    provdict={}
    fname = os.path.join(incomdir,'%s' % filename)
    f = splitfile(fname,'^')
    for (items,line) in f:
        if not items or items[0]=='CONTROL TOTALS':
            continue
        
        try:
            phy,lname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone  = items #[x.strip() for x in items]
        except:
            iplogging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
        if not fname:
            fname = 'Unknown'
        if not lname:
            lname = 'Unknown'
        if phone:
            phone = string.replace(phone, '-','')
        #if not phonearea: #fake one
        #    phonearea='999'
            
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
    """
    """
    demogdict={}
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            continue                                
        try:
            pid,mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,phy,mari,religion,alias,mom,death  = items #[x.strip() for x in items]            
        except:
            iplogging.error('Parser %s: wrong size - %s at line# %d' % (filename,str(items),linenum)) # 25 needed
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
            lname = 'Unknown'
        #if not phonearea: #fake one
        #    phonearea='999'
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
    """
    """
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):

        if not items or items[0]=='CONTROL TOTALS':
            continue
        try:
            pid,mrn,encid,encd,close,closed,phy,deptid,dept,enctp,edc,temp,cpt,tmp1,tmp2,tmp3,tmp4,tmp5,tmp6,icd9  = items #[x.strip() for x in items]
        except:
            iplogging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
            
        try:    
            patient = demogdict[pid]    
        except:
            iplogging.warning('Parser In ENC: NO patient found: %s\n' % str(items))
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
               

        try:
            prov =provdict[phy]
            enc.EncEncounter_Provider=prov
        except:
            pass


        enc.save()

    movefile(incomdir, filename)    


################################
def parseLxOrd(incomdir,filename,demogdict, provdict):
    
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            continue

        try:
            pid,mrn,orderid,cpt,modi,accessnum,orderd, ordertp, phy = items
        except:
            iplogging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue

            
        try:
            if demogdict:
                patient = demogdict[pid]
            else:
                patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
            iplogging.warning('Parser In LXORD: NO patient found: %s\n' % str(items))
            continue

        
        #always create a new record, since no good way to identify unique tuple
        if not string.strip(orderid): orderid = today  ##since when passing HL7 msg, this is required
        
        lx = Lx(LxPatient=patient,LxOrder_Id_Num=orderid)
        lx.LxMedical_Record_Number =mrn
        lx.LxTest_Code_CPT=cpt
        lx.LxTest_Code_CPT_mod =modi
        lx.LxHVMA_Internal_Accession_number=accessnum
        lx.LxOrderDate=orderd
        lx.LxOrderType=ordertp

        
        #get loinc
        c = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt='')
        if c:
            lx.LxLoinc=(c[0].Loinc).strip()

        try:
            if provdict:
                prov=provdict[phy]
            else:
                prov=Provider.objects.filter(provCode__exact=phy)[0]
            lx.LxOrdering_Provider=prov
        except:
            pass
                
        lx.save()
                
    movefile(incomdir, filename)
                                                                                                                                                                                                                                                                                                                                            
                
           
################################
def parseLxRes(incomdir,filename,demogdict, provdict):
    """
    """
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            continue
        try:
            pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,comp,compname,res,normalf,refl,refh,refu,status,note,accessnum,impre  = items #[x.strip() for x in items]
        except:
            try:
                pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,note,access,impre  = items #[x.strip() for x in items]
                comp=compname=res=normalf=refl=refh=refu=status=''
            except:
                iplogging.error('Parser %s: wrong size - %s' % (filename,str(items)))
                continue

        ##This is to double check if ESP identifies all cases
        #if compname.upper().find('CHLAMYDIA')!=-1 or note.upper().find('CHLAMYDIA')!=-1:
        #    iplogging.info("CHLAMYDIA LX: %s\n"  % str(items))
            
        try:
            if demogdict:
                patient = demogdict[pid]
            else:
                patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
            iplogging.warning('Parser In LXRES: NO patient found: %s\n' % str(items))
            continue
            
          
        #always create a new record, since no good way to identify unique tuple

        if not string.strip(orderid):
            orderid = today  ##since when passing HL7 msg, this is required
        if not string.strip(resd):
            resd =today

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

        if not refu:
            refu = 'N/A'          

        lx.LxReference_Unit=refu
        lx.LxTest_status=status
        lx.LxComment=note
        lx.LxImpression=impre

        #get loinc
        c = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=comp)
        if c:
            lx.LxLoinc=(c[0].Loinc).strip()
        elif compname:
            if compname.upper().find('CHLAMYDIA')!=-1 and (cpt,comp) not in chlamydia: ##log new CPT code which is not in esp_cptloincmap
                chlamydia.append((cpt,comp))
                

        try:
            if provdict:
                prov=provdict[phy]
            else:
                prov=Provider.objects.filter(provCode__exact=phy)[0]
            lx.LxOrdering_Provider=prov
        except:
            pass
        
        lx.save()

    movefile(incomdir, filename)   


           
################################
def parseRx(incomdir,filename,demogdict,provdict):

    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            continue                                
        try:
            if len(items) == 13:
                pid,mrn,orderid,phy, orderd,status, med,ndc,meddesc,qua,ref,sdate,edate  = items #[x.strip() for x in items]
                route=''
            else:
                pid,mrn,orderid,phy, orderd,status, med,ndc,meddesc,qua,ref,sdate,edate,route  = items #[x.strip() for x in items]
        except:
            iplogging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
                         
           
        try:
            patient=demogdict[pid]
            #patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
            iplogging.warning('Parser In RX: NO patient found: %s\n' % str(items))
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
    
    fname = os.path.join(incomdir,'%s' % filename)
    for (items, linenum) in splitfile(fname,'^'):
        if not items or items[0]=='CONTROL TOTALS':
            continue
        try:
            pid, immtp, immname,immd,immdose,manf,lot,recid  = items #[x.strip() for x in items]
        except:
            iplogging.error('Parser %s: wrong size - %s' % (filename,str(items)))
            continue
                                    
        try:
            if demogdict:
                patient = demogdict[pid]
            else:
                patient = Demog.objects.filter(DemogPatient_Identifier__exact=pid)[0]
        except:
            iplogging.warning('Parser In IMM: NO patient found: %s\n' % str(items))
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
            iplogging.error('Parser In IMM: error when save: %s\n' % (str(items)))

    movefile(incomdir, filename)   
    
################################
def movefile(incomdir, f):
    """file name format shoUld be ***.esp.MMDDYY
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
        iplogging.info('Moving file %s from %s to %s\n' % (f, incomdir, subdir))
        shutil.move(incomdir+'/%s' % f, subdir)
    except:
        iplogging.warning('Parser No this file: %s' % f)


################################
def getfilesByDay(incomdir):
    files=os.listdir(incomdir)
    files.sort()
    dayfiles={}
    for f in files:
        if dayfiles.has_key(f[-6:]):
            dayfiles[f[-6:]].append(f)
        else:
            dayfiles[f[-6:]] = [f]
            
    days = dayfiles.keys()
    days.sort()
    
    return days

################################
def validateOnefile(incomdir, fname,delimiternum,needidcolumn,datecolumn=[],required=[],returnids=[],checkids=[]):
    returnd={}
    errors=0
    fname = os.path.join(incomdir,'%s' % fname)
    try:
        f = file(fname,'r')
        f.close()
    except:
        iplogging.error('Validator - Can not read file:%s\n' % (fname))
        return (errors, returnd)
    for (l, linenum) in splitfile(fname,'^',True):
        l = l.strip()
        if not l or l.find('CONTROL TOTALS')>-1:
            continue
        
        fnum=len(re.findall("\^",l))

        #check delimit number
        if int(delimiternum) != fnum:
            msg ='Validator - %s: wrong number of delimiter, should be %s, in file=%s\n=========LINE%s: %s\n' % (fname,delimiternum,fnum,linenum,l)
            errors = 1
            iplogging.error(msg)
            
        items = l.split('^')
        if items == ['']* (int(delimiternum)+1):
            continue
        
        #check required fileds
        for r in required:
            if not string.strip(items[r]):
                col = r+1
                msg = 'Validator - %s, LINE%s: Empty for Required filed in column %s\n' % (fname,linenum, col )
                errors = 1
                iplogging.error(msg)
                
                
        ##check ID
        if checkids and needidcolumn and items[needidcolumn[0]].strip() not in checkids[0]:
            msg = """Validator - %s: LINE%s-Patient =%s= not in mem file\n""" % (fname, linenum, items[needidcolumn[0]])
            iplogging.error(msg)
            errors=1
        if checkids and len(needidcolumn)==2 and items[needidcolumn[1]].strip() not in checkids[1]:
            msg = """Validator - %s: LINE%s-Provider =%s= not in provider file\n""" % (fname, linenum, items[needidcolumn[1]])
            iplogging.error(msg)
            errors=1

        #check returnd    
        for n in returnids:
            returnd.setdefault(0,[]).append(items[n].strip())

        #check date
        for d in datecolumn:
            if items[d] and len(items[d])!=8 or re.search('\D', items[d]):
                msg = 'Validator - %s: wrong Date format: %s\n=========LINE%s: %s\n'  % (fname,items[d],linenum, l)
                errors = 1
                iplogging.error(msg)

    return  (errors,returnd)                                                                                                                                                                                                                                                                                                                                                      


################################
def validateOneday(incomdir, oneday):
    """validate one day files
    """

    finalerr=0
    #patient
    demogf = 'epicmem.esp.'+oneday
    iplogging.info('Validator - Process %s' % demogf)
    (err,tempd) = validateOnefile(incomdir,demogf,24,[0],datecolumn=[14],required=[0,1],returnids=[0])
    pids = tempd[0]
    if err:
        finalerr = 1
        
    #provider
    providerf = 'epicpro.esp.'+oneday
    iplogging.info('Validator -Process %s' % providerf)
    err,tempd = validateOnefile(incomdir,providerf,13,[0],required=[0],returnids=[0] )
    provids= tempd[0]
    if err:
        finalerr = 1
        
    #encounter
    visf = 'epicvis.esp.'+oneday
    iplogging.info('Validator -Process %s' % visf)
    err,tempd = validateOnefile(incomdir,visf,19,[0,6], datecolumn=[3,5,10],required=[0,1],checkids=[pids,provids])
    if err:
        finalerr = 1
        
    #lxord
    lxordf = 'epicord.esp.'+oneday
    iplogging.info('Validator - Process %s' % lxordf)
    err, tempd = validateOnefile(incomdir,lxordf,8,[0,8],datecolumn=[6],required=[0,1],checkids=[pids,provids])
    if err:
        finalerr = 1

    #lxres
    lxresf = 'epicres.esp.'+oneday
    iplogging.info('Validator - Process %s' % lxresf)
    err, tempd = validateOnefile(incomdir,lxresf,18,[0,5],datecolumn=[3,4],required=[0,1],checkids=[pids,provids])
    if err :
        finalerr = 1

    #med
    medf = 'epicmed.esp.'+oneday
    iplogging.info('Validator - Process %s' % medf)
    err,tempd = validateOnefile(incomdir,medf,13,[0,3],datecolumn=[4,11,12],required=[0,1],checkids=[pids,provids])
    if err:
        finalerr = 1

    #imm
    mmf = 'epicimm.esp.'+oneday
    iplogging.info('Validator - Process %s' % mmf)
    err,tempd = validateOnefile(incomdir,mmf,7,[0],datecolumn=[3],checkids=[pids,provids])
    if err :
        finalerr = 1
    return finalerr
                                                                                      
    
################################
def doValidation(incomdir,days):

    parsedays = []
    for oneday in days:
        err = validateOneday(incomdir,oneday)
        if REJECT_INVALID and err: #not OK
            iplogging.error("Validator - Files for day %s not OK, rejected - not  processed\n" % oneday)
        else: #OK
            iplogging.info("Validator - Files for day %s OK\n" % oneday)
            parsedays.append(oneday)
    return parsedays

################################
################################
if __name__ == "__main__":
    try: 
        startt = datetime.datetime.now()
       
        ##get incoming files and do validations
        incomdir = os.path.join(TOPDIR, localconfig.LOCALSITE,'incomingData/')
        days = getfilesByDay(incomdir)
        if DO_VALIDATE:
                parsedays = doValidation(incomdir,days)
        else:
                parsedays = copy.copy(days)
        iplogging.info('Validating is done. Days are: %s;  Parsed days are %s\n' % (str(days),str(parsedays)))


        ##start to parse by days
        ##always load files no matter it passed validator or not
        for oneday in days:
            iplogging.info("Parser - parse day %s\n" % oneday)
            provf = 'epicpro.esp.'+oneday
            provdict = parseProvider(incomdir, provf)

            demogf =  'epicmem.esp.'+oneday 
            demogdict = parseDemog(incomdir, demogf)
            
            visf =  'epicvis.esp.'+oneday      
            parseEnc(incomdir , visf,demogdict,provdict)

            medf = 'epicmed.esp.'+oneday
            parseRx(incomdir , medf,demogdict,provdict)

            lxordf = 'epicord.esp.'+oneday
            parseLxOrd(incomdir,lxordf, demogdict,provdict)

            lxresf = 'epicres.esp.'+oneday
            parseLxRes(incomdir,lxresf, demogdict,provdict)
      
            immf = 'epicimm.esp.'+oneday  
            parseImm(incomdir , immf, demogdict)

        iplogging.warning('New Chlamydia CPT code: %s\n' % str(chlamydia))
        
        iplogging.info('Start: %s\n' %  startt)
        iplogging.info('End:   %s\n' % datetime.datetime.now())
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        iplogging.info(message+'\n')
    iplogging.shutdown()
    