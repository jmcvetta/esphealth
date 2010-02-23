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
from ESP.nodis.models import Condition
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
from ESP.nodis.management.commands.validate_cases import RELATED_MARGIN
from ESP.utils.utils import log
from ESP.utils.utils import Flexigrid



#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class TableSelectMultiple(SelectMultiple):
    # This class taken from Django Snippets.
    # URL:    http://www.djangosnippets.org/snippets/518/
    # Author:  insin
    """
    Provides selection of items via checkboxes, with a table row
    being rendered for each item, the first cell in which contains the
    checkbox.

    When providing choices for this field, give the item as the second
    item in all choice tuples. For example, where you might have
    previously used::

        field.choices = [(item.id, item.name) for item in item_list]

    ...you should use::

        field.choices = [(item.id, item) for item in item_list]
    """
    def __init__(self, item_attrs, *args, **kwargs):
        """
        item_attrs
            Defines the attributes of each item which will be displayed
            as a column in each table row, in the order given.

            Any callable attributes specified will be called and have
            their return value used for display.

            All attribute values will be escaped.
        """
        super(TableSelectMultiple, self).__init__(*args, **kwargs)
        self.item_attrs = item_attrs

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        str_values = set([force_unicode(v) for v in value]) # Normalize to strings.
        for i, (option_value, item) in enumerate(self.choices):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            output.append(u'<tr><td>%s</td>' % rendered_cb)
            for attr in self.item_attrs:
                if callable(getattr(item, attr)):
                    content = getattr(item, attr)()
                else:
                    content = getattr(item, attr)
                output.append(u'<td>%s</td>' % escape(content))
            output.append(u'</tr>')
        return mark_safe(u'\n'.join(output))

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
        print row
        details.append(row)
    values['details'] = details
    return render_to_response('ui/labtest_detail.html', values, context_instance=RequestContext(request))