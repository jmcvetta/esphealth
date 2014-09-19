ALTER TABLE emr_patient
   ADD COLUMN ethnicity character varying(100) ;

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
  ADD COLUMN patient_class character varying(50),
  ADD COLUMN patient_status character varying(50);
-- These two columns are added to determine if the prescription
-- is from a hospital setting.
ALTER TABLE emr_laborder 
  ADD COLUMN test_status character varying(5),
  ADD COLUMN patient_class character varying(50),
  ADD COLUMN patient_status character varying(50);
-- Test status indicates if the order has been processed or cancelled.
-- Patient status and class are added to determin if the order
-- is from a hospital setting.
ALTER TABLE emr_labresult
  ADD COLUMN patient_class character varying(50),
  ADD COLUMN patient_status character varying(50);
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
-- ----------------------------------------------------------------
-- 2012-11-12
-- Carolina chacin
-- ----------------------------------------------------------------
ALTER TABLE emr_encounter RENAME COLUMN o2_stat TO o2_sat;
ALTER TABLE emr_encounter RENAME COLUMN raw_o2_stat TO raw_o2_sat;
-- ----------------------------------------------------------------
-- 2013-03-04
-- Bob Zambarano
-- ----------------------------------------------------------------
ALTER TABLE emr_provenance
  ADD COLUMN raw_rec_count integer,
  ADD COLUMN insert_count integer,
  ADD COLUMN update_count integer,
  ADD COLUMN post_load_count integer;
-- ----------------------------------------------------------------
-- 2013-07-17
-- Bob Zambarano
-- ----------------------------------------------------------------
ALTER TABLE vaers_sender
  ADD COLUMN date_added date;
ALTER TABLE vaers_report_sent
  RENAME COLUMN vaers_report TO report;
ALTER TABLE vaers_report_sent
  ADD COLUMN report_type character varying(20);
-- ----------------------------------------------------------------
-- 2013-09-05
-- Bob Zambarano
-- mods to accompany redmine rev 4104
-- ----------------------------------------------------------------
ALTER TABLE conf_vaccinecodemap 
  DROP CONSTRAINT conf_vaccinecodemap_native_code_key;
-- ----------------------------------------------------------------
-- 2013-12-10
-- Bob Zambarano
-- mods to accompany conf model updates 
-- bin/esp syncdb will not create new many-to-many relationship tables
-- if the two target tables already exist.
-- (see https://code.djangoproject.com/ticket/2229)
-- New installation works fine, but for updates
-- to existing models you must run this instead.
-- ----------------------------------------------------------------
CREATE TABLE conf_labtestmap_donotsend_results (
    id serial NOT NULL,
    labtestmap_id integer NOT NULL,
    resultstring_id integer NOT NULL,
    CONSTRAINT conf_labtestmap_donotsend_results_pkey PRIMARY KEY (id ),
    CONSTRAINT conf_labtestmap_donotsend_results_resultsstring_id_fk FOREIGN KEY (resultstring_id)
      REFERENCES conf_resultstring (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT conf_labtestmap_donotsend_results_labtestmap_id_fk FOREIGN KEY (labtestmap_id)
      REFERENCES conf_labtestmap (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT conf_labtestmap_donotsend_resultstring_labtestmap_id_key UNIQUE (labtestmap_id , resultstring_id )
)
;
-- ------------------------------------------------------------------------------
-- support for icd10 codes and meaningful use 
-- 2014-04-09 CCHACIN

-- redmine 496 to expand nodis case criteria column 
ALTER TABLE nodis_case 
  ALTER COLUMN criteria TYPE character varying(2000); 

--static model changes 
ALTER TABLE static_fakeicd9s
 RENAME COLUMN fakeicd9_id TO fakedx_code_id;
ALTER TABLE static_fakeicd9s 
 RENAME COLUMN icd9_codes TO dx_codes;
ALTER TABLE static_fakeicd9s
 RENAME TO static_fakedx_codes;

ALTER TABLE static_icd9
 ADD COLUMN "type" character varying(10);
ALTER TABLE static_icd9
 RENAME COLUMN code TO combotypecode;
ALTER TABLE static_icd9 
 ADD COLUMN code character varying(10),
 ALTER COLUMN combotypecode TYPE character varying(20);
ALTER TABLE static_icd9
 RENAME TO static_dx_code;
 
UPDATE  static_dx_code SET "type" = 'icd9', code = combotypecode;
--you must run the following BEFORE loading ANY icd10 data!!!
UPDATE static_dx_code SET combotypecode='icd9:'||code 
  where type='icd9';

-- conf model changes    
ALTER TABLE  conf_conditionconfig
  RENAME COLUMN icd9_days_before TO dx_code_days_before;
ALTER TABLE  conf_conditionconfig    
  RENAME COLUMN icd9_days_after TO  dx_code_days_after;
 
ALTER TABLE conf_reportableicd9
 RENAME TO conf_reportabledx_code;
 
ALTER TABLE  conf_reportabledx_code
 RENAME COLUMN icd9_id TO dx_code_id;
ALTER TABLE  conf_reportabledx_code
  ALTER COLUMN dx_code_id TYPE character varying(20);
  
-- dependency tables for emr changes 
CREATE TABLE emr_labinfo
(
  "CLIA_ID" character varying(20) NOT NULL,
  provenance_id integer NOT NULL,
  perf_auth_nid character varying(100),
  perf_auth_uid character varying(100),
  perf_auth_uidtype character varying(100),
  perf_idtypecode character varying(100),
  laboratory_name character varying(150),
  lab_name_type_code character varying(100),
  "Lab_Director_lname" character varying(100),
  "Lab_Director_fname" character varying(100),
  "Lab_Director_mname" character varying(100),
  "Lab_Director_suff" character varying(100),
  "Lab_Director_pref" character varying(100),
  "NPI_ID" character varying(60),
  labdir_auth_nid character varying(100),
  labdir_auth_uid character varying(100),
  labdir_auth_uidtype character varying(100),
  labdir_nametypecode character varying(100),
  labdir_idtypecode character varying(100),
  labdir_fac_nid character varying(100),
  labdir_fac_uid character varying(100),
  labdir_fac_uidtype character varying(100),
  labdir_profsuff character varying(100),
  address1 character varying(200),
  address2 character varying(100),
  city character varying(50),
  state character varying(20),
  zip character varying(20),
  zip5 character varying(5),
  country character varying(60),
  addr_type character varying(10),
  county_code character varying(10),
  CONSTRAINT emr_labinfo_pkey PRIMARY KEY ("CLIA_ID"),
  CONSTRAINT emr_labinfo_provenance_id_fkey FOREIGN KEY (provenance_id)
      REFERENCES emr_provenance (provenance_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE emr_labinfo OWNER TO esp;

-- Index: emr_labinfo_provenance_id

-- DROP INDEX emr_labinfo_provenance_id;

CREATE INDEX emr_labinfo_provenance_id
  ON emr_labinfo
  USING btree
  (provenance_id);

-- Index: emr_labinfo_zip

-- DROP INDEX emr_labinfo_zip;

CREATE INDEX emr_labinfo_zip
  ON emr_labinfo
  USING btree
  (zip);

-- Index: emr_labinfo_zip5

-- DROP INDEX emr_labinfo_zip5;

CREATE INDEX emr_labinfo_zip5
  ON emr_labinfo
  USING btree
  (zip5);

-- Index: emr_labinfo_zip5_like

-- DROP INDEX emr_labinfo_zip5_like;

CREATE INDEX emr_labinfo_zip5_like
  ON emr_labinfo
  USING btree
  (zip5 varchar_pattern_ops);

-- Index: emr_labinfo_zip_like

-- DROP INDEX emr_labinfo_zip_like;

CREATE INDEX emr_labinfo_zip_like
  ON emr_labinfo
  USING btree
  (zip varchar_pattern_ops);

CREATE TABLE emr_specimen
(
  id serial NOT NULL,
  order_natural_key character varying(128),
  specimen_num character varying(100),
  laborder_id integer NOT NULL,
  provenance_id integer NOT NULL,
  fill_nid character varying(50),
  fill_uid character varying(50),
  fill_uidtype character varying(50),
  specimen_source character varying(255),
  type_modifier character varying(100),
  additives character varying(100),
  collection_method character varying(100),
  "Source_site" character varying(100),
  "Source_site_modifier" character varying(100),
  "Specimen_role" character varying(100),
  "Collection_amount" character varying(100),
  amount_id character varying(50),
  range_startdt character varying(50),
  range_enddt character varying(50),
  "Received_date" timestamp with time zone,
  creceived_date character varying(100),
  analysis_date timestamp with time zone,
  canalysis_date character varying(100),
  CONSTRAINT emr_specimen_pkey PRIMARY KEY (id),
  CONSTRAINT emr_specimen_laborder_id_fkey FOREIGN KEY (laborder_id)
      REFERENCES emr_laborder (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT emr_specimen_provenance_id_fkey FOREIGN KEY (provenance_id)
      REFERENCES emr_provenance (provenance_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT emr_specimen_order_natural_key_key UNIQUE (order_natural_key, specimen_num)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE emr_specimen OWNER TO esp;

-- Index: emr_specimen_laborder_id

-- DROP INDEX emr_specimen_laborder_id;

CREATE INDEX emr_specimen_laborder_id
  ON emr_specimen
  USING btree
  (laborder_id);

-- Index: emr_specimen_provenance_id

-- DROP INDEX emr_specimen_provenance_id;

CREATE INDEX emr_specimen_provenance_id
  ON emr_specimen
  USING btree
  (provenance_id);


 -- emr model changes 
ALTER TABLE emr_provider
ADD COLUMN   dept_country character varying(100),
ADD COLUMN   dept_county_code character varying(10),
ADD COLUMN   tel_country_code character varying(10),
ADD COLUMN   tel_ext character varying(10),
ADD COLUMN   call_info character varying(200),
ADD COLUMN   clin_address1 character varying(100),
ADD COLUMN   clin_address2 character varying(100),
ADD COLUMN   clin_city character varying(50),
ADD COLUMN   clin_state character varying(50),
ADD COLUMN   clin_zip character varying(10),
ADD COLUMN   clin_country character varying(100),
ADD COLUMN   clin_county_code character varying(10),
ADD COLUMN   clin_tel_country_code character varying(10),
ADD COLUMN   clin_areacode character varying(5),
ADD COLUMN   clin_tel character varying(10),
ADD COLUMN   clin_tel_ext character varying(10),
ADD COLUMN   clin_call_info character varying(200),
ADD COLUMN   suffix character varying(20),
ADD COLUMN   dept_addr_type character varying(20),
ADD COLUMN   clin_addr_type character varying(20);

 
ALTER TABLE emr_patient
ADD COLUMN cdate_of_birth character varying(100),
ADD COLUMN  cdate_of_death character varying(100),
ADD COLUMN   mother_maiden_name character varying(100),
ADD COLUMN   last_update timestamp with time zone,
ADD COLUMN   clast_update character varying(100),
ADD COLUMN   last_update_site character varying(100),
ADD COLUMN   title character varying(50),
ADD COLUMN   remark text,
ALTER COLUMN date_of_birth SET DATA TYPE timestamp with time zone,
ALTER COLUMN date_of_death SET DATA TYPE timestamp with time zone;
 
 
ALTER TABLE emr_labresult
RENAME COLUMN  "CLIA_ID"  TO  "CLIA_ID_id" ;
ALTER TABLE emr_labresult
ADD COLUMN    cresult_date character varying(100),
ADD COLUMN    ccollection_date character varying(100),
ADD COLUMN    ref_text character varying(100),
ADD COLUMN    collection_date_end timestamp with time zone,
ADD COLUMN    ccollection_date_end character varying(100),
ADD COLUMN    status_date timestamp with time zone,
ADD COLUMN    cstatus_date character varying(100),
ADD COLUMN    interpreter character varying(100),
ADD COLUMN    interpreter_id character varying(20),
ADD COLUMN    interp_id_auth character varying(50),
ADD COLUMN    interp_uid character varying(50),
ADD COLUMN    lab_method character varying(100),
ADD CONSTRAINT  "emr_labresult_CLIA_ID_id_fkey" FOREIGN KEY ("CLIA_ID_id")
      REFERENCES emr_labinfo ("CLIA_ID"),
ALTER COLUMN result_date SET DATA TYPE timestamp with time zone,
ALTER COLUMN collection_date SET DATA TYPE timestamp with time zone,
ALTER COLUMN patient_class TYPE character varying(50),
ALTER COLUMN patient_status TYPE character varying(50),
ALTER COLUMN status TYPE character varying(200);
         
ALTER TABLE emr_laborder
ADD COLUMN    cdate character varying(100),
ADD COLUMN    group_id character varying(15),
ADD COLUMN    reason_code character varying(15),
ADD COLUMN    reason_code_type character varying(25),
ADD COLUMN    order_info character varying(100),
ADD COLUMN    remark text,
ADD COLUMN    obs_start_date character varying(100),
ADD COLUMN    obs_end_date character varying(100),
ALTER COLUMN patient_class TYPE character varying(50),
ALTER COLUMN patient_status TYPE character varying(50);

--rename tables for many to many for emr_encounter
ALTER TABLE  emr_encounter_icd9_codes 
 RENAME COLUMN icd9_id  TO dx_code_id;
      
ALTER TABLE  emr_encounter_icd9_codes 
 RENAME TO emr_encounter_dx_codes;

ALTER TABLE  emr_encounter_dx_codes
  ALTER COLUMN dx_code_id TYPE character varying(20);
  
ALTER TABLE emr_problem 
 RENAME COLUMN icd9_id TO dx_code_id;

ALTER TABLE  emr_problem
  ALTER COLUMN dx_code_id TYPE character varying(20);
ALTER TABLE  emr_problem
  DROP COLUMN raw_icd9_code;
  
ALTER TABLE emr_hospital_problem
 DROP COLUMN raw_icd9_code ;
ALTER TABLE emr_hospital_problem
 RENAME COLUMN icd9_id TO dx_code_id;
 
ALTER TABLE  emr_hospital_problem
  ALTER COLUMN dx_code_id TYPE character varying(20);

 -- vaers model changes 
ALTER TABLE  vaers_excludedicd9code
 RENAME TO vaers_excludeddx_code;
ALTER TABLE  vaers_excludeddx_code
 ADD COLUMN   "type" character varying(10)  NULL;
 
UPDATE vaers_excludeddx_code SET "type" = 'icd9';
  
--rename tables for many to many for diagnosiseventrule
ALTER TABLE   vaers_diagnosticseventrule_heuristic_defining_codes 
 RENAME COLUMN icd9_id  TO dx_code_id;
 
ALTER TABLE  vaers_diagnosticseventrule_heuristic_defining_codes
  ALTER COLUMN dx_code_id TYPE character varying(20);

ALTER TABLE  vaers_diagnosticseventrule_heuristic_discarding_codes 
  RENAME COLUMN icd9_id  TO dx_code_id;
   
ALTER TABLE  vaers_diagnosticseventrule_heuristic_discarding_codes
  ALTER COLUMN dx_code_id TYPE character varying(20);
    
ALTER TABLE emr_prescription
 ALTER COLUMN patient_class TYPE character varying(50),
 ALTER COLUMN patient_status TYPE character varying(50);

ALTER TABLE emr_immunization
 ALTER COLUMN patient_class TYPE character varying(50),
 ALTER COLUMN patient_status TYPE character varying(50);

--straggling changes from MU updates
ALTER TABLE emr_laborder
 ADD COLUMN parent_res character varying(128);
ALTER TABLE emr_labresult_details
 ALTER COLUMN ref_range TYPE character varying(30),
 ADD COLUMN comment_type character varying(5),
 ADD COLUMN comment_source character varying(5);
 
--- aug 2014 reportables requeueing feature in case report
ALTER TABLE	nodis_case
	ADD COLUMN reportables text;
	 
 --change to conf_conditionconfig to support condtion-specific case detail pages
 --8/26/2014
 ALTER TABLE conf_conditionconfig
   ADD COLUMN url_name character varying(100);
-- 8/3/2014 redmine 516
-- changing to allow nulls in native_codes reportable labs 
ALTER TABLE conf_reportablelab 
  DROP COLUMN output_code,
  DROP COLUMN native_code,
  DROP COLUMN snomed_pos,
  DROP COLUMN snomed_neg,
  DROP COLUMN snomed_ind;
