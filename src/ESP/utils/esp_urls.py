from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
import sys
sys.path.insert(0, '/home/ESP/')
from ESP.settings import CODEDIR

urlpatterns = patterns('',
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates' % CODEDIR}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/css' % CODEDIR}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/js' % CODEDIR}),
    (r'^/index/$', 'ESP.esp.views.index'),
    (r'^$', 'ESP.esp.views.index'),
    (r'^/$', 'ESP.esp.views.index'),
    (r'^utilities/$','ESP.esp.views.showutil'),
    (r'^preload/rulexclud/(?P<update>\S*)/$', 'ESP.esp.views.preloadrulexclud'),
    (r'^preload/rulexclud/$', 'ESP.esp.views.preloadrulexclud'),
    (r'^preload/rulexclud/$', 'ESP.esp.views.preloadrulexclud'),
    (r'^preload/(?P<table>\S*)/update/$', 'ESP.esp.views.preloadupdate'),                   
    (r'^preload/(?P<table>\S*)/$', 'ESP.esp.views.preloadview'),
    (r'^cases/sent/(?P<orderby>\S*)/(?P<download>\S*)/$', 'ESP.esp.views.casesent'),
    (r'^cases/sent/(?P<orderby>\S*)/$', 'ESP.esp.views.casesent'),
    (r'^cases/sent/$', 'ESP.esp.views.casesent'),
    (r'^cases/search/$', 'ESP.esp.views.casesearch'),
    (r'^cases/match/(?P<download>\S*)/$', 'ESP.esp.views.casematch'),                       
    (r'^cases/match/$', 'ESP.esp.views.casematch'),
    (r'^cases/define/download/(?P<cpt>\S*)/(?P<component>\S*)/$', 'ESP.esp.views.casedefine_detail'),                 
    (r'^cases/define/detail/$', 'ESP.esp.views.casedefine_detail'),
    (r'^cases/define/(?P<compfilter>\S*)/$', 'ESP.esp.views.casedefine'),
    (r'^cases/define/$', 'ESP.esp.views.casedefine'),
    (r'^cases/search/(?P<inprod>\d+)/$', 'ESP.esp.views.casesearch'),
    (r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/(?P<orderby>\S*)/(?P<download>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/(?P<orderby>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/$', 'ESP.esp.views.casesearch'),                   
    (r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/$', 'ESP.esp.views.casesearch'),                   
    (r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/$', 'ESP.esp.views.casesearch'),
                       
    (r'^cases/(?P<object_id>\d+)/updatewf/(?P<newwf>\S*)/$', 'ESP.esp.views.updateWorkflow'),
    (r'^cases/(?P<object_id>\d+)/updatewf/$', 'ESP.esp.views.updateWorkflow'),
    (r'^cases/(?P<inprod>\d+)/(?P<object_id>\d+)/(?P<restrict>\w*)/$', 'ESP.esp.views.old_casedetail'),
    (r'^pcps/(?P<object_id>\w+)/$', 'ESP.esp.views.pcpdetail'),
    (r'^lx/(?P<object_id>\w+)/$', 'ESP.esp.views.lxdetail'),                  
    (r'^rules/(?P<object_id>\w+)/$', 'ESP.esp.views.ruledetail'),
    (r'^workflows/(?P<object_id>\d+)/$', 'ESP.esp.views.wfdetail'),
    (r'^workflows/(?P<object_id>\d+)/updatewfComment/$', 'ESP.esp.views.updateWorkflowComment'),
    (r'^help/(?P<topic>\w+)/$','ESP.esp.views.showhelp'),
    (r'^help/$','ESP.esp.views.showhelp'),
    (r'^admin/(.*)', admin.site.root),
    (r'^login/$', 'ESP.esp.views.esplogin'),
    (r'^pswdchange/$', 'ESP.esp.views.password_change'),
    (r'^logout/$', 'ESP.esp.views.logout'),

    (r'^ESP/images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates' % CODEDIR}),
    (r'^ESP//index/$', 'ESP.esp.views.index'),
    (r'^ESP/$', 'ESP.esp.views.index'),
    (r'^ESP//$', 'ESP.esp.views.index'),
    (r'^ESP/utilities/$','ESP.esp.views.showutil'),
    (r'^ESP/preload/rulexclud/(?P<update>\S*)/$', 'ESP.esp.views.preloadrulexclud'),
    (r'^ESP/preload/rulexclud/$', 'ESP.esp.views.preloadrulexclud'),
    (r'^ESP/preload/rulexclud/$', 'ESP.esp.views.preloadrulexclud'),
        

    (r'^ESP/preload/(?P<table>\S*)/update/$', 'ESP.esp.views.preloadupdate'),
    (r'^ESP/preload/(?P<table>\S*)/$', 'ESP.esp.views.preloadview'),
    (r'^ESP/cases/sent/(?P<orderby>\S*)/(?P<download>\S*)/$', 'ESP.esp.views.casesent'),
    (r'^ESP/cases/sent/(?P<orderby>\S*)/$', 'ESP.esp.views.casesent'),
    (r'^ESP/cases/sent/$', 'ESP.esp.views.casesent'),

    (r'^ESP/cases/search/$', 'ESP.esp.views.casesearch'),
    (r'^ESP/cases/match/(?P<download>\S*)/$', 'ESP.esp.views.casematch'),
    (r'^ESP/cases/match/$', 'ESP.esp.views.casematch'),
    (r'^ESP/cases/define/download/(?P<cpt>\S*)/(?P<component>\S*)/$', 'ESP.esp.views.casedefine_detail'),
    (r'^ESP/cases/define/detail/$', 'ESP.esp.views.casedefine_detail'),
    (r'^ESP/cases/define/(?P<compfilter>\S*)/$', 'ESP.esp.views.casedefine'),
    (r'^ESP/cases/define/$', 'ESP.esp.views.casedefine'),
    (r'^ESP/cases/search/(?P<inprod>\d+)/$', 'ESP.esp.views.casesearch'),
    (r'^cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/(?P<orderby>\S*)/(?P<download>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^ESP/cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/(?P<orderby>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^ESP/cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/(?P<rulefilter>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^ESP/cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/(?P<mrnfilter>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^ESP/cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/(?P<cfilter>\S*)/$', 'ESP.esp.views.casesearch'),
    (r'^ESP/cases/search/(?P<inprod>\d+)/(?P<wf>\S*)/$', 'ESP.esp.views.casesearch'),
    
    (r'^ESP/cases/(?P<object_id>\d+)/updatewf/(?P<newwf>\S*)/$', 'ESP.esp.views.updateWorkflow'),
    (r'^ESP/cases/(?P<object_id>\d+)/updatewf/$', 'ESP.esp.views.updateWorkflow'),
    (r'^ESP/cases/(?P<inprod>\d+)/(?P<object_id>\d+)/(?P<restrict>\w*)/$', 'ESP.esp.views.old_casedetail'),
    (r'^ESP/pcps/(?P<object_id>\w+)/$', 'ESP.esp.views.pcpdetail'),
    (r'^ESP/lx/(?P<object_id>\w+)/$', 'ESP.esp.views.lxdetail'),
    (r'^ESP/rules/(?P<object_id>\w+)/$', 'ESP.esp.views.ruledetail'),
    (r'^ESP/workflows/(?P<object_id>\d+)/$', 'ESP.esp.views.wfdetail'),
    (r'^ESP/workflows/(?P<object_id>\d+)/updatewfComment/$', 'ESP.esp.views.updateWorkflowComment'),
    (r'^ESP/help/(?P<topic>\w+)/$','ESP.esp.views.showhelp'),
    (r'^ESP/help/$','ESP.esp.views.showhelp'),
    (r'^ESP/admin/(.*)', admin.site.root),
    (r'^ESP/login/$', 'ESP.esp.views.esplogin'),
    (r'^ESP/pswdchange/$', 'ESP.esp.views.password_change'),
    (r'^ESP/logout/$', 'ESP.esp.views.logout'),
    
)

urlpatterns += patterns('ESP.esp.views',
    #
    # New pages to display HIPAA-restricted case information
    #
    url(r'^new/cases/list', 'case_list'),
    url(r'^new/cases/grid', 'json_case_grid', name='json_case_grid'),
)


