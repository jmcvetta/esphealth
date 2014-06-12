'''
                               ESP Health Project
                             User Interface Module
                                     Views

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''

import datetime, time
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
from django.core.servers.basehttp import FileWrapper

from dateutil.relativedelta import relativedelta
from ESP.settings import ROWS_PER_PAGE
from ESP.settings import PY_DATE_FORMAT
from ESP.settings import SITE_NAME
from ESP.settings import DATA_DIR
from ESP.settings import STATUS_REPORT_TYPE
from ESP.ui.views import _populate_status_values
from ESP.emr.models import SurveyReports

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
    cursor.execute("TRUNCATE emr_surveyresponse CASCADE")
    connection.connection.commit()
    cursor.execute("COPY emr_surveyresponse ( provenance_id, survey_id, \"created_timestamp\" , \"updated_timestamp\" ,mrn,question,response_float,response_string,response_choice,response_boolean,date ) FROM '/srv/esp-data/surveyresponse.copy'  WITH  DELIMITER  ',' CSV  HEADER")
    connection.connection.commit()
    values = _populate_status_values()
    values['comment'] = 'Survey Responses successfully imported, please import them from the survey app'
    
    return render_to_response('ui/status.html', values, context_instance=RequestContext(request))

def view_survey_report(request): 
    
    filename=DATA_DIR+"survey_report.csv"
    try: 
        vfile=open(filename,'r')       
    
    except:
        values = _populate_status_values()
        values['comment'] = 'The %s file was not found, please generate the report first. ' % filename
        return render_to_response('ui/status.html', values, context_instance=RequestContext(request))
    
    response = HttpResponse(FileWrapper(vfile), content_type='application/csv')
    response['Content-Disposition'] = 'attachment;filename=survey_report.csv'
    return response


def write_survey_report (title, desc, rows, writer):
    header = []
    writer.writerow([title])
    for description in desc:
        header.append(description.name)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    writer.writerow('')
        

        
def generate_survey_report(request):
    
    '''
    survey report tables from running a query
    '''
    #set the db flag to running 
    survey_id = 1
    survey_report = SurveyReports.objects.filter(survey_id__exact = survey_id)
    sr = None
    if  not survey_report:
        sr = SurveyReports(  survey_id = survey_id ,  running =True )
        sr.save()
    elif not survey_report[0].running and datetime.datetime.date(survey_report[0].date) <> datetime.datetime.now().date():
        survey_report[0].running = True
        survey_report[0].date = datetime.datetime.now()
        survey_report[0].save()
    else:
        values = _populate_status_values()       
        values['comment'] = 'Survey Responses report already generated today or is running. Please wait until completion or select: View Last BRFSS Demo from: Survey Results menu option '
        return render_to_response('ui/status.html', values, context_instance=RequestContext(request))
        
    cursor = connection.cursor()    
     
    sqlfile =  os.path.join(TOPDIR+"/surveys/", 'newsurveyreport.sql')
    f = open(sqlfile)
    sql = f.read()
    f.close()
        
    response = cursor.execute(sql)
        
    file_path = os.path.join(DATA_DIR,  'survey_report.csv')
    file_handle = open(file_path, 'w')
    writer = csv.writer(file_handle, dialect='excel')
        
    cursor.execute("select question as \"Questions\", noofrespondents as \"No. of Respondents\", NoOfEHRRespondents as \"No. of EHR Respondents\", selfreportmean::text   as \"Self-Report Mean\",  ' +/- ' || selfreportsd::text  as \"SD\", "+
            " EHRReportMean::text  as \"EHR Mean\",  ' +/- ' || EHRReportSD::text as \"SD\"  from ContinuousVariables where selfreportmean>0")
    write_survey_report('Continuous variables', cursor.description, cursor.fetchall() , writer)
        
    cursor.execute("select Question, NoOfRespondents as \"No. of Respondents\", PtYes as \"Pt Yes\",PTNo  as \"Pt No\", PtUnsure as \"Pt Unsure\",  EHRYes as \"EHR Yes\",  EHRNo as \"EHR No\" ,"+
            "PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\","+
            "PtUnsureEHRYes as \"Pt Unsure / EHR Yes\", PtUnsureEHRNo as \"Pt Unsure / EHR Yes\" from YesNoUnsureQuestions order by question;")
    write_survey_report('Yes / No / Unsure Questions',cursor.description, cursor.fetchall() , writer)
            
    cursor.execute("select  RaceEthnicity as \"Race-Ethnicity\" , SelfReportYes as \"Self-Report Yes\",SelfReportNo  as \"Self-Report No\","+  
          "EHRYes as \"EHR Yes\",  EHRNo as \"EHR No\" ,PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", "+
          "PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\" from CategoricalVariables;")
    write_survey_report('Categorical variables',cursor.description, cursor.fetchall() , writer)
           
    cursor.execute("select type as \"Diabetes Type\", SelfReportYes as \"Self-Report Yes\",SelfReportNo  as \"Self-Report No\", EHRYes as \"EHR Yes\","+
           "EHRNo as \"EHR No\" ,PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", "+
           "PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\" from DiabetesType;")
    write_survey_report('What type of diabetes do you have?', cursor.description, cursor.fetchall() , writer)
        
    cursor.execute("select type as \"BMI Category\", SelfReportYes as \"Self-Report Yes\",SelfReportNo  as \"Self-Report No\",  EHRYes as \"EHR Yes\", "+
          "EHRNo as \"EHR No\" ,EHRMissing as \"EHR Missing\",PtYesEHRYes as \"Pt Yes / EHR Yes\", PtYesEHRNo as \"Pt Yes / EHR No\", "+
          "PtNoEHRYes as \"Pt No / EHR Yes\", PtNoEHRNo as \"Pt No / EHR No\", ptyesehrmissing as \"Pt Yes / EHR Missing\", ptnoehrmissing as \"Pt No / EHR Missing\" from WeightType;")
    write_survey_report('How would you classify your weight?', cursor.description, cursor.fetchall() , writer)
        
    cursor.execute("select * from LineList;")
    write_survey_report('Line List', cursor.description, cursor.fetchall() , writer)
    if not survey_report:
        sr.running = False
        sr.save()
    else:
        survey_report[0].running = False
        survey_report[0].save()
    

    values = _populate_status_values()       
    values['comment'] = 'Survey Responses successfully generated, please select: View Last BRFSS Demo from: Survey Results menu option'
    
    return render_to_response('ui/status.html', values, context_instance=RequestContext(request))
   
