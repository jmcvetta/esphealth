--since we're updating tables, we want things to stop if there are problems:
\set ON_ERROR_STOP

--drop all the  tables used in a prior pass
drop table if exists mdphnet_updated_patients;
drop table if exists esp_demographic_u;
drop table if exists esp_encounter_u;
drop table if exists esp_diagnosis_u;
drop table if exists esp_disease_u;
drop table if exists mdphnet_updated_patients;
drop table if exists mdphnet_updated_encounters;
drop table if exists mdphnet_updated_diseases;

--create the table of patients who have been updated
create table mdphnet_updated_patients as select t0.natural_key as patid from emr_patient t0,
  (select max(latest_update) as updated_timestamp from mdphnet_schema_update_history) t1 
  where t0.updated_timestamp>=t1.updated_timestamp;
alter table mdphnet_updated_patients 
  add constraint mdphnet_updated_patients_pkey primary key (patid);
vacuum analyze mdphnet_updated_patients;

--create the demog table
CREATE table esp_demographic_u AS
SELECT '1'::varchar(1) as centerid,
       pat.natural_key as patid,
       pat.date_of_birth - ('1960-01-01'::date) as birth_date,
       CASE
         WHEN UPPER(gender) in ('M','MALE') THEN 'M'::char(1)
         WHEN UPPER(gender) in ('F','FEMALE') THEN 'F'::char(1)
         WHEN UPPER(gender) = 'U' THEN 'U'::char(1)
         ELSE 'U'::char(1)
       END as sex,
       CASE
         WHEN UPPER(race) = 'HISPANIC' THEN 'Y'::char(1)
         ELSE 'U'::char(1)
       END as Hispanic,
       CASE
         WHEN UPPER(race) in ('NAT AMERICAN','ALASKAN','AMERICAN INDIAN/ALASKAN NATIVE') THEN 1
         WHEN UPPER(race) in ('ASIAN','INDIAN') THEN 2
         WHEN UPPER(race) = 'BLACK'  THEN 3
         WHEN UPPER(race) in ('NATIVE HAWAI','PACIFIC ISLANDER/HAWAIIAN') then 4
         WHEN UPPER(race) in ('CAUCASIAN','WHITE') THEN 5
         ELSE 0
       END as race,
       zip5
  FROM public.emr_patient as pat
  inner join mdphnet_updated_patients as updtpats on updtpats.patid=pat.natural_key;

--create the table of encounter ids that have been updated
create table mdphnet_updated_encounters as select t0.natural_key as encounterid from emr_encounter as t0,
  (select max(latest_update) as updated_timestamp from mdphnet_schema_update_history) as t1 
  where t0.updated_timestamp>=t1.updated_timestamp
union select t2.encounterid from esp_encounter as t2 where exists (select null from esp_demographic_u as t3,
       esp_demographic as t4 
       where t3.patid=t4.patid and t3.birth_date<>t4.birth_date and t3.patid=t2.patid);
alter table mdphnet_updated_encounters 
  add constraint mdphnet_updated_encounters_pkey primary key (encounterid);
vacuum analyze mdphnet_updated_encounters;

-- create the updated encounters table
CREATE table esp_encounter_u AS
SELECT '1'::varchar(1) as centerid,
       pat.natural_key as patid,
       enc.natural_key as encounterid,
       enc.date - ('1960-01-01'::date) as a_date,
       enc.date_closed - ('1960-01-01'::date) as d_date,
       prov.natural_key as provider,
       enc.site_name as facility_location,
       'AV'::varchar(10) as enc_type, --this is initial value for Mass League data
       enc.site_natural_key as facility_code,
       date_part('year', enc.date)::integer as enc_year,
       age_at_year_start(enc.date, pat.date_of_birth) as age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth)::varchar(5) as age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth)::varchar(5) as age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth)::varchar(5) as age_group_ms
  FROM public.emr_encounter as enc
         INNER JOIN public.emr_patient as pat ON enc.patient_id = pat.id
         LEFT JOIN public.emr_provider as prov ON enc.provider_id = prov.id
         inner join mdphnet_updated_encounters as updts on updts.encounterid=enc.natural_key;

--diagnoses are based on encounter ICD9 data, so same subset
CREATE table esp_diagnosis_u AS
SELECT '1'::varchar(1) as centerid,
       pat.natural_key as patid,
       enc.natural_key as encounterid,
       enc.date - ('1960-01-01'::date) as a_date,
       prov.natural_key as provider,
       'AV'::varchar(10) as enc_type, --this is initial value for Mass League data
       diag.icd9_id as dx,
       icd9_prefix(diag.icd9_id, 3)::varchar(4) as dx_code_3dig,
       icd9_prefix(diag.icd9_id, 4)::varchar(5) as dx_code_4dig,
       case 
         when length(icd9_prefix(diag.icd9_id, 4))=5
	   then substr(diag.icd9_id,1,6)
         else substr(diag.icd9_id,1,5)
       end as dx_code_4dig_with_dec,
       icd9_prefix(diag.icd9_id, 5)::varchar(6) as dx_code_5dig,
       case 
         when length(icd9_prefix(diag.icd9_id, 4))=6
	   then substr(diag.icd9_id,1,7)
         else substr(diag.icd9_id,1,6)
       end as dx_code_5dig_with_dec,
       enc.site_name as facility_location,
       enc.site_natural_key as facility_code,
       date_part('year', enc.date)::integer as enc_year,
       age_at_year_start(enc.date, pat.date_of_birth) as age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth)::varchar(5) as age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth)::varchar(5) as age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth)::varchar(5) as age_group_ms
  FROM public.emr_encounter as enc
         INNER JOIN public.emr_patient as pat ON enc.patient_id = pat.id
         INNER JOIN (select * from public.emr_encounter_icd9_codes 
                     where strpos(trim(icd9_id),'.')<>3
                       and length(trim(icd9_id))>=3 ) as diag ON enc.id = diag.encounter_id
         LEFT JOIN public.emr_provider as prov ON enc.provider_id = prov.id
         inner join mdphnet_updated_encounters as updtencs on updtencs.encounterid=enc.natural_key;

--create the table of disease pkey vars (patid, condition, date) that have been updated
create table mdphnet_updated_diseases as select t2.natural_key as patid, t0.condition, t0.date
  from public.nodis_case as t0
  inner join (select max(latest_update) as updated_timestamp from mdphnet_schema_update_history) as t1 
  on t0.updated_timestamp>=t1.updated_timestamp
  inner join public.emr_patient as t2 on t0.patient_id=t2.id;
alter table mdphnet_updated_diseases 
  add constraint mdphnet_updated_diseases_pkey primary key (patid, condition, date);
vacuum analyze mdphnet_updated_diseases;

CREATE table esp_disease_u AS
SELECT '1'::varchar(1) as centerid,
       pat.natural_key as patid,
       disease.condition,
       disease.date - ('1960-01-01'::date) as date,
       age_at_year_start(disease.date, pat.date_of_birth) as age_at_detect_year,
       age_group_5yr(disease.date, pat.date_of_birth)::varchar(5) as age_group_5yr,
       age_group_10yr(disease.date, pat.date_of_birth)::varchar(5) as age_group_10yr,
       age_group_ms(disease.date, pat.date_of_birth)::varchar(5) as age_group_ms,
       disease.criteria,
       disease.status,
       disease.notes
  FROM public.nodis_case as disease
         INNER JOIN public.emr_patient as pat ON disease.patient_id = pat.id
	 inner join mdphnet_updated_diseases as updt on 
                 updt.condition=disease.condition and updt.date=disease.date
  where updt.patid=pat.natural_key;

--Now that update sets are pulled,
--add timestamp to current history, as the point where then next update should start from
--  (delete the new history record if you need to restart the process from this point.)
insert into mdphnet_schema_update_history
  select current_timestamp, count(*) from mdphnet_updated_patients;

--now update the UVTs with primary>>foreign keys 
--    UVT_SEX
      insert into UVT_SEX 
      SELECT DISTINCT
             pat.sex as item_code,
             CASE
               WHEN pat.sex = 'M' THEN 'Male'::varchar(10)
               WHEN pat.sex = 'F' THEN 'Female'::varchar(10)
               WHEN pat.sex = 'U' THEN 'Unknown'::varchar(10)
               ELSE 'Not Mapped'::varchar(10)
             END as item_text
        FROM esp_demographic_u as pat
        where not exists (select null from uvt_sex as t0 where t0.item_code=pat.sex);

--    UVT_RACE
      insert into UVT_RACE 
      SELECT DISTINCT
             pat.race as item_code,
             CASE
               WHEN pat.race = 0 THEN 'Unknown'::varchar(50)
               WHEN pat.race = 1 THEN 'American Indian or Alaska Native'::varchar(50)
               WHEN pat.race = 2 THEN 'Asian'::varchar(50)
               WHEN pat.race = 3 THEN 'Black or African American'::varchar(50)
               WHEN pat.race = 4 THEN 'Native Hawaiian or Other Pacific Islander'::varchar(50)
               WHEN pat.race = 5 THEN 'White'::varchar(50)
               ELSE 'Not Mapped'::varchar(50)
             END as item_text
        FROM esp_demographic_u as pat
        where not exists (select null from uvt_race as t0 where t0.item_code=pat.race);

--    UVT_CENTER
      insert into UVT_CENTER 
      SELECT DISTINCT
             pat.centerid as item_code,
             pat.centerid as item_text
        FROM esp_demographic_u as pat
        where not exists (select null from uvt_center as t0 where t0.item_code=pat.centerid);

--    UVT_ZIP5
      insert into UVT_ZIP5
      select distinct 
             pat.zip5 as item_code,
             null::varchar(10) as item_text
      from esp_demographic_u as pat
      where not exists (select null from uvt_zip5 as t0 where t0.item_code=pat.zip5);

--    UVT_PROVIDER
      insert into UVT_PROVIDER 
      SELECT DISTINCT
             enc.provider as item_code,
             ''::varchar(10) as item_text
        FROM esp_encounter_u as enc
        where not exists (select null from uvt_provider as t0 where t0.item_code=enc.provider);

--    UVT_SITE
      insert into UVT_SITE
      SELECT DISTINCT
             enc.facility_code as item_code,
             enc.facility_location as item_text
        FROM esp_encounter_u as enc 
          where enc.facility_code is not null
          and not exists (select null from uvt_site as t0 where t0.item_code=enc.facility_code); 

--    UVT_PERIOD
      insert into UVT_PERIOD
      SELECT DISTINCT
             enc.enc_year as item_code,
             enc.enc_year::varchar(4) as item_text
        FROM esp_encounter_u as enc
        where not exists (select null from uvt_period as t0 where t0.item_code=enc.enc_year);

--    UVT_ENCOUNTER
      insert into UVT_ENCOUNTER
      SELECT DISTINCT
             enc.enc_type as item_code,
             CASE
               WHEN enc.enc_type = 'IP' THEN 'Inpatient Hospital Stay'
               WHEN enc.enc_type = 'IS' THEN 'Non-Acute Institutional Stay'
               WHEN enc.enc_type = 'ED' THEN 'Emergency Department'
               WHEN enc.enc_type = 'AV' THEN 'Ambulatory Visit'
               WHEN enc.enc_type = 'OA' THEN 'Other Ambulatory Visit'
               ELSE 'Not Mapped'
             END as item_text
        FROM esp_encounter_u as enc
        where not exists (select null from uvt_encounter as t0 where t0.item_code=enc.enc_type);

--    UVT_AGEGROUP_5YR
      insert into UVT_AGEGROUP_5YR
      SELECT DISTINCT
             enc.age_group_5yr as item_code,
             enc.age_group_5yr::varchar(5) as item_text
        FROM esp_encounter_u as enc 
       where enc.age_group_5yr is not null
             and not exists (select null from uvt_agegroup_5yr as t0 where t0.item_code=enc.age_group_5yr);

--    UVT_AGEGROUP_10YR
      insert into UVT_AGEGROUP_10YR
      SELECT DISTINCT
             enc.age_group_10yr as item_code,
             enc.age_group_10yr::varchar(5) as item_text
        FROM esp_encounter_u as enc 
       where enc.age_group_10yr is not null
             and not exists (select null from uvt_agegroup_10yr as t0 where t0.item_code=enc.age_group_10yr);

--    UVT_AGEGROUP_MS
      insert into UVT_AGEGROUP_MS 
      SELECT DISTINCT
             enc.age_group_ms as item_code,
             enc.age_group_ms::varchar(5) as item_text
        FROM esp_encounter_u as enc where enc.age_group_ms is not null
           and not exists (select null from uvt_agegroup_ms as t0 where t0.item_code=enc.age_group_ms);

--    UVT_DX
      insert into UVT_DX
      SELECT DISTINCT
             diag.dx as item_code,
             icd9.name as item_text
        FROM esp_diagnosis_u as diag
               INNER JOIN public.static_icd9 as icd9 ON diag.dx = icd9.code
           where not exists (select null from uvt_dx as t0 where t0.item_code=diag.dx);

--    UVT_DX_3DIG
      insert into UVT_DX_3DIG
      SELECT DISTINCT
             diag.dx_code_3dig as item_code,
             icd9.name as item_text
        FROM esp_diagnosis_u as diag
               LEFT OUTER JOIN  (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) as icd9 
               ON diag.dx_code_3dig = REPLACE(icd9.code, '.', '')
        WHERE diag.dx_code_3dig is not null and icd9.name not like '%load_epic%'
           and not exists (select null from uvt_dx_3dig as t0 where t0.item_code=diag.dx_code_3dig);

--    UVT_DX_4DIG
      insert into UVT_DX_4DIG 
      SELECT DISTINCT
             diag.dx_code_4dig as item_code,
             diag.dx_code_4dig_with_dec as item_code_with_dec,
             icd9.name as item_text
        FROM esp_diagnosis_u as diag
               LEFT OUTER JOIN  (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=4 ) as icd9
               ON diag.dx_code_4dig_with_dec = icd9.code
        WHERE diag.dx_code_4dig is not null and icd9.name not like '%load_epic%'
         and not exists (select null from uvt_dx_4dig as t0 where t0.item_code=diag.dx_code_4dig);

--    UVT_DX_5DIG
      insert into UVT_DX_5DIG
      SELECT DISTINCT
             diag.dx_code_5dig as item_code,
             diag.dx_code_5dig_with_dec as item_code_with_dec,
             icd9.name as item_text
        FROM esp_diagnosis_u as diag
               LEFT OUTER JOIN  (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) as icd9
               ON diag.dx_code_5dig_with_dec = icd9.code
        WHERE diag.dx_code_5dig is not null and icd9.name not like '%load_epic%'
          and not exists (select null from uvt_dx_5dig as t0 where t0.item_code=diag.dx_code_5dig);

--    UVT_DETECTED_CONDITION
      insert into UVT_DETECTED_CONDITION 
      SELECT DISTINCT
             disease.condition as item_code,
             disease.condition as item_text
        FROM esp_disease_u as disease
         where not exists (select null from uvt_detected_condition as t0 where t0.item_code=disease.condition);
      
--    UVT_DETECTED_CRITERIA
      insert into UVT_DETECTED_CRITERIA
      SELECT DISTINCT
             disease.criteria as item_code,
             disease.criteria as item_text
        FROM esp_disease_u as disease
          where disease.criteria is not null
            and not exists (select null from uvt_detected_criteria as t0 where t0.item_code=disease.criteria);
      
--    UVT_DETECTED_STATUS
      insert into UVT_DETECTED_STATUS 
      SELECT DISTINCT
             disease.status as item_code,
             CASE
               WHEN disease.status = 'AR' THEN 'Awaiting Review'::varchar(80)
               WHEN disease.status = 'UR' THEN 'Under Review'::varchar(80)
               WHEN disease.status = 'RM' THEN 'Review By MD'::varchar(80)
               WHEN disease.status = 'FP' THEN 'False Positive - Do Not Process'::varchar(80)
               WHEN disease.status = 'Q'  THEN 'Confirmed Case, Transmit to Health Department'::varchar(80)
               WHEN disease.status = 'S'  THEN 'Transmitted to Health Department'::varchar(80)
               ELSE 'Not Mapped'::varchar(80)
             END as item_text
        FROM esp_disease_u as disease
          where not exists (select null from uvt_detected_status as t0 where t0.item_code=disease.status);

--now clear out the old patient data from each of the main tables
-- NB: dropping and recreating indexes takes more time than just loading a day or two's updates
delete from esp_disease
  where exists(select null from mdphnet_updated_diseases
               where mdphnet_updated_diseases.patid=esp_disease.patid
                     and mdphnet_updated_diseases.condition=esp_disease.condition
                     and mdphnet_updated_diseases.date - ('1960-01-01'::date)=esp_disease.date);
delete from esp_diagnosis
  where exists(select null from mdphnet_updated_encounters 
               where mdphnet_updated_encounters.encounterid=esp_diagnosis.encounterid);
delete from esp_encounter
where exists(select null from mdphnet_updated_encounters 
               where mdphnet_updated_encounters.encounterid=esp_encounter.encounterid);
--can't delete from demographic, due to FK constaints on PATID.

--first update the demographic data, where it has been updated, then insert the new data
update esp_demographic as t0
  set centerid=t1.centerid,
      birth_date=t1.birth_date,
      sex=t1.sex,
      hispanic=t1.hispanic,
      race=t1.race,
      zip5=t1.zip5
  from (select *
        from esp_demographic_u) as t1
  where t1.patid=t0.patid;
insert into esp_demographic select * from esp_demographic_u
   as t0 where not exists (select null from esp_demographic as t1 where t1.patid=t0.patid);
insert into esp_encounter select * from esp_encounter_u;
insert into esp_diagnosis select * from esp_diagnosis_u;
insert into esp_disease select * from esp_disease_u;

--now vacuum analyze each table
vacuum analyze esp_demographic;
vacuum analyze esp_encounter;
vacuum analyse esp_diagnosis;
vacuum analyse esp_disease;
/*
--now rerun the summary table creation.  This actually takes the longest of all the 
--Create the summary table for 3-digit ICD9 codes and populate it with information for the 5 year age groups
drop table if exists esp_diagnosis_icd9_3dig_new;
CREATE TABLE esp_diagnosis_icd9_3dig_new AS
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 5yr'::varchar(15) age_group_type, diag.age_group_5yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_3dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_5yr, pat.sex, diag.enc_year, diag.dx_code_3dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9 
                 ON t1.code_ = replace(icd9.code, '.', '')
UNION
-- Add the summary information for the 10 year age groups
-- INSERT INTO esp_diagnosis_icd9_3dig
--        (centerid, age_group_type, age_group, sex, period, code_, setting, members, events, dx_name)
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 10yr'::varchar(15) age_group_type, diag.age_group_10yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_3dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_10yr, pat.sex, diag.enc_year, diag.dx_code_3dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '')
UNION
-- Add the summary information for the mini-Sentinel age groups
-- INSERT INTO esp_diagnosis_icd9_3dig
--        (centerid, age_group_type, age_group, sex, period, code_, setting, members, events, dx_name)
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group MS'::varchar(15) age_group_type, diag.age_group_ms age_group,
               pat.sex, diag.enc_year period, diag.dx_code_3dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_ms, pat.sex, diag.enc_year, diag.dx_code_3dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '');
create index diag3dig_centerid_idx_new on esp_diagnosis_icd9_3dig_new (centerid);
create index diag3dig_age_group_type_idx_new on esp_diagnosis_icd9_3dig_new (age_group_type);
create index diag3dig_age_group_idx_new on esp_diagnosis_icd9_3dig_new (age_group);
create index diag3dig_sex_idx_new on esp_diagnosis_icd9_3dig_new (sex);
create index diag3dig_period_idx_new on esp_diagnosis_icd9_3dig_new (period);
create index diag3dig_code_idx_new on esp_diagnosis_icd9_3dig_new (code_);
create index diag3dig_setting_idx_new on esp_diagnosis_icd9_3dig_new (setting);
drop table if exists esp_diagnosis_icd9_3dig;
alter table esp_diagnosis_icd9_3dig_new rename to esp_diagnosis_icd9_3dig;
alter index diag3dig_centerid_idx_new rename to diag3dig_centerid_idx;
alter index diag3dig_age_group_type_idx_new rename to diag3dig_age_group_type_idx;
alter index diag3dig_age_group_idx_new rename to diag3dig_age_group_idx;
alter index diag3dig_sex_idx_new rename to diag3dig_sex_idx;
alter index diag3dig_period_idx_new rename to diag3dig_period_idx;
alter index diag3dig_code_idx_new rename to diag3dig_code_idx;
alter index diag3dig_setting_idx_new rename to diag3dig_setting_idx;

-- Create the summary table for 4-digit ICD9 codes and populate it with information for the 5 year age groups
drop table if exists esp_diagnosis_icd9_4dig_new;
CREATE TABLE esp_diagnosis_icd9_4dig_new AS
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 5yr'::varchar(15) age_group_type, diag.age_group_5yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_4dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_5yr, pat.sex, diag.enc_year, diag.dx_code_4dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '')
UNION
-- Add the summary information for the 10 year age groups
-- INSERT INTO esp_diagnosis_icd9_4dig
--        (centerid, age_group_type, age_group, sex, period, code_, setting, members, events, dx_name)
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 10yr'::varchar(15) age_group_type, diag.age_group_10yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_4dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_10yr, pat.sex, diag.enc_year, diag.dx_code_4dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '')
UNION
-- Add the summary information for the mini-Sentinel age groups
-- INSERT INTO esp_diagnosis_icd9_4dig
--        (centerid, age_group_type, age_group, sex, period, code_, setting, members, events, dx_name)
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group MS'::varchar(15) age_group_type, diag.age_group_ms age_group,
               pat.sex, diag.enc_year period, diag.dx_code_4dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_ms, pat.sex, diag.enc_year, diag.dx_code_4dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '');
create index diag4dig_centerid_idx_new on esp_diagnosis_icd9_4dig_new (centerid);
create index diag4dig_age_group_type_idx_new on esp_diagnosis_icd9_4dig_new (age_group_type);
create index diag4dig_age_group_idx_new on esp_diagnosis_icd9_4dig_new (age_group);
create index diag4dig_sex_idx_new on esp_diagnosis_icd9_4dig_new (sex);
create index diag4dig_period_idx_new on esp_diagnosis_icd9_4dig_new (period);
create index diag4dig_code_idx_new on esp_diagnosis_icd9_4dig_new (code_);
create index diag4dig_setting_idx_new on esp_diagnosis_icd9_4dig_new (setting);
drop table if exists esp_diagnosis_icd9_4dig;
alter table esp_diagnosis_icd9_4dig_new rename to esp_diagnosis_icd9_4dig;
alter index diag4dig_centerid_idx_new rename to diag4dig_centerid_idx;
alter index diag4dig_age_group_type_idx_new rename to diag4dig_age_group_type_idx;
alter index diag4dig_age_group_idx_new rename to diag4dig_age_group_idx;
alter index diag4dig_sex_idx_new rename to diag4dig_sex_idx;
alter index diag4dig_period_idx_new rename to diag4dig_period_idx;
alter index diag4dig_code_idx_new rename to diag4dig_code_idx;
alter index diag4dig_setting_idx_new rename to diag4dig_setting_idx;

-- Create the summary table for 5-digit ICD9 codes and populate it with information for the 5 year age groups
drop table if exists esp_diagnosis_icd9_5dig_new;
CREATE TABLE esp_diagnosis_icd9_5dig_new
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 5yr'::varchar(15) age_group_type, diag.age_group_5yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_5dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_5yr, pat.sex, diag.enc_year, diag.dx_code_5dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '')
UNION
-- Add the summary information for the 10 year age groups
-- INSERT INTO esp_diagnosis_icd9_5dig
--        (centerid, age_group_type, age_group, sex, period, code_, setting, members, events, dx_name)
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 10yr'::varchar(15) age_group_type, diag.age_group_10yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_5dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_10yr, pat.sex, diag.enc_year, diag.dx_code_5dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '')
UNION
-- Add the summary information for the mini-Sentinel age groups
-- INSERT INTO esp_diagnosis_icd9_5dig
--        (centerid, age_group_type, age_group, sex, period, code_, setting, members, events, dx_name)
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group MS'::varchar(15) age_group_type, diag.age_group_ms age_group,
               pat.sex, diag.enc_year period, diag.dx_code_5dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_ms, pat.sex, diag.enc_year, diag.dx_code_5dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '');
create index diag5dig_centerid_idx_new on esp_diagnosis_icd9_5dig_new (centerid);
create index diag5dig_age_group_type_idx_new on esp_diagnosis_icd9_5dig_new (age_group_type);
create index diag5dig_age_group_idx_new on esp_diagnosis_icd9_5dig_new (age_group);
create index diag5dig_sex_idx_new on esp_diagnosis_icd9_5dig_new (sex);
create index diag5dig_period_idx_new on esp_diagnosis_icd9_5dig_new (period);
create index diag5dig_code_idx_new on esp_diagnosis_icd9_5dig_new (code_);
create index diag5dig_setting_idx_new on esp_diagnosis_icd9_5dig_new (setting);
drop table if exists esp_diagnosis_icd9_5dig;
alter table esp_diagnosis_icd9_5dig_new rename to esp_diagnosis_icd9_5dig;
alter index diag5dig_centerid_idx_new rename to diag5dig_centerid_idx;
alter index diag5dig_age_group_type_idx_new rename to diag5dig_age_group_type_idx;
alter index diag5dig_age_group_idx_new rename to diag5dig_age_group_idx;
alter index diag5dig_sex_idx_new rename to diag5dig_sex_idx;
alter index diag5dig_period_idx_new rename to diag5dig_period_idx;
alter index diag5dig_code_idx_new rename to diag5dig_code_idx;
alter index diag5dig_setting_idx_new rename to diag5dig_setting_idx;
*/
