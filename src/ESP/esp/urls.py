'''
URLs for ESP Health core
'''


from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from ESP.settings import CODEDIR

urlpatterns = patterns('',
    url(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates' % CODEDIR}),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/css' % CODEDIR}),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/js' % CODEDIR}),
    url(r'^/index/$', 'ESP.esp.views.index'),
    url(r'^$', 'ESP.esp.views.index'),
    url(r'^/$', 'ESP.esp.views.index'),
    url(r'^utilities/$','ESP.esp.views.showutil'),
    url(r'^preload/rulexclud/(?P<update>\S*)/$', 'ESP.esp.views.preloadrulexclud'),
    url(r'^preload/rulexclud/$', 'ESP.esp.views.preloadrulexclud'),
    url(r'^preload/rulexclud/$', 'ESP.esp.views.preloadrulexclud'),
        

    url(r'^preload/(?P<table>\S*)/update/$', 'ESP.esp.views.preloadupdate'),
    url(r'^preload/(?P<table>\S*)/$', 'ESP.esp.views.preloadview'),
    url(r'^cases/sent/(?P<orderby>\S*)/(?P<download>\S*)/$', 'ESP.esp.views.casesent'),
    url(r'^cases/sent/(?P<orderby>\S*)/$', 'ESP.esp.views.casesent'),
    url(r'^cases/sent/$', 'ESP.esp.views.casesent'),

    url(r'^cases/search/$', 'ESP.esp.views.casesearch'),
    url(r'^cases/match/(?P<download>\S*)/$', 'ESP.esp.views.casematch'),
    url(r'^cases/match/$', 'ESP.esp.views.casematch'),
    url(r'^cases/define/download/(?P<cpt>\S*)/(?P<component>\S*)/$', 'ESP.esp.views.casedefine_detail'),
    url(r'^cases/define/detail/$', 'ESP.esp.views.casedefine_detail'),
    url(r'^cases/define/(?P<compfilter>\S*)/$', 'ESP.esp.views.casedefine'),
    url(r'^cases/define/$', 'ESP.esp.views.casedefine'),
    url(r'^cases/search/(?P<inprod>\d+)/$', 'ESP.esp.views.casesearch'),
    url(r'^^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/(?P<orderby>\S*)/(?P<download>\S*)/$', 'ESP.esp.views.casesearch'),
    url(r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/(?P<orderby>\S*)/$', 'ESP.esp.views.casesearch'),
    url(r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/$', 'ESP.esp.views.casesearch'),
    url(r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/$', 'ESP.esp.views.casesearch'),
    url(r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/$', 'ESP.esp.views.casesearch'),
    url(r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/$', 'ESP.esp.views.casesearch'),
    
    url(r'^cases/(?P<object_id>\d+)/updatewf/(?P<newwf>\S*)/$', 'ESP.esp.views.updateWorkflow'),
    url(r'^cases/(?P<object_id>\d+)/updatewf/$', 'ESP.esp.views.updateWorkflow'),
    url(r'^cases/(?P<inprod>\d+)/(?P<object_id>\d+)/(?P<restrict>\w*)/$', 'ESP.esp.views.old_casedetail'),
    url(r'^pcps/(?P<object_id>\w+)/$', 'ESP.esp.views.pcpdetail'),
    url(r'^lx/(?P<object_id>\w+)/$', 'ESP.esp.views.lxdetail'),
    url(r'^rules/(?P<object_id>\w+)/$', 'ESP.esp.views.ruledetail'),
    url(r'^workflows/(?P<object_id>\d+)/$', 'ESP.esp.views.wfdetail'),
    url(r'^workflows/(?P<object_id>\d+)/updatewfComment/$', 'ESP.esp.views.updateWorkflowComment'),
    url(r'^help/(?P<topic>\w+)/$','ESP.esp.views.showhelp'),
    url(r'^help/$','ESP.esp.views.showhelp'),
    url(r'^admin/(.*)', admin.site.root),
    url(r'^login/$', 'ESP.esp.views.esplogin'),
    url(r'^pswdchange/$', 'ESP.esp.views.password_change'),
    url(r'^logout/$', 'ESP.esp.views.logout'),
)

urlpatterns += patterns('ESP.esp.views',
    #
    # New pages to display HIPAA-restricted case information
    #
    url(r'^cases/list', 'case_list', name='cases_all'),
    url(r'^cases/grid', 'json_case_grid', name='json_case_grid'),
)


