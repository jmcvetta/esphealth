'''
                               ESP Health Project
                             User Interface Module
                                     Views

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''


import re
import sys
import datetime
import csv
import cStringIO as StringIO

from django import forms
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
from django.db.models import Max
from django.db.models import Min
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

from django.forms.widgets import CheckboxInput, SelectMultiple
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe


from ESP.settings import ROWS_PER_PAGE
from ESP.settings import DATE_FORMAT
from ESP.settings import SITE_NAME

from ESP.conf.models import CodeMap
from ESP.conf.models import IgnoredCode
from ESP.static.models import Loinc
from ESP.emr.models import Provenance
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import LabTestConcordance
from ESP.hef.core import BaseHeuristic
from ESP.hef import events # Required to register hef events
from ESP.nodis.models import Condition
from ESP.nodis.models import Case
from ESP.nodis.models import CaseStatusHistory
from ESP.nodis.models import ReferenceCaseList
from ESP.nodis.models import ReferenceCase
from ESP.nodis.models import ValidatorRun
from ESP.nodis.models import ValidatorResult
from ESP.nodis.views import _get_unmapped_labs
from ESP.nodis.forms import CaseStatusForm
from ESP.nodis.forms import CodeMapForm
from ESP.nodis.forms import ConditionForm
from ESP.nodis.forms import ReferenceCaseForm
from ESP.nodis.management.commands.validate_cases import RELATED_MARGIN
from ESP.utils.utils import log
from ESP.utils.utils import Flexigrid
from ESP.utils import TableSelectMultiple



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


def _populate_status_values():
    '''
    Utility method to populate values dict for use with status_page() view and
    manage.py status_report command.
    '''
    today_string = datetime.datetime.now().strftime(DATE_FORMAT)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    new_cases = Case.objects.filter(updated_timestamp__gte=yesterday)
    values = {
        'title': _('Status Report'),
        'today_string': today_string,
        'site_name': SITE_NAME,
        'all_case_summary': Case.objects.values('condition').annotate(count=Count('pk')).order_by('condition'),
        'new_case_summary': new_cases.values('condition').annotate(count=Count('pk')).order_by('condition'),
        'provenances': Provenance.objects.filter(timestamp__gte=yesterday).order_by('-timestamp'),
        'unmapped_labs': _get_unmapped_labs().select_related(),
        }
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
    strings = Condition.all_test_name_search_strings()
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

