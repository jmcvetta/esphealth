import os,sys
import django
import datetime,time

import string
import traceback
import smtplib
import random

sys.path.append('../')
import settings

from esp.models import *
from django.db.models import Q




def random_string(length=10):
    chars = string.digits + string.letters
    return ''.join([random.choice(chars) for x in xrange(length)])


filenlist = ['epicmem.esp.','epicpro.esp.','epicvis.esp.','epicord.esp.','epicres.esp.','epicmed.esp.','epicimm.esp.']
FILEBASE='epic' ##'epic' or 'test'

######################################################################
def getAnotherdate(date1, dayrange):
    try:
        return datetime.date(int(date1[:4]),int(date1[4:6]),int(date1[6:8]))+datetime.timedelta(dayrange)
    except:
        print 'Error when get another date: date1=%s,range=%s' % (date1,dayrange)

    return ''

                    
######################################################################
def sendoutemail(towho=['rexua@channing.harvard.edu', 'MKLOMPAS@PARTNERS.ORG'],msg='',subject='ESP management'):
    ##send email
    sender=EMAILSENDER
    
    headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, ','.join(towho), subject)
    
    message = headers + 'on %s\n%s\n' % (datetime.datetime.now(),msg)
    mailServer = smtplib.SMTP('localhost')
    mailServer.sendmail(sender, towho, message)
    mailServer.quit()

                                
######################################################################
def getPeriod(date1,date2):
    try:
        timeperiod = datetime.date(int(date1[:4]),int(date1[4:6]),int(date1[6:8]))-datetime.date(int(date2[:4]),int(date2[4:6]),int(date2[6:8]))
        return abs(timeperiod.days)
    except:
        return 0
    

        
################################
def getfilesByDay(files):

    files.sort()
    dayfiles={}
    returndays=[]
    ##filename shoule be: epic***.esp.MMDDYY or epic***.esp.MMDDYYYY
    for f in files:
        if f.lower().find('test')!=-1 and FILEBASE!='test': ##test file
            continue
        
        mmddyy =f[f.find('esp.')+4:]
        if len(mmddyy)==6: ##DDMMYY
            newdate='20'+mmddyy[-2:]+mmddyy[:4]
        elif mmddyy.find('_')!= -1: #monthly or weekly update, formart is epic***.esp.MMDDYYYY_m or epic***.esp.MMDDYYYY_w
            newdate=mmddyy[-6:-2]+mmddyy[:4]
        else:
            newdate=mmddyy[-4:]+mmddyy[:4]

            
        if (newdate,mmddyy) not in returndays:
            returndays.append((newdate,mmddyy))

    returndays.sort(key=lambda x:x[0])
    return returndays

                                                                        
