from django import forms

CASE_CONFIRMATION_CHOICES = (
    ('confirm', 'Confirm'),
    ('false_positive', 'Do not confirm. This case is a false positive'),
    ('wait', 'Wait')
    
)

CASE_RESPONSE_CHOICES = (
    ('confirm', 'Yes, it is possible that this event is due to an adverse effect of a vaccine, submit an adverse event report (with optional comments)'),
    ('false_positive', 'No, it is unlikely that the new diagnosis is related to the vaccine'),
    
)

CASE_YESNO_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
    
)

CASE_TYPE_CHOICES = (
    ('approp', 'Appropriate'),
    ('frequent', 'Too Frequent'),
    ('rare', 'Too Rare'),
)
   
class CaseConfirmForm(forms.Form):   
    
    state = forms.ChoiceField(label = 'Possible Adverse Event?',choices=CASE_RESPONSE_CHOICES, 
                               widget=forms.RadioSelect)
    
    comment = forms.CharField(label = 'Please provide details so that we can refine our adverse event detection algorithms (optional)',
                                widget=forms.Textarea)
    
    message_ishelpful = forms.ChoiceField(label = 'Please help us assess this automated adverse event reporting facility. Was this message helpful?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    interrupts_work = forms.ChoiceField(label = 'Did it interrupt your work flow?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    satisfaction_num_msg =  forms.ChoiceField(label = 'Has the number of messages recently been', choices=CASE_TYPE_CHOICES, 
                               widget=forms.RadioSelect)
     
