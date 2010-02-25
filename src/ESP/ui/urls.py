'''
                              ESP Health Project
User Interface Module
                               URL Configuration

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''


from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import handler404
from django.conf.urls.defaults import handler500
from django.contrib import admin

from ESP.settings import MEDIA_ROOT, MEDIA_URL


urlpatterns = patterns('ESP.ui.views',
    #
    # Utilities
    #
    url(r'^tests/lookup/$', 'labtest_lookup', name='labtest_lookup'),
    url(r'^tests/detail/$', 'labtest_detail', name='labtest_detail'),
    url(r'^tests/linelist/(?P<native_code>.*)$', 'labtest_csv', name='labtest_csv'),
)
