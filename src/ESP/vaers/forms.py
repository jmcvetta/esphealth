from django import forms

CASE_CONFIRMATION_CHOICES = (
    ('confirm', 'Confirm'),
    ('false_positive', 'Do not confirm. This case is a false positive'),
    ('wait', 'Wait')
)

class CaseConfirmForm(forms.Form):
    action = forms.ChoiceField(choices=CASE_CONFIRMATION_CHOICES, 
                               widget=forms.RadioSelect)
    comment = forms.CharField(widget=forms.Textarea)
