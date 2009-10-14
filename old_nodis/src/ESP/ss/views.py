#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template

PAGE_TEMPLATE_DIR = 'pages/ss/'
WIDGET_TEMPLATE_DIR = 'widgets/ss/'

def index(request):
    today = datetime.date.today()
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'home.html',
                              {'report_date':today})

def date(request, year, month, day):
    date = datetime.date(year=int(year), month=int(month), day=int(day))
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'home.html',
                              {'report_date':date})
