from django.shortcuts import render_to_response, get_list_or_404
import os,datetime
os.environ['DJANGO_SETTINGS_MODULE'] = 'espss.settings'
from espss.ssmap.models import event,geoplace
from espss.settings import GOOGLE_KEY

heathexlist	= ["#00ff00","#19E500","#33CC00",
"#4CB200","#669900","#7F7F00","#996600","#B24C00","#CC3200","#FF0000"]
# from colour gradient maker at 
# http://www.herethere.net/~samson/php/color_gradient/?cbegin=00FF00&cend=FF0000&steps=10


def bydate(request,d):
    """ need scount_list - z,synd,tot,pct,edate
        and date_list of available dates
        refactored may 19 for new tables
        This currently ONLY generates seen_place maps
        res_place for usez should work
    """
    
    usez = 'seen_place' # or res_place
    sdate = '%s-%s-%s' % (d[0:4],d[4:6],d[6:8])
    dt = datetime.date(int(d[0:4]),int(d[4:6]),int(d[6:8]))
    nextd = dt + datetime.timedelta(1)
    nextw = dt + datetime.timedelta(7)
    prevd = dt - datetime.timedelta(1)
    prevw = dt - datetime.timedelta(7)
    date_list = event.objects.all().distinct().values_list('edate',flat=True)
    firstd = min(date_list)
    lastd = max(date_list)
    if nextd > lastd:
        nextd = None
    else:
        nextd = nextd.strftime('%Y%m%d')
    if prevd < firstd:
        prevd = None
    else:
        prevd = prevd.strftime('%Y%m%d')
    if nextw > lastd:
        nextw = None
    else:
        nextw = nextw.strftime('%Y%m%d')
    if prevw < firstd:
        prevw = None
    else:
        prevw = prevw.strftime('%Y%m%d')
    allzip_list = event.objects.select_related(usez).distinct().values_list(usez,flat=True)
    allzips = [x.split('zip:')[-1] for x in allzip_list] # get rid of u'zip:01005'
    allzips.sort()
    # all zips so can generate zeros
    date_list = [{'datetime':x,'date':'%04d%02d%02d' % (x.year,x.month,x.day) } for x in date_list]
    esel = {'lat': # django has a very neat way to inject sql
        'select la from ssmap_geoplace where ssmap_geoplace.place  = ssmap_event.%s_id' % usez,
        'lon': 
        'select lo from ssmap_geoplace where ssmap_geoplace.place = ssmap_event.%s_id' % usez,
        'z':
        'select zipcode from ssmap_geoplace where ssmap_geoplace.place = ssmap_event.%s_id' % usez}
    # an extra select dict to speed up the foreign key lookup - note real SQL table and column names!
    scount = event.objects.filter(edate__exact=sdate).extra(select=esel).values('lat','lon','z','rule',
       'edate' ).order_by('z')
    synd = None
    sclen = scount.count()
    print '## scountlen=',sclen
    if sclen > 0:    
        tots = {} 
        details = {}
        for c in scount:
            if not synd:
                synd = c['rule']
            z = c['z']
            tots.setdefault(z,0)
            tots[z] += 1        
            details.setdefault(z,c) # keep details
        tk = tots.keys()
        tval = tots.values()
        maxtot = max(tval)
        mintot = min(tval)
        tinterval = maxtot/10.0 # 10 steps to cover maxrange
        heatn = [1 + int(i*tinterval) for i in range(10)]
        heatn[0] = 0
        heatn[-1] = maxtot
        print 'maxtot = %d, tinterval = %f, heatn= %s' % (maxtot,tinterval,heatn)
        heatlist = [{'hex':heathexlist[i],'n':'%d' % heatn[i]} for i in range(10)]
        scount_list = []
        syndrome = None
        for k in allzips: # some will be missing
            c = details.get(k,None)
            if not c:
                g = geoplace.objects.filter(zipcode__exact=k)
                if len(g) > 0: # fake a record
                    g0 = g[0] # in case multiples!
                    c = {'z':k,'lat':g0.la,'lon':g0.lo,'rule':synd,'edate':sdate}
                    tots[k] = 0
                    print '### added zip',k
                else:
                    print '# cannot find geoplace record for zipcode = %s' % k    
            n = tots.get(k,None)
            if n <> None:
                if n > 0:
                    heat = int((n)/tinterval) - 1
                else:
                    heat = 0
                c['heat'] = heat
                c['n'] = '%d' % n
                c['pct'] = '0.0'
                c['longi'] = float(c['lon'])
                c['lati'] = float(c['lat'])
                scount_list.append(c)
                if not syndrome:
                    syndrome = c['rule']
        print '## scount_list=',scount_list
        rdict = {'tdate':d, 'sdate':sdate,'syndrome':syndrome,
             'scount_list':scount_list, 'GOOGLE_KEY':GOOGLE_KEY, 'heathex_list':heatlist,
            'width':640,'height':480,'nextd':nextd,'prevd':prevd,'nextw':nextw,'prevw':prevw}

    else:
       rdict = {'tdate':d, 'sdate':sdate,'syndrome':'',
            'scount_list':{}, 'GOOGLE_KEY':GOOGLE_KEY, 'heathex':{},
            'width':640,'height':480,'nextd':nextd,'prevd':prevd,'nextw':nextw,'prevw':prevw}
    return render_to_response('bydate.html',rdict )



def ssmap(request):
    s = bydate(request,'20090501')
    return s

def espss(request):
    """ index
    """
    return render_to_response('espss.html')

def ssmapperdefault(request):
    s = ssmapper(request,'20090501')
    return s

def ssmapper(request,d):
    """ need scount_list - z,synd,tot,pct,edate
        and date_list of available dates
        refactored may 19 for new tables
        This currently ONLY generates seen_place maps
        res_place for usez should work
    """
    usez = 'seen_place' # or res_place
    sdate = '%s-%s-%s' % (d[0:4],d[4:6],d[6:8])
    dt = datetime.date(int(d[0:4]),int(d[4:6]),int(d[6:8]))
    nextd = dt + datetime.timedelta(1)
    nextw = dt + datetime.timedelta(7)
    prevd = dt - datetime.timedelta(1)
    prevw = dt - datetime.timedelta(7)
    date_list = event.objects.all().distinct().values_list('edate',flat=True)
    firstd = min(date_list)
    lastd = max(date_list)
    if nextd > lastd:
        nextd = None
    else:
        nextd = nextd.strftime('%Y%m%d')
    if prevd < firstd:
        prevd = None
    else:
        prevd = prevd.strftime('%Y%m%d')
    if nextw > lastd:
        nextw = None
    else:
        nextw = nextw.strftime('%Y%m%d')
    if prevw < firstd:
        prevw = None
    else:
        prevw = prevw.strftime('%Y%m%d')
    allzip_list = event.objects.select_related(usez).distinct().values_list(usez,flat=True)
    allzips = [x.split('zip:')[-1] for x in allzip_list] # get rid of u'zip:01005'
    allzips.sort()
    # all zips so can generate zeros
    date_list = [{'datetime':x,'date':'%04d%02d%02d' % (x.year,x.month,x.day) } for x in date_list]
    esel = {'lat': # django has a very neat way to inject sql
        'select la from ssmap_geoplace where ssmap_geoplace.place  = ssmap_event.%s_id' % usez,
        'lon': 
        'select lo from ssmap_geoplace where ssmap_geoplace.place = ssmap_event.%s_id' % usez,
        'z':
        'select zipcode from ssmap_geoplace where ssmap_geoplace.place = ssmap_event.%s_id' % usez}
    # an extra select dict to speed up the foreign key lookup - note real SQL table and column names!
    scount = event.objects.filter(edate__exact=sdate).extra(select=esel).values('lat','lon','z','rule',
       'edate' ).order_by('z')
    synd = None
    sclen = scount.count()
    print '## scountlen=',sclen
    if sclen > 0:    
        tots = {} 
        details = {}
        for c in scount:
            if not synd:
                synd = c['rule']
            z = c['z']
            tots.setdefault(z,0)
            tots[z] += 1        
            details.setdefault(z,c) # keep details
        tk = tots.keys()
        tval = tots.values()
        maxtot = max(tval)
        mintot = min(tval)
        tinterval = maxtot/10.0 # 10 steps to cover maxrange
        heatn = [1 + int(i*tinterval) for i in range(10)]
        heatn[0] = 0
        heatn[-1] = maxtot
        #print 'maxtot = %d, tinterval = %f, heatn= %s' % (maxtot,tinterval,heatn)
        heatlist = [{'hex':heathexlist[i],'n':'%d' % heatn[i]} for i in range(10)]
        scount_list = []
        syndrome = None
        for k in allzips: # some will be missing
            c = details.get(k,None)
            if not c:
                g = geoplace.objects.filter(zipcode__exact=k)
                if len(g) > 0: # fake a record
                    g0 = g[0] # in case multiples!
                    c = {'z':k,'lat':g0.la,'lon':g0.lo,'rule':synd,'edate':sdate}
                    tots[k] = 0
                    #print '### added zip',k
                else:
                    print '# cannot find geoplace record for zipcode = %s' % k    
            n = tots.get(k,None)
            if n <> None:
                if n > 0:
                    heat = int((n)/tinterval) - 1
                    if heat < 0:
                        heat = 1
                else:
                    heat = 0
                c['heat'] = heat
                c['n'] = '%d' % n
                c['pct'] = '0.0'
                c['longi'] = float(c['lon'])
                c['lati'] = float(c['lat'])
                scount_list.append(c)
                if not syndrome:
                    syndrome = c['rule']
        print '## scount_list=',scount_list
        rdict = {'tdate':d, 'sdate':sdate,'syndrome':syndrome,'date_list':date_list,
             'scount_list':scount_list, 'GOOGLE_KEY':GOOGLE_KEY, 'heathex_list':heatlist,
            'width':640,'height':480,'nextd':nextd,'prevd':prevd,'nextw':nextw,'prevw':prevw}

    else:
       rdict = {'tdate':d, 'sdate':sdate,'syndrome':'','date_list':date_list,
            'scount_list':{}, 'GOOGLE_KEY':GOOGLE_KEY, 'heathex':{},
            'width':640,'height':480,'nextd':nextd,'prevd':prevd,'nextw':nextw,'prevw':prevw}
    return render_to_response('ssmapper.html',rdict )

def ssmap(request):
    s = bydate(request,'20090501')
    return s

def espss(request):
    """ index
    """
    return render_to_response('espss.html')
