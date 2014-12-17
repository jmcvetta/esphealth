'''
                              ESP Health Project
                                qmetric Module
                               URL Configuration

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc. http://www.commoninf.com
@copyright: (c) 2014 Commonwealth Informatics Inc.
@license: LGPL
'''


from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

urlpatterns = patterns('ESP.qmetric.views',
    url(r'^qmetric/results/$', 'qmetric_results', name='qmetric_results'),
)