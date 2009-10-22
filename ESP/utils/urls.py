

from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
# added august 2008 rml for 1.0 alpha svn django

from ESP.settings import MEDIA_ROOT

urlpatterns = patterns('',
 ( r'^$', include( 'ESP.utils.esp_urls' ) ),
 ( r'^', include( 'ESP.utils.esp_urls' ) ),
 ( r'^/', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP$', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP/', include( 'ESP.utils.esp_urls' ) ),
 (r'^ESP/admin/(.*)', admin.site.root),
 (r'^admin/(.*)', admin.site.root),
 (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT})
)

