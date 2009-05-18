"""
welcome to espSS.py
Please look at http://esphealth.org/trac/ESP/wiki/ESPSS
to get some idea of the background

Most Recent Changes First:
7 May 2009: specification stampede overwhelms valiant programmer - now with site zip amalgamation
            and code bloat(TM)
2 May 2009: fixed a silly xml bug found while experimenting with AMDS format files
30 april 2009: get ids and encounter counts for zips over long period as sampling weights?
30 april 2009: KY wants site volumes in line list. Sigh. As Frank Zappa said, 'the torture never stops...'
29 april 2009: create reports with and without site exclusions - they're interesting and variable
29 april 2009: added temp for ILI individual report with age to nearest 5 years
29 april 2009: fixed all encounter counting - add SQL extras to the filter and .iterator() - wicked fast now.
               surprisingly good for an ORM - sqlalchemy is really slick
28 april 2009: changed code to count all encounters to work by day to save ram. Not sure how to speed it up
28 april 2009: ah - mixing up icd9Fact ids with Enc ids is not a very good idea - counts now sane
28 april 2009: getting one zip with 1 as volume but 2 ILI cases. arrgh. 
27 april 2009: swine flu - added a simple tab delimited file dumperqscreen 
21 april 2009: added btzipdict to espSSconf.py - lookup a zip code to get the MDPH BT region
22 april 2009: added quick'n'dirty AMDS xml generator - bugger the xsd :)

Copyright Ross Lazarus April 20 2009
All rights reserved
Licensed under the LGPL v2.0 or a later version at your preference
see http://www.gnu.org/licenses/lgpl.html
Part of the esp project - see http://esphealth.org
Feel free to modify and redistribute this source but please leave this copyright and license
statement - add your own as an LGPL derived work and please let me know if you
can figure out how to find me.


This is a syndromic surveillance module for ESP encounter tables
It generates prototypical AMDS XML format for CDC NCPHI, and aggregate tables with 
unit records as simple fake spreadsheets for MDPH.

It's probably useful as a starting point for any icd9 or lab value based ESP rule engine
because it's fairly low impedance to reconfigure, using a corny, specification table
text processing kludge in an accompanying configuration python module, (do we really
need a database? We have svn for free?) 
to dynamically set up a fairly horrible set of rules:

a) case if in period encounter with any of an icd9 list 'NoFever';
b) case if has 'fever' and any of icd9list 'WithFever'. 
Define fever as measured >= 100F or measure missing (yes, missing) 
and one of 2 fever icd9 codes. 

Given code to implement those definitions, the idea is to construct 
some simple dict based structures to enable the kinds of 
reports needed. Essentially, we can arrange the data in subdicts of syndromes, 
then event dates, then zipcodes, and then ages (yes we need all those) or more generally, as
a tuple of characteristics needed for unit records like age and residential zip.

Given those data structures, formatting AMDS by syndrome, period, and zip; 
and similar but xls format aggregate summaries and unit records is straightforward.

The last of those will probably requiring some additional and explicit
approval and permission from the local data custodians before deploying those - we
have it here at Atrius...

======================
Accumulated debris of free form notes during development:

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
myVersion = '0.7'
thisSite = 'Atrius' # for amds header
thisRequestor = 'Ross Lazarus' 
cclassifier = 'ESPSSApril2009'  
ageChunksize = 5 #

import os, sys, django, time, datetime
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import *
import utils
SSlogging = getLogging('espSS_v%s' % myVersion, debug=0)
#sendEmailToList = ['rexua@channing.harvard.edu', 'MKLOMPAS@PARTNERS.ORG',
# 'jason.mcvetta@channing.harvard.edu', 'ross.lazarus@channing.harvard.edu']
sendEmailToList = ['ross.lazarus@gmail.com']


# conditions for ESP:SS are determined by an encounter having any of a (potentially empty)
# 'nofevericd9' list of icd9 codes, or any of a different 'fevericd9'
# (potentially empty) list of icd9 codes that also require a fever to be counted as cases.
# the definition of fever is painful as it involves a lot of missing temp data
#
from espSSconfATRIUS import btzipdict,localSiteUseDict,localSiteLookup,localSiteExcludeCodes,localSiteUseCodes, \
localSiteZips, ILIdef,HAEMdef,LESIONSdef,LYMPHdef,LGIdef,UGIdef,NEUROdef,RASHdef,RESPdef
# these are a defining group of [icd,feverreq] lists, and they are instantiated from
# long strings cut and paste from the 
# original specification, subject to text processing into dicts and lists 
# used as structures representing rules to identify syndrome 'cases'
# over a specified period, for reporting by syndrome, date and zipcode counts as AMDS
# xml, as tab delimited aggregate count, and as unit record formats for MDPH
#
# if feverreq, additional complex logic is used - either measured temp >= 100
# or no temp measured (ie missing) but one of 2 icd9 fever/febrile convulsion icd9s
# eesh
# The icd9 codes are matched 'or' on all the subject codes.  



defList = [ILIdef,HAEMdef,LESIONSdef,LYMPHdef,LGIdef,UGIdef,NEUROdef,RASHdef,RESPdef]
nameList = ['ILI','Haematological','Lesions','Lymphatic','Lower GI','Upper GI',
'Neurological','Rashes','Respiratory']
syndDefs = dict(zip(nameList,defList))
# our application is now configured with all the data structures
# needed to identify and report cases and aggregates
# these can be easily adjusted - check the espSSconfATRIUS.py file
# to see how this is done.
# TODO: use svn to version these and allow updating - propogate version metadata
#       to derived data
#

def isoTime(t=None): 
    """ Needed for AMDS - now unless a localtime is passed in
    ncphi has tz and seps
    date time handling is hard - use gmt and punt on dst and tz
    """
    if t == None:
        t = time.gmtime()
    s = time.strftime('%Y-%m-%dT%H:%M:%S00:00',t)
    return s


def makeAge(dob='20070101',edate='20080101',chunk=ageChunksize):
    """return age in year chunks for mdph ILI reports 
    for d in ['20000101','20010101','20030204']:
    for e in ['20040101','20050101','20030604']:
        print makeAge(dob=d,edate=e,chunk=5)

    """
    if len(dob) < 8:
        SSlogging.error('### Short (<8) dob "%s" in makeAge' % dob)
        return None
    else:
        yy,mm,dd = map(int,[dob[:4],dob[4:6],dob[6:8]])
        bd = datetime.date(yy,mm,dd)
    if len(edate) < 8:
        SSlogging.error('### Short (<8)edate "%s" in makeAge' % edate)
        return None
    else:
        yy,mm,dd = map(int,[edate[:4],edate[4:6],edate[6:8]]) # dates are all yyyymmdd 
        ed = datetime.date(yy,mm,dd)       
    age = (ed-bd).days
    age = int(age/365.25) # whole years taking leap years into account (!)
    age = chunk*int(age/chunk) # if 0-4 = 0, if 5..9 = 5 if 10..14=10 etc
    age = min(80,age) # compress last cat so all > 80 are 80
    return age


def AgeencDateVolumes(startDT='20090301',endDT='20090331',ziplen=5,localIgnore=True):
    """
    This started simple, but grew with specification creep. 
    Now returns 3 sets of counts for each date
    a) by residential zip, b) by residential zip and then age chunk, 
    and...drum roll..c) by clinic site zip and age. 
    Oy.
    localIgnore determines whether specific total encounter volume for each day excludes the sites
    in localSiteExcludeCodes. 
    Challenge is that it requires looking up the zip and age of
    every encounter..
    Using extra to squirt some SQL into the ORM call 
    iterator seems to work - ram use is now reasonable and it's fast enough..
    Age in 5 year chunks added at Ben Kruskal's request for line lists
    """
    started = time.time()
    dateCounts = {} # for residential zip volumes
    dateSitecounts = {} # for local practice zip code volumes
    dateAgecounts = {} # for age chunk by residential zip volumes
    ageCounts = {} # for debugging - why no infants - rml april 30 ?
    esel = {'ezip': # django has a very neat way to inject sql
            'select DemogZip from esp_demog where esp_demog.id = esp_enc.EncPatient_id',
            'dob': 
            'select DemogDate_of_Birth from esp_demog where esp_demog.id = esp_enc.EncPatient_id'}
    # an extra select dict to speed up the foreign key lookup - note real SQL table and column names!
    if localIgnore: # use encounter site exclusions 
                    # from the exclude list in the espSSconf[sitename].py file
        allenc = Enc.objects.filter(EncEncounter_Date__gte=startDT, EncEncounter_Date__lte=endDT,
             EncEncounter_Site__in = localSiteUseCodes).extra(select=esel).values_list('ezip','dob',
            'EncEncounter_Date','EncEncounter_Site').iterator() 
            # yes - this works well to minimize ram    
    else:
        allenc = Enc.objects.filter(EncEncounter_Date__gte=startDT, 
        EncEncounter_Date__lte=endDT).extra(select=esel).values_list('ezip','dob',
            'EncEncounter_Date','EncEncounter_Site').iterator() # yes - this works well to minimize ram             
    zl = ziplen # eg use 5 - ignore rest
    for i,anenc in enumerate(allenc):
        if (i+1) % 10000 == 0:
            SSlogging.debug('AgeencDateVolumes at %d, %f /sec' % (i+1, i/(time.time() - started)))
        (z,dob,thisd,siteCode) = anenc # returned as a list of tuples by value_list
        age = makeAge(dob,thisd,ageChunksize) # small fraction have bad dates
        if age <> None:
            ageCounts.setdefault(age,0)
            ageCounts[age] += 1
            z = z[:zl] # corresponding zip
            dz = dateAgecounts.setdefault(thisd,{})
            az = dateAgecounts[thisd].setdefault(z,{})
            naz = dateAgecounts[thisd][z].setdefault(age,0)
            dateAgecounts[thisd][z][age] += 1
            dz = dateCounts.setdefault(thisd,{})
            az = dateCounts[thisd].setdefault(z,0)
            dateCounts[thisd][z] += 1
            siteZip = localSiteZips.get(siteCode,'Unknown')
            dateSitecounts.setdefault(thisd,{})
            dateSitecounts[thisd].setdefault(siteZip,{}) # eeesh.
            dateSitecounts[thisd][siteZip].setdefault(age,0)
            dateSitecounts[thisd][siteZip][age] += 1
    del allenc
    ak = ageCounts.keys()
    ak.sort()
    a = ['%d:%d' % (x, ageCounts[x]) for x in ak]
    SSlogging.info('*****AgeencDateVolumes, localIgnore = %s, age chunk counts=\n%s' % (localIgnore,'\n'.join(a)))
    return dateCounts,dateAgecounts,dateSitecounts


def findCaseFactIds(syndDef=[],syndName='',startDT=None,endDT=None,ziplen=5,localIgnore=True):
    """ revised to make the icd9fact record the basis for the report
    requires removing demogid redundancy for each synd/date/zip
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
        SSlogging.info('## %s Nofever: %d diags (+redundancies on patients in events)' % (syndName,len(list(nffacts))))
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
        SSlogging.info('### %s fever icds: %d icdmatch, %d +fever, %d notemp but icd9 fever' % (syndName, n1,
        n2,n3))
    caseids = nffacts + ffacts # already lists
    SSlogging.info('#### %s Total count = %d' % (syndName,len(caseids)))
    return caseids

def caseIdsToDateIds(caseids=[],ziplen=5,localIgnore=True,syndrome='?'):
    """
    easier to amalgamate by sitezip here than in the aggregate reporting
    specification creep from MDPH is more like specification stampede :(
    split out from preparing icd9 fact id list - now process icd9 facts into
    reporting structures - individual level xls and for aggregates AMDS and xls
    must remove demogId redundancy by syndrome/date/zip 
    """
    redundant = 0
    ignoreSite = 0
    ignoredSites = {}
    if caseids: # some - we need lots of additional info on each 'case' for reporting and redundancy filtering
        factids = icd9Fact.objects.filter(id__in=caseids).order_by('id') # recreate query set - keep in id order
        zips = [x.icd9Patient.DemogZip.split('-')[0] for x in factids] # get zips less -xxxx 
        dobs = [x.icd9Patient.DemogDate_of_Birth for x in factids] # get dobs  
        localSiteCodes = [x.icd9Enc.EncEncounter_Site for x in factids] 
        localZips = [localSiteZips.get(x,'Unknown') for x in localSiteCodes] # for Katherine...
        encdates = [x.icd9Enc.EncEncounter_Date for x in factids] # get encdates   
        encAges = [makeAge(dobs[i],encdates[i],ageChunksize) for i in range(len(encdates))]
        temperatures = [x.icd9Enc.EncTemperature for x in factids]
        icd9FactIds = [x.id for x in factids]
        encIds = [x.icd9Enc.id for x in factids] # fk lookup
        demogIds = [x.icd9Patient.id for x in factids]
        icd9codes = [x.icd9Code for x in factids]
        # need to remove redundancy on demog Id and date
        dateId = {} # this will be hard if we got to periods other than days? TODO: fixme...one day
        sitedateId = {} # for stampede
        for i,edate in enumerate(encdates): # reporting outermost is date
            id = demogIds[i] # this subject
            z = zips[i][:ziplen]            
            dateId.setdefault(edate,{})
            dateId[edate].setdefault(z,{})
            if dateId[edate][z].get(id,None) == None: # demogid not yet counted for this syndrome, date, zip
                # this step is crucial to remove multiple potential counting for a single syndrome/person/day
                aSite = localSiteCodes[i]
                if localSiteUseDict.get(aSite,None) or (not localIgnore): # site not important if not localIgnore     
                    age = encAges[i]
                    if age <> None: # may be null if duff dates
                        encId = encIds[i]
                        icd9FactId = icd9FactIds[i]
                        temperature = temperatures[i]
                        icd9code = icd9codes[i]
                        demogId = demogIds[i]
                        siteZip = localZips[i] # looked up from local site data
                        dob = dobs[i] # for debugging
                        dateId[edate][z][id] = (z,age,icd9FactId,encId,icd9code,demogId,edate,temperature,dob,siteZip)
                        # preserve entire record for line list
                        # TODO may need to expand this for more line list column versions
                        sitedateId.setdefault(edate,{})
                        sitedateId[edate].setdefault(siteZip,0)
                        sitedateId[edate][siteZip] += 1 # for aggregate reports by site zip
                else:
                    aSiteName = localSiteLookup.get(aSite,'%s?' % aSite)
                    n = ignoredSites.setdefault(aSiteName,0)
                    ignoredSites[aSiteName] += 1
                    ignoreSite += 1
                    # keep track of sites not being counted
            else:
                redundant += 1
        del factids # could be a big structure
        if localIgnore: # log some evidence of the effects...
            SSlogging.info('# %s Total localSite ignore site cases = %d, sites= %s' % (syndrome, ignoreSite,ignoredSites))
        SSlogging.info('## %s Total redundant ids for zip/date/syndrome = %d' % (syndrome,redundant))
        return dateId,sitedateId
    else:
        return {},{} # nada


def makeAMDS(sdate=None,edate=None,syndrome=None,encDateVols=None,cclassifier='ESPSS',ziplen=3,
    encAgeDateVols=None,doid=None,requ=None,minCount=0,crtime=None,localIgnore=False):
    """crude generator for xls for a period and 
    genesis at http://esphealth.org/trac/ESP/wiki/ESPSS
    rml april 27 2009 swine flu season?
    """

    def makeGeoHeader(ziplist=[]):
        """
        xml fragment easily isolated and faked
        not sure if we need a zero entry for every zip specified here.
        Prolly do...
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
        xml fragment easily isolated and faked
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

    def makeCounts(syndrome='?',aday={},edate='20080101',ziplist=[]):
        """ 
        all counts for a date by zip
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
            SSlogging.debug('!!!!#### processing syndrome %s for date %s' % (syndrome,thisdate))
            c = makeCounts(syndrome,dateId[thisdate],thisdate,ziplist)
            m += c
        m.append('</CountSet>')
        m.append('</AMDSQueryResponse>')
        return m  
    
    # main makeAMDS starts here
    SSlogging.info('makeAMDS now looking for %s at %s' % (syndrome, isoTime()))
    icdlist = syndDefs[syndrome] # icd list
    icdlist = syndDefs[syndrome] # icd list
    caseids = findCaseFactIds(syndDef=icdlist,syndName=syndrome,startDT=sdate,endDT=edate,
        ziplen=ziplen,localIgnore=localIgnore)
    # generate a simple vector of caseId encounter primary keys
    dateId,sitedateId = caseIdsToDateIds(caseids=caseids,ziplen=ziplen,localIgnore=localIgnore,syndrome=syndrome)
    # process it into the reporting structure - a dict as date->zip->age..counts and a dict of cases
    # now returns (z,age,icd9FactId,encId,icd9code,demogId,edate,temperature) = zids[id]
    if len(dateId) > 0:
        res = makeMessage(syndrome, dateId)
    else:
        res = []
    return res
# end makeAMDS


def generateAMDS(sdate='20090401',edate='20090431',minCount=0,ziplen=3,outdir='./'):
    """ test stub for AMDS xml generator
    On Thu, Apr 23, 2009 at 11:54 PM, Lee, Brian A. (CDC/CCHIS/NCPHI)
    (CTR) <fya1@cdc.gov> wrote:
    > I changed the root element to be <AMDSQueryResponse> since these
    > examples have two root elements (AMDSRecordSummary and CountSet). Other
    > than that, the data makes for great sample sets.
    """    
    dateZip,dateZipAge,dateSiteZipAge = AgeencDateVolumes(startDT=sdate,
      endDT=edate,localIgnore=False,ziplen=ziplen)
    # these are the volume counts of all encounters by date and zip, or date, zip and chunked year age 
    # or date, site seen zip and chunked age (!)
    # BL has agreed to add AllCount element to AMDS spec next revision - yay!
    doid='ESPSS@%s' % thisSite
    requ=thisRequestor
    crtime=isoTime(time.localtime())
    SSlogging.debug('crtime = %s' % crtime)
    fproto = os.path.join(outdir,'ESP%s_AMDS_zip%s_%s_%s_%s.xml')
    syndromes = syndDefs.keys() # syndromes
    syndromes.sort()
    for syndrome in syndromes: # get ready to write AMDS XML as a list of strings
        res = makeAMDS(sdate=sdate,edate=edate,syndrome=syndrome,minCount=minCount,
          encDateVols=dateZip,encAgeDateVols=dateZipAge,cclassifier=cclassifier,
          doid=doid,requ=requ,crtime=crtime,localIgnore=False,ziplen=ziplen)
        if len(res) > 0:
            fname = fproto % (thisSite,ziplen,syndrome,sdate,edate)
            f = open(fname,'w')
            f.write('\n'.join(res))
            f.write('\n')
            f.close()
            SSlogging.debug('## wrote %d rows to %s' % (len(res),fname))
  

def makeTab(sdate='20080101',edate='20080102',syndrome='ILI',ziplen=5,
    encDateVols={},encDateAgeVols={},encDateSiteVols={},localIgnore=True):
    """crude generator for xls
    rml april 27 2009 swine flu season?
    """

    def makeCounts(syndrome='?',aday={},siteaday={}, edate='20080101'):
        """ all counts for a date by residential zip
        and at Katherine's request, site zip
        """
        res = [] # residential zip
        ress = [] # site zip aggregate rows - need to do some fancy footwork - eesh.
        zips = aday.keys()
        if len(zips) == 0:
             SSlogging.info('## no events for %s on %s' % (syndrome, edate))
             return res,ress # empty
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
        # do it all again for site zips. Specification stampede - wheee...
        zips = siteaday.keys()
        if len(zips) == 0:
             SSlogging.info('## no site events for %s on %s' % (syndrome, edate))
             return res,ress # maybe empty
        zips.sort()
        alld = encDateSiteVols.get(edate,{}) # site encounter totals !
        SSlogging.debug('\n\n@@@@###### %s site makeCountstab %s: alld (%d) = \n###%s' % (syndrome,edate,len(alld),alld))
        SSlogging.debug('aday (%d) =\n###%s' % (len(aday),aday))   
        for i,z in enumerate(zips):
            zn = siteaday[z] # not length - is number of individual records in each zip for this date/synd
            if zn > 0: # can be empty because of the way it's constructed
                allencs = alld.get(z,None)
                if allencs:
                    alln = sum(allencs.values()) # dict keyed by age!
                else:
                    alln = 0
                if alln > 0:
                    if zn > alln:
                        SSlogging.warning('####! site syndrome counts %d > volume %d for zip %s, date %s, synd %s' % (zn,
                        alln,z,edate,syndrome))
                        allfrac = '? bug'
                    else:
                        f = (100.0*zn)/alln
                        allfrac = '%f' % f
                else:
                    allfrac = '###!! wtf None - no site all event count zip %s ?' % z
                    SSlogging.warning(allfrac)
                    alln = 0
                row = '\t'.join((edate,z,syndrome,'%d' % zn,'%d' % alln,allfrac))
                ress.append(row)
        return res,ress

            
    
    def makeLinelist(syndrome='?',aday={},edate='20080101'):
        """ make individual records
        """
        res = []
        zips = aday.keys()
        zips.sort()
        alld = encDateAgeVols.get(edate,{})
        allsd = encDateSiteVols.get(edate,{}) # for site volumes...eeeksssh
        SSlogging.debug('### MakeLinelist zips=',zips)
        for zipcode in zips:
            zids = aday[zipcode]
            idk = zids.keys()
            if len(idk) > 0: # can be empty because of the way we generate..
                idk.sort()
                alldz = alld.get(zipcode,{})
                if alldz == {}:
                    SSlogging.warning('###!! Makelinelist: alldz empty for syndrome %s zip %s' % (syndrome, zipcode)) 
                zipN = zipcode[:ziplen] # 5 or 3 digit zips configurable
                for id in idk:
                    (z,age,icd9FactId,encId,icd9code,demogId,edate,temperature,dob,siteZip) = zids[id] # whew 
                    allsdz = allsd.get(siteZip,{})
                    if allsdz == {}:
                        SSlogging.warning('###!! Makelinelist: allsdz empty for syndrome %s sitezip %s' % (syndrome, siteZip)) 
                    if age <> None:
                        alldza = alldz.get(age,0)
                        alldsza = allsdz.get(age,0)
                    else:
                        alldza = 0
                        alldsza = 0
                    if alldza == 0:
                        SSlogging.warning('###!! Makelinelist: 0 reszip count for age=%d,synd=%s,zipcode=%s' % (age,syndrome,zipN))
                    if alldsza == 0:
                        SSlogging.warning('###!! Makelinelist: 0 sitezip count for age=%d,synd=%s,sitezip=%s' % (age,syndrome,siteZip))
                    row = '\t'.join((syndrome,edate,z,siteZip,'%d' % age,icd9code,temperature,'%d' % alldza,'%d' % alldsza))
                    res.append(row)
        return res 
    
    
    def makeMessage(syndrome='?',dateId={}, sitedateId={}):
        """
        format a simple fake table delimited header row text.xls - return list of 
        ready to write strings
        """
        # provide sd,ed,ctime,ruser,doid
        m = ['edate\tzip_res\tsyndrome\tnsyndrome\tnallEnc\tpctsyndrome',] # amalg
        sm = ['edate\tzip_site\tsyndrome\tnsyndrome\tnallEnc\tpctsyndrome',] # site zip amalg
        lm = ['syndrome\tedate\tzip_res\tzip_seen\tage_5yrs\ticd9\ttemperature\tnencs_age_zip_res\tnencs_age_zip_site',] 
        # lm is list of strings for the line list
        # todo - add N all encs age zip_seen as well as zipres
        edk = dateId.keys()
        edk.sort()
        for thisdate in edk:
            SSlogging.debug('!!!!#### processing syndrome %s at %s' % (syndrome,isoTime()))
            thisdateId = dateId.get(thisdate,{}) # strange, one of these may be missing
            thissitedateId = sitedateId.get(thisdate,{})
            c,sc = makeCounts(syndrome,thisdateId,thissitedateId,thisdate)
            m += c
            sm += sc
            if True or syndrome == 'ILI': # all for the moment..
                c = makeLinelist(syndrome,dateId[thisdate],thisdate)
                lm += c
        return m,sm,lm  
    
    # main makeTab starts here
    icdlist = syndDefs[syndrome] # icd list
    caseids = findCaseFactIds(syndDef=icdlist,syndName=syndrome,startDT=sdate,endDT=edate,
        ziplen=ziplen,localIgnore=localIgnore)
    # generate a simple vector of caseId encounter primary keys
    dateId,sitedateId = caseIdsToDateIds(caseids=caseids,ziplen=5,localIgnore=localIgnore,syndrome=syndrome)
    # process it into the reporting structure - a dict as date->zip->age..counts and a dict of cases
    # now returns (z,age,icd9FactId,encId,icd9code,demogId,edate,temperature) = zids[id]
    res,sres,lres = makeMessage(syndrome, dateId, sitedateId) # specification gallop
    return res,sres,lres
# end makeTab  


def generateTab(sdate='20090401',edate='20090431',ziplen=5,outdir='./'):
    """ test wrapper for simple aggregate 
    date synd zip n nall pct
    and unit record tab delim generator
    date zip_residence zip_practice syndrome temp syndN allencN syndPct 
    """
    for i,localIgnore in enumerate((True,False)):
        ignoreMode = ['Excl','All'][i]
        encDateVols,encDateAgeVols,encDateSiteVols = AgeencDateVolumes(startDT=sdate,endDT=edate,
           localIgnore=localIgnore,ziplen=ziplen)
        fproto = os.path.join(outdir,'ESP%s_SyndAgg_zip%s_%s_%s_%s_%s.xls')
        lfproto = os.path.join(outdir,'ESP%s_SyndInd_zip%s_%s_%s_%s_%s.xls')
        syndromes = syndDefs.keys() # syndromes
        syndromes.sort()
        for syndrome in syndromes: # get ready to write tab delimited data as a list of strings
            res,sres,lres = makeTab(sdate=sdate,edate=edate,syndrome=syndrome,encDateVols=encDateVols,
               encDateAgeVols=encDateAgeVols,encDateSiteVols=encDateSiteVols,localIgnore=localIgnore)
            fname = fproto % (thisSite,'%d_Res' % ziplen,ignoreMode,syndrome,sdate,edate)
            f = open(fname,'w') 
            f.write('\n'.join(res))
            f.write('\n')
            f.close()
            SSlogging.debug('## wrote %d rows to %s' % (len(res),fname))
            fname = fproto % (thisSite,'%d_Site' % ziplen,ignoreMode,syndrome,sdate,edate)
            f = open(fname,'w') 
            f.write('\n'.join(sres))
            f.write('\n')
            f.close()
            SSlogging.debug('## wrote %d rows to %s' % (len(sres),fname))
            if len(lres) > 1: # makeTab only returns header row except for ILI at present 
                fname = lfproto % (thisSite,ziplen,ignoreMode,syndrome,sdate,edate)
                f = open(fname,'w')
                f.write('\n'.join(lres))
                f.write('\n')
                f.close()
                SSlogging.debug('## wrote %d rows to %s' % (len(lres),fname))
        del encDateVols,encDateAgeVols,encDateSiteVols   

def makeEncVols(sdate='20060701',edate='20200101',outdir='./',ziplen=5):
    """ need volumes for espss over all time
    write site and residential total encs by age
    eg date zip all 0 5..80 85
    limit to zips with > 10 cases over entire period arbitrarily
    """
    limit = 10
    fproto = os.path.join(outdir,'ESP%s_AllEnc_zip%d_%s_%s.xls')
    localIgnore = 1
    ziplen = 5
    encDateVols,encDateAgeVols,encDateSiteVols = AgeencDateVolumes(startDT=sdate,endDT=edate,
           localIgnore=localIgnore,ziplen=ziplen)
    ages = [x for x in range(0,90,5)]
    agess = ['%d' % x for x in ages]
    head = ['edate','zip','all'] + agess
    head = '\t'.join(head)
    sres = [head,]
    rres = [head,] # residential
    dk = encDateSiteVols.keys()
    dk.sort()
    allrz = {}
    allsz = {} # keep tabs of all
    for d in dk: # 
        zk = encDateVols.get(d,{}).keys() # if any
        for z in zk:
            allrz.setdefault(z,0) # keep trac of res zips
            allrz[z] += 1
        zk = encDateSiteVols.get(d,{}).keys() # if any
        for z in zk:
            allsz.setdefault(z,0) # keep trac of site zips
            allsz[z] += 1
    rzk = allrz.keys()
    szk = allsz.keys()
    for d in dk: # now make report with empty days and zips!
        for z in rzk: # for all possible zips
            if allrz[z] > limit:
                rt = 0 
                resn = []
                dz = encDateAgeVols[d].get(z,{}) # may be empty
                for a in ages: # all ages
                    n = dz.get(a,0)
                    rt += n # total
                    resn.append(n) # res counts by age
                row = [d,z,'%d' % rt] + ['%d' % x for x in resn] # string    
                rres.append(row) # for residential encounter report
        for z in szk: # for all possible zips
            if allsz[z] > limit:
                st = 0 
                siten = []
                dz = encDateSiteVols[d].get(z,{}) # may be empty
                for a in ages: # all ages
                    n = dz.get(a,0)
                    st += n # total
                    siten.append(n) # res counts by age
                row = [d,z,'%d' % st] + ['%d' % x for x in siten] # string    
                sres.append(row) # for residential encounter report
    fname = fproto % (thisSite,ziplen,'Excl','Site')
    f = open(fname,'w')
    f.write('\n'.join(['\t'.join(x) for x in sres]))
    f.write('\n')
    f.close()
    fname = fproto % (thisSite,ziplen,'Excl','Res')
    f = open(fname,'w')
    f.write('\n'.join(['\t'.join(x) for x in rres]))
    f.write('\n')
    f.close()
    
            


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        sdate = sys.argv[1]
        edate = sys.argv[2]
    else:
        SSlogging.info('## supply sdate and edate as command line parameters to change the default dates')
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        sdate= '%d%02d%02d' % (yesterday.year,yesterday.month,yesterday.day)
        edate= '%d%02d%02d' % (today.year,today.month,today.day)
    if len(sys.argv) >= 4:
        ziplen = int(sys.argv[3])
    else:
        ziplen = 5
        print '## supply ziplen (eg 3 or 5) as the third parameter to change from default %d' % ziplen
    if len(sys.argv) >= 5:
        outdir = sys.argv[4]
    else:
        outdir = '/home/ESP/SS'
        print '## supply the output directory path as the fourth parameter to change from default %s' % outdir
    SSlogging.info('espSS.py starting at %s. sdate=%s, edate=%s, ziplen=%d, outdir=%s' % (isoTime(),sdate,edate,ziplen,outdir))
    #generateTab(ziplen=ziplen,sdate=sdate,edate=edate,outdir=outdir)
    #generateAMDS(ziplen=3,minCount=0,sdate=sdate,edate=edate,outdir=outdir)
    #generateAMDS(ziplen=5,minCount=0,sdate=sdate,edate=edate,outdir=outdir)
    makeEncVols(sdate='20060701',edate='20200101',outdir='./',ziplen=5)

