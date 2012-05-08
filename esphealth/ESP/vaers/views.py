#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseNotAllowed, Http404
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.mail import mail_admins
from django.shortcuts import render_to_response

from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site
from django.core.servers.basehttp import FileWrapper


from ESP.vaers.models import AdverseEvent, Case,Questionaire, ADVERSE_EVENT_CATEGORY_ACTION
from ESP.vaers.forms import CaseConfirmForm
from ESP.utils.utils import log, Flexigrid
from ESP.emr.models import Immunization, Encounter, Prescription,LabResult,Allergy
from ESP.settings import VAERS_LINELIST_PATH

import datetime

PAGE_TEMPLATE_DIR = 'pages/vaers/'
WIDGET_TEMPLATE_DIR = 'widgets/vaers/'

def index(request):
     # Complete query and present results
    cases = AdverseEvent.paginated()
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'home.html',
                              {'cases':cases,
                               'page':1
                               })

def list_cases(request):
    # This is a ajax call. Our response contains only the result page.

    # Page may be passed in the query string and must be a positive number
    
    grid = Flexigrid(request)
    page = grid.page
    

    # Complete query and present results
    cases = AdverseEvent.paginated(page=int(page))
    total = AdverseEvent.objects.all().count()
    return direct_to_template(request, WIDGET_TEMPLATE_DIR +'case_grid.json',
                              {'cases':cases,
                               'total':total,
                               'page':page},
                              mimetype='application/json'
                              )


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

def report(request):
    cases = AdverseEvent.objects.all()
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'report.html',
                              {'cases':cases})                             

def verify(request, key):
    # TODO change to use two parameters: pkid of Q, key is digest from Q
    # initial version dont verify digest , TODO verify later
    # TODO digest should be associated with the questionaire
    # and get the provider from the Q.
    # sends to case details with the id of Q
    
    case = AdverseEvent.by_digest(key)
    if not case: raise Http404
    # TODO get the events from case in Q and get highest category?
    if case.category == '1_common': 
        return HttpResponseForbidden('This case will be automatically reported')
    # TODO get it from the Q
    provider = case.provider()
    if not provider: return HttpResponseForbidden('Not for your eyes')

    if request.method == 'GET':
        authorized_id = int(request.COOKIES.get('confirmed_id', 0))
        if authorized_id and authorized_id == provider.id:
            # No need to see confirm again. Will redirect
            return HttpResponseRedirect(reverse('present_case', kwargs={'id':case.id}))
        else:
            return direct_to_template(request, PAGE_TEMPLATE_DIR + 'identify.html', {
                    'case':case })

    else: # request.method == 'POST'
        confirmed_id = request.POST.get('provider_confirmation', 0) and provider.id
        response = HttpResponseRedirect(reverse('present_case', kwargs={'id':case.id}))
        response.set_cookie('confirmed_id', confirmed_id)
        mail_admins('ESP:VAERS - User confirmed identity on verification page',
                    'User confirmed to be provider %s' % (provider.full_name))
        return response
    
# @param id : is the primary key of the questionaire        
def case_details(request, id):
    category = None
    
    questionaire = Questionaire.objects.get(id =id)
    
    case = questionaire.case
    
    if not case: raise Http404
    
    #finding the highest category in the event, 
    if  case.adverse_event.filter(category__startswith ='2'):#2_rare
        category  = ADVERSE_EVENT_CATEGORY_ACTION[1][0]
    elif  case.adverse_event.filter(category__startswith ='3'):#3_possible
        category  =  ADVERSE_EVENT_CATEGORY_ACTION[2][0] 
    elif  case.adverse_event.filter(category__startswith ='1'):#3_possible
        category  =  ADVERSE_EVENT_CATEGORY_ACTION[0][0]  
    
    if category == ADVERSE_EVENT_CATEGORY_ACTION[0][0] : 
        return HttpResponseForbidden(ADVERSE_EVENT_CATEGORY_ACTION[0][1])
    
    provider = questionaire.provider
    if not provider: return HttpResponseForbidden('No provider in questionaire')
    
    #authorized_id = request.COOKIES.get('confirmed_id', None)
    # TODO fix this as part of fixing verify 
    #if not (authorized_id and int(authorized_id)==provider.id):
        #return HttpResponseForbidden('You have not confirmed you are the care '\
                                        # 'provider for this patient. Please go '\
                                         #'back to the confirmation step.')

    if request.method == 'POST':
        form = CaseConfirmForm(request.POST) 
    else:
        form = CaseConfirmForm()

    if request.method == 'POST' and form.is_valid():
        next_status = {
            'confirm':'Q',
            'false_positive':'FP',
            'wait':'UR'
            }
        
        # this is where we get stuff from the form
        # initializing flags
        questionaire.state = next_status[form.cleaned_data['state']]
        questionaire.comment = form.cleaned_data['comment']
        questionaire.message_ishelpful=  form.cleaned_data['message_ishelpful'] =='True'
        questionaire.interrupts_work =  form.cleaned_data['interrupts_work'] == 'True'
        questionaire.satisfaction_num_msg = form.cleaned_data['satisfaction_num_msg']
        
        questionaire.save()
        mail_admins('ESP:VAERS - Provider changed case status',
                    'Case %s.\nProvider %s\n.' % (case, provider))

        return HttpResponseRedirect(reverse('present_case', kwargs={'id':id}))
            
    else:
       
        mail_admins('ESP:VAERS - User viewed case report',
                    'Case %s.\nProvider %s \n.' % (case, provider))
        
        
        return direct_to_template(request, PAGE_TEMPLATE_DIR + 'present.html', {
                'case':case,
                'questionaire':questionaire,
                'form':form,
                'content_type_enc': ContentType.objects.get_for_model(Encounter),
                'content_type_lx': ContentType.objects.get_for_model(LabResult),
                'content_type_rx': ContentType.objects.get_for_model(Prescription),
                'content_type_all': ContentType.objects.get_for_model(Allergy),
                })
        
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
