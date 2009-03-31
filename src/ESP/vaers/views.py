#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site

from models import AdverseEvent, LabResultEvent, ProviderComment
from esp.models import Lx, Demog, Immunization
from vaers.utils import send_notifications
from forms import CaseConfirmForm
import reports

import datetime

PAGE_TEMPLATE_DIR = 'pages/vaers/'
WIDGET_TEMPLATE_DIR = 'widgets/vaers/'

def index(request):
    send_notifications()
    return HttpResponse('ok')


def verify(request, key):

    case = AdverseEvent.manager.by_digest(key)
    if not case: return HttpResponseNotFound('Case not found')
    if case.category == 'auto': 
        return HttpResponseForbidden('This case will be automatically reported')

    provider = case.patient.DemogProvider
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

    response = HttpResponse()

    case = AdverseEvent.manager.by_id(id)
    if not case: return HttpResponseNotFound('Case not found')
    if case.category == 'auto': 
        return HttpResponseForbidden('This case will be automatically reported')

    provider = case.patient.DemogProvider
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
        parse_date = datetime.datetime.strptime # Just a shorter name. 
        case.immunization.date = parse_date(case.immunization.ImmDate, '%Y%m%d')
        encounter_date = getattr(case, 'encounter', None) and parse_date(
            case.encounter.EncEncounter_Date, '%Y%m%d')
        lab_result_date = getattr(case, 'lab_result', None) and parse_date(
            case.lab_result.LxDate_of_result, '%Y%m%d')

        comments = ProviderComment.objects.filter(author=provider,
                                                  event=case).order_by('-created_on')

        return direct_to_template(request, PAGE_TEMPLATE_DIR + 'present.html', {
                'case':case,
                'encounter_date': encounter_date,
                'lab_result_date': lab_result_date,
                'comments':comments,
                'form':form
                
                
                })






