from ESP.esp.models import Enc
from ESP.conf.models import Icd9

INCREMENT = 30000
START = 2481000

def update():
    total_encounters = Enc.objects.all().count()
    
    for idx in xrange(START, total_encounters, INCREMENT):
        for encounter in Enc.objects.exclude(EncICD9_Codes='').exclude(EncICD9_Codes=None).order_by('id')[idx:idx+INCREMENT]:
            # Most of the strings are separated by commas
            icd9_strings = encounter.EncICD9_Codes.split(';')
            for icd9_string in [s.strip() for s in icd9_strings]:
                # But some of them are separated by spaces :(
                try:
                    for s in icd9_string.split():
                        code = Icd9.objects.get(icd9Code=s.upper)
                        encounter.reported_icd9_list.add(code)
                except Exception, msg:
                    print 'Exception: Encounter %s trying to retrieve code %s' % (encounter.id, icd9_string)




if __name__ == '__main__':
    update()
            
