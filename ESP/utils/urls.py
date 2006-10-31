from django.conf.urls.defaults import *

# split into snsearch and mrnsearch
# updated may 26 for fastcgi server
# which requires all urls to start with
# /ESP/demo
# moving the admin interface is not so easy..


urlpatterns = patterns('',
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'C:/django/ESP/templates'}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/rerla/mydjango/templates'}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/rerla/mydjango/templates'}),
                       
    (r'^/index/$', 'ESP.esp.views.index'),
    (r'^$', 'ESP.esp.views.index'),
    (r'^/$', 'ESP.esp.views.index'),
    (r'^utilities/$','ESP.esp.views.showutil'),                   
    (r'^preload/(?P<table>\S*)/update/$', 'ESP.esp.views.preloadupdate'),                   
    (r'^preload/(?P<table>\S*)/$', 'ESP.esp.views.preloadview'),
    (r'^cases/search/$', 'ESP.esp.views.casesearch'),
    (r'^cases/search/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<orderby>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^cases/search/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/$', 'ESP.esp.views.casesearch'),                   
    (r'^cases/search/(?P<wf>\S*)/(?P<cfilter>\S*)/$', 'ESP.esp.views.casesearch'),                   
    (r'^cases/search/(?P<wf>\S*)/$', 'ESP.esp.views.casesearch'),   
    (r'^cases/(?P<object_id>\d+)/updatewf/$', 'ESP.esp.views.updateWorkflow'),
    (r'^cases/(?P<object_id>\d+)/(?P<restrict>\w*)/$', 'ESP.esp.views.casedetail'),
    (r'^pcps/(?P<object_id>\w+)/$', 'ESP.esp.views.pcpdetail'),
    (r'^lx/(?P<object_id>\w+)/$', 'ESP.esp.views.lxdetail'),                  
    (r'^rules/(?P<object_id>\w+)/$', 'ESP.esp.views.ruledetail'),
    (r'^workflows/(?P<object_id>\d+)/$', 'ESP.esp.views.wfdetail'),
    (r'^workflows/(?P<object_id>\d+)/updatewfComment/$', 'ESP.esp.views.updateWorkflowComment'),
    (r'^help/(?P<topic>\w+)/$','ESP.esp.views.showhelp'),
    (r'^help/$','ESP.esp.views.showhelp'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^accounts/login/$', 'ESP.esp.views.login'),
    (r'^logout/$', 'ESP.esp.views.logout'),
    (r'^ESP/demo/index/$', 'ESP.esp.views.index'),
    (r'^ESP/demo$', 'ESP.esp.views.index'),
    (r'^ESP/demo/$', 'ESP.esp.views.index'),
    (r'^ESP/demo/cases/search/$', 'ESP.esp.views.casesearch'),
    (r'^ESP/demo/cases/snsearch/$', 'ESP.esp.views.caseNameSearch'),
    (r'^ESP/demo/cases/snsearch/(?P<snfilter>\s*)/$', 'ESP.esp.views.caseNameSearch'),                       
    (r'^ESP/demo/cases/mrnsearch/$', 'ESP.esp.views.caseMRNSearch'),
    (r'^ESP/demo/cases/mrnsearch/(?P<mrnfilter>\s*)/$', 'ESP.esp.views.caseMRNSearch'),                       
    (r'^ESP/demo/cases/(?P<object_id>\d+)/(?P<restrict>\w*)/$', 'ESP.esp.views.casedetail'),
    (r'^ESP/demo/cases/search/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/$', 'ESP.esp.views.casesearch'),                   
    (r'^ESP/demo/cases/search/(?P<wf>\S*)/(?P<cfilter>\S*)/$', 'ESP.esp.views.casesearch'),                   
    (r'^ESP/demo/cases/search/(?P<wf>\S*)/$', 'ESP.esp.views.casesearch'),                   
    (r'^ESP/demo/cases/(?P<object_id>\d+)/$', 'ESP.esp.views.casedetail'),
    (r'^ESP/demo/cases/(?P<object_id>\d+)/updatewf/$', 'ESP.esp.views.updateWorkflow'),
    (r'^ESP/demo/pcps/(?P<object_id>\w+)/$', 'ESP.esp.views.pcpdetail'),
    (r'^ESP/demo/lx/(?P<object_id>\w+)/$', 'ESP.esp.views.lxdetail'),                   
    (r'^ESP/demo/rules/(?P<object_id>\w+)/$', 'ESP.esp.views.ruledetail'),
    (r'^ESP/demo/workflows/(?P<object_id>\d+)/$', 'ESP.esp.views.wfdetail'),
    (r'^ESP/demo/workflows/(?P<object_id>\d+)/updatewfComment/$', 'ESP.esp.views.updateWorkflowComment'),
    (r'^ESP/demo/help/(?P<topic>\w+)/$','ESP.esp.views.showhelp'),
    (r'^ESP/demo/help/$','ESP.esp.views.showhelp'),
    (r'^ESP/demo/admin/', include('django.contrib.admin.urls')),
    (r'^ESP/demo/admin/', include('django.contrib.admin.urls')),
    (r'^ESP/demo/accounts/login/$', 'ESP.esp.views.login'),
    (r'^ESP/demo/logout/$', 'ESP.esp.views.logout'),


)

