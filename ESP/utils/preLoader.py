##preLoader is to load some data into ESP_conditionNDC table, ESP_conditionLOINC, ESP_CPTLOINCMAP table
##
import  os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#os.environ['PYTHONPATH'] = '\home\ESP\django\ESP'
import django, datetime
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR
import localconfig 
import string
import sys
import traceback
import StringIO

logging = localconfig.getLogging('preLoader.py v0.1', debug=0)
datadir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/', 'preLoaderData/')


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
        id, cpt,cmpt,loinc =(x.strip() for x in l)
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
        id, rulename, ndc,define,send =(x.strip() for x in l)
        
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
        id, rulename, icd,define,send = (x.strip() for x in l)
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
        id, rulename, loinc,snmdposi,snmdnega,snmdinde,define,send = (x.strip() for x in l)

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
        
        if id:
            try:
                rl = Rule.objects.filter(id__exact=id)[0]
            except:
                rl = Rule()
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
        (id, t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25) = (x.strip() for x in items)
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
   
            
################################
################################
if __name__ == "__main__":
    startt = datetime.datetime.now()
    if len(sys.argv) > 1:
        try:
            table = sys.argv[1]
            if table == 'esp_conditionndc':
                load2ndc(table)
            if table == 'esp_conditionicd9':
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
                log.write(msg)

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
        
    
