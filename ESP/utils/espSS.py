"""
28 april 2009: changed code to count all encounters to work by day to save ram. Not sure how to speed it up
28 april 2009: ah - mixing up icd9Fact ids with Enc ids is not a very good idea - counts now sane
28 april 2009: getting one zip with 1 as volume but 2 ILI cases. arrgh. 
27 april 2009: swine flu - added a simple tab delimited file dumperqscreen 
21 april 2009: added btzipdict to espSSconf.py - lookup a zip code to get the MDPH BT region
22 april 2009: added quick'n'dirty AMDS xml generator - bugger the xsd :)

Copyright Ross Lazarus April 20 2009
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
myVersion = '0.003'
thisSite = 'Atrius'
thisRequestor = 'Ross Lazarus'
import os, sys, django, time
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import *

from espSSconf import btzipdict,atriusUseDict,atriusLookup,atriusExcludeCodes,atriusUseCodes, \
atriusZips, ILIdef,HAEMdef,LESIONSdef,LYMPHdef,LGIdef,UGIdef,NEUROdef,RASHdef,RESPdef
# these are [icd,feverreq] lists
import utils
defList = [ILIdef,HAEMdef,LESIONSdef,LYMPHdef,LGIdef,UGIdef,NEUROdef,RASHdef,RESPdef]
nameList = ['ILI','Haematological','Lesions','Lymphatic','Lower GI','Upper GI',
'Neurological','Rashes','Respiratory']
syndDefs = dict(zip(nameList,defList))

SSlogging = getLogging('espSS_v%d' % myVersion, debug=0)
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


def AgeencDateVolumes(startDT='20090301',endDT='20090331',zip5=True):
    """return a dict of date, with zip and age in years (!) specific total encounter volume for each day
    exclude from atriusExcludeCodes. Challenge is that it requires looking up the zip and age of
    every encounter..
)   Using extra to squirt some SQL into the ORM call 
    iterator seems to work - ram use is now reasonable and it's fast enough..
    """
    started = time.time()
    datecounts = {}
    dateagecounts = {}
    esel = {'ezip':'select DemogZip from esp_demog where esp_demog.id = esp_enc.EncPatient_id',
            'dob': 'select DemogDate_of_Birth from esp_demog where esp_demog.id = esp_enc.EncPatient_id'}
    # an extra select dict to speed up the foreign key lookup - note real SQL table and column names!
    allenc = Enc.objects.filter(EncEncounter_Date__gte=startDT, EncEncounter_Date__lte=endDT,
         EncEncounter_Site__in = atriusUseCodes).extra(select=esel).values_list('ezip','dob',
        'EncEncounter_Date').iterator() # not sure if this will really work - lets test       
    if not zip5:
       zl = 3
    else:
       zl = 5 # use 5 - ignore rest
    for i,anenc in enumerate(allenc):
        if (i+1) % 10000 == 0:
            SSlogging.info('AgeencDateVolumes at %d, %f /sec' % (i+1, i/(time.time() - started)))
        (z,dob,thisd) = anenc
        age = makeAge(dob,thisd) # small fraction have bad dates
        if age:
            age = int(age/365.25) + 1 # make <1 = 1 etc..
            z = z[:zl] # corresponding zip
            dz = dateagecounts.setdefault(thisd,{})
            az = dateagecounts[thisd].setdefault(z,{})
            naz = dateagecounts[thisd][z].setdefault(age,0)
            dateagecounts[thisd][z][age] += 1
            dz = datecounts.setdefault(thisd,{})
            az = datecounts[thisd].setdefault(z,0)
            datecounts[thisd][z] += 1

    del allenc
    return datecounts,dateagecounts


def syndDateZipId(syndDef=[],syndName='',startDT=None,endDT=None,ziplen=5):
    """ revised to make the enc record the central unit
    Atrius exclusions are such a pain...
    yield all cases for this specific syndName from startDT to endDT with any
    of the ICD codes in syndDef taking fever into account if required
    from the spreadshit:
    2) One of the following under the conditions specified:
        a) Measured fever of at least 100F (in temperature field of database)   
        OR, if and only if there is no valid measured temperature of any magnitude,
        b) ICD9 code of 780.6 (fever)   

    """
    redundant = 0
    ignoreSite = 0
    ignoredSites = {}
    nffacts = [] # so we can add
    ffacts = []
    fcases = []    
    cases = []
    icdFevercodes = ['780.6','780.31'] # note febrile convulsion added !
    noFevercodes = [x[0] for x in syndDef if not x[1]] # definitive in absence of fever 
    feverCodes = [x[0] for x in syndDef if x[1]] # definitive if fever or.. see note on complexities
    checkFever = (len(feverCodes) > 0) # no point if not needed
    checkNoFever = (len(noFevercodes) > 0)
    if checkNoFever: # get all definitive cases as icd9fact ids
        nffacts = icd9Fact.objects.filter(icd9EncDate__gte=startDT, 
             icd9EncDate__lte=endDT, icd9Code__in=noFevercodes).values_list('id',flat=True)
        nffacts = list(nffacts) # and back to list of unique encounter id 
        SSlogging.info('## %s Nofever: %d diags (+redundancies on patients in events)' % (syndrome,len(list(nffacts))))
    if checkFever: # must look for specific icd9 codes accompanied by measured fever or no temp measure but icd9 fever
        # complex - find all encs with relevant icd9 code requiring a fever
        icd9Encs = icd9Fact.objects.filter(icd9EncDate__gte=startDT, icd9EncDate__lte=endDT, 
            icd9Code__in=feverCodes).exclude(id__in=nffacts).values_list('icd9Enc',flat=True) 
        # all relevant icd9facts -> enc id list
        feverEncs = Enc.objects.filter(EncTemperature__gte=100,EncEncounter_Date__gte=startDT, 
             EncEncounter_Date__lte=endDT,
            id__in=icd9Encs).values_list('id',flat=True) # filtered with measured fever
        realFeverFacts = icd9Fact.objects.filter(icd9Code__in=feverCodes, icd9EncDate__gte=startDT, 
             icd9EncDate__lte=endDT,
            icd9Enc__in=feverEncs).exclude(id__in=nffacts).values_list('id',flat=True) 
        # convert to icd9Fact ids - may include redundancies - filter encounters later
        # whew - these are all cases with a measured fever as icd9Fact ids
        # Look for no temp recorded but one of the icd9 codes for fever instead
        notFeverEncs = Enc.objects.filter(EncTemperature__lt=100, EncTemperature__gte=90,EncEncounter_Date__gte=startDT, 
             EncEncounter_Date__lte=endDT,
            id__in = icd9Encs).values_list('id',flat=True) # measured, but NOT fever      
        # find all with an icd9 code for fever but NO measured temp
        icdFeverFacts = icd9Fact.objects.filter(icd9Enc__in = icd9Encs, icd9EncDate__gte=startDT, 
             icd9EncDate__lte=endDT,
          icd9Code__in=icdFevercodes).exclude(icd9Enc__in=notFeverEncs,id__in=nffacts).values_list('id',flat=True)
        # these are cases without measured temp but an icd9 fever code recorded
        ffacts = set(list(realFeverFacts) + list(icdFeverFacts)) # enc id lists
        ffacts = list(ffacts) # back to list (!) cheap way to remove duplicate encounters...
        n1 = len(list(icd9Encs))
        n2 = len(list(realFeverFacts))
        n3 = len(list(icdFeverFacts))
        SSlogging.info('### %s fever icds: %d icdmatch, %d +fever, %d notemp but icd9 fever' % (syndrome, n1,
        n2,n3))
    caseids = nffacts + ffacts # already lists
    SSlogging.info('#### Total count = %d' % (len(caseids)))
    if caseids: # some
        factids = icd9Fact.objects.filter(id__in=caseids).order_by('id') # keep in id order
        zips = [x.icd9Patient.DemogZip.split('-')[0] for x in factids] # get zips less -xxxx 
        dobs = [x.icd9Patient.DemogDate_of_Birth for x in factids] # get dobs  
        atriusCodes = [x.icd9Enc.EncEncounter_Site for x in factids] 
        encdates = [x.icd9Enc.EncEncounter_Date for x in factids] # get encdates   
        encAges = [makeAge(dobs[i],encdates[i]) for i in range(len(encdates))]
        icd9FactIds = [x.id for x in factids]
        encIds = [x.icd9Enc.id for x in factids] # fk lookup
        demogIds = [x.icd9Patient.id for x in factids]
        icd9codes = [x.icd9Code for x in factids]
        # need to remove redundancy on demog Id and date
        dateId = {} # this will be hard if we got to periods other than days? TODO: fixme...one day
        for i,edate in enumerate(encdates):
            id = demogIds[i] # this subject
            z = zips[i][:ziplen]            
            dateId.setdefault(edate,{})
            dateId[edate].setdefault(z,{})
            if dateId[edate][z].get(id,None) == None: # is new for this syndrome, date, zip
                aSite = atriusCodes[i]
                if atriusUseDict.get(aSite,None):     
                    age = encAges[i]
                    if age: # may be null if duff dates
                        age = int(age/365.25)
                        encId = encIds[i]
                        icd9FactId = icd9FactIds[i]
                        icd9code = icd9codes[i]
                        demogId = demogIds[i]
                        dateId[edate][z][id] = (z,age,icd9FactId,encId,icd9code,demogId,edate)
                else:
                    aSiteName = atriusLookup.get(aSite,'%s?' % aSite)
                    n = ignoredSites.setdefault(aSiteName,0)
                    ignoredSites[aSiteName] += 1
                    ignoreSite += 1
            else:
                redundant += 1
        SSlogging.info('# %s Total Atrius ignore site cases = %d, sites= %s' % (syndrome, ignoreSite,ignoredSites))
        SSlogging.info('## %s total redundant ids for zip/date/syndrome = %d' % (syndrome,redundant))
        return dateId


def makeAMDS(sdate=None,edate=None,syndrome=None,encDateVols=None,
    encAgeDateVols=None,doid=None,requ=None,minCount=5,crtime=None):
    """crude generator for xls
    rml april 27 2009 swine flu season?
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

    def makeCounts(aday={},edate='20080101',ziplist=[]):
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
        I guess we need zeros for empty zips to keep the xml bloated and regular?
        """
        res = []
        alld = encDateVols.get(edate,{})
        zips = aday.keys()
        if len(zips) == 0:
             SSlogging.info('## no events for %s on %s' % (syndrome, edate))
             return res # empty
        zips.sort()
        alld = encDateVols.get(edate,{})
        res.append('<CountItem>')
        res.append('<Day>%s-%s-%s</Day>' % (edate[:4],edate[4:6],edate[6:]))
        for i,z in enumerate(ziplist): # note use of ziplist to keep xml bloated
            count = len(aday.get(z,[])) 
            #if count > 0: # can be zero because of exclusions
            alln = alld.get(z,0)
            res.append('<LocationItem>')
            res.append('<PatientLocation>%s</PatientLocation>' % z)
            if count > minCount:
                res.append('<Count>%d</Count>' % count)
            else:
                res.append('<Count suppressed="true"/>')
            res.append('<AllCount>%d</AllCount>' % alln) # ross addition to xml!
            res.append('</LocationItem>')
        res.append('</CountItem>')
        return res

    def makeMessage(syndrome='?',dateId={}):
        """
        so simple, not worth using an xml parser?
        First challenge - write the header with all the zips and syndromes to follow
        counts is a dict of syndromes, containing dicts of dates containing dicts of zip/count
        """
        zips = {}
        for d in dateId.keys():
            zs = dateId[d].keys()
            for z in zs:
                zips.setdefault(z,z)
        ziplist = zips.keys()
        ziplist.sort() # for header
        m = ['<AMDSQueryResponse>']
        m.append('<AMDSRecordSummary>')
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
        edk = dateId.keys()
        edk.sort()
        for thisdate in edk:
            SSlogging.info('!!!!#### processing syndrome %s for date %s' % (syndrome,thisdate))
            c = makeCounts(syndrome,dateId[thisdate],thisdate,ziplist)
            m += c
        m.append('</CountSet>')
        m.append('</AMDSRecordSummary>')
        m.append('</AMDSQueryResponse>')
        return m  
    
    # main makeAMDS starts here
    SSlogging.info('looking for %s' % syndrome)
    icdlist = syndDefs[syndrome] # icd list
    dateId = syndDateZipId(syndDef=icdlist,syndName=syndrome,startDT=sdate,endDT=edate)
    # now returns dateId[edate][z][id] = (z,age,icd9FactId,encId,icd9code,demogId,edate)
    res = makeMessage(syndrome, dateId)
    return res


def makeTab(sdate='20080101',edate='20080102',syndrome='ILI',
    encDateVols={},encAgeDateVols={}):
    """crude generator for xls
    rml april 27 2009 swine flu season?
    """

    def makeCounts(syndrome='?',aday={},edate='20080101'):
        """ all counts for a date by zip
        """
        res = []
        zips = aday.keys()
        if len(zips) == 0:
             SSlogging.info('## no events for %s on %s' % (syndrome, edate))
             return res # empty
        zips.sort()
        alld = encDateVols.get(edate,{})
        SSlogging.debug('\n\n@@@@###### %s makeCountstab %s: alld (%d) = \n###%s' % (syndrome,edate,len(alld),alld))
        SSlogging.debug('aday (%d) =\n###%s' % (len(aday),aday))   
        for i,z in enumerate(zips):
            zn = len(aday[z]) # number of individual records in each zip for this date/synd
            if zn > 0: # can be empty because of the way it's constructed
                alln = alld.get(z,None)
                SSlogging.debug('z=',z,type(z), 'alln=',alln,type(alln),'zn=',zn,type(zn))
                if alln:
                    if zn > alln:
                        SSlogging.warning('####! syndrome counts %d > volume %d for zip %s, date %s, synd %s' % (zn,
                        alln,z,edate,syndrome))
                        allfrac = '? bug'
                    else:
                        f = (100.0*zn)/alln
                        allfrac = '%f' % f
                else:
                    allfrac = '###!! wtf None - no all event count zip %s ?' % z
                    SSlogging.warning(allfrac)
                    alln = 0
                row = '\t'.join((edate,z,syndrome,'%d' % zn,'%d' % alln,allfrac))
                res.append(row)
        return res
    
    def makeLinelist(syndrome='?',aday={},edate='20080101'):
        """ make individual records
        """
        res = []
        zips = aday.keys()
        zips.sort()
        alld = encDateAgeVols.get(edate,{})
        SSlogging.debug('### MakeLinelist zips=',zips)
        for zipcode in zips:
            alldz = alld.get(zipcode,{})
            if alldz == {}:
                SSlogging.warning('###!! Makelinelist: alldz empty for syndrome %s zip %s' % (syndrome, zipcode)) 
            zip5 = zipcode[:5] # testing with 3 digit zips
            zips.setdefault(zip5,zip5) # record all unique zips for amds headers
            zids = zipIds[zipcode]
            idk = zids.keys()
            idk.sort()
            for id in idk:
                (z,age,icd9FactId,encId,icd9code,demogId,edate) = zids[id] # whew 
                if age:
                    alldza = alldz.get(age,0)
                else:
                    alldza = 0
                if alldza == 0:
                    SSlogging.warning('###!! Makelinelist: 0 count for age=%d, syndrome=%s, zipcode=%s' % (age,syndrome,zip5))
                row = '\t'.join((syndrome,edate,z,age,icd9code,alldza))
                res.append(row)
        return res 
    
    
    def makeMessage(syndrome='?',dateId={}):
        """
        format a simple xls report
        """
        # provide sd,ed,ctime,ruser,doid
        m = ['Date\tZip\tSyndrome\tNSyndrome\tNAllEnc\tPctSyndrome',] # amalg
        lm = ['Synd\tDate\tZip_Res\tAge_Yrs\tICD9code\tN_All_Encs_Age_Zip',] # line list
        edk = dateId.keys()
        edk.sort()
        for thisdate in edk:
            SSlogging.debug('!!!!#### processing syndrome %s for date %s' % (syndrome,thisdate))
            c = makeCounts(syndrome,dateId[thisdate],thisdate)
            m += c
            c = makeLinelist(syndrome,dateId[thisdate],thisdate)
            lm += c
        return m,lm  
    
    # main makeTab starts here
    icdlist = syndDefs[syndrome] # icd list
    dateId = syndDateZipId(syndDef=icdlist,syndName=syndrome,startDT=sdate,endDT=edate)
    # now returns dateId[edate][z][id] = (z,age,icd9FactId,encId,icd9code,demogId,edate)
    res = makeMessage(syndrome, dateId)
    return res



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
    On Thu, Apr 23, 2009 at 11:54 PM, Lee, Brian A. (CDC/CCHIS/NCPHI)
    (CTR) <fya1@cdc.gov> wrote:
    > I changed the root element to be <AMDSQueryResponse> since these
    > examples have two root elements (AMDSRecordSummary and CountSet). Other
    > than that, the data makes for great sample sets.
    """
    
    dateZip,dateZipAge = AgeencDateVolumes(startDT=sdate,endDT=edate)
    doid='ESPSS@%s' % thisSite
    requ=thisRequestor
    minCount=5
    crtime=isoTime(time.localtime())
    SSlogging.debug('crtime = %s' % crtime)
    fproto = 'ESP_AMDS_%s_%s_%s.xml'
    syndromes = syndDefs.keys() # syndromes
    syndromes.sort()
    for syndrome in syndromes:
        res = makeAMDS(sdate=sdate,edate=edate,syndrome=syndrome,
          encDateVols=dateZip,encAgeDateVols=dateZipAge,
          doid=doid,requ=requ,minCount=minCount,crtime=crtime)
        fname = fproto % (thisSite,syndrome,sdate,edate)
        f = open(fname,'w')
        f.write('\n'.join(res))
        f.write('\n')
        f.close()
        SSlogging.debug('## wrote %d rows to %s' % (len(res),fname))
    


def testTab(sdate='20090401',edate='20090431'):
    """ test stub for tab delim generator
    date zip syndrome syndN allencN syndPct
    """
    dateZip,dateZipAge = AgeencDateVolumes(startDT=sdate,endDT=edate)
    fproto = '%s%s_Synd_%s_%s_%s.xls'
    syndromes = syndDefs.keys() # syndromes
    syndromes.sort()
    for syndrome in syndromes:
        res = makeTab(sdate=sdate,edate=edate,syndrome=syndrome,encDateVols=dateZip,encAgeDateVols=dateZipAge)
        fname = fproto % (thisSite,syndrome,sdate,edate)
        f = open(fname,'w')
        f.write('\n'.join(res))
        f.write('\n')
        f.close()
        SSlogging.debug('## wrote %d rows to %s' % (len(res),fname))

if __name__ == "__main__":
  testTab()

