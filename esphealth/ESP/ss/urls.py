# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns
from django.conf.urls.defaults import include
from django.conf.urls.defaults import handler404
from django.conf.urls.defaults import handler500


from ESP.ss import views

urlpatterns = patterns(
    '',
    (r'^$', views.index),
    (r'^syndrome/(?P<syndrome>\w+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', views.detail)    
)



