"""
21 april 2009: added btzipdict to espSSconf.py - lookup a zip code to get the MDPH BT region
22 april 2009: added quick'n'dirty AMDS xml generator - bugger the xsd :)

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
import os, sys, django, time
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
#sendEmailToList = ['rexua@channing.harvard.edu', 'MKLOMPAS@PARTNERS.ORG',
# 'jason.mcvetta@channing.harvard.edu', 'ross.lazarus@channing.harvard.edu']
sendEmailToList = ['ross.lazarus@gmail.com']

def isoTime(t=None): 
    """ yyyymmddhhmmss - as at now unless a localtime is passed in
    # bah. Not what ncphi use - has tz and seps
    date time handling is hard - use gmt and punt on dst and tz
    """
    if t == None:
        t = time.gmtime()
    s = time.strftime('%Y-%m-%dT%H:%M:%S00:00',t)
    return s


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
    2) One of the following under the conditions specified:	
a) Measured fever of at least 100F (in temperature field of database)	
OR, if and only if there is no valid measured temperature of any magnitude,	
b) ICD9 code of 780.6 (fever)	

    """
    nfcases = None
    fcases = None
    cases = None
    icdFevercodes = ['780.6','780.31'] # note febrile convulsion!
    noFevercodes = [x[0] for x in syndDef if not x[1]]
    feverCodes = [x[0] for x in syndDef if x[1]]
    checkFever = (len(feverCodes) > 0)
    checkNoFever = (len(noFevercodes) > 0)
    nfcases = []
    fcases = []
    if checkNoFever:
        nfcases = icd9Fact.objects.filter(icd9EncDate__gte=startDT, 
             icd9EncDate__lte=endDT, icd9Code__in=noFevercodes).values_list('id',flat=True).distinct()
        print '## Nofever: %d cases' % len(list(nfcases))
    if checkFever: # must look for some codes with fever or icd9 fever
        # complex - find all encs with relevant icd9 code first
        icd9encs = icd9Fact.objects.filter(icd9EncDate__gte=startDT, icd9EncDate__lte=endDT, 
            icd9Code__in=feverCodes).values_list('icd9Enc',flat=True).distinct() # all relevant icd9facts
        realFeverEncs = Enc.objects.filter(EncTemperature__gte=100,
            id__in = icd9encs,EncEncounter_Date__gte=startDT,
            EncEncounter_Date__lte=endDT).values_list('id',flat=True).distinct() # encids of these with measured fever
        realFeverCases = icd9Fact.objects.filter(icd9EncDate__gte=startDT, icd9EncDate__lte=endDT, 
            icd9Code__in=feverCodes, icd9Enc__in=realFeverEncs).values_list('id',flat=True).distinct()  
        # whew - these are all cases with a measured fever 
        # pass if no temp recorded but an icd9 fever code
        notFeverEncs = Enc.objects.filter(EncTemperature__lt=100, EncTemperature__gte=90,
            id__in = icd9encs, EncEncounter_Date__gte=startDT,
            EncEncounter_Date__lte=endDT).values_list('id',flat=True).distinct() # measured, but NOT fever      
        # find all with an icd9 code for fever but NO measured temp
        icdFeverCases = icd9Fact.objects.filter(icd9EncDate__gte=startDT, 
          icd9EncDate__lte=endDT, icd9Enc__in = icd9encs,
          icd9Code__in=icdFevercodes).exclude(icd9Enc__in=notFeverEncs).values_list('id',flat=True).distinct()
        # these are cases without measured temp but an icd9 fever code recorded
        fcases = list(realFeverCases) + list(icdFeverCases) # icd9fact id lists
        n1 = len(list(icd9encs))
        n2 = len(list(realFeverCases))
        n3 = len(list(icdFeverCases))
        print '### fever: %d potential matches, %d with measured fever, %d with no measured temp but icd9 fever' % (n1,n2,n3)
    caseids = list(nfcases) + fcases
    cases = icd9Fact.objects.filter(id__in=caseids) # convert to icd9fact object lists
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

def makeAMDS(sdate='20080101',edate='20080102',syndDefs={},cclassifier="ESPSS",
    crtime='2009-03-30T22:24:23-05:00',doid='',requ='',minCount=5):
    """this includes some very crude xml generating code for
    testing.
    """

    def makeGeoHeader(ziplist=[]):
        """
        <GeoLocationSupported>
    <GeoLocation type="zip3">300</GeoLocation>
    <GeoLocation type="zip3">301</GeoLocation>
    </GeoLocationSupported>
        """
        res = ['<GeoLocationSupported>',]
        gs = '<GeoLocation type="zip%d">%s</GeoLocation>'
        for z in ziplist: 
            ndig = len(z.strip())
            s = gs % (ndig,z)
            res.append(s)
        res.append('</GeoLocationSupported>')
        return res


    def makeTargetHeader(syndlist=[]):
        """
        <TargetQuery>
    <Condition classifier="BioSense">GI</Condition>
    <Condition classifier="BioSense">Fever</Condition>
    </TargetQuery>
        """
        res = ['<TargetQuery>',]
        ts = '<Condition classifier="%s">%s</Condition>'
        for synd in syndlist:
            s = ts % (cclassifier,synd)
            res.append(s)
        res.append('</TargetQuery>')
        return res

    def makeCounts(aday={},edate='20080101'):
        """ all counts for a date by zip
        <CountItem>
    <Day>2009-01-01</Day>
    <LocationItem>
    <PatientLocation>300</PatientLocation>
    <Count>51</Count>
    </LocationItem>
    <LocationItem>				
    <PatientLocation>300</PatientLocation>
    <Count suppressed="true"/>
    </LocationItem>
    </CountItem>
        """
        res = []
        zips = aday.keys()
        zips.sort()
        for i,z in enumerate(zips):
            count = aday[z]
            if i == 0: # first one
                res.append('<CountItem>')
                res.append('<Day>%s-%s-%s</Day>' % (edate[:4],edate[4:6],edate[6:]))
            res.append('<LocationItem>')
            res.append('<PatientLocation>%s</PatientLocation>' % z)
            if count > minCount:
                res.append('<Count>%d</Count>' % count)
            else:
                res.append('<Count suppressed="true"/>')
            res.append('</LocationItem>')
        res.append('</CountItem>')
        return res
        
    def makeMessage(ziplist,syndrome,countsBydate):
        """
        so simple, not worth using an xml parser?
        First challenge - write the header with all the zips and syndromes to follow
        counts is a dict of syndromes, containing dicts of dates containing dicts of zip/count
        """
        # provide sd,ed,ctime,ruser,doid
        m = ['<AMDSRecordSummary>',]
        m.append('<DateStart>%s</DateStart>' % sdate)
        m.append('<DateEnd>%s</DateEnd>' % edate)
        m.append('<CreationDateTime>%s</CreationDateTime>' % crtime)
        m.append('<RequestingUser>%s</RequestingUser>' % requ)
        m.append('<DataSourceOID>%s</DataSourceOID>' % doid)
        g = makeGeoHeader(ziplist)
        m += g
        t = makeTargetHeader([syndrome,])
        m += t
        m.append('<CellSuppressionRule>%d</CellSuppressionRule>' % minCount)
        m.append('</AMDSRecordSummary>')
        m.append('<CountSet>')
        dkeys = countsBydate.keys()
        dkeys.sort()
        for d in dkeys:
            c = makeCounts(countsBydate[d],d)
            m += c
        m.append('</CountSet>')
        m.append('</AMDSRecordSummary>')
        return m  
    
    # main makeAMDS starts here
    mdict = {}
    for syndrome in syndDefs:
        countsBydate = {} # we want {date1:{zip1:22,zip2:41},date2:{..}}
        zips = {}
        print 'looking for',syndrome
        icdlist = syndDefs[syndrome] # icd list
        g = syndGen(syndDef=icdlist,syndName=syndrome,startDT=sdate,endDT=edate)
        for i,c in enumerate(g):
            (zipc,age,id,enc,icd,demog,encdate) = c
            zip3 = zipc[:3] # testing with 3 digit zips
            zips.setdefault(zip3,zip3) # record all unique zips        
            countsBydate.setdefault(encdate,{})
            countsBydate[encdate].setdefault(zip3,0)
            countsBydate[encdate][zip3] += 1
        del g
        m = makeMessage(zips,syndrome,countsBydate)
        mdict[syndrome] = m
    return mdict

def testsyndGen():
    """ 
    for dev
    """
    for s in syndDefs:
        print 'looking for',s
        d = syndDefs[s] # icd list
        g = syndGen(syndDef=d,syndName=s,startDT='20080201',endDT='20080201')
        for i,c in enumerate(g):
            (age,zip,id,enc,icd,demog,encdate) = c
            print s,i,c
        del g

def testAMDS(sdate='20080101',edate='20080102'):
    """ test stub for AMDS xml generator
    """
    doid='ESP:SS@Atrius'
    requ='Ross'
    minCount=5
    crtime=isoTime(time.localtime())
    print 'crtime =',crtime
    fproto = 'ESP_AMDS_%s_%s_%s.xml'
    mdict = makeAMDS(sdate=sdate,edate=edate,syndDefs=syndDefs,cclassifier="ESPSS",
       crtime=crtime,doid=doid,requ=requ,minCount=minCount)
    mdk = mdict.keys() # syndromes
    mdk.sort()
    for syndrome in mdk:
        m = mdict[syndrome]
        fname = fproto % (syndrome,sdate,edate)
        f = open(fname,'w')
        f.write('\n'.join(m))
        f.write('\n')
        f.close()
        print '## wrote %d rows to %s' % (len(m),fname)

if __name__ == "__main__":
  testAMDS()


