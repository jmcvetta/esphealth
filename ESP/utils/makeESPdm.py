
import MySQLdb,sys,os,glob,time,datetime

try:
    import psyco
    psyco.full()
except:
    print 'no psyco :-('

nvalsperinsert = 10000 # this speeds things up..

debug = 1
esp = MySQLdb.Connect('localhost','ESP','3spuser2006')
cursor = esp.cursor()
dictcursor = esp.cursor(MySQLdb.cursors.DictCursor)
icdfact = 'esp.icd9Fact'
icd9table = 'esp.esp_icd9'

def makeICD9Fact():
    """ version with the actual code rather than a foreign key
    """
    icdFact = 'esp.icd9Fact'
    varss = """id int unsigned auto_increment, icd9 varchar(10),
    encId int unsigned not null, demogId int unsigned not null, encDate char(10), index icdindex 
(icd9), index dateindex (encDate), primary key (id)"""
    iinsert = "id,icd9,encId,demogId,encDate"
    insertsql = '''insert into esp.icd9Fact (%s) values (%%s,%%s,%%s,%%s,%%s)''' % iinsert
    sql = 'drop table if exists %s' % icdFact
    cursor.execute(sql)
    sql = 'create table %s (%s)' % (icdFact,varss)
    cursor.execute(sql)
    sql = 'select * from esp.esp_icd9'
    cursor.execute(sql)
    nrows = 0
    insertme = []
    offset = 0
    fetch = 5000
    nrows = 0
    started = time.time()
    while 1:
        sql = '''select id, EncPatient_id, EncEncounter_Date, EncICD9_Codes
        from esp.esp_enc limit %d offset %d''' % (fetch,offset)
        cursor.execute(sql)
        res = cursor.fetchall()
        if len(res) == 0:
            break
        offset += len(res)
        for nextenc in res:
            (eid,epid,edate,ecodes) = nextenc
            clist = ecodes.split()
            if len(edate.strip()) < 8:
                if len(edate) == 6:
                    edate = '%s01' % edate
                else:
                    edate = "?"
            for icd in clist:
                newrec = (None,icd,eid,epid,edate)
                insertme.append(newrec)
        if len(insertme) >= nvalsperinsert:
            cursor.executemany(insertsql,insertme)
            esp.commit()
            nrows += len(insertme)
            insertme = []
            dur = time.time() - started
            print '### %d icd9 facts inserted, %5.1f/sec' % (nrows,nrows/dur)
    if len(insertme) > 0: # stragglers
        cursor.executemany(insertsql,insertme)
        esp.commit()
        nrows += len(insertme)
        insertme = []
    cursor.close()
    esp.close()
    print '### %d icd9 facts inserted' % nrows




def dsplit(d='20070101'):
    if len(d) <> 8:
        print 'duff date %s in dsplit' % d                 
        dd=0
        yy=0                
        mm=0
    else:
        yy,mm,dd = map(int,[d[:4],d[4:6],d[6:8]])        
    return yy,mm,dd


def cohort(ages=["ALL"],genders=["ALL"],races=["ALL"],pcps=["ALL"],period=None):
    """return a set of demogIds compatible with the filter settings
    period refers to a date start to end where the subject was somewhere between the
    high and low ages passed in. Note that generally, subsequent filters will need to reapply the
    age check at the actual event because this crude filter tries to be overinclusive - any demogId
    who could have something happen during period within constraints of ages.
    
    mysql> describe esp_demog;
    +----------------------------+--------------+------+-----+---------------------+----------------+
    | Field                      | Type         | Null | Key | Default             | Extra          |
    +----------------------------+--------------+------+-----+---------------------+----------------+
    | id                         | int(11)      |      | PRI | NULL                | auto_increment |
    | DemogPatient_Identifier    | varchar(20)  |      | MUL |                     |                |
    | DemogMedical_Record_Number | varchar(20)  |      | MUL |                     |                |
    | DemogLast_Name             | varchar(199) |      |     |                     |                |
    | DemogFirst_Name            | varchar(199) |      |     |                     |                |
    | DemogMiddle_Initial        | varchar(199) |      |     |                     |                |
    | DemogSuffix                | varchar(199) |      |     |                     |                |
    | DemogAddress1              | varchar(200) |      |     |                     |                |
    | DemogAddress2              | varchar(100) |      |     |                     |                |
    | DemogCity                  | varchar(50)  |      |     |                     |                |
    | DemogState                 | varchar(20)  |      |     |                     |                |
    | DemogZip                   | varchar(20)  |      |     |                     |                |
    | DemogCountry               | varchar(20)  |      |     |                     |                |
    | DemogAreaCode              | varchar(20)  |      |     |                     |                |
    | DemogTel                   | varchar(100) |      |     |                     |                |
    | DemogExt                   | varchar(50)  |      |     |                     |                |
    | DemogDate_of_Birth         | varchar(20)  |      |     |                     |                |
    | DemogGender                | varchar(20)  |      |     |                     |                |
    | DemogRace                  | varchar(20)  |      |     |                     |                |
    | DemogHome_Language         | varchar(20)  |      |     |                     |                |
    | DemogSSN                   | varchar(20)  |      |     |                     |                |
    | DemogProvider_id           | int(11)      | YES  | MUL | NULL                |                |
    | DemogMaritalStat           | varchar(20)  |      |     |                     |                |
    | DemogReligion              | varchar(20)  |      |     |                     |                |
    | DemogAliases               | varchar(250) |      |     |                     |                |
    | DemogMotherMRN             | varchar(20)  |      |     |                     |                |
    | DemogDeath_Date            | varchar(200) |      |     |                     |                |
    | DemogDeath_Indicator       | varchar(30)  |      |     |                     |                |
    | DemogOccupation            | varchar(199) |      |     |                     |                |
    | lastUpDate                 | datetime     |      | MUL | 0000-00-00 00:00:00 |                |
    | createdDate                | datetime     |      |     | 0000-00-00 00:00:00 |                |
    +----------------------------+--------------+------+-----+---------------------+----------------+
    31 rows in set (0.00 sec)

    mysql> select DemogRace, count(*) from esp_demog group by DemogRace order by DemogRace;
    +--------------+----------+
    | DemogRace    | count(*) |
    +--------------+----------+
    |              |   354104 |
    | ALASKAN      |        5 |
    | ASIAN        |     7600 |
    | BLACK        |    23440 |
    | CAUCASIAN    |   159696 |
    | HISPANIC     |     7229 |
    | INDIAN       |       25 |
    | NAT AMERICAN |      278 |
    | NATIVE HAWAI |      127 |
    | OTHER        |     2863 |
    | PATIENT DECL |     1556 |
    +--------------+----------+
    11 rows in set (9.77 sec)
    """
    all = "ALL"
    demogtable = 'esp.esp_demog'
    g = None
    r = None
    alow = 0
    ahigh = 999
    res = []
    if period:
        pstart,pend = period.split(',')
        psyy,psmm,psdd = dsplit(pstart)
        peyy,pemm,pedd = dsplit(pend)       
        pstart = datetime.date(psyy,psmm,psdd)
        pend = datetime.date(peyy,pemm,pedd)        
    if ages <> all:
        alow,ahigh = map(int,ages.split(',')) # we hope
        alow = datetime.timedelta(365.25*alow)
        ahigh = datetime.timedelta(365.25*ahigh)
    if genders <> all:
        g = genders.split(',')
        gdict = dict(zip(g,g))
    if races <> all:
        r = races.split(',')
        rdict = dict(zip(r,r))
    offset = 0
    fetch = 5000
    nrows = 0
    started = time.time()
    loop = 0
    while 1:
        loop += 1
        if loop % 10 == 0:
            dur = time.time()-started
            print 'offset = %d at %5.2f rec/sec' % (offset,offset/dur)
        sql = 'select * from %s limit %d offset %d ' % (demogtable,fetch,offset)
        dictcursor.execute(sql)
        dres = dictcursor.fetchall()
        if len(dres) == 0:
            break
        offset += len(dres)
        for d in dres:
            keep = 1
            if r:
                keep = rdict.get(d['DemogRace'],0)
            if g:
                keep = rdict.get(d['DemogGender'],0)        
            if ages <> all:
                dobs = d['DemogDate_of_Birth']
                if len(dobs.strip()) == 8:
                    yy = int(dobs[:4])
                    mm = int(dobs[4:6])
                    dd = int(dobs[6:8])
                    dob = datetime.date(yy,mm,dd)
                    lowage = pstart - dob
                    highage = pend - dob
                    if lowage > ahigh or highage < alow: #never within age range for entire period
                        keep = 0
                else:
                    keep = 0
                    print 'id %d, dobs = %s' % (d['id'],dobs)
            if keep:
                res.append(d) #(d['id']) # just keep ids ? could probably keep entire d object?
    print 'cohort returning %d - %s' % (len(res),res[:10])
    return res      


def exposure(cohort=None,icd9=[],rx=[],lx=[],ix=[],period=None):
    """return all relevant records matching icd9 codes,rx,lx,ix during period
    idea is to find all members of a cohort who have had any of the relevant exposure
    codes during the period
    Lists are returned containing relevant record ids in enc,rx,lx,ix
    """
    matched = []
    if period:
        pstart,pend = period.split(',')
        psyy,psmm,psdd = dsplit(pstart)
        peyy,pemm,pedd = dsplit(pend)       
        pstart = datetime.date(psyy,psmm,psdd)
        pend = datetime.date(peyy,pemm,pedd)        
    ids = [x['id'] for x in cohort]
    iddict = dict(zip(ids,ids)) # for fast lookup
    icddict = dict(zip(icd9,icd9))
    icds = ["%s" % x for x in icd9] # make a list of strings
    icds = '(%s)' % ','.join(icds)
    rxs = ["%s" % x for x in rx] # make a list of strings
    rxs = '(%s)' % ','.join(rxs)
    lxs = ["%s" % x for x in lx] # make a list of strings
    lxs = '(%s)' % ','.join(lxs)
    ixs = ["%s" % x for x in ilx] # make a list of strings
    ixs = '(%s)' % ','.join(ixs)
    rxdict = dict(zip(rx,rx))
    lxdict = dict(zip(lx,lx))
    ixdict = dict(zip(ix,ix))
    ricd9 = [] # records we find matching
    rrx = []
    rlx = []
    rix = []
    """
    mysql> describe icd9Fact;
    +---------+------------------+------+-----+---------+----------------+
    | Field   | Type             | Null | Key | Default | Extra          |
    +---------+------------------+------+-----+---------+----------------+
    | id      | int(10) unsigned |      | PRI | NULL    | auto_increment |
    | icd9    | varchar(10)      | YES  | MUL | NULL    |                |
    | encId   | int(10) unsigned |      |     | 0       |                |
    | demogId | int(10) unsigned |      |     | 0       |                |
    | encDate | varchar(10)      | YES  | MUL | NULL    |                |
    +---------+------------------+------+-----+---------+----------------+
    5 rows in set (0.00 sec)
    """
    if len(icd9) > 0:
        if period: # work with datetime date and timedelta objects
            pstart,pend = period.split(',')
            psyy,psmm,psdd = dsplit(pstart)
            peyy,pemm,pedd = dsplit(pend)       
            pstart = datetime.date(psyy,psmm,psdd)
            pend = datetime.date(peyy,pemm,pedd)        
        ids = [x['id'] for x in cohort]
        iddict = dict(zip(ids,ids)) # for fast lookup
        icddict = dict(zip(icd9,icd9)) # for fast lookup
        icds = ["%s" % x for x in icd9] # make a list of strings for sql
        icds = '(%s)' % ','.join(icds)
        """
        mysql> describe icd9Fact;
        +---------+------------------+------+-----+---------+----------------+
        | Field   | Type             | Null | Key | Default | Extra          |
        +---------+------------------+------+-----+---------+----------------+
        | id      | int(10) unsigned |      | PRI | NULL    | auto_increment |
        | icd9    | varchar(10)      | YES  | MUL | NULL    |                |
        | encId   | int(10) unsigned |      |     | 0       |                |
        | demogId | int(10) unsigned |      |     | 0       |                |
        | encDate | varchar(10)      | YES  | MUL | NULL    |                |
        +---------+------------------+------+-----+---------+----------------+
        5 rows in set (0.00 sec)
        """
        sql = 'select encId,demogId,encDate from %s where icd9 in %s' % (icdfact,icds)
        dictcursor.execute(sql)
        started = time.time()
        loop = 0
        while 1:
            loop += 1
            if loop % 10 == 0:
                dur = time.time()-started
                print 'offset = %d at %5.2f rec/sec' % (loop,loop/dur)         
            i = dictcursor.fetchone()
            if not i:
                break
            dId = i['demogId']
            encId = i['encId']
            if iddict.get(dId,None): # score = this id has one of the icds
                if period:
                    dobs = i['encDate']
                    if len(dobs.strip()) == 8:
                        yy = int(dobs[:4])
                        mm = int(dobs[4:6])
                        dd = int(dobs[6:8])
                        dobs = datetime.date(yy,mm,dd)
                        if dobs >= pstart and dobs < pend:
                            ricd9.append(encId)
                else: # if no period, all
                    ricd9.append((encId,dId)) # tuple - encounter and demogId
    print '# returning %d icd9 matches - %s' % (len(ricd9),ricd9[:20])        
    if len(rx) > 0:
        """
        mysql> describe esp_rx;
        +-------------------------+--------------+------+-----+---------------------+----------------+
        | Field                   | Type         | Null | Key | Default             | Extra          |
        +-------------------------+--------------+------+-----+---------------------+----------------+
        | id                      | int(11)      |      | PRI | NULL                | auto_increment |
        | RxPatient_id            | int(11)      |      | MUL | 0                   |                |
        | RxMedical_Record_Number | varchar(20)  |      | MUL |                     |                |
        | RxOrder_Id_Num          | varchar(20)  |      |     |                     |                |
        | RxProvider_id           | int(11)      | YES  | MUL | NULL                |                |
        | RxOrderDate             | varchar(20)  |      |     |                     |                |
        | RxStatus                | varchar(20)  |      |     |                     |                |
        | RxDrugName              | longtext     |      |     |                     |                |
        | RxDrugDesc              | longtext     |      |     |                     |                |
        | RxNational_Drug_Code    | varchar(20)  |      |     |                     |                |
        | RxDose                  | varchar(200) |      |     |                     |                |
        | RxFrequency             | varchar(200) |      |     |                     |                |
        | RxQuantity              | varchar(200) |      |     |                     |                |
        | RxRefills               | varchar(200) |      |     |                     |                |
        | RxRoute                 | varchar(200) |      |     |                     |                |
        | RxStartDate             | varchar(20)  |      |     |                     |                |
        | RxEndDate               | varchar(20)  |      |     |                     |                |
        | lastUpDate              | datetime     |      | MUL | 0000-00-00 00:00:00 |                |
        | createdDate             | datetime     |      |     | 0000-00-00 00:00:00 |                |
        +-------------------------+--------------+------+-----+---------------------+----------------+
        19 rows in set (0.00 sec)
        """
        sql = 'select id,RxPatient_id,RxOrderDate from esp_rx where RxDrugName in %s' % rxs
        dictcursor.execute(sql)
        while 1:
            i = dictcursor.fetchone()
            if not i:
                break
            dId = i['RxPatient_id']
            rxId = i['id']
            if iddict.get(dId,None): # score = this id has one of the icds
                if period:
                    dobs = i['RxOrderDate']
                    if len(dobs.strip()) == 8:
                        yy = int(dobs[:4])
                        mm = int(dobs[4:6])
                        dd = int(dobs[6:8])
                        dobs = datetime.date(yy,mm,dd)
                        if dobs >= pstart and dobs < pend:
                            rrx.append((rxId,dId))
                else: # if no period, all
                    rrx.append((rxId,dId)) # tuple - rxId and demogId for quick lookup of details for reporting
    return ricd9, rrx        
    
        
def exposureICD(cohort=None,icd9=[], period=None):
    """return all relevant records from cohort demogIds with any matching icd9 codes in
    an encounter during period. Uses the icd9Fact table to deconvolve the encounter
    icd9 list
    idea is to find all members of a cohort who have had any of the relevant exposure
    codes during the period
    List returned containing relevant record ids as a tuple (demogId,encId)
    """
    ricd9 = [] # records we find matching
    if len(icd9) > 0:
        matched = []
        if period: # work with datetime date and timedelta objects
            pstart,pend = period.split(',')
            psyy,psmm,psdd = dsplit(pstart)
            peyy,pemm,pedd = dsplit(pend)       
            pstart = datetime.date(psyy,psmm,psdd)
            pend = datetime.date(peyy,pemm,pedd)        
        ids = [x['id'] for x in cohort]
        iddict = dict(zip(ids,ids)) # for fast lookup
        icddict = dict(zip(icd9,icd9)) # for fast lookup
        icds = ["%s" % x for x in icd9] # make a list of strings for sql
        icds = '(%s)' % ','.join(icds)
        """
        mysql> describe icd9Fact;
        +---------+------------------+------+-----+---------+----------------+
        | Field   | Type             | Null | Key | Default | Extra          |
        +---------+------------------+------+-----+---------+----------------+
        | id      | int(10) unsigned |      | PRI | NULL    | auto_increment |
        | icd9    | varchar(10)      | YES  | MUL | NULL    |                |
        | encId   | int(10) unsigned |      |     | 0       |                |
        | demogId | int(10) unsigned |      |     | 0       |                |
        | encDate | varchar(10)      | YES  | MUL | NULL    |                |
        +---------+------------------+------+-----+---------+----------------+
        5 rows in set (0.00 sec)
        """
        sql = 'select encId,demogId,encDate from %s where icd9 in %s' % (icdfact,icds)
        dictcursor.execute(sql)
        started = time.time()
        loop = 0
        while 1:
            loop += 1
            if loop % 10000 == 0:
                dur = time.time()-started
                print 'offset = %d at %5.2f rec/sec' % (loop,loop/dur)         
            i = dictcursor.fetchone()
            if not i:
                break
            dId = i['demogId']
            encId = i['encId']
            if iddict.get(dId,None): # score = this id has one of the icds
                if period:
                    dobs = i['encDate']
                    if len(dobs.strip()) == 8:
                        yy = int(dobs[:4])
                        mm = int(dobs[4:6])
                        dd = int(dobs[6:8])
                        dobs = datetime.date(yy,mm,dd)
                        if dobs >= pstart and dobs < pend:
                            ricd9.append(encId)
                else: # if no period, all
                    ricd9.append((encId,dId)) # tuple - encounter and demogId
    print '# returning %d icd9 matches - %s' % (len(ricd9),ricd9[:20])
    return ricd9 
    
 

def test():
    foo = cohort(ages='40,50',genders="ALL",races="ALL",pcps="ALL",period='20060101,20060131')
    bar = exposureICD(cohort=foo,icd9=['413.9','414.00'], period='20070101,20070930')
    
if __name__ == "__main__":
     makeICD9Fact()
     #test()

