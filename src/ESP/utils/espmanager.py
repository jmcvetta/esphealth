import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime
from ESP.esp.models import *
from ESP.localsettings import LOCALSITE, FTP_USER, FTP_PASSWORD, FTP_SERVER
from ESP.settings import TOPDIR, CODEDIR, EMAIL_SENDER, getLogging,getJavaInfo
from ESP.utils import hl7XML
import ESP.utils.utils as utils

import string
import shutil
import StringIO
import traceback
import smtplib

from ftplib import FTP


today=datetime.datetime.now().strftime('%Y%m%d')
emlogging = getLogging('espmanager.py_v0.1', debug=0)


###################################
def sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg=''):
    ##send email
    sender=EMAIL_SENDER

    subject='ESP management'
    headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, ','.join(towho), subject)

    message = headers + 'on %s\n%s\n' % (datetime.datetime.now(),msg)
    mailServer = smtplib.SMTP('localhost')
    mailServer.sendmail(sender, towho, message)
    mailServer.quit()

                                
################################
################################
def generateHL7(hl7dir,cases):
    emlogging.info('Total cases for sending: %s\n' % len(cases))
    batchsize=30
    indx_e = 0
    today1=datetime.datetime.now().strftime('%Y%m%d%H%M')
    filecnt=1
    for i in range(len(cases)/batchsize):
        indx_s = min(i*batchsize, len(cases))
        indx_e = min((i+1)*batchsize, len(cases))
        templist = cases[indx_s:indx_e]
        filename = today1+'_%s' %filecnt
        generateOneBatch(hl7dir,templist,filename)
        filecnt=filecnt+1
        

    #get reset of cases
    if indx_e < len(cases):
        filename = today1+'_%s' %filecnt
        templist = cases[indx_e:]
        generateOneBatch(hl7dir,templist,filename)

###################################
def generateOneBatch(hl7dir,cases,filename):
    testDoc = hl7XML.hl7Batch(institutionName=LOCALSITE, nmessages=len(cases))

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
        
        emlogging.info('one batch-Adding caseID %s, icd9:%s' % (case.id,str(finalicd9)))

        wfr = CaseWorkflow.objects.filter(workflowCaseID=case,workflowState='Q').order_by('id')
        if len(wfr):
            ntestr = wfr[len(wfr)-1].workflowComment
        else:
            ntestr=''
        try:
            hl7lxids = testDoc.addCase(demog=demog,pcp=pcp,rule=rule, lx=lx, rx=rx,ex=ex,icd9=finalicd9,casenote=ntestr,caseid=case.id)
        except:
            errmsg = 'Build hl7 ERROR when running testDoc.addCase in generateOneBatch for CASE:%s' % case.id
            emlogging.error(errmsg)
            sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg=errmsg)
            continue
        
        #update caseworkflow
        case.caseWorkflow = 'S'
        case.caseSendDate=datetime.datetime.now()
        case.save()
        wfr = CaseWorkflow(workflowCaseID=case,
                           workflowDate=datetime.datetime.now().strftime("%Y-%m-%d"),
                           workflowState='S',
                           workflowChangedBy='ESP Auto',
                           workflowComment='Case sent')
        wfr.save()

        ##store in Hl7OutputFile for tracking
        trmtdt =''
        if rx:
            rxobjs = Rx.objects.filter(id__in = rx).order_by('RxOrder_Id_Num')
            if rxobjs:
                try:
                    trmtdt =rxobjs[0].RxOrderDate
                except:
                    pass

        specdate = '/'.join([lxtemp.LxOrderDate for lxtemp in Lx.objects.filter(id__in=hl7lxids).order_by('LxOrder_Id_Num')])
        hl7track = Hl7OutputFile(filename=filename, case=case,
                           demogMRN=demog.DemogMedical_Record_Number,
                           hl7comment=ntestr,
                           hl7encID=','.join([str(i).strip() for i in ex]),
                           hl7lxID=','.join([str(i).strip() for i in lx]),
                           hl7rxID=','.join([str(i).strip() for i in rx]),
                           hl7ICD9=','.join([str(i).strip() for i in finalicd9]),
                           hl7reportlxID=','.join([str(i).strip() for i in hl7lxids]),
                           hl7specdate = specdate,
                           hl7trmtDT=trmtdt)
        hl7track.save()

        
    # Print our newly created XML
    s = testDoc.renderBatch()
    f = file(hl7dir + '/hl7_%s.hl7' % filename,'w')
    emlogging.info('One HL7 file:%s' % filename)
    f.write(s)
    f.close()
                                                                                                                                                                                            
###################################
def hl7handler():
    logfile = os.path.join(TOPDIR,LOCALSITE, 'logs/messageHandler_java_%s.log' % today)
    hl7dir = os.path.join(TOPDIR,LOCALSITE,'queuedHL7Msgs/')
    if not os.path.isdir(hl7dir):
        os.mkdir(hl7dir)

    #check queued cases with status 'IN QUEUE FOR MESSAGING' in db and generate HL7 message
   # cases = TestCase.objects.filter(caseWorkflow__iexact='Q')
    cases = Case.objects.filter(caseWorkflow__iexact='Q')

    if len(cases)>0:
        generateHL7(hl7dir,cases)



    #send all HL7 messages under HL7Msgs folder
    files=os.listdir(hl7dir)
    if len(files):
        (javadir, javaclass,sendMsgcls) = getJavaInfo()
        javacmd="%s -classpath %s %s.java" % (os.path.join(javadir, 'javac'), javaclass,os.path.join(CODEDIR, 'sendMsgs', sendMsgcls))
        fin,fout = os.popen4(javacmd)

        result = fout.read()
        if string.upper(result).find('ERROR') !=-1: ##error
            emlogging.error('ERROR when running javac:%s' % result)
            emlogging.error('Compile java Exception: %s' %javacmd )

    for f in files:
        f = hl7dir + '/%s' % f
        javaruncmd = "%s -classpath %s %s %s >> %s" % (os.path.join(javadir, 'java'), javaclass, sendMsgcls, f,logfile )

        fin,fout = os.popen4(javaruncmd)
        result = fout.read()
        if string.upper(result).find('ERROR')!=-1: ##error
            emlogging.error('Run java Exception: %s' %javaruncmd )
            emlogging.error('Error when sending HL7: %s' % result)
            continue
        else:
            #move processed file to processed folder
            procdir = os.path.join(TOPDIR,LOCALSITE,'processedHL7Msgs/')
            if not os.path.isdir(procdir):
                os.mkdir(procdir)
            shutil.move(f, procdir)
                

                                                                                                                                                                                                                                                                                                

################################
def doFTP():
    newfiles=[]
    ##get incoming files
    try:
    	ftp = FTP(FTP_SERVER)
    except:
        return newfiles
    try:
        ftp.login(FTP_USER, FTP_PASSWORD)
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        errmsg = 'Error when do FTP:\n\n' + fp.getvalue()
        sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg=errmsg)
        
    #local site directory
    todir = os.path.join(TOPDIR, LOCALSITE,'incomingData/')
    os.chdir(todir)    
    #remote site directory
    ftp.cwd('ESPFiles')
    filenames = ftp.nlst()

    downloadfiles = []
    curdays = utils.getfilesByDay(filenames)
    missdays=[]
    for oneday in map(lambda x:x[1],curdays):
        for onef in utils.filenlist:
            onef = onef+oneday
            if onef not in filenames:
                missdays.append(oneday)
                break
                                                        
    for eachfile in filenames:
        error=0
        for oneday in missdays:
            if eachfile.find(oneday) <> -1:
                error=1
                break
                                            
        #check eachfile if this has been downloaded or not
        if error==0 and (eachfile.find('.esp.') <> -1) and not DataFile.objects.filter(filename__exact=eachfile) and (eachfile <> 'Processed'):
            ##not downloaded yet
            newfiles.append(eachfile)
            ftp.retrbinary('RETR ' + eachfile, open(eachfile, 'wb').write)
            
    ftp.quit()
    return newfiles


###################################
def checkPrev5days():
    """Check previous 5 days to see if there is any day missing
    if today is: 09172007, there it checks: 09152007,09142007,09132007,09122007,09112007
    """
    errordays = []
    alldays=[]
    for i in range(2,7,1):
        d = datetime.datetime.now()-datetime.timedelta(i)
        thisday = d.strftime('%m%d%Y')
        alldays.append( thisday)
        file_list = DataFile.objects.filter(filename__endswith='%s' % thisday)
        if len(file_list)==0:
            errordays.append(thisday)

    emlogging.info('Check if have files for days: %s' % str(alldays))
    
    if len(errordays)>0:
        ##there are days that are missing file
        errmsg = 'There are no files for the days: %s' % str(errordays)
        emlogging.error(errmsg)
        sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg=errmsg)

            
                         
################################
################################
if __name__ == "__main__":
    startt = datetime.datetime.now()

    ##get files by ftp
    try:
        ##
        checkPrev5days()

#        newfiles=[]
        newfiles=doFTP()
        if newfiles:
            ##1. parse data
            emlogging.info('Date-%s:new data = %s\n' % (today, str(newfiles)))
            parsercmd='%s %s/incomingParser.py' % (sys.executable,os.path.join(CODEDIR,'utils'))
            fin,fout = os.popen4(parsercmd)
            result = fout.read()
            if string.upper(result).find('ERROR') !=-1: ##error
                emlogging.error('ERROR when running incomingParser.py:%s' % result)
            else:
                emlogging.info('%s: Done on parsing' % datetime.datetime.now())

            ##2. identify cases
            identifycasecmd = '%s %s/identifyCases.py' % (sys.executable,os.path.join(CODEDIR,'utils'))
            fin,fout = os.popen4(identifycasecmd)
            result = fout.read()
            if string.upper(result).find('ERROR') !=-1: ##error
                emlogging.error('ERROR when running identifyCases.py:%s' % result)
            else:
                emlogging.info('%s: Done on identifying cases' % datetime.datetime.now())

        ##always try to send msgs
        emlogging.info('Start to generate HL7')
        hl7handler()
        emlogging.info('%s: Done on sending HL7 msgs' % datetime.datetime.now())
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        emlogging.error(message+'\n')
                                             
    emlogging.info('Start: %s' %  startt)
    emlogging.info('End:   %s\n\n' % datetime.datetime.now())
    emlogging.shutdown() 
