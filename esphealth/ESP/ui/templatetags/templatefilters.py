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
    except ObjectDoesNotExist:
        url_name='nodis_case_detail'
    return url_name

