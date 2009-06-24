'''
                              ESP Health Project
                             Configuration Module
User Interface Forms

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


from django import forms
from django.forms.util import ErrorList
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm




class CodeMappingForm(forms.Form):
    '''
    Form for mapping Native Code to LOINC
    '''
    native_name = forms.CharField(max_length=255, required=True)
    native_code = forms.CharField(max_length=100, required=True)

