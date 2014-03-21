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
    
    cursor.execute("CREATE TEMPORARY TABLE ContinuousVariables(    Question   VARCHAR(80),    NoOfRespondents INTEGER,   SelfReportMean  DECIMAL(7,2), " +
        " SelfReportSD  DECIMAL(7,2),  EHRReportMean  DECIMAL(7,2),  EHRReportSD  DECIMAL(7,2))")
    cursor.execute("INSERT INTO ContinuousVariables(   Question  ,   NoOfRespondents ,SelfReportMean ,SelfReportSD )  select question, count(mrn) " +
        " as \"No. of Respondents\",Round( avg(response_float)::numeric,2) as \"Self-Report Mean\",round( stddev(response_float)::numeric,2) as " +
        " \"+- SD\" from emr_surveyresponse where  response_float is not null group by question")
    cursor.execute("update ContinuousVariables set EHRReportMean= (select round(avg(date_part('year',age(emr_surveyresponse.date, date_of_birth)) )::numeric,2) " + 
        " from emr_patient , emr_surveyresponse where emr_patient.mrn = emr_surveyresponse.mrn and question ='What is your age?'), " +
        " EHRReportSD=(select round(stddev(date_part('year',age(emr_surveyresponse.date, date_of_birth)) )::numeric,2) from emr_patient , emr_surveyresponse " +
        " where emr_patient.mrn = emr_surveyresponse.mrn and question ='What is your age?') where Question ='What is your age?'")
    cursor.execute("select question as \"Questions\", noofrespondents as \"No. of Respondents\",  selfreportmean::text   as \"Self-Report Mean\",  ' +/- ' || selfreportsd::text  as \"SD\", "+
        " EHRReportMean::text  as \"EHR Mean\",  ' +/- ' || EHRReportSD::text as \"SD\"  from ContinuousVariables where selfreportmean>0")
        
    
    sqlfile =  os.path.join(TOPDIR+"/surveys/", 'surveyreport.sql')
    #sqlfile =  os.path.join(TOPDIR+"/surveys/", 'test.sql')
    f = open(sqlfile)
    #response = cursor.execute(f.read())
    f.close()
    cursor.execute("select question as \"Questions\", noofrespondents as \"No. of Respondents\",  selfreportmean::text   as \"Self-Report Mean\",  ' +/- ' || selfreportsd::text  as \"SD\", "+
        " EHRReportMean::text  as \"EHR Mean\",  ' +/- ' || EHRReportSD::text as \"SD\"  from ContinuousVariables where selfreportmean>0")
    
    desc = cursor.description
    rows = cursor.fetchall() 

    values = _populate_status_values()
    values['title'] = 'BRFSS Results'
    values['subtitle'] = 'ESP Survey vs EHR report'
    values['table1title'] = 'Continuous variables'
    values['tableheader'] = desc
    values['tablecontent'] = rows 
   
    return render_to_response('ui/survey_report.html', values, context_instance=RequestContext(request))

