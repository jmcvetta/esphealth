-- ----------------------------------------------------------------
-- 2012-10-08
-- ----------------------------------------------------------------
ALTER TABLE emr_provenance
   ADD COLUMN data_date date;

-- Populate the data_date for provenance records that already exist.
UPDATE emr_provenance
   SET data_date = to_date(substring(source, E'.*\\.(\\d{8})$'),
                           'MMDDYYYY')
 WHERE data_date is null
   AND char_length(substring(source, E'.*\\.(\\d{8})$')) = 8;
COMMIT;
-- ----------------------------------------------------------------
-- 2012-10-08
-- Bob Zambarano
-- ----------------------------------------------------------------
ALTER TABLE emr_labresult
   ADD COLUMN order_type character varying(20);
-- This would have to be populated via load_epic.  This is a field 
-- that has been provided but never loaded.  So the --reload option
-- could be used with archived data files.
ALTER TABLE emr_encounter
   ADD COLUMN hosp_admit_dt date,
   ADD COLUMN hosp_dschrg_dt date;
CREATE INDEX emr_encounter_hosp_admit_dt
  ON emr_encounter
  USING btree
  (hosp_admit_dt);
CREATE INDEX emr_encounter_hosp_dschrg_dt
  ON emr_encounter
  USING btree
  (hosp_dschrg_dt);
-- These are new v3 columns and would be populated via load_epic
-- They are added to the end of the previous standard record, so
-- there is no problem with loading epic data without these 
-- fields. If your data source does not include these columns
-- it may be most efficient to skip building the indexes. Django
-- will not complain if the indexes don't exist.
ALTER TABLE emr_encounter
   ADD COLUMN cpt character varying(20);
CREATE INDEX emr_encounter_cpt
   ON emr_encounter
   USING btree
   (cpt);
-- This is a field that has been provided in v2 epic data, but 
-- has never been loaded.  It is now included in the model.
-- To populate, you would need to run load_epic with the --reload
-- option.
ALTER TABLE static_icd9
   ADD COLUMN longname character varying(1000);
-- This column is added to support a feature request regarding
-- the clinician's inbasket message at MetroHealth.  It is not 
-- a required field for any other feature.  It is used in 
-- vaers/hl7_clinbasket.py.  If you are not running vaers detection
-- at your site, you don't need to insert data to this new column.
-- If you are running vaers, it would be best to drop the old
-- version of the table, rebuild via syncdb, then load_data from
-- the static/fixtures/icd9.json file.
ALTER TABLE vaers_adverseevent
   ADD COLUMN version character varying(20);
-- This column is added to support a feature request from
-- MetroHealth.  Data is inserted to this field along with new 
-- VAERS AEs, and the value is set from vaers.py
-- ----------------------------------------------------------------
-- 2012-10-10
-- Bob Zambarano
-- ----------------------------------------------------------------
ALTER TABLE emr_problem
   ADD COLUMN hospital_pl_yn character varying(1);
-- This column is added to provide a means of 
-- determining if the problem was recorded in a hospital setting.
-- Values should be limited to  "Y" or null.
ALTER TABLE emr_prescription 
  ADD COLUMN patient_class character varying(5),
  ADD COLUMN patient_status character varying(5);
-- These two columns are added to determine if the prescription
-- is from a hospital setting.
ALTER TABLE emr_laborder 
  ADD COLUMN test_status character varying(5),
  ADD COLUMN patient_class character varying(5),
  ADD COLUMN patient_status character varying(5);
-- Test status indicates if the order has been processed or cancelled.
-- Patient status and class are added to determin if the order
-- is from a hospital setting.
ALTER TABLE emr_labresult
  ADD COLUMN patient_class character varying(5),
  ADD COLUMN patient_status character varying(5);
-- These two columns are added to determine if the lab
-- is from a hospital setting.
ALTER TABLE emr_patient ALTER COLUMN country TYPE character varying(60);
-- Country can be longer than 20 characters. 
ALTER TABLE vaers_report_sent
  ADD COLUMN questionnaire_id integer;
ALTER TABLE vaers_report_sent 
  ALTER COLUMN questionnaire_id SET NOT NULL;
ALTER TABLE vaers_report_sent
  ADD CONSTRAINT vaers_report_sent_questionnaire_id_fkey FOREIGN KEY (questionnaire_id)
      REFERENCES vaers_questionnaire (id);
-- Added a foreign key reference to questionnaire id, since each VAERS report
-- represent transmission based first on creation of a specific questionnaire.




