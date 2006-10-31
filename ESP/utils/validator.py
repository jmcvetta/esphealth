import  os
##os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
##os.environ['PYTHONPATH'] = 'C:\django\ESP'
import datetime
from ESP.settings import TOPDIR
import localconfig 

import string,re
import sys
#import shutil
import StringIO
import traceback
import logging



################################
def validateOnefile(incomdir, fname,delimiternum,needidcolumn,datecolumn=[],required=[]):
    returnd={}
    errors=0
    try:
        lines= file(incomdir+fname).readlines()
    except:
        logging.error('Valitator - Can not read file:%s%s\n' % (incomdir,fname))
        return (errors, returnd)
    
    for l in lines[:-1]:
        if not string.strip(l): continue
        
        linenum=lines.index(l)+1
        fnum=len(re.findall("\^",l))
        if int(delimiternum) != fnum:
            msg ='Valitator - %s: wrong number of delimiter, should be %s, in file=%s\n=========LINE%s: %s\n' % (fname,delimiternum,fnum,linenum,l)
            errors = 1
            logging.error(msg)
          
        items = l.split('^')
        for r in required:
            if not string.strip(items[r]):
                col = r+1
                msg = 'Valitator - %s, LINE%s: Empty for Required filed in column %s\n' % (fname,linenum, col )
                errors = 1
                logging.error(msg)
        for n in needidcolumn:
            returnd.setdefault(n,[]).append(items[n])
        for d in datecolumn:
            if items[d] and len(items[d])!=8 or re.search('\D', items[d]):
                msg = 'Valitator - %s: wrong Date format: %s\n=========LINE%s: %s\n'  % (fname,items[d],linenum, l)
                errors = 1
                logging.error(msg)
               
    return (errors,returnd)



################################
def checkID(pids, provids, vispids,visprovids,demogf,providerf,visf):

 
    msgs=[]
    errors = 0
    for i in vispids:
        if i not in pids:
            msg = 'Valitator - %s: Patient %s not in mem file: %s\n' % (visf,i,demogf)            
            if msg not in msgs: msgs.append(msg)

   
    for i in visprovids:
        if i and i not in provids:
            msg = 'Valitator - %s: Provider %s not in prov file: %s\n' % (visf,i,providerf)
            if msg not in msgs: msgs.append(msg)
            
    for m in msgs:
        errors = 1
        logging.error(m)
    return errors
        
################################
def validateOneday(incomdir, oneday):
    """validate one day files
    """
    finalerr=0
    #patient
    demogf = 'epicmem.esp.'+oneday
    logging.info('Valitator - Process %s' % demogf)
    (err,tempd) = validateOnefile(incomdir,demogf,24,[0],datecolumn=[14],required=[0,1])
    pids = tempd[0]
    if err:
        finalerr = 1
        
    #provider
    providerf = 'epicpro.esp.'+oneday
    logging.info('Valitator -Process %s' % providerf)
    err,tempd = validateOnefile(incomdir,providerf,13,[0],required=[0] )
    provids= tempd[0]
    if err:
        finalerr = 1
        
    #encounter
    visf = 'epicvis.esp.'+oneday
    logging.info('Valitator -Process %s' % visf)
    err,tempd = validateOnefile(incomdir,visf,13,[0,6], datecolumn=[3,5,10],required=[0,1])
    if tempd:
       err2 = checkID(pids, provids, tempd[0],tempd[6],demogf,providerf,visf)
    if err or err2:
        finalerr = 1
    #lxres
    lxresf = 'epicres.esp.'+oneday
    logging.info('Valitator - Process %s' % lxresf)
    err, tempd = validateOnefile(incomdir,lxresf,18,[0,5],datecolumn=[3,4],required=[0,1])
    if tempd:
        err2 = checkID(pids, provids, tempd[0],tempd[5],demogf,providerf,lxresf)
    if err or err2:
        finalerr = 1

    #med
    medf = 'epicmed.esp.'+oneday
    logging.info('Valitator - Process %s' % medf)
    err,tempd = validateOnefile(incomdir,medf,13,[0,3],datecolumn=[4,11,12],required=[0,1])
    if tempd:
       err2 = checkID(pids, provids, tempd[0],tempd[3],demogf,providerf,medf)
    if err or err2:
        finalerr = 1
    #imm
    mmf = 'epicimm.esp.'+oneday
    logging.info('Valitator - Process %s' % mmf)
    err,tempd = validateOnefile(incomdir,mmf,7,[0],datecolumn=[3])
    #if tempd:
    #    err2 = checkID(pids, provids, tempd[0],[],demogf,providerf,mmf)
    #if err or err2:
    #    finalerr = 1
    return finalerr

################################
def getfilesByDay(incomdir):
    files=os.listdir(incomdir)
    files.sort()
    dayfiles={}
    for f in files:
        if dayfiles.has_key(f[-6:]):
            dayfiles[f[-6:]].append(f)
        else:
            dayfiles[f[-6:]] = [f]

    days = dayfiles.keys()
    days.sort()
   
    return days


        
################################
################################
if __name__ == "__main__":
    logging = localconfig.getLogging('validator.py v0.1', debug=0)
    try: 
        startt = datetime.datetime.now()
       
        ##get incoming files
        incomdir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/','realData/real_20061026/')
        days = getfilesByDay(incomdir)
  
        for oneday in days:
            logging.info('Processing day: %s' % oneday)
            finalerr = validateOneday(incomdir, oneday)
            logging.info('DONE on validating day: %s, result=%s' % (oneday,finalerr))
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        logging.error(message)
    logging.shutdown() 
