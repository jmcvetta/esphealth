# incoming parser
# uses a generator for large file processing
# of delimited files

import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESPNew/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

import django, datetime
from ESP.esp.models import *

from ESP.settings import TOPDIR,LOCALSITE, getLogging,EMAILSENDER


import string,re
import shutil
import StringIO
import traceback
from django.db import connection
cursor = connection.cursor()



VERSION = '0.1'
today=datetime.datetime.now().strftime('%Y%m%d')

########For logging
iplogging= getLogging('removeDulLx.py_%s' % VERSION, debug=0)

###################################
def checkCaseLx():
    curcases = Case.objects.all()

    for c in curcases:
        curLxidlist = c.caseLxID.split(',')
        lxs = Lx.objects.filter(id__in = curLxidlist)
        
        lxdict,dupk = buildLxdict(lxs)
        for onek in dupk: ##has duplicate
            print 'CASE%s: CaseDupLxids=%s, %s\n' % (c.id, str(lxdict[onek]),c.caseDemog.id)

    
###################################
def getCaseLxid():
    curcases = Case.objects.all()
    curLxidlist=[]
    for c in curcases:
        curLxidlist=curLxidlist+c.caseLxID.split(',')
        
    caselxdict = dict(map(lambda x:(int(x),None), curLxidlist))
    return caselxdict
                      
###################################
def doDeletion(templist):
    if len(templist) >1:
        tmpstr = str(tuple(templist))
    else:
        tmpstr ='(%s)' % templist[0]
                                    
    try:
        delstmt = """delete from esp_lx where id in %s;""" % tmpstr
        cursor.execute(delstmt)
        cursor.execute("commit;")
    except:
        cursor.execute("rollback;")
        iplogging.error("ERROR: %s\n" % delstmt)


################################
def buildLxdict(lxs):
    lxdict={}
    dupk=[]
                    
    for i in lxs: ##lxs for one demog
        thisk = (i.LxMedical_Record_Number, i.LxOrder_Id_Num,i.LxTest_Code_CPT,i.LxTest_Code_CPT_mod,i.LxOrderDate,i.LxOrderType,i.LxOrdering_Provider.id,i.LxDate_of_result,i.LxHVMA_Internal_Accession_number,i.LxComponent, i.LxComponentName,i.LxTest_results,i.LxNormalAbnormal_Flag,i.LxReference_Low,i.LxReference_High,i.LxReference_Unit,i.LxTest_status,i.LxComment,i.LxImpression,i.LxLoinc)
        if lxdict.has_key(thisk): #duplicate
            lxdict[thisk].append(i.id)
            if thisk not in dupk:
                dupk.append(thisk)
        else: # no thisk
            lxdict[thisk]=[i.id]

    return (lxdict,dupk)

################################
################################
if __name__ == "__main__":

    startt = datetime.datetime.now()

    caselxdict = getCaseLxid()

    iplogging.info('Getting all demogs')
    cursor.execute("""select id from esp_demog;""")
    demogids = cursor.fetchall()

    indx=1
    iplogging.info('Total %s demogs' % len(demogids))
    delcnt=0
    for thisid, in demogids:
        lxdict={}
        dupk=[]
        removeLxs=[]
        
        lxs = Lx.objects.filter(LxPatient__id=thisid)
        lxdict,dupk = buildLxdict(lxs)

        for dk in dupk:
            duplxids = lxdict[dk]
            duplxids.sort()
            
            for onelxid in duplxids[1:]:

                if caselxdict.has_key(int(onelxid)):
                    iplogging.info('INCASE: DemogID%s,LX%s' % (thisid,onelxid))
                else:
                    removeLxs.append(int(onelxid))
        if len(removeLxs)>1:
            doDeletion(removeLxs)
            delcnt=delcnt+len(removeLxs)
            #iplogging.info('Deleted DEMOG%s, RemoveLx=%s' % (thisid, len(removeLxs)))
        
        if indx % 1000 == 0:
            iplogging.info('Processed DEMOG%s, deletedLx=%s' % (indx,delcnt))

        indx=indx+1

                 
    iplogging.info('\nDone on deleting\n')
    iplogging.shutdown()
    

