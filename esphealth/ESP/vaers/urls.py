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
    
    # ptype can be digest or case.  digest takes a digest value for id, case takes a questionnaire id for id.
    url(r'^(?P<ptype>case|digest)/(?P<id>\w*)/$', views.case_details, name='present_case'),

    #line listing report
    url(r'^download/', views.download_vae_listing, name='download_listing'),    

)

