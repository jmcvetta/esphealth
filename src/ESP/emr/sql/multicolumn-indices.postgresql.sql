--------------------------------------------------------------------------------
--
--                           Multi-Column Indices
--
--
-- These indices provide significant performance improvements for our queries.
--------------------------------------------------------------------------------
CREATE INDEX emr_labresult_native_code_and_result_float ON emr_labresult (native_code, result_float);
CREATE INDEX emr_labresult_native_code_and_result_string ON emr_labresult (native_code, result_string);
CREATE INDEX emr_labresult_code_high_float ON emr_labresult (native_code, ref_high_float, result_float);
CREATE INDEX emr_labresult_ts_native_code_and_result_float ON emr_labresult (updated_timestamp, native_code, result_float);
CREATE INDEX emr_labresult_ts_native_code_and_result_string ON emr_labresult (updated_timestamp, native_code, result_string);
CREATE INDEX emr_labresult_ts_code_high_float ON emr_labresult (updated_timestamp, native_code, ref_high_float, result_float);
CREATE INDEX emr_labresult_native_code_native_name ON emr_labresult (native_code, native_name);
CREATE INDEX emr_encounter_patient_date ON emr_encounter (patient_id, date);
CREATE INDEX emr_encounter_patient_edc ON emr_encounter (patient_id, edc);
CREATE INDEX emr_encounter_patient_date_edc ON emr_encounter (patient_id, date, edc);
CREATE INDEX emr_prescription_ts_name_like ON emr_prescription (updated_timestamp, name text_pattern_ops);
