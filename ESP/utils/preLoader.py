##preLoader is to load some data into ESP_conditionNDC table, ESP_conditionLOINC, ESP_CPTLOINCMAP table
##
import os,sys
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


import django, datetime
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR
from ESP.utils import localconfig 
import string,csv
import traceback
import StringIO

logging = localconfig.getLogging('preLoader.py v0.1', debug=0)
datadir = os.path.join(TOPDIR,localconfig.LOCALSITE, 'preLoaderData/')


###############################
def getlines(fname):
    logging.info('Process %s\n' % fname)
    lines = file(fname).readlines()
   # print file,len(lines)
    returnl = [x.split('\t') for x in lines if len(x.split('\t')) >= 1]
    return returnl

 
################################
def load2cptloincmap(table):
    lines = getlines(datadir+table+'.txt')
   
    for l in lines:
        id, cpt,cmpt,loinc = [x.strip() for x in l]
        if id:
            try:
                cl = CPTLOINCMap.objects.filter(id__exact=id)[0]
            except:
                cl = CPTLOINCMap()
        else:
            c = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=cmpt,Loinc=loinc)
            if not c:
                cl = CPTLOINCMap()
            else:
                continue
            
        cl.CPT = cpt
        cl.CPTCompt=cmpt
        cl.Loinc=loinc
        cl.save()


################################
def load2ndc(table):
    lines = getlines(datadir+table+'.txt')
    
    for l in lines:
        id, rulename, ndc,define,send = [x.strip() for x in l]
        
        r = Rule.objects.filter(ruleName__iexact=rulename)[0]
        #ndc = '0'+string.replace(ndc,'-','')
        if string.strip(id):
            try:
                cl = ConditionNdc.objects.filter(id__exact=id)[0]
            except:
                cl = ConditionNdc()
        else:
            c = ConditionNdc.objects.filter(CondiRule__ruleName__iexact=rulename,CondiNdc=ndc)
            if not c:
                cl = ConditionNdc()
            else:
                cl = c[0]
        cl.CondiRule=r
        cl.CondiNdc=ndc
        cl.CondiDefine=define
        cl.CondiSend=send
        cl.save()


################################
def load2icd9(table):
    lines = getlines(datadir+table+'.txt')
    for l in lines:
        id, rulename, icd,define,send = [x.strip() for x in l]
        r = Rule.objects.filter(ruleName__iexact=rulename)[0]
        if string.strip(id):
            try:
                cl = ConditionIcd9.objects.filter(id__exact=id)[0]
            except:
                cl = ConditionIcd9()
        else:
            c = ConditionIcd9.objects.filter(CondiRule__ruleName__iexact=rulename,CondiICD9=icd)
            if not c:
                cl = ConditionIcd9()
            else:
                cl = c[0]
        cl.CondiRule=r
        cl.CondiICD9=icd
        cl.CondiDefine=define
        cl.CondiSend=send
        cl.save()

        
################################
def load2loinc(table):
    lines = getlines(datadir+table+'.txt')
    for l in lines:
        id, rulename, loinc,snmdposi,snmdnega,snmdinde,define,send = [x.strip() for x in l]

        r = Rule.objects.filter(ruleName__iexact=rulename)[0]
        if string.strip(id):
            try:
                cl = ConditionLOINC.objects.filter(id__exact=id)[0]
            except:
                cl = ConditionLOINC()
        else:
            c = ConditionLOINC.objects.filter(CondiRule__ruleName__iexact=rulename,CondiLOINC=loinc)
            if not c:
                cl = ConditionLOINC()
            else:
                cl = c[0]
        cl.CondiRule=r
        cl.CondiLOINC=loinc
        cl.CondiDefine=define
        cl.CondiSend=send
        cl.CondiSNMDPosi=snmdposi
        cl.CondiSNMDNega=snmdnega
        cl.CondiSNMDInde=snmdinde
        cl.save()


################################
def load2rule(table):
    lines = getlines(datadir+table+'.txt')
  
    for items  in lines:
        id, name,fmt, dest,hl7name,hl7c,hl7ctype,note = (x.strip() for x in items)
        if not name: continue
        rl=''
        if id:
            rl = Rule.objects.filter(id__exact=id)
            if rl:
                rl=rl[0]

        if not rl:
            r = Rule.objects.filter(ruleName__iexact=name)
            if r:   
                rl=r[0]
            else:
                rl = Rule()

        rl.ruleName = name
        rl.ruleMsgFormat = fmt
        rl.ruleMsgDest = dest
        rl.ruleHL7Name = hl7name
        rl.ruleHL7Code = hl7c
        rl.ruleHL7CodeType = hl7ctype
        rl.ruleComments = note
        rl.save()
        
################################
def  load2config(table):
    lines = getlines(datadir+table+'.txt')
    #print lines
  
    for items  in lines:
        (id, t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25) = [x.strip() for x in items]
        if id:
            try:
                cf = config.objects.filter(id__exact=id)[0]
            except:
                cf = config()
        else:
            cf = config()
        
        cf.appName = t1
        cf.FacilityID=t2
        cf.sendingFac=t3

        cf.instTechName = t4
        cf.instTechEmail = t5
        cf.instTechTel = t6
        cf.instTechcel = t7
        
        cf.institution_name=t8
        cf.institution_CLIA=t9
        cf.instAddress1=t10
        cf.instAddress2 = t11
        cf.instCity = t12
        cf.instState = t13
        cf.instZip= t14
        cf.instCountry = t15
        cf.instTel=t16
        cf.instFax =t17
        
        cf.instIDFName = t18
        cf.instIDLName = t19
        cf.instIDEmail =t20
        cf.instIDTelArea = t21
        cf.instIDTel = t22
        cf.instIDTelExt = t23
        cf.instIDcel= t24
        cf.instComments=t25      
        cf.save()

###################################
###################################
#################################
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


###################################
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


###################################
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
                                                                                                                                                                                                                                            
            
################################
################################
if __name__ == "__main__":
    startt = datetime.datetime.now()
    if len(sys.argv) > 1:
        try:
            table = sys.argv[1]
            if table == 'remake':
                makendc()
                makeicd9() 
                makecpt()
            elif table == 'esp_conditionndc':
                load2ndc(table)
            elif table == 'esp_conditionicd9':
                load2icd9(table)
            elif table == 'esp_conditionloinc':
                load2loinc(table)
            elif table == 'esp_cptloincmap':
                load2cptloincmap(table)
            elif table =='esp_config':
                load2config(table)
            elif table == 'esp_rule':
                load2rule(table)
            else:
                msg = 'Unknown table - %s\n' % table
                logging.info(msg)

            logging.info('Start: %s\n' %  startt)
            logging.info('End:   %s\n' % datetime.datetime.now())
        except:
            fp = StringIO.StringIO()
            traceback.print_exc(file=fp)
            message = fp.getvalue()
            logging.info(message+'\n')
    else:
        table = 'esp_rule'
        load2rule(table)  
        table = 'esp_conditionndc'
        load2ndc(table)
        table = 'esp_conditionicd9'
        load2icd9(table)
        table = 'esp_conditionloinc'
        load2loinc(table)
        table = 'esp_cptloincmap'
        load2cptloincmap(table)
        table = 'esp_config'
        load2config(table)
        
    
