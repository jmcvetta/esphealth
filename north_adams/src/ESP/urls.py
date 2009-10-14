'''
URLs for entire ESP Health django project

'''
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Django Admin
    url(r'^ESP/admin/(.*)', admin.site.root, name='db_admin'),
    url(r'^ESP/admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Core Application
    url(r'^ESP/', include('ESP.esp.urls')),
    url(r'', include('ESP.esp.urls')),
    
    # Static Content 
    #
    # TODO: Remove before deployment into production!
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/ESP/ESP/templates'}),
)
