
##preLoader is to load some data into ESP_conditionNDC table, ESP_conditionLOINC, ESP_CPTLOINCMAP table
##
import os,sys
sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


import django, datetime
from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR,LOCALSITE, USESQLITE,getLogging,EMAIL_SENDER
import string,csv
import traceback
import StringIO
import smtplib


logging=''
datadir = os.path.join(TOPDIR,LOCALSITE, 'preLoaderData/')


###############################
def getlines(fname):

    try:
        lines = file(fname).readlines()
    except:
        if logging:
            logging.error('Can not read file:%s\n' % fname)
        return []
            
   # print file,len(lines)
    returnl = [x.split('\t') for x in lines if len(x.split('\t')) >= 1]

    return returnl



###################################
###################################
def sendoutemail(towho=['rexua@channing.harvard.edu','rerla@channing.harvard.edu'],msg=''):
    ##send email
    sender=EMAIL_SENDER
    
    subject='ESP management: preLoader'
    headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, ','.join(towho), subject)
    
    message = headers + 'on %s\n%s\n' % (datetime.datetime.now(),msg)
    mailServer = smtplib.SMTP('localhost')
    mailServer.sendmail(sender, towho, message)
    mailServer.quit()
                                 
 
################################
def load2cptloincmap(table,lines, cursor):
    if logging:
        logging.info('Load CPTLOINC Map')

    cursor.execute("delete from esp_cptloincmap")

    if logging:
        logging.info('Total %s CPT_Loinc_map records in file' % len(lines))

    indx=1
    for l in lines:
        id, cpt,cmpt,loinc = [x.strip() for x in l]
        cl = CPTLOINCMap(id=indx)
        cl.CPT = cpt
        cl.CPTCompt=cmpt
        cl.Loinc=loinc
        cl.save()
        indx+=1
    if logging:
        logging.info('Done on saving into esp_cptloincmap table.')
    

###################################
def addNewcptloincmap(cursor):
    
    cursor.execute("""select distinct LxTest_Code_CPT,LxComponent from esp_lx where LxLoinc =''""")
    cptcmpt_list = cursor.fetchall()
    if cptcmpt_list:
        cptcmpt_dic = dict(map(lambda x:(x, None), cptcmpt_list))
    else:
        cptcmpt_dic ={}

    cptmap = CPTLOINCMap.objects.all()
    indx=1
    for onecptmap in cptmap:
        cpt =onecptmap.CPT
        cmpt=onecptmap.CPTCompt
        loinc = onecptmap.Loinc
        if cptcmpt_dic.has_key(('%s' % cpt,'%s'%cmpt)):
            if logging:
                logging.info('%s of %s: Adding new loinc-%s for (CPT, COMPT)=(%s,%s)' % (indx, len(cptmap), loinc, cpt,cmpt))
            ##add into Lx table
            a=Lx.objects.filter(LxTest_Code_CPT=cpt,LxComponent=cmpt)
            for onelx in a:##need update loinc
                onelx.LxLoinc=loinc
                onelx.save()
        indx+=1
    if logging:
        logging.info('Done on Adding new loinc to esp_lx table')
    
###################################
def correctcptloincmap_lx(table, cursor):
    if logging:
        logging.info('Correct CPTLOINC Map in esp_lx table')

    curcases=Case.objects.all()
    caselx=[]
    for onecase in curcases:
        newlx_list = [i for i in onecase.caseLxID.split(',') if i.strip()]
        caselx =caselx+newlx_list
    caselxid_dict = dict(map(lambda x:(x,0), caselx))
    

    #cursor.execute("""select id, LxTest_Code_CPT,LxComponent,Lxloinc from esp_lx where LxLoinc !=''""")
    # this is nearly 2M records after 2 years at atrius out of 50M total 
    #cptcmpt_list = cursor.fetchall()
    # sadly this iterator still chews up all the ram
    # TODO fix this to iterate through the cptmap loincs and filter on those?
    # will decrease ram requirements at least?
    # cptmap = CPTLOINCMap.objects.all()
    n = 0
    for acpt in CPTLOINCMap.objects.all().iterator():
        thisCPT = acpt.CPT
        thisCOMP = acpt.CPTCompt
        thisLOINC = acpt.Loinc
        for anLx in Lx.objects.filter(LxLoinc__iexact=thisLOINC).iterator(): # restricted loop
            n += 1
            if n % 100000 == 0:
                if logging:
                    logging.info('## correctcptloincmap_lx at %d' % n)
            id = anLx.id
            cpt = anLx.LxTest_Code_CPT
            comp = anLx.LxComponent
            loinc = anLx.LxLoinc
            temp = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=comp)
            if caselxid_dict.has_key('%s' % id):
                ##is a case, do nothing
                continue
            
            if temp and temp[0].Loinc == loinc:
                pass
            elif temp and temp[0].Loinc != loinc:
                thislx = Lx.objects.filter(id=id)[0]
                thislx.LxLoinc=temp[0].Loinc
                thislx.save()
                if logging:
                    logging.info('CPT=%s, Comp=%s, CorrectLoinc=%s, LxLoinc=%s, Lxid=%s' % (cpt,comp,temp[0].Loinc,loinc,id))
            elif not temp:
                if logging:
                    logging.info('CPT=%s, Comp=%s, CorrectLoinc=None, LxLoinc=%s, Lxid=%s' % (cpt,comp,loinc,id))
                thislx = Lx.objects.filter(id=id)[0]
                thislx.LxLoinc=''
                thislx.save()
    if logging:
        logging.info('## correctcptloincmap_lx scanned %d records' % n)


#####################################
def correctcptloincmap_lx(table, cursor):
    if logging:
        logging.info('## Correct CPTLOINC Map in esp_lx table')

    curcases=Case.objects.all()
    if logging:        
        logging.info('# got all case objects')

    caselx=[]
    for onecase in curcases:
        newlx_list = [i for i in onecase.caseLxID.split(',') if i.strip()]
        caselx =caselx+newlx_list
    caselxid_dict = dict(map(lambda x:(x,0), caselx))
    if logging:        
        logging.info('# created caselxid_dict of len %d' % len(caselxid_dict))
    

    cptmap = CPTLOINCMap.objects.all()
    if logging:        
        logging.info('# created cptmap of len %d' % len(cptmap))

    #cursor.execute("""select id, LxTest_Code_CPT,LxComponent,LxLoinc from esp_lx where LxLoinc !=''""")
    # this is nearly 2M records after 2 years at atrius out of 50M total 
    #cptcmpt_list = cursor.fetchall()
    #for id,cpt,comp,loinc in cptcmpt_list:
    n = 0
    for anLx in Lx.objects.filter(LxLoinc__gt='').iterator():
        n += 1
	if (n) % 100000 == 0:
	   print 'correctcptloincmap_lx at %d' % n
        id = anLx.id
        cpt = anLx.LxTest_Code_CPT
        comp = anLx.LxComponent
        loinc = anLx.LxLoinc


        temp = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=comp)
        if caselxid_dict.has_key('%s' % id):
            ##is a case, do nothing
            continue
        
        if temp and temp[0].Loinc == loinc:
            pass
        elif temp and temp[0].Loinc != loinc:
            thislx = Lx.objects.filter(id=id)[0]
            thislx.LxLoinc=temp[0].Loinc
            thislx.save()
            if logging:
                logging.info('CPT=%s, Comp=%s, CorrectLoinc=%s, LxLoinc=%s, Lxid=%s' % (cpt,comp,temp[0].Loinc,loinc,id))
        elif not temp:
            if logging:
                logging.info('CPT=%s, Comp=%s, CorrectLoinc=None, LxLoinc=%s, Lxid=%s' % (cpt,comp,loinc,id))
            thislx = Lx.objects.filter(id=id)[0]
            thislx.LxLoinc=''
            thislx.save()

def small_ram_correctcptloincmap_lx(table, cursor):
    """smaller ram - about half of that for the old version
    """
    if logging:
        logging.info('## Correct CPTLOINC Map in esp_lx table')

    curcases=Case.objects.all()
    if logging:        
        logging.info('# got all case objects')

    caselx=[]
    for onecase in curcases:
        newlx_list = [i for i in onecase.caseLxID.split(',') if i.strip()]
        caselx =caselx+newlx_list
    caselxid_dict = dict(map(lambda x:(x,0), caselx))
    if logging:        
        logging.info('# created caselxid_dict of len %d' % len(caselxid_dict))
    

    #cursor.execute("""select id, LxTest_Code_CPT,LxComponent,Lxloinc from esp_lx where LxLoinc !=''""")
    # this is nearly 2M records after 2 years at atrius out of 50M total 
    #cptcmpt_list = cursor.fetchall()
    # sadly this iterator still chews up all the ram
    # TODO fix this to iterate through the cptmap loincs and filter on those?
    # will decrease ram requirements at least?
    cptmap = CPTLOINCMap.objects.all()
    allLOINC = []
    n = 0
    for acpt in CPTLOINCMap.objects.all().iterator():
        thisCPT = actp.CPT
        thisCOMP = actp.CPTCompt
        thisLOINC = actp.Loinc
        allLOINC.append(thisLOINC) # use later to delete old loincs
        for anLx in Lx.objects.filter(LxLoinc__iexact=thisLOINC).iterator(): # restricted loop
            n += 1
            if n % 100000 == 0:
                if logging:
                    logging.info('## correctcptloincmap_lx at %d' % n)
            id = anLx.id
            cpt = anLx.LxTest_Code_CPT
            comp = anLx.LxComponent
            loinc = anLx.Lxloinc
            temp = CPTLOINCMap.objects.filter(CPT=cpt,CPTCompt=comp)
            if caselxid_dict.has_key('%s' % id):
                ##is a case, do nothing
                continue
            
            if temp and temp[0].Loinc == loinc:
                pass
            elif temp and temp[0].Loinc != loinc:
                thislx = Lx.objects.filter(id=id)[0]
                thislx.LxLoinc=temp[0].Loinc
                thislx.save()
                if logging:
                    logging.info('CPT=%s, Comp=%s, CorrectLoinc=%s, LxLoinc=%s, Lxid=%s' % (cpt,comp,temp[0].Loinc,loinc,id))
            elif not temp:
                if logging:
                    logging.info('CPT=%s, Comp=%s, CorrectLoinc=None, LxLoinc=%s, Lxid=%s' % (cpt,comp,loinc,id))
                thislx = Lx.objects.filter(id=id)[0]
                thislx.LxLoinc=''
                thislx.save()
    allLOINC = list(set(allLOINC)) # remove dupes
    if logging:
        logging.info('## correctcptloincmap_lx scanned %d records - now looking for old loincs' % n)
    n = 0
    q_obj = Q(LxLoinc__in=allLOINC)
    for anLx in Lx.objects.filter(~q_obj).iterator(): # restricted loop
        n += 1
        if n % 1000 == 0:
            if logging:
                logging.info('## correctcptloincmap_lx deleting old loincs at %d' % n)
        id = anLx.id
        cpt = anLx.LxTest_Code_CPT
        comp = anLx.LxComponent
        loinc = anLx.Lxloinc
        if logging:
            logging.info('CPT=%s, Comp=%s, CorrectLoinc=None, LxLoinc=%s, Lxid=%s' % (cpt,comp,loinc,id))
        thislx = Lx.objects.filter(id=id)[0]
        thislx.LxLoinc=''
        thislx.save()
    if logging:
        logging.info('## correctcptloincmap_lx deleted old loincs from %d records' % n)



                    
################################
def correctcptloincmap(table):
    logging.info('Correct CPTLoinc map')
    curcases=Case.objects.all()
    caselx=[]
    for onecase in curcases:
        newlx_list = [i for i in onecase.caseLxID.split(',') if i.strip()]
        caselx =caselx+newlx_list
        
    logging.info('Total Case Lx=%s' % len(caselx))

    lines = getlines(datadir+table+'.txt')
    logging.info('Total %s CPT_Loinc_map records' % len(lines))
    disclx={}
    indx=1
    for l in lines:
        id, cpt,cmpt,loinc = [x.strip() for x in l]
        if indx%10==0:
            logging.info('Processed %s of %s maps' % (indx, len(lines)))
        indx=indx+1

        ##update Lx table
        a=Lx.objects.filter(LxTest_Code_CPT=cpt,LxComponent=cmpt)
        lx = a.exclude(id__in=caselx)
        for onelx in lx:##need update loinc
            if onelx.LxLoinc!=loinc:
                disclx[onelx.id]=(loinc,onelx.LxLoinc)
                logging.info('LOINC update,ID=%s: %s-->%s'  % (onelx.id,onelx.LxLoinc,loinc))
                onelx.LxLoinc=loinc
                onelx.save()

  #  logging.info('DisLOINC:%s' % str(disclx))

                                                                                                                                                                                

################################
def load2DrugNames(table,lines,cursor):
    """ an attempt to text match drugs on generic names
    to try to avoid the vagaries and complexities of matching exaxt ndc's which
    is a fool's errand
    """	
    cursor.execute("delete from esp_conditiondrugname")
    #cursor.execute("alter table esp_conditiondrugname AUTO_INCREMENT=1") # make sure we start id=1 again!

    n = 0
    for l in lines:
        id, rulename, drugname,route, define,send =  [x.strip() for x in l]
        r = Rule.objects.filter(ruleName__iexact=rulename)[0]
        n += 1
        cl = ConditionDrugName(id=n)
        cl.CondiRule=r
        cl.CondiDrugName=drugname
        cl.CondiDrugRoute = route
        cl.CondiDefine=define
        cl.CondiSend=send
        cl.save()
    if logging:
        logging.info('Done on loading to esp_conditiondrugname')

################################
def load2ndc(table,lines,cursor):
    ndclen = 9 # really 11 but we ignore the pack size last 2 digits
    cursor.execute("delete from esp_conditionndc")

    n = 0
    for l in lines:
	n += 1
        id, rulename, rawndc,define,send = [x.strip() for x in l]
        r = Rule.objects.filter(ruleName__iexact=rulename)[0]
	ttab = string.maketrans(' -*','000')
        ndc = string.translate(rawndc,ttab,'-') # translate and get rid of crap
        l = len(ndc) # pad to ndclen or remove leading zero
        if l < ndclen:
           ndc = '%s%s' % (ndc,'0'*(ndclen-l)) # right pad to 9
        elif l == ndclen+1: # ? leading zero
            if ndc[0] == '0':
              ndc = ndc[1:]
        elif l > ndclen:
            if logging:
                logging.warning('Bah. ndc code %s at line %d is not massagable into 9 meaningful digits' % (ndc,n))
                        
        cl = ConditionNdc(id=n)

        cl.CondiRule=r
        cl.CondiNdc=ndc
        cl.CondiDefine=define
        cl.CondiSend=send
        cl.save()


################################
def load2icd9(table,lines, cursor):
    cursor.execute("delete from esp_conditionicd9")

    n=0
    for l in lines:
        id, rulename, icd,define,send = [x.strip() for x in l]
        r = Rule.objects.filter(ruleName__iexact=rulename)[0]
        n+=1
        cl = ConditionIcd9(id=n)

        cl.CondiRule=r
        cl.CondiICD9=icd
        cl.CondiDefine=define
        cl.CondiSend=send
        cl.save()

        
################################
def load2loinc(table,lines,cursor):
    cursor.execute("delete from esp_conditionloinc")

    n=0
    for l in lines:
        id, rulename, loinc,ope,value,snmdposi,snmdnega,snmdinde,define,send = [x.strip() for x in l]

        if loinc.strip()=='':
            continue
        
        r = Rule.objects.filter(ruleName__iexact=rulename)[0]
        n+=1
        cl = ConditionLOINC(id=n)

        cl.CondiRule=r
        cl.CondiLOINC=loinc
        cl.CondiOperator=ope
        cl.CondiValue=value
        cl.CondiDefine=define
        cl.CondiSend=send
        cl.CondiSNMDPosi=snmdposi
        cl.CondiSNMDNega=snmdnega
        cl.CondiSNMDInde=snmdinde
        cl.save()



################################
def load2rule(table,lines):

    lines.sort()
    for items  in lines:
        id, name,initstatus,inprod, fmt, dest,hl7name,hl7c,hl7ctype,note,excludstr = [x.strip() for x in items]
        if not name: continue

        r = Rule.objects.filter(ruleName__iexact=name)
        if r:
            rl=r[0]
        elif id:
            r = Rule.objects.filter(id=id)
            if r:
                rl=r[0]
            else:
                rl = Rule(id=id)
        else:
            rl = Rule()
            
        rl.ruleName = name
        rl.ruleInitCaseStatus=initstatus
        rl.ruleinProd = inprod
        rl.ruleMsgFormat = fmt
        rl.ruleMsgDest = dest
        rl.ruleHL7Name = hl7name
        rl.ruleHL7Code = hl7c
        rl.ruleHL7CodeType = hl7ctype
        rl.ruleComments = note
        rl.ruleExcludeCode=excludstr
        rl.save()
        print 'Added Rule - %s, InProduction=%s' % (name,inprod)
    print 'Total rules: %s ' % len(Rule.objects.all())
        
################################
def  load2config(table,lines,cursor):
    cursor.execute("delete from esp_config", ())

    indx=0
    for items  in lines:
        (id, t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25) = [x.strip() for x in items]
        indx+=1
        cf = config(id=indx)
        
        cf.appName = t1
        cf.FacilityID=t2
        cf.sendingFac=t3

        cf.instTechName = t4
        cf.instTechEmail = t5
        cf.instTechTel = t6
        cf.instTechcel = t7
        
        cf.institution_name=t8
        cf.institution_CLIA=t9
        cf.instAddress1=t10
        cf.instAddress2 = t11
        cf.instCity = t12
        cf.instState = t13
        cf.instZip= t14
        cf.instCountry = t15
        cf.instTel=t16
        cf.instFax =t17
        
        cf.instIDFName = t18
        cf.instIDLName = t19
        cf.instIDEmail =t20
        cf.instIDTelArea = t21
        cf.instIDTel = t22
        cf.instIDTelExt = t23
        cf.instIDcel= t24
        cf.instComments=t25      
        cf.save()

###################################
###################################
#################################
def makecpt(cursor):
    """found these at www.tricare.osd.mil/tai/downloads/cpt_codes.xls
    """
    cursor.execute("delete from esp_cpt")
    cursor.execute("alter table esp_cpt AUTO_INCREMENT=1") # make sure we start id=1 again!
    reader = csv.reader(open('cpt_codes.csv','rb'),dialect='excel')
    header = reader.next()
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    i = 0
    for ll in reader: # here be dragons. lots of "" at the 4th pos - but some other subtle crap too...
        code,long,short = ll[:3] # good thing it doesn't really matter..
        i += 1
        if i % 10000 == 0:
            print i,'cpt done'
        long = long.replace('"','')
        short = short.replace('"','')
        c = cpt(cptCode=code,cptLong=long.capitalize(),cptShort=short.capitalize(),cptLastedit=now)
        c.save()


###################################
def makeicd9(cursor):
    """ found these codes somewhere or other..."""
    cursor.execute("delete from esp_icd9")
    cursor.execute("alter table esp_icd9 AUTO_INCREMENT=1") # make sure we start id=1 again!
    codes = []
    n = 1
    from ESPicd9 import icd
    for line in icd.split('\n'):
        if n % 10000 == 0:
            print n,'icd done'
        n += 1
        line = line.replace("'",'')
        code,trans = line.split('\t')
        code = '%s.%s' % (code[:3],code[3:]) # make all 3 digit decimals
        c = icd9(icd9Code=code,icd9Long=trans.capitalize())
        c.save()


###################################
def makendc(cursor):
    """ found these codes somewhere http://www.fda.gov/cder/ndc/"""
    cursor.execute("delete from esp_ndc")
    cursor.execute("alter table esp_ndc AUTO_INCREMENT=1") # make sure we start id=1 again!
    f = file('ndc_codes.txt','r')
    foo = f.next() # lose header
    n = 1
    for line in f:
        if n % 10000 == 0:
            print n,'ndc done'
        n += 1
        lbl = line[8:14]
        prod = line[15:19]
        lbl = lbl.replace('*','0')
        prod = prod.replace('*','0')
        trade = line[44:].strip()
        newn = ndc(ndcLbl=lbl.capitalize(),ndcProd=prod.capitalize(),ndcTrade=trade.capitalize())
        newn.save()
                                                                                                                                                                                                                                            
            
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#--- ~~~ Main Logic ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    startt = datetime.datetime.now()
    logging = getLogging('preLoader.py_v0.1', debug=0)

    from django.db import connection
    cursor = connection.cursor()

    
    if len(sys.argv) > 1:
        try:
            table = sys.argv[1]
            if table == 'remake':
                makendc(cursor)
                makeicd9(cursor) 
                makecpt(cursor)
            elif table == 'esp_conditionndc':
                load2ndc(table,getlines(datadir+table+'.txt'), cursor)
            elif table == 'esp_conditionicd9':
                load2icd9(table,getlines(datadir+table+'.txt'), cursor)
            elif table == 'esp_conditionloinc':
                load2loinc(table,getlines(datadir+table+'.txt'), cursor)
            elif table == 'esp_cptloincmap':
                if 1:
                    if len(sys.argv)==3 and sys.argv[2]=='CORRECT':
                        correctcptloincmap(table)
                    elif len(sys.argv)==2:
                        load2cptloincmap(table, getlines(datadir+table+'.txt'), cursor)
                        addNewcptloincmap(cursor)
                        correctcptloincmap_lx(table,cursor)

                    sendoutemail(towho=['rexua@channing.harvard.edu'],msg='Successfully running preLoader.py for CPTLOINCMap;')
                #except:
                #    sendoutemail(towho=['rexua@channing.harvard.edu'],msg='ERROR when running preLoader.py for CPTLOINCMap;')
                    
            elif table =='esp_config':
                load2config(table,getlines(datadir+table+'.txt'), cursor)
            elif table == 'esp_rule':
                load2rule(table, getlines(datadir+table+'.txt'))
            elif table == 'esp_conditiondrugname':
                load2DrugNames(table,getlines(datadir+table+'.txt'), cursor)
            else:
                msg = 'Unknown table - %s\n' % table
                logging.info(msg)

            logging.info('Start: %s\n' %  startt)
            logging.info('End:   %s\n' % datetime.datetime.now())
        except:
            fp = StringIO.StringIO()
            traceback.print_exc(file=fp)
            message = fp.getvalue()
            logging.info(message+'\n')
    else:
        table = 'esp_rule'
        load2rule(table, getlines(datadir+table+'.txt'))  
        table = 'esp_conditionndc'
        load2ndc(table,getlines(datadir+table+'.txt'), cursor)
        table = 'esp_conditionicd9'
        load2icd9(table,getlines(datadir+table+'.txt'), cursor)
        table = 'esp_conditionloinc'
        load2loinc(table,getlines(datadir+table+'.txt'), cursor)
        table = 'esp_cptloincmap'
        load2cptloincmap(table, getlines(datadir+table+'.txt'), cursor)
        addNewcptloincmap(cursor)
        correctcptloincmap_lx(table,cursor)
        table = 'esp_config'
        load2config(table,getlines(datadir+table+'.txt'),cursor)
        table = 'esp_conditiondrugname'
        load2DrugNames(table,getlines(datadir+table+'.txt'), cursor)
    

if __name__ == "__main__":
    main()
    

