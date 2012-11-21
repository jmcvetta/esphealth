'''
                               ESP Health Project
                             User Interface Module
                                     Views

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''


import datetime
import csv
import django_tables as tables


from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db import connection, transaction
from django.db.models import Q
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import redirect_to
from django.http import HttpResponse


from ESP.settings import ROWS_PER_PAGE
from ESP.settings import DATE_FORMAT
from ESP.settings import SITE_NAME
from ESP.settings import STATUS_REPORT_TYPE

from ESP.conf.models import LabTestMap 
from ESP.conf.models import IgnoredCode
from ESP.conf.models import STATUS_CHOICES
from ESP.emr.models import Provenance
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import LabTestConcordance
#from ESP.hef import events # Required to register hef events
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.models import Case
from ESP.nodis.models import CaseStatusHistory
from ESP.nodis.models import Report
from ESP.nodis.models import ReferenceCase
from ESP.nodis.models import ValidatorRun
from ESP.nodis.models import ValidatorResult
from ESP.vaers.heuristics import VaersLxHeuristic
from ESP.ui.forms import CaseStatusForm
from ESP.ui.forms import CodeMapForm
from ESP.ui.forms import ConditionForm
from ESP.ui.forms import ReferenceCaseForm
#from ESP.ui.management.commands.validate_cases import RELATED_MARGIN
from ESP.utils import log
from ESP.utils import log_query
from ESP.utils import TableSelectMultiple
from ESP.vaers.models import AdverseEvent



#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


################################################################################
#
#--- Status Report
#
################################################################################
RELATED_MARGIN = 400

def _populate_status_values():
    '''
    Utility method to populate values dict for use with status_page() view and
    manage.py status_report command.
    '''
    today_string = datetime.datetime.now().strftime(DATE_FORMAT)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    values1 = {}
    values2 = {}
    values = {
            'type': STATUS_REPORT_TYPE,
            'title': _('Status Report'),
            'today_string': today_string,
            'site_name': SITE_NAME,
            }
    if STATUS_REPORT_TYPE in ['NODIS','BOTH']:
        new_cases = Case.objects.filter(created_timestamp__gte=yesterday)
        reports = Report.objects.filter(timestamp__gte=yesterday, sent=True)
        values1 = {
            'new_cases': new_cases,
            'all_case_summary': Case.objects.values('condition').annotate(count=Count('pk')).order_by('condition'),
            'new_case_summary': new_cases.values('condition').annotate(count=Count('pk')).order_by('condition'),
            'data_status': Provenance.objects.filter(timestamp__gte=yesterday).values('status').annotate(count=Count('pk')),
            'provenances': Provenance.objects.filter(timestamp__gte=yesterday).order_by('-timestamp'),
            'unmapped_labs': _get_unmapped_labs().select_related(),
            'reports': reports.order_by('timestamp'),            
            }
    if STATUS_REPORT_TYPE=='VAERS' or STATUS_REPORT_TYPE=='BOTH':
        values2 = {
            'aecase_daycounts': _get_ae_case_counts('day'),
            'aecase_weekcounts': _get_ae_case_counts('week'),
            'aecase_monthcounts': _get_ae_case_counts('month'),
            'vx_daycounts': _get_vx_counts('day'),
            'vx_weekcounts': _get_vx_counts('week'),
            'vx_monthcounts': _get_vx_counts('month'),
            'oth_daycounts':  _get_oth_counts('day'), 
            'oth_weekcounts':  _get_oth_counts('week'), 
            'oth_monthcounts':  _get_oth_counts('month'), 
            'tot_daycounts':  _get_tot_counts('day'), 
            'tot_weekcounts':  _get_tot_counts('week'), 
            'tot_monthcounts':  _get_tot_counts('month'), 
            'msg_daycounts': _get_provider_sent_counts('day'),
            'msg_weekcounts': _get_provider_sent_counts('week'),
            'msg_monthcounts': _get_provider_sent_counts('month'),
                  }
    values.update(values1)
    values.update(values2)     
    return values

@login_required
def status_page(request):
    '''
    View returning a status report page.
    '''
    values = _populate_status_values()
    return render_to_response('ui/status.html', values, context_instance=RequestContext(request))



################################################################################
#
#--- Lab Test Lookup tool
#
################################################################################


class TestSearchForm(forms.Form):
    
    search_string = forms.CharField(max_length=255, required=True)


@login_required
def labtest_lookup(request):
    '''
    Lookup lab tests by native_name
    '''
    values = {
        'title': 'Lab Test Lookup',
        "request": request,
        }
    if request.method == 'POST':
        lookup_form = TestSearchForm(request.POST)
        if lookup_form.is_valid():
            lookup_string = lookup_form.cleaned_data['search_string']
            tests = LabTestConcordance.objects.filter(native_name__icontains=lookup_string).distinct('native_code').order_by('native_code')
            choices = [(i.native_code, i) for i in tests]
            class NativeCodeForm(forms.Form):
                tests = forms.MultipleChoiceField(choices=choices, label=None,
                    widget=TableSelectMultiple(item_attrs=('native_code', 'native_name'))
                    )
            result_form = NativeCodeForm()
    else:
        lookup_form = TestSearchForm()
        native_codes = None
        tests = None
        result_form = None
    values['lookup_form'] = lookup_form
    values['tests'] = tests
    values['result_form'] = result_form
    return render_to_response('ui/labtest_lookup.html', values, context_instance=RequestContext(request))


@login_required
def labtest_detail(request):
    '''
    Display detailed information about one or more lab test
    '''
    values = {
        'title': 'Lab Test Detail',
        "request": request,
        }
    native_codes = request.POST.getlist('tests')
    if not native_codes:
        msg = 'Request not understood: no test codes specified for detail query'
        request.user.message_set.create(message=msg)
        return redirect_to(request, reverse('labtest_lookup'))
    details = []
    for nc in native_codes:
        labs = LabResult.objects.filter(native_code=nc)
        #native_names = [i['native_name'] for i in labs.values('native_name').distinct().annotate(count=Count('id')).order_by('-count')[:10] ]
        #native_names = labs.values('native_name').distinct().annotate(count=Count('id')).order_by('-count')[:10] 
        #result_strings = [i['result_string'] for i in labs.filter(result_float__isnull=True).values('result_string').distinct().annotate(count=Count('id')).order_by('-count')[:10] ]
        #comments = labs.values('comment').distinct().annotate(count=Count('id')).order_by('-count')[:10]
        row = {
            'native_code': nc,
            'native_names': labs.values_list('native_name', flat=True).distinct().order_by('native_name'),
            'result_strings': labs.filter(result_float__isnull=True).values_list('result_string', flat=True).distinct().order_by('result_string'),
            'comments': labs.values_list('comment', flat=True).distinct().order_by('comment'),
            'ref_high_values': labs.values_list('ref_high_string', flat=True).distinct().order_by('ref_high_string'),
            'ref_low_values': labs.values_list('ref_low_string', flat=True).distinct().order_by('ref_low_string'),
            'min_result_float': labs.filter(result_float__isnull=False).aggregate(min=Min('result_float'))['min'],
            'max_result_float': labs.filter(result_float__isnull=False).aggregate(max=Max('result_float'))['max'],
            'count': labs.count(),
            }
        details.append(row)
    values['details'] = details
    return render_to_response('ui/labtest_detail.html', values, context_instance=RequestContext(request))

@login_required
def labtest_csv(request, native_code):
    '''
    Returns a linelist CSV file of lab results with patient info
    '''
    header = [
        'Native Test Name',
        'Native Test Code',
        'Patient Surname', 
        'Patient Given Name', 
        'MRN', 
        'Gender', 
        'Date of Birth',
        'Test Result',
        'Test Order Date',
        'Test Result Date',
        'Reference Low',
        'Reference High', 
        'Comment',
        ]
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=lab_results.%s.csv' % native_code
    writer = csv.writer(response)
    writer.writerow(header)
    for lab in LabResult.objects.filter(native_code=native_code).select_related():
        row = [
            lab.native_name,
            lab.native_code,
            lab.patient.last_name,
            lab.patient.first_name,
            lab.patient.mrn,
            lab.patient.gender,
            lab.patient.date_of_birth,
            lab.result_string,
            lab.date, # 'date' is order date
            lab.result_date,
            lab.ref_low_string,
            lab.ref_high_string,
            lab.comment,
            ]
        writer.writerow(row)
    return response



@login_required
def unmapped_labs_report(request):
    '''
    Display Unmapped Labs report generated from cache
    '''
    unmapped = _get_unmapped_labs()
    strings = DiseaseDefinition.get_all_test_name_search_strings()+ VaersLxHeuristic.test_name_search_strings
    strings.sort()
    values = {
        'title': 'Unmapped Lab Tests Report',
        "request":request,
        'unmapped': unmapped,
        'search_strings': strings,
        }
    return render_to_response('ui/unmapped_labs.html', values, context_instance=RequestContext(request))
    

@user_passes_test(lambda u: u.is_staff)
def map_native_code(request, native_code):
    '''
    Convenience screen to help users map native lab test codes to LOINC codes 
    used by Nodis.  This view is part of nodis because it depends on several
    lower-level modules (conf, hef, & static).
    '''
    form = CodeMapForm() # This may be overridden below
    labs = LabResult.objects.filter(native_code=native_code)
    native_names = labs.values_list('native_name', flat=True).distinct().order_by('native_name')
    if request.method == 'POST':
        form = CodeMapForm(request.POST)
        if form.is_valid():
            threshold = form.cleaned_data['threshold']
            test_name = form.cleaned_data['test_name']
            cm, created = LabTestMap.objects.get_or_create(native_code=native_code, test_name=test_name)
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
    return render_to_response('ui/map_native_code.html', values, context_instance=RequestContext(request))
    

@user_passes_test(lambda u: u.is_staff)
def ignore_code_set(request):
    '''
    Ignores a set of native codes pass in REQUEST
    '''
    native_codes = request.POST.getlist('codes')
    if not native_codes:
        msg = 'Request not understood: no test codes specified to be ignored'
        request.user.message_set.create(message=msg)
        return redirect_to(request, reverse('unmapped_labs_report'))
    details = []
    for nc in native_codes:
        ic_obj, created = IgnoredCode.objects.get_or_create(native_code=nc)
        if created:
            ic_obj.save()
            msg = 'Native code "%s" has been added to the ignore list' % nc
        else:
            msg = 'Native code "%s" is already on the ignore list' % nc
        request.user.message_set.create(message=msg)
        log.debug(msg)
    return redirect_to(request, reverse('unmapped_labs_report'))


# PERFORMANCE NOTE:  Current version of django-tables seems to generate entire
# table, then paginate; rather than paginating by object id, then generating
# table.  This results in sub-optimal performance on our Case table, since
# collection_date and result_date are not DB fields, but rather are properties
# which get their data from aggregate queries, which can be expensive.  With
# current count of cases at Atrius this is not a big deal, but it could become
# problematic in the future.  At that point, it will probably be necessary to
# hack on django-tables and submit a patch to its author.

class CaseTableNoPHI(tables.ModelTable):
    '''
    Case table without PHI
    '''
    id = tables.Column(verbose_name='Case ID')
    condition = tables.Column()
    date = tables.Column('Case Date')
    created_timestamp__date = tables.Column('Date Detected')
    provider__dept = tables.Column(verbose_name='Provider Department')
    collection_date = tables.Column(verbose_name='Collection Date', sortable=False)
    result_date = tables.Column(verbose_name='Result Date', sortable=False)
    #
    status = tables.Column()
    sent_timestamp = tables.Column(verbose_name='Sent Date')
    
class CaseTablePHI(tables.ModelTable):
    '''
    Case table including PHI
    '''
    id = tables.Column(verbose_name='Case ID')
    condition = tables.Column()
    date = tables.Column('Case Date')
    created_timestamp__date = tables.Column('Date Detected')
    provider__dept = tables.Column(verbose_name='Provider Department')
    # Begin PHI
    patient__mrn = tables.Column(verbose_name='Patient MRN')
    patient__name = tables.Column(verbose_name='Patient Name', sortable=False)
    patient__date_of_birth = tables.Column(verbose_name='Date of Birth')
    # End PHI
    collection_date = tables.Column(verbose_name='Collection Date', sortable=False)
    result_date = tables.Column(verbose_name='Result Date', sortable=False)
    #
    status = tables.Column()
    sent_timestamp = tables.Column(verbose_name='Sent Date')
    


class CaseFilterFormPHI(forms.Form):
    __status_choices = [('', '---')] + STATUS_CHOICES
    __condition_choices = [('', '---')] + DiseaseDefinition.get_all_condition_choices()
    case_id = forms.CharField(required=False, label="Case ID")
    condition = forms.ChoiceField(choices=__condition_choices, required=False)
    date_after = forms.DateField(required=False, label='Date After')
    date_before = forms.DateField(required=False, label='Date Before')
    patient_mrn = forms.CharField(required=False, label='Patient MRN')
    patient_last_name = forms.CharField(required=False, label='Patient Surname')


class CaseFilterFormNoPHI(forms.Form):
    __status_choices = [('', '---')] + STATUS_CHOICES
    __condition_choices = [('', '---')] + DiseaseDefinition.get_all_condition_choices()
    case_id = forms.CharField(required=False)
    condition = forms.ChoiceField(choices=__condition_choices, required=False)
    date_after = forms.DateField(required=False)
    date_before = forms.DateField(required=False)

@login_required
def case_list(request, status):
    values = {}
    if request.user.has_perm('nodis.view_phi'):
        CaseTable = CaseTablePHI
        CaseFilterForm = CaseFilterFormPHI
    else: # User cannot view or search by PHI
        CaseTable = CaseTableNoPHI
        CaseFilterForm = CaseFilterFormNoPHI
    qs = Case.objects.all()
    if status == 'await':
        qs = qs.filter(status='AR')
    elif status == 'under':
        qs = qs.filter(status='UR')
    elif status == 'queued':
        qs = qs.filter(status='Q')
    elif status == 'sent':
        qs = qs.filter(status='S')
    search_form = CaseFilterForm(request.GET)
    if search_form.is_valid():
        log.debug(search_form.cleaned_data)
        case_id = search_form.cleaned_data['case_id']
        condition = search_form.cleaned_data['condition']
        date_before = search_form.cleaned_data['date_before']
        date_after = search_form.cleaned_data['date_after']
        if case_id:
            qs = qs.filter(pk=case_id)
        if condition:
            qs = qs.filter(condition=condition)
        if date_before:
            qs = qs.filter(date__lte=date_before)
        if date_after:
            qs = qs.filter(date__gte=date_after)
        if request.user.has_perm('nodis.view_phi'):
            patient_mrn = search_form.cleaned_data['patient_mrn']
            patient_last_name = search_form.cleaned_data['patient_last_name']
            if patient_mrn:
                qs = qs.filter(patient__mrn__istartswith=patient_mrn)
            if patient_last_name:
                qs = qs.filter(patient__last_name__istartswith=patient_last_name)
    log_query('Nodis case list', qs)
    table = CaseTable(qs, order_by=request.GET.get('sort', '-id'))
    page = Paginator(table.rows, ROWS_PER_PAGE).page(request.GET.get('page', 1))
    # Remove '?sort=' bit from full URL path
    full_path = request.get_full_path()
    sort_index = full_path.find('&sort')
    if sort_index != -1:
        full_path = full_path[:sort_index]
    # If path does not contain a query string (beginning with '?'), add a '?' 
    # so the template's "&sort=" html forms a valid query
    query_index = full_path.find('?')
    if query_index == -1:
        full_path += '?'
    clear_search_path = full_path[:query_index]
    values['full_path'] = full_path
    values['clear_search_path'] = clear_search_path
    values['table'] = table
    values['page'] = page
    values['search_form'] = search_form
    return render_to_response('ui/case_list.html', values, context_instance=RequestContext(request))



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

def _get_provider_sent_counts(interval):
    '''
    Utility function to generate list of providers sent reports
    and counts of reports sent in the interval provided
    '''
    cursor1 = connection.cursor()
    cursor1.execute("select provider, count(distinct ques_id) initial, " +
       "count(distinct case when state='S' then ques_id end) sent, " +
       "count(distinct case when state in ('FP','FU') then ques_id end) false_positive, " +
       "count(distinct case when state='AS' then ques_id end) autosent " +
       "from (select t0.*,  " +
       "case when t1.sent_id is null or t0.created_on < t1.date_added " +
       "    then 'VAERS team review' " +
       "else (t1.first_name || ' ' || t1.last_name) end provider from " +
       "(select a.id ques_id, a.provider_id, a.state, a.created_on, " +
       "b.id sent_id, b.report_type " +
       "from vaers_questionnaire a left join vaers_report_sent b on a.id=b.questionnaire_id " +
       "where a.created_on > current_timestamp - interval '1" + interval + "' " +
       "or b.date > current_date - interval '1" + interval + "' ) t0 " +
       "inner join (select a.id, a.first_name, a.last_name, b.id sent_id, b.date_added from emr_provider a " +
       "     left join vaers_sender b on a.id=b.provider_id) t1  " +
       "on t0.provider_id=t1.id) vaers_reports " +
       "group by provider;")
    desc = cursor1.description
    table = [dict(zip([col[0] for col in desc], row))
            for row in cursor1.fetchall()]
    return table
    

def _get_oth_counts(interval):
    '''
    Utility method to generate a dictionary of source counts
    over the period of now minus interval
    '''
    cursor1 = connection.cursor()
    cursor1.execute("select a.diag_code, b.name, " +
                       "count(distinct a.id) as ae_counts,  " +
                       "count(distinct a.case_id) as case_counts " +
                    "from " +
                    "(select regexp_split_to_table(a.matching_rule_explain, E'\\\s+') as diag_code, " +
                     "      b.case_id, " +
                     "      a.id " +
                    "from vaers_adverseevent a, " +
                    "     vaers_case_adverse_events b " +
                    "where a.id=b.adverseevent_id " +
                    "     and a.date > current_date - interval '1 " + interval + "' " +
                    "     and a.name='VAERS: Any other Diagnosis') a, " +
                    "     static_icd9 b " +
                    "where a.diag_code=b.code " +
                    "group by a.diag_code, b.name " +
                    "order by count(distinct a.case_id) desc")
    desc = cursor1.description
    table = [dict(zip([col[0] for col in desc], row))
            for row in cursor1.fetchall()]
    return table

def _get_tot_counts(interval):
    '''
    Utility method to generate a dictionary of source counts
    over the period of now minus interval
    '''
    cursor1 = connection.cursor()
    cursor1.execute("select 'Labs' as source, count(*) as counts from emr_labresult " +
                    "where date > current_date - interval '1 " + interval + "' " +
                    "union select 'Visits' as source, count(*) as counts from emr_encounter " +
                    "where date > current_date - interval '1 " + interval + "' " +
                    "union select 'Prescriptions' as source, count(*) as counts from emr_prescription " +
                    "where date > current_date - interval '1 " + interval + "' ")
    desc = cursor1.description
    table = [dict(zip([col[0] for col in desc], row))
            for row in cursor1.fetchall()]
    return table

def _get_vx_counts(interval):
    '''
    Utility method to generate a dictionary of vaccine counts
    over the period of now minus interval
    '''
    cursor1 = connection.cursor()
    cursor1.execute("select name, count(*) as vx_counts " +
                    "from emr_immunization " +
                    "where isvaccine and date > current_date - interval '1 " + interval + "' " +
                    "group by name " +
                    "order by count(*) desc")
    desc = cursor1.description
    table = [dict(zip([col[0] for col in desc], row))
            for row in cursor1.fetchall()]
    return table

def _get_ae_case_counts(interval):
    '''
    Utility method to generate a dictionary of VAERS aes and cases
    over the period of now minus interval
    '''
    cursor1 = connection.cursor()
    cursor1.execute("select a.category, c.name as ae_basis, a.name as ae_name, " +
                   "   count(distinct a.*) as ae_count, count(distinct b.case_id) as case_count " +
                   "from vaers_adverseevent a, " +
                   "     vaers_case_adverse_events b, " +
                   "     django_content_type c " +
                   "where a.id=b.adverseevent_id  " +
                   "     and a.content_type_id=c.id " +
                   "     and a.created_on > current_timestamp - interval '1 " + interval + "' " +
                   "group by a.category, c.name, a.name " +
                   "order by a.category, c.name, count(a.*) desc")
    desc = cursor1.description
    table = [dict(zip([col[0] for col in desc], row))
            for row in cursor1.fetchall()]
    return table

def _get_unmapped_labs():
    '''
    Utililty method to generate a LabTestCondordance QuerySet of unmapped, 
    suspicious tests.  This is *not* a view.  It is called from ui.views.status 
    as well as unmapped_labs_report() below.
    '''
    ignored = IgnoredCode.objects.values('native_code')
    
    mapped = LabTestMap.objects.values('native_code').distinct()
    all_strings = DiseaseDefinition.get_all_test_name_search_strings() + VaersLxHeuristic.test_name_search_strings
    all_strings.sort()
    
    # this only happens when system has just been installed with no data.
    if not all_strings:
        all_strings = ['','']
        
    q_obj = Q(native_name__icontains=all_strings[0])
    for string in all_strings[1:]:
        q_obj |= Q(native_name__icontains=string)
    q_obj &= Q(native_code__isnull=False)
    q_obj &= ~Q(native_code__in=ignored)
    q_obj &= ~Q(native_code__in=mapped)
    unmapped = LabTestConcordance.objects.filter(q_obj).order_by('native_name', 'native_code')
    return unmapped


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
        validator_run = ValidatorRun.objects.all().aggregate(max=Max('pk'))['max']
        #ValidatorRun.objects.all().order_by('-pk')[0]
    if not validator_run:     
        values = {
        'title': 'Case Validator: Summary',
        'run': validator_run,
        'ref_cases': None,
        'results': None,
        'total': 0,
        'related_margin': RELATED_MARGIN,
        }
    return render_to_response('nodis/validator_summary.html', values, context_instance=RequestContext(request))

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

def validate_exact(request, validator_run_id=None):
    if validator_run_id:
        validator_run = get_object_or_404(ValidatorRun, pk=validator_run_id)
    else:
        validator_run = ValidatorRun.objects.all().order_by('-pk')[0]
    exact = validator_run.exact.order_by('ref_case__date')
    condition_form = ConditionForm()
    if request.method == 'POST':
        condition_form = ConditionForm(request.POST)
        if condition_form.is_valid():
            condition = condition_form.cleaned_data['condition']
            log.debug('Filtering on condition: %s' % condition)
            if not condition == '*': # Filter not applied for wildcard
                exact = exact.filter(ref_case__condition=condition)
    values = {
        'title': 'Case Validator: Exact Matches',
        'run': validator_run,
        'exact': exact.select_related(), # Is select_related() helpful here?
        'counts': exact.values('ref_case__condition').order_by('ref_case__condition').annotate(Count('pk')),
        'condition_form': condition_form
        }
    return render_to_response('nodis/validator_exact.html', values, context_instance=RequestContext(request))

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
    values = {
        'title': 'Case Validator: New Cases',
        'run': validator_run,
        }
    #cases = Case.objects.filter(validatorresult__run=validator_run, validatorresult__disposition='new')
    new_cases = validator_run.new.order_by('date')
    condition_form = ConditionForm()
    values['counts'] = new_cases.values('condition').annotate(Count('pk')).order_by('condition')
    values['condition_form'] = condition_form
    if request.method == 'POST':
        condition_form = ConditionForm(request.POST)
        if condition_form.is_valid():
            condition = condition_form.cleaned_data['condition']
            log.debug('Filtering on condition: %s' % condition)
            if not condition == '*': # Filter not applied for wildcard
                new_cases = new_cases.filter(condition=condition)
    values['cases'] = new_cases.order_by('date').select_related() # Is select_related() helpful here?
    return render_to_response('nodis/validator_new.html', values, context_instance=RequestContext(request))


@login_required
def validate_similar(request, validator_run_id=None):
    if validator_run_id:
        validator_run = get_object_or_404(ValidatorRun, pk=validator_run_id)
    else:
        validator_run = ValidatorRun.objects.all().order_by('-pk')[0]
    similar = validator_run.similar.order_by('ref_case__date')
    condition_form = ConditionForm()
    values = {
        'title': 'Case Validator: Similar Cases',
        'run': validator_run,
        }
    if request.method == 'POST':
        condition_form = ConditionForm(request.POST)
        if condition_form.is_valid():
            condition = condition_form.cleaned_data['condition']
            log.debug('Filtering on condition: %s' % condition)
            if not condition == '*': # Filter not applied for wildcard
                similar = similar.filter(ref_case__condition=condition)
    values['similar'] = similar.select_related() # Is select_related() helpful here?
    values['counts'] = validator_run.similar.values('ref_case__condition').order_by('ref_case__condition').annotate(Count('pk'))
    values['condition_form'] = condition_form
    return render_to_response('nodis/validator_similar.html', values, context_instance=RequestContext(request))


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
    
    
