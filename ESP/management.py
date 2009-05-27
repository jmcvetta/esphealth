import datetime,csv,sys,os
# for esphealth testing sys.path.append('/home/ESPnew')
import string
import settings
sys.path.insert(0, settings.TOPDIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

from django.dispatch import dispatcher
from django.db.models import signals

import ESP.settings as settings
from ESP.esp.models import *
from ESP.esp import models as espmodel


##################################
def makeicd9():
    """ found these codes somewhere or other..."""
    codes = []
    n = 1
    from ESP.utils.ESPicd9 import icd
    for line in icd.split('\n'):
        if n % 1000 == 0:
            print n,'icd done'
        n += 1
        line = line.replace("'",'')
        code,trans = line.split('\t')
        code = '%s.%s' % (code[:3],code[3:]) # make all 3 digit decimals
        c = icd9(icd9Code=code,icd9Long=trans.capitalize())
        c.save()
        
#####################################
def makendc():
    """ found these codes somewhere http://www.fda.gov/cder/ndc/"""
    f = file(settings.CODEDIR+'/utils/ndc_codes.txt','r')
    foo = f.next() # lose header
    n = 1
    for line in f:
        if n % 1000 == 0:
            print n,'ndc done'
        n += 1
        lbl = line[8:14]
        prod = line[15:19]
        trade = line[44:].strip()
        newn = ndc(ndcLbl=lbl.capitalize(),ndcProd=prod.capitalize(),ndcTrade=trade.capitalize())
        newn.save()

##################################
def makecpt():
    """found these at www.tricare.osd.mil/tai/downloads/cpt_codes.xls
    """
    reader = csv.reader(open(settings.CODEDIR+'/utils/cpt_codes.csv','rb'),dialect='excel')
    header = reader.next()
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    i = 0
    for ll in reader: # here be dragons. lots of "" at the 4th pos - but some other subtle crap too...
        code,long,short = ll[:3] # good thing it doesn't really matter..
        i += 1
        if i % 1000 == 0:
            print i,'cpt done'
        long = long.replace('"','')
        short = short.replace('"','')
        c = cpt(cptCode=code,cptLong=long.capitalize(),cptShort=short.capitalize(),cptLastedit=now)
        c.save()
        
###################################
def cleanup():
    from django.db import connection
    cursor = connection.cursor()
    sqlist = []
    sqlist.append('delete from esp_ndc;')
    sqlist.append('delete from esp_icd9;')
    sqlist.append('delete from esp_cpt;')
    
#    sqlist.append('commit;')
    for sql in sqlist:
        print sql
        try:
            cursor.execute(sql)
        except:
            print 'Error executing %s' % sql



################################
def my_syncdb_func(sender,**kwargs):
    """To load CPT/ICD9/NDC for displaying purpose on case detail page
    """

    if settings.SYNC_PRE:
        print 'syncdb signal for %s - installing initial data' % sender
        preloadcmd='%s %s/preLoader.py' % (sys.executable,os.path.join(settings.CODEDIR,'utils'))
        os.system(preloadcmd)
        print  'PreLoad Done'
        
        if icd9.objects.count()>0 and cpt.objects.count()>0 and ndc.objects.count()>0:
            print 'No need to load data into CPT/ICD9/NDC'
        else: ##cleanup and reload again
            cleanup()
            makendc()
            makeicd9()
            makecpt()

        ##run makefakefile
        if settings.RUNFAKEDATA:
            print 'Generate Faked data'
            fakecmd='%s %s/makeFakeFiles.py' % (sys.executable,os.path.join(settings.CODEDIR,'utils'))
            fin,fout = os.popen4(fakecmd)
            result = fout.read()
            if string.upper(result).find('ERROR') !=-1: ##error
                print ('ERROR when running makeFakeFiles.py:%s' % result)
    else:
        print 'syncdb signal for %s - no action' % sender

                                             

        

######################################
signals.post_syncdb.connect(my_syncdb_func) 
