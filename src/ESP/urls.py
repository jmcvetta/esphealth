'''
URLs for entire ESP Health django project

'''
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.contrib.auth.views import login, logout

from django.contrib import admin

from ESP.esp.views import index

from settings import MEDIA_ROOT, MEDIA_URL

admin.autodiscover()

urlpatterns = patterns(
    '',
    
    # Core Application
    (r'^$', index),
    (r'^esp/', include('ESP.esp.urls')),
    
    # Vaers
    (r'^vaers/', include('ESP.vaers.urls')),
    
    
    
    # Django Admin
    (r'^admin/(.*)', admin.site.root),
#    (r'^admin/doc/', include('django.contrib.admindocs.urls'),
    


    # Static Content 
    #
    # TODO: Remove before deployment into production!
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)
