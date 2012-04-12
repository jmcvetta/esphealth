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
from datetime import date
from dateutil.relativedelta import relativedelta



from ESP.vaers.models import AdverseEvent

def vaers_csv(no_phi):
    '''
    Creates a linelist CSV file of all vaers data
    '''
    fpath='/srv/download/'
    vaers_qs=AdverseEvent.objects.all()
    obsc='PHI'
    if no_phi:
        file=open(fpath+"vaers_linelist_nophi.csv",'w')
    else:
        file=open(fpath+"vaers_linelist_phi.csv",'w')        
    #rebuild each time
    file.truncate()
    #this has to be parameterized.
    writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(['MRN',
              'Name',    
              'DOB',     
              'Age',     
              'Gender',    
              'Practice',    
              'Reporting_clinician_name',
              'Vaccine_name',
              'Action_category1',
              'Date_vaccination',
              'Vaccine_Lot_no',    
              'Additional_vaccine_name_no1',    
              'Additional_vaccine_name_no2',    
              'Additional_vaccine_name_no3',
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
              'ICD9_result_date1',
              'ICD9_result_text1',
              'ICD9_result_code1',
              'ICD9_result_date2',
              'ICD9_result_text2',
              'ICD9_result_code2',
              'ICD9_result_date3',
              'ICD9_result_text3',
              'ICD9_result_code3',
              'Allergy_date1',
              'Allergy_name1',
              'Allergy_text1',
              'Allergy_date2',
              'Allergy_name2',
              'Allergy_text2',
              'Prescription_date1',
              'Prescription_name1',
              'Prescription_dose_frequency_duration1',
              'Prescription_date2',
              'Prescription_name2',
              'Prescription_dose_frequency_duration2',
              'Date_Report_Submitted',
              'Clinical_Opinion',  
              'Clinical_Comment',
        ])
    for AE in vaers_qs:
        patient = AE.patient
        mrn = patient.mrn
        fullname = patient.last_name + ', ' + patient.first_name
        dob = patient.date_of_birth
        age = patient.age.years
        category = AE.category
        provider = patient.pcp
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
        for imm in immunization:
            if no_phi:
                immuarray.append(imm.date.year)
            else:
                immuarray.append(imm.date) 
            immuarray.append(imm.name) 
            immuarray.append(imm.lot)
        while len(immuarray) < 12:
            immuarray.append(None)
        types = ContentType.objects.get_for_id(AE.content_type_id).model
        dxarray = []
        rxarray = []
        lbarray = []
        alarray = []
        if types == 'encounterevent':
            icd9codes = AE.encounterevent.encounter.icd9_codes.all()
            if no_phi:
                dxdate = AE.encounterevent.encounter.date.year
            else:
                dxdate = AE.encounterevent.encounter.date
            for dx in icd9codes:
                dxarray.append(dx.name)
                dxarray.append(dx.code)
        elif types == 'prescriptionevent':    
            rxs = AE.prescriptionevent.prescription.prescriptionevent_set.all()
            for rx in rxs:
                if no_phi:
                    rxarray.append(rx.prescription.date.year)
                else:
                    rxarray.append(rx.prescription.date)
                rxarray.append(rx.prescription.name)
                rxarray.append(rx.prescription.directions)
        elif types == 'labresultevent':
            labs = AE.labresultevent.lab_result.labresultevent_set.all()
            for lab in labs:
                lbarray.append(lab.lab_result.native_name)
                if no_phi:
                    lbarray.append(lab.lab_result.result_date.year)
                else:
                    lbarray.append(lab.lab_result.result_date)
                lbarray.append(lab.lab_result.result_float)
                lbarray.append(lab.lab_result.result_string)
        elif types == 'allergyevent':
            allergies = AE.allergyevent.allergy.allergyevent_set.all()
            for allrgy in allergies:
                if no_phi:
                    alarray.append(allrgy.allergy.date.year)
                else:
                    alarray.append(allrgy.allergy.date)
                alarray.append(allrgy.allergy.allergen)
                alarray.append(allrgy.allergy.description)
        while len(dxarray) < 6:
            dxarray.append(None)
        while len(rxarray) < 6:
            rxarray.append(None)
        while len(lbarray) < 12:
            lbarray.append(None)
        while len(alarray) < 6:
            alarray.append(None)
        row = [mrn,
               fullname,    
               dob,     
               age,     
               patient.gender,    
               provider.dept,    
               pname,
               immuarray[1],    
               category,
               immuarray[0],
               immuarray[2],    
               immuarray[4],    
               immuarray[7],    
               immuarray[10],    
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
               dxdate,
               dxarray[0],
               dxarray[1],
               dxdate,
               dxarray[2],
               dxarray[3],
               dxdate,
               dxarray[4],
               dxarray[5],
               alarray[0],
               alarray[1],
               alarray[2],
               alarray[3],
               alarray[4],
               alarray[5],
               rxarray[0],
               rxarray[1],
               rxarray[2],
               rxarray[3],
               rxarray[4],
               rxarray[5],
               AE.date,
               AE.state,  
               'providercomment',
            ]
        writer.writerow(row) 
    file.close()      

class Command(BaseCommand):
 
    help = 'Generates .csv VAERS Listing table for download'
    
    def handle(self, *args, **options):
        vaers_csv(True)
        vaers_csv(False)
        

