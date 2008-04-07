import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESPNew/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR,LOCALSITE, getLogging,EMAILSENDER

from django.db import connection
cursor = connection.cursor()
        
import string,re,copy
import shutil
import StringIO
import traceback
import smtplib
import time

###################################
def buildLabCompt(query=0):
    cmptname_dict={}
    stmt = """select distinct upper(LxComponentName), LxTest_Code_CPT ,LxComponent from esp_lx where LxComponentName!= ''"""
    cursor.execute(stmt)
    res = cursor.fetchall()
    print 'Total records = ', len(res)
    inststmt ="""insert into esp_labcomponent
                    set componentName=%s,  CPT=%s, CPTCompt=%s, lastUpDate=sysdate(), createdDate=sysdate()"""
    for cmpname, cpt, cmpt in res:
        if query==1:
            stmt = """select id from esp_labcomponent where componentName = %s""" 
            cursor.execute(stmt, (cmpname,))
            labcmptid  = cursor.fetchall()
            if not labcmptid :
                try:
                    cursor.execute(inststmt, (cmpname,cpt,cmpt))
                    labcmptid = cursor.lastrowid
                except:
                    print 'Error', inststmt
                    sys.exit(1)
            else:
                labcmptid =labcmptid[0][0]
        elif query==0:
            try:
                cursor.execute(inststmt, (cmpname,cpt,cmpt))
                labcmptid = cursor.lastrowid
            except:
                print 'Error', inststmt
                sys.exit(1)
                                                                                                    
            
        cmptname_dict[cmpname] = labcmptid
    return cmptname_dict

###############################
################################
if __name__ == "__main__":
    try:
        cmptname_dict = buildLabCompt()
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        print message


                                            
