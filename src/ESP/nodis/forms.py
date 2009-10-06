'''
                              ESP Health Project
                         Notifiable Diseases Framework
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

from ESP.nodis.models import STATUS_CHOICES
from ESP.hef.core import BaseHeuristic
from ESP.static.models import Loinc




class CaseStatusForm(forms.Form):
    '''
    Form for mapping Native Code to LOINC
    '''
    status = forms.ChoiceField(STATUS_CHOICES[:4], required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)


class MapNativeCodeForm(forms.Form):
    loinc = forms.ChoiceField(choices=BaseHeuristic.get_all_loincs(choices=True), required=True)