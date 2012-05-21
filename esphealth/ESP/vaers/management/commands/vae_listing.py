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
              'Vaccine_name_6',
              'Vaccine_Lot_no_6',  
              'Vaccine_name_7',
              'Vaccine_Lot_no_7',  
              'Vaccine_name_8',
              'Vaccine_Lot_no_8',  
              'Vaccine_name_9',
              'Vaccine_Lot_no_9',  
              'Vaccine_name_10',
              'Vaccine_Lot_no_10',  
              'Vaccine_name_11',
              'Vaccine_Lot_no_11',  
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
              'Event_name6',
              'Reporting_clinician_name6',
              'Action_category6',
              'Event_name7',
              'Reporting_clinician_name7',
              'Action_category7',
              'Event_name8',
              'Reporting_clinician_name8',
              'Action_category8',
              'Event_name9',
              'Reporting_clinician_name9',
              'Action_category9',
              'Event_name10',
              'Reporting_clinician_name10',
              'Action_category10',
              'Event_name11',
              'Reporting_clinician_name11',
              'Action_category11',
              'Event_name12',
              'Reporting_clinician_name12',
              'Action_category12',
              'Event_name13',
              'Reporting_clinician_name13',
              'Action_category13',
              'Event_name14',
              'Reporting_clinician_name14',
              'Action_category14',
              'Event_name15',
              'Reporting_clinician_name15',
              'Action_category15',
              'Event_name16',
              'Reporting_clinician_name16',
              'Action_category16',
              'Event_name17',
              'Reporting_clinician_name17',
              'Action_category17',
              'Event_name18',
              'Reporting_clinician_name18',
              'Action_category18',
              'Event_name19',
              'Reporting_clinician_name19',
              'Action_category19',
              'Event_name20',
              'Reporting_clinician_name20',
              'Action_category20',
              'Event_name21',
              'Reporting_clinician_name21',
              'Action_category21',
              'Event_name22',
              'Reporting_clinician_name22',
              'Action_category22',
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
              'ICD9_result_date6',
              'ICD9_result_text6',
              'ICD9_result_code6',
              'ICD9_result_date7',
              'ICD9_result_text7',
              'ICD9_result_code7',
              'ICD9_result_date8',
              'ICD9_result_text8',
              'ICD9_result_code8',
              'ICD9_result_date9',
              'ICD9_result_text9',
              'ICD9_result_code9',
              'ICD9_result_date10',
              'ICD9_result_text10',
              'ICD9_result_code10',
              'ICD9_result_date11',
              'ICD9_result_text11',
              'ICD9_result_code11',
              'ICD9_result_date12',
              'ICD9_result_text12',
              'ICD9_result_code12',
              'ICD9_result_date13',
              'ICD9_result_text13',
              'ICD9_result_code13',
              'ICD9_result_date14',
              'ICD9_result_text14',
              'ICD9_result_code14',
              'ICD9_result_date15',
              'ICD9_result_text15',
              'ICD9_result_code15',
              'ICD9_result_date16',
              'ICD9_result_text16',
              'ICD9_result_code16',
              'ICD9_result_date17',
              'ICD9_result_text17',
              'ICD9_result_code17',
              'ICD9_result_date18',
              'ICD9_result_text18',
              'ICD9_result_code18',
              'ICD9_result_date19',
              'ICD9_result_text19',
              'ICD9_result_code19',
              'ICD9_result_date20',
              'ICD9_result_text20',
              'ICD9_result_code20',
              'ICD9_result_date21',
              'ICD9_result_text21',
              'ICD9_result_code21',
              'ICD9_result_date22',
              'ICD9_result_text22',
              'ICD9_result_code22',
              'ICD9_result_date23',
              'ICD9_result_text23',
              'ICD9_result_code23',
              'ICD9_result_date24',
              'ICD9_result_text24',
              'ICD9_result_code24',
              'ICD9_result_date25',
              'ICD9_result_text25',
              'ICD9_result_code25',
              'ICD9_result_date26',
              'ICD9_result_text26',
              'ICD9_result_code26',
              'ICD9_result_date27',
              'ICD9_result_text27',
              'ICD9_result_code27',
              'ICD9_result_date28',
              'ICD9_result_text28',
              'ICD9_result_code28',
              'ICD9_result_date29',
              'ICD9_result_text29',
              'ICD9_result_code29',
              'ICD9_count',
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
              'Prescription_date6',
              'Prescription_name6',
              'Prescription_dose_freq_dur6',
              'Prescription_date7',
              'Prescription_name7',
              'Prescription_dose_freq_dur7',
              'Prescription_date8',
              'Prescription_name8',
              'Prescription_dose_freq_dur8',
              'Prescription_date9',
              'Prescription_name9',
              'Prescription_dose_freq_dur9',
              'Prescription_date10',
              'Prescription_name10',
              'Prescription_dose_freq_dur10',
              'Prescription_date11',
              'Prescription_name11',
              'Prescription_dose_freq_dur11',
              'Prescription_date12',
              'Prescription_name12',
              'Prescription_dose_freq_dur12',
              'Prescription_date13',
              'Prescription_name13',
              'Prescription_dose_freq_dur13',
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
              'Pysician_notified6',
              'Workflow_status6',
              'Clinical_comment6',  
              'Message_ishelpful6',
              'Message_interuptswork6',
              'Pysician_notified7',
              'Workflow_status7',
              'Clinical_comment7',  
              'Message_ishelpful7',
              'Message_interuptswork7',
              'Pysician_notified8',
              'Workflow_status8',
              'Clinical_comment8',  
              'Message_ishelpful8',
              'Message_interuptswork8',
              'Pysician_notified9',
              'Workflow_status9',
              'Clinical_comment9',  
              'Message_ishelpful9',
              'Message_interuptswork9',
              'Pysician_notified10',
              'Workflow_status10',
              'Clinical_comment10',  
              'Message_ishelpful10',
              'Message_interuptswork10',
              'Pysician_notified11',
              'Workflow_status11',
              'Clinical_comment11',  
              'Message_ishelpful11',
              'Message_interuptswork11',
              'Pysician_notified12',
              'Workflow_status12',
              'Clinical_comment12',  
              'Message_ishelpful12',
              'Message_interuptswork12',
              'Pysician_notified13',
              'Workflow_status13',
              'Clinical_comment13',  
              'Message_ishelpful13',
              'Message_interuptswork13',
              'Pysician_notified14',
              'Workflow_status14',
              'Clinical_comment14',  
              'Message_ishelpful14',
              'Message_interuptswork14',
              'Pysician_notified15',
              'Workflow_status15',
              'Clinical_comment15',  
              'Message_ishelpful15',
              'Message_interuptswork15',
              'Pysician_notified16',
              'Workflow_status16',
              'Clinical_comment16',  
              'Message_ishelpful16',
              'Message_interuptswork16',
              'Message_count',
        ])
    for case in case_qs:
        immunization_qs = case.immunizations.all()
        patient = case.patient
        mrn = patient.mrn
        if not patient.last_name:
            fullname=None
        elif not patient.first_name:
            fullname=patient.last_name
        else:
            fullname = patient.last_name + ', ' + patient.first_name
        dob = patient.date_of_birth
        if patient.age:
            age = patient.age.years
        else:
            age = None
        provider=Provider.objects.get(id=immunization_qs[0].provider_id)
        pname=provider._get_name()
        vaccdate=immunization_qs[0].date
        if no_phi:
            mrn = obsc
            fullname = obsc
            if relativedelta(date.today(), dob).years >= 90:
                dob = None 
            elif patient.date_of_birth:
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
        while len(immuarray) < 22:
            immuarray.append(None)
        aearray = []
        dxarray = []
        rxarray = []
        lbarray = []
        alarray = []
        vaers_qs=case.adverse_events.distinct()
        #todo: this needs to be ordered by category -- worst first.  Order by does not work, as category order is 2, 3, 1
        for AE in vaers_qs:
            aearray.append(AE.name)
            if no_phi:
                aearray.append(obsc)
            else:
                aearray.append(AE.content_object.provider)
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
        while len(aearray) < 66:
            aearray.append(None)
        nlab=len(lbarray)/4
        while len(lbarray) < 20:
            lbarray.append(None)
        ndx=len(dxarray)/3
        while len(dxarray) < 87:
            dxarray.append(None)
        nrx=len(rxarray)/3    
        while len(rxarray) < 39:
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
        while len(qarray) < 80:
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
               immuarray[10],    
               immuarray[11],
               immuarray[12],    
               immuarray[13],    
               immuarray[14],    
               immuarray[15],    
               immuarray[16],    
               immuarray[17],    
               immuarray[18],    
               immuarray[19],    
               immuarray[20],    
               immuarray[21],
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
               aearray[15],
               aearray[16],
               aearray[17],
               aearray[18],
               aearray[19],
               aearray[20],
               aearray[21],
               aearray[22],
               aearray[23],
               aearray[24],
               aearray[25],
               aearray[26],
               aearray[27],
               aearray[28],
               aearray[29],
               aearray[30],
               aearray[31],
               aearray[32],
               aearray[33],
               aearray[34],
               aearray[35],
               aearray[36],
               aearray[37],
               aearray[38],
               aearray[39],
               aearray[40],
               aearray[41],
               aearray[42],
               aearray[43],
               aearray[44],
               aearray[45],
               aearray[46],
               aearray[47],
               aearray[48],
               aearray[49],
               aearray[50],
               aearray[51],
               aearray[52],
               aearray[53],
               aearray[54],
               aearray[55],
               aearray[56],
               aearray[57],
               aearray[58],
               aearray[59],
               aearray[60],
               aearray[61],
               aearray[62],
               aearray[63],
               aearray[64],
               aearray[65],
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
               dxarray[15],
               dxarray[16],
               dxarray[17],
               dxarray[18],
               dxarray[19],
               dxarray[20],
               dxarray[21],
               dxarray[22],
               dxarray[23],
               dxarray[24],
               dxarray[25],
               dxarray[26],
               dxarray[27],
               dxarray[28],
               dxarray[29],
               dxarray[30],
               dxarray[31],
               dxarray[32],
               dxarray[33],
               dxarray[34],
               dxarray[35],
               dxarray[36],
               dxarray[37],
               dxarray[38],
               dxarray[39],
               dxarray[40],
               dxarray[41],
               dxarray[42],
               dxarray[43],
               dxarray[44],
               dxarray[45],
               dxarray[46],
               dxarray[47],
               dxarray[48],
               dxarray[49],
               dxarray[50],
               dxarray[51],
               dxarray[52],
               dxarray[53],
               dxarray[54],
               dxarray[55],
               dxarray[56],
               dxarray[57],
               dxarray[58],
               dxarray[59],
               dxarray[60],
               dxarray[61],
               dxarray[62],
               dxarray[63],
               dxarray[64],
               dxarray[65],
               dxarray[66],
               dxarray[67],
               dxarray[68],
               dxarray[69],
               dxarray[70],
               dxarray[71],
               dxarray[72],
               dxarray[73],
               dxarray[74],
               dxarray[75],
               dxarray[76],
               dxarray[77],
               dxarray[78],
               dxarray[79],
               dxarray[80],
               dxarray[81],
               dxarray[82],
               dxarray[83],
               dxarray[84],
               dxarray[85],
               dxarray[86],
               ndx,
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
               rxarray[15],
               rxarray[16],
               rxarray[17],
               rxarray[18],
               rxarray[19],
               rxarray[20],
               rxarray[21],
               rxarray[22],
               rxarray[23],
               rxarray[24],
               rxarray[25],
               rxarray[26],
               rxarray[27],
               rxarray[28],
               rxarray[29],
               rxarray[30],
               rxarray[31],
               rxarray[32],
               rxarray[33],
               rxarray[34],
               rxarray[35],
               rxarray[36],
               rxarray[37],
               rxarray[38],
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
               qarray[25],
               qarray[26],
               qarray[27],
               qarray[28],
               qarray[29],
               qarray[30],
               qarray[31],
               qarray[32],
               qarray[33],
               qarray[34],
               qarray[35],
               qarray[36],
               qarray[37],
               qarray[38],
               qarray[39],
               qarray[40],
               qarray[41],
               qarray[42],
               qarray[43],
               qarray[44],
               qarray[45],
               qarray[46],
               qarray[47],
               qarray[48],
               qarray[49],
               qarray[50],
               qarray[51],
               qarray[52],
               qarray[53],
               qarray[54],
               qarray[55],
               qarray[56],
               qarray[57],
               qarray[58],
               qarray[59],
               qarray[60],
               qarray[61],
               qarray[62],
               qarray[63],
               qarray[64],
               qarray[65],
               qarray[66],
               qarray[67],
               qarray[68],
               qarray[69],
               qarray[70],
               qarray[71],
               qarray[72],
               qarray[73],
               qarray[74],
               qarray[75],
               qarray[76],
               qarray[77],
               qarray[78],
               qarray[79],
               nques,
            ]
        writer.writerow(row) 
    vfile.close()      

class Command(BaseCommand):
 
    help = 'Generates .csv VAERS Listing table for download'
    
    def handle(self, *args, **options):
        vaers_csv(True)
        vaers_csv(False)
        

