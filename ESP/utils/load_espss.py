# fill espss mapss data structure from an individual espss xls report 
# crude quick generator for testing
# and development espss ssmap application
# major refactoring may 19 ross
# more generalised...with aim to integrate with esp tables

"""
from geopy import geocoders
g = geocoders.Google('ABQIAAAA8hCh4ZOXEq9d21R-RUiHhxQ8137lu9UdsPO-DxiAof2VAbzYxRRxwv5iZ5uHbMH0m5bmwZ2Hz1tzAg')
>>> g.geocode('02445')
(u'Brookline, MA 02445, USA', (42.332802700000002, -71.138910100000004))

"""

import  os, sys, time, datetime, django, MySQLdb

sys.path.insert(0, '/home/ESP/ESP') # eg '/var/www/html/esphealth'
sys.path.insert(0, '/home/ESP') # eg '/var/www/html/esphealth'

os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

VERSION = 0.01
from ESP.ssmap.models import eventdate, geoplace, rule, event, enc

########For logging
from ESP.settings import *
sslogging= getLogging('load_espss.py_%s' % VERSION, debug=0)
from geopy import geocoders
ESPGKEY='ABQIAAAA8hCh4ZOXEq9d21R-RUiHhxQ8137lu9UdsPO-DxiAof2VAbzYxRRxwv5iZ5uHbMH0m5bmwZ2Hz1tzAg'
goog = geocoders.Google(ESPGKEY)
ageChunksize=5


class iterCursor:
    '''Fake a cursor in MySQL
    Iterable results from a mysql connection
    this one doesn't suck (literally) the entire
    record set into ram - a stoopid thing to do when
    there are millions of records - and not much ram
    SSCursor is the thing it seems'''

    def __init__(self, connection, query, data = None):
            self._cursor = connection.cursor(SSCursor)
            if data:
                self._cursor.execute(query, data)
            else:
                self._cursor.execute(query)    

    def __iter__(self):
            while True:
                    result = self._cursor.fetchone()
                    if not result:
                        raise StopIteration
                    yield result



def timenow(t=None):
    if t == None:
        t = datetime.datetime.now()
    return t.strftime('%Y-%m-%d')

def getZipPlace(z='',badzips={}):
    """ lookup or add
       geoname returns 
       (u'Brookline, US 02445', (42.318097000000002, -71.143697000000003))
    """
    p = badzips.get(z,None)
    if p:
        badzips[z] += 1 
        return None
    p = geoplace.objects.filter(place__exact=('zip:%s' % z))
    if len(p) > 0:
        return p[0]
    else:
        name = None
        town = None
        g = list(goog.geocode('%s' % z,exactly_one=False))
        if len(g) == 0:
            sslogging.error( '## getZipPlace: error %s yielded nada' % z)
            town = None        
        if len(g) > 1:
            sslogging.error('## getZipPlace: error %s yielded %s - using first' % (z,g))
        try:
            name,(la,lo) = g[0] # take the first of many
        except:
            town = None
        if name:
            town = None
            name = name.replace(',','')
            ns = name.split(' ')
            try:
                if ns[-2] == z: # good
                	town = ' '.join(ns[:-2])
                else:
                   sslogging.error('## getZipPlace: short ns = %s' % ns)
            except:
                sslogging.error('## getZipPlace: wierd ns = %s' % ns)
        else:
            town = None 
            sslogging.error('## getZipPlace: no name from g = %s ' % g)
    if not town:
        sslogging.error('## getZipPlace: google maps geocode error for %s' % (z))
        badzips.setdefault(z,0)
        badzips[z] += 1 
        return None
    p = geoplace()
##     place = models.CharField(max_length=50,primary_key=True,unique=True)
##    la = models.DecimalField(max_digits=9, decimal_places=6)
##    lo = models.DecimalField(max_digits=9, decimal_places=6)
##    zip = models.CharField(max_length=10,db_index=True)
##    address = models.TextField()
##    narrative = models.TextField()
    p.place = 'zip:%s' % z
    try:
        laf = '%9.6f' % la
    except:
        laf = '%s' % la
    try:
        lof = '%9.6f' % lo
    except:
        lof = '%s' % lo
    p.la = laf
    p.lo = lof
    p.zipcode = z
    p.town = town
    p.narrative="google maps on %s, as %s" % (timenow(),g)
    p.save()
    return p   

def doload(fname=''):
    """
Synd	Date	Zip_Res	Zip_Seen	Age_5Yrs	ICD9code	Temperature	NEncs_Age_Zip_Res	NEncs_Age_Zip_Site
ILI	20060701	1876	2184	30	462	100.2	3	19
ILI	20060701	2122	2215	15	79.99	100.5	2	15

    """
    badzips = {'Unknown':0}
    f = file(fname,'r')
    for i,row in enumerate(f):
      if i < 1000:
        rowl = row.strip().split('\t')
        if i == 0:
            head = rowl
        else:
            if i % 1000 == 0:
                sslogging.info('at %d' % i)
            synd,adate,zip_res,zip_seen,age,icd,t,nencs_age_zip_res,nencs_age_zip_site = rowl
            adatedt = '%04d-%02d-%02d' % (int(adate[0:4]),int(adate[4:6]),int(adate[6:8]))
            if eventdate.objects.filter(edate__exact = adatedt).count() == 0:
                e = eventdate()
                e.edate = adatedt
                e.save() # cache as foreign key
            p_seen = getZipPlace(zip_seen,badzips)
            p_res = getZipPlace(zip_res,badzips)
            if p_seen or p_res:
                c = event()
                ##class eventdate(models.Model):
                ##   rule = models.ForeignKey('rule')
                ##   edate = models.ForeignKey('edate') # this allows us to get all events on any date
                ##   res_place = models.ForeignKey('geoplace',related_name='res')
                ##   seen_place = models.ForeignKey('geoplace',related_name='seen')
                ##   temp = models.FloatField()
                ##   icd = models.TextField()
                ##   age = models.IntegerField()
                r = rule.objects.filter(rulename__exact = synd)
                if r.count() > 0:
                    c.rule = r[0]
                    edateToday = eventdate.objects.filter(edate__exact = adatedt)
                    if len(edateToday) > 0:
                        edateToday = edateToday[0]
                    else:
                        e = eventdate()
                    e.edate = adatedt
                    e.save() # cache as foreign key
                    edateToday = e
                    c.edate=edateToday
                    if p_seen:
                        c.seen_place=p_seen
                    else:
                        c.seen_place=p_res # fake!
                    if p_res:
                        c.res_place=p_res
                    else:
                        c.res_place=p_seen
                    try:
                        ft=float(t)
                    except:
                        ft = 0.0
                    c.temp = ft
                    c.icd = icd
                    c.age = age
                    c.save()
                else:
                    sslogging.error('### cannot find rule corresponding to %s' % synd)
    f = file('badzips.xls','w')
    s = 'badzipc\tn\n'
    f.write(s)
    print s
    bk = badzips.keys()
    bk.sort()
    for z in bk:
        s = '%s\t%d\n' % (z,badzips[z])
        f.write(s)
        sslogging.info( s )
    f.close()

def makeAge(dob='20070101',edate='20080101',chunk=ageChunksize):
    """return age in year chunks for mdph ILI reports
    for d in ['20000101','20010101','20030204']:
    for e in ['20040101','20050101','20030604']:
        print makeAge(dob=d,edate=e,chunk=5)

    """
    if len(dob) < 8:
        sslogging.error('### Short (<8) dob "%s" in makeAge' % dob)
        return None
    else:
        yy,mm,dd = map(int,[dob[:4],dob[4:6],dob[6:8]])
        bd = datetime.date(yy,mm,dd)
    if len(edate) < 8:
        sslogging.error('### Short (<8)edate "%s" in makeAge' % edate)
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
    # try to trick namespace
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'
    import django
    import ESP.settings 
    from ESP.esp.models import Enc,Demog
    from ESP.utils.espSSconfATRIUS import btzipdict,localSiteUseDict,localSiteLookup,localSiteExcludeCodes,localSiteUseCodes, \
      localSiteZips, ILIdef,HAEMdef,LESIONSdef,LYMPHdef,LGIdef,UGIdef,NEUROdef,RASHdef,RESPdef    
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
        if (i+1) % 500000 == 0:
            s = 'AgeencDateVolumes at %d, %f /sec' % (i+1, i/(time.time() - started))
            sslogging.info(s)
            print s
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
    sslogging.info('*****AgeencDateVolumes, localIgnore = %s, age chunk counts=\n%s' % (localIgnore,'\n'.join(a)))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'espss.settings'
    return dateCounts,dateAgecounts,dateSitecounts


    
def loadEnc(sdate='20060701',edate='20200101',ziplen=5):
    """
    zeros are killing us. 10 to 1. This is silly. Must default to 0 if we have no record.

   edate = models.ForeignKey('edate')
   place = models.ForeignKey('geoplace')
   agecounts = models.TextField() # use this to store age counts eg
   total = models.IntegerField()
    need volumes for espss over all time
    write site and residential total encs by age
    eg date zip all 0 5..80 85
    limit to zips with > 10 cases over entire period arbitrarily
    """
    badzips = {}
    limit = 10
    localIgnore = 1
    ziplen = 5
    encDateVols,encDateAgeVols,encDateSiteVols = AgeencDateVolumes(startDT=sdate,endDT=edate,
           localIgnore=localIgnore,ziplen=ziplen)
    ages = [x for x in range(0,90,ageChunksize)]
    agess = ['%d' % x for x in ages]
    dk = encDateSiteVols.keys()
    dk.sort()
    allrz = {}
    allsz = {} # keep tabs of all
    for d in dk: # 
        adatedt = '%04d-%02d-%02d' % (int(d[0:4]),int(d[4:6]),int(d[6:8]))  
        edateToday = eventdate.objects.filter(edate__exact=adatedt)
        if len(edateToday) < 1:
            e = eventdate()
            e.edate = adatedt
            e.save() # cache as foreign key
        zk = encDateVols.get(d,{}).keys() # if any
        for z in zk:
            allrz.setdefault(z,0) # keep trac of res zips
            allrz[z] += 1
        zk = encDateSiteVols.get(d,{}).keys() # if any
        for z in zk:
            allsz.setdefault(z,0) # keep trac of site zips
            allsz[z] += 1
    rzk = [x for x in allrz.keys() if x > limit] # ignore very rarely reported zips
    szk = [x for x in allsz.keys() if x > limit]
    for d in dk: # now make report with empty days and zips!
        dd = encDateAgeVols.get(d,{})
        for z in rzk: # for all useable zips
            rg = getZipPlace(z,badzips)
            if rg:
                rt = 0 
                resn = []
                ddz = dd.get(z,{}) # may be empty
                for a in ages: # all ages
                    n = ddz.get(a,0)
                    rt += n # total
                    resn.append(n) # res counts by age
                if rt == 0:
                    break # lets not write these - 10 to 1
                resrow = [d,z,'%d' % rt] + ['%d' % x for x in resn] # string
                adatedt = '%04d-%02d-%02d' % (int(d[0:4]),int(d[4:6]),int(d[6:8]))  
                edateToday = eventdate.objects.filter(edate__exact = adatedt)[0]
                e = enc.objects.filter(edate__exact = edateToday, place__exact = rg) # need one for each of these
                if len(e) > 0:
                    e = e[0]
                else:
                    e = enc() # new encounter date record
                e.edate = edateToday
                e.agecounts = '\t'.join(resrow)
                e.place = rg
                e.total = rt
                e.save()

        dd = encDateSiteVols.get(d,{})
        for z in szk: # for all possible zips
            rg = getZipPlace(z,badzips)
            if rg:
                st = 0 
                siten = []
                ddz = dd.get(z,{}) # may be empty
                for a in ages: # all ages
                    n = ddz.get(a,0)
                    st += n # total
                    siten.append(n) # res counts by age
                if st == 0:
                    break
                siterow = [d,z,'%d' % st] + ['%d' % x for x in siten] # string    
                adatedt = '%04d-%02d-%02d' % (int(d[0:4]),int(d[4:6]),int(d[6:8]))  
                edateToday = eventdate.objects.filter(edate__exact = adatedt)[0]
                e = enc.objects.filter(edate__exact = edateToday, place__exact = rg) # need one for each of these
                if len(e) > 0:
                    e = e[0]
                else:
                    e = enc() # new encounter date record
                e.edate = edateToday
                e.agecounts = '\t'.join(resrow)
                e.place = rg
                e.total = st
                e.save()
            else:
                sslogging.error('## loadenc missing geoplace for key=%s' % gk)
    f = file('badzips.xls','w')
    s = 'badzipc\tn\n'
    f.write(s)
    bk = badzips.keys()
    bk.sort()
    for z in bk:
        s = '%s\t%d' % (z,badzips[z])
        f.write(s)
        f.write('\n')
        sslogging.info( s )
    f.close()
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = '/home/ESP/espss/ESPAtrius_SyndInd_zip5_Excl_ILI_20060701_20090517.xls'
        # '/home/rerla/espss/ESPAtrius_SyndInd_zip5_Excl_ILI_20060701_20090516.xls'
        sslogging.info( 'Provide infile name as parameter to over ride default %s' % fname)
        sslogging.info(  'Reading %s' % fname )
        #doload(fname=fname)
        loadEnc(sdate='20071014',edate='20200101',ziplen=5)
