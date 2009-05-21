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
from ESP.conf.models import NativeToLoincMap
from ESP.emr.models import LabResult
from ESP.utils.utils import Flexigrid


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@login_required
def code_maintenance(request):
    values = {'title': 'Code Maintenance'}
    search_re = re.compile(r'|'.join(NLP_SEARCH))
    exclude_re = re.compile(r'|'.join(NLP_EXCLUDE))
    mapped_codes = NativeToLoincMap.objects.values_list('native_code', flat=True)
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
#    maps = models.NativeToLoincMap.objects.select_related().all().order_by(sortname)
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
            loinc = NativeToLoincMap.objects.get(native_code=native_code).loinc
            loinc_num = loinc.loinc_num
            loinc_name = loinc.name
        except NativeToLoincMap.DoesNotExist:
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

