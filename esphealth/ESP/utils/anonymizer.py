
from ESP.settings import TOPDIR
import localconfig
import validator
import string
import os
import shutil
import StringIO
import traceback
#TODO this is not working because fakename is not in the code.
from makeESPdata import fakename
import random,datetime

logging = localconfig.getLogging('anonymizer.py v0.1', debug=0)
provdict={}
demogdict={}

###############################
def getlines(fname):
    logging.info('Process %s\n' % fname)
    lines = file(fname).readlines()
   # print file,len(lines)
    retunl = [x.split('^') for x in lines[:-1] if len(x.split('^')) >= 1]
    return retunl


################################
def parseProvider(fname,fh):
    indx = 1
    
    for items in getlines(fname):
        phy, lname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone = items

        #replace phy, names
        fname,sname=fakename()
        newpid = '%s_%s_%d' % (sname[:3],fname[:3],indx)
        provdict[phy]=newpid
        
        newl = "^".join((newpid, sname,fname,mname,title,depid,depname,addr1,addr2,city,state,zip,phonearea,phone))
        fh.write(newl+"\n")
        indx=indx+1
       


################################
def parseDemog(fname,fh):
    for items in getlines(fname):
        #print items
        pid,mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,phy,mari,religion,alias,mom,death=items

        if phy:
            try:  
                newphy = provdict[phy]
            except:
                print 'NO provider in Demog: %s' % phy
                newphy=''
        else:
            newphy = phy
            
        fname,lname=fakename()
        newpid = '%09d' % random.randint(1,999999999)
        ssn = '%03d-%02d-%04d' % (random.randint(1,999),random.randint(1,99),random.randint(1,9999))
        mrn = '%09d' % random.randint(1,999999999)
        dob =dob[:4]+'0101'
        addr1 = 'Address 1'
        
        demogdict[pid]=(newpid,mrn)
        newl = "^".join((newpid,mrn,lname,fname,mname,addr1,addr2,city,state,zip,cty,phonearea,phone,ext,dob,gender,race,lang,ssn,newphy,mari,religion,alias,mom,death))
        fh.write(newl+"\n")
        
################################
def parseEnc(fname,fh):
    for items in getlines(fname):
        #print items 
        pid,mrn,encid,encd,close,closed,phy,deptid,dept,enctp,edc,temp,cpt,dx_code=items
        newpid, newmrn, newphy = getfakeinfo(pid, phy)
        if newpid=='':
            print 'NO patient in Enc: %s' % pid
            continue
               
        newl = "^".join((newpid,newmrn,encid,encd,close,closed,newphy,deptid,dept,enctp,edc,temp,cpt,dx_code))
        fh.write(newl+"\n")

           
################################
def parseLxRes(fname,fh):
 
    for items in getlines(fname):
        try:
            pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,comp,compname,res,normalf,refl,refh,refu,status,note,accessnum,impre = items
        except:
            try:
                pid,mrn,orderid,orderd,resd,phy,ordertp,cpt,note,access,impre = items
                comp=compname=res=normalf=refl=refh=refu=status=''
            except:
                logging.error('In LXRES: %s\n' % str(items))
                continue

        newpid, newmrn, newphy = getfakeinfo(pid, phy)
        if newpid=='':
            print 'NO patient in LxREs: %s' % pid
            continue
        newl = "^".join((newpid,newmrn,orderid,orderd,resd,newphy,ordertp,cpt,comp,compname,res,normalf,refl,refh,refu,status,note,accessnum,impre))
        fh.write(newl+"\n")
         
           
################################
def parseRx(fname,fh):
    for items in getlines(fname):
        try:
            pid,mrn,orderid,phy, orderd,status, meddirect,ndc,med,qua,ref,sdate,edate=items
            route=''
        except:
            pid,mrn,orderid,phy, orderd,status, meddirect,ndc,med,qua,ref,sdate,edate,route=items
           
        newpid, newmrn, newphy = getfakeinfo(pid, phy)
        if newpid=='':
            print 'NO patient in Rx: %s' % pid
            continue
        newl = "^".join((newpid,newmrn,orderid,newphy, orderd,status, meddirect,ndc,med,qua,ref,sdate,edate,route))
        fh.write(newl+"\n")
 

###################################          
def getfakeinfo(pid, phy):
    try:
        newpid,newmrn = demogdict[pid]              
    except:
        print 'NO patient for pid: %s' % pid
        newpid=''
        newmrn=''
        
    if phy: 
        try:
            newphy = provdict[phy]   
        except:
            print 'NO provider for providercode: %s' % phy
            newphy=''
    else:
        newphy = phy

    return (newpid, newmrn, newphy)

        
    
################################
################################
if __name__ == "__main__":
    try: 
        startt = datetime.datetime.now()
       
        ##get incoming files
        incomdir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/','realData/real_20061026/')
        outdir = os.path.join(TOPDIR+localconfig.LOCALSITE+'/','incomingData/')
        days = validator.getfilesByDay(incomdir)
        control='CONTROL TOTALS^epicmem^09/01/2006^09/30/2006^17152^10/16/06 13:49^10/16/06 14:03^0h13m21s\n'
        for oneday in days:
            logging.info('Process %s' % oneday)
            err = validator.validateOneday(incomdir,oneday)
            if err: #not OK
                logging.info("Files for day %s not OK, reject to process\n" % oneday)
            else: #OK
                f = 'epicpro.esp.'+oneday
                fh = open(outdir + f, 'w')
                parseProvider(incomdir + f,fh)
                fh.write(control)
                fh.close()

                f = 'epicmem.esp.'+oneday 
                fh = open(outdir + f, 'w')
                parseDemog(incomdir + f,fh)
                fh.write(control)
                fh.close()

                f = 'epicvis.esp.'+oneday   
                fh = open(outdir +  f, 'w')
                parseEnc(incomdir + f,fh)
                fh.write(control)
                fh.close()

                f = 'epicmed.esp.'+oneday
                fh = open(outdir + f, 'w')
                parseRx(incomdir + f,fh)
                fh.write(control)
                fh.close()

                f = 'epicres.esp.'+oneday
                fh = open(outdir + f, 'w')
                parseLxRes(incomdir +f,fh)
                fh.write(control)
                fh.close()
        
        logging.info('Start: %s\n' %  startt)
        logging.info('End:   %s\n' % datetime.datetime.now())
    except:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        logging.info(message+'\n')

