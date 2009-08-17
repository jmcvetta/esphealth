from ESP.ss.models import Site, Locality
from ESP.ss.definitions import btzip


if __name__ == '__main__':
    Locality.objects.all().delete()
    
    for code in btzip:
        try:
            Locality.objects.create(
                zip_code = code[2],
                locality = code[3],
                city = code[5],
                state = 'MA',
                region_code = code[0],
                region_name = code[1],
                is_official = (code[4] == 'Official')
                )
        except Exception, why:
            zip_code = code[2]
            l = Locality.objects.get(zip_code=zip_code)
            print 'Locations %s and %s have the same zip code' % (l, code)
            
