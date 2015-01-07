'''
                               ESP Health Project
                             User Interface Module
                           Template Tags and Filters

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc. http://www.commoninf.com
@copyright: (c) 2014 Commonwealth Informatics Inc.
@license: LGPL
'''

from django.core.exceptions import ObjectDoesNotExist
from django import template
from ESP.conf.models import ConditionConfig

register = template.Library()
@register.filter(name='get_url')
def get_url(condition):
    '''
    This custom template tag will return the name of the case detail url provided for a case-condition, 
    or the default case_detail url if nothing is configured
    '''
    try:
        url_name=ConditionConfig.objects.get(name__exact=condition).url_name
        if (url_name=='' or url_name==None):
            url_name='nodis_case_detail'
    except ObjectDoesNotExist:
        url_name='nodis_case_detail'
    return url_name

@register.filter(name='format_note')
def format_note(provider_note):
    '''
    This custom template tag will return a text string with color formatting for specific text strings.
    '''
    provider_note = provider_note.replace('Patient Progress:','<span style="color:red;font-weight:bold;background-color:yellow">Patient Progress:</span>')
    provider_note = provider_note.replace('Final Impression/Diagnosis:','<span style="color:red;font-weight:bold;background-color:yellow">Final Impression/Diagnosis:</span>')
    provider_note = provider_note.replace('Need HPI (History of Present Illness):','<span style="color:red;font-weight:bold;background-color:yellow">Need HPI (History of Present Illness):</span>')
    provider_note = provider_note.replace('Need Assessment:','<span style="color:red;font-weight:bold;background-color:yellow">Need Assessment:</span>')
    provider_note = provider_note.replace('Need Plan:','<span style="color:red;font-weight:bold;background-color:yellow">Need Plan:</span>')
    return provider_note

