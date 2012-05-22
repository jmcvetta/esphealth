from django import forms

CASE_CONFIRMATION_CHOICES = (
    ('confirm', 'Confirm'),
    ('false_positive', 'Do not confirm. This case is a false positive'),
    ('wait', 'Wait')
    
)

CASE_RESPONSE_CHOICES = (
    ('confirm', 'Yes, submit the adverse event report to CDC/FDA'),
    ('false_positive', 'No'),
    
)

CASE_YESNO_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
    
)

CASE_TYPE_CHOICES = (
    ('approp', 'Appropriate'),
    ('frequent', 'Too Frequent')
)
   
class CaseConfirmForm(forms.Form):   
    
    state = forms.ChoiceField(label = 'Possible Adverse Event?',choices=CASE_RESPONSE_CHOICES, 
                               widget=forms.RadioSelect)
    
    #for yes : Please comment on the likelihood and severity of this possible event:
    #TODO For no: Please provide details so that we can refine our adverse event detection algorithms

    comment = forms.CharField(label = 'Please comment on the likelihood and severity of this possible event:',
                               widget=forms.Textarea )
    
    label = forms.CharField(label = 'Please help us assess this automated adverse event reporting tool.' )
    
    message_ishelpful = forms.ChoiceField(label = 'Was this message helpful?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    interrupts_work = forms.ChoiceField(label = 'Did it interrupt your work flow?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    satisfaction_num_msg =  forms.ChoiceField(label = 'Has the number of messages recently been', choices=CASE_TYPE_CHOICES, 
                               widget=forms.RadioSelect)
     
    def __init__(self, *args, **kwargs):
        super(CaseConfirmForm, self).__init__(*args, **kwargs) # Call to constructor
        self.fields['comment'].widget.attrs['cols'] = 10
        self.fields['comment'].widget.attrs['rows'] = 10
