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

from ESP.settings import NLP_SEARCH, NLP_EXCLUDE
from ESP.settings import ROWS_PER_PAGE
from ESP.conf.models import NativeCode
from ESP.conf.models import CodeMap
from ESP.conf.models import IgnoredCode
from ESP.emr.models import NativeNameCache
from ESP.emr.models import LabResult
from ESP.hef.core import BaseHeuristic
from ESP.hef import events # Required to register hef events
from ESP.utils.utils import log
from ESP.utils.utils import Flexigrid


def refresh_native_name_cache():
    '''
    Update the cache of lab result native_name and native_code values
    '''
    log.debug('Flushing old native_name cache')
    NativeNameCache.objects.all().delete()
    log.debug('Populating cache table with distinct native_name values')
    for item in LabResult.objects.values('native_name', 'native_code').distinct():
        NativeNameCache(**item).save()
    count = NativeNameCache.objects.all().count()
    log.debug('There are %s distinct native_name + native_code values in LabResult table' % count)


def get_required_loincs():
    '''
    Returns a dictionary mapping a required LOINC number to the heuristic 
    definition(s) that require it.
    '''
    required_loincs = {}
    for heuristic in BaseHeuristic.get_all_heuristics():
        try:
            for l in heuristic.loinc_nums:
                try:
                    required_loincs[l] += [heuristic.def_name]
                except KeyError:
                    required_loincs[l] = [heuristic.def_name]
        except AttributeError:
            pass # Skip heuristics w/ no LOINCs defined
    return required_loincs
    
    
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class LoincMap:
    '''
    Convenience data structure for loinc_mapping()
    '''
    def __init__(self, loinc_num, required_by, native_codes=None):
        self.loinc_num = loinc_num
        self.required_by = required_by
        self.native_codes = native_codes
        

@login_required
def loinc_mapping(request):
    '''
    LOINC Mapping Report
    '''
    values = {'title': 'LOINC Mapping Report'}
    mapped = []
    unmapped = []
    required_loincs = get_required_loincs()
    for loinc_num in required_loincs:
        mappings = NativeCode.objects.filter(loinc=loinc_num)
        if mappings:
            native_code_lab_count = []
            for code in mappings.values_list('native_code', flat=True):
                count = LabResult.objects.filter(native_code=code).count()
                native_code_lab_count.append( (code, count) )
            log.debug('native_code_lab_count: \n%s' % pprint.pformat(native_code_lab_count))
            lm = LoincMap(
                loinc_num=loinc_num, 
                required_by=required_loincs[loinc_num], 
                native_codes=native_code_lab_count,
                )
            mapped.append(lm)
        else:
            unmapped.append( LoincMap(loinc_num=loinc_num, required_by=required_loincs[loinc_num]) )
    values['mapped'] = mapped
    values['unmapped'] = unmapped
    return render_to_response('conf/loinc_mapping.html', values, context_instance=RequestContext(request))

@login_required
def code_mapping_report(request):
    values = {'title': 'Code Mapping Report'}
    mapped = []
    unmapped = []
    for heuristic in BaseHeuristic.lab_heuristics():
        maps = CodeMap.objects.filter(heuristic=heuristic.name)
        if not maps:
            unmapped.append(heuristic)
            continue
        codes = maps.values_list('native_code', flat=True)
        mapped.append( (heuristic, codes) )
    mapped.sort(key=operator.itemgetter(1))
    values['mapped'] = mapped
    values['unmapped'] = unmapped
    return render_to_response('conf/code_mapping_report.html', values, context_instance=RequestContext(request))



@user_passes_test(lambda u: u.is_staff)
def ignore_code(request, native_code):
    '''
    Display Unmapped Labs report generated from cache
    '''
    if request.method == 'POST':
        ic_obj, created = IgnoredCode.objects.get_or_create(native_code=native_code.lower())
        if created:
            ic_obj.save()
            msg = 'Native code "%s" has been added to the ignore list' % native_code
        else:
            msg = 'Native code "%s" is already on the ignore list' % native_code
        request.user.message_set.create(message=msg)
        log.debug(msg)
        return redirect_to(request, reverse('unmapped_labs_report'))
    else:
        values = {
            'title': 'Unmapped Lab Tests Report',
            "request":request,
            'native_code': native_code,
            }
        return render_to_response('conf/confirm_ignore_code.html', values, context_instance=RequestContext(request))
    