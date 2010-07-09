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
    url(r'^labtest/lookup/$', 'labtest_lookup', name='labtest_lookup'),
    url(r'^labtest/detail/$', 'labtest_detail', name='labtest_detail'),
    url(r'^labtest/linelist/(?P<native_code>.*)$', 'labtest_csv', name='labtest_csv'),
    url(r'^labtest/linelist/(?P<native_code>.*)$', 'labtest_csv', name='labtest_csv'),
    url(r'^labtest/ignore_set/$', 'ignore_code_set', name='ignore_code_set'),
    url(r'^labtest/map/(?P<native_code>.+)/$', 'map_native_code', name='map_native_code'),
    url(r'^labtest/unmapped/$', 'unmapped_labs_report', name='unmapped_labs_report'),
    #
    #-------------------------------------------------------------------------------
    # Nodis
    #-------------------------------------------------------------------------------
    #
    url(r'^cases/$', 'case_list', {'status': 'all'}, name='nodis_cases_all'),
    url(r'^cases/list/awaiting_review/$', 'case_list', {'status': 'await'}, name='nodis_cases_awaiting_review'),
    url(r'^cases/list/under_review/$', 'case_list', {'status': 'under'}, name='nodis_cases_under_review'),
    url(r'^cases/list/queued/$', 'case_list', {'status': 'queued'}, name='nodis_cases_queued'),
    url(r'^cases/list/sent/$', 'case_list', {'status': 'sent'}, name='nodis_cases_sent'),
    #
    # JSON Case Grid
    #
    url(r'^cases/json/$', 'json_case_grid', {'status': 'all'}, name='nodis_case_grid'),
    url(r'^cases/json/all/$', 'json_case_grid', {'status': 'all'}),
    url(r'^cases/json/await/$', 'json_case_grid', {'status': 'await'}),
    url(r'^cases/json/under/$', 'json_case_grid', {'status': 'under'}),
    url(r'^cases/json/queued/$', 'json_case_grid', {'status': 'queued'}),
    url(r'^cases/json/sent/$', 'json_case_grid', {'status': 'sent'}),
    #
    # Case Detail
    #
    url(r'^cases/view/(?P<case_id>\d+)/$', 'case_detail', name='nodis_case_detail'),
    url(r'^cases/update/(?P<case_id>\d+)/$', 'case_status_update', name='nodis_case_update'),
    url(r'^cases/transmit/(?P<case_id>\d+)/$', 'case_queue_for_transmit', name='nodis_case_transmit'),
    url(r'^provider/(?P<provider_id>\w+)/$', 'provider_detail', name='provider_detail'),
    url(r'^patient/(?P<patient_pk>\d+)/records/$', 'all_records', name='all_records'),
    #
    # Validator
    #
    url(r'^validate/$', 'validator_summary', name='validator_summary'),
    url(r'^validate/missing/$', 'validate_missing', name='validate_missing'),
    url(r'^validate/missing/case/(?P<result_id>\d+)/$', 'missing_case_detail', name='missing_case_detail'),
    url(r'^validate/new/$', 'validate_new', name='validate_new'),
    url(r'^validate/similar/$', 'validate_similar', name='validate_similar'),
    url(r'^validate/exact/$', 'validate_exact', name='validate_exact'),

)
