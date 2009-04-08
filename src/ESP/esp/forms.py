'''
Forms for the ESP Health Project
'''

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from ESP.esp import models
from ESP.utils.utils import log

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30, widget=forms.PasswordInput)


class ExtLoincForm(forms.Form):
    native_code = forms.CharField(max_length=100, required=True)
    native_code = forms.CharField(max_length=255, required=False)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc_num = forms.CharField(max_length=100, required=True)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    
    def clean_native_code(self):
        native_code = self.cleaned_data['native_code']
        log.debug('native_code: %s' % native_code)
        existing = models.NativeToLoincMap.objects.filter(native_code=native_code)
        if len(existing) > 0:
            msg = _('Each code may be mapped to only one LOINC, and this code is already mapped to LOINC %s.' % existing[0].loinc.loinc_num)
            raise forms.ValidationError(msg)
        return native_code
    
