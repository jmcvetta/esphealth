#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site

from models import AdverseEvent, LabResultEvent
from esp.models import Lx

import datetime

PAGE_TEMPLATE_DIR = 'pages/vaers/'
WIDGET_TEMPLATE_DIR = 'widgets/vaers/'

def index(request):
    return HttpResponse('Welcome Home')



def present(request, case_id):

    case = AdverseEvent.manager.by_id(int(case_id))
    if not case: return HttpResponseNotFound('Case not found')
    if case.category == 'auto': return HttpResponseForbidden('Not for your eyes')

    parse_date = datetime.datetime.strptime # Just a shorter name. 
    case.immunization.date = parse_date(case.immunization.ImmDate, '%Y%m%d')
    encounter_date = getattr(case, 'encounter', None) and parse_date(
        case.encounter.EncEncounter_Date, '%Y%m%d')
    lab_result_date = getattr(case, 'lab_result', None) and parse_date(
                case.lab_result.LxDate_of_result, '%Y%m%d')

    confirm_url = reverse('case_action', 
                          kwargs={'case_id':case_id, 'action':'confirm'})
    discard_url = reverse('case_action', 
                          kwargs={'case_id':case_id, 'action':'discard'})

    
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'present.html', {
            'case':case,
            'encounter_date': encounter_date,
            'lab_result_date': lab_result_date,
            'confirm_url':confirm_url,
            'discard_url':discard_url
            })

def action(request, case_id, action):
    collect_info_actions = {
        'confirm':{
            'headline':'Case Report Notes',
            'instructions':'Please include information that you would like to add to the case report',
            'url':reverse('case_action', kwargs={'case_id':case_id, 
                                                 'action':'comment'})
            },
        'discard':{
            'headline':'Report Detection Error',
            'instructions':'Please explain why do you think our detection system is wrong',
            'url':reverse('case_action', kwargs={'case_id':case_id, 
                                                 'action':'feedback'})
            }
        }

    if action in collect_info_actions: 
        a = collect_info_actions[action]
        return direct_to_template(
            request,  WIDGET_TEMPLATE_DIR + 'feedback_form.html', {
                'headline': a['headline'],
                'instructions':a['instructions'],
                'action_url':a['url']
                })

    else:
        return HttpResponse('Not Implemented Yet')



