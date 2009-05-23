from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    (r'^$', 'espss.ssmap.views.espss'),
    (r'^espss/ssmap/admin/', include(admin.site.urls)),
    (r'^ssmap/admin/', include(admin.site.urls)),
    (r'^admin/$', include(admin.site.urls)),
    (r'^ssmap/', 'espss.ssmap.views.ssmap'),
    (r'^espss/ssmap/(\d{8})', 'espss.ssmap.views.bydate'),
    (r'^ssmap/(\d{8})', 'espss.ssmap.views.bydate'),
    (r'^espss/ssmap/', 'espss.ssmap.views.ssmap'),
    (r'^ssmapper/(\d{8})', 'espss.ssmap.views.ssmapper'),
    (r'^ssmapper/', 'espss.ssmap.views.ssmapperdefault'),
    (r'^espss/ssmapper/(\d{8})', 'espss.ssmap.views.ssmapper'),
    (r'^espss/ssmapper/', 'espss.ssmap.views.ssmapperdefault'),
    (r'^espss/$', 'espss.ssmap.views.espss'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}),
)
