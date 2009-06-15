'''
                              ESP Health Project
                             Configuration Module
                               URL Configuration

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.contrib import admin

from ESP.settings import MEDIA_ROOT, MEDIA_URL
from ESP.esp.views import index, esplogin


urlpatterns = patterns('ESP.conf.views',
    url(r'^codes/loinc/$', 'loinc_mapping'),
    url(r'^codes/native/$', 'native_mapping'),
    url(r'^codes/map/$', 'map_code'),
    url(r'^codes/map/loinc/(?P<loinc_num>\d+)/$', 'map_code', name='map_loinc'),
    url(r'^codes/map/native/(?P<native_code>\d+)/$', 'map_code', name='map_native'),
    #url(r'^json_code_grid', json_code_grid, name='json_code_grid'),
)
