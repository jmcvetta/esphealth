
import datetime, random, csv, sys, os


sys.path.append('/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django
import os,sys
from ESP.esp.models import *

from ESP.localsettings import LOCALSITE
from ESP.settings import TOPDIR

incomdir = os.path.join(TOPDIR,LOCALSITE,'incomingData/')
if not os.path.isdir(incomdir):
    os.makedirs(incomdir)
            

today = datetime.datetime.now().strftime('%m%d%Y')
print 'today=%s' % today



try:
    import psyco
    psyco.full()
except:
    print 'no psyco :-('


fnames = ['Bill','Mary','Jim','Donna','Patricia','Susan','Robert','Barry','Bazza','Deena','Kylie','Shane'] # for testing
snames = ['Bazfar','Barfoo','Hoobaz','Sotbar','Farbaz','Zotbaz','Smith','Jones','Fitz','Wong','Wright','Ngyin']
psnames = ['Spock','Kruskal','Platt','Klompas','Lazarus','Who','Nick','Livingston','Doolittle','Casey','Finlay']
sites = ['Brookline Ave','West Roxbury','Matapan','Sydney','Kansas']
city = [('PEABODY','01960'), ('DEDHAM','02026'),('Lincoln','02865'),('Boston','02215')]
races=['ALASKAN','ASIAN','BLACK','CAUCASIAN', 'HISPANIC','INDIAN','NAT AMERICAN','NATIVE HAWAI','OTHER']
routes=['ORAL','INHALATION','INTRAVENOUS']




###################################
###################################
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


#################################
def fakeDemogs(n=100,pcps=[],icds=[],cpts=[],ndcs=[]):
    """create a fake person for testing
    and a fake case - note need to hook these up
    """
    fh = open(incomdir + 'epicmem.esp.'+today, 'w')
    encfh = open(incomdir + 'epicvis.esp.'+today, 'w')
    lxresfh = open(incomdir + 'epicres.esp.'+ today, 'w')
    rxfh = open(incomdir + 'epicmed.esp.'+ today, 'w')
    immfh=open(incomdir +'epicimm.esp.'+today,'w')
    for i in range(1,n+1):
        if i % 100 == 0:
            print i
        ssn = '%03d-%02d-%04d' % (random.randint(1,999),random.randint(1,99),random.randint(1,9999))
        mrn = 'ESPTEST-FAKED%09d' % random.randint(1,999999999)
        recid = '%09d' % random.randint(1,999999999)
        fname,sname=fakename()
        dob = '%04d%02d%02d' % (random.randint(1900,2005),random.randint(1,12),random.randint(1,28))
        gender = 'M'
        if random.random() >= 0.51:
            gender = 'F'
        pcp = random.choice(pcps)
        pname = '%s, %s' % (sname, fname)
        ct,zip = random.choice(city)
        race=random.choice(races)
        p = "%s^%s^%s^%s^^Patient Address 1^^%s^MA^%s^USA^617^1556555^^%s^%s^%s^^%s^%s^^^Aliases^^\n" % (recid,mrn,sname,fname,ct, zip, dob,gender,race, ssn,pcp)
        fh.write(p)   


        fakeimm(fh=immfh,pid=recid)

        for e in range(random.randint(3,6)):
            fakeenc(fh=encfh, pid = recid, mrn = mrn, icds = icds, cpts = cpts, pcps=pcps)

        for e in range(random.randint(1,6)):
            fakerx(fh=rxfh,pid =recid, mrn=mrn, ndcs=ndcs, pcps=pcps)

        for e in range(random.randint(1,6)):
            fakelx(fh=lxresfh,pid = recid, mrn=mrn, cpts=cpts, pcps=pcps)
        

    ##close incoming files
    lxordfh = open(incomdir + 'epicord.esp.'+ today, 'w')
    lxordfh.write("CONTROL TOTALS^epicord^06/01/2006^07/31/2006^553^8/15/06 09:52^8/15/06 09:52^0h0m17s")
    lxordfh.close()

    fh.write("CONTROL TOTALS^epicmem^07/01/2006^07/31/2006^12889^8/9/06 15:10^8/9/06 15:10^0h0m12s\n")
    fh.close()
    
    encfh.write("CONTROL TOTALS^epicvis^06/01/2006^07/31/2006^20059^8/9/06 14:59^8/9/06 15:00^0h0m34s")
    encfh.close()

    lxresfh.write("CONTROL TOTALS^epicres^06/01/2006^07/31/2006^73413^8/15/06 09:52^8/15/06 09:52^0h0m17s")
    lxresfh.close()

    rxfh.write("CONTROL TOTALS^epicmed^06/01/2006^07/31/2006^272^8/15/06 09:52^8/15/06 09:52^0h0m17s")
    rxfh.close()

    immfh.write("CONTROL TOTALS^epicmed^06/01/2006^07/31/2006^272^8/15/06 09:52^8/15/06 09:52^0h0m17s")
    immfh.close()
    
#######################################
def fakeimm(fh=None,pid=1):
    r="%s^TYPE^NAME^^0.5^^LOT^1\n" %(pid)
    fh.write(r)
    
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
    d = '%04d%02d%02d' % (random.choice([2003,2004,2005,2006]),random.randint(1,12),random.randint(1,28))
    orderid = random.randint(100,100000)
    ncode, drugname = random.choice(ndcs)
    pcp = random.choice(pcps)
    route= random.choice(routes)
    r="%s^%s^%s^%s^%s^^%s^%s^^^0^^^%s\n" %(pid,mrn,orderid,pcp,d,drugname,ncode,route)
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

    d = '%04d%02d%02d' % (random.randint(2005,2006),random.randint(1,12),random.randint(1,28))
    orderid = random.randint(1000,100000)
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
    res = "%s^%s^%s^%s^^%s^1^%s^%s^^%s^%s^^^^^^^\n" % (pid,mrn,orderid,d,pcp,cpt,compt,r,f)
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
    
    d = '%04d%02d%02d' % (random.randint(2005,2006),random.randint(1,12),random.randint(1,28))
    # need to avoid multiples of the same icd code because of use of icd9.get in view method
    # ross august 10 2006
    #icd = ','.join([random.choice(icds) for x in range(random.randint(1,3))])
    random.shuffle(icds)
    icd = ' '.join(icds[0:random.randint(2,5)]) # should be unique
    cpt = ','.join([random.choice(cpts) for x in range(random.randint(2,6))])
    pcp = random.choice(pcps)
    s = random.choice(sites)
    e = "%s^%s^%s^%s^Y^^%s^^%s^APPT^^^%s^^^^^^^%s\n" % (pid,mrn,'%08d' % (random.randint(1,9999999)),d,pcp,s,cpt,icd )
    fh.write(e)

 
###################################
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
    pcps = []
    fh = open(incomdir + 'epicpro.esp.'+ today, 'w')
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
        ct,zip = random.choice(city)
        p = "%s^%s^%s^^MD^^%s^Address 1^^%s^MA^%s^617^1234567\n" % (pid,sname,fname,d,ct,zip)
        fh.write(p)
        pcps.append(pid)
    fh.write('CONTROL TOTALS^epicpro^^^346^8/9/06 15:10^8/9/06 15:10^0h0m1s\n')
    fh.close()
 
    return pcps


###################################
def cleanup():
    from django.db import connection
    cursor = connection.cursor()
    sqlist = ['delete from esp_case;']
    sqlist.append('delete from esp_caseworkflow;')
    sqlist.append('delete from esp_pcp;')
    sqlist.append('delete from esp_demog;') 
    sqlist.append('delete from esp_enc;')
    sqlist.append('delete from  esp_lx;')
    sqlist.append('delete from esp_rx;')
    sqlist.append('delete from esp_immunization;')


###################################
###################################
if __name__ == "__main__":


    ##cleanup data table first
    cleanup()
    
    ndcs = [('%s%s' % (x.ndcLbl,x.ndcProd),x.ndcTrade) for x in ndc.objects.filter(ndcTrade__istartswith='Levofloxacin')]
    ndcs += [('%s%s'% (x.ndcLbl,x.ndcProd),x.ndcTrade) for x in ndc.objects.filter(ndcTrade__istartswith='Amoxicillin')]
    ndcs += [('%s%s'% (x.ndcLbl,x.ndcProd),x.ndcTrade) for x in ndc.objects.filter(ndcTrade__istartswith='Ciprofloxacin')]
    print 'got %d ndcs to play with' % (len(ndcs))
    

    icds = [x.icd9Code for x in icd9.objects.extra(where=['icd9Code IN (788.7,099.40,616.10,789.07,789.09,099.56,614.0,614.2,614.3,614.5)'])]
    icds += [x.icd9Code for x in icd9.objects.filter(icd9Long__istartswith='Chlamydia')]
    icds += [x.icd9Code for x in icd9.objects.filter(icd9Long__istartswith='Gonorrhea')]
    print 'got %d icds to play with' % (len(icds))
            
    cpts = [x.cptCode for x in cpt.objects.filter(cptLong__contains='chlamydia')]
    cpts = [x.cptCode for x in cpt.objects.filter(cptLong__contains='ex')]
    cpts += [x.cptCode for x in cpt.objects.filter(cptLong__contains='GC ')]
    cpts = [x.cptCode for x in cpt.objects.filter(cptCode__in=['87491','87492','87591','86631','87800','87178'])]
    print 'got %d cpts to play with' % (len(cpts))
                   
    pcps = fakepcps(50) # make 50 pcps
    fakeDemogs(100,pcps,icds,cpts,ndcs)
