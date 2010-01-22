import os,sys

import datetime
from ESP.localsettings import LOCALSITE
from ESP.settings import FTP_USER, FTP_PASSWORD, FTP_SERVER
from ESP.settings import TOPDIR, CODEDIR, EMAIL_SENDER, getJavaInfo
from ESP.utils import utils


import string
import shutil
import StringIO
import traceback
import smtplib

from ftplib import FTP


today=datetime.datetime.now().strftime('%Y%m%d')
emlogging = utils.log

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
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        emlogging.error(message+'\n')
                                             
    emlogging.info('Start: %s' %  startt)
    emlogging.info('End:   %s\n\n' % datetime.datetime.now())
    emlogging.shutdown() 
