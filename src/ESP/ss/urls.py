# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns
from django.conf.urls.defaults import include

from ESP.ss import views

urlpatterns = patterns(
    '',
    (r'^$', views.index),
    (r'^date/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', views.date)    
)

