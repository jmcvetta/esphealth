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
from ESP.nodis.base import DiseaseDefinition #Condition
from ESP.hef.base import AbstractLabTest
from ESP.static.models import Loinc
from ESP.vaers.heuristics import VaersLxHeuristic
from ESP.conf.models import Status


class GenericStatusForm(forms.Form):
    '''
    Form for pertussis details (initially)
    '''
    def __init__(self, curstat, *args, **kwargs):
        super(GenericStatusForm,self).__init__(*args, **kwargs)
        self.fields['comment'] = forms.CharField(widget=forms.Textarea, required=False)
        try:
            status_choice_codes=Status.objects.get(code__exact=curstat).startcode.all().values_list('endcode',flat=True)
        except:
            status_choice_codes=STATUS_CHOICES
        #status_choices = Status.objects.filter(code__in=status_choice_codes).values_list('name',flat=True)
        self.fields['status'] = forms.ModelChoiceField(queryset=Status.objects.filter(code__in=status_choice_codes), required=False, )



class CaseStatusForm(forms.Form):
    '''
    Form for mapping Native Code to LOINC
    '''
    status = forms.ChoiceField(STATUS_CHOICES[:4], required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)


class CodeMapForm(forms.Form):
    # fake instanciation to get the labs in the drop down
    vaerslabs = VaersLxHeuristic('wbc',None,None,None)
    TEST_CHOICES = [(name, name) for name in AbstractLabTest.get_all_names()]
    # FIXING MULTIPLE BILIRUBINS IN LIST 
    for name in vaerslabs.get_all_names():
        if (name,name) not in TEST_CHOICES:
            TEST_CHOICES.append((name, name))
    
    TEST_CHOICES.sort()
    test_name = forms.ChoiceField(choices=TEST_CHOICES, required=True)
    threshold = forms.FloatField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    output_code = forms.CharField(max_length=100, required=False)

class ConditionForm(forms.Form):
    #condition = forms.ChoiceField(choices=DiseaseDefinition.get_all_condition_choices())
    #old code 
    #Condition.condition_choices(wildcard=True))
    pass

class ReferenceCaseForm(forms.Form):
    notes = forms.CharField(required=False, widget=forms.Textarea)
    ignore = forms.BooleanField(required=False)