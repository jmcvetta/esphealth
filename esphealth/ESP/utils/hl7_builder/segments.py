#!/usr/bin/python
# -*- coding: utf-8 -*-

from core import VERSION, ENCODING
from core import Segment, Field

class MSH(Segment):
    '''
    MSH is used as the message header section
    '''
    Fields = [
        Field('encoding', default=ENCODING),
        Field('sending_application'),
        Field('sending_facility'), 
        Field('receiving_application'),
        Field('receiving_facility'),
        Field('time'),
        Field('security'),
        Field('message_type'),
        Field('message_control_id'),
        Field('processing_id'),
        Field('version', default=VERSION),
        Field('sequence_number'),
        Field('continuation_number'),
        Field('accept_ack_type'),
        Field('application_ack_type'),
        Field('country_code'),
        Field('charset'),
        Field('principal_language_of_message'),
        Field('Alternate_charset')
        ]


class PID(Segment):
    '''
    PID is used as a patient identification section
    '''
    Fields = [
        Field('set_id', serial=True),
        Field('patient_internal_id'),
        Field('patient_external_id'),
        Field('alternate_patient_id'),
        Field('patient_name'),
        Field('mother_maiden_name'),
        Field('date_of_birth'),
        Field('sex'),
        Field('alias'),
        Field('race'),
        Field('patient_address'),
        Field('country_code'),
        Field('home_phone'),
        Field('business_phone'),
        Field('primary_language'),
        Field('marital_status'),
        Field('religion'),
        Field('patient_account'),
        Field('ssn_number'),
        Field('driver_license'),
        Field('mother_identifier'),
        Field('ethnic_group'),
        Field('birth_place'),
        Field('multiple_birth_indicator'),
        Field('birth_order'),
        Field('citizenship'),
        Field('veteran_military_status'),
        Field('nationality'),
        Field('death_datetime'),
        Field('death_indicator')
        ]


class NK1(Segment):
    '''
    NK1 contains information about the patient's other related parties
    '''
    Fields = [
        Field('set_id', serial=True),
        Field('name'),
        Field('relationship'),
        Field('address'),
        Field('phone_number'),
        Field('business_phone_number'),
        Field('contact_role'),
        Field('start_date'),
        Field('end_date'),
        Field('associated_parties_job_title'),
        Field('associated_parties_job_code'),
        Field('associated_parties_employee_number'),
        Field('organization_name'),
        Field('marital_status'),
        Field('sex'),
        Field('date_of_birth'),
        Field('living_dependency'),
        Field('ambulatory_status'),
        Field('citizenship'),
        Field('primary_language'),
        Field('living_arrangement'),
        Field('publicity_indicator'),
        Field('protection_indicator'),
        Field('student_indicator'),
        Field('religion'),
        Field('mother_maiden_name'),
        Field('nationality'),
        Field('ethnic_group'),
        Field('contact_reason'),
        Field('contact_name'),
        Field('contact_phone_number'),
        Field('contact_address'),
        Field('associated_party_identifiers'),
        Field('job_status'),
        Field('race'),
        Field('handicap'),
        Field('contact_person_ssn')
        ]


class ORC(Segment):
    '''
    The ORC segment is used for order information
    '''
    Fields = [
        Field('control'),
        Field('placer_number'),
        Field('filler_number'),
        Field('placer_group_number'),
        Field('status'),
        Field('response_flag'),
        Field('quantity'),
        Field('parent'),
        Field('transaction_datetime'),
        Field('entered_by'),
        Field('verified_by'),
        Field('ordering_provider'),
        Field('enterer_location'),
        Field('callback_phone'),
        Field('effective_datetime'),
        Field('control_reason_code'),
        Field('entering_organization'),
        Field('entering_device'),
        Field('action_by')
        ]
        

class OBR(Segment):
    '''
    The OBR segment is used to specify observation requests
    '''
    Fields = [
        Field('set_id', serial=True),
        Field('placer_order_number'),
        Field('filler_order_number'),
        Field('universal_service_id'),
        Field('priority'),
        Field('request_date'),
        Field('observation_date'),
        Field('observation_end_date'),
        Field('collection_volume'),
        Field('collector_identifier'),
        Field('specimen_action_code'),
        Field('danger_code'),
        Field('relevant_clinical_info'),
        Field('specimen_receive_date'),
        Field('specimen_source'),
        Field('ordering_provider'),
        Field('order_callback_phone_number'),
        Field('placer_field_1'),
        Field('placer_field_2'),
        Field('filler_field_1'),
        Field('filler_field_2'),
        Field('report_status_change_date'),
        Field('charge_to_practice'),
        Field('diagnostic_serv_sect_id'),
        Field('result_status'),
        Field('parent_result'),
        Field('quantity'),
        Field('result_copies_to'),
        Field('parent'),
        Field('transportation_mode'),
        Field('reason_for_study'),
        Field('principal_result_interpreter'),
        Field('assistant_result_interpreter'),
        Field('technician'),
        Field('transcriptionist'),
        Field('schedule_datetime'),
        Field('number_samp_containers'),
        Field('transport_logistics'),
        Field('collectors_comment'),
        Field('transport_arrangement_responsibility'),
        Field('transport_arranged'),
        Field('escort_required')
        ]

class OBX(Segment):
    '''
    OBX is used to transmit a single observation or fragment.
    '''
    Fields = [
        Field('set_id', serial=True),
        Field('value_type'),
        Field('identifier'),
        Field('sub_id', subsequence=True),
        Field('value'),
        Field('units'),
        Field('references_range'),
        Field('abnormal_flags'),
        Field('probability'),
        Field('nature_of_abnormal_result'),
        Field('observation_result_status'),
        Field('date_last_observed_normal_values'),
        Field('user_defined_access_checks'),
        Field('date'),
        Field('producer_id'),
        Field('responsible_observer'),
        Field('method')
        ]

class EVN(Segment):
    '''
    EVN is used to provide event type information
    '''
    Fields = [
        Field('event_type_code'),
        Field('recorded_datetime'),
        Field('planned_datetime'),
        Field('event_reason_code'),
        Field('operator_id'),
        Field('event_occurred'),
        Field('event_facility')
        ]
    
class PV1(Segment):
    '''
    PV1 is used to provide information about a patient visit
    '''
    Fields = [
        Field('set_id'),
        Field('patient_class'),
        Field('assigned_patient_location'),
        Field('admission_type'),
        Field('preadmit_number'),
        Field('prior_patient_locator'),
        Field('attending_doctor'),
        Field('referring_doctor'),
        Field('consulting_doctor'),
        Field('hospital_service'),
        Field('temporary_location'),
        Field('preadmit_test_indicator'),
        Field('readmission_indicator'),
        Field('admit_source'),
        Field('ambulatory_status'),
        Field('vip_indicator'),
        Field('admitting_doctor'),
        Field('patient_type'),
        Field('visit_number'),
        Field('financial_class'),
        Field('charge_price_indicator'),
        Field('courtesy_code'),
        Field('credit_rating'),
        Field('contract_code'),
        Field('contract_effective_date'),
        Field('contract_amount'),
        Field('contract_period'),
        Field('interest_code'),
        Field('transfer_to_bad_debt_code'),
        Field('transfer_to_bad_debt_date'),
        Field('bad_debt_agency_code'),
        Field('bad_debt_transfer_amount'),
        Field('bad_debt_recover_amount'),
        Field('delete_acount_indicator'),
        Field('delete_account_date'),
        Field('discharge_disposition'),
        Field('discharged_to_location'),
        Field('diet_type'),
        Field('servicing_facility'),
        Field('bed_status'),
        Field('account_status'),
        Field('pending_location'),
        Field('prior_temporary_location'),
        Field('admit_date'),
        Field('discharge_date'),
        Field('current_patient_balance'),
        Field('total_charges'),
        Field('total_adjustments'),
        Field('total_payments'),
        Field('alternate_visit_id')
        ]
    
class TXA(Segment):
    '''
    TXA Transcription report header contains information specific to a transcribed report but not text of the report
    '''
    Fields = [
        Field('set_id'),
        Field('report_type'),
        Field('document_content_presentation'),
        Field('activity_date'),
        Field('primary_activity_provider'),
        Field('origination_datetime'),
        Field('transcription_datetime'),
        Field('edit_datetime'),
        Field('originator_codename'),
        Field('assigned_document_authenticator'),
        Field('transcriptionist_codename'),
        Field('unique_document_number'),
        Field('parent_document_number'),
        Field('placer_id'),
        Field('order_filler_number'),
        Field('unique_document_file_name'),
        Field('document_completion_status'),
        Field('document_confidentiality_status'),
        Field('document_availability_status'),
        Field('document_storage_status'),
        Field('document_change_reason'),
        Field('authentication_person_time_stamp'),
        Field('distributed_copies')
        ]