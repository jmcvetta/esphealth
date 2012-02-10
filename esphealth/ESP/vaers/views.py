#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.mail import mail_admins
from django.shortcuts import render_to_response

from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site

from ESP.vaers.models import AdverseEvent, ProviderComment
from ESP.vaers.forms import CaseConfirmForm
from ESP.utils.utils import log, Flexigrid


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



def detect(request):
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'detect.html')

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

    case = AdverseEvent.by_digest(key)
    if not case: raise Http404

    if case.category == '1_common': 
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
        mail_admins('ESP:VAERS - User confirmed identity on verification page',
                    'User confirmed to be provider %s' % (provider.full_name))
        return response
        
            
        


def case_details(request, id):
    
    case = AdverseEvent.by_id(id)
    if not case: raise Http404



    if case.category == '1_common': 
        return HttpResponseForbidden('This case will be automatically reported')
    
    provider = case.provider()
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
        mail_admins('ESP:VAERS - Provider changed case status',
                    'Case %s.\nProvider %s\n.' % (case, provider))

        return HttpResponseRedirect(reverse('present_case', kwargs={'id':case.id}))
            
    else:
        comments = ProviderComment.objects.filter(
            author=provider, event=case).order_by('-created_on')
        mail_admins('ESP:VAERS - User viewed case report',
                    'Case %s.\nProvider %s \n.' % (case, provider))
            
        return direct_to_template(request, PAGE_TEMPLATE_DIR + 'present.html', {
                'case':case,
                'comments':comments,
                'form':form
                })






