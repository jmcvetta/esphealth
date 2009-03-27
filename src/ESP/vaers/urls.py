# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns

import views

urlpatterns = patterns(
    '',
    (r'^$', views.index),
    (r'^case/(?P<case_id>\d*)/$', views.present),
    url(r'^case/(?P<case_id>\d*)/(?P<action>\w+)$', views.action, name='case_action')    
)

