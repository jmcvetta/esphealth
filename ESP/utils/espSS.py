"""
21 april 2009: added btzipdict to espSSconf.py - lookup a zip code to get the MDPH BT region

Copyright ross lazarus April 20 2009
All rights reserved
Licensed under the LGPL v3.0 or a later version at your preference
see http://www.gnu.org/licenses/lgpl.html

Notes during design and prototyping of an ESP:SS module
Need to decouple the definitions, detection and consumption of events

a) Definitions are lists of icd9 codes +/- fever

Create these for testing from spreadsheet cut'n'pastery (TM)
each is a list of [icd9code,feverRequired] - uniform structures
from the zoo of spreadsheetery

TODO: store these in tables 

Use 'in' queries to allow the database to do the work of finding
encounters for a given date using icd9fact table

DONE: first task is to set up data structures for defs
rml april 20 - see espSSconf.py

fever # MDPH definition of ILI
2) One of the following under the conditions specified:	
a) Measured fever of at least 100F (in temperature field of database)	
OR, if and only if there is no valid measured temperature of any magnitude,	
b) ICD9 code of 780.6 (fever)	
Note febrile convulsion added sometimes? 
ICD9 code 780.31 (Febrile Convulsions)			

TODO: clarify whether febrile convulsions diag counts as fever
TODO: create a function to figure if an encounter with an 
ICD9 requiring a fever had a fever..

b) Make the detection algorithm a generator so the consumer can be decoupled - it can
choose the latest set of defs for a syndrome from esp_syndefs, then set up an 
event iterator as eg getEvents(icdList,needFever,startDT,endDT)
returning a tuple (encId,demogId,pcpId,icd9,obsDT,obsZip) for each event, 
and do whatever it wants including store individual records or just pump out totals by zip

TODO: icdList and needFever come from a table eg of:
esp_syndefs
id
syndName
syndCode
icd9List 
needFever
versionDate

ordered by date so first one is always most current
Need a web interface to edit these and bump versionDate

filled from one of the excel spreadsheets we have from Katherine

DONE: see espSSconf.py - this code now has an ILI test that appears
to work - returns 1680 ILI cases for feb1-2 2008

TODO: squirt into database tables and adjust the test
here; create django application to manage these

c) first iteration consumer can just write text files of count by zip by syndrome

a table perhaps for more generic reporting - eg we might need to construct individual
records with name, address, gender (demog), event and pcp details

esp_ssevents
id
syndCode ->fk esp_syndefs
eventDT
eventZip
demogID
encID (gives PCP)
age
zip



"""
import os, sys, django, datetime
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import *

from espSSconf import btzipdict,atriusSites,ILIdef,HAEMdef,LESIONSdef,LYMPHdef
from espSSconf import LGIdef,UGIdef,NEUROdef,RASHdef,RESPdef
# these are [icd,feverreq] lists
import utils
defList = [ILIdef,HAEMdef,LESIONSdef,LYMPHdef,LGIdef,UGIdef,NEUROdef,RASHdef,RESPdef]
nameList = ['ILI','Haematological','Lesions','Lymphatic','Lower GI','Upper GI',
'Neurological','Rashes','Respiratory']
syndDefs = dict(zip(nameList,defList))

iclogging = getLogging('espSSdev_v0.1', debug=0)
#sendEmailToList = ['rexua@channing.harvard.edu', 'MKLOMPAS@PARTNERS.ORG','jason.mcvetta@channing.harvard.edu', 'ross.lazarus@channing.harvard.edu']
sendEmailToList = ['ross.lazarus@gmail.com']

def makeAge(dob='20070101',edate='20080101'):
    """return age in days for mdph ILI reports 
    """
    if len(dob) < 8:
        logging.error('### duff dob %s in makeAge' % dob)
        return None
    else:
        yy,mm,dd = map(int,[dob[:4],dob[4:6],dob[6:8]])
        bd = datetime.date(yy,mm,dd)
    if len(edate) < 8:
        logging.error('### duff edate %s in makeAge' % edate)
        return None
    else:
        yy,mm,dd = map(int,[edate[:4],edate[4:6],edate[6:8]])
        ed = datetime.date(yy,mm,dd)       
    return (ed-bd).days

def syndGen(syndDef=[],syndName='',startDT=None,endDT=None):
    """ prototype for development
    yield all events from startDT to endDT with any
    of the ICD codes taking fever into account if required
    """
    nfcases = None
    fcases = None
    cases = None
    icdFevercodes = ['780.6','780.31'] # note febrile convulsion!
    noFevercodes = [x[0] for x in syndDef if not x[1]]
    feverCodes = [x[0] for x in syndDef if x[1]]
    checkFever = (len(feverCodes) > 0)
    checkNoFever = (len(noFevercodes) > 0)
    if checkNoFever:
        icases = icd9Fact.objects.filter(icd9Code__in=noFevercodes).values_list('id',flat=True)
        if len(icases) > 0:
            nfcases = icd9Fact.objects.filter(id__in=icases,icd9EncDate__gte=startDT, 
             icd9EncDate__lte=endDT)
    if checkFever: # must look for some codes with fever or icd9 fever
        # TODO: eesh - the text seems to want to ignore any case with 
        # an ICD9 fever code but a measured temp <= 100F!!
        # not sure I can be bothered...
        realFevers = Enc.objects.filter(EncTemperature__gte='100', EncEncounter_Date__gte=startDT,
            EncEncounter_Date__lte=endDT).values_list('EncPatient',flat=True).distinct()
        # mmmm - we really only need this done once over all syndromes
        # TODO is this worth fixing - move outside syndrome loop - bah!
        # patient ids with measured fever
        icdFevers = icd9Fact.objects.filter(icd9Code__in=icdFevercodes,icd9EncDate__gte=startDT, 
        icd9EncDate__lte=endDT).values_list('icd9Patient',flat=True).distinct() 
        # patient ids with icd fever
        feverIDs = list(realFevers) + list(icdFevers)
        if len(feverIDs) > 0: # expect few of these each period
            fcases = icd9Fact.objects.filter(icd9EncDate__gte=startDT, icd9EncDate__lte=endDT, 
            icd9Code__in=feverCodes, icd9Patient__in=feverIDs)
    if fcases and cases:
        cases = nfcases + fcases
    elif fcases:
        cases = fcases
    elif nfcases:
        cases = nfcases
    if cases:
        zips = [x.icd9Patient.DemogZip for x in cases] # get zips!   
        zips = [x.split('-')[0] for x in zips] # get rid of trailing stuff - want 5 digit only  
        dobs = [x.icd9Patient.DemogDate_of_Birth for x in cases] # get dobs   
        encdates = [x.icd9Enc.EncEncounter_Date for x in cases] # get encdates   
        encAges = [int(makeAge(dobs[i],encdates[i])/365.25) for i in range(len(encdates))]
        # for testing can return tuples for efficiency rather than mongo django objects
        # or values for dict instead with overheads.
        caselist = list(cases.values_list('id','icd9Enc','icd9Code','icd9Patient','icd9EncDate')) 
        for i,c in enumerate(caselist):
            c = list(c)
            c.insert(0,encAges[i])
            c.insert(0,zips[i])
            caselist[i] = c
        for c in caselist:
            yield c
    else:
        raise StopIteration # nada
    
def test():
    """ 
    for dev
    """
    for s in syndDefs:
        print 'looking for',s
        d = syndDefs[s] # icd list
        g = syndGen(syndDef=d,syndName=s,startDT='20080201',endDT='20080201')
        for i,c in enumerate(g):
            print s,i,c
        del g

if __name__ == "__main__":
  test()