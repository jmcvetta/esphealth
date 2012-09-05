#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseNotAllowed, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.mail import mail_admins
from django.shortcuts import render_to_response

from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site
from django.core.servers.basehttp import FileWrapper


from ESP.vaers.models import AdverseEvent, Case, Questionnaire, ADVERSE_EVENT_CATEGORY_ACTION
from ESP.vaers.forms import CaseConfirmForm
from ESP.utils.utils import log, Flexigrid
from ESP.emr.models import Immunization, Encounter, Prescription,LabResult,Allergy
from ESP.settings import VAERS_LINELIST_PATH

import datetime

PAGE_TEMPLATE_DIR = 'pages/vaers/'
WIDGET_TEMPLATE_DIR = 'widgets/vaers/'

@login_required
def index(request):
    # Complete query and present results
    cases = Case.paginate()
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'home.html',
                              {'cases':cases,
                               'page':1
                               })
@login_required
def list_cases(request):
    # This is a ajax call. Our response contains only the result page.

    # Page may be passed in the query string and must be a positive number
    
    grid = Flexigrid(request)
    page = grid.page
    

    # Complete query and present results
    cases = Case.paginate(page=int(page))
    total = Case.objects.all().count()
    return direct_to_template(request, WIDGET_TEMPLATE_DIR +'case_grid.json',
                              {'cases':cases,
                               'total':total,
                               'page':page},
                              mimetype='application/json'
                              )


@login_required
def notify(request, id):

    case = AdverseEvent.by_id(id)
    if request.method == 'POST' and case:
        try:
            assert case.is_fake()
            email = request.POST.get('email', None)
            case.mail_notification(email_address=email)
            result = 'Successfully sent report on case %s to %s' % (
                case.id, email)
            return HttpResponse(result)
        except Exception, why:
            log.warn('Exception during email notification: %s' % why)
    else:
        return direct_to_template(request, PAGE_TEMPLATE_DIR + 'notify.html')

@login_required
def report(request):
    cases = AdverseEvent.objects.all()
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'report.html',
                              {'cases':cases})                             
    
# @param id : is the primary key of the questionnaire or the digest value, depending on ptype
def case_details(request, ptype, id):
    '''
    This view presents a user with case details and a form to update a specific questionnaire 
    It can accept either a digest value or a questionnaire id, and uses ptype to determine which is being provided.
    If the details are accessed via digest, user may be anonymous.  Otherwise, user must be logged in and have the 
    vaers.view_phi permission
    '''
    category = None
    if ptype=='case':
        if request.user.has_perm('vaers.view_phi'):
            questionnaire = Questionnaire.objects.get(id=id)
        else:
            return HttpResponseForbidden('You cannot access this page unless you are logged in and have permission to view PHI.')
    elif ptype=='digest':
        questionnaire = Questionnaire.by_digest(id)
        if not any(x for x in ['AR','AS'] if x==questionnaire.state):
            return HttpResponse('You have already processed this case.  Thank you for your attention.')
    else: 
        #should never get here due to regex in vaers/urls.py for this view, but just in case...
        return HttpResponse('<h2>Vaers page type "' + ptype + '" not found.  Valid types are "case" and "digest".</h2>')
    
    case = questionnaire.case
    #another just in case catch...
    if not case: raise Http404
    
    #finding the highest category in the event, 
    if  case.adverse_events.filter(category__startswith ='2'):#2_rare
        category  = ADVERSE_EVENT_CATEGORY_ACTION[1][0]
    elif  case.adverse_events.filter(category__startswith ='3'):#3_possible
        category  =  ADVERSE_EVENT_CATEGORY_ACTION[2][0] 
    elif  case.adverse_events.filter(category__startswith ='1'):#1_common
        category  =  ADVERSE_EVENT_CATEGORY_ACTION[0][0]  
    
    if category == ADVERSE_EVENT_CATEGORY_ACTION[0][0] : 
        return HttpResponseForbidden(ADVERSE_EVENT_CATEGORY_ACTION[0][1])
    
    provider = questionnaire.provider
    if not provider: 
        #likewise, not likely to be a problem since provider has not-null foreign key attributes in db.
        return HttpResponseForbidden('No provider in questionnaire')
    
    if request.method == 'POST':
        form = CaseConfirmForm(request.POST) 
    else:
        form = CaseConfirmForm()

    if request.method == 'POST' and form.is_valid():
        next_status = {
            'confirm':'Q',
            'false_positive':'FP'
            #,'wait':'UR'
            }
        
        # this is where we get stuff from the form
        # initializing flags
        questionnaire.state = next_status[form.cleaned_data['state']]
        questionnaire.comment = form.cleaned_data['comment']
        questionnaire.message_ishelpful=  form.cleaned_data['message_ishelpful'] =='True'
        questionnaire.interrupts_work =  form.cleaned_data['interrupts_work'] == 'True'
        questionnaire.satisfaction_num_msg = form.cleaned_data['satisfaction_num_msg']
        
        questionnaire.save()
        if ptype=='case':
            #mail_admins('ESP:VAERS - Authenticated user changed case status',
            #        'Case %s.\nUser %s\n.' % (case, request.user))
            return HttpResponseRedirect(reverse('present_case', kwargs={'id':id, 'ptype':ptype}))
        else:
            #mail_admins('ESP:VAERS - Provider changed case status',
            #        'Case %s.\nProvider %s\n.' % (case, provider))
            return HttpResponse('Thank you for providing instruction and feedback for this case.  You may close the browser window')
            
    else:
        #mail_admins('ESP:VAERS - User viewed case report',
        #            'Case %s.\nProvider %s \n.' % (case, provider))
        
        return direct_to_template(request, PAGE_TEMPLATE_DIR + 'present.html', {
                'case':case,
                'questionnaire':questionnaire,
                'form':form,
                'content_type_enc': ContentType.objects.get_for_model(Encounter),
                'content_type_lx': ContentType.objects.get_for_model(LabResult),
                'content_type_rx': ContentType.objects.get_for_model(Prescription),
                'content_type_all': ContentType.objects.get_for_model(Allergy),
                'ptype': ptype,
                'formid': id
                })
        
@login_required
def download_vae_listing(request):
    if request.user.has_perm('vaers.view_phi'):
        filename=VAERS_LINELIST_PATH+"vaers_linelist_phi.csv"
        vfile=open(filename,'r')
    else:
        filename=VAERS_LINELIST_PATH+"vaers_linelist_nophi.csv"
        vfile=open(filename,'r')        
    response = HttpResponse(FileWrapper(vfile), content_type='application/csv')
    response['Content-Disposition'] = 'attachment; filename=vae_linelist.csv'
    return response
