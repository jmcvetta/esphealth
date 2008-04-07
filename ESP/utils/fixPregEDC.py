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
import datetime

iplogging= getLogging('fixPregEDC.py', debug=0)



###################################
def getPeriod(date1,date2):
    timeperiod = datetime.date(int(date1[:4]),int(date1[4:6]),int(date1[6:8]))-datetime.date(int(date2[:4]),int(date2[4:6]),int(date2[6:8]))
    return abs(timeperiod.days)


                    
###############################

def splitfile(fname=None,delim='^',validate=False):
    """ generator to return delim split lines
    ross lazarus nov 21 2006
    """
    f = file(fname,'r')
    r = []
    more = 1
    n = 0
    while more:
        try:
            r = f.next()
        except:
            more = 0
            raise StopIteration
        n += 1

        if not validate:
            ll = r.split(delim) # use original file.next!
            r=[re.sub("'", "''", x.strip()) for x in ll]
            
            
        if n % 1000000 == 0:
            iplogging.info('At line %d in file %s' % (n,fname))

        if validate or len(r) > 2: # ignore lines without delimiters if not validation phase
            yield (r, n)
                       
                                                                                                            
###################################
def getAllFiles(incomdir):
    dirs = os.listdir(incomdir)
    dirs.sort()
    for d in dirs:
        curdir = os.path.join(incomdir,d)
        if os.path.isdir(curdir): #is a directory
            getAllFiles(curdir)
        else: ##get a file
            filename = d
            if string.find(filename, 'vis')==-1: ##Thi is not an enc file
                continue

            ##Enc file
            iplogging.info("Process File=%s" % curdir)
            for (items, linenum) in splitfile(curdir,'^'):
                if not items or items[0]=='CONTROL TOTALS':
                    filelines = linenum
                    continue
                try:
                    pid,mrn,encid,encd,close,closed,phy,deptid,dept,enctp,edc,temp,cpt,weight,height,bpsys,bpdias,o2stat,peakflow,icd9  = items #[x.strip() for x in items]
                except:
                    continue
                
                encdb = Enc.objects.filter(EncPatient__DemogPatient_Identifier__exact=pid,EncEncounter_ID__exact=encid)
                try:
                    enc = encdb[0]
                except:
                    iplogging.error("***Not found in DB: MRN=%s, EncID=%s" % (mrn,encid))
                    continue

                if edc=='' and enc.EncEDC =='':
                    ##do nothing
                    pass
                elif edc=='' and enc.EncEDC !='': 
                    if getPeriod(encd, enc.EncEDC)>280:
                        iplogging.info("EDCFile is Null: espId=%s, EncID=%s, Encdate=%s, edcDB=%s*edcfile=%s-->%s" % (enc.id,enc.EncEncounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc,edc) )
                        enc.EncEDC=edc
                        enc.EncPregnancy_Status=''
                        enc.save()
                                                                        
                elif edc!='' and enc.EncEDC=='':
                    if getPeriod(encd, edc)<=280:
                        iplogging.info("EDCDB is Null: espId=%s, EncID=%s, Encdate=%s, edcDB=%s*edcfile=%s-->%s" % (enc.id,enc.EncEncounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc,edc) )
                        enc.EncEDC=edc
                        enc.EncPregnancy_Status='Y'
                        enc.save()
                                                                        
                elif edc!='' and enc.EncEDC!='':
                    if enc.EncEDC!=edc:
                        if getPeriod(encd, edc)>280 and  getPeriod(encd, enc.EncEDC)>280:
                            newedc=''
                            newst = ''
                        elif  getPeriod(encd, edc)<=280 and getPeriod(encd, enc.EncEDC)>280:
                            newedc = edc
                            newst='Y'
                        elif getPeriod(encd, edc)>280 and getPeriod(encd, enc.EncEDC)<=280:
                            newedc =enc.EncEDC
                            newst='Y'
                        elif getPeriod(encd, edc)<=280 and getPeriod(encd, enc.EncEDC)<=280:
                            newedc =edc
                            newst='Y'
                                                    
                        else: ##Should no this case also
                            iplogging.error("DIFF STRANGE: enc.id=%s, enc.encID=%s, enc.date=%s, enc.EDC=%s*****edc=%s" % (enc.id,enc.Encounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc) )

                        iplogging.info("DIFF: espId=%s, EncID=%s, Encdate=%s, edcDB=%s*edcfile=%s-->%s" % (enc.id,enc.EncEncounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc,newedc) )
                        enc.EncEDC=newedc
                        enc.EncPregnancy_Status=newst
                        enc.save()
                                                                        
                else: ##Should not have this case
                    iplogging.error("STRANGE: enc.id=%s, enc.encID=%s, enc.date=%s, enc.EDC=%s*****edc=%s" % (enc.id,enc.Encounter_ID, enc.EncEncounter_Date, enc.EncEDC, edc) )
                    
                    
                                                                                      
                        
                        
                    
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


                                            
