'''
                              ESP Health Project
Configuration Module
Views

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


import re
import sys
import pprint
import operator

from django import forms as django_forms, http
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core import serializers
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import formset_factory, modelformset_factory
from django.forms.util import ErrorList
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic import create_update, list_detail
from django.views.generic.simple import redirect_to
from django.template.defaultfilters import slugify
from django.http import HttpResponse, HttpResponseRedirect

from ESP.settings import ROWS_PER_PAGE
from ESP.conf.models import IgnoredCode
from ESP.conf.models import LabTestMap
from ESP.nodis.base import DiseaseDefinition
from ESP.emr.models import LabResult
from ESP.utils.utils import log
from ESP.utils.utils import Flexigrid
from ESP.hef.base import BaseLabResultHeuristic, BaseEventHeuristic, PrescriptionHeuristic, DiagnosisHeuristic


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@login_required
def heuristic_mapping_report(request):
    values = {'title': 'Abstract Lab Mapping Summary'}
    mapped = []
    unmapped = []
    
    for heuristic in BaseLabResultHeuristic.get_all(): 
        maps = LabTestMap.objects.filter(test_name=heuristic.test_name)
        if not maps:
            # if unmapped doesnt already have test name then add it
            if not unmapped.__contains__(heuristic.test_name):
                unmapped.append( (heuristic.test_name) )
            continue
        codes = maps.values_list('native_code', flat=True)
        # if mapped doesnt already contain (heuristic.test_name, codes) then add it
        # it is sorted already,for each in mapped get item compare with test name 
        # add first one
        if not mapped: mapped.append( (heuristic.test_name, codes) )
        # loop through mapped make sure is not already there
        else:
            contains=False
            for index in range(len(mapped)):  
                if mapped.__getitem__(index).__contains__((heuristic.test_name)):
                    contains=True
                    continue
            if not contains: 
                mapped.append( (heuristic.test_name, codes) )              
        
    mapped.sort(key=operator.itemgetter(0))
    unmapped.sort()
    values['mapped'] = mapped
    values['unmapped'] = unmapped
    return render_to_response('conf/heuristic_mapping_report.html', values, context_instance=RequestContext(request))

@login_required
def heuristic_reportables(request):
    values = {'title': 'Heuristic Reportables Summary'}
    
    reportable_rx = []
    reportable_dx = []
    reportable_lx = []
    
    for heuristic in BaseLabResultHeuristic.get_all():
        if heuristic.test_name not in reportable_lx:
            reportable_lx.append(heuristic.test_name)
    
    for heuristic in DiagnosisHeuristic.get_all():
        if isinstance(heuristic, DiagnosisHeuristic):
            for dx_code in heuristic.dx_code_queries:
                if dx_code not in reportable_dx:
                    reportable_dx.append(dx_code)
            
    for heuristic in PrescriptionHeuristic.get_all():
        if isinstance(heuristic, PrescriptionHeuristic):
            for drug in heuristic.drugs:
                if drug not in reportable_rx:
                    reportable_rx.append(drug)
    
    reportable_lx.sort()
    reportable_dx.sort()
    reportable_rx.sort()
    
    values['reportable_lx'] = reportable_lx
    values['reportable_dx'] = reportable_dx
    values['reportable_rx'] = reportable_rx
    
    return render_to_response('conf/heuristic_reportables.html', values, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_staff)
def ignore_code(request, native_code):
    '''
    Display Unmapped Labs report generated from cache
    '''
    if request.method == 'POST':
        #ic_obj, created = IgnoredCode.objects.get_or_create(native_code=native_code.lower())
        ic_obj, created = IgnoredCode.objects.get_or_create(native_code=native_code) # Why was this lower() before?
        if created:
            ic_obj.save()
            msg = 'Native code "%s" has been added to the ignore list' % native_code
        else:
            msg = 'Native code "%s" is already on the ignore list' % native_code
        messages.add_message(request,messages.INFO,msg)
        log.debug(msg)
        return redirect_to(request, reverse('unmapped_labs_report'))
    else:
        values = {
            'title': 'Unmapped Lab Tests Report',
            "request":request,
            'native_code': native_code,
            }
        return render_to_response('conf/confirm_ignore_code.html', values, context_instance=RequestContext(request))
    
