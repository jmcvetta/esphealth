# prototype ESP case maker
# run after new data inserted
#
# writes new case and AR workflow records for all newly identified cases in the database
# selects patients with any of icd9s on the case definition icd list and any one of lx_list
# To save time, remembers all of the associated lx records, rx records, enc records
# and (for hl7 construction) remembers the icd9_list icd9 codes from each encounter
# (tuples of those codes from each encounter in the
# same order as the encounters)
# this saves us having to do much work at display or message format time
#
# Likely that each condition will need a separate version of this logic
# some patterns may be reuseable with any luck.
#
# Each condition not only has criteria, but also elements which should be
# supplied as part of any notification. Prescriptions are particularly
# important to see if the case was appropriately treated
#
# Most of the logic is amazingly simple when using the django ORM
#

import os, sys, django, datetime
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from django.db.models import Q
import localconfig



###For logging
pglogging = localconfig.getLogging('purge.py_v0.1', debug=0)

###################
def delprov(pids): 
    patients = Demog.objects.filter(id__in=pids)
    pcps = [i.values()[0] for i in patients.values('DemogProvider').distinct()]

    encs = Enc.objects.filter(EncPatient__id__in=pids)
    encprov = [i.values()[0] for i in encs.values('EncEncounter_Provider').distinct()]

    lxs = Lx.objects.filter(LxPatient__id__in=pids)
    lxprov = [i.values()[0] for i in lxs.values('LxOrdering_Provider').distinct()]

    rxs = Rx.objects.filter(RxPatient__id__in=pids)
    rxprov = [i.values()[0] for i in rxs.values('RxProvider').distinct()]

    ##get all distinct relates providers
    relatedprovs = dict(map(lambda x:(x,1), pcps+encprov+lxprov+rxprov)).keys()
    p = Provider.objects.exclude(id__in=relatedprovs)
    doDelete(p)




###################################
def doDelete(removel):
    
    prevdate = datetime.datetime.now()-datetime.timedelta(90)
   # prevdate = datetime.datetime.now()
    pglogging.info('Deleted data before %s' % prevdate)
    for i in removel:
        if i.lastUpDate<prevdate:
            i.delete()
                    


################################
################################
if __name__ == "__main__":

    ##get all related patient IDs
    pglogging.info('\nStart on Deleteing:%s' % datetime.datetime.now())
    pids = map(lambda x:x.caseDemog_id, Case.objects.all())
    
    ##delete from demog
    d = Demog.objects.exclude(id__in=pids)
    doDelete(d)
   # d = Demog.objects.filter(lastUpDate__lte=prevdate).exclude(id__in=pids)
    pglogging.info('Done on Deleteing demog:%s' % datetime.datetime.now())
    

    ##delete from provider
    delprov(pids)
    pglogging.info('Done on Deleteing provider:%s' % datetime.datetime.now())
    
    
    ##delete from Lx
    l=Lx.objects.exclude(LxPatient__id__in=pids)
    doDelete(l)
    pglogging.info('Done on Deleteing Lx:%s' % datetime.datetime.now())
    

    ##delete from Rx 
    r=Rx.objects.exclude(RxPatient__id__in=pids)
    doDelete(r)
    pglogging.info('Done on Deleteing Rx:%s' % datetime.datetime.now())
    

    #delete from enc
    enc = Enc.objects.exclude(EncPatient__id__in=pids)
    doDelete(enc)
    pglogging.info('Done on Deleteing Enc:%s' % datetime.datetime.now())
    

    #delete from immiunization:
    imm = Immunization.objects.exclude(ImmPatient__id__in=pids)
    doDelete(imm)
    pglogging.info('Done on Deleteing Imm:%s' % datetime.datetime.now())
    
    ###
    pglogging.info('Done on Deleteing:%s' % datetime.datetime.now())
        
    pglogging.shutdown()
