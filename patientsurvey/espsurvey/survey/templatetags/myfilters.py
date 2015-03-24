'''
                               ESP Patient Self Survey

@authors: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics www.commoninf.com
@copyright: (c) 2014 cii
@license: LGPL
'''

from django import template

register = template.Library()

@register.filter(name='field_type')
def field_type(field, ftype):
    try:
        
        t = field.field.widget.__class__.__name__
        return t.lower() == ftype
    except:
        pass
    return False

@register.filter(name='field_inline')
def field_inline(field):
    try:
        
        if field.field.inline:
            return True
    except:
        pass
    return False

#this returns the parent field name 
@register.filter(name='field_hidden')
def field_hidden(field):
    try:
        
        t = field.field.hidden
        if t:
            return field.field.hidden[0] 
    except:
        pass
    return False

#this returns the parent field name 
@register.filter(name='field_hidden_parent_type')
def field_hidden_parent_type(field, ftype):
    try:
        
        t = field.field.hidden_parent_type.widget.__class__.__name__
        return t.lower() == ftype 
    except:
        pass
    return False

#this returns the dependent field name 
@register.filter(name='field_unsure')
def field_unsure(field):
    try:
        
        t = field.field.unsure
        if t:
            return field.field.unsure 
    except:
        pass
    return False

@register.filter(name='field_hiding_value')
def field_hiding_value(field):
    try:
        
        t = field.field.hidden
        if t:
            return field.field.hidden[1]  
    except:
        pass
    return False


