# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns

from ESP.vaers import views

urlpatterns = patterns(
    '',
    (r'^$', views.index),
    url(r'^verify/(?P<key>\w*)/$', views.verify, name='verify_case'),
    url(r'^case/(?P<id>\d+)/$', views.case_details, name='present_case'),
    
)

