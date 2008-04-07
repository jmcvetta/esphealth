import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESPNew/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime,time
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import *


import string
import traceback
import smtplib
import datetime

###################################
###################################
def sendoutemail(towho=['rexua@channing.harvard.edu', 'MKLOMPAS@PARTNERS.ORG'],msg='',subject='ESP management'):
    ##send email
    sender=EMAILSENDER
    
    headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, ','.join(towho), subject)
    
    message = headers + 'on %s\n%s\n' % (datetime.datetime.now(),msg)
    mailServer = smtplib.SMTP('localhost')
    mailServer.sendmail(sender, towho, message)
    mailServer.quit()

                                
###################################
###################################
def getPeriod(date1,date2):
    try:
        timeperiod = datetime.date(int(date1[:4]),int(date1[4:6]),int(date1[6:8]))-datetime.date(int(date2[:4]),int(date2[4:6]),int(date2[6:8]))
        return abs(timeperiod.days)
    except:
        return 0
    

        
