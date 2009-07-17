from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

import views

urlpatterns = patterns(
    '',     
    (r'^$', views.index),
    (r'^manufacturers$', views.manufacturers),
    (r'^vaccine/(?P<id>\d*)$', views.vaccine_detail),
    (r'^manufacturer/(?P<id>\d*)$', views.manufacturer_detail)
    
)
