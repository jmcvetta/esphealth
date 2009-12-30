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
from ESP.nodis.models import Condition
from ESP.hef.core import BaseHeuristic
from ESP.static.models import Loinc




class CaseStatusForm(forms.Form):
    '''
    Form for mapping Native Code to LOINC
    '''
    status = forms.ChoiceField(STATUS_CHOICES[:4], required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)


class CodeMapForm(forms.Form):
    heuristic = forms.ChoiceField(choices=BaseHeuristic.lab_heuristic_choices(), required=True)
    threshold = forms.FloatField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    output_code = forms.CharField(max_length=100, required=False)

class ConditionForm(forms.Form):
    condition = forms.ChoiceField(choices=Condition.condition_choices(wildcard=True))

class ReferenceCaseForm(forms.Form):
    notes = forms.CharField(required=False, widget=forms.Textarea)
    ignore = forms.BooleanField(required=False)