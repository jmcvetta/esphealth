'''
                               ESP Patient Self Survey

@authors: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics www.commoninf.com
@copyright: (c) 2014 cii
@license: LGPL
'''

import datetime
import csv
#import django_tables as tables

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Q
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import redirect_to
from django.http import HttpResponse

from dateutil.relativedelta import relativedelta
from espsurvey.settings import ROWS_PER_PAGE, VERSION
from espsurvey.settings import PY_DATE_FORMAT
from espsurvey.settings import SITE_NAME
from espsurvey.settings import STATUS_REPORT_TYPE

from espsurvey.survey.models import Response
from espsurvey.survey.models import Survey
from espsurvey.survey.models import Participant
from espsurvey.survey.models import ParticipantActivity
from espsurvey.survey.models import Question
from espsurvey.ui.forms import SurveyForm

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 
# All views must pass "context_instance=RequestContext(request)" argument 
# to render_to_response().
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

################################################################################
#
#--- Status Report
#
################################################################################
RELATED_MARGIN = 400

def _populate_status_values():
    '''
    Utility method to populate values dict for use with status_page() view and
    manage.py status_report command.
    '''
    today_string = datetime.datetime.now().strftime(PY_DATE_FORMAT)
    #yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    values1 = {}
    values2 = {}
    values = {
            'type': STATUS_REPORT_TYPE,
            'title': _('Patient Self-Report Survey'),
            'today_string': today_string,
            'site_name': SITE_NAME,
            'version': VERSION,
            }
    values.update(values1)
    values.update(values2)     
    return values

def thanks_for_survey(request):
    '''
    thank you page main survey.
    '''
    values = _populate_status_values()
     
    return render_to_response('ui/thanks_for_survey.html', values, context_instance=RequestContext(request))

@login_required
def survey_admin(request):
    admin = True
    return prepare_survey(request, admin)

def launch_survey(request):
    
    return prepare_survey(request, False)
    
def prepare_survey(request, admin):
    '''
    Launching main survey.
    '''
    values = _populate_status_values()
    if admin:
        values['admin'] = True
     
    #loads all the questions from survey question and let user save. 
    values['surveys'] = Response.create_survey()
       
    return render_to_response('ui/launch_survey.html', values, context_instance=RequestContext(request))

SURVEY_FILLED_OUT = 'It appears that you have already completed this survey. Thank you.  If you believe that you have not completed the survey, please speak to the survey organizer.'
CANNOT_FIND_MRN = 'I am sorry, I cannot find a record of your medical record number in the electronic medical record.  Please try re-entering your medical record number'
NO_SURVEY_QUESTION  = 'I am sorry, I cannot find this question in the survey. Please speak to the survey organizer'

def enter_survey(request):
    '''
    enter main survey.
    '''
    values = _populate_status_values()
    mrn = str(request.POST.getlist('mrn')[0])
    surveyid = str(request.POST.getlist('surveyid')[0])
    error_message = None
   
    #loads all the questions from survey question and let user save. 
    values['surveys'] = Response.create_survey()
    form  = SurveyForm(auto_id=True)
    values['form'] = form
    values['mrn'] =  mrn
    values['surveyid'] = surveyid
    participant_id = Participant.objects.filter(login = mrn).values_list('id', flat=True)
    #checking if there are rows for survey and participant
    if participant_id :
        participant_id= participant_id[0]
        if ParticipantActivity.objects.filter(participant__id =participant_id, survey__id = surveyid, completed=True):
            error_message =SURVEY_FILLED_OUT        
    else:
        if not participant_id:
            error_message = CANNOT_FIND_MRN
    
    values ['error_message'] = error_message 
    if error_message:
        return render_to_response('ui/thanks_for_survey.html', values, context_instance=RequestContext(request))
    
    return render_to_response('ui/enter_survey.html', values, context_instance=RequestContext(request))

def save_survey_response(request):
    '''
    saves responses from survey pass in REQUEST
    '''
    mrn = str(request.POST.getlist('mrn')[0])
    surveyid = str(request.POST.getlist('surveyid')[0])
    form = SurveyForm(auto_id=True)
    error_message= None
    participant = Participant.objects.filter(login = mrn)
    survey = Survey.objects.filter(id = surveyid)
    #checking if there are rows for survey and participant
    if not participant or not survey:
        error_message = CANNOT_FIND_MRN
        
    if request.method == 'POST' and not error_message:
        form = SurveyForm(request.POST)
        if form.is_valid(): 
            if ParticipantActivity.objects.filter(participant =participant[0], survey = survey[0], completed=True):
                error_message =SURVEY_FILLED_OUT
            else:
                for name, field in form.fields.items():
                    question = Question.objects.filter(id = field.question) #or get by short name
                    if not question:
                        error_message = NO_SURVEY_QUESTION
                        continue
                    response, created = Response.objects.get_or_create(survey = survey[0],  question = question[0], participant = participant[0])
                    answer = form.cleaned_data[name]
                    if field.__class__.__name__ == 'ChoiceField' :
                        response.response_choice = answer
                    elif field.__class__.__name__ == 'CharField': 
                        response.response_string = answer
                    elif field.__class__.__name__ == 'FloatField' :
                        response.response_float = answer
                    elif field.__class__.__name__ == 'BooleanField':
                        response.response_boolean = answer
                    elif field.__class__.__name__ == 'IntegerField' :
                        response.response_float = answer
                    response.save()
                    if created:
                        msg = 'Saved survey question : %s' % response
                    else:
                        msg = 'Updated survey question: %s' % response
                    #request.user.message_set.create(message=msg)
                    print(msg)
                pact, created = ParticipantActivity.objects.get_or_create(survey = survey[0],  participant= participant[0], completed = True )
                pact.save()
                #return redirect_to(request,  reverse('thanks_for_survey'))
        else:
            error_message = 'Some of your survey responses do not seem right. Please see below for errors (highlighted in red).' 
            
            #form.cleaned_data to clear fields or show survey again
    values = _populate_status_values()
    values ['error_message'] = error_message
    values ['form'] = form
    values ['mrn'] = mrn
    values ['surveyid'] = surveyid
    if error_message:
            return render_to_response('ui/enter_survey.html', values, context_instance=RequestContext(request))
    else:
        return render_to_response('ui/thanks_for_survey.html', values, context_instance=RequestContext(request))
    
    '''
    if not responses:
        msg = 'Responses not understood: no answered questions from survey'
        request.user.message_set.create(message=msg)
        return redirect_to(request, reverse('launch_survey'))
    
    for res in responses:
      
        #TODO get the participant
        ic_obj, created = Response.objects.get_or_create(survey_id =survey.id, participant_id = 1 , question =res.id , response_string= res)
        if created:
            ic_obj.save()
            msg = 'Response "%s" has been added to the Survey' % res
        else:
            msg = 'Response "%s" is already on the survey' % res
        request.user.message_set.create(message=msg)
        log.debug(msg)
    return launch_survey(request)
    '''