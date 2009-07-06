'''
                              ESP Health Project
                         Notifiable Diseases Framework
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


urlpatterns = patterns('ESP.nodis.views',
    url(r'^cases/$', 'case_list', {'status': 'all'}, name='nodis_case_list'),
    url(r'^cases/json/$', 'json_case_grid', {'status': 'all'}, name='nodis_case_grid'),
    url(r'^cases/json/all/$', 'json_case_grid', {'status': 'all'}),
    url(r'^cases/json/await/$', 'json_case_grid', {'status': 'await'}),
    url(r'^cases/json/under/$', 'json_case_grid', {'status': 'under'}),
    url(r'^cases/json/queued/$', 'json_case_grid', {'status': 'queued'}),
    url(r'^cases/json/sent/$', 'json_case_grid', {'status': 'sent'}),
)
