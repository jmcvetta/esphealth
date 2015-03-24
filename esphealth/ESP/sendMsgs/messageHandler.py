# message handle
import os,sys
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


import django, datetime
import string
#hl7xml class is not in utils anymore.. this feature is not working
# existed in rev 1498 in the source repository, under nodis folder
from ESP.utils import hl7XML
from ESP.esp.models import *
from ESP.emr.models import Provider
from ESP.nodis.models import Case
from ESP.vaers.models import Rule
from django.db.models import Q
import ESP.utils.localconfig as localconfig
from ESP.settings import TOPDIR
import shutil
import traceback

###
today=datetime.datetime.now().strftime('%Y%m%d')

########For logging
logging = localconfig.getLogging('messageHandler.py_v0.1', debug=0)
logfile = os.path.join(TOPDIR,localconfig.LOCALSITE, 'logs/messageHandler_java_%s.log' % today)

##############



################################
################################
def generateHL7(hl7dir,cases):
    logging.info('Total cases: %s\n' % len(cases))
    batchsize=30
    indx_e = 0
    for i in range(len(cases)/batchsize):
        indx_s = min(i*batchsize, len(cases))
        indx_e = min((i+1)*batchsize, len(cases))
        templist = cases[indx_s:indx_e]
        generateOneBatch(hl7dir,templist)

    #get reset of cases
    if indx_e < len(cases):
        templist = cases[indx_e:]
        generateOneBatch(hl7dir,templist)
        


#
# NOTE: This method is probably cruft - certainly it hasn't been used in quite a 
# while since the Case member names are from ESP 1.0.
# TODO issue 337 fix me is using old  models prior to 3
#
def generateOneBatch(hl7dir,cases):
    testDoc = hl7XML.hl7Batch(institutionName=localconfig.LOCALSITE, nmessages=len(cases))
    today1=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    for case in cases:
        demog = Demog.objects.filter(id__exact=case.caseDemog.id)[0]
        pcp = Provider.objects.filter(id__exact=case.caseProvider.id)[0]
        rule = Rule.objects.filter(id__exact=case.caseRule.id)[0]

        ex = string.split(case.caseEncID,',') 
        rx = string.split(case.caseRxID,',')
        lx = string.split(case.caseLxID,',')
        casedx_code = string.split(case.casedx_code,',')
        finaldx_code=[]
        for i in casedx_code:
            i = i.strip()
            if not i: continue
            oneenc = string.split(i, ' ')
            for j in oneenc:
                if j not in finaldx_code: finaldx_code.append(j)
        if '' in ex: ex.remove('')
        if '' in rx: rx.remove('')
        if '' in lx: lx.remove('')
        logging.info('Adding caseID %s, dx codes:%s' % (case.id,str(finaldx_code)))
        testDoc.addCase(demog=demog,pcp=pcp,rule=rule, lx=lx, rx=rx,ex=ex,dx_code=finaldx_code)

        #update caseworkflow         
        case.caseWorkflow = 'S'
        case.caseSendDate=datetime.datetime.now()
        case.save()
        
    # Print our newly created XML
    s = testDoc.renderBatch()
    f = file(hl7dir + '/hl7_%s.hl7' % today1,'w')
    f.write(s)
    f.close()
    # print s


################################
################################
if __name__ == "__main__":
  
    hl7dir = os.path.join(TOPDIR,localconfig.LOCALSITE,'queuedHL7Msgs/')
    if not os.path.isdir(hl7dir):
        os.mkdir(hl7dir)
    #check queued cases with status 'IN QUEUE FOR MESSAGING' in db and generate HL7 message
    cases = Case.objects.filter(caseWorkflow__iexact='Q')
    if len(cases)>0:
        generateHL7(hl7dir,cases)


    #send all HL7 messages under HL7Msgs folder
    files=os.listdir(hl7dir)
    if len(files):
        (javadir, javaclass,sendMsgcls) = localconfig.getJavaInfo()
        javacmd="%s -classpath %s %s.java" % (os.path.join(javadir, 'javac'), javaclass,sendMsgcls)

        try:
            fin,fout = os.popen4(javacmd)
            result = fout.read()
        except:
            logging.error('Compile java Exception: %s' %javacmd )
            sys.exit(1)

    
    for f in files:
        
        f = hl7dir + '/%s' % f
        #javacmd="/home/ESP/ESP/sendMsgs/sendMsg.bat %s" % f
        javaruncmd = "%s -classpath %s %s %s >> %s" % (os.path.join(javadir, 'java'), javaclass, sendMsgcls, f,logfile )
        logging.info("Runs java command: %s" % javaruncmd)
        try:
            fin,fout = os.popen4(javaruncmd)
            result = fout.read()
            if string.upper(result).find('ERROR')!=-1: ##error
                logging.error('Error when sending HL7: %s' % result)
            else:
                #move processed file to processed folder
                procdir = os.path.join(TOPDIR,localconfig.LOCALSITE,'processedHL7Msgs/')
                if not os.path.isdir(procdir):
                    os.mkdir(procdir)
                shutil.move(f, procdir)
                
        except:
            logging.error('Run java Exception' )
            continue


  
