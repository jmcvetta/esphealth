""" fever counts
"""
myVersion = '0.7'
thisSite = 'Atrius' # for amds header
thisRequestor = 'Ross Lazarus'
cclassifier = 'ESPSSApril2009'
ageChunksize = 5 #

import os, sys, django, time, datetime
from optparse import OptionParser
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import *
import utils
SSlogging = getLogging('espSS_v%s' % myVersion, debug=0)


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


def AgeFevers(startDT='20090301',endDT='20090331'):
    """
    discover rates for no temp, normal temp, fever temp and all encounters by age chunk
    Age in 5 year chunks added at Ben Kruskal's request for line lists
    """
    started = time.time()
    notemp = {}
    normtemp = {}
    fevertemp = {}
    tot =  {}
    demage = {}

    esel = {'dob':
            'select DemogDate_of_Birth from esp_demog where esp_demog.id = esp_enc.EncPatient_id'}
    # an extra select dict to speed up the foreign key lookup - note real SQL table and column names!

    allenc = Enc.objects.filter(EncEncounter_Date__gte=startDT,
        EncEncounter_Date__lte=endDT).extra(select=esel).values('EncPatient','dob',
        'EncEncounter_Date','EncTemperature').iterator() # yes - this works well to minimize ram
    for e in allenc:
        did = e['EncPatient'] # demog
        age = demage.get(did,-999)
        if age == -999:
            dob = e.get('dob',None)
            ed = e.get('EncEncounter_Date',None)
            age = makeAge(dob=dob,edate=ed,chunk=ageChunksize)
            demage[did] = age # cache
        t = e.get('EncTemperature',None)
        if t > '':
            try:
                t = float(t)
            except:
                t = None
        if t == None:
            notemp.setdefault(age,0)
            notemp[age] += 1
        elif t < 100.4:
            normtemp.setdefault(age,0)
            normtemp[age] += 1
        else:
            fevertemp.setdefault(age,0)
            fevertemp[age] += 1
        tot.setdefault(age,0)
        tot[age] += 1
    return notemp,normtemp,fevertemp,tot


def count(startDT=None,endDT=None):
    notemp,normtemp,fevertemp,tot = AgeFevers(startDT=startDT,endDT=endDT)
    ak = tot.keys()
    ak.sort()
    h = 'Age\tMeasuref\tFeverf\tnoFeverf\ttotenc'
    res = [h,]
    for a in ak:
        t = tot[a]
        nno = notemp[a]
        nhot = fevertemp[a]
        nnot = normtemp[a]
        row = ['%d' % a,'%3.2f' % (nnot+nhot)/t,'%3.2f' % nhot/t,'%3.2f' % nnot/t,t]
        res.append('\t'.join(row))
    print '\n'.join(res)
    f = open('fevercounts.xls','w')
    f.write('\n'.join(res))
    f.write('\t')
    f.close()

if __name__ == "__main__":
    count('20060701','20060730')





