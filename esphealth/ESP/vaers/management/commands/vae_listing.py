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

import csv

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datetime import date
from dateutil.relativedelta import relativedelta
from ESP.vaers.models import Case
from ESP.settings import VAERS_LINELIST_PATH
from ESP.utils.utils import log

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
              'Reporting_clinician_name',
              'Action_category1',
              'Vaccine_name_1',
              'Date_vaccination_1',
              'Vaccine_Lot_no_1',    
              'Vaccine_name_2',
              'Date_vaccination_2',
              'Vaccine_Lot_no_2',    
              'Vaccine_name_3',
              'Date_vaccination_3',
              'Vaccine_Lot_no_3',    
              'Vaccine_name_4',
              'Date_vaccination_4',
              'Vaccine_Lot_no_4',    
              'Vaccine_name_5',
              'Date_vaccination_5',
              'Vaccine_Lot_no_5',    
              'Lab_result_name1',    
              'Lab_result_date1',
              'Lab_result_text1',    
              'Lab_result_value1',    
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
              'Prescription_date1',
              'Prescription_name1',
              'Prescription_dose_frequency_duration1',
              'Date_Report_Submitted',
              'Clinical_Opinion',  
              'Clinical_Comment',
        ])
    for case in case_qs:
        ques_qs=case.questionaire_set.all()
        vaers_qs=case.adverse_event.distinct()
        for AE in vaers_qs:
            patient = AE.patient
            mrn = patient.mrn
            fullname = patient.last_name + ', ' + patient.first_name
            dob = patient.date_of_birth
            age = patient.age.years
            category = AE.category
            provider = patient.pcp
            try:
                state = ques_qs.get(provider=patient.pcp_id).state
            except MultipleObjectsReturned:
                log.warn('multiple questionnaire rows returned for case %s and physician %s' % (case.id, provider))
                state = None
            except ObjectDoesNotExist:
                state = None
            pname = provider.last_name + ',' + provider.first_name
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
            immunization = AE.immunizations.all()
            immuarray = []
            x = 0
            for imm in immunization:
                immuarray.append(imm.name) 
                if no_phi:
                    immuarray.append(imm.date.year)
                else:
                    immuarray.append(imm.date) 
                immuarray.append(imm.lot)
            types = ContentType.objects.get_for_id(AE.content_type_id).model
            dxarray = []
            rxarray = []
            lbarray = []
            alarray = []
            if types.startswith('encounter'): 
                icd9codes = AE.encounterevent.content_object.icd9_codes.all()
                for icd9code in icd9codes:
                    if no_phi:
                        dxdate = AE.encounterevent.date.year
                    else:
                        dxdate = AE.encounterevent.date
                    dxarray.append(dxdate)
                    dxarray.append(icd9code.name)
                    dxarray.append(icd9code.code)
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
                lbarray.append(labs.result_float)
                lbarray.append(labs.result_string)
            elif types.startswith('allergy'):
                allergies = AE.allergyevent.allergy.allergyevent_set.all()
                for allrgy in allergies:
                    if no_phi:
                        alarray.append(allrgy.allergy.date.year)
                    else:
                        alarray.append(allrgy.allergy.date)
                    alarray.append(allrgy.allergy.allergen)
                    alarray.append(allrgy.allergy.description)
            while len(immuarray) < 15:
                immuarray.append(None)
            while len(dxarray) < 15:
                dxarray.append(None)
            while len(rxarray) < 3:
                rxarray.append(None)
            while len(lbarray) < 4:
                lbarray.append(None)
            while len(alarray) < 0:
                alarray.append(None)
            row = [case.id,
                   mrn,
                   fullname,    
                   dob,     
                   age,     
                   patient.gender,    
                   provider.dept,    
                   pname,
                   category,
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
                   lbarray[0],    
                   lbarray[1],    
                   lbarray[2],    
                   lbarray[3],    
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
                   rxarray[0],
                   rxarray[1],
                   rxarray[2],
                   AE.date,
                   state,  
                   'questionaire',
                   #TODO should be getting the text from provider response
                ]
            writer.writerow(row) 
    vfile.close()      

class Command(BaseCommand):
 
    help = 'Generates .csv VAERS Listing table for download'
    
    def handle(self, *args, **options):
        vaers_csv(True)
        vaers_csv(False)
        

