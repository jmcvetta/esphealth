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
)

urlpatterns += patterns('ESP.esp.views',
    url(r'^/index/$', 'index'),
    url(r'^$', 'index'),
    url(r'^/$', 'index'),
    url(r'^utilities/$','showutil'),
    url(r'^preload/rulexclud/(?P<update>\S*)/$', 'preloadrulexclud'),
    url(r'^preload/rulexclud/$', 'preloadrulexclud'),
    url(r'^preload/rulexclud/$', 'preloadrulexclud'),
    url(r'^preload/(?P<table>\S*)/update/$', 'preloadupdate'),
    url(r'^preload/(?P<table>\S*)/$', 'preloadview'),
    url(r'^cases/sent/(?P<orderby>\S*)/(?P<download>\S*)/$', 'casesent'),
    url(r'^cases/sent/(?P<orderby>\S*)/$', 'casesent'),
    url(r'^cases/sent/$', 'casesent'),
    url(r'^cases/match/(?P<download>\S*)/$', 'casematch'),
    url(r'^cases/match/$', 'casematch'),
    url(r'^cases/define/download/(?P<cpt>\S*)/(?P<component>\S*)/$', 'casedefine_detail'),
    url(r'^cases/define/detail/$', 'casedefine_detail'),
    url(r'^cases/define/(?P<compfilter>\S*)/$', 'casedefine'),
    url(r'^cases/define/$', 'casedefine'),
    url(r'^cases/(?P<object_id>\d+)/updatewf/(?P<newwf>\S*)/$', 'updateWorkflow'),
    url(r'^cases/(?P<object_id>\d+)/updatewf/$', 'updateWorkflow'),
    url(r'^cases/(?P<inprod>\d+)/(?P<object_id>\d+)/(?P<restrict>\w*)/$', 'old_casedetail'),
    url(r'^pcps/(?P<object_id>\w+)/$', 'pcpdetail'),
    url(r'^lx/(?P<object_id>\w+)/$', 'lxdetail'),
    url(r'^rules/(?P<object_id>\w+)/$', 'ruledetail'),
    url(r'^workflows/(?P<object_id>\d+)/$', 'wfdetail'),
    url(r'^workflows/(?P<object_id>\d+)/updatewfComment/$', 'updateWorkflowComment'),
    url(r'^help/(?P<topic>\w+)/$','showhelp'),
    url(r'^help/$','showhelp'),
    url(r'^admin/(.*)', admin.site.root),
    url(r'^login/$', 'esplogin'),
    url(r'^pswdchange/$', 'password_change'),
    url(r'^logout/$', 'logout'),
    #
    # Case List
    #
    url(r'^cases/list/all/$', 'case_list', {'status': 'all'}, name='cases_all'),
    url(r'^cases/list/awaiting_review/$', 'case_list', {'status': 'await'}, name='cases_awaiting_review'),
    url(r'^cases/list/under_review/$', 'case_list', {'status': 'under'}, name='cases_under_review'),
    url(r'^cases/list/queued/$', 'case_list', {'status': 'queued'}, name='cases_queued'),
    url(r'^cases/list/sent/$', 'case_list', {'status': 'sent'}, name='cases_sent'),
    url(r'^cases/grid/$', 'json_case_grid', {'status': 'all'}, name='json_case_grid'),
    url(r'^cases/grid/all/$', 'json_case_grid', {'status': 'all'}),
    url(r'^cases/grid/await/$', 'json_case_grid', {'status': 'await'}),
    url(r'^cases/grid/under/$', 'json_case_grid', {'status': 'under'}),
    url(r'^cases/grid/queued/$', 'json_case_grid', {'status': 'queued'}),
    url(r'^cases/grid/sent/$', 'json_case_grid', {'status': 'sent'}),
    #
    # Case Detail
    #
    url(r'^cases/view/(?P<object_id>\d+)/$', 'old_casedetail', {'restrict': 'F', 'inprod': 1}, name='case_detail'),
)


