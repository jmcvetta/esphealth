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
from django.conf.urls.defaults import handler404
from django.conf.urls.defaults import handler500
from django.contrib import admin

from esp.settings import MEDIA_ROOT, MEDIA_URL


urlpatterns = patterns('ESP.conf.views',
    url(r'^codes/ignore/(?P<native_code>.+)/$', 'ignore_code', name='ignore_code'),
    url(r'^codes/report', 'heuristic_mapping_report', name='heuristic_mapping_report'),
    #url(r'^json_code_grid', json_code_grid, name='json_code_grid'),
)
