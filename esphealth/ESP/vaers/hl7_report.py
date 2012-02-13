#-*- coding:utf-8 -*-

from ESP.static.models import Vaccine, ImmunizationManufacturer
from ESP.emr.models import Patient, Provider, Immunization
from ESP.vaers.models import AdverseEvent
from ESP.utils import utils
from ESP.settings import SITE_NAME

from ESP.utils.hl7_builder.core import Field, SegmentTree
from ESP.utils.hl7_builder.segments import MSH, PID,ORC,  OBR, OBX
from ESP.utils.hl7_builder.nodes import VaccineDetail, PriorVaccinationDetail
from ESP.utils.hl7_builder.nodes import VaersProjectIdentification

UNKNOWN_VACCINE = Vaccine.objects.get(short_name='unknown')
UNKNOWN_MANUFACTURER = ImmunizationManufacturer.objects.get(code='UNK')

class AdverseReactionReport(object):
    def __init__(self, event):
        self.event = event


    def make_MSH(self):
        msh = MSH()

        # Most of these values should be parameters from the
        # function. For now they are defined here simpy because we
        # have no other recipient except for Atrius Health.
        msh.receiving_application = 'VAERS HL7 Processor'
        msh.receiving_facility = 'VAERS PROCESSOR'
        msh.processing_id = 'T'
        msh.accept_ack_type = 'NE'
        msh.application_ack_type = 'AL'
        msh.message_type = ['ORU', 'R01']
        msh.message_control_id = SITE_NAME
        msh.sending_facility = SITE_NAME

        return msh

    def make_PID(self):
        
        patient = self.event.patient
        pid = PID()

        pid.patient_internal_id = [patient.patient_id_num]
        pid.patient_name = [patient.last_name, patient.first_name]
        pid.date_of_birth = utils.str_from_date(patient.date_of_birth)
        pid.sex = patient.gender
        pid.patient_address = [patient.address1, patient.address2, 
                               patient.city, patient.state, patient.zip]
        pid.home_phone = patient.phone_number
        pid.primary_language = patient.home_language

        return pid

    def event_summary(self):
        obr_fda_report = OBR()
        obr_fda_report.universal_service_id = 'CDC VAERS-1 (FDA) Report'
        obr_fda_report.observation_date = utils.str_from_date(self.event.date)

        observation_results = []
                

        
        age = self.event.patient._get_age_str()
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
        obx_form.value = utils.str_from_date(self.event.last_updated)
        obx_form.observation_result_status = 'F'
        observation_results.append(obx_form)

        obx_treatment = OBX()
        obx_treatment.value_type = 'FT'
        obx_treatment.identifier = ['30948-4', 'Vaccination adverse events and treatment, if any', 'LN']
        obx_treatment.subsequence_id = 1
        obx_treatment.value = self.event.matching_rule_explain
        obx_treatment.observation_result_status = 'F'
        observation_results.append(obx_treatment)
        
        obx_vaccination = OBX()
        obx_vaccination.value_type = 'TS'
        obx_vaccination.identifier = ['30952-6', 'Date of vaccination', 'LN']
        obx_vaccination.value = utils.str_from_date(
            max([x.date for x in self.event.immunizations.all()]))
        obx_vaccination.observation_result_status = 'F'
        observation_results.append(obx_vaccination)

        obx_date = OBX()
        obx_date.value_type = 'TS'
        obx_date.identifier = ['30953-4', 'Adverse event onset date and time', 'LN']
        obx_date.value = utils.str_from_date(self.event.date)
        obx_date.observation_result_status = 'F'
        observation_results.append(obx_date)




        return SegmentTree(obr_fda_report, observation_results)
        
        

    def vaccine_list(self):
        obr_vaccine_list = OBR()
        obr_vaccine_list.universal_service_id = ['30955-9','All vaccines given on date listed in #10','LN']

        vaccines = []

        for idx, immunization in enumerate(self.event.immunizations.all()):
            vaccine_detail = VaccineDetail(immunization)
            for seg in vaccine_detail.segments:
                vaccines.append(seg)
            
        return SegmentTree(obr_vaccine_list, vaccines)
    
    def prior_vaccination(self):
        obr_prior_vaccination_list = OBR()
        obr_prior_vaccination_list.universal_service_id = ['30961-7', 'Any other vaccinations within 4 weeks prior to the date listed in #10', 'LN']

        vaccines = []

        for idx, immunization in enumerate(self.event.immunizations.all()):
            vaccine_detail = PriorVaccinationDetail(immunization)
            for seg in vaccine_detail.segments:
                vaccines.append(seg)
            
        return SegmentTree(obr_prior_vaccination_list, vaccines)


    def immunization_project(self):
        obr_project = OBR()
        obr_project.universal_service_id = 'Only for reports submitted by manufacturer/immunization project'

        project_info = VaersProjectIdentification()
        
        return SegmentTree(obr_project, project_info.segments)

    def render(self):
        observation_reports = [self.event_summary(), self.vaccine_list(), 
                               self.prior_vaccination(), self.immunization_project()]

        for idx, report in enumerate(observation_reports):
            report.parent.sequence_id = idx + 1

        patient_header = [self.make_MSH(), self.make_PID()]

        all_segments = patient_header + observation_reports
        return '\n'.join([str(x) for x in all_segments])




if __name__ == '__main__':

    events = AdverseEvent.objects.order_by('?')[:50]
    for ev in events:
        event = AdverseEvent.by_id(ev.id)
        event.save_hl7_message_file()
