# message handle

import django, datetime
from ESP.utils import hl7XML
from ESP.esp.models import *
from django.db.models import Q
import ESP.utils.localconfig as localconfig
from ESP.settings import TOPDIR
import os,sys
import shutil
import traceback,logging

###
today=datetime.datetime.now().strftime('%Y%m%d')

########For logging
logging = localconfig.getLogging('messageHandler.py v0.1', debug=0)
##############



################################
################################
def generateHL7(hl7dir,cases):
    logging.info('Total cases: %s\n' % len(cases))
    testDoc = hl7XML.hl7Batch(institutionName=localconfig.LOCALSITE, nmessages=len(cases))
    for case in cases:
        demog = Demog.objects.filter(id__exact=case.caseDemog.id)[0]
        pcp = Provider.objects.filter(id__exact=case.caseProvider.id)[0]
        rule = Rule.objects.filter(id__exact=case.caseRule.id)[0]

        ex = string.split(case.caseEncID,',') 
        rx = string.split(case.caseRxID,',')
        lx = string.split(case.caseLxID,',')
        caseicd9 = string.split(case.caseICD9,',')
        finalicd9=[]
        for i in caseicd9:
            i = i.strip()
            if not i: continue
            oneenc = string.split(i, ' ')
            for j in oneenc:
                if j not in finalicd9: finalicd9.append(j)
        if '' in ex: ex.remove('')
        if '' in rx: rx.remove('')
        if '' in lx: lx.remove('')
        logging.info('Adding caseID %s, icd9:%s' % (case.id,str(finalicd9)))
        testDoc.addCase(demog=demog,pcp=pcp,rule=rule, lx=lx, rx=rx,ex=ex,icd9=finalicd9)

        #update caseworkflow         
        case.caseWorkflow = 'S'
        case.save()
        
    # Print our newly created XML
    today1=datetime.datetime.now().strftime('%Y%m%d%H%M')
    s = testDoc.renderBatch()
    f = file(hl7dir + '/hl7_%s.hl7' % today1,'w')
    f.write(s)
    f.close()
   # print s


################################
################################
if __name__ == "__main__":
  
    hl7dir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/','queuedHL7Msgs/')
    if not os.path.isdir(hl7dir):
        os.mkdir(hl7dir)
    #check queued cases with status 'IN QUEUE FOR MESSAGING' in db and generate HL7 message
    cases = Case.objects.filter(caseWorkflow__iexact='Q')
    if len(cases)>0:
        generateHL7(hl7dir,cases)
  #  sys.exit(1) 

    #send all HL7 messages under HL7Msgs folder
    files=os.listdir(hl7dir)
    for f in files:
        
        f = hl7dir + '/%s' % f
        javacmd="sendMsg.bat %s" % f
        logging.info("Runs java command: %s" % javacmd)
        try:
            os.system(javacmd)
        except:
            logging.error('Run java Exception' )
            traceback.print_exc()

        #move processed file to processed folder
        procdir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/','processedHL7Msgs/')
        if not os.path.isdir(procdir):
            os.mkdir(procdir)

        shutil.move(f, procdir)
  