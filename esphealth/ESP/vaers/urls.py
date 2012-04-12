# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns
from django.conf.urls.defaults import include

from ESP.vaers import views


urlpatterns = patterns(
    '',
    (r'^$', views.index),
    (r'^casetable$', views.list_cases),
    (r'^notify/(?P<id>\d+)/$', views.notify),
    (r'^report$', views.report),

    # Vaccine and Manufacturer Mapping
    url(r'^vaccines/', include('ESP.vaers.vaccine.urls')),
    
    
    url(r'^verify/(?P<key>\w*)/$', views.verify, name='verify_case'),
    url(r'^case/(?P<id>\d+)/$', views.case_details, name='present_case'),

    #line listing report
    url(r'^download/', views.download_vae_listing, name='download_listing'),    

)

