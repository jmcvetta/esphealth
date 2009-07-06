'''
URLs for entire ESP Health django project

'''
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.contrib import admin

from ESP.settings import MEDIA_ROOT, MEDIA_URL
from ESP.esp.views import index, esplogin


admin.autodiscover()

urlpatterns = patterns(
    '', # Why this??
    
    # Core Application
    url(r'^$', index),
    url(r'^esp/', include('ESP.esp.urls')),
    
    # Vaers
    url(r'^vaers/', include('ESP.vaers.urls')),
    
    # Login and Logout
    url(r'^login/?$', esplogin),
    
    
    # Django Admin
    url(r'^admin/(.*)', admin.site.root),
#    (r'^admin/doc/', include('django.contrib.admindocs.urls'),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    
    # Configuration
    url(r'^conf/', include('ESP.conf.urls')),
    
    # Nodis
    url(r'^nodis/', include('ESP.nodis.urls')),
    
    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #url(r'^codes', code_maintenance),
    #url(r'^json_code_grid', json_code_grid, name='json_code_grid'),
)
