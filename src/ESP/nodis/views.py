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
import datetime

from django import forms as django_forms
from django import http
from django.core import serializers
from django.core import urlresolvers
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models import Count
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
from ESP.conf.models import CodeMap
from ESP.conf.models import IgnoredCode
from ESP.static.models import Loinc
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import LabTestConcordance
from ESP.hef.core import BaseHeuristic
from ESP.hef import events # Required to register hef events
from ESP.nodis.core import Condition
from ESP.nodis.models import Case
from ESP.nodis.models import CaseStatusHistory
from ESP.nodis.models import ReferenceCaseList
from ESP.nodis.models import ReferenceCase
from ESP.nodis.models import ValidatorRun
from ESP.nodis.models import ValidatorResult
from ESP.nodis.forms import CaseStatusForm
from ESP.nodis.forms import CodeMapForm
from ESP.nodis.forms import ConditionForm
from ESP.nodis.forms import ReferenceCaseForm
from ESP.nodis.validator import RELATED_MARGIN
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
                case.updated_timestamp.strftime(DATE_FORMAT),
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
    history = case.casestatushistory_set.all().order_by('-timestamp')
    patient = case.patient
    pid = patient.pk
    # patient.age is derived directly from patient.date_of_birth.  When the 
    # latter is None, the former will also be None
    try:
        dob = patient.date_of_birth.strftime(DATE_FORMAT)
        age = patient.age.days / 365 # Note that 365 is Int not Float, thus so is result
    except AttributeError: 
        age = None
        dob = None
    if age >= 90:
        age = '90+'
    created = case.created_timestamp.strftime(DATE_FORMAT)
    updated = case.updated_timestamp.strftime(DATE_FORMAT)
    #
    # Reportable Info
    #
    #
    # Non-Reportable Info
    #
    #other_enc = set(Encounter.objects.filter(patient=patient)) - set(case.encounters.all())
    #other_lab = set(LabResult.objects.filter(patient=patient)) - set(case.lab_results.all())
    #other_rx = set(Prescription.objects.filter(patient=patient)) - set(case.medications.all())
    data = {'status': case.status}
    status_form = CaseStatusForm(initial=data)
    values = {
        'title': 'Detail Report: Case #%s' % case.pk,
        "request":request,
        "case": case,
        'pid': pid,
        'condition': case.condition,
        'age': age,
        'dob': dob,
        "history": history,
        'created': created,
        'updated': updated,
        'status_form': status_form,
        }
    return render_to_response('nodis/case_detail.html', values, context_instance=RequestContext(request))

def case_status_update(request, case_id):
    '''
    Update the case status and comments.  This method should only ever be 
    called from a form POST.
    '''
    if not request.method == 'POST':
        msg = 'case_status_update() can only be called from a form POST'
        request.user.message_set.create(message=msg)
        return redirect_to(request, reverse('nodis_case_detail', args=[case_id]))
    form = CaseStatusForm(request.POST)
    if not form.is_valid():
        msg = 'Invalid form -- no action taken'
        request.user.message_set.create(message=msg)
        return redirect_to(request, reverse('nodis_case_detail', args=[case_id]))
    case = get_object_or_404(Case, pk=case_id)
    new_status = form.cleaned_data['status']
    comment = form.cleaned_data['comment']
    if not comment: # I'd rather save a Null than a blank string in the DB
        comment = None 
        if new_status == case.status:
            msg = 'You must either change the change the case status, make a comment, or both.'
            request.user.message_set.create(message=msg)
            return redirect_to(request, reverse('nodis_case_detail', args=[case_id]))
    old_status = case.status
    case.status = new_status
    case.save()
    log.debug('Updated status of case #%s: %s' % (case.pk, case.status))
    hist = CaseStatusHistory(case=case, old_status=old_status, new_status=new_status, 
        changed_by=request.user.username, comment=comment)
    hist.save() # Add a history object
    log.debug('Added new CaseStatusHistory object #%s for Case #%s.' % (hist.pk, case.pk))
    msg = 'Case status updated.'
    request.user.message_set.create(message=msg)
    return redirect_to(request, reverse('nodis_case_detail', args=[case_id]))


def case_queue_for_transmit(request, case_id):
    '''
    Change status of specified case to 'Q' -- queued for transmit to Health Dept.
    '''
    if not request.method == 'POST':
        msg = 'case_queue_for_transmit() can only be called from a form POST'
        request.user.message_set.create(message=msg)
        return redirect_to(request, reverse('nodis_case_detail', args=[case_id]))
    case = get_object_or_404(Case, pk=case_id)
    old_status = case.status
    case.status = 'Q'
    case.save()
    log.debug('Updated status of case #%s: %s' % (case.pk, case.status))
    hist = CaseStatusHistory(case=case, old_status=old_status, new_status='Q', 
        changed_by=request.user.username, comment='Queued for transmit from case detail screen.')
    hist.save() # Add a history object
    log.debug('Added new CaseStatusHistory object #%s for Case #%s.' % (hist.pk, case.pk))
    msg = 'Case #%s has been queued for transmission to the Health Department' % case.pk
    request.user.message_set.create(message=msg)
    return redirect_to(request, reverse('nodis_cases_all'))


@login_required
def provider_detail(request, provider_id):
    values = {'provider': Provider.objects.get(pk=provider_id) }
    return render_to_response('nodis/provider_detail.html', values, context_instance=RequestContext(request))


@login_required
def updateWorkflow(request,object_id,newwf=''):
    acase = Case.objects.get(id__exact=object_id)
    if not newwf:
        newwf = request.POST['NewWorkflow']
        cmt = request.POST['Comment']
    else:
        cmt=''
   # if acase.caseworkflow <> newwf:
    wf = CaseWorkflow(workflowDate=datetime.datetime.now(),
                         workflowState=newwf,
                         workflowChangedBy=request.user.username,
                         workflowComment = cmt)
    acase.caseworkflow_set.add(wf)
    acase.caseworkflow = newwf
    acase.caseLastUpDate = datetime.datetime.now()
    acase.save()
    ###########Go to a confirm page
    msg='The workflow state of this case has been successfully changed to "%s"!' % dict(choices.WORKFLOW_STATES)[newwf]
    arcase = Case.objects.filter(caseworkflow='AR')
    if arcase:
        nextcaseid=arcase[0].id
    else:
        nextcaseid=''
    cinfo = {
        "request":request,
        'wfmsg': msg,
        'inprod': 1,
        'nextcaseid':nextcaseid
        }
    con = Context(cinfo)
    return render_to_response('esp/case_detail.html',con)
            

@login_required
def wfdetail(request, object_id):
    """detailed workflow view
    """
    wf = get_object_or_404(CaseWorkflow, pk=object_id)
    caseid = wf.workflowCaseID.id
    cinfo = {"request":request,
             "object":wf,
             "caseid":caseid
    }
    c = Context(cinfo)
    return render_to_response('esp/workflow_detail.html',c)


@login_required
def updateWorkflowComment(request,object_id):
    """update caseworkflow comment only
    workflowComment = meta.TextField('Comments',blank=True)
     """
    wf = CaseWorkflow.objects.get(id__exact=object_id)
    caseid = wf.workflowCaseID.id
    if request.POST['NewComment'].strip() > ' ':
        nowd = datetime.datetime.now()
        saveme = wf.workflowComment
        newme = request.POST['NewComment']
        wf.workflowDate=nowd
        wf.workflowComment = '%s\nAdded at %s: %s' % (saveme, nowd.isoformat(), newme)
        wf.save()
    else:
        log.debug('No change in workflow comment - not saved')
        
    return HttpResponseRedirect("cases/%s/F/" % caseid)


@login_required
def unmapped_labs_report(request):
    '''
    Display Unmapped Labs report generated from cache
    '''
    ignored = IgnoredCode.objects.values('native_code')
    mapped = CodeMap.objects.values('native_code').distinct()
    all_strings = Condition.all_test_name_search_strings()
    q_obj = Q(native_name__icontains=all_strings[0])
    for string in all_strings[1:]:
        q_obj |= Q(native_name__icontains=string)
    q_obj &= Q(native_code__isnull=False)
    q_obj &= ~Q(native_code__in=ignored)
    q_obj &= ~Q(native_code__in=mapped)
    unmapped = LabTestConcordance.objects.filter(q_obj).order_by('native_name', 'native_code')
    strings = Condition.all_test_name_search_strings()
    strings.sort()
    values = {
        'title': 'Unmapped Lab Tests Report',
        "request":request,
        'unmapped': unmapped,
        'search_strings': strings,
        }
    return render_to_response('nodis/unmapped_labs.html', values, context_instance=RequestContext(request))
    

@user_passes_test(lambda u: u.is_staff)
def map_native_code(request, native_code):
    '''
    Convenience screen to help users map native lab test codes to LOINC codes 
    used by Nodis.  This view is part of nodis because it depends on several
    lower-level modules (conf, hef, & static).
    '''
    #native_code = native_code.lower()
    native_code = native_code # Why was this .lower() before??
    form = CodeMapForm() # This may be overridden below
    labs = LabResult.objects.filter(native_code=native_code)
    native_names = labs.values_list('native_name', flat=True).distinct().order_by('native_name')
    if request.method == 'POST':
        form = CodeMapForm(request.POST)
        if form.is_valid():
            heuristic_name = form.cleaned_data['heuristic']
            assert BaseHeuristic.get_heuristic(heuristic_name)
            threshold = form.cleaned_data['threshold']
            cm, created = CodeMap.objects.get_or_create(native_code=native_code, heuristic=heuristic_name)
            cm.notes = form.cleaned_data['notes']
            cm.native_name = native_names[0]
            cm.threshold = threshold
            cm.output_code = form.cleaned_data['output_code']
            cm.save()
            if created:
                msg = 'Saved code map: %s' % cm
            else:
                msg = 'Updated code map: %s' % cm
            request.user.message_set.create(message=msg)
            log.debug(msg)
            return redirect_to(request, reverse('unmapped_labs_report'))
    result_strings = labs.values('result_string').distinct().annotate(count=Count('id')).order_by('-count')[:10]
    ref_high_values = labs.values('ref_high_string').distinct().annotate(count=Count('id')).order_by('-count')[:10]
    comments = labs.values('comment').distinct().annotate(count=Count('id')).order_by('-count')[:10]
    without_ref_high = labs.filter(result_float__isnull=False, ref_high_float__isnull=True).count()
    without_ref_high_percent = float(without_ref_high) / float(labs.count()) * 100
    values = {
        'title': 'Map Native Code to Heuristic',
        "request":request,
        'native_code': native_code,
        'native_names': native_names,
        'result_strings': result_strings,
        'ref_high_values': ref_high_values,
        'without_ref_high': without_ref_high,
        'without_ref_high_percent': without_ref_high_percent,
        'comments': comments,
        'form': form,
        'count': labs.count()
        }
    return render_to_response('nodis/map_native_code.html', values, context_instance=RequestContext(request))
    

@login_required
def all_records(request, patient_pk):
    '''
    Display all medical records on file for specified patient.
    '''
    patient = get_object_or_404(Patient, pk=patient_pk)
    lab_results = LabResult.objects.filter(patient=patient).order_by('-date').select_related()
    encounters = Encounter.objects.filter(patient=patient).order_by('-date').select_related()
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date').select_related()
    immunizations = Immunization.objects.filter(patient=patient).order_by('-date').select_related()
    values = {
        'lab_results': lab_results,
        'prescriptions': prescriptions,
        'encounters': encounters,
        'immunizations': immunizations,
        }
    return render_to_response('nodis/all_records.html', values, context_instance=RequestContext(request))


@login_required
def validator_summary(request, validator_run_id=None):
    if validator_run_id:
        validator_run = get_object_or_404(ValidatorRun, pk=validator_run_id)
    else:
        validator_run = ValidatorRun.objects.all().order_by('-pk')[0]
    results = validator_run.results
    ref_cases = ReferenceCase.objects.filter(list=validator_run.list, ignore=False)
    values = {
        'title': 'Case Validator: Summary',
        'run': validator_run,
        'ref_cases': ref_cases,
        'results': results.select_related(),
        #'percent_exact': float(exact.count()) / results.count(),
        #'percent_similar': float(similar.count()) / results.count(),
        #'percent_missing': float(missing.count()) / results.count(),
        #'percent_new': float(new.count()) / results.count(),
        #'no_mrn': no_mrn,
        #'count_no_mrn': count_no_mrn,
        #'percent_no_mrn': percent_no_mrn,
        'total': results.count(),
        'related_margin': RELATED_MARGIN,
        }
    return render_to_response('nodis/validator_summary.html', values, context_instance=RequestContext(request))

@login_required
def validate_missing(request, validator_run_id=None):
    if validator_run_id:
        validator_run = get_object_or_404(ValidatorRun, pk=validator_run_id)
    else:
        validator_run = ValidatorRun.objects.all().order_by('-pk')[0]
    missing = validator_run.missing.order_by('ref_case__date')
    condition_form = ConditionForm()
    values = {
        'title': 'Case Validator: Missing Cases',
        'run': validator_run,
        }
    if request.method == 'POST':
        condition_form = ConditionForm(request.POST)
        if condition_form.is_valid():
            condition = condition_form.cleaned_data['condition']
            log.debug('Filtering on condition: %s' % condition)
            if not condition == '*': # Filter not applied for wildcard
                missing = missing.filter(ref_case__condition=condition)
    values['missing'] = missing.select_related() # Is select_related() helpful here?
    values['counts'] = validator_run.missing.values('ref_case__condition').order_by('ref_case__condition').annotate(Count('pk'))
    values['condition_form'] = condition_form
    return render_to_response('nodis/validator_missing.html', values, context_instance=RequestContext(request))

    
@login_required
def validate_new(request, validator_run_id=None):
    if validator_run_id:
        validator_run = get_object_or_404(ValidatorRun, pk=validator_run_id)
    else:
        validator_run = ValidatorRun.objects.all().order_by('-pk')[0]
    cases = Case.objects.filter(validatorresult__run=validator_run)
    condition_form = ConditionForm()
    values = {
        'title': 'Case Validator: New Cases',
        'run': validator_run,
        }
    if request.method == 'POST':
        condition_form = ConditionForm(request.POST)
        if condition_form.is_valid():
            condition = condition_form.cleaned_data['condition']
            log.debug('Filtering on condition: %s' % condition)
            if not condition == '*': # Filter not applied for wildcard
                cases = cases.filter(ref_case__condition=condition)
    values['cases'] = cases.select_related() # Is select_related() helpful here?
    values['counts'] = cases.values('condition').order_by('condition').annotate(Count('pk'))
    values['condition_form'] = condition_form
    return render_to_response('nodis/validator_new.html', values, context_instance=RequestContext(request))
    

@login_required
def missing_case_detail(request, result_id):
    result = get_object_or_404(ValidatorResult, pk=result_id)
    initial = {'notes': result.ref_case.notes, 'ignore': result.ref_case.ignore}
    form = ReferenceCaseForm(initial=initial)
    values = {
        'title': 'Missing Case Detail',
        'result': result,
        }
    if request.method == 'POST':
        form = ReferenceCaseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ref_case = result.ref_case
            if not data['notes'] == ref_case.notes:
                request.user.message_set.create(message='Updated notes for reference case # %s' % ref_case.pk)
            if data['ignore']:
                request.user.message_set.create(message='Ignoring reference case # %s' % ref_case.pk)
            ref_case.notes = data['notes']
            ref_case.ignore = data['ignore']
            ref_case.save()
    values['form'] = form
    return render_to_response('nodis/missing_case_detail.html', values, context_instance=RequestContext(request))
    
    