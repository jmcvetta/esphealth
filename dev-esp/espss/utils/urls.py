from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
# added august 2008 rml for 1.0 alpha svn django

urlpatterns = patterns('',
 ( r'^$', include( 'ESP.utils.esp_urls' ) ),
 ( r'^', include( 'ESP.utils.esp_urls' ) ),
 ( r'^/', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP$', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP/', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ssmap$', include( 'ESP.utils.ssmap_urls' ) ),
 ( r'^ssmap', include( 'ESP.utils.ssmap_urls' ) ),
 ( r'^ssmap/', include( 'ESP.utils.ssmap_urls' ) ),
 (r'^ESP/admin/(.*)', admin.site.root),
 (r'^admin/(.*)', admin.site.root),
 (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/ESP/ESP/templates'}),
 
)

