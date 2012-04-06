from django import forms

CASE_CONFIRMATION_CHOICES = (
    ('confirm', 'Confirm'),
    ('false_positive', 'Do not confirm. This case is a false positive'),
    ('wait', 'Wait')
    
)

CASE_RESPONSE_CHOICES = (
    ('confirm', 'Yes, submit an adverse event report (with optional comments)'),
    ('false_positive', 'No, diagnosis not related to vaccination'),
    
)

CASE_YESNO_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
    
)

CASE_TYPE_CHOICES = (
    ('rare', 'Too Rare'),
    ('approp', 'Appropriate'),
    ('frequent', 'Too Frequent'),
)

class CaseConfirmFormold(forms.Form):
    action = forms.ChoiceField(choices=CASE_CONFIRMATION_CHOICES, 
                               widget=forms.RadioSelect)
    comment = forms.CharField(widget=forms.Textarea)
    
class CaseConfirmForm(forms.Form):   
    
    action = forms.ChoiceField(label = 'Probable Adverse Event?',choices=CASE_RESPONSE_CHOICES, 
                               widget=forms.RadioSelect)
    comment = forms.CharField(label = 'Please provide details so that we can refine our adverse event detection algorithms (optional)',
                                widget=forms.Textarea)
    ishelpful = forms.ChoiceField(label = 'Please help us assess this automated adverse event reporting facility. Was this message helpful?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    interrupts = forms.ChoiceField(label = 'Did this message interrupt your work flow?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    messagetype =  forms.ChoiceField(label = 'Over the past month, the messages have been', choices=CASE_TYPE_CHOICES, 
                               widget=forms.RadioSelect)
     
