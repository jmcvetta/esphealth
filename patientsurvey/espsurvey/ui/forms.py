'''
                               ESP Patient Self Survey

@authors: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics www.commoninf.com
@copyright: (c) 2014 cii
@license: LGPL
'''


from django import forms
from django.forms.util import ErrorList
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


from espsurvey.survey.models import GENDER, UNSURE
from espsurvey.survey.models import RACE, YES_NO_UNSURE,DIABETES_TYPE, WEIGHT_TYPE

from django.utils.safestring import mark_safe
from django.forms import CheckboxSelectMultiple, CheckboxInput
from django.utils.encoding import  force_unicode
from django.utils.html import escape, conditional_escape
from itertools import chain
from django.forms.widgets import RadioFieldRenderer, RadioInput


class CustomRadioInput(RadioInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        if 'id' in self.attrs:
            label_for = ' id="%s" for="%s"' % (self.attrs['id'], self.attrs['id'])
        else:
            label_for = ' id="%s" ' % ( self.attrs['id'])
            choice_label = conditional_escape(force_unicode(self.choice_label))
            return mark_safe(u'%s<label %s >%s</label>' % (self.tag(), label_for, choice_label))
        
class RadioCustomRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield CustomRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]
        return CustomRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)

    def render(self):
        
        return mark_safe(u'%s' % u'\n'.join([u'%s' % force_unicode(w) for w in self]))
            
class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))
    
class SimpleVerticalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):   
        
        return mark_safe(u'\n'.join([u'%s<br>\n' % w for w in self]))

class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<p>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<label%s>%s %s</label><br>' % (label_for, rendered_cb, option_label))
        output.append(u'</p>')
        return mark_safe(u'\n'.join(output))

class SurveyForm (forms.Form):
    '''
    Form for surveys 
    '''
    #notify_new_friends = forms.ChoiceField(label='Notify when new friends join', widget=forms.RadioSelect(renderer=RadioCustomRenderer), choices=YES_NO_UNSURE);
    age = forms.IntegerField( required=True, label='What is your age?')
    age.question = 4
    gender = forms.ChoiceField(GENDER, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label = 'What is your gender?')
    gender.question = 5
    
    race = forms.ChoiceField(RACE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label = 'What is your race/ethnicity?')
    #race = forms.ChoiceField( RACE, widget=MyCheckboxSelectMultiple(),  required=True, label = '3. What is your race/ethnicity?')
    race.question =6 
    systolic = forms.IntegerField( required=False, label='What was your blood pressure the last time it was measured by your doctor? ')
    systolic.question =7
    systolic.unsure = 'diastolic_unsure'
    diastolic = forms.IntegerField(required=False, label='/')
    diastolic.question =25
    diastolic.inline= True
    diastolic.unsure= 'diastolic_unsure'
    diastolic_unsure = forms.BooleanField(required=False, label = 'Unsure')
    diastolic_unsure.question =9
    diastolic_unsure.inline= True
    high_blood_pressure = forms.ChoiceField(YES_NO_UNSURE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label='Have you ever been diagnosed with high blood pressure?')
    high_blood_pressure.question =10
    meds_high_blood_pressure = forms.ChoiceField(YES_NO_UNSURE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label='Are you currently being prescribed medications for high blood pressure?')
    meds_high_blood_pressure.question =11
    diabetes = forms.ChoiceField(YES_NO_UNSURE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label='Do you have diabetes?')
    diabetes.question =12
    diabetes_type = forms.ChoiceField(DIABETES_TYPE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False, label='What kind of diabetes do you have?')
    diabetes_type.question =13
    diabetes_type.hidden =['diabetes_0','Y'] 
    diabetes_type.hidden_parent_type = diabetes
    a1c = forms.ChoiceField(YES_NO_UNSURE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label='Have you ever had your hemoglobin A1C level checked?')
    a1c.question =14
    a1c_value = forms.FloatField(  required=False, label='What was your most recent hemoglobin A1C value?')
    a1c_value.question =15
    a1c_value.hidden =['a1c_0','Y'] 
    a1c_value.hidden_parent_type = a1c
    a1c_value.unsure = 'a1c_unsure'
    a1c_unsure = forms.BooleanField(required=False,  label = 'Unsure')
    a1c_unsure.question =24
    a1c_unsure.inline= True
    a1c_unsure.hidden =['a1c_0','Y']
    a1c_unsure.hidden_parent_type = a1c
    height = forms.FloatField( required=False, label='What is your current height in Feet?')
    height.question =16
    height.unsure = 'height_unsure'
    height_unsure = forms.BooleanField(required=False,  label = 'Unsure')
    height_unsure.question =17
    height_unsure.inline= True
    weight = forms.FloatField( required=False, label='What is your current weight in pounds?')
    weight.question =26
    weight.unsure = 'weight_unsure'
    weight_unsure = forms.BooleanField(required=False,  label = 'Unsure')
    weight_unsure.question =18
    weight_unsure.inline= True
    weight_type = forms.ChoiceField(WEIGHT_TYPE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label='How would you classify your weight?')
    weight_type.question =19
    high_cholesterol = forms.ChoiceField(YES_NO_UNSURE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label='Do you have a history of hyperlipidemia or elevated cholesterol?')
    high_cholesterol.question =20
    ldl = forms.FloatField( required=False, label='What was your last LDL level?')
    ldl.question =21
    ldl.unsure = 'ldl_unsure'
    ldl_unsure = forms.BooleanField(required=False, label = 'Unsure')
    ldl_unsure.question =22
    ldl_unsure.inline= True
    meds_cholesterol = forms.ChoiceField(YES_NO_UNSURE, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True, label='Are you currently being prescribed medications for high cholesterol?')
    meds_cholesterol.question =23
        


