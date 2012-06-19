from django import forms
#TODO: I think this should be ModelForm so that the form values reflect the data model
#See Creating forms from models

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
    
    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': '55', 'rows': '5'}))
    
    message_ishelpful = forms.ChoiceField( label = 'Was this message helpful?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    interrupts_work = forms.ChoiceField(label = 'Did it interrupt your work flow?', choices=CASE_YESNO_CHOICES, 
                               widget=forms.RadioSelect)
    satisfaction_num_msg =  forms.ChoiceField(label = 'Has the number of messages recently been', choices=CASE_TYPE_CHOICES, 
                               widget=forms.RadioSelect)
     
   