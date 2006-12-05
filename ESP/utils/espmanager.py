import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime
from ESP.esp.models import *
from ESP.settings import TOPDIR
import localconfig 

import string
import shutil
import StringIO
import traceback
from ftplib import FTP

 
today=datetime.datetime.now().strftime('%Y%m%d')



################################
def doFTP():
    newfiles=[]
    
    ##get incoming files
    ftp = FTP('')
    ftp.login('username', 'password')
    #local site directory
    todir = os.path.join(TOPDIR, localconfig.LOCALSITE,'incomingData/')
    os.chdir(todir)
    
    #remote site directory
    ftp.cwd('ftpdirectory')
    filenames = ftp.nlst()
    for eachfile in filenames:
        #check eachfile if this has been downloaded or not
        if not DataFile.objects.filter(filename__exact=eachfile):
            ##not downloaded yet
            newfiles.append(eachfile)
            ftp.retrbinary('RETR ' + eachfile, open(eachfile, 'wb').write)
            
    ftp.quit()
    return newfiles

################################
################################
if __name__ == "__main__":
    emlogging = localconfig.getLogging('espmanager.py_v0.1', debug=0)
    
    startt = datetime.datetime.now()
    ##get files by ftp
    try:
#       newfiles=doFTP()

        ##
        newfiles=[1]
        if newfiles:
            emlogging.info('Date-%s:new data = %s\n' % (today, str(newfiles)))
            parsercmd='/usr/local/bin/python %s/incomingParser.py' % os.path.join(TOPDIR,'ESP','utils')
            os.system(parsercmd)
            emlogging.info('%s: Done on parsing' % datetime.datetime.now())

            identifycasecmd = '/usr/local/bin/python %s/identifyCases.py' % os.path.join(TOPDIR,'ESP','utils')
            os.system(identifycasecmd)
            emlogging.info('%s: Done on identifying cases' % datetime.datetime.now())

        ##always try to send msgs
        sendcmd='/usr/local/bin/python %s/messageHandler.py' % os.path.join(TOPDIR,'ESP','sendMsgs')
        os.system(sendcmd)
        emlogging.info('%s: Done on sending HL7 msgs' % datetime.datetime.now())
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        emlogging.error(message+'\n')
                                             
    emlogging.info('Start: %s' %  startt)
    emlogging.info('End:   %s\n\n' % datetime.datetime.now())
    emlogging.shutdown() 
