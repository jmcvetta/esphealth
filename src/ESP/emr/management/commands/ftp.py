import os, sys
import datetime
import string
import shutil
import StringIO
import traceback
import smtplib
import ftplib

from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.emr.models import Provenance
from ESP.utils.utils import log
from ESP.utils.utils import email_notify
from ESP.utils.utils import getfilesByDay
from ESP.utils.utils import filenlist
from ESP.settings import DATA_DIR
from ESP.settings import FTP_USER
from ESP.settings import FTP_PASSWORD
from ESP.settings import FTP_SERVER





class Command(BaseCommand):
    
    help = 'Fetch ETL files via FTP'
    
    def handle(self, *fixture_labels, **options):
        #
        # Check folder structure
        #
        dropbox = os.path.join(DATA_DIR, 'incoming') # Download files to this folder
        if not os.path.isdir(dropbox):
            try:
                os.mkdir(dropbox)
            except OSError:
                msg = 'Folder does not exist, and could not be created:\n'
                msg += '    %s\n' % dropbox
                msg += 'This is problably a permissions issue.  Please correct the problem and try again.'
                log.critical(msg)
                print >> sys.stderr, msg
                sys.exit()
        #
        # Get incoming files
        #
        newfiles=[]
        errmsg = 'FTP login to %s failed.' % FTP_SERVER
        try:
            ftp = ftplib.FTP(FTP_SERVER)
        except:
            errmsg = 'FTP login to %s failed.' % FTP_SERVER
            email_notify(subject='ESP: FTP login failed', msg=errmsg)
            log.critical(errmsg)
            return newfiles
        try:
            ftp.login(FTP_USER, FTP_PASSWORD)
        except:
            fp = StringIO.StringIO()
            #traceback.print_exc(file=fp)
            email_notify(subject='ESP: FTP login failed', msg=errmsg)
            log.warn(errmsg)        
        os.chdir(dropbox)    
        # Remote site directory
        ftp.cwd('ESPFiles')
        filenames = ftp.nlst()
        downloadfiles = []
        curdays = getfilesByDay(filenames)
        missdays=[]
        for oneday in map(lambda x:x[1],curdays):
            for onef in filenlist:
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
            # Check eachfile if this has been downloaded or not
            if error==0 \
                and (eachfile.find('.esp.') <> -1)  \
                and not Provenance.objects.filter(source__exact=eachfile)  \
                and (eachfile <> 'Processed'):
                # Not downloaded yet
                newfiles.append(eachfile)
                ftp.retrbinary('RETR ' + eachfile, open(eachfile, 'wb').write)
                log.debug('FTP - retrieved file: %s' % eachfile)
        ftp.quit()
        log.info('Retrieved %s files from FTP' % len(newfiles))
        return newfiles
    
