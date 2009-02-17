'''
Forms for the ESP Health Project
'''
from django import forms
from ESP.esp import models

class ExtLoincForm(forms.Form):
    ext_code = forms.CharField(max_length=100, required=True)
    ext_name = forms.CharField(max_length=255, required=False)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc_num = forms.CharField(max_length=100, required=True)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    