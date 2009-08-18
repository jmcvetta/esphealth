from ESP.ss.models import Site, Locality
from ESP.ss.definitions import btzip, localSiteSites


def make_localities():
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
            


def make_non_specialty_clinics():
    # Some really twisted list comprehension magic to get a
    # tab-demilited file turned into a a list of lists, each list
    # representing the data from about the relevant sites.

    # According to the file, a relevant site is one where the line
    # does not start with an asterisk.
    relevant_sites = [x for x in localSiteSites if not x.split('|')[0].startswith('*')][2:-1]
    site_matrix = [x.split('|') for x in relevant_sites]
    site_clean = [[x.strip() for x in entry] for entry in site_matrix]

    for site in site_matrix:
        Site.objects.create(
            code = site[3],
            name = site[2],
            zip_code = site[0]
            )
        





if __name__ == '__main__':
    make_non_specialty_clinics()
    make_localities()
    
