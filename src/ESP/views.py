'''
Views that pertain to the entire ESP project, not just one particular module.
'''

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from ESP.utils.status_report import populate_values


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@login_required
def status(request):
    values = populate_values()
    values['title'] = _('Status Report')
    return render_to_response('status.html', values, context_instance=RequestContext(request))