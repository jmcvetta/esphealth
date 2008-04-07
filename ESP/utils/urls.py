from django.conf.urls.defaults import *

urlpatterns = patterns('',
 ( r'^$', include( 'ESP.utils.esp_urls' ) ),
 ( r'^', include( 'ESP.utils.esp_urls' ) ),
 ( r'^/', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP$', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP', include( 'ESP.utils.esp_urls' ) ),
 ( r'^ESP/', include( 'ESP.utils.esp_urls' ) ),
 (r'^ESP/admin/', include('django.contrib.admin.urls')),
 (r'^admin/', include('django.contrib.admin.urls')),
)

