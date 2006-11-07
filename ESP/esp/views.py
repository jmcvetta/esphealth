
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

from django.template import Context, loader, Template
from ESP.esp.models import *
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404
from django.core.paginator import ObjectPaginator, InvalidPage

import os
import string
from django.contrib.auth.decorators import login_required, user_passes_test
from ESP.settings import SITEROOT,TOPDIR
import ESP.utils.localconfig as localconfig

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.contrib.auth import REDIRECT_FIELD_NAME
import datetime

LOGIN_URL = '%s/accounts/login/' % SITEROOT

def login(request):
    "Displays the login form and handles the login action."
    manipulator = AuthenticationForm(request)
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if request.POST:
        errors = manipulator.get_validation_errors(request.POST)
        if not errors:
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '://' in redirect_to or ' ' in redirect_to:
                redirect_to = SITEROOT
            else:
                redirect_to = '%s/%s' % (SITEROOT,redirect_to)
            request.session[SESSION_KEY] = manipulator.get_user_id()
            request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        errors = {}
    request.session.set_test_cookie()
    return render_to_response('registration/login.html', {
        'form': forms.FormWrapper(manipulator, request.POST, errors),
        REDIRECT_FIELD_NAME: redirect_to,
        'site_name': Site.objects.get_current().name,
        'SITEROOT': SITEROOT,
    }, context_instance=RequestContext(request))

def rosslogout(request):
    try:
        request.user = None
        del request.user
        del request.session
        print 'request.user is None now'
    except:
        print "whoopsie on del request.session"
    return HttpResponse("You are now logged out.")



def logout(request, next_page=SITEROOT):
    "Logs out the user and displays 'You are logged out' message."
    try:
        del request.session[SESSION_KEY]
    except KeyError:
        return render_to_response('registration/logged_out.html', {'title': 'Logged out'}, context_instance=RequestContext(request))
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page or request.path)

def logout_then_login(request, login_url=LOGIN_URL):
    "Logs out the user if he is logged in. Then redirects to the log-in page."
    return logout(request, login_url)

def redirect_to_login(next, login_url=LOGIN_URL):
    "Redirects the user to the login page, passing the given 'next' page"
    return HttpResponseRedirect('%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, next))

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

def password_change(request):
    new_data, errors = {}, {}
    form = PasswordChangeForm(request.user)
    if request.POST:
        new_data = request.POST.copy()
        errors = form.get_validation_errors(new_data)
        if not errors:
            form.save(new_data)
            return HttpResponseRedirect('%sdone/' % request.path)
    return render_to_response('registration/password_change_form.html', {'form': forms.FormWrapper(form, new_data, errors)},
        context_instance=RequestContext(request))
password_change = login_required(password_change)

def password_change_done(request):
    return render_to_response('registration/password_change_done.html', context_instance=RequestContext(request))


    
def index(request):
    """
    core index page
    """
    c = Context({'request':request,'SITEROOT':SITEROOT,})
    return render_to_response('esp/index.html',c)

    

#################################
#@user_passes_test(lambda u: not u.is_anonymous() , login_url='%s/accounts/login/' % SITEROOT)
def casesearch(request, wf="*", cfilter="*", mrnfilter="*",orderby="sortid"):
    """search cases by Patient Name or MRN
    """

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
        wf = string.strip(request.POST['wf'])
    except:
        pass
    print 'got wf=%s, mrn=%s, cfilter=%s' % (wf, mrnfilter,cfilter)
    objs = Case.objects.all()
    if cfilter and cfilter <> '*':
        ##name search is wildcard search with case insensetive (sql:like '%')
        cfilter = cfilter.upper()
        objs = Case.objects.filter(caseDemog__DemogLast_Name__istartswith=cfilter)
    if mrnfilter and mrnfilter <> '*':
        ##MRN search needs exactly matching (=)
        objs = objs.filter(caseDemog__DemogMedical_Record_Number__exact=mrnfilter)

    wf_display = ""
    if wf and wf <> '*':
        objs = objs.filter(caseWorkflow=wf)
        wf_display = dict(WORKFLOW_STATES)[wf]

   ##Sort options        
    if not orderby or orderby =='sortid':
        objs =objs.order_by('id')
    elif orderby == 'sortrule':
        objs =objs.select_related().order_by('caseRuleID','esp_demog.DemogLast_Name', 'esp_demog.DemogFirst_Name')
    elif orderby == 'sortwf':
        objs =objs.select_related().order_by('caseWorkflow','esp_demog.DemogLast_Name')
    elif orderby=='sortname':
        objs = objs.select_related().order_by('esp_demog.DemogLast_Name', 'esp_demog.DemogFirst_Name')
    elif orderby == 'sortmrn':
        objs =objs.select_related().order_by('esp_demog.DemogMedical_Record_Number')
    elif orderby=='sortaddr':
        objs = objs.select_related().order_by('esp_demog.DemogAddress1','esp_demog.DemogCity','esp_demog.DemogState')
        #objs =objs.order_by('caseLastUpDate')


        
    postdest = '%s/cases/search/%s/%s/%s' % (SITEROOT,wf,cfilter,mrnfilter)
    print 'using postdest=%s' % postdest
    if objs.count()>0:
        paginate_by = 10
        paginator = ObjectPaginator(objs, paginate_by)
        page = int(request.GET.get('page', 0))
        cinfo = {
            "request": request,
            "is_search": True,
            "pname": cfilter,
            "postdest": postdest,
            "mrn":mrnfilter,
            "wf": wf,
            "orderby": orderby,
            "wf_display":wf_display,
            "object_list":paginator.get_page(page),
            "casenum": len(objs),
            "is_paginated": paginator.pages > 1,
            "results_per_page": paginate_by,
            "has_next": paginator.has_next_page(page),
            "has_previous": paginator.has_previous_page(page),
            "page": page + 1,
            "next": page + 1,
            "previous": page - 1,
            "pages": paginator.pages,
            "first_page": 0,
            "last_page": paginator.pages - 1,
            'SITEROOT':SITEROOT,
            }
    else:
        cinfo={
            "is_search": True,
            "pname": cfilter,
            "mrn":mrnfilter,
            "wf": wf,
            "orderby": orderby,
            "wf_display":wf_display,
            "casenum": 0,
            "object_list": None,
            "is_paginated": False,
            'SITEROOT':SITEROOT,
            }
    c = Context(cinfo)
    return render_to_response('esp/cases_list.html',c)
    


def caseNameSearch(request, snfilter=""):
    """search cases by Patient Name 
    """
    ##retrieve filtered objects 
    objs = Case.objects.filter(caseDemog__DemogLast_Name__startswith=cfilter)
    objs =objs.order_by('caseLastUpDate')
    postdest = '%s/cases/snsearch/' % SITEROOT   
    if objs.count()>0:
        paginate_by = 10
        paginator = ObjectPaginator(objs, paginate_by)
        page = int(request.GET.get('page', 0))
        cinfo = {
            "request": request,
            "is_search": True,
            "pname": snfilter,
            "postdest": postdest,
            "object_list":paginator.get_page(page),
            "casenum": len(objs),
            "is_paginated": paginator.pages > 1,
            "results_per_page": paginate_by,
            "has_next": paginator.has_next_page(page),
            "has_previous": paginator.has_previous_page(page),
            "page": page + 1,
            "next": page + 1,
            "previous": page - 1,
            "pages": paginator.pages,
            "first_page": 0,
            "last_page": paginator.pages - 1,
            'SITEROOT':SITEROOT,
            }
    else:
        cinfo={
            "is_search": True,
            "pname": cfilter,
            "mrn":mrnfilter,
            "wf": wf,
            "wf_display":wf_display,
            "casenum": 0,
            "object_list": None,
            "is_paginated": False,
            'SITEROOT':SITEROOT,
            }
    c = Context(cinfo)
    return render_to_response('esp/cases_list.html',c)

def caseMRNSearch(request, mrnfilter=""):
    """search cases by Patient Name 
    """
    ##retrieve filtered objects 
    objs = Case.objects.filter(caseDemog__DemogMedical_Record_Number__startswith=mrnfilter)
    objs =objs.order_by('caseLastUpDate')
    postdest = '%s/cases/mrnsearch/' % SITEROOT    
    if objs.count()>0:
        paginate_by = 10
        paginator = ObjectPaginator(objs, paginate_by)
        page = int(request.GET.get('page', 0))
        cinfo = {
            "request": request,
            "is_search": True,
            "postdest": postdest,
            "mrn":mrnfilter,
            "object_list":paginator.get_page(page),
            "casenum": len(objs),
            "is_paginated": paginator.pages > 1,
            "results_per_page": paginate_by,
            "has_next": paginator.has_next_page(page),
            "has_previous": paginator.has_previous_page(page),
            "page": page + 1,
            "next": page + 1,
            "previous": page - 1,
            "pages": paginator.pages,
            "first_page": 0,
            "last_page": paginator.pages - 1,
            'SITEROOT':SITEROOT,
            }
    else:
        cinfo={
            "is_search": True,
            "mrn":mrnfilter,
            "casenum": 0,
            "object_list": None,
            "is_paginated": False,
            'SITEROOT':SITEROOT,
            }
    c = Context(cinfo)
    return render_to_response('esp/cases_list.html',c)



###############################
#@user_passes_test(lambda u: not u.is_anonymous() , login_url='%s/accounts/login/' % SITEROOT)
def casedetail(request, object_id,restrict='F'):

    """detailed case view with workflow history
    """
    
    c = get_object_or_404(Case, pk=object_id)
    wf = c.caseworkflow_set.all().order_by('-workflowDate')
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
             "cobject":c,
             "wf":wf,
             "caseid":object_id,
             'encounters':encs,
             'pid' : pid,
             'labs':labs,
             'prescriptions':rxs,
             "wfstate":WORKFLOW_STATES,
             'SITEROOT':SITEROOT,
            }

    con = Context(cinfo)
    return render_to_response('esp/cases_detail.html',con)

#@user_passes_test(lambda u: not u.is_anonymous() , login_url='%s/accounts/login/' % SITEROOT)
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


#@user_passes_test(lambda u: not u.is_anonymous() , login_url='%s/accounts/login/' % SITEROOT)
def ruledetail(request, 
object_id):
    """rule detail
    """
    r = Rule.objects.get(id__exact=object_id)
    
    cinfo = {"request":request,
             "rule":r,
            'SITEROOT':SITEROOT,
            }
    con = Context(cinfo)
    return render_to_response('esp/rule_detail1.html',con)



#################################
def preloadview(request,table='cptloincmap'):
    rules=[]
    newrec=10
    if table == 'cptloincmap':
        maps = CPTLOINCMap.objects.all()
        maps = maps.order_by('CPT', 'CPTCompt', 'Loinc')
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
            'SITEROOT':SITEROOT,
             'newrec':range(newrec),
            }
    con = Context(cinfo)
    
    return render_to_response(returnurl,con)


################################
def showutil(request):
    cinfo = {"request":request,
             "SITEROOT":SITEROOT,
             }
    c = Context(cinfo)
    return render_to_response('esp/utiladmin.html',c)


################################
def preloadupdate(request,table='cptloincmap'):

    dbids = []
    for k in request.POST.keys():
        if string.find(k, 'ID_')!=-1:
            print request.POST[k]
            dbids.append(string.split(k,'_')[1])
    #print dbids
    datadir = os.path.join(TOPDIR,localconfig.LOCALSITE,'preLoaderData/')
    if table == 'cptloincmap':
        f = open(datadir+'esp_cptloincmap.txt','w')
        for dbid in dbids:
            cpt = request.POST['CPT_%s'% dbid]
            cmpt = request.POST['CMPT_%s'% dbid]
            loinc = request.POST['LOINC_%s'% dbid]
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if cpt and loinc:
                f.write('%s\t%s\t%s\t%s\n' % (dbid,cpt,cmpt,loinc))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_cptloincmap.txt'    
        returnurl = 'esp/cptloincmap.html'

    elif table == 'conditionloinc':
        f = open(datadir+'esp_conditionloinc.txt','w')
        for dbid in dbids:
            rule = request.POST['RULE_%s'% dbid]
            loinc = request.POST['LOINC_%s'% dbid]
            cldefine = request.POST['DEFINE_%s'% dbid]
            clsend = request.POST['SEND_%s'% dbid]
            snmdposi = request.POST['SNMDPOSI_%s'% dbid]
            snmdnega = request.POST['SNMDNEGA_%s'% dbid]
            snmdinde = request.POST['SNMDINDE_%s'% dbid]
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if loinc:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (dbid,rule,loinc,snmdposi,snmdnega,snmdinde,cldefine,clsend))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_conditionloinc.txt'  
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
                f.write('%s\t%s\t%s\t%s\t%s\n' % (dbid,rule,icd,cldefine,clsend))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_conditionicd9.txt'  
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
                f.write('%s\t%s\t%s\t%s\t%s\n' % (dbid,rule,ndc,cldefine,clsend))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_conditionndc.txt'  
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
	res.sort(key=lambda x: x.split('\t')[1:3]) # sort nicely on rule, drugname
        res.append('')
        f.write('\n'.join(res))
        f.close()
        msg = 'Data have been save to ' + datadir+fname  
        returnurl = 'esp/conditiondrugnamemap.html'

    elif table == 'rule':
        f = open(datadir+'esp_rule.txt','w')
        for dbid in dbids:
            name =request.POST['NAME_%s'% dbid]
            msgfmt = request.POST['MSGFMT_%s'% dbid]
            msgdest = request.POST['MSGDEST_%s'% dbid]
            hl7name = request.POST['HL7NAME_%s'% dbid]
            hl7code = request.POST['HL7CODE_%s'% dbid]
            hl7type = request.POST['HL7TYPE_%s'% dbid]
            note = string.strip(request.POST['NOTE_%s'% dbid])
            if string.find(dbid, 'NEW')!=-1: #new records
                dbid = ''
            if name:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (dbid,name,msgfmt,msgdest,hl7name,hl7code,hl7type,note))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_rule.txt'  
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
                f.write(s % (dbid, appname,faciname,sfaciname,tename,teemail,tephone,tecell,instname,instclia,instadd1,instadd2,instcity,instst,instzip,instcountry,instphone,instfax,infefname,infelname,infeemail,infephonearea,infephone,infephoneext,infecell,note))
        f.close()
        msg = 'Data have been save to ' + datadir+'esp_config.txt'  
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

#@user_passes_test(lambda u: not u.is_anonymous() , login_url='%s/accounts/login/' % SITEROOT)
def updateWorkflow(request,object_id):
    """update case workflow state
    write a new workflow state history record
    workflowCaseID = meta.ForeignKey(Case,edit_inline=meta.TABULAR,max_num_in_admin=3)
    workflowDate = meta.DateTimeField('Activated',auto_now=True)
    workflowState = meta.CharField('Workflow State',choices=WORKFLOW_STATES,core=True,maxlength=20 )
    workflowChangedBy = meta.CharField('Changed By', maxlength=30)
    workflowComment = meta.TextField('Comments',blank=True)
     """
    acase = Case.objects.get(id__exact=object_id)
    if acase.caseWorkflow <> request.POST['NewWorkflow']:
        wf = CaseWorkflow(workflowDate=datetime.datetime.now(),
                         workflowState=request.POST['NewWorkflow'],workflowChangedBy='ross',
                         workflowComment = request.POST['Comment'])
        acase.caseworkflow_set.add(wf)
        acase.caseWorkflow = request.POST['NewWorkflow']
        acase.caseLastUpDate = datetime.datetime.now()
        acase.save()
    else:
        print 'No change in workflow state - not saved'

    return HttpResponseRedirect("%s/cases/%s/F/" % (SITEROOT,object_id))

#@user_passes_test(lambda u: not u.is_anonymous() , login_url='%s/accounts/login/' % SITEROOT)
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

#@user_passes_test(lambda u: not u.is_anonymous() , login_url='%s/accounts/login/' % SITEROOT)
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


