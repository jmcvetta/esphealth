#-*- coding:utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from ESP.static.models import Vaccine, ImmunizationManufacturer, Dx_code
from ESP.vaers.models import Case, Questionnaire, Report_Sent
from ESP.emr.models import Provider, Patient
from ESP.utils import utils
from ESP.settings import SITE_NAME, SYSTEM_STATUS, PHINMS_SERVER, PHINMS_USER, PHINMS_PASSWORD, PHINMS_PATH, VAERS_AUTOSENDER

from ESP.utils.utils import log

from ESP.utils.hl7_builder.core import SegmentTree
from ESP.utils.hl7_builder.segments import MSH, PID, ORC, OBR, OBX, NK1
from ESP.utils.hl7_builder.nodes import VaccineDetail, PriorVaccinationDetail
from ESP.utils.utils import mt
from ESP.conf.models import VaccineCodeMap

import ftplib
import csv, cStringIO
import datetime

UNKNOWN_VACCINE = Vaccine.objects.get(short_name='unknown')
UNKNOWN_MANUFACTURER = ImmunizationManufacturer.objects.get(code='UNK')

now = datetime.datetime.now()

class AdverseReactionReport(object):
    #initialize with a questionnaire record
    def __init__(self, questionnaire):
        self.ques = questionnaire
        self.case = Case.objects.get(id=self.ques.case_id)
        self.immunizations = self.case.immunizations.all()
        self.patient = Patient.objects.get(id=self.case.patient_id)

    def make_MSH(self):
        msh = MSH()

        # Most of these values should be parameters from the
        # function. For now they are defined here simply because we
        # have no other recipient except for Atrius Health.
        msh.receiving_application = 'VAERS HL7 Processor'
        msh.receiving_facility = 'VAERS PROCESSOR'
        msh.time = now.strftime("%Y%m%d%H%M%s")
        msh.processing_id = SYSTEM_STATUS
        msh.accept_ack_type = 'NE'
        msh.application_ack_type = 'AL'
        msh.message_type = ['ORU', 'R01']
        msh.message_control_id = self.ques.id
        msh.sending_facility = SITE_NAME

        return msh

    def make_PID(self):
        #TODO: deal with not available potential.  See NK1s
        patient = self.case.patient
        pid = PID()
        pid.patient_id_list = [patient.mrn,'','','','MR']
        pid.patient_name = [mt(patient.last_name), mt(patient.first_name),'','','','','L']
        pid.date_of_birth = utils.str_from_date(patient.date_of_birth)
        pid.sex = mt(patient.gender)
        pid.patient_address = [mt(patient.address1), mt(patient.address2), 
                               mt(patient.city), mt(patient.state), mt(patient.zip),'','C']
        pid.home_phone = [mt(patient.phone_number),'PRN']

        return pid
    
    def make_NK1s(self):
        
        vax_provider = Provider.objects.filter(id=self.immunizations.values_list('provider_id').distinct())
        comp_provider = self.ques.provider
        if self.ques.state=='AR':
            comp_provider = Provider.objects.get(natural_key=VAERS_AUTOSENDER)
            #VAERS AUTOSENDER must be identified for a site, and a Provider record entered for this individual
            #This is the sender of record in cases where case category is 2_serious and should be autosent.
        nk1_1 = NK1()
        if mt(vax_provider.get().last_name)=='':
            nk1_1.name='Not available'
        else:
            nk1_1.name=[mt(vax_provider.get().last_name),mt(vax_provider.get().first_name),'','',
                    mt(vax_provider.get().title),'','L']
        nk1_1.relationship = ['VAB', 'Vaccine administered by (Name)', 'HL70063']
        nk1_2 = NK1()
        if mt(comp_provider.last_name)=='':
            nk1_2.name='Not available'
        else:
            nk1_2.name=[mt(comp_provider.last_name),mt(comp_provider.first_name),'','',
                    mt(comp_provider.title),'','L']
        if nk1_1.name==nk1_2.name:
            nk1_2.relationship = ['FVP', 'Form completed by (Name)-Vaccine provider','HL70063']
        else:
            nk1_2.relationship = ['FOT', 'Form completed by (Name)-Other','HL70063']
        nk1_2.address = [mt(comp_provider.dept_address_1), mt(comp_provider.dept_address_2), 
                         mt(comp_provider.dept_city), mt(comp_provider.dept_state), 
                         mt(comp_provider.dept_zip),'','B']
        if nk1_2.address==['', '', '', '', '', '', 'B']:
            nk1_2.address='Not available'
        if mt(comp_provider.telephone)=='':
            nk1_2.phone_number='Not available'
        else:
            nk1_2.phone_number = [mt(comp_provider.telephone),'WPN']
        nk1=[]
        nk1.append(nk1_1)
        nk1.append(nk1_2)
        return SegmentTree(self.make_PID(), nk1)
    
    def make_ORC(self):
        #TODO: deal with not available potential.  See NK1s
        vax_provider = Provider.objects.filter(id=self.immunizations.values_list('provider_id').distinct())
        orc = ORC()
        orc.control='RE'
        orc.ordering_provider=[vax_provider.get().natural_key, mt(vax_provider.get().last_name),mt(vax_provider.get().first_name),'','',
                    mt(vax_provider.get().title),'','L']
        orc.ordering_facility_name=mt(vax_provider.get().dept)
        orc.ordering_facility_address = [mt(vax_provider.get().dept_address_1), mt(vax_provider.get().dept_address_2), 
                         mt(vax_provider.get().dept_city), mt(vax_provider.get().dept_state), 
                         mt(vax_provider.get().dept_zip),'','B']
        orc.ordering_facility_phone = [mt(vax_provider.get().telephone),'WPN']
        orc.ordering_provider_address = [mt(vax_provider.get().dept_address_1), mt(vax_provider.get().dept_address_2), 
                         mt(vax_provider.get().dept_city), mt(vax_provider.get().dept_state), 
                         mt(vax_provider.get().dept_zip),'','B']
        return orc


    def event_summary(self):
        obr_fda_report = OBR()
        obr_fda_report.universal_service_id = 'CDC VAERS-1 (FDA) Report'
        obr_fda_report.observation_date = utils.str_from_date(self.case.date)

        observation_results = []
        
        age = self.case.patient._get_age_str()
        if age:
            obx_patient_age = OBX()
            obx_patient_age.value_type = 'NM'
            obx_patient_age.identifier = ['21612-7', 'Reported Patient Age', 'LN']
            if age.endswith('Months'):
                obx_patient_age.value = age.split()[0]       
                obx_patient_age.units = ['mo', 'month', 'ANSI']
            else:
                obx_patient_age.value = age  
                obx_patient_age.units = ['yr', 'year', 'ANSI']
            obx_patient_age.observation_result_status = 'F'
            observation_results.append(obx_patient_age)
        
        obx_form = OBX()
        obx_form.value_type = 'TS'
        obx_form.identifier = ['30947-6', 'Date form completed', 'LN']
        obx_form.value = utils.str_from_date(self.ques.last_updated)
        obx_form.observation_result_status = 'F'
        observation_results.append(obx_form)

        obx_treatment = OBX()
        obx_treatment.value_type = 'FT'
        obx_treatment.identifier = ['30948-4', 'Vaccination adverse events and treatment, if any', 'LN']
        obx_treatment.sub_id = 1
        AEs = self.case.adverse_events.distinct().order_by('date')
        quests = self.case.questionnaire_set.filter(comment__isnull=False)
        caseDescription=''
        for AE in AEs:
            if ContentType.objects.get_for_id(AE.content_type_id).model.startswith('encounter'):
                #TODO check how the matching rule explain is filled out for icd10 patched for now
                dx_codes = AE.matching_rule_explain.split()
                for dx_code in dx_codes:
                    #TODO fix icd10 patched  for now
                    if Dx_code.objects.filter(code=dx_code, type= 'ICD9').exists():
                        caseDescription += Dx_code.objects.get(code=dx_code, type= 'ICD9').name + ', '
                caseDescription = caseDescription[0:-2] + ' on ' + str(AE.encounterevent.date) + ', '  
            elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('prescription'):
                caseDescription = caseDescription + AE.prescriptionevent.content_object.name + ' on ' + str(AE.prescriptionevent.content_object.date) + ', '
            elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('labresult'):
                caseDescription = caseDescription + AE.labresultevent.content_object.output_name + ' on ' + str(AE.labresultevent.content_object.result_date) + ', '
            elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('allergy'):
                caseDescription = caseDescription + AE.allergyevent.content_object.name + ' allergy on ' + str(AE.allergyevent.content_object.date) + ', '
        for quest in quests:
            caseDescription += 'clinician comment: ' + quest.comment + ', '
        caseDescription = caseDescription[0:-2] + '. '
        obx_treatment.value = caseDescription
        obx_treatment.observation_result_status = 'F'
        observation_results.append(obx_treatment)
        
        for AE in AEs:
            if ContentType.objects.get_for_id(AE.content_type_id).model.startswith('encounter'):
                if AE.encounterevent.content_object.encounter_type=='ER':
                    obx_ER = OBX()
                    obx_ER.value_type = 'CE'
                    obx_ER.identifier = ['30949-4','Vaccination adverse event outcome','LN']
                    obx_ER.sub_id=1
                    obx_ER.value=['E','required emergency room/doctor visit','NIP005']
                    obx_ER.observation_result_status='F'
                    observation_results.append(obx_ER)
                elif (AE.encounterevent.content_object.hosp_admit_dt and
                        AE.encounterevent.content_object.hosp_dschrg_dt and
                        AE.encounterevent.content_object.date >= AE.encounterevent.content_object.hosp_admit_dt and
                        AE.encounterevent.content_object.date <= AE.encounterevent.content_object.hosp_dschrg_dt):
                    obx_hosp = OBX()
                    obx_hosp.value_type = 'CE'
                    obx_hosp.identifier = ['30949-4','Vaccination adverse event outcome','LN']
                    obx_ER.sub_id=1
                    obx_ER.value=['H','required hospitalization','NIP005']
                    obx_ER.observation_result_status='F'
                    observation_results.append(obx_hosp)
                    obx_hdur = OBX()
                    obx_hdur.value_type = 'NM'
                    obx_hdur.identifier = ['30950-0','Number of days hospitalized due to vaccination adverse event','LN']
                    obx_hdur.sub_id=1
                    obx_hdur.value=AE.encounterevent.content_object.hosp_dschrg_dt - AE.encounterevent.content_object.date
                    obx_hdur.units = ['d','day','ANSI']
                    obx_hdur.observation_result_status = 'F'
                    observation_results.append(obx_hdur)
                          
        obx_vaccination = OBX()
        obx_vaccination.value_type = 'TS'
        obx_vaccination.identifier = ['30952-6', 'Date of vaccination', 'LN']
        obx_vaccination.value = utils.str_from_date(
            max([x.date for x in self.immunizations]))
        obx_vaccination.observation_result_status = 'F'
        observation_results.append(obx_vaccination)

        obx_date = OBX()
        obx_date.value_type = 'TS'
        obx_date.identifier = ['30953-4', 'Adverse event onset date and time', 'LN']
        obx_date.value = utils.str_from_date(min([AE.date for AE in AEs]))
        obx_date.observation_result_status = 'F'
        observation_results.append(obx_date)

        obx_labs = OBX()
        obx_labs.value_type = 'FT'
        obx_labs.identifier = ['30954-2','Relevant diagnostic tests/lab data','LN']
        obx_labs.observation_result_status = 'F'
        for AE in AEs:
            if ContentType.objects.get_for_id(AE.content_type_id).model.startswith('labresult'):
                obx_labs.value = AE.matching_rule_explain + ' Observed value: ' + AE.labresultevent.content_object.result_string
                observation_results.append(obx_labs)

        return SegmentTree(obr_fda_report, observation_results)

    def vaccine_list(self):
        obr_vaccine_list = OBR()
        obr_vaccine_list.universal_service_id = ['30955-9','All vaccines given on date listed in #10','LN']

        vaccines = []

        for immunization in self.immunizations:
            vaccine_detail = VaccineDetail(immunization)
            for seg in vaccine_detail.segments:
                vaccines.append(seg)
            
        return SegmentTree(obr_vaccine_list, vaccines)
    
    def prior_vax(self):
        obr_prior_vaccination_list = OBR()
        obr_prior_vaccination_list.universal_service_id = ['30961-7', 'Any other vaccinations within 4 weeks prior to the date listed in #10', 'LN']

        vaccines = []
        for immunization in self.case.prior_immunizations.all():
            vaccine_detail = PriorVaccinationDetail(immunization)
            for seg in vaccine_detail.segments:
                vaccines.append(seg)
        
        vax_at = OBX()
        vax_at.value_type = 'CE'
        vax_at.identifier = ['30962-5','Vaccinated at','LN']
        vax_at.value = ['PVT','Private doctor''s office/hospital','NIP008']
        vax_at.observation_result_status = 'F'
        #these are not prior vax data, but VAERS message spec defines these OBX segments as subs 
        # of the prior vax OBR seg.  
        vaccines.append(vax_at)  
        
        oth_meds = []
        oth_med = OBX()
        oth_med.value_type = 'FT'
        oth_med.identifier = ['30964-1','Other medications','LN']
        oth_med.observation_result_status = 'F'
        oth_cnt = 0
        AEs = self.case.adverse_events.distinct().order_by('date')
        for AE in AEs:
            if ContentType.objects.get_for_id(AE.content_type_id).model.startswith('prescription'):
                oth_med.value = AE.prescriptionevent.content_object.name
                oth_meds.append(oth_med)
                oth_cnt += 1
        if oth_cnt==0:
            oth_med.value = 'None'
            oth_meds.append(oth_med)
        #these are not prior vax data, but VAERS message spec defines these OBX segments as subs 
        # of the prior vax OBR seg.  
        vaccines.append(oth_med)

        prev_rept = OBX()
        prev_rept.value_type = 'CE'
        prev_rept.identifier = ['30967-4','Was adverse event reported previously','LN']
        prev_rept.value = ['D','To doctor','NIP009']
        prev_rept.observation_result_status = 'F'
        #these are not prior vax data, but VAERS message spec defines these OBX segments as subs 
        # of the prior vax OBR seg.  
        vaccines.append(prev_rept)
        
                        
        return SegmentTree(obr_prior_vaccination_list, vaccines)
    
    def prior_ae(self, case):
        
        obr = OBR()
        obr.universal_service_id = ['30968-2','Adverse event following prior vaccination in patient','LN']
       
        p_aes = []
        p_ae = OBX()
        p_ae.value_type = 'CE'
        p_ae.observation_result_status = 'F'
        ae_list = []
        p_ae.identifier = ['30968-2&30971-6','Adverse event','LN']
        AEs = case.adverse_events.distinct().order_by('date')
        for AE in AEs:
            ae_list.append(AE.matching_rule_explain)
        p_ae.value = ae_list 
        p_aes.append(p_ae)
        p_ae.identifier = ['30968-2&30971-6','Onset age','LN']
        p_ae.value = self.patient.age.years
        p_ae.units = ['yr','year','ANSI']
        if p_ae.value < 2:
            p_ae.value = self.patient.age.months
            p_ae.units = ['mo','month','ANSI']
        p_aes.append(p_ae)
        p_ae.units = None
        p_ae.identifier = ['30968-2&30971-6','Vaccine Type','LN']  
        for imm in case.immunizations.all():
            CVXVax = Vaccine.objects.get(id=imm.vaccine.code)
            p_ae.value = [CVXVax.code, CVXVax.short_name, 'CVX']
            p_aes.append(p_ae)           
        return SegmentTree(obr, p_aes)
    
    def repno(self):
        obr = OBR()
        obr.universal_service_id = ['','Only for reports submitted by manufacturer/immunization project']
        obx = OBX()
        obx.value_type = 'ST'
        obx.observation_result_status = 'F'
        obx.identifier = ['30975-7','Mfr./Imm. Proj. report no.','LN']
        obx.value = ['METROHEALTHESP2012'+str(self.ques.id)]
        return SegmentTree(obr, obx)
        

    def render(self):
        observation_reports = [self.event_summary(), self.vaccine_list(), 
                               self.prior_vax()]
        pcases = Case.objects.filter(patient=self.case.patient, date__lt=self.case.date, report_sent__id__isnull=False)
        pcases = pcases.filter(id__in=Report_Sent.objects.filter)
        for pcase in pcases:
            observation_reports.append(self.prior_ae(pcase))
        observation_reports.append(self.repno())
        for idx, report in enumerate(observation_reports):
            report.parent.sequence_id = idx + 1

        patient_header = [self.make_MSH(), self.make_NK1s(), self.make_ORC()]

        all_segments = patient_header + observation_reports
        hl7file = cStringIO.StringIO()
        hl7file.write('\r'.join([str(x) for x in all_segments]))
        hl7file.seek(0)
        if transmit_ftp(hl7file, 'vaers_msg_ID' + str(self.ques.id) + '.hl7'):
            if Questionnaire.objects.filter(id=self.ques.id, state='Q'):
                Questionnaire.objects.filter(id=self.ques.id).update(state='S')
            elif Questionnaire.objects.filter(id=self.ques.id, state='AR'):
                Questionnaire.objects.filter(id=self.ques.id).update(state='AS')
            Report_Sent.objects.create(questionnaire_id=self.ques.id,
                                       case_id=self.case.id,
                                       date=now,
                                       report=hl7file.getvalue(),
                                       report_type='VAERS')
        hl7file.close()
    


def transmit_ftp(fileObj, filename):
        '''
        Upload a file using cleartext FTP.  
        '''
        log.info('Transmitting case report via FTP')
        log.debug('FTP server: %s' % PHINMS_SERVER)
        log.debug('FTP user: %s' % PHINMS_USER)
        log.debug('Attempting to connect...')
        conn = ftplib.FTP(PHINMS_SERVER, PHINMS_USER, PHINMS_PASSWORD)
        log.debug('Connected to %s' % PHINMS_SERVER)
        log.debug('CWD to %s' % PHINMS_PATH)
        conn.cwd(PHINMS_PATH)
        command = 'STOR ' + filename
        try:
            conn.storlines(command, fileObj)
            log.info('Successfully uploaded VAERS HL7 message to PHINMS Server')
        except BaseException, e:
            log.error('FTP ERROR: %s' % e)
            return False
        return True
