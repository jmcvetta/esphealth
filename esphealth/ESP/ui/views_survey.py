'''
                               ESP Health Project
                             User Interface Module
                                     Views

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''

import datetime
import csv
import django_tables as tables
import os
from ESP.settings import TOPDIR

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
from ESP.settings import ROWS_PER_PAGE
from ESP.settings import PY_DATE_FORMAT
from ESP.settings import SITE_NAME
from ESP.settings import STATUS_REPORT_TYPE
from ESP.ui.views import _populate_status_values

#from ESP.hef import events # Required to register hef events
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.models import Case
from ESP.nodis.models import CaseStatusHistory
from ESP.nodis.models import Report
from ESP.nodis.models import ReferenceCase
from ESP.nodis.models import ValidatorRun
from ESP.nodis.models import ValidatorResult
from ESP.vaers.heuristics import VaersLxHeuristic
from ESP.ui.forms import CaseStatusForm
from ESP.ui.forms import CodeMapForm
from ESP.ui.forms import ConditionForm
from ESP.ui.forms import ReferenceCaseForm
#from ESP.ui.management.commands.validate_cases import RELATED_MARGIN
from ESP.utils import log
from ESP.utils import log_query
from ESP.utils import TableSelectMultiple


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

@login_required
def status_page(request):
    '''
    View returning a status report page.
    '''
    values = _populate_status_values()
    return render_to_response('ui/status.html', values, context_instance=RequestContext(request))

def survey_import(request):
    '''
    importing responses from survey app.
    '''
    
    cursor = connection.cursor()
    cursor.execute("COPY emr_surveyresponse ( provenance_id,\"created_timestamp\",updated_timestamp,mrn,question,response_float,response_string,response_choice,response_boolean,date ) FROM '/srv/esp-data/surveyresponse.copy'  WITH  DELIMITER  ',' CSV  HEADER")
    
    values = _populate_status_values()
    values['comment'] = 'Survey Responses successfully imported'
    
    return render_to_response('ui/status.html', values, context_instance=RequestContext(request))

def survey_report(request):
    
    '''
    survey report tables from running a query
    '''
    
    cursor = connection.cursor()    
    sqlfile =  os.path.join(TOPDIR+"/surveys/", 'newsurveyreport.sql')
    f = open(sqlfile)
    sql = f.read()
    f.close()
    response = cursor.execute(sql)
    
    values = _populate_status_values()
    values['title'] = 'BRFSS Results'
    values['subtitle'] = 'ESP Survey vs EHR report'
    
    cursor.execute("select question as \"Questions\", noofrespondents as \"No. of Respondents\", NoOfEHRRespondents as \"No. of EHR Respondents\", selfreportmean::text   as \"Self-Report Mean\",  ' +/- ' || selfreportsd::text  as \"SD\", "+
        " EHRReportMean::text  as \"EHR Mean\",  ' +/- ' || EHRReportSD::text as \"SD\"  from ContinuousVariables where selfreportmean>0")
    desc = cursor.description
    rows = cursor.fetchall() 

    values['table1title'] = 'Continuous variables'
    values['tableheader1'] = desc
    values['tablecontent1'] = rows 
    
    cursor.execute("select Question, NoOfRespondents as \"No. of Respondents\", PtYes as \"Pt Yes\",PTNo  as \"Pt No\",    EHRYes as \"EHR Yes\",  EHRNo as \"EHR No\" ,"+
        "PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\","+
        "PtUnsureEHRYes as \"Pt Unsure / EHR Yes\", PtUnsureEHRNo as \"Pt Unsure / EHR Yes\" from YesNoUnsureQuestions order by question;")
    desc = cursor.description
    rows = cursor.fetchall() 
    
    values['table2title'] = 'Yes / No / Unsure Questions'
    values['tableheader2'] = desc
    values['tablecontent2'] = rows 
    
    cursor.execute("select  RaceEthnicity as \"Race-Ethnicity\" , SelfReportYes as \"Self-Report Yes\",SelfReportNo  as \"Self-Report No\","+  
      "EHRYes as \"EHR Yes\",  EHRNo as \"EHR No\" ,PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", "+
      "PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\" from CategoricalVariables;")
    desc = cursor.description
    rows = cursor.fetchall() 
    
    values['table3title'] = 'Categorical variables'
    values['tableheader3'] = desc
    values['tablecontent3'] = rows 
    
    cursor.execute("select type as \"Diabetes Type\", SelfReportYes as \"Self-Report Yes\",SelfReportNo  as \"Self-Report No\", EHRYes as \"EHR Yes\","+
       "EHRNo as \"EHR No\" ,PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", "+
       "PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\" from DiabetesType;")
    desc = cursor.description
    rows = cursor.fetchall() 

    values['table4title'] = 'What type of diabetes do you have?'
    values['tableheader4'] = desc
    values['tablecontent4'] = rows 
    
    cursor.execute("select type as \"BMI Category\", SelfReportYes as \"Self-Report Yes\",SelfReportNo  as \"Self-Report No\",  EHRYes as \"EHR Yes\", "+
      "EHRNo as \"EHR No\" ,EHRMissing as \"EHR Missing\",PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", "+
      "PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\", ptyesehrmissing as \"Pt Yes / EHR Missing\", ptnoehrmissing as \"Pt No / EHR Missing\" from WeightType;")
    desc = cursor.description
    rows = cursor.fetchall() 

    values['table5title'] = 'How would you classify your weight?'
    values['tableheader5'] = desc
    values['tablecontent5'] = rows 
   
    return render_to_response('ui/survey_report.html', values, context_instance=RequestContext(request))

