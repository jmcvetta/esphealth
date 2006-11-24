import os,sys
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'
import datetime
from ESP.settings import TOPDIR
import localconfig 

import string,re
import StringIO
import traceback
import logging


###############################

class splitfile(file):
    """ extend file class to return delim split lines
    ross lazarus nov 21 2006
    """

    def __init__(self,fname):
        self.fname = fname
        self.n = 0
        file.__init__(self,fname,'r')
        
    def next(self):
        """ override file.next()
        """
        r = []
        while len(r) < 2: # want a line with the delim
            r = file.next(self)
            self.n += 1
            if self.n % 10000 == 0:
                logging.info('At line %d in file %s' % (self.n,self.fname))
        return (r,self.n)

                                                                                                                            
################################
def validateOnefile(incomdir, fname,delimiternum,needidcolumn,datecolumn=[],required=[]):
    returnd={}
    errors=0
    fname = os.path.join(incomdir,'%s' % fname)
    try:
        f = splitfile(fname)
    except:
        logging.error('Validator - Can not read file:%s\n' % (fname))
        return (errors, returnd)
                    
    for (l,linenum) in f:
        if not string.strip(l) or l.find('CONTROL TOTALS')>-1:
            continue
        
        fnum=len(re.findall("\^",l))
        if int(delimiternum) != fnum:
            msg ='Validator - %s: wrong number of delimiter, should be %s, in file=%s\n=========LINE%s: %s\n' % (fname,delimiternum,fnum,linenum,l)
            errors = 1
            logging.error(msg)
          
        items = l.split('^')
        if items == ['']* (int(delimiternum)+1):
            continue
        
        for r in required:
            if not string.strip(items[r]):
                col = r+1
                msg = 'Validator - %s, LINE%s: Empty for Required filed in column %s\n' % (fname,linenum, col )
                errors = 1
                logging.error(msg)
        for n in needidcolumn:
            returnd.setdefault(n,[]).append(items[n])
        for d in datecolumn:
            if items[d] and len(items[d])!=8 or re.search('\D', items[d]):
                msg = 'Validator - %s: wrong Date format: %s\n=========LINE%s: %s\n'  % (fname,items[d],linenum, l)
                errors = 1
                logging.error(msg)
               
    return (errors,returnd)



################################
def checkID(pids, provids, vispids,visprovids,demogf,providerf,visf):

 
    msgs=[]
    errors = 0
    for i in vispids:
        if i not in pids:
            msg = 'Validator - %s: Patient %s not in mem file: %s\n' % (visf,i,demogf)            
            if msg not in msgs: msgs.append(msg)

   
    for i in visprovids:
        if i and i not in provids:
            msg = 'Validator - %s: Provider %s not in prov file: %s\n' % (visf,i,providerf)
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
    logging.info('Validator - Process %s' % demogf)
    (err,tempd) = validateOnefile(incomdir,demogf,24,[0],datecolumn=[14],required=[0,1])
    pids = tempd[0]
    if err:
        finalerr = 1
        
    #provider
    providerf = 'epicpro.esp.'+oneday
    logging.info('Validator -Process %s' % providerf)
    err,tempd = validateOnefile(incomdir,providerf,13,[0],required=[0] )
    provids= tempd[0]
    if err:
        finalerr = 1
        
    #encounter
    visf = 'epicvis.esp.'+oneday
    logging.info('Validator -Process %s' % visf)
    err,tempd = validateOnefile(incomdir,visf,13,[0,6], datecolumn=[3,5,10],required=[0,1])
    if tempd:
       err2 = checkID(pids, provids, tempd[0],tempd[6],demogf,providerf,visf)
    if err or err2:
        finalerr = 1

    #lxord
    lxordf = 'epicord.esp.'+oneday
    logging.info('Validator - Process %s' % lxordf)
    err, tempd = validateOnefile(incomdir,lxordf,8,[0,8],datecolumn=[6],required=[0,1])
    if tempd:
        err2 = checkID(pids, provids, tempd[0],tempd[8],demogf,providerf,lxordf)
    if err or err2:
        finalerr = 1
                                        
    #lxres
    lxresf = 'epicres.esp.'+oneday
    logging.info('Validator - Process %s' % lxresf)
    err, tempd = validateOnefile(incomdir,lxresf,18,[0,5],datecolumn=[3,4],required=[0,1])
    if tempd:
        err2 = checkID(pids, provids, tempd[0],tempd[5],demogf,providerf,lxresf)
    if err or err2:
        finalerr = 1

    #med
    medf = 'epicmed.esp.'+oneday
    logging.info('Validator - Process %s' % medf)
    err,tempd = validateOnefile(incomdir,medf,13,[0,3],datecolumn=[4,11,12],required=[0,1])
    if tempd:
       err2 = checkID(pids, provids, tempd[0],tempd[3],demogf,providerf,medf)
    if err or err2:
        finalerr = 1
    #imm
    mmf = 'epicimm.esp.'+oneday
    logging.info('Validator - Process %s' % mmf)
    err,tempd = validateOnefile(incomdir,mmf,7,[0],datecolumn=[3])
    if tempd:
        err2 = checkID(pids, provids, tempd[0],[],demogf,providerf,mmf)
    if err or err2:
        finalerr = 1
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
    logging = localconfig.getLogging('validator.py_v0.1', debug=0)
    try: 
        startt = datetime.datetime.now()
       
        ##get incoming files
        incomdir = os.path.join(TOPDIR,localconfig.LOCALSITE,'incomingData/')
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
