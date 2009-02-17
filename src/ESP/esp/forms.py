'''
Forms for the ESP Health Project
'''

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from ESP.esp import models
from ESP.utils.utils import log


class ExtLoincForm(forms.Form):
    ext_code = forms.CharField(max_length=100, required=True)
    ext_name = forms.CharField(max_length=255, required=False)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc_num = forms.CharField(max_length=100, required=True)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    
    def clean_ext_code(self):
        ext_code = self.cleaned_data['ext_code']
        log.debug('ext_code: %s' % ext_code)
        existing = models.ExternalToLoincMap.objects.filter(ext_code=ext_code)
        if len(existing) > 0:
            msg = _('Each code may be mapped to only one LOINC, and this code is already mapped to LOINC %s.' % existing[0].loinc.loinc_num)
            raise forms.ValidationError(msg)
        return ext_code
    