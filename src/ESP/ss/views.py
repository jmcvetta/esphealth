#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import random

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template

from definitions import SYNDROME_NAMES
from mapping import MAP_ZOOM_LEVEL, MAP_CENTER_LATITUDE, MAP_CENTER_LONGITUDE

PAGE_TEMPLATE_DIR = 'pages/ss/'
WIDGET_TEMPLATE_DIR = 'widgets/ss/'

def index(request):
    today = datetime.date.today()
    return detail(request, 'ili', today.year, today.month, today.day)

def detail(request, syndrome, year, month, day):

    def url_from_date(d, syndrome):
        return reverse(detail, kwargs={'syndrome':syndrome, 
                                       'year':'%04d' % d.year, 
                                       'month':'%02d' % d.month, 
                                       'day':'%02d' % d.day})


    
    date = datetime.date(year=int(year), month=int(month), day=int(day))

    previous_week_url = url_from_date(date - datetime.timedelta(days=7), syndrome)
    next_week_url = url_from_date(date + datetime.timedelta(days=7), syndrome)

    previous_day_url = url_from_date(date - datetime.timedelta(days=1), syndrome)
    next_day_url = url_from_date(date + datetime.timedelta(days=1), syndrome)

    all_syndrome_urls = dict([(k, url_from_date(date, k))
                              for k, v in SYNDROME_NAMES.items()])

    syndromes = {}
    for key, value in SYNDROME_NAMES.items():
        syndromes[key] = {'name':value, 'url':all_syndrome_urls[key]}

    
    latitude, longitude = MAP_CENTER_LATITUDE, MAP_CENTER_LONGITUDE
    zoom = MAP_ZOOM_LEVEL

    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'home.html',
                              {'report_date':date,
                               'title': 'Syndrome Heat Map',
                               'syndromes':syndromes,
                               'syndrome_key':syndrome,
                               'selected_syndrome': SYNDROME_NAMES[syndrome],
                               'latitude': latitude,
                               'longitude': longitude,
                               'zoom':zoom,
                               'next_week_url':next_week_url,
                               'previous_week_url':previous_week_url,
                               'next_day_url':next_day_url,
                               'previous_day_url':previous_day_url})

