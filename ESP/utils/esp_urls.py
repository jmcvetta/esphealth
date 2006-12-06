from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^/index/$', 'ESP.esp.views.index'),
    (r'^$', 'ESP.esp.views.index'),
    (r'^/$', 'ESP.esp.views.index'),
    (r'^utilities/$','ESP.esp.views.showutil'),                   
    (r'^preload/(?P<table>\S*)/update/$', 'ESP.esp.views.preloadupdate'),                   
    (r'^preload/(?P<table>\S*)/$', 'ESP.esp.views.preloadview'),
    (r'^cases/sent/(?P<orderby>\S*)/(?P<download>\S*)/$', 'ESP.esp.views.casesent'),
    (r'^cases/sent/(?P<orderby>\S*)/$', 'ESP.esp.views.casesent'),
    (r'^cases/sent/$', 'ESP.esp.views.casesent'),
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
    (r'^admin$', include('django.contrib.admin.urls')),
    (r'^admin/$', include('django.contrib.admin.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^login/$', 'ESP.esp.views.login'),
    (r'^pswdchange/$', 'ESP.esp.views.password_change'),
    (r'^logout/$', 'ESP.esp.views.logout'),


)

