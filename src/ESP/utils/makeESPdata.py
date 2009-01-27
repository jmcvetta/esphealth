# load ESP with some data
# eg  p = pids.PID(PIDLast_Name='Jones',PIDMedical_Record_Number1='1221')
# p.save()
# note the DJANGO_SETTINGS_MODULE must be set
# eg set DJANGO_SETTINGS_MODULE=ESP.settings and run this from
# the folder containing the ESP directory

import datetime,random,csv,sys,os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#os.environ['PYTHONPATH'] = '\home\rerla\mydjango\ESP'
import django
import os
from ESP.esp.models import *
from ESP.settings import TOPDIR
import localconfig

incomdir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/','incomingData/')
today = datetime.datetime.now().strftime('%Y%m%d')

try:
    import psyco
    psyco.full()
except:
    print 'no psyco :-('

fnames = ['Bill','Mary','Jim','Donna','Patricia','Susan','Robert','Barry','Bazza','Deena','Kylie','Shane'] # for testing
snames = ['Bazfar','Barfoo','Hoobaz','Sotbar','Farbaz','Zotbaz','Smith','Jones','Fitz','Wong','Wright','Ngyin']
psnames = ['Spock','Kruskal','Platt','Klompas','Lazarus','Who','Nick','Livingston','Doolittle','Casey','Finlay']
sites = ['Brookline Ave','West Roxbury','Matapan','Sydney','Kansas']

remakendc = 0
remakeicd = 0
remakecpt = 0


WORKFLOW_STATES = (
    ('AR','AWAITING REVIEW'),
    ('UR','UNDER REVIEW'),
    ('Q','IN QUEUE FOR MESSAGING'),
    ('FP','FALSE POSITIVE - DO NOT PROCESS'),
    ('S','SENT TO DESTINATION'),
    )

def getawf(x):
    if x >= len(WORKFLOW_STATES):
        x = random.randint(0,2)
    return WORKFLOW_STATES[x][0]

def fakeCase(p=None,wfn=1,rule=1,pcps=[]):
    """
    caseWorkflow = meta.CharField('Workflow State', maxlength=20,choices=WORKFLOW_STATES, blank=True, )
    caseComments = meta.TextField('Comments', blank=True, null=True)
    caseLastUp
    = meta.DateTimeField('Last Updated date',auto_now=True)
    casecreatedDate = meta.DateTimeField('Date Created', auto_now_add=True)
    caseRuleID = meta.CharField('Rule which generated this case',maxlength=20,  blank=True, null=True)
    caseQueryID = meta.CharField('External Query which generated this case',maxlength=20, blank=True, null=True)
    caseMsgFormat = meta.CharField('Case Message Format', maxlength=10, choices=FORMAT_TYPES, blank=True, null=True)
    caseMsgDest = meta.CharField('Destination for formatted messages', maxlength=10, choices=DEST_TYPES, blank=True, null=True)
    """
    r = Rule.objects.filter(ruleName__exact='Chlamydia')[0]
    pcp = random.choice(pcps)
    if wfn <> None:
        wf = getawf(wfn)
        created = datetime.date(random.randint(2004,2006),random.randint(1,12),random.randint(1,28))
        c = Case(caseWorkflow=wf,caseDemog=p,caseComments='Faked',casecreatedDate=created,caseRule=r,caseProviderid=pcp)
        c.save()
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        s = 'Comments made here are visible whenever the case is viewed. Changes to workflow state can have new comments'
        wfr = CaseWorkflow(workflowCaseID=c,workflowDate=now,workflowState=wf,workflowChangedBy='DataFaker (tm)',workflowComment=s)
        wfr.save()

def fakename():
    """
    """
    if random.random() > 0.5:
        fn1 = random.randint(1,len(fnames)-1)
        fn2 = random.randint(1,len(fnames)-1)
        fname = '%s %s' % (fnames[fn1],fnames[fn2])
    else:
        fn1 = random.randint(1,len(fnames)-1)
        fname = fnames[fn1]
    if random.random() > 0.5:
        sn1 = random.randint(1,len(snames)-1)
        sn2 = random.randint(1,len(snames)-1)
        sname = '%s%s' % (snames[sn1],snames[sn2].lower())
    else:
        sn1 = random.randint(1,len(snames)-1)
        sname = snames[sn1]
    return fname,sname

def fakeDemogs(n=100,wf = 1,pcps=[],icds=[],cpts=[],  ndcs=[]):
#def fakepids(n=100,wf = 1,pcps=[],icds=[],cpts=[],ndcs=[]):
    """create a fake person for testing
    and a fake case - note need to hook these up
    """
    fh = open(incomdir + today+'_demog1.txt', 'w')
    encfh = open(incomdir + today+'_enc1.txt', 'w')
   # lxordfh = open(incomdir + today+'_lxord1.txt', 'w')
    lxresfh = open(incomdir + today+'_lxres1.txt', 'w')
    rxfh = open(incomdir + today+'_rx1.txt', 'w')
    for i in range(1,n+1):
        if i % 100 == 0:
            print i
        ssn = '%03d-%02d-%04d' % (random.randint(1,999),random.randint(1,99),random.randint(1,9999))
        mrn = '%09d' % random.randint(1,999999999)
        recid = '%09d' % random.randint(1,999999999)
        fname,sname=fakename()
        dob = '%04d%02d%02d' % (random.randint(1900,2005),random.randint(1,12),random.randint(1,28))
        gender = 'M'
        if random.random() >= 0.51:
            gender = 'F'
        pcp = random.choice(pcps)
        pname = '%s, %s' % (sname, fname)

        p = "%s^%s^%s^%s^^^^^^^^617^155-5555^^%s^%s^^^%s^%s^^^Aliases^^\n" % (recid,mrn,sname,fname,dob,gender,ssn,pcp)
        fh.write(p)   



        #if wf <> 0:
        #    fakeCase(p=p,wfn=wf,rule=1, pcps=pcps)

        for e in range(random.randint(3,6)):

            fakeenc(fh=encfh, pid = recid, mrn = mrn, icds = icds, cpts = cpts, pcps=pcps)

        for e in range(random.randint(1,6)):
            fakerx(fh=rxfh,pid =recid, mrn=mrn, ndcs=ndcs, pcps=pcps)
        for e in range(random.randint(1,6)):
            fakelx(fh=lxresfh,pid = recid, mrn=mrn, cpts=cpts, pcps=pcps)

    ##close incoming files        
    fh.write("CONTROL TOTALS^epicmem^07/01/2006^07/31/2006^12889^8/9/06 15:10^8/9/06 15:10^0h0m12s\n")
    fh.close()
    encfh.write("CONTROL TOTALS^epicvis^06/01/2006^07/31/2006^20059^8/9/06 14:59^8/9/06 15:00^0h0m34s")
    encfh.close()
   # lxordfh.write("CONTROL TOTALS^epicord^06/01/2006^07/31/2006^553^8/15/06 09:52^8/15/06 09:52^0h0m17s")
   # lxordfh.close()
    lxresfh.write("CONTROL TOTALS^epicres^06/01/2006^07/31/2006^73413^8/15/06 09:52^8/15/06 09:52^0h0m17s")
    lxresfh.close()
    rxfh.write("CONTROL TOTALS^epicmed^06/01/2006^07/31/2006^272^8/15/06 09:52^8/15/06 09:52^0h0m17s")
    rxfh.close()


###################################################
def fakerx(fh=None,pid = 1, mrn=2, ndcs = [], pcps=[]):
    """create a fake enc for testing
    RxPatient_Identifier = models.CharField('Patient Identifier',maxlength=20,blank=True)
    RxMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,blank=True)
    RxOrder_Id_Num = models.CharField('Order Id #',maxlength=20,blank=True)
    RxPrescriber = models.CharField('Prescriber',maxlength=20,blank=True)
    RxOrderDate = models.CharField('Date',maxlength=20,blank=True)
    RxName_of_Drug = models.CharField('Name of Drug',maxlength=20,blank=True)
    RxNational_Drug_Code = models.CharField('National Drug Code',maxlength=20,blank=True)
    RxDose = models.CharField('Dose',maxlength=20,blank=True)
    RxFrequency = models.CharField('Frequency',maxlength=20,blank=True)
    RxQuantity = models.CharField('Quantity',maxlength=20,blank=True)
    RxRefills = models.CharField('Refills',maxlength=20,blank=True)
    """
    d = '%04d%02d%02d' % (random.choice([2003,2004,2005,2006]),random.randint(1,12),random.randint(1,30))
    n = random.choice(ndcs)
    pcp = random.choice(pcps)
    r="%s^%s^^%s^%s^^^%s^^^0^^^ORAL\n" %(pid,mrn,pcp,d,n)
    fh.write(r)


##########################################################    
def fakelx(fh=None,pid = 1, mrn=2, cpts = [], pcps=[]):
    """create a fake lx for testing
    LxPatient_Identifier = models.CharField('Patient Identifier',maxlength=20,blank=True)
    LxMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,blank=True)
    LxOrder_Id_Num = models.CharField('Order Id #',maxlength=20,blank=True)
    LxDate_ordered = models.CharField('Date ordered',maxlength=20,blank=True)
    LxDate_of_result = models.CharField('Date of result',maxlength=20,blank=True)
    LxOrdering_Clinician = models.CharField('Ordering Clinician',maxlength=20,blank=True)
    LxTest_Code_CPT = models.CharField('Test Code (CPT)',maxlength=20,blank=True)
    LxComponent = models.CharField('Component',maxlength=20,blank=True)
    LxTest_results = models.CharField('Test results',maxlength=20,blank=True)
    LxNormalAbnormal_Flag = models.CharField('Normal/Abnormal Flag',maxlength=20,blank=True)
    LxReference_Low = models.CharField('Reference Low',maxlength=20,blank=True)
    LxReference_High = models.CharField('Reference High',maxlength=20,blank=True)
    LxReference_Unit = models.CharField('Reference Unit',maxlength=20,blank=True)
    LxTest_status = models.CharField('Test status',maxlength=20,blank=True)
    LxHVMA_Internal_Accession_number = models.CharField('HVMA Internal Accession number',maxlength=20,blank=True)
    """

    d = '%04d%02d%02d' % (random.randint(2005,2006),random.randint(1,12),random.randint(1,30))
   
    
    cpt = random.choice(cpts)
    pcp = random.choice(pcps)
    r = 'positive nucleic acid amplification on cervical probe'
    f = 'Abnormal'
    if random.random() <= 0.75:
        f = 'Normal'
        r='OK'
    if cpt =='87491':
        compt='1312'
    else:
        compt=''
        
    #ord = "%s^%s^^%s^^^%s^1^%s\n" % (pid,mrn,cpt,d, pcp)
    #ordfh.write(ord)
    res = "%s^%s^^%s^^%s^1^%s^%s^^%s^%s^^^^^^^\n" % (pid,mrn,d,pcp,cpt,compt,r,f)
    fh.write(res)
    

####################################
def fakeenc(fh=None, pid = 1,mrn=2,icds = [], cpts=[], pcps=[]):
    """create a fake enc for testing
    EncPatient_id = models.CharField('Patient Identifier',maxlength=20,blank=True)
    EncMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,blank=True)
    EncEncounter_ID = models.CharField('Encounter ID',maxlength=20,blank=True)
    EncEncounter_Date = models.CharField('Encounter Date',maxlength=20,blank=True)
    EncEncounter_Status = models.CharField('Encounter Status',maxlength=20,blank=True)
    EncEncounter_Clinician = models.CharField('Encounter Clinician',maxlength=20,blank=True)
    EncEncounter_Site = models.CharField('Encounter Site',maxlength=20,blank=True)
    EncEvent_Type = models.CharField('Event Type',maxlength=20,blank=True)
    EncPregnancy_Status = models.CharField('Pregnancy Status',maxlength=20,blank=True)
    EncTemperature = models.CharField('Temperature',maxlength=20,blank=True)
    EncCPT_codes = models.CharField('CPT codes',maxlength=200,blank=True)
    EncICD9_Codes = models.CharField('ICD-9 Codes',maxlength=2000,blank=True)
    EncICD9_Qualifier = models.CharField('ICD-9 Qualifier',maxlength=200,blank=True)
    """
    
    d = '%04d%02d%02d' % (random.randint(2005,2006),random.randint(1,12),random.randint(1,30))
    # need to avoid multiples of the same icd code because of use of icd9.get in view method
    # ross august 10 2006
    #icd = ','.join([random.choice(icds) for x in range(random.randint(1,3))])
    random.shuffle(icds)
    icd = ' '.join(icds[0:random.randint(2,5)]) # should be unique
    cpt = ','.join([random.choice(cpts) for x in range(random.randint(2,6))])
    pcp = random.choice(pcps)
    s = random.choice(sites)
    e = "%s^%s^%s^%s^^^%s^^%s^APPT^^^%s^%s\n" % (pid,mrn,'%08d' % (random.randint(1,9999999)),d,pcp,s,cpt,icd )
    fh.write(e)
 

def fakepcps(n=100):
    """create a fake pcp for testing
    provCode= models.CharField('Physician code',maxlength=20,blank=True)
    provLast_Name = models.CharField('Last Name',maxlength=70,blank=True)
    provFirst_Name = models.CharField('First Name',maxlength=50,blank=True)
    provMiddle_Initial = models.CharField('Middle_Initial',maxlength=20,blank=True)
    provTitle = models.CharField('Title',maxlength=20,blank=True)
    provPrimary_Dept_Id = models.CharField('Primary Department Id',maxlength=20,blank=True)
    provPrimary_Dept = models.CharField('Primary Department',maxlength=20,blank=True)
    provPrimary_Dept_Address_1 = models.CharField('Primary Department Address 1',maxlength=20,blank=True)
    provPrimary_Dept_Address_2 = models.CharField('Primary Department Address 2',maxlength=20,blank=True)
    provPrimary_Dept_City = models.CharField('Primary Department City',maxlength=20,blank=True)
    provPrimary_Dept_State = models.CharField('Primary Department State',maxlength=20,blank=True)
    provPrimary_Dept_Zip = models.CharField('Primary Department Zip',maxlength=20,blank=True)
    provTelAreacode = models.CharField('Primary Department Phone Areacode',maxlength=20,blank=True)
    provTel = models.CharField('Primary Department Phone Number',maxlength=20,blank=True)    
    """
    fakepcps = []
    fh = open(incomdir + today+'_prov1.txt', 'w')
    for i in range(n):
        if random.random() > 0.5:
            fn1 = random.randint(1,len(fnames)-1)
            fn2 = random.randint(1,len(fnames)-1)
            fname = '%s %s' % (fnames[fn1],fnames[fn2])
        else:
            fn1 = random.randint(1,len(fnames)-1)
            fname = fnames[fn1]
        sn1 = random.randint(1,len(psnames)-1)
        sname = psnames[sn1]
        d = random.choice(sites)
        pid = '%s_%s_%d' % (sname[:3],fname[:3],i)
        p = "%s^%s^%s^^MD^^%s^^^^^^^\n" % (pid,sname,fname,d)
        fh.write(p)
        fakepcps.append(pid)
    fh.write('CONTROL TOTALS^epicpro^^^346^8/9/06 15:10^8/9/06 15:10^0h0m1s\n')
    fh.close()
 
    return fakepcps

##################################
def makecpt():
    """found these at www.tricare.osd.mil/tai/downloads/cpt_codes.xls
    """
    reader = csv.reader(open('cpt_codes.csv','rb'),dialect='excel')
    header = reader.next()
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    i = 0
    for ll in reader: # here be dragons. lots of "" at the 4th pos - but some other subtle crap too...
        code,long,short = ll[:3] # good thing it doesn't really matter..
        i += 1
        if i % 10000 == 0:
            print i,'cpt done'
        long = long.replace('"','')
        short = short.replace('"','')
        c = cpt(cptCode=code,cptLong=long.capitalize(),cptShort=short.capitalize(),cptLastedit=now)
        c.save()
        
def makeicd9():
    """ found these codes somewhere or other..."""
    codes = []
    n = 1
    from ESPicd9 import icd
    for line in icd.split('\n'):
        if n % 10000 == 0:
            print n,'icd done'
        n += 1
        line = line.replace("'",'')
        code,trans = line.split('\t')
        code = '%s.%s' % (code[:3],code[3:]) # make all 3 digit decimals
        c = icd9(icd9Code=code,icd9Long=trans.capitalize())
        c.save()
        
def makendc():
    """ found these codes somewhere http://www.fda.gov/cder/ndc/"""
    f = file('ndc_codes.txt','r')
    foo = f.next() # lose header
    n = 1
    for line in f:
        if n % 10000 == 0:
            print n,'ndc done'
        n += 1
        lbl = line[8:14]
        prod = line[15:19]
        trade = line[44:].strip()        
        newn = ndc(ndcLbl=lbl.capitalize(),ndcProd=prod.capitalize(),ndcTrade=trade.capitalize())
        newn.save()

def remakeCodes():
    """
    """
    from django.db import connection
    cursor = connection.cursor()
    sqlist = ['delete from esp_ndc;']
    sqlist.append('delete from esp_icd9;')
    sqlist.append('delete from esp_cpt;')
    sqlist.append('commit;')
    for sql in sqlist:
        print sql
        try:
            cursor.execute(sql)
        except:
            print 'Error executing %s' % sql

    makendc()
    makeicd9()
    makecpt()

def cleanup():
    from django.db import connection
    cursor = connection.cursor()
    sqlist = ['delete from esp_case;']
    sqlist.append('delete from esp_caseworkflow;')
    sqlist.append('delete from esp_pcp;')
    sqlist.append('delete from esp_demog;')  ##Xuanlin
    sqlist.append('delete from esp_enc;')
    sqlist.append('delete from  esp_lx;')
    sqlist.append('delete from esp_rx;')
    sqlist.append('delete from esp_pid;')

    sqlist.append('delete from esp_rule;')
    if remakendc:
        sqlist.append('delete from esp_ndc;')    
    if remakeicd:
        sqlist.append('delete from esp_icd;')    
    if remakecpt:
        sqlist.append('delete from esp_cpt;')    

    sqlist.append('commit;')
    for sql in sqlist:
        print sql
        try:
            cursor.execute(sql)
        except:
            print 'Error executing %s' % sql
    if remakendc:
        makendc()    
    if remakeicd:
        makeicd9()  
    if remakecpt:
        makecpt()   


if __name__ == "__main__":

   # cleanup()


   # ndcs = ['%s%s' % (x.ndcLbl,x.ndcProd) for x in ndc.objects.filter(ndcTrade__istartswith='azithromycin 1 g')]
    ndcs = ['%s%s' % (x.ndcLbl,x.ndcProd) for x in ndc.objects.filter(ndcTrade__istartswith='Darvon')]
   

    print 'got %d ndcs to play with' % (len(ndcs))
    

    icds = [x.icd9Code for x in icd9.objects.extra(where=['icd9Code IN (079.88,099.5,09953)'])]
    icds += [x.icd9Code for x in icd9.objects.filter(icd9Long__istartswith='Chlamydia')]

    print 'got %d icds to play with' % (len(icds))

    cpts = [x.cptCode for x in cpt.objects.filter(cptLong__contains='chlamydia')]
 
    cpts = [x.cptCode for x in cpt.objects.filter(cptLong__contains='ex')]
    cpts += [x.cptCode for x in cpt.objects.filter(cptLong__contains='re')]
    cpts = [x.cptCode for x in cpt.objects.filter(cptCode__exact='87491')]
    print 'got %d cpts to play with' % (len(cpts))

    pcps = fakepcps(10) # make 10 pcps
    fakeDemogs(20,1,pcps,icds,cpts,ndcs)

    
#    r = Rule(ruleName='Chlamydia',ruleSQL='Chlamydia rules',ruleMsgFormat='HL7',ruleMsgDest='MaDPH',
#             ruleHL7Code='603.9',ruleHL7Name='Chlamydia',ruleHL7CodeType='I9')
#    r.save()
#    r = Rule(ruleName='LatentTB',ruleSQL='Latent TB rules',ruleMsgFormat='HL7',ruleMsgDest='MaDPH',
#             ruleHL7Code='023.9',ruleHL7Name='LatentTB',ruleHL7CodeType='I9')
#    r.save()

   # fakeDemogs(20,2,pcps,icds,cpts,ndcs)
   # fakeDemogs(20,3,pcps,icds,cpts,ndcs)
   # fakeDemogs(20,4,pcps,icds,cpts,ndcs)
   # fakeDemogs(100000,None,pcps,icds,cpts,ndcs)

