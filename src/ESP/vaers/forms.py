from django import forms

CASE_CONFIRMATION_CHOICES = (
    ('confirm', 'Confirm'),
    ('false_positive', 'Do not confirm. This case is a false positive'),
    ('wait', 'Wait')
)

class CaseConfirmForm(forms.Form):
    action = forms.ChoiceField(choices=CASE_CONFIRMATION_CHOICES, 
                               widget=forms.RadioSelect)
    comment = forms.CharField(widget=forms.Textarea, help_text='Please add any commentary or information that you would like to attach to the case report here. Comments for confirmed cases will be added to the final report, while comments on false positives will be used as feedback for our detection system.')
