
import os, sys, django, datetime
sys.path.insert(0, '/home/ESP/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


from ESP.esp.models import *
from django.db.models import Q
from ESP.settings import TOPDIR,LOCALSITE,getLogging

outputdir =  os.path.join(TOPDIR,LOCALSITE, 'logs/')
casefile ='case_backup_new2.txt'
wffile = 'casewf_backup_new2.txt'
iclogging = getLogging('backupcase.py_v0.1', debug=0)

###################################
def backupcases():
    cases = Case.objects.all()
    casef = open(outputdir+casefile, 'w')
    
    #case
    for c in cases:
        temp = '%s|'* 13 % (c.id, c.caseDemog.id, c.caseProvider.id,
                            c.caseWorkflow,c.caseComments,
                            c.caseLastUpDate,c.casecreatedDate,
                            c.caseSendDate,c.caseRule.id,
                            c.caseEncID,c.caseLxID,c.caseRxID,c.caseICD9)
        casef.write(temp+ '\n')


    #caseworkflow
    wf_file = open(outputdir+wffile, 'w')
    casewf = CaseWorkflow.objects.all()
    for c in casewf:
        try:
            temp = '%s|'* 6 % (c.id, c.workflowCaseID.id, c.workflowDate, c.workflowState,
                           c.workflowChangedBy, c.workflowComment)
            wf_file.write(temp+ '\n')
            
        except:
            pass

                    
    casef.close()
    wf_file.close()

###################################
def  cleantable():
    from django.db import connection
    cursor = connection.cursor()
    sqlist = []
    sqlist.append("delete from esp_case;")
    sqlist.append("alter table esp_case AUTO_INCREMENT=1;") # make sure we start id=1 again!
    sqlist.append("delete from esp_caseworkflow;")
    sqlist.append("alter table esp_caseworkflow AUTO_INCREMENT=1;") # make sure we start id=1 again!
     

#    sqlist.append('drop table esp_case;')
#    sqlist.append('drop table esp_caseworkflow;')
    sqlist.append('commit;')
    for sql in sqlist:
        try:
            cursor.execute(sql)
        except:
            iclogging.error('Error executing %s' % sql)

 #   synccmd='/usr/bin/python2.4 %s/manage.py syncdb' % os.path.join(TOPDIR,'ESP')
 #   try:
 #       os.system(synccmd)
 #   except:
 #       iclogging.error('Error executing %s' % synccmd)
         
###################################
def reload(state=[]):
    try:
        cases = file(outputdir+casefile).readlines()
    except:
        iclogging.error('Error opening file %s' % casefile)
        return
    for c in cases:
        c= c.strip()
        id, casedemog_id,caseProvider_id,caseWorkflow,caseComments,caseLastUpDate,casecreatedDate,caseSendDate,caseRule_id,caseEncID,caseLxID,caseRxID,caseICD9 = c.split('|')[:-1]
        p = Demog.objects.get(id__exact=casedemog_id)
        rule = Rule.objects.filter(id=caseRule_id)[0]
        
        if not state or caseWorkflow not in state: ##load all cases or load cases except 'AR' case 
            c = Case(id=id, caseWorkflow=caseWorkflow,caseDemog=p,caseComments=caseComments,caseRule=rule,
                 caseLastUpDate=caseLastUpDate,casecreatedDate=casecreatedDate,
                 caseEncID=caseEncID, caseLxID=caseLxID,caseRxID=caseRxID,caseICD9=caseICD9)
                    
            if p.DemogProvider:
                c.caseProvider=p.DemogProvider
            if caseSendDate!='None':
                c.caseSendDate=caseSendDate
            c.save()
        
    iclogging.info('reload case done')


    ##########load workflow
    try:
        wfs = file(outputdir+wffile).readlines()
    except:
        iclogging.error('Error opening file %s' % wffile)
        return
    for wf in wfs:
        wf = wf.strip()
        id, workflowCaseID_id ,workflowDate,workflowState, workflowChangedBy,workflowComment=wf.split('|')[:-1]

        case = Case.objects.filter(id = workflowCaseID_id)
        if case:
            case = case[0]
            if string.upper(workflowChangedBy).find('ESP')==0 or workflowComment.strip()=='':
                ##do not restore
                pass
            else:
                wfr = CaseWorkflow(id=id,
                           workflowCaseID=case,
                           workflowDate=workflowDate,
                           workflowState=workflowState,
                           workflowChangedBy=workflowChangedBy,
                           workflowComment=workflowComment)
                
                wfr.save()
    iclogging.info('reload caseworkflow done')
    

###################################
################################
if __name__ == "__main__":
    if sys.argv[1]=='backup':
        iclogging.info('Start to backup')
        backupcases()
        cleantable()
    
    elif sys.argv[1]=='reload':
        iclogging.info('Start to reload all')
        reload()
    elif sys.argv[1]=='reloadsent':
        iclogging.info('Start to reload all except Awaiting Review cases')
        reload(state=['AR'])

    else:
        iclogging.error('Unknown option')
                        
    iclogging.shutdown()
    
