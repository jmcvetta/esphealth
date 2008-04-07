import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESPNew/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR,LOCALSITE, getLogging,EMAILSENDER


import string,re,copy
import shutil
import StringIO
import traceback
import smtplib



def getAllFiles(incomdir):
    dirs = os.listdir(incomdir)
    dirs.sort()
    for d in dirs:
        curdir = os.path.join(incomdir,d)
        if os.path.isdir(curdir): #is a directory
            getAllFiles(curdir)
        else: ##get a file
            filename = d
            f = file(curdir)
            linenum = len(f.readlines())-1
            f.close()
            finDB = DataFile.objects.filter(filename=filename)
            if finDB:
                print '%s IN DB' % filename
                dataf = finDB[0]
                dataf.numrecords = linenum
                #dataf.datedownloaded = dataf.datedownloaded
                dataf.save()
            else:
                print '%s not in DB, create a new one' % filename
                dataf = DataFile()
                dataf.filename=filename
                dataf.numrecords = linenum
                dataf.save()
                            

                    
###############################
################################
if __name__ == "__main__":
    try:
        incomdir = os.path.join(TOPDIR, LOCALSITE,'processedData/')

        getAllFiles(incomdir)
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        print message


                                            
