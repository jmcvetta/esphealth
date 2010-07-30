'''
URLs for entire ESP Health django project

'''
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import handler404
from django.conf.urls.defaults import handler500
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib.auth.forms import AuthenticationForm

from ESP.settings import MEDIA_ROOT, MEDIA_URL
#from ESP.esp.views import index, esplogin
from ESP.ui.views import status_page


admin.autodiscover()

urlpatterns = patterns(
    '', # Why this??
    
    # Core Application
    url(r'^$', status_page, name='status'),
    
    # Vaers
    url(r'^vaers/', include('ESP.vaers.urls')),

    # Syndromic Surveillance
    url(r'^ss/', include('ESP.ss.urls')),

    
    # Login and Logout
    url(r'^login/?$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/?$', logout, {'next_page': '/'}, name='logout'),
    
    # About
    url(r'^about/', direct_to_template, {
        'template': 'about.html',
        'extra_context': {'title': 'About ESP'}
        }, name='about'),
    
    
    # Django Admin
    url(r'^admin/', include(admin.site.urls)),
#    (r'^admin/doc/', include('django.contrib.admindocs.urls'),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    
    # Configuration
    url(r'^conf/', include('ESP.conf.urls')),
    
    # Nodis
    url(r'^nodis/', include('ESP.nodis.urls')),
    
    # Nodis
    url(r'^util/', include('ESP.ui.urls')),
    
    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #url(r'^codes', code_maintenance),
    #url(r'^json_code_grid', json_code_grid, name='json_code_grid'),
)
