# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns

import views

urlpatterns = patterns(
    '',
    (r'^$', views.index),
    url(r'^case/(?P<key>\w*)/$', views.present, name='case_details'),
    url(r'^case/(?P<case_id>\d*)/(?P<action>\w+)$', views.action, name='case_action')    
)

