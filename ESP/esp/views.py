
"""
May 26 added site root for all contexts
May 1
Now adding faked enc, Lx and Rx records to case_detail views

April 25
Workflow history is now visible and individual entries can have their comment updated
Todo - find patient by name or mrn

so far, we have a fake case and workflow generator
we can scroll through cases in each workflow state and change that state
this makes a workflow history record and updates the case state

need workflow history view for each case
find patient by name and show cases and their states

eventually need to extend case faker to include some pharmacy and labs
show case with all encounter, pharmacy, lab and pcp data
on the workflow updater screen which is probably the central one

overview (counts) of workflow states, changes by date etc onto home page
last logged in, who's logged in

"""
import os,sys
sys.path.insert(0, '/home/ESP/')

from django.template import Context, loader, Template
from ESP.esp.models import *
#from ESP.esp.forms import RegistrationForm 
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404
from django.core.paginator import Paginator, InvalidPage
# svn 1.0 alpha has changed ObjectPaginator to Paginator - rml august 2008
#from django.core.paginator import ObjectPaginator, InvalidPage
from django.core.mail import send_mail

import string
from django.contrib.auth.decorators import login_required, user_passes_test
from ESP.settings import SITEROOT,TOPDIR,LOCALSITE,CODEDIR
#import ESP.utils.localconfig as localconfig

from django.contrib.auth import authenticate, logout, login
#from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django import forms# ,oldforms # TODO fixme!
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.contrib.auth import REDIRECT_FIELD_NAME,SESSION_KEY, authenticate
import datetime,random,sha


LOGIN_URL = '%s/accounts/login/' % SITEROOT
REDIRECT_FIELD_NAME = 'next'


def esplogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if not redirect_to or '://' in redirect_to or ' ' in redirect_to:
	    if SITEROOT:
                 redirect_to = SITEROOT
            else:
                 redirect_to ='/'
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(redirect_to)
        else:
            return HttpResponseRedirect(LOGIN_URL)
            # Return a 'disabled account' error message
    else:
        # Return an 'invalid login' error message.
        return HttpResponseRedirect('/login')


############################
def oldesplogin(request):
    "Displays the login form and handles the login action."
    if not request.POST:
       return render_to_response('registration/login.html', {
          REDIRECT_FIELD_NAME: '',
         'site_name': Site.objects.get_current().name,
         'SITEROOT': SITEROOT, }, context_instance=RequestContext(request))
    else:
        username = request.POST['username']
        password = request.POST['password']
        redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
        # Light security check -- make sure redirect_to isn't garbage.
        if not redirect_to or '://' in redirect_to or ' ' in redirect_to:
    	    if SITEROOT:
                 redirect_to = SITEROOT
            else:
                 redirect_to ='/'
        user = authenticate(username=username, password=password)
        if user is not None:
	    if user.is_active:
                  login(request,user)
                  return HttpResponseRedirect(redirect_to)
            else: 
                 return HttpResponseRedirect('/login')
        else:
            return HttpResponseRedirect('/login')




def userlogout(request, next_page=SITEROOT):
    "Logs out the user and displays 'You are logged out' message."
    logout(request)
    return HttpResponseRedirect(next_page or request.path)


def logout_then_login(request, login_url=LOGIN_URL):
    "Logs out the user if he is logged in. Then redirects to the log-in page."
    return logout(request, login_url)

def redirect_to_login(next, login_url=LOGIN_URL):
    "Redirects the user to the login page, passing the given 'next' page"
    return HttpResponseRedirect('%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, next))

#####################
def password_reset(request, is_admin_site=False):
    new_data, errors = {}, {}
    form = PasswordResetForm()
    if request.POST:
        new_data = request.POST.copy()
        errors = form.get_validation_errors(new_data)
        if not errors:
            if is_admin_site:
                form.save(request.META['HTTP_HOST'])
            else:
                form.save()
            return HttpResponseRedirect('%sdone/' % request.path)
    return render_to_response('registration/password_reset_form.html', {'form': forms.FormWrapper(form, new_data, errors)},
        context_instance=RequestContext(request))

def password_reset_done(request):
    return render_to_response('registration/password_reset_done.html', context_instance=RequestContext(request))


#####################
def password_change(request):
    new_data, errors = {}, {}
    form = PasswordChangeForm(request.user)
    if request.POST:
        new_data = request.POST.copy()
        errors = form.get_validation_errors(new_data)
        if not errors:
            form.save(new_data)
            return render_to_response('registration/password_change_done.html', Context({'request':request,'SITEROOT': SITEROOT,}))
        
    return render_to_response('registration/password_change_form.html', {'form': forms.FormWrapper(form, new_data, errors), 'SITEROOT': SITEROOT, 'request':request},
        context_instance=RequestContext(request))
password_change = login_required(password_change)



###################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def index(request):
    """
    core index page
    """
    c = Context({'request':request,'SITEROOT':SITEROOT,})
    return render_to_response('esp/index.html',c)

    
#################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def casesent(request, orderby="sortid",download=''):
    """A report for sent cases
    """
    if not download :
        linebreak='<br>'
    else:
        linebreak='; '
        
    objs = Case.objects.filter(caseSendDate__isnull=False)
    returnlist=[]
    for c in objs:
        encs=[]
        labs=[]
        rxs=[]

        #lab
        orderdate=resultdate=''
        testname=''
        sitename=''
        lxstr = c.caseLxID
        if lxstr:
            labs = Lx.objects.extra(where=['id IN (%s)' % lxstr])
            labs = labs.order_by('-LxOrder_Id_Num')
            orderdate=labs[0].LxOrderDate
            resultdate=labs[0].LxDate_of_result
            testname=labs[0].LxComponentName
            relprov = Provider.objects.filter(id=labs[0].LxOrdering_Provider.id)[0]
            sitename = relprov.provPrimary_Dept
        #Rx
        drugstrl=[]
        rxstr = c.caseRxID
        if rxstr:
            rxs = Rx.objects.extra(where=['id IN (%s)' % rxstr])
            for rxRec in rxs:
                rxDur='N/A'
                if rxRec.RxStartDate and not rxRec.RxEndDate:
                    rxDur ='1'
                elif rxRec.RxStartDate and rxRec.RxEndDate:
                    rxDur =datetime.date(int(rxRec.RxEndDate[:4]),int(rxRec.RxEndDate[4:6]), int(rxRec.RxEndDate[6:8]))- datetime.date(int(rxRec.RxStartDate[:4]),int(rxRec.RxStartDate[4:6]), int(rxRec.RxStartDate[6:8]))
                    rxDur = rxDur.days +1

                drugstrl.append('%s;%s;%s;%s;%s day(s)' % (rxRec.RxNational_Drug_Code, rxRec.RxDrugName,rxRec.RxDose,rxRec.RxFrequency,rxDur))
            drugstr = (linebreak).join(drugstrl)

        #ICD9
        i9strl=[]
        i9l = c.caseICD9.split(',')
        finali9l=[]
        for i in i9l:
            finali9l=finali9l+i.split()
        for oneicd9 in finali9l:
            oneicd9=oneicd9.strip()
            if oneicd9:
                i9strl.append(getI9_onecode(oneicd9))
        i9str=(linebreak).join(i9strl)


        ##pregnant
        (msg, edc) = c.getPregnant()
        if msg!='': 
            pregstr = 'Y'
        else:
            pregstr ='N/A'
            
        onerow = ['%s' % c.id, c.caseRule.ruleName, c.caseDemog.DemogLast_Name+','+c.caseDemog.DemogFirst_Name,'%s' % c.caseDemog.DemogMedical_Record_Number,c.caseDemog.DemogGender,pregstr, c.caseDemog.DemogDate_of_Birth, sitename, testname,orderdate,resultdate,c.caseSendDate.strftime("%Y%m%d"),drugstr,i9str]
        returnlist.append(onerow)

    
    ##Sort options
    if not orderby: orderby ='sortid'

    if orderby=='sortid':
        returnlist.sort(key=lambda x:x[0])
    elif orderby == 'sortrule':
        returnlist.sort(key=lambda x:[x[1],x[2]])
    elif orderby=='sortname':
        returnlist.sort(key=lambda x:x[2])
    elif orderby == 'sortmrn':
        returnlist.sort(key=lambda x:x[3])
    elif orderby == 'sortgender':
        returnlist.sort(key=lambda x:[x[4],x[2]])
    elif orderby=='sortpreg':
        returnlist.sort(key=lambda x:[x[5],x[2]])
    elif orderby=='sortsendate':
        returnlist.sort(key=lambda x:[x[11],x[2]])
    elif orderby=='sortresdate':
        returnlist.sort(key=lambda x:[x[10],x[2]])
    elif orderby=='sortorderdate':
        returnlist.sort(key=lambda x:[x[9],x[2]])
    elif orderby=='sortdob':
        returnlist.sort(key=lambda x:x[6])
    elif orderby=='sortsite':
        returnlist.sort(key=lambda x:[x[7],x[2]])
        

    if download:
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        report_filename ='CaseArchive_%s' % datetime.datetime.now().strftime("%Y%m%d")
        response['Content-Disposition'] = 'attachment; filename="%s"' % report_filename
        
        headerl=['Case ID','Condition','Patient Name','MRN','Gender', 'Pregnancy status','D.O.B','SiteName', 'TestName','Test Order Date','Test Result Date','Date sent to DPH','Medication Prescribed','Symptoms']
        returnlist.insert(0,headerl)
        report  ='\n'.join(map(lambda x:'\t'.join(x), returnlist))
        response.write(report)
        return response
    else:
        cinfo = {
            "request": request,
            "object_list": returnlist,
            "orderby": orderby,
            "casenum": len(returnlist),
            'SITEROOT':SITEROOT,
                    }
    
        c = Context(cinfo)
        return render_to_response('esp/case_sentlist.html',c)


###################################
###################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def casedefine(request,compfilter=""):
    """a page to enable admin to search cpt, component by inputing partial of component name during the new condition define process
    """

    from django.db import connection
    #connection.use_signal_cursor = True
    cursor = connection.cursor()

    try:
        compfilter = string.strip(request.POST['CompName'])
    except:
        pass
    numrec =0
    cptcmpt_list=[]
    if compfilter:
        cursor.execute("""select cpt, CPTCompt, componentName from esp_labcomponent where upper(componentName) like '%s%s%s'
                  order by componentName, cpt, CPTCompt;""" % ('%%', string.upper(compfilter), '%%'))

#        cursor.execute("""select distinct LxTest_Code_CPT,LxComponent,LxComponentName from esp_lx where upper(LxComponentName) like '%s%s%s' order by LxTest_Code_CPT,LxComponent;""" % ('%%', string.upper(compfilter), '%%'))
        while 1:
            cptcmpt = cursor.fetchone()
            if not cptcmpt :
                break
            else:
                cpt,cmpt,name = cptcmpt
                temp = (cpt,cmpt,name,'CPT_%s_%s' % (cpt,cmpt))
                cptcmpt_list.append(temp)
          
        numrec = len(cptcmpt_list)

    cinfo={
        "request": request,
        "lxs": cptcmpt_list,
        "numrec": numrec,
        "compname": compfilter,
        'SITEROOT':SITEROOT,
        }
    c = Context(cinfo)
    return render_to_response('esp/casedefine.html',c)


###################################
###################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def casedefine_detail(request, cpt="",component=""):
    from django.db import connection
    cursor = connection.cursor()


    if cpt and component: ##need download
        returnlist=[]
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        report_filename ='CPT%sCOMP%s_%s' % (cpt, component, datetime.datetime.now().strftime("%Y%m%d"))
        response['Content-Disposition'] = 'attachment; filename="%s"' % report_filename
        headerl=['ComponentName','CPT','Component', 'Patient LastName','Patient FirstName', 'MRN','Gender', 'D.O.B','TestResult','Test OrderDate','Test Result Date','Reference Low','Reference High', 'Comment']
        returnlist.insert(0,headerl)
        cursor.execute("""select distinct LxComponentName, LxTest_Code_CPT,LxComponent, DemogLast_Name, DemogFirst_Name,DemogMedical_Record_Number,DemogGender,DemogDate_of_Birth,LxTest_results, LxOrderDate,LxDate_of_result,LxReference_Low, LxReference_High,LxComment  from esp_lx,esp_demog where esp_lx.LxPatient_id=esp_demog.id and LxTest_Code_CPT='%s' and LxComponent='%s' limit 10000;""" % (cpt,component))
        returnlist = returnlist+list(cursor.fetchall())
        
        report  ='\n'.join(map(lambda x:'\t '.join(x), returnlist))
        response.write(report)
        return response
    
    

    cptcmpt_list=[]
    for k in request.POST.keys():
        if string.find(k, 'CPT_')!=-1:
            items = string.split(k,'_')
            cptcmpt_list.append((items[1],items[2]))
    returnl=[]
    cptcmpt_list.sort()
    for i in cptcmpt_list:
        cpt,comp= i

        #get total Lx records
        cursor.execute("""select count(*) from esp_lx where LxTest_Code_CPT='%s' and LxComponent='%s' """ % (cpt,comp))
        cptnum = cursor.fetchall()[0][0]
        if int(cptnum)<=10000:                
            ##select all no numeric value
            cursor.execute("""select distinct LxTest_results from esp_lx where LxTest_Code_CPT='%s' and LxComponent='%s' and LxTest_results REGEXP '^[^0-9]' order by LxTest_results""" % (cpt,comp))
            res=cursor.fetchall()
            res_str=''
            for r in res:
                res_str = res_str + '<br>%s' % r

            ##select all no numeric value
            cursor.execute("""select distinct LxReference_High,LxReference_Low from esp_lx where LxTest_Code_CPT='%s' and LxComponent='%s' order by  LxReference_High,LxReference_Low""" % (cpt,comp))
            res=cursor.fetchall()
            ref_str=''
            for rh,rl in res:
                ref_str = ref_str + '<br>%s || %s' % (rl,rh)
                                                                        
            ##get all min, max numeric value
                cursor.execute("""select min(LxTest_results), max(LxTest_results) from esp_lx where LxTest_Code_CPT='%s' and LxComponent='%s' and  LxTest_results REGEXP '^[0-9]'""" % (cpt,comp))
                res1=cursor.fetchall()
                minv =res1[0][0]
                if not minv:
                    minv=''
                maxv = res1[0][1]
                if not maxv:
                    maxv=''
        else: ###>10K records
            minv=maxv=ref_str=""
            res_str = "<font color=RED>Please email for the results of this test<br>since there are more than 10K records in Lx table!</font>"

        compname = ''
        cursor.execute("""select componentName from esp_labcomponent where cpt='%s' and  CPTCompt='%s'""" % (cpt,comp))
        res2=cursor.fetchall()
        if res2:
            compname = '<br>'.join(map(lambda x:x[0], res2))


        returnl.append((compname,cpt,comp,res_str,minv,maxv,ref_str, cptnum ))


    if len(returnl)==0:
        returnl=None
    
    cinfo={
        "request": request,
        "lxs": returnl,
        'SITEROOT':SITEROOT,
        }
    c = Context(cinfo)
    return render_to_response('esp/casedefine_detail.html',c)
    
                                
                
###################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def casematch(request,  download=''):
    from django.db import connection
    cursor = connection.cursor()

    returnlist = []
    try:
        file = request.FILES['upfile']
        filedata =file['content'].split('\n')[1:]  ##assume the first line is header
        indx=1


        ##go through incoming data
        for onedemog in filedata:
            
            if onedemog.strip()=='':
                continue
            items = onedemog.strip().split('\t')
            if len(items)>5:
                (fname,lname,gender,dob,dphstatus,dphdate) =items[:6]
            else:
                fname = onedemog.strip()
                lname=''
                gender=''
                dob=''
                dphstatus=''
                dphdate=''

            fname = string.replace(fname, "'", '')
            lname = string.replace(lname, "'", '')

            cursor.execute("""select id, REPLACE(DemogLast_Name, "'", ""), REPLACE(DemogFirst_Name, "'", ""), DemogGender, DemogDate_of_Birth
                              from esp_demog
                              where upper(REPLACE(DemogLast_Name, "'", ""))=%s and upper(REPLACE(DemogFirst_Name, "'", ""))=%s and upper(DemogGender)=%s
                              order by DemogDate_of_Birth """, (string.upper(lname),string.upper(fname),string.upper(gender)))
            exactobjs = cursor.fetchall()
            if exactobjs:
                exactids = map(lambda x:'%s' % x[0], exactobjs)
                exactobjs = map(lambda x:x[1:], exactobjs)

            stmt = """select REPLACE(DemogLast_Name, "'", ""), REPLACE(DemogFirst_Name, "'", ""), DemogGender, DemogDate_of_Birth
                                      from esp_demog
                                      where upper(REPLACE(DemogLast_Name, "'", "")) like '%s%s' and upper(REPLACE(DemogLast_Name, "'", "")) like '%s%s' and upper(DemogGender)='%s' """ % (string.upper(lname[:3]),'%%', string.upper(fname[:2]),'%%', string.upper(gender))
            if exactobjs:
                stmt = stmt + " and id not in (%s) " % ','.join(exactids)

            if dob!='':
                dobmatch = int(dob[:4])-12
                stmt = stmt + """ and DemogDate_of_Birth !='' and substring(DemogDate_of_Birth, 1,4)>%s""" % (dobmatch)
            stmt = stmt + ' order by DemogDate_of_Birth'                 
            cursor.execute(stmt)
            res = cursor.fetchall()
            thisd = [lname,fname,gender,dob,len(exactobjs)+len(res), exactobjs, res, dphstatus,dphdate,indx]
                

            returnlist.append(thisd)
            indx+=1
    except:
        pass

        
    if download:
        report=[]
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        report_filename ='PatientMatch_%s' % datetime.datetime.now().strftime("%Y%m%d")
        response['Content-Disposition'] = 'attachment; filename="%s"' % report_filename
        
        headerl=['Patient Index', 'DPH Status','DPH Date','ESP LastName','ESP FirstName','ESP Gender', 'ESP D.O.B','Note']
        report.insert(0,headerl)
        returnlist= eval(request.POST['filedata'])
        if not returnlist: # None type is not iterable, so we must replace it with blank list
            returnlist = []
        indx=1
        for onerow in returnlist:
            (lname,fname,gender,dob,totalnum, exactrec, totalrec,dphstatus,dhpdate,indx) = onerow
            for i in exactrec:
                report.append(['Patient%s' % indx, dphstatus,dhpdate,'%s' % i[0],'%s' % i[1],'%s'%i[2],'%s'%i[3],'Exact Match'])
            for i in totalrec:
                report.append(['Patient%s' %indx, dphstatus,dhpdate,'%s'%i[0],'%s'%i[1],'%s'%i[2],'%s'%i[3],''])
            if int(totalnum)==0:
                report.append(['Patient%s' %indx,dphstatus,dhpdate,'','','','',''])
            indx+=1
        report  ='\n'.join(map(lambda x:'\t'.join(x), report))
        response.write(report)
        return response
                                                    
    else:
        
        if len(returnlist)>0:
            cinfo = {

                "request": request,
                "filedata": returnlist,
                'SITEROOT':SITEROOT,
                }
        else:
            cinfo={
                "request": request,
                "filedata": None,
                'SITEROOT':SITEROOT,
                }
        c = Context(cinfo)
        return render_to_response('esp/matchupload.html',c)



#################################
def getDownloaddata(objs):
    ##return a list of data ['Case ID','Condition','Patient Name','MRN','D.O.B','Gender','EDC','TestName','Test Order Date','Test Result Date','TestResult','ICD9']
    returnlist = []
    for c in objs:
        encs=[]
        labs=[]
        rxs=[]
        
        #lab
        orderdate=resultdate=''
        testname=''
        sitename=''
        lxstr = c.caseLxID
        if lxstr:
            labs = Lx.objects.extra(where=['id IN (%s)' % lxstr])
            labs = labs.order_by('LxOrder_Id_Num')
            orderdate = '; '.join([i.LxOrderDate for i in labs])
            resultdate='; '.join([i.LxDate_of_result for i in labs])
            testname='; '.join([i.LxComponentName for i in labs])
            testresult = '; '.join([i.LxTest_results for i in labs])
            
            
            
        #ICD9
        linebreak='; '
        i9strl=[]
        i9l = c.caseICD9.split(',')
        finali9l=[]
        for i in i9l:
            finali9l=finali9l+i.split()
        for oneicd9 in finali9l:
            oneicd9=oneicd9.strip()
            if oneicd9:
                i9strl.append(getI9_onecode(oneicd9))
        i9str=(linebreak).join(i9strl)
        
        
        #preg
        (msg, edc) = c.getPregnant()
        if not edc:
            edc = ''
        onerow = ['%s' % c.id, c.caseRule.ruleName, c.caseDemog.DemogLast_Name+','+c.caseDemog.DemogFirst_Name,'%s' % c.caseDemog.DemogMedical_Record_Number,c.caseDemog.DemogDate_of_Birth, c.caseDemog.DemogGender,edc, testname,orderdate,resultdate,testresult ,i9str]
        returnlist.append(onerow)
    return returnlist

#################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def casesearch(request, inprod="1", wf="*", cfilter="*", mrnfilter="*",rulefilter="0", orderby="sortid",download=''):
    """search cases by Patient Name or MRN
    """
    datecol = 'LastUpdated'
    
    rules = Rule.objects.filter(ruleinProd=inprod)
    rules.order_by('ruleName')
    
    ##retrieve filtered objects
    try:
        cfilter = string.strip(request.POST['PatientName'])
    except:
        pass
    try:
        mrnfilter = string.strip(request.POST['MRN'])
    except:
        pass

    try:
        rulefilter = string.strip(request.POST['RULE'])
    except:
        pass
        #rulefilter = rulefilter
                        
    if rulefilter=="":
        rulefilter="0"
        
    if string.upper(wf)=='Q': #queue
        datecol = "Date Approved"
    elif  string.upper(wf)=='S': #sent
        datecol = 'Date Sent'

    #print 'got wf=%s, mrn=%s, cfilter=%s' % (wf, mrnfilter,cfilter)
    if int(inprod)==1:
        objs = Case.objects.all()
    else:
        objs = TestCase.objects.all()

    if cfilter and cfilter <> '*':
        ##name search is wildcard search with case insensetive (sql:like '%')
        cfilter = cfilter.upper()
        objs = objs.filter(caseDemog__DemogLast_Name__istartswith=cfilter)
    if mrnfilter and mrnfilter <> '*':
        ##MRN search needs exactly matching (=)
        objs = objs.filter(caseDemog__DemogMedical_Record_Number__exact=mrnfilter)
    if '%s' % rulefilter <>'0':
        #objs = objs.filter(caseRule__ruleName__exact=rulefilter)
        objs = objs.filter(caseRule__id__exact=rulefilter)
        
    wf_display = ""
    if wf and wf <> '*':
        objs = objs.filter(caseWorkflow=wf)
        wf_display = dict(WORKFLOW_STATES)[wf]

        
    ##Sort options        
    if not orderby or orderby =='sortid':
        objs =objs.order_by('id')
    elif orderby == 'sortrule':
        objs =objs.select_related().order_by('esp_rule.ruleName','esp_demog.DemogLast_Name', 'esp_demog.DemogFirst_Name')
    elif orderby == 'sortdate' or orderby =='sortloc': #sort by order date
        finalobjs=[]
        for obj in objs:
            lxdate = obj.getLxOrderdate()
            loc = obj.getLxProviderSite()
            finalobjs.append([obj, lxdate,loc])
        if orderby == 'sortdate':
            finalobjs.sort(key=lambda x:x[1])
        else:
            finalobjs.sort(key=lambda x:x[2])
        objs = map(lambda x:x[0], finalobjs)
        #objs =objs.select_related().order_by('caseLxID')
    elif orderby == 'sortwf':
        objs =objs.select_related().order_by('caseWorkflow','esp_demog.DemogLast_Name')
    elif orderby=='sortname':
        objs = objs.select_related().order_by('esp_demog.DemogLast_Name', 'esp_demog.DemogFirst_Name')
    elif orderby == 'sortmrn':
        objs =objs.select_related().order_by('esp_demog.DemogMedical_Record_Number')
    elif orderby=='sortaddr':
        objs = objs.select_related().order_by('esp_demog.DemogAddress1','esp_demog.DemogCity','esp_demog.DemogState')
        #objs =objs.order_by('caseLastUpDate')
    elif orderby == 'datecol':
        objs = objs.select_related().order_by('esp_case.caseLastUpDate')
        
    postdest = '%s/cases/search/%s/%s/%s/%s/%s/' % (SITEROOT,wf,cfilter,mrnfilter,rulefilter,orderby)
    #print 'using postdest=%s, rulefilter=%sDDD' % (postdest,rulefilter)
    if download:
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        report_filename ='TestCases_%s' % datetime.datetime.now().strftime("%Y%m%d")
        response['Content-Disposition'] = 'attachment; filename="%s"' % report_filename
        
        
        returnlist = getDownloaddata(objs)
        headerl=['Case ID','Condition','Patient Name','MRN','D.O.B','Gender','EDC','TestName','Test Order Date','Test Result Date','TestResult','ICD9']
        returnlist.insert(0,headerl)
        report  ='\n'.join(map(lambda x:'\t'.join(x), returnlist))
        response.write(report)
        return response
    elif len(objs)>0:
        paginate_by = 10
        paginator = Paginator(objs, paginate_by)
        page = int(request.GET.get('page', 1))
        thispage = paginator.page(page)
        cinfo = {
            "request": request,
            "is_search": True,
            "rules":rules,
            "pname": cfilter,
            "postdest": postdest,
            "mrn":mrnfilter,
            "inprod":inprod,
            "wf": wf,
            "rulefilter":rulefilter,
            "datecol":datecol,
            "orderby": orderby,
            "wf_display":wf_display,
            "object_list": thispage.object_list,
            "casenum": len(objs),
            "is_paginated": paginator.num_pages > 1,
            "results_per_page": paginate_by,
            "has_next": thispage.has_next(),
            "has_previous": thispage.has_previous(),
            "page": page,
            "next": page + 1,
            "previous": max(page - 1,1),
            "pages": paginator.num_pages,
            "first_page": 1,
            "last_page": max(paginator.num_pages,1),
            'SITEROOT':SITEROOT,
            }
    else:
        cinfo= {
            "request": request,
            "is_search": True,
            "rules":rules,
            "pname": cfilter,
            "postdest": postdest,
            "mrn":mrnfilter,
            "inprod":inprod,
            "wf": wf,
            "rulefilter":rulefilter,
            "datecol":datecol,
            "orderby": orderby,
            "wf_display":wf_display,
            "casenum": None,
            "object_list": None,
            "is_paginated": False,
            'SITEROOT':SITEROOT,
            }
    c = Context(cinfo)
    return render_to_response('esp/cases_list.html',c)
    


    

###############################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def casedetail(request, inprod="1", object_id=None,restrict='F'):

    """detailed case view with workflow history
    """
    if int(inprod)==1:
        c = get_object_or_404(Case, pk=object_id)
        wf = c.caseworkflow_set.all().order_by('-workflowDate')
    else:
        c = get_object_or_404(TestCase, pk=object_id)
        wf = None
        
    pid = c.caseDemog.id
    encs=[]
    labs=[]
    rxs=[]

    if restrict == 'F': ##full view
        encs = Enc.objects.filter(EncPatient__id__exact=pid)
        labs = Lx.objects.filter(LxPatient__id__exact=pid)
        rxs = Rx.objects.filter(RxPatient__id__exact=pid)
    else: #restrict view
        encstr = c.caseEncID
        lxstr = c.caseLxID
        rxstr = c.caseRxID
        if encstr:
            encs = Enc.objects.extra(where=['id IN (%s)' % encstr])
        if lxstr:
            labs = Lx.objects.extra(where=['id IN (%s)' % lxstr])
        if rxstr:
            rxs = Rx.objects.extra(where=['id IN (%s)' % rxstr])
                                        
    print 'got %d encs, %d lx, %d rx' % (len(encs),len(labs),len(rxs))
    print ` WORKFLOW_STATES`
    cinfo = {"request":request,
             "restrict":restrict,
             "cobject":c,
             "inprod":inprod,
             "wf":wf,
             "caseid":object_id,
             'encounters':encs,
             'pid' : pid,
             'labs':labs,
             'prescriptions':rxs,
             "wfstate":WORKFLOW_STATES[:-1],
             'SITEROOT':SITEROOT,
            }

    con = Context(cinfo)
    return render_to_response('esp/cases_detail.html',con)


###################################
def getI9(oneenc):
    returnl=[]
    for oneicd9 in oneenc.EncICD9_Codes.split(' '):
        i9str=getI9_onecode(oneicd9)
        returnl.append((oneicd9,i9str))
                                                    
    return returnl

###################################
def getI9_onecode(oneicd9):
    ilong = icd9.objects.filter(icd9Code__exact=oneicd9)
    if ilong:
        ilong = ilong[0].icd9Long # not sure why, but > 1 being found!
    else:
        ilong=''
        
    i9str = '%s=%s' % (oneicd9,ilong)
    return i9str

#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def pcpdetail(request, object_id):
    """detailed case view with workflow history
    """
    p = Provider.objects.get(id__exact=object_id)
    cinfo = {"request":request,
             "pcp":p,
             'SITEROOT':SITEROOT,
             }
    con = Context(cinfo)
    return render_to_response('esp/pcp_detail.html',con)


#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def lxdetail(request, object_id):
    """detailed Lab result  view for a given lab order
    """
    lx = Lx.objects.get(id__exact=object_id)
    cinfo = {"request":request,
             "lx":lx,
             'SITEROOT':SITEROOT,
             }
    con = Context(cinfo)
    return render_to_response('esp/lx_detail.html',con)



#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def ruledetail(request, object_id):
    """rule detail
    """
    r = Rule.objects.get(id__exact=object_id)
    
    cinfo = {"request":request,
             "rule":r,
            'SITEROOT':SITEROOT,
            }
    con = Context(cinfo)
    return render_to_response('esp/rule_detail1.html',con)



#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL)
def preloadrulexclud(request,update=0):

    rules = Rule.objects.all()
    rules.order_by('ruleName')
    newrec=10
    exclude_l=[]
    returnurl="esp/rule_excludlist.html"
    msg=''
    if int(update)==2:
        ruleid = string.strip(request.POST['TORULE'])
        fromruleid = string.strip(request.POST['FROMRULE'])
        if int(fromruleid) == 0:
            msg = "Please select condition to show exclusion list first"
        else:
            ##need copy/paste
            fromr = Rule.objects.filter(id = fromruleid)[0]
            torule = Rule.objects.filter(id = ruleid)[0]
            torule.ruleExcludeCode=fromr.ruleExcludeCode
            torule.save()
            msg = "<br>The exclusion list for %s has been copied to %s in Database!<br>" % (fromr.ruleName,torule.ruleName)
            
    elif int(update)==1: ##save into DB
        ruleid = string.strip(request.POST['RULE'])
        
        thisr = Rule.objects.filter(id = ruleid)[0]
        save_l=[]
        if thisr.ruleExcludeCode:
            exclude_l = eval(thisr.ruleExcludeCode)
            for dbid in range(1,len(exclude_l)+1):
                cpt = request.POST['CPT_%s'% dbid].strip()
                cmpt = request.POST['CMPT_%s'% dbid].strip()
                if cpt or cmpt:
                    if (cpt,cmpt)not in save_l:
                        save_l.append((cpt,cmpt))
        for dbid in range(newrec):
            cpt = request.POST['CPT_NEW%s'% dbid].strip()
            cmpt = request.POST['CMPT_NEW%s'% dbid].strip()
            if cpt or cmpt:
                if (cpt,cmpt)not in save_l:
                    save_l.append((cpt,cmpt))
        thisr.ruleExcludeCode = '%s' % save_l
        thisr.save()
        msg = "<br>The exclusion list for %s has been saved to Database!<br>" % thisr.ruleName
        newrec=0
        exclude_l=[]
         
                                                                                                                       
    else:    
        try:
            ruleid = string.strip(request.POST['RULE'])
            thisr = Rule.objects.filter(id = ruleid)[0]
            if thisr.ruleExcludeCode:
                exclude_l = eval(thisr.ruleExcludeCode)
                exclude_l.sort()
                exclude_l=zip(range(1,len(exclude_l)+1),exclude_l)

        except:
            ruleid=0
            newrec=0
            pass
                     
        
    cinfo = {"request":request,
             "rules": rules,
             "msg":msg,
             "preloadrule": ruleid,
             "exclusions":exclude_l,
             'newrec':range(newrec),
             'SITEROOT':SITEROOT,
                         }
    con = Context(cinfo)
    
    return render_to_response(returnurl,con)

        

#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL)
def preloadview(request,table='cptloincmap',orderby="cpt"):
    if not request.user.is_staff:
        return HttpResponse("You do not have permission to see this page")
    
    rules=[]
    newrec=10
    if table == 'cptloincmap':
        maps = CPTLOINCMap.objects.all()
        
        try:
            orderby = string.strip(request.POST['ORDERBY'])
        except:
            pass
        if orderby == 'cpt':
            maps = maps.order_by('CPT', 'CPTCompt', 'Loinc')
        elif  orderby == 'cmptname':
            newm = map(lambda x:(x.getComptName(), x.CPT,x.CPTCompt, x), maps)
            newm.sort()
            maps = map(lambda x:x[3], newm)
        elif orderby == 'loinc':
            maps = maps.order_by('Loinc','CPT', 'CPTCompt')

        returnurl = 'esp/cptloincmap.html'
    elif table == 'conditionloinc':
        maps = ConditionLOINC.objects.all()
        maps =maps.select_related().order_by('esp_rule.ruleName', 'CondiLOINC')
        rules = Rule.objects.all()
        rules.order_by('ruleName')
        returnurl = 'esp/conditionloincmap.html'
    elif table == 'conditionndc':
        maps = ConditionNdc.objects.all()
        maps =maps.select_related().order_by('esp_rule.ruleName', 'CondiNdc')
        rules = Rule.objects.all()
        rules.order_by('ruleName')
        returnurl = 'esp/conditionndcmap.html'
    elif table == 'conditiondrugname':
        maps = ConditionDrugName.objects.all()
        maps =maps.select_related().order_by('esp_rule.ruleName', 'CondiDrugName')
        rules = Rule.objects.all()
        rules.order_by('ruleName')
        returnurl = 'esp/conditiondrugnamemap.html'
    elif table == 'conditionicd9':
        maps = ConditionIcd9.objects.all()
        maps =maps.select_related().order_by('esp_rule.ruleName', 'CondiICD9')
        rules = Rule.objects.all()
        rules.order_by('ruleName')
        returnurl = 'esp/conditionicd9map.html'
    elif table =='config':
        maps = config.objects.all()
        maps = maps.order_by('institution_name')
        newrec=2
        returnurl = 'esp/config.html'
    elif table == 'rule':
        maps = Rule.objects.all()
        maps = maps.order_by('ruleName')
        newrec=3
        returnurl = 'esp/rule.html'
        
    cinfo = {"request":request,
            'maps': maps,
             'rules':rules,
             "wfstate":WORKFLOW_STATES[:-1],
             "orderby": orderby,
            'SITEROOT':SITEROOT,
             'newrec':range(newrec),
            }
    con = Context(cinfo)
    
    return render_to_response(returnurl,con)


#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def showutil(request):
    if not request.user.is_staff:
        return HttpResponse("You do not have permission to see this page")
            
    cinfo = {"request":request,
             "SITEROOT":SITEROOT,
             }
    c = Context(cinfo)
    return render_to_response('esp/utiladmin.html',c)


#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def preloadupdate(request,table='cptloincmap'):
    if not request.user.is_staff:
        return HttpResponse("You do not have permission to see this page")
            
    dbids = []
    for k in request.POST.keys():
        if string.find(k, 'ID_')!=-1:
            print request.POST[k]
            dbids.append(string.split(k,'_')[1])
    #print dbids
    from django.db import connection
    cursor = connection.cursor()
            
    lines=[]
    okmsg = '<br><br>Data also has been saved to Database!'
    errmsg = '<br><br><font color="RED">However there is an ERROR when saved to DB</font>'
    datadir = os.path.join(TOPDIR,LOCALSITE,'preLoaderData/')
    if table == 'cptloincmap':
        f = open(datadir+'esp_cptloincmap.txt','w')
        for dbid in dbids:
            cpt = request.POST['CPT_%s'% dbid]
            cmpt = request.POST['CMPT_%s'% dbid]
            loinc = request.POST['LOINC_%s'% dbid]
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if cpt and loinc:
                lines.append([dbid,cpt,cmpt,loinc])
                f.write('%s\t%s\t%s\t%s\n' % (dbid,cpt,cmpt,loinc))
        f.close()
        msg = 'Data has been saved to ' + datadir+'esp_cptloincmap.txt'

        ##save to DB
        #from ESP.utils.preLoader import load2cptloincmap
        #try:
        #    load2cptloincmap('esp_cptloincmap',lines, cursor)
        #    msg = msg+ okmsg
        #except:
        #    msg = msg+ errmsg

#        import subprocess
#        script = os.path.join(CODEDIR,'utils', 'preLoader.py')
#        pid = subprocess.Popen([sys.executable, script,'esp_cptloincmap'], shell=True).pid
#        msg = msg +'<br>%s %s<br>Backend process %s has been launched in order to save data to database' % (sys.executable, script, pid)

        returnurl = 'esp/cptloincmap.html'

    elif table == 'conditionloinc':
        f = open(datadir+'esp_conditionloinc.txt','w')
        for dbid in dbids:
            rule = request.POST['RULE_%s'% dbid]
            loinc = request.POST['LOINC_%s'% dbid]
            ope = request.POST['OPE_%s'% dbid]
            opevalue = request.POST['VALUE_%s'% dbid]
            cldefine = request.POST['DEFINE_%s'% dbid]
            clsend = request.POST['SEND_%s'% dbid]
            snmdposi = request.POST['SNMDPOSI_%s'% dbid]
            snmdnega = request.POST['SNMDNEGA_%s'% dbid]
            snmdinde = request.POST['SNMDINDE_%s'% dbid]
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if loinc:
                items = [dbid,rule,loinc,ope,opevalue,snmdposi,snmdnega,snmdinde,cldefine,clsend]
                lines.append(items)
                f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'  % tuple(items))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_conditionloinc.txt'  

        ##save to DB
        from ESP.utils.preLoader import load2loinc
        try:
            load2loinc('esp_conditionloinc',lines, cursor)
            msg = msg+ okmsg
        except:
            msg = msg+ errmsg
                         
        returnurl = 'esp/conditionloincmap.html'

    elif table == 'conditionicd9':
        f = open(datadir+'esp_conditionicd9.txt','w')
        for dbid in dbids:
            rule = request.POST['RULE_%s'% dbid]
            icd = request.POST['ICD_%s'% dbid]
            cldefine = request.POST['DEFINE_%s'% dbid]
            clsend = request.POST['SEND_%s'% dbid]
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if icd:
                items = [dbid,rule,icd,cldefine,clsend]
                lines.append(items)
                f.write('%s\t%s\t%s\t%s\t%s\n' % tuple(items))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_conditionicd9.txt'  
        ##save to DB
        from ESP.utils.preLoader import load2icd9
        try:
            load2icd9('esp_conditionicd9',lines, cursor)
            msg = msg+ okmsg
        except:
            msg = msg+ errmsg
                                                            

        returnurl = 'esp/conditionicd9map.html'

    elif table == 'conditionndc':
        f = open(datadir+'esp_conditionndc.txt','w')
        for dbid in dbids:
            rule = request.POST['RULE_%s'% dbid]
            ndc = request.POST['NDC_%s'% dbid]
            cldefine = request.POST['DEFINE_%s'% dbid]
            clsend = request.POST['SEND_%s'% dbid]
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if ndc:
                items = [dbid,rule,ndc,cldefine,clsend]
                lines.append(items)
                f.write('%s\t%s\t%s\t%s\t%s\n' % tuple(items))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_conditionndc.txt'  

         ##save to DB
        from ESP.utils.preLoader import load2ndc
        try:
            load2ndc('esp_conditionndc',lines, cursor)
            msg = msg+ okmsg
        except:
            msg = msg+ errmsg
                                                            
        returnurl = 'esp/conditionndcmap.html'
    elif table == 'conditiondrugname':
        fname = 'esp_conditiondrugname.txt'
        f = open(os.path.join(datadir,fname),'w')
        res = []
        for dbid in dbids:
            rule = request.POST['RULE_%s'% dbid]
            drugname = request.POST['NDC_%s'% dbid]
            route = request.POST['ROUTE_%s'% dbid]
            cldefine = request.POST['DEFINE_%s'% dbid]
            clsend = request.POST['SEND_%s'% dbid]
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if drugname:
                res.append('%s\t%s\t%s\t%s\t%s\t%s' % (dbid,rule,drugname,route,cldefine,clsend))
                lines.append([dbid,rule,drugname,route,cldefine,clsend])
                
	res.sort(key=lambda x: x.split('\t')[1:3]) # sort nicely on rule, drugname
        res.append('')
        f.write('\n'.join(res))
        f.close()
        msg = 'Data have been save to ' + datadir+fname

        ##save to DB
        from ESP.utils.preLoader import load2DrugNames
        try:
            load2DrugNames('esp_conditiondrugname',lines, cursor)
            msg = msg+ okmsg
        except:
            msg = msg+ errmsg
                                                            
        returnurl = 'esp/conditiondrugnamemap.html'

    elif table == 'rule':
        f = open(datadir+'esp_rule.txt','w')
        for dbid in dbids:
            name =request.POST['NAME_%s'% dbid]
            initstatus = request.POST['INITSTATUS_%s'% dbid]
            inprod = request.POST['INPROD_%s'% dbid]
            msgfmt = request.POST['MSGFMT_%s'% dbid]
            msgdest = request.POST['MSGDEST_%s'% dbid]
            hl7name = request.POST['HL7NAME_%s'% dbid]
            hl7code = request.POST['HL7CODE_%s'% dbid]
            hl7type = request.POST['HL7TYPE_%s'% dbid]

           # excludl = request.POST['EXCLUDE_%s'% dbid]
            note = string.strip(request.POST['NOTE_%s'% dbid])
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
                excludl = ''
            else:
                thisr = Rule.objects.filter(id = dbid)[0]
                excludl = thisr.ruleExcludeCode
            if name:
                temp= '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (dbid,name,initstatus, inprod,msgfmt,msgdest,hl7name,hl7code,hl7type,note,excludl)
                lines.append(temp.split('\t'))
                f.write('%s\n' % temp)
        f.close()

        msg = 'Data have been save to ' + datadir+'esp_rule.txt'
        
        ##save to DB
        from ESP.utils.preLoader import load2rule
        try:
            load2rule('esp_rule',lines)
            msg = msg+ okmsg
        except:
            msg = msg+ errmsg


        returnurl = 'esp/rule.html'
        
    elif table == 'config':
        f = open(datadir+'esp_config.txt','w')
        for dbid in dbids:
            appname = request.POST['APP_%s'% dbid]
            faciname = request.POST['FACI_%s'% dbid]
            sfaciname = request.POST['SENDFAC_%s'% dbid]

            tename = request.POST['TECHNAME_%s'% dbid]
            teemail = request.POST['TECHEMAIL_%s'% dbid]
            tephone = request.POST['TECHTEL_%s'% dbid]
            tecell = request.POST['TECHCELL_%s'% dbid]

            instname = request.POST['INSTNAME_%s'% dbid]
            instclia = request.POST['INSTCLIA_%s'% dbid]
            instadd1 = request.POST['INSTADRS1_%s'% dbid]
            instadd2 = request.POST['INSTADRS2_%s'% dbid]
            instcity = request.POST['INSTCITY_%s'% dbid]
            instst = request.POST['INSTST_%s'% dbid]
            instzip = request.POST['INSTZIP_%s'% dbid]
            instcountry = request.POST['INSTCOUNT_%s'% dbid]
            instphone = request.POST['INSTPHONE_%s'% dbid]
            instfax = request.POST['INSTFAX_%s'% dbid]

            infefname = request.POST['INFEFNAME_%s'% dbid]
            infelname = request.POST['INFELNAME_%s'% dbid]
            infeemail = request.POST['INFEEMAIL_%s'% dbid]
            infephone = request.POST['INFETEL_%s'% dbid]
            infephonearea = request.POST['INFETELAREA_%s'% dbid]
            infephoneext = request.POST['INFETELEXT_%s'% dbid]
            infecell = request.POST['INFECEL_%s'% dbid]
            
            note = string.strip(request.POST['NOTE_%s'% dbid])
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if appname:
                s ='%s\t'*25 + '%s\n'
                items = [dbid, appname,faciname,sfaciname,tename,teemail,tephone,tecell,instname,instclia,instadd1,instadd2,instcity,instst,instzip,instcountry,instphone,instfax,infefname,infelname,infeemail,infephonearea,infephone,infephoneext,infecell,note]
                lines.append(items)
                f.write(s % tuple(items))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_config.txt'
        ##save to DB
        from ESP.utils.preLoader import load2config
        if 1: #try:
            load2config('esp_config',lines,cursor)
            msg = msg+ okmsg
        #except:
        #    msg = msg+ errmsg
            
            
        returnurl = 'esp/config.html'
        
    ###########        
    cinfo = {"request":request,
            'msg': msg,
            'SITEROOT':SITEROOT,
            }
    con = Context(cinfo)
    
    return render_to_response(returnurl,con)


#################################
def showhelp(request, topic=None):
    print 'topic=', topic
    if topic:
        try:
        	h = get_object(helpdb,helpTopic__exact=topic)
        except:
                h = helpdb()
                h.helpTopic = 'Not available yet'
                h.helpText = 'Sorry, nothing is written for this topic (yet)'

    else:
    	h = None
    cinfo = {"request":request,
             "object":h,
             "SITEROOT":SITEROOT,
             }
    c = Context(cinfo)
    return render_to_response('esp/help.html',c)


#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL)
def updateWorkflow(request,object_id,newwf=''):
    """update case workflow state
    write a new workflow state history record
    workflowCaseID = meta.ForeignKey(Case,edit_inline=meta.TABULAR,max_num_in_admin=3)
    workflowDate = meta.DateTimeField('Activated',auto_now=True)
    workflowState = meta.CharField('Workflow State',choices=WORKFLOW_STATES,core=True,maxlength=20 )
    workflowChangedBy = meta.CharField('Changed By', maxlength=30)
    workflowComment = meta.TextField('Comments',blank=True)
     """

    acase = Case.objects.get(id__exact=object_id)
    if not newwf:
        newwf = request.POST['NewWorkflow']
        cmt = request.POST['Comment']
    else:
        cmt=''

   # if acase.caseWorkflow <> newwf:
    wf = CaseWorkflow(workflowDate=datetime.datetime.now(),
                         workflowState=newwf,
                         workflowChangedBy=request.user.username,
                         workflowComment = cmt)
    acase.caseworkflow_set.add(wf)
    acase.caseWorkflow = newwf
    acase.caseLastUpDate = datetime.datetime.now()
    acase.save()
        
    ###########Go to a confirm page
    msg='The workflow state of this case has been successfully changed to "%s"!' % dict(WORKFLOW_STATES)[newwf]
    arcase = Case.objects.filter(caseWorkflow='AR')
    if arcase:
        nextcaseid=arcase[0].id
    else:
        nextcaseid=''
        
    cinfo = {"request":request,
             'wfmsg': msg,
             'inprod': 1,
             'nextcaseid':nextcaseid,
             'SITEROOT':SITEROOT,
                             }
    con = Context(cinfo)
    
    return render_to_response('esp/cases_detail.html',con)
            



#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def wfdetail(request, object_id):
    """detailed workflow view
    """
    wf = get_object_or_404(CaseWorkflow, pk=object_id)
    caseid = wf.workflowCaseID.id
    cinfo = {"request":request,
             "object":wf,
             "caseid":caseid,
             'SITEROOT':SITEROOT,
    }
    c = Context(cinfo)
    return render_to_response('esp/workflow_detail.html',c)


#######################################
@user_passes_test(lambda u: u.is_authenticated() , login_url=LOGIN_URL )
def updateWorkflowComment(request,object_id):
    """update caseworkflow comment only
    workflowComment = meta.TextField('Comments',blank=True)
     """
    wf = CaseWorkflow.objects.get(id__exact=object_id)
    caseid = wf.workflowCaseID.id
    if request.POST['NewComment'].strip() > ' ':
        nowd = datetime.datetime.now()
        saveme = wf.workflowComment
        newme = request.POST['NewComment']
        wf.workflowDate=nowd
        wf.workflowComment = '%s\nAdded at %s: %s' % (saveme, nowd.isoformat(), newme)
        wf.save()
    else:
        print 'No change in workflow comment - not saved'
        
    return HttpResponseRedirect("%s/cases/%s/F/" % (SITEROOT,caseid))


