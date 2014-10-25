--------------------------------------------------------------------------------
--
--                           Multi-Column Indices
--
--
-- These indices provide significant performance improvements for our queries.
--------------------------------------------------------------------------------
-- Optimization for reporting
CREATE INDEX emr_encounter_patient_date ON emr_encounter (patient_id, date);
CREATE INDEX emr_encounter_patient_date_bmi ON emr_encounter (patient_id, date, bmi);
CREATE INDEX emr_encounter_patient_date_height ON emr_encounter (patient_id, date, height);
CREATE INDEX emr_encounter_patient_date_weight ON emr_encounter (patient_id, date, weight);
CREATE INDEX emr_encounter_patient_edd ON emr_encounter (patient_id, edd);
CREATE INDEX emr_encounter_patient_date_edd ON emr_encounter (patient_id, date, edd);
