import os, sys
#from ESP.esp.models import *
import xml.dom.minidom
from xml.dom.minidom import Document
import os, sys, django, datetime
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'
#from ESP.esp.models import *

import string, time,datetime,random
from ESP.settings import getLogging
plogging = getLogging('parsehl7.py_v0.1', debug=0)


###################################
def getChildNode(childNodes, nodename):
    for i in childNodes:
        if i.nodeName ==nodename:
            returnnode = i
            return returnnode

###################################
def getDemogfromDB(mrn):

    try:
        p = Demog.objects.get(DemogMedical_Record_Number__exact=mrn)
    except:
        return ''

    
    curcases = Case.objects.filter(caseDemog =p)
    curLxids = [c.caseLxID for c in curcases]
    if curLxids:
        curLxidlist = ','.join(curLxids).split(',')
        lxorderids = [(l.LxOrder_Id_Num,l.LxOrderDate,l.LxLoinc) for l in Lx.objects.filter(id__in=curLxidlist)]
    else:
        lxorderids=[]

    curRxids = [c.caseRxID for c in curcases]
    if curRxids:
        curRxidlist = ','.join(curRxids).split(',')
        rxorderids = [(l.RxOrder_Id_Num,l.RxOrderDate) for l in Rx.objects.filter(id__in=curRxidlist)]
    else:
        rxorderids=[]

    returnstr = ''
    for i in curcases:
        returnstr =returnstr+ 'CASE%s, RULE=%s, Lx (ORDER#, DATE, LOINC)=%s, Rx (ORDER#, DATE)=%s, ICD9=%s\n' % (i.id, i.caseRule.ruleName,str(lxorderids),str(rxorderids),i.caseICD9)
    return returnstr

###################################
class ParseDemog(object):
    def __init__(self,msgnum,mrn):
        self.msgnum = msgnum
        self.mrn = mrn
        self.condition=None
        self.icd9=''
        self.lxs = []
        self.rxs=[]

    def setCondition(self,value):
        self.condition=value

    def getCondition(self):
        return self.condition
    
    def setIcd9(self,value):
        self.icd9=value

    def getIcd9(self):
        return self.icd9

    def setLxs(self,value):
        self.lxs.append(value)

    def getLxs(self):
        return self.lxs
                        
    def setRxs(self,value):
        self.rxs.append(value)
        
    def getRxs(self):
        return self.rxs


                        
###################################
def parsedata(data,hl7file):

    lines = data.split('\n')
    demogcnt=0
    demogs = []
    for indx in range(len(lines)):
        if string.find(lines[indx], '<CX.1>')!=-1 and string.find(lines[indx+4], 'MR')!=-1:
            dbinfo = getDemogfromDB(lines[indx+1].strip())
            demogcnt=demogcnt+1
            demogmrn = lines[indx+1].strip()
            curdemog = ParseDemog(demogcnt,demogmrn)
            demogs.append(curdemog)

        if string.find(lines[indx], '<OBR.31>')!=-1:
            rulename = lines[indx+5].strip()
            icd9str = lines[indx+2].strip()
            curdemog.setCondition(rulename)
            curdemog.setIcd9(icd9str)

        if string.find(lines[indx], '<OBR.3>') !=-1: #<EI.1>')!=-1:
            ordernum = lines[indx+2].strip()
            orderdate = lines[indx+15].strip()
            ordercode = lines[indx+7].strip()
            if string.find(lines[indx+7],'18776-5') ==-1: ##Lx
                curdemog.setLxs('Order#=%s; Date=%s; LOINC=%s' % (ordernum,orderdate,ordercode))
            else: ##Rx
                drugstr = 'Order#=%s; Date=%s; ' % (ordernum,orderdate)

        if string.find(lines[indx], 'NA-56') !=-1:
            drugstr = drugstr + 'Drug=%s; ' % lines[indx+4].strip()
            curdemog.setRxs(drugstr)
            drugst=''

    return demogs



###################################
def write2file(hl7file,demogs):
     outf = open(hl7file+'_out.txt', 'w')
     outf.write('Msg#\tDemog\tCondition\tIcd9\tLx\tRx\n')
     for d in demogs:
         lxstr = ' || '.join(d.getLxs())
         rxstr = ' || '.join(d.getRxs())
         outf.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (d.msgnum,d.mrn,d.getCondition(),d.getIcd9(),lxstr,rxstr))
        
     outf.close()
     

###################################
def parse(hl7file):
    doc  =  xml.dom.minidom.parse (hl7file )
    pt =  doc.childNodes[0]
    msgbtnode = getChildNode(pt.childNodes,'MESSAGEBATCH')
    msgnode = getChildNode(msgbtnode.childNodes,'MESSAGES')
    data = msgnode.childNodes[1].data

    demogs = parsedata(data, hl7file)
    write2file(hl7file,demogs)

        
                    
    
###################################
if __name__ == "__main__":
    plogging.info('\n\nStart to parsing HL7 file: %s' % sys.argv[1])
    parse(sys.argv[1])
    
    plogging.info('Done on parsing HL7 file: %s\n\n' % sys.argv[1])
    


