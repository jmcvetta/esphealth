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

from espsurvey.settings import MEDIA_ROOT, MEDIA_URL

from espsurvey.ui.views import launch_survey, save_survey_response, thanks_for_survey, survey_admin, enter_survey

admin.autodiscover()

urlpatterns = patterns('',
    
    
    # Core Application
    url(r'^launch_survey', launch_survey, name='launch_survey'),
    url(r'^enter_survey', enter_survey, name='enter_survey'),
    url(r'^$', survey_admin, name='esp_survey'),
    url(r'^thanks_for_survey', thanks_for_survey, name='thanks_for_survey'),
    
    url(r'^save_survey_response', save_survey_response, name='save_survey_response'),
     
    # Django Admin
    url(r'^admin/', include(admin.site.urls)),

      # Login and Logout
    url(r'^login/?$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/?$', logout, {'next_page': '/'}, name='logout'),
    
    # About
    url(r'^about/', direct_to_template, {
        'template': 'about.html',
        'extra_context': {'title': 'About ESP'}
        }, name='about'),
   
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    
    
)
