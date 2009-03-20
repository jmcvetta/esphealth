from core import VERSION, ENCODING
from core import Segment, Field

class MSH(Segment):
    Fields = [
        Field('key', 'MSH'),
        Field('encoding', default=ENCODING),
        Field('sending_application'),
        Field('sending_facility'), 
        Field('receiving_application'),
        Field('receiving_facility'),
        Field('time'),
        Field('security'),
        Field('message_type'),
        Field('processing_id'),
        Field('version', default=VERSION),
        Field('sequence_number'),
        Field('continuation_number'),
        Field('application_ack_type'),
        Field('accept_ack_type'),
        Field('country_code')
        ]



class PID(Segment):
    Fields = [
        Field('key', 'PID'),
        Field('patient_external_id'),
        Field('patient_internal_id'),
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
        Field('patient_language'),
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
        Field('veteran_military_status')
        ]

class ORC(Segment):
    Fields = [
        Field('key', 'ORC'),
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
    Fields = [
        Field('key', 'OBR'),
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
        Field('reason_for_study'),
        Field('principal_result_interpreter'),
        Field('assistant_result_interpreter'),
        Field('technician'),
        Field('transcriptionist'),
        Field('schedule_datetime')
        ]

class OBX(Segment):
    Fields = [
        Field('key', 'OBX'),
        Field('value_type'),
        Field('id'),
        Field('sub_id'),
        Field('value'),
        Field('units'),
        Field('references_range'),
        Field('abnormal_flags'),
        Field('probability'),
        Field('nature_of_abnormal_result'),
        Field('date_last_observed_normal_values'),
        Field('user_defined_access_checks'),
        Field('date'),
        Field('producer_id'),
        Field('responsible_observer')
        ]
        
        
        


























        

























               
