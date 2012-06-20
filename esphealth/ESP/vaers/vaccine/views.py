#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.shortcuts import render_to_response

from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site

from ESP.static.models import Vaccine
from ESP.static.models import ImmunizationManufacturer
from ESP.conf.models import VaccineCodeMap
from ESP.conf.models import VaccineManufacturerMap
from ESP.vaers.models import AdverseEvent

from ESP.vaers.forms import CaseConfirmForm
from ESP.utils.utils import log
from ESP.utils.utils import Flexigrid
from ESP.vaers.vaccine.forms import StandardVaccinesForm, StandardManufacturersForm

PAGE_TEMPLATE_DIR = 'pages/vaers/'
WIDGET_TEMPLATE_DIR = 'widgets/vaers/'


def index(request):
    unmapped_vaccines = VaccineCodeMap.objects.filter(canonical_code__isnull=True)
    mapped_vaccines = VaccineCodeMap.objects.filter(canonical_code__isnull=False)

    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'vaccines.html',
                              {'unmapped_vaccines':unmapped_vaccines,
                               'mapped_vaccines':mapped_vaccines})

def manufacturers(request):
    unmapped_manufacturers = VaccineManufacturerMap.objects.filter(canonical_code__isnull=True)
    mapped_manufacturers = VaccineManufacturerMap.objects.filter(canonical_code__isnull=False)
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'vaccine_index.html',
                              {'unmapped_manufacturers':unmapped_manufacturers,
                               'mapped_manufacturers':mapped_manufacturers})

    


def vaccine_detail(request, id):
    is_post = request.method == 'POST'
    form = (is_post and StandardVaccinesForm(request.POST)) or StandardVaccinesForm()
    message = ''
    if is_post and form.is_valid():
        native = VaccineCodeMap.objects.get(native_code=id)
        #TODO: figure out what is going on with native_code and 
        standard = Vaccine.objects.get(code=int(form.cleaned_data['vaccine']))
        native.canonical_code = standard
        native.save()
        message = 'Native Vaccine %s now mapped to CVX value of %s' % (native, standard)
    else:
        native = VaccineCodeMap.objects.get(native_code=id)
    
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'map_vaccine.html',
                              {'native_vaccine':native, 'form':form,
                               'message':message})

        
def manufacturer_detail(request, id):
    is_post = request.method == 'POST'
    form = (is_post and StandardManufacturersForm(request.POST)) or StandardManufacturersForm()
    message = ''
    if is_post and form.is_valid():
        native = VaccineManufacturerMap.objects.get(id=id)
        standard = ImmunizationManufacturer.objects.get(code=form.cleaned_data['manufacturer'])
        native.canonical_code = standard
        native.save()
        message = 'Native Manufacturer %s now mapped to MVX value of %s' % (native, standard)
    else:
        native = VaccineManufacturerMap.objects.get(id=id)
    
    return direct_to_template(request, PAGE_TEMPLATE_DIR + 'map_manufacturer.html',
                              {'native_manufacturer':native, 'form':form,
                               'message':message})

        

    

    
