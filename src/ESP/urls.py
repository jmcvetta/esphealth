'''
URLs for entire ESP Health django project

'''
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.contrib import admin

from ESP.settings import MEDIA_ROOT, MEDIA_URL
from ESP.esp.views import index, esplogin
from ESP.conf.views import code_maintenance


admin.autodiscover()

urlpatterns = patterns(
    '',
    
    
    # Core Application
    (r'^$', index),
    (r'^esp/', include('ESP.esp.urls')),
    
    # Vaers
    (r'^vaers/', include('ESP.vaers.urls')),
    
    # Login and Logout
    (r'^login/?$', esplogin),
    
    
    # Django Admin
    (r'^admin/(.*)', admin.site.root),
#    (r'^admin/doc/', include('django.contrib.admindocs.urls'),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    (r'^codes', code_maintenance),
)
