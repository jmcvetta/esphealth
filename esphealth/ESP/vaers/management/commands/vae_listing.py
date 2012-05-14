#!/usr/bin/env python
'''
                                  ESP Health
                                VAERS Listing
                              Command Line Runner


@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc. http://www.commoninf.com
@copyright: (c) 2012 Commonwealth Informatics Inc.
@license: LGPL
'''

import csv, re

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from datetime import date
from dateutil.relativedelta import relativedelta
from ESP.vaers.models import Case
from ESP.emr.models import Provider
from ESP.static.models import Icd9
from ESP.settings import VAERS_LINELIST_PATH

def vaers_csv(no_phi):
    '''
    Creates a linelist CSV file of all vaers data
    the parameter no_phi is a boolean value for keeping or obscuring phi
    if no_phi is true, phi is obscured
    '''
    fpath=VAERS_LINELIST_PATH
    case_qs=Case.objects.all()
    obsc='PHI'
    if no_phi:
        vfile=open(fpath+"vaers_linelist_nophi.csv",'w')
    else:
        vfile=open(fpath+"vaers_linelist_phi.csv",'w')        
    #rebuild each time
    vfile.truncate()
    #this has to be parameterized.
    writer = csv.writer(vfile, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(['Case_id',
              'MRN',
              'Name',    
              'DOB',     
              'Age',     
              'Gender',    
              'Practice', 
              'Vaccine provider',   
              'Vaccination_date',
              'Vaccine_name_1',
              'Vaccine_Lot_no_1',    
              'Vaccine_name_2',
              'Vaccine_Lot_no_2',    
              'Vaccine_name_3',
              'Vaccine_Lot_no_3',    
              'Vaccine_name_4',
              'Vaccine_Lot_no_4',    
              'Vaccine_name_5',
              'Vaccine_Lot_no_5',  
              'Immunization_count',  
              'Event_name1',
              'Reporting_clinician_name1',
              'Action_category1',
              'Event_name2',
              'Reporting_clinician_name2',
              'Action_category2',
              'Event_name3',
              'Reporting_clinician_name3',
              'Action_category3',
              'Event_name4',
              'Reporting_clinician_name4',
              'Action_category4',
              'Event_name5',
              'Reporting_clinician_name5',
              'Action_category5',
              'AE_Count',
              'Lab_result_name1',    
              'Lab_result_date1',
              'Lab_result_text1',    
              'Lab_result_value1',    
              'Lab_result_name2',    
              'Lab_result_date2',
              'Lab_result_text2',    
              'Lab_result_value2',    
              'Lab_result_name3',    
              'Lab_result_date3',
              'Lab_result_text3',    
              'Lab_result_value3',    
              'Lab_result_name4',    
              'Lab_result_date4',
              'Lab_result_text4',    
              'Lab_result_value4',    
              'Lab_result_name5',    
              'Lab_result_date5',
              'Lab_result_text5',    
              'Lab_result_value5', 
              'Lab_count',   
              'ICD9_result_date1',
              'ICD9_result_text1',
              'ICD9_result_code1',
              'ICD9_result_date2',
              'ICD9_result_text2',
              'ICD9_result_code2',
              'ICD9_result_date3',
              'ICD9_result_text3',
              'ICD9_result_code3',
              'ICD9_result_date4',
              'ICD9_result_text4',
              'ICD9_result_code4',
              'ICD9_result_date5',
              'ICD9_result_text5',
              'ICD9_result_code5',
              'ICD9_count',
              'Fever_date1',
              'Fever_temp1',
              'Fever_date2',
              'Fever_temp2',
              'Fever_date3',
              'Fever_temp3',
              'Fever_date4',
              'Fever_temp4',
              'Fever_date5',
              'Fever_temp5',
              'Fever_count',
              'Prescription_date1',
              'Prescription_name1',
              'Prescription_dose_freq_dur1',
              'Prescription_date2',
              'Prescription_name2',
              'Prescription_dose_freq_dur2',
              'Prescription_date3',
              'Prescription_name3',
              'Prescription_dose_freq_dur3',
              'Prescription_date4',
              'Prescription_name4',
              'Prescription_dose_freq_dur4',
              'Prescription_date5',
              'Prescription_name5',
              'Prescription_dose_freq_dur5',
              'Prescription_count',
              'Pysician_notified1',
              'Workflow_status1',
              'Clinical_comment1',  
              'Message_ishelpful1',
              'Message_interuptswork1',
              'Pysician_notified2',
              'Workflow_status2',
              'Clinical_comment2',  
              'Message_ishelpful2',
              'Message_interuptswork2',
              'Pysician_notified3',
              'Workflow_status3',
              'Clinical_comment3',  
              'Message_ishelpful3',
              'Message_interuptswork3',
              'Pysician_notified4',
              'Workflow_status4',
              'Clinical_comment4',  
              'Message_ishelpful4',
              'Message_interuptswork4',
              'Pysician_notified5',
              'Workflow_status5',
              'Clinical_comment5',  
              'Message_ishelpful5',
              'Message_interuptswork5',
              'Message_count',
        ])
    for case in case_qs:
        immunization_qs = case.immunizations.all()
        patient = case.patient
        mrn = patient.mrn
        fullname = patient.last_name + ', ' + patient.first_name
        dob = patient.date_of_birth
        age = patient.age.years
        provider=Provider.objects.get(id=immunization_qs[0].provider_id)
        pname=provider._get_name()
        vaccdate=immunization_qs[0].date
        if no_phi:
            mrn = obsc
            fullname = obsc
            if relativedelta(date.today(), dob).years >= 90:
                dob = None 
            else:
                dob = (patient.date_of_birth).year
            if age > 90: 
                age = 90
            pname = obsc
            vaccdate=vaccdate.year
        #here is the immunization array
        immuarray=[]
        for imm in immunization_qs:
            immuarray.append(imm.name) 
            immuarray.append(imm.lot)
        nimmu=len(immuarray)/2
        while len(immuarray) < 10:
            immuarray.append(None)
        aearray = []
        dxarray = []
        rxarray = []
        lbarray = []
        alarray = []
        fevarray = []
        vaers_qs=case.adverse_events.distinct()
        for AE in vaers_qs:
            aearray.append(AE.name)
            if no_phi:
                aearray.append(obsc)
            else:
                aearray.append(AE.provider())
            aearray.append(AE.category)
            types = ContentType.objects.get_for_id(AE.content_type_id).model
            if types.startswith('encounter') and AE.name.find('Fever')==-1: 
                icd9codes = AE.matching_rule_explain.split()
                for icd9code in icd9codes:
                    if re.search(r'[0-9]',icd9code):
                        if no_phi:
                            dxdate = AE.encounterevent.date.year
                        else:
                            dxdate = AE.encounterevent.date
                        dxarray.append(dxdate)
                        dxarray.append(Icd9.objects.filter(code=icd9code)[0].name)
                        dxarray.append(icd9code)
            elif types.startswith('encounter') and AE.name.find('Fever')>-1:
                if no_phi:
                    fvdate = AE.encounterevent.date.year
                else:
                    fvdate = AE.encounterevent.date
                fevarray.append(fvdate)
                fevarray.append(AE.encounterevent.VAERS_FEVER_TEMPERATURE)
            elif types.startswith('prescription'):    
                rx = AE.prescriptionevent.content_object
                if no_phi:
                    rxarray.append(rx.date.year)
                else:
                    rxarray.append(rx.date)
                rxarray.append(rx.name)
                rxarray.append(rx.directions)
            elif types.startswith('labresult'):
                labs = AE.labresultevent.content_object
                lbarray.append(labs.native_name)
                if no_phi:
                    lbarray.append(labs.result_date.year)
                else:
                    lbarray.append(labs.result_date)
                lbarray.append(labs.result_string)
                lbarray.append(labs.result_float)
            elif types.startswith('allergy'):
                allergies = AE.allergyevent.allergy.allergyevent_set.all()
                for allrgy in allergies:
                    if no_phi:
                        alarray.append(allrgy.allergy.date.year)
                    else:
                        alarray.append(allrgy.allergy.date)
                    alarray.append(allrgy.allergy.allergen)
                    alarray.append(allrgy.allergy.description)
        nae=len(aearray)/3
        while len(aearray) < 15:
            aearray.append(None)
        nlab=len(lbarray)/4
        while len(lbarray) < 20:
            lbarray.append(None)
        ndx=len(dxarray)/3
        while len(dxarray) < 15:
            dxarray.append(None)
        nfv=len(fevarray)/2
        while len(fevarray) < 10:
            fevarray.append(None)
        nrx=len(rxarray)/3    
        while len(rxarray) < 15:
            rxarray.append(None)
        while len(alarray) < 0:
            alarray.append(None)
        qarray=[]
        ques_qs=case.questionaire_set.all()
        for ques in ques_qs:
            if no_phi:
                qarray.append(obsc)
            else:    
                qarray.append(ques.provider)
            qarray.append(ques.state)
            if no_phi:
                qarray.append(obsc)
            else:    
                qarray.append(ques.comment)
            qarray.append(ques.message_ishelpful)
            qarray.append(ques.interrupts_work)
        nques=len(qarray)/5
        while len(qarray) < 25:
            qarray.append(None)
        row = [case.id,
               mrn,
               fullname,    
               dob,     
               age,     
               patient.gender,    
               provider.dept,    
               pname,
               vaccdate,
               immuarray[0],    
               immuarray[1],
               immuarray[2],    
               immuarray[3],    
               immuarray[4],    
               immuarray[5],    
               immuarray[6],    
               immuarray[7],    
               immuarray[8],    
               immuarray[9],    
               nimmu,
               aearray[0],
               aearray[1],
               aearray[2],
               aearray[3],
               aearray[4],
               aearray[5],
               aearray[6],
               aearray[7],
               aearray[8],
               aearray[9],
               aearray[10],
               aearray[11],
               aearray[12],
               aearray[13],
               aearray[14],
               nae,
               lbarray[0],    
               lbarray[1],    
               lbarray[2],    
               lbarray[3],    
               lbarray[4],    
               lbarray[5],    
               lbarray[6],    
               lbarray[7],    
               lbarray[8],    
               lbarray[9],    
               lbarray[10],    
               lbarray[11],    
               lbarray[12],    
               lbarray[13],    
               lbarray[14],    
               lbarray[15],    
               lbarray[16],    
               lbarray[17],    
               lbarray[18],    
               lbarray[19],    
               nlab,
               dxarray[0],
               dxarray[1],
               dxarray[2],
               dxarray[3],
               dxarray[4],
               dxarray[5],
               dxarray[6],
               dxarray[7],
               dxarray[8],
               dxarray[9],
               dxarray[10],
               dxarray[11],
               dxarray[12],
               dxarray[13],
               dxarray[14],
               ndx,
               fevarray[0],
               fevarray[1],
               fevarray[2],
               fevarray[3],
               fevarray[4],
               fevarray[5],
               fevarray[6],
               fevarray[7],
               fevarray[8],
               fevarray[9],
               nfv,
               rxarray[0],
               rxarray[1],
               rxarray[2],
               rxarray[3],
               rxarray[4],
               rxarray[5],
               rxarray[6],
               rxarray[7],
               rxarray[8],
               rxarray[9],
               rxarray[10],
               rxarray[11],
               rxarray[12],
               rxarray[13],
               rxarray[14],
               nrx,
               qarray[0],
               qarray[1],
               qarray[2],
               qarray[3],
               qarray[4],
               qarray[5],
               qarray[6],
               qarray[7],
               qarray[8],
               qarray[9],
               qarray[10],
               qarray[11],
               qarray[12],
               qarray[13],
               qarray[14],
               qarray[15],
               qarray[16],
               qarray[17],
               qarray[18],
               qarray[19],
               qarray[20],
               qarray[21],
               qarray[22],
               qarray[23],
               qarray[24],
               nques,
            ]
        writer.writerow(row) 
    vfile.close()      

class Command(BaseCommand):
 
    help = 'Generates .csv VAERS Listing table for download'
    
    def handle(self, *args, **options):
        vaers_csv(True)
        vaers_csv(False)
        

