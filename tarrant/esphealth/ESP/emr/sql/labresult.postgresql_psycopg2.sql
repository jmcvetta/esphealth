--------------------------------------------------------------------------------
--
--                           Multi-Column Indices
--
--
-- These indices provide significant performance improvements for our queries.
--------------------------------------------------------------------------------
CREATE INDEX emr_labresult_native_code_result_float ON emr_labresult (native_code, result_float);
CREATE INDEX emr_labresult_native_code_result_string ON emr_labresult (native_code, result_string);
CREATE INDEX emr_labresult_code_high_float ON emr_labresult (native_code, ref_high_float, result_float);
CREATE INDEX emr_labresult_ts_native_code_and_result_float ON emr_labresult (updated_timestamp, native_code, result_float);
CREATE INDEX emr_labresult_ts_native_code_and_result_string ON emr_labresult (updated_timestamp, native_code, result_string);
CREATE INDEX emr_labresult_ts_code_high_float ON emr_labresult (updated_timestamp, native_code, ref_high_float, result_float);
CREATE INDEX emr_labresult_native_code_native_name ON emr_labresult (native_code, native_name);
-- Optimization for GDM report
CREATE INDEX emr_labresult_native_code_patient_date_result_float ON emr_labresult (native_code, patient_id, date, result_float);
-- Optimization for reporting
CREATE INDEX emr_labresult_patient_date_code ON emr_labresult (patient_id, date, native_code);
CREATE INDEX emr_labresult_patient_date_code_result ON emr_labresult (patient_id, date, native_code, result_float);
