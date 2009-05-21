#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site

from ESP.vaers.models import AdverseEvent, LabResultEvent, ProviderComment
from ESP.esp.models import Lx, Demog, Immunization
from ESP.vaers.utils import send_notifications
from ESP.vaers.forms import CaseConfirmForm

from ESP.utils.utils import log


import datetime

PAGE_TEMPLATE_DIR = 'pages/vaers/'
WIDGET_TEMPLATE_DIR = 'widgets/vaers/'

def index(request):
    # Check pagination
    RESULTS_PER_PAGE = 100
    page = int(request.GET.get('page', 1))

    # Set limits for query
    floor = max(page-1, 0)*RESULTS_PER_PAGE
    ceiling = floor+RESULTS_PER_PAGE

    # Complete query and present results
    cases = AdverseEvent.fakes()[floor:ceiling]
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'home.html',
                              {'cases':cases})

def detect(request):
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'detect.html')

def notify(request, id):

    case = AdverseEvent.by_id(id)
    log.info('case: %s' % case)
    if request.method == 'POST' and case:
        try:
            assert case.is_fake()
            case.mail_notification()
            return HttpResponse('OK')
        except Exception, why:
            log.warn(why)
    else:
        return direct_to_template(request, PAGE_TEMPLATE_DIR + 'notify.html')

def report(request):
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'report.html')

                              


def verify(request, key):

    case = AdverseEvent.by_digest(key)
    if not case: raise Http404

    if case.category == 'auto': 
        return HttpResponseForbidden('This case will be automatically reported')
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


    else:
        confirmed_id = request.POST.get('provider_confirmation', 0) and provider.id
        response = HttpResponseRedirect(reverse('present_case', kwargs={'id':case.id}))
        response.set_cookie('confirmed_id', confirmed_id)
        return response
        
            
        


def case_details(request, id):
    
    case = AdverseEvent.by_id(id)
    if not case: raise Http404



    if case.category == 'auto': 
        return HttpResponseForbidden('This case will be automatically reported')
    
    try:
        provider = case.provider()
    except:
        import pdb
        pdb.set_trace()
    if not provider: return HttpResponseForbidden('Not for your eyes')
    
    authorized_id = request.COOKIES.get('confirmed_id', None)
    
    if not (authorized_id and int(authorized_id)==provider.id):
        return HttpResponseForbidden('You have not confirmed you are the care '\
                                         'provider for this patient. Please go '\
                                         'back to the confirmation step.')


    form = CaseConfirmForm(request.POST) if request.method == 'POST' else CaseConfirmForm()

    
    if request.method == 'POST' and form.is_valid():
        next_status = {
            'confirm':'Q',
            'false_positive':'FP',
            'wait':'UR'
            }
        
        action = form.cleaned_data['action']
        comment_text = form.cleaned_data['comment']
        
            
        case.status = next_status[action]
        case.save()
        comment = ProviderComment(author=provider, event=case,
                                  text=comment_text)
        comment.save()

        return HttpResponseRedirect(reverse('present_case', kwargs={'id':case.id}))
            
    else:
        comments = ProviderComment.objects.filter(author=provider,
                                                  event=case).order_by('-created_on')

        return direct_to_template(request, PAGE_TEMPLATE_DIR + 'present.html', {
                'case':case,
                'comments':comments,
                'form':form
                })






