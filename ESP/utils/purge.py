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
#


# Purge.py: delete non-case related records which are older than 90 days.

import os, sys, django, datetime
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from ESP.settings import DATABASE_HOST,DATABASE_USER,DATABASE_PASSWORD,DATABASE_NAME,getLogging
from django.db.models import Q
import MySQLdb


espdb = MySQLdb.Connect(DATABASE_HOST,DATABASE_USER,DATABASE_PASSWORD,DATABASE_NAME)
cur = espdb.cursor()

###For logging
pglogging = getLogging('purge.py_v0.1', debug=0)

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
def doDelete(table, idcolumn):
    """
    if using
       d = Demog.objects.filter(lastUpDate__lte=prevdate).exclude(id__in=pids)
       d.delete()
    it takes a long time. So change to use for loop to delete one by one. 
    
    """

    sql = """delete from %s
             where lastupdate < DATE_SUB(CURDATE(),INTERVAL 90 DAY)
                      and %s not in (select caseDemog_id from esp_case);
          """ % (table, idcolumn)
    cur.execute(sql)
    pglogging.info('Done on Deleteing %s:%s' % (table, datetime.datetime.now()))


    #prevdate = datetime.datetime.now()-datetime.timedelta(90)
    #pglogging.info('Deleted data before %s' % prevdate)
    #for i in removel:
     #   if i.lastUpDate<prevdate:
      #      i.delete()

                    
####################################
def doDelbyAPI():
    pids = map(lambda x:x.caseDemog_id, Case.objects.all())

    ##delete demog
    d = Demog.objects.exclude(id__in=pids)
    doDelete(d)
    # d = Demog.objects.filter(lastUpDate__lte=prevdate).exclude(id__in=pids)

    ##no need to delete provider
    #delprov(pids)
    #pglogging.info('Done on Deleteing provider:%s' % datetime.datetime.now())

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

                                                    

################################
################################
if __name__ == "__main__":

    ##get all related patient IDs
    pglogging.info('\nStart on Deleteing:%s' % datetime.datetime.now())
    pids = map(lambda x:x.caseDemog_id, Case.objects.all())
    
    doDelete('esp_demog', 'id')
    doDelete('esp_lx', 'LxPatient_id')
    doDelete('esp_rx', 'RxPatient_id')
    doDelete('esp_enc', 'EncPatient_id')
    doDelete('esp_immunization', 'ImmPatient_id')
    cur.execute('commit')
    
    ##
    pglogging.info('Done on Deleteing:%s' % datetime.datetime.now())
        
    pglogging.shutdown()
    espdb.close()
