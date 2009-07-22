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

from django import forms as django_forms, http
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
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
    
    
def foobar():
    necessary_loincs = set(BaseHeuristic.get_all_loincs())
    mapped_loincs = set(NativeCode.objects.values_list('loinc', flat=True))
    return necessary_loincs - mapped_loincs


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@login_required
def map_code(request, loinc_num=None, native_code=None):
    values = {'title': 'Code Mapping'}
    values['loinc_num'] = loinc_num
    values['native_code'] = native_code
    values['form'] 
    return render_to_response('conf/map_code.html', values, context_instance=RequestContext(request))


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
    values = {'title': 'Required LOINC Codes'}
    mapped_loinc_nums = set(NativeCode.objects.values_list('loinc', flat=True))
    mapped = []
    unmapped = []
    required_loincs = get_required_loincs()
    print required_loincs
    for loinc_num in required_loincs:
        native_codes = NativeCode.objects.filter(loinc=loinc_num).values_list('native_code', flat=True)
        if native_codes:
            #native_codes = [m.native_code for m in mappings]
            #print native_codes
            lm = LoincMap(loinc_num, required_loincs[loinc_num], native_codes=native_codes)
            mapped += [lm]
        else:
            unmapped += [LoincMap(loinc_num, required_loincs[loinc_num])]
    values['mapped'] = mapped
    values['unmapped'] = unmapped
    return render_to_response('conf/loinc_mapping.html', values, context_instance=RequestContext(request))


def foo():
    search_re = re.compile(r'|'.join(NLP_SEARCH))
    exclude_re = re.compile(r'|'.join(NLP_EXCLUDE))
    mapped_codes = NativeCode.objects.values_list('native_code', flat=True)
    q_obj = ~Q(native_code__in=mapped_codes)
    q_obj = q_obj & Q(native_code__isnull=False)
    #native_names = LabResult.objects.filter(q_obj).values_list('native_code', 'native_name').distinct('native_code')
    native_names = []
    for item in native_names:
        code, name = item
        if not name:
            continue # Skip null
        uname = name.upper()
        if exclude_re.match(uname):
            continue # Excluded
        if search_re.match(uname):
            print '%-20s %s' % (code, name)
    values['default_rp'] = ROWS_PER_PAGE
    return render_to_response('conf/code_maintenance.html', values, context_instance=RequestContext(request))


@login_required
def json_code_grid(request):
    '''
    '''
    flexi = Flexigrid(request)
    if flexi.sortorder == 'asc':
        sortname = flexi.sortname
    else:
        sortname = '-%s' % flexi.sortname
#    maps = models.NativeCode.objects.select_related().all().order_by(sortname)
#    if flexi.query:
#        query_str = 'Q(%s__icontains="%s")' % (flexi.qtype, flexi.query)
#        q_obj = eval(query_str)
#        maps = maps.filter(q_obj)
#    rows = []
#    for m in maps:
#        row = {}
#        row['id'] = m.id
#        row['cell'] = [
#            m.id,
#            m.native_code,
#            m.native_name,
#            m.loinc.loinc_num,
#            m.loinc.name,
#            ]
#        rows += [row]
    codes = LabResult.objects.all().values('native_code', 'native_name').distinct('native_code')
    rows = []
    for item in codes:
        native_code = item['native_code']
        native_name = item['native_name']
        ignore = '-' # TODO: finish me!!
        try:
            loinc = NativeCode.objects.get(native_code=native_code).loinc
            loinc_num = loinc.loinc_num
            loinc_name = loinc.name
        except NativeCode.DoesNotExist:
            loinc_num = None
            loinc_name = None
        row = {}
        row['id'] = native_code
        row['cell'] = [
            native_code,
            native_name,
            loinc_num,
            loinc_name,
            ignore,
            ]
        rows += [row]
    json = flexi.json(rows)
    #return HttpResponse(json, mimetype='application/json')
    return HttpResponse(json)

