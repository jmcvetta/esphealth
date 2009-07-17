'''
                              ESP Health Project
Notifiable Diseases Framework
                                     Views

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


import re
import sys

from django import forms as django_forms
from django import http
from django.core import serializers
from django.core import urlresolvers
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import formset_factory
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import create_update
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from ESP.settings import NLP_SEARCH
from ESP.settings import NLP_EXCLUDE
from ESP.settings import ROWS_PER_PAGE
from ESP.settings import DATE_FORMAT
from ESP.conf.models import NativeCode
from ESP.conf.models import NativeNameCache
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.hef.core import BaseHeuristic
from ESP.hef import events # Required to register hef events
from ESP.nodis.models import Case
from ESP.nodis.models import STATUS_CHOICES
from ESP.utils.utils import log
from ESP.utils.utils import Flexigrid



#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



@login_required
def case_list(request, status):
    values = {}
    values['default_rp'] = ROWS_PER_PAGE
    values['request'] = request # Should this really be necessary?
    values['status'] = status
    return render_to_response('nodis/case_list.html', values, context_instance=RequestContext(request))


@login_required
def json_case_grid(request, status):
    view_phi = request.user.has_perm('view_phi') # Does user have permission to view PHI?
    flexi = Flexigrid(request)
    cases = Case.objects.all()
    #
    # Limit Cases by Status
    #
    if status == 'await':
        cases = cases.filter(status='AR')
    elif status == 'under':
        cases = cases.filter(status='UR')
    elif status == 'queued':
        cases = cases.filter(status='Q')
    elif status == 'sent':
        cases = cases.filter(status='S')
    #
    # Search Cases
    #
    # I would like also to be able to search by site, but we cannot do so in 
    # a tolerably efficient manner without changes to the data model.
    if flexi.query and flexi.qtype == 'condition':
        cases = cases.filter(condition__icontains=flexi.query)
    # Search on PHI -- limited to users w/ correct permissions
    elif view_phi and flexi.query and flexi.qtype == 'name':
        cases = cases.filter(patient__last_name__icontains=flexi.query)
    elif view_phi and flexi.query and flexi.qtype == 'mrn':
        # Is it sensible that MRN search is exact rather than contains?
        cases = cases.filter(patient__mrn__iexact=flexi.query)
    #
    # Sort Cases
    #
    # Maybe some/all of this sorting logic should be in the Case model?
    if flexi.sortname == 'workflow':
        cases = cases.order_by('workflow_state')
    elif flexi.sortname == 'last_updated':
        cases = cases.order_by('updated_timestamp')
    elif flexi.sortname == 'date_ordered':
        cases = cases.order_by('date')
    elif flexi.sortname == 'condition':
        cases = cases.order_by('condition')
#    elif flexi.sortname == 'site':
#        list = [(c.latest_lx_provider_site(), c) for c in cases]
#        list.sort()
#        cases = [item[1] for item in list]
    # Sort on PHI -- limited to users w/ correct permissions
    elif view_phi and flexi.sortname == 'name':
        cases = cases.order_by('patient__last_name', 'patient__first_name')
    elif view_phi and flexi.sortname == 'mrn':
        cases = cases.order_by('patient__mrn')
    elif view_phi and flexi.sortname == 'address':
        list = [(c.address, c) for c in cases]
        list.sort()
        cases = [item[1] for item in list]
    else: # sortname == 'id'
         cases = cases.order_by('pk')
    if flexi.sortorder == 'desc':
        # It should not be necessary to convert QuerySet to List in order to
        # do reverse(), but there appears to be a bug in Django requiring this
        # work-around.
        # TODO: submit bug report
        cases = [c for c in cases]
        cases.reverse()
    #
    # Generate JSON
    #
    p = Paginator(cases, flexi.rp)
    cases = p.page(flexi.page).object_list
    rows = []
    for case in cases:
        row = {}
        case_date = case.date.strftime(DATE_FORMAT)
        row['id'] = case.id
        href = urlresolvers.reverse('nodis_case_detail', kwargs={'case_id': int(case.id)})
        case_id_link = '%s <a href="' % case.pk  + href + '">(view)</a>'
        if view_phi:
            patient = case.patient
            row['cell'] =  [
                case_id_link,
                case.condition,
                case_date,
                case.provider.dept,
                # Begin PHI
                patient.name.title(),
                patient.mrn,
                patient.address.title(),
                # End PHI
                case.get_status_display(),
                case.updated_timestamp.strftime(DATE_FORMAT),
                #case.getPrevcases()
                'n/a',
                ]
        else:
            row['cell'] =  [
                case_id_link,
                case.condition,
                case_date,
                case.provider.dept,
                case.get_status_display(),
                last_update,
                #case.getPrevcases()
                'n/a',
                ]
        rows += [row]
    json = flexi.json(rows, use_paginator=False, page_count=p.count)
    #return HttpResponse(json, mimetype='application/json')
    return HttpResponse(json)


@login_required
def case_detail(request, case_id):
    '''
    Detailed case view with workflow history
    '''
    case = get_object_or_404(Case, pk=case_id)
    #wf = case.caseworkflow_set.all().order_by('-workflowDate')
    wf = []
    patient = case.patient
    pid = patient.pk
    age = patient.age.days / 365 # Note that 365 is Int not Float, thus so is result
    if age >= 90:
        age = '90+'
    dob = patient.date_of_birth.strftime(DATE_FORMAT)
    created = case.created_timestamp.strftime(DATE_FORMAT)
    updated = case.updated_timestamp.strftime(DATE_FORMAT)
    #
    # Reportable Info
    #
    #
    # Non-Reportable Info
    #
    other_enc = set(Encounter.objects.filter(patient=patient)) - set(case.encounters.all())
    other_lab = set(LabResult.objects.filter(patient=patient)) - set(case.lab_results.all())
    other_rx = set(Prescription.objects.filter(patient=patient)) - set(case.medications.all())
    values = {
        "request":request,
        "case": case,
        'pid': pid,
        'condition': case.condition,
        'age': age,
        'dob': dob,
        "wf": wf,
        "wfstate": 'n/a', # FIXME: Implement this!
        'created': created,
        'updated': updated,
        'all_encs': other_enc,
        'all_lxs': other_lab,
        'all_rxs': other_rx,
        'rep_encs': case.encounters.all(),
        'rep_lxs': case.lab_results.all(),
        'rep_rxs': case.medications.all(),
        'inprod': '1', # Ugh
        }
    return render_to_response('nodis/case_detail.html', values, context_instance=RequestContext(request))

@login_required
def provider_detail(request, provider_id):
    values = {'provider': Provider.objects.get(pk=provider_id) }
    return render_to_response('nodis/provider_detail.html', values, context_instance=RequestContext(request))

@login_required
def show_ext_loinc_maps(request):
    '''
    Administrative screen to add/delete/update NativeCode objects
    '''
    values = {}
    values['request'] = request # Needed for espbase.html
    values['default_rp'] = ROWS_PER_PAGE
    return render_to_response('nodis/show_ext_loinc_maps.html', values, context_instance=RequestContext(request))


@login_required
def json_ext_loinc_grid(request):
    '''
    '''
    flexi = Flexigrid(request)
    if flexi.sortorder == 'asc':
        sortname = flexi.sortname
    else:
        sortname = '-%s' % flexi.sortname
    maps = models.NativeCode.objects.select_related().all().order_by(sortname)
    if flexi.query:
        query_str = 'Q(%s__icontains="%s")' % (flexi.qtype, flexi.query)
        q_obj = eval(query_str)
        maps = maps.filter(q_obj)
    rows = []
    for m in maps:
        row = {}
        row['id'] = m.id
        row['cell'] = [
            m.id,
            m.native_code,
            m.native_name,
            m.loinc.loinc_num,
            m.loinc.name,
            ]
        rows += [row]
    json = flexi.json(rows)
    #return HttpResponse(json, mimetype='application/json')
    return HttpResponse(json)


@login_required
def edit_ext_loinc_map(request, map_id=None, action=None):
    '''
    '''
    values = {}
    values['request'] = request # FIXME: Ugh, we really need to clean up espbase.html
    log.debug('map_id: %s' % map_id)
    log.debug('action: %s' % action)
    if action == 'delete':
        map_obj = get_object_or_404(models.NativeCode, pk=map_id)
        map_obj.delete()
        return redirect_to(request, urlresolvers.reverse('show_ext_loinc_maps'))
    elif action == 'new':
        values['loinc_name'] = '[Enter a LOINC code...]'
        map_obj = models.NativeCode()
        form = forms.ExtLoincForm()
    else: # Edit
        map_obj = get_object_or_404(models.NativeCode, pk=map_id)
        data = {
            'native_code': map_obj .native_code,
            'native_name': map_obj.native_name,
            'loinc_num': map_obj.loinc.loinc_num,
            'notes': map_obj.notes,
            }
        values['loinc_name'] = map_obj.loinc.name
        form = forms.ExtLoincForm(data)
    if request.method == 'POST':
        form = forms.ExtLoincForm(request.POST)
        if form.is_valid():
            loinc = models.Loinc.objects.get(pk=form.cleaned_data['loinc_num'])
            map_obj.loinc = loinc
            map_obj.native_code = form.cleaned_data['native_code']
            map_obj.native_name = form.cleaned_data['native_name']
            map_obj.notes = form.cleaned_data['notes']
            map_obj.save()
            return redirect_to(request, urlresolvers.reverse('show_ext_loinc_maps'))
    values['form'] = form
    return render_to_response('esp/edit_ext_loinc_map.html', values, context_instance=RequestContext(request))
    

@login_required
def loinc_name_lookup(request):
    loinc_num = request.REQUEST['loinc_num']
    log.debug('loinc_num: %s' % loinc_num)
    loinc = get_object_or_404(models.Loinc, pk=loinc_num)
    return HttpResponse(loinc.name, mimetype='text/plain')
