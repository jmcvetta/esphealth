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
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       pat.date_of_birth - ('1960-01-01'::date) birth_date,
       CASE
         WHEN UPPER(gender) = 'M' THEN 'M'::char(1)
         WHEN UPPER(gender) = 'F' THEN 'F'::char(1)
         WHEN UPPER(gender) = 'U' THEN 'U'::char(1)
         ELSE 'U'::char(1)
       END sex,
       CASE
         WHEN UPPER(race) = 'HISPANIC' THEN 'Y'::char(1)
         ELSE 'U'::char(1)
       END Hispanic,
       CASE
         WHEN UPPER(race) in ('NAT AMERICAN','ALASKAN') THEN 1
         WHEN UPPER(race) in ('ASIAN','INDIAN') THEN 2
         WHEN UPPER(race) = 'BLACK'  THEN 3
         WHEN UPPER(race) = 'NATIVE HAWAI' then 4
         WHEN UPPER(race) = 'CAUCASIAN' THEN 5
         ELSE 0
       END race,
       zip5
  FROM public.emr_patient pat
  inner join mdphnet_updated_patients updtpats on updtpats.patid=pat.natural_key;

--create the table of encounter ids that have been updated
create table mdphnet_updated_encounters as select t0.natural_key as encounterid from emr_encounter t0,
  (select max(latest_update) as updated_timestamp from mdphnet_schema_update_history) t1 
  where t0.updated_timestamp>=t1.updated_timestamp
union select t2.encounterid from esp_encounter t2 where exists (select null from esp_demographic_u t3,
       esp_demographic t4 
       where t3.patid=t4.patid and t3.birth_date<>t4.birth_date and t3.patid=t2.patid);
alter table mdphnet_updated_encounters 
  add constraint mdphnet_updated_encounters_pkey primary key (encounterid);
vacuum analyze mdphnet_updated_encounters;

-- create the updated encounters table
CREATE table esp_encounter_u AS
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       enc.natural_key encounterid,
       enc.date - ('1960-01-01'::date) a_date,
       enc.date_closed - ('1960-01-01'::date) d_date,
       prov.natural_key provider,
       enc.site_name facility_location,
       'AV'::varchar(10) as enc_type, --this is initial value for Mass League data
       enc.site_natural_key facility_code,
       date_part('year', enc.date)::integer enc_year,
       age_at_year_start(enc.date, pat.date_of_birth) age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth)::varchar(5) age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth)::varchar(5) age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth)::varchar(5) age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN public.emr_patient pat ON enc.patient_id = pat.id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id
         inner join mdphnet_updated_encounters updts on updts.encounterid=enc.natural_key;

--diagnoses are based on encounter ICD9 data, so same subset
CREATE table esp_diagnosis_u AS
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       enc.natural_key encounterid,
       enc.date - ('1960-01-01'::date) a_date,
       prov.natural_key provider,
       'AV'::varchar(10) enc_type, --this is initial value for Mass League data
       diag.icd9_id dx,
       icd9_prefix(diag.icd9_id, 3)::varchar(4) dx_code_3dig,
       icd9_prefix(diag.icd9_id, 4)::varchar(5) dx_code_4dig,
       case 
         when length(icd9_prefix(diag.icd9_id, 4))=5
	   then substr(diag.icd9_id,1,6)
         else substr(diag.icd9_id,1,5)
       end as dx_code_4dig_with_dec,
       icd9_prefix(diag.icd9_id, 5)::varchar(6) dx_code_5dig,
       case 
         when length(icd9_prefix(diag.icd9_id, 4))=6
	   then substr(diag.icd9_id,1,7)
         else substr(diag.icd9_id,1,6)
       end as dx_code_5dig_with_dec,
       enc.site_name facility_location,
       enc.site_natural_key facility_code,
       date_part('year', enc.date)::integer enc_year,
       age_at_year_start(enc.date, pat.date_of_birth) age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth)::varchar(5) age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth)::varchar(5) age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth)::varchar(5) age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN public.emr_patient pat ON enc.patient_id = pat.id
         INNER JOIN (select * from public.emr_encounter_icd9_codes 
                     where strpos(trim(icd9_id),'.')<>3
                       and length(trim(icd9_id))>=3 ) diag ON enc.id = diag.encounter_id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id
         inner join mdphnet_updated_encounters updtencs on updtencs.encounterid=enc.natural_key;

--create the table of disease pkey vars (patid, condition, date) that have been updated
create table mdphnet_updated_diseases as select t2.natural_key as patid, t0.condition, t0.date
  from public.nodis_case t0
  inner join (select max(latest_update) as updated_timestamp from mdphnet_schema_update_history) t1 
  on t0.updated_timestamp>=t1.updated_timestamp
  inner join public.emr_patient t2 on t0.patient_id=t2.id;
alter table mdphnet_updated_diseases 
  add constraint mdphnet_updated_diseases_pkey primary key (patid, condition, date);
vacuum analyze mdphnet_updated_diseases;

CREATE table esp_disease_u AS
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       disease.condition,
       disease.date - ('1960-01-01'::date) date,
       age_at_year_start(disease.date, pat.date_of_birth) age_at_detect_year,
       age_group_5yr(disease.date, pat.date_of_birth)::varchar(5) age_group_5yr,
       age_group_10yr(disease.date, pat.date_of_birth)::varchar(5) age_group_10yr,
       age_group_ms(disease.date, pat.date_of_birth)::varchar(5) age_group_ms,
       disease.criteria,
       disease.status,
       disease.notes
  FROM public.nodis_case disease
         INNER JOIN public.emr_patient pat ON disease.patient_id = pat.id
	 inner join mdphnet_updated_diseases updt on 
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
             pat.sex item_code,
             CASE
               WHEN pat.sex = 'M' THEN 'Male'::varchar(10)
               WHEN pat.sex = 'F' THEN 'Female'::varchar(10)
               WHEN pat.sex = 'U' THEN 'Unknown'::varchar(10)
               ELSE 'Not Mapped'::varchar(10)
             END item_text
        FROM esp_demographic_u pat
        where not exists (select null from uvt_sex t0 where t0.item_code=pat.sex);

--    UVT_RACE
      insert into UVT_RACE 
      SELECT DISTINCT
             pat.race item_code,
             CASE
               WHEN pat.race = 0 THEN 'Unknown'::varchar(50)
               WHEN pat.race = 1 THEN 'American Indian or Alaska Native'::varchar(50)
               WHEN pat.race = 2 THEN 'Asian'::varchar(50)
               WHEN pat.race = 3 THEN 'Black or African American'::varchar(50)
               WHEN pat.race = 4 THEN 'Native Hawaiian or Other Pacific Islander'::varchar(50)
               WHEN pat.race = 5 THEN 'White'::varchar(50)
               ELSE 'Not Mapped'::varchar(50)
             END item_text
        FROM esp_demographic_u pat
        where not exists (select null from uvt_race t0 where t0.item_code=pat.race);

--    UVT_CENTER
      insert into UVT_CENTER 
      SELECT DISTINCT
             pat.centerid item_code,
             pat.centerid item_text
        FROM esp_demographic_u pat
        where not exists (select null from uvt_center t0 where t0.item_code=pat.centerid);

--    UVT_ZIP5
      insert into UVT_ZIP5
      select distinct 
             pat.zip5 item_code,
             null::varchar(10) item_text
      from esp_demographic_u pat
      where not exists (select null from uvt_zip5 t0 where t0.item_code=pat.zip5);

--    UVT_PROVIDER
      insert into UVT_PROVIDER 
      SELECT DISTINCT
             enc.provider item_code,
             ''::varchar(10) item_text
        FROM esp_encounter_u enc
        where not exists (select null from uvt_provider t0 where t0.item_code=enc.provider);

--    UVT_SITE
      insert into UVT_SITE
      SELECT DISTINCT
             enc.facility_code item_code,
             enc.facility_location item_text
        FROM esp_encounter_u enc 
          where enc.facility_code is not null
          and not exists (select null from uvt_site t0 where t0.item_code=enc.facility_code); 

--    UVT_PERIOD
      insert into UVT_PERIOD
      SELECT DISTINCT
             enc.enc_year item_code,
             enc.enc_year::varchar(4) item_text
        FROM esp_encounter_u enc
        where not exists (select null from uvt_period t0 where t0.item_code=enc.enc_year);

--    UVT_ENCOUNTER
      insert into UVT_ENCOUNTER
      SELECT DISTINCT
             enc.enc_type item_code,
             CASE
               WHEN enc.enc_type = 'IP' THEN 'Inpatient Hospital Stay'
               WHEN enc.enc_type = 'IS' THEN 'Non-Acute Institutional Stay'
               WHEN enc.enc_type = 'ED' THEN 'Emergency Department'
               WHEN enc.enc_type = 'AV' THEN 'Ambulatory Visit'
               WHEN enc.enc_type = 'OA' THEN 'Other Ambulatory Visit'
               ELSE 'Not Mapped'
             END item_text
        FROM esp_encounter_u enc
        where not exists (select null from uvt_encounter t0 where t0.item_code=enc.enc_type);

--    UVT_AGEGROUP_5YR
      insert into UVT_AGEGROUP_5YR
      SELECT DISTINCT
             enc.age_group_5yr item_code,
             enc.age_group_5yr::varchar(5) item_text
        FROM esp_encounter_u enc 
       where enc.age_group_5yr is not null
             and not exists (select null from uvt_agegroup_5yr t0 where t0.item_code=enc.age_group_5yr);

--    UVT_AGEGROUP_10YR
      insert into UVT_AGEGROUP_10YR
      SELECT DISTINCT
             enc.age_group_10yr item_code,
             enc.age_group_10yr::varchar(5) item_text
        FROM esp_encounter_u enc 
       where enc.age_group_10yr is not null
             and not exists (select null from uvt_agegroup_10yr t0 where t0.item_code=enc.age_group_10yr);

--    UVT_AGEGROUP_MS
      insert into UVT_AGEGROUP_MS 
      SELECT DISTINCT
             enc.age_group_ms item_code,
             enc.age_group_ms::varchar(5) item_text
        FROM esp_encounter_u enc where enc.age_group_ms is not null
           and not exists (select null from uvt_agegroup_ms t0 where t0.item_code=enc.age_group_ms);

--    UVT_DX
      insert into UVT_DX
      SELECT DISTINCT
             diag.dx item_code,
             icd9.name item_text
        FROM esp_diagnosis_u diag
               INNER JOIN public.static_icd9 icd9 ON diag.dx = icd9.code
           where not exists (select null from uvt_dx t0 where t0.item_code=diag.dx);

--    UVT_DX_3DIG
      insert into UVT_DX_3DIG
      SELECT DISTINCT
             diag.dx_code_3dig item_code,
             icd9.name item_text
        FROM esp_diagnosis_u diag
               LEFT OUTER JOIN  (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9 
               ON diag.dx_code_3dig = REPLACE(icd9.code, '.', '')
        WHERE diag.dx_code_3dig is not null and icd9.name not like '%load_epic%'
           and not exists (select null from uvt_dx_3dig t0 where t0.item_code=diag.dx_code_3dig);

--    UVT_DX_4DIG
      insert into UVT_DX_4DIG 
      SELECT DISTINCT
             diag.dx_code_4dig item_code,
             diag.dx_code_4dig_with_dec item_code_with_dec,
             icd9.name item_text
        FROM esp_diagnosis_u diag
               LEFT OUTER JOIN  (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
               ON diag.dx_code_4dig = REPLACE(icd9.code, '.', '')
        WHERE diag.dx_code_4dig is not null and icd9.name not like '%load_epic%'
         and not exists (select null from uvt_dx_4dig t0 where t0.item_code=diag.dx_code_4dig);

--    UVT_DX_5DIG
      insert into UVT_DX_5DIG
      SELECT DISTINCT
             diag.dx_code_5dig item_code,
             diag.dx_code_5dig_with_dec item_code_with_dec,
             icd9.name item_text
        FROM esp_diagnosis_u diag
               LEFT OUTER JOIN  (select * from public.static_icd9
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
               ON diag.dx_code_5dig = REPLACE(icd9.code, '.', '')
        WHERE diag.dx_code_5dig is not null and icd9.name not like '%load_epic%'
          and not exists (select null from uvt_dx_5dig t0 where t0.item_code=diag.dx_code_5dig);

--    UVT_DETECTED_CONDITION
      insert into UVT_DETECTED_CONDITION 
      SELECT DISTINCT
             disease.condition item_code,
             disease.condition item_text
        FROM esp_disease_u disease
         where not exists (select null from uvt_detected_condition t0 where t0.item_code=disease.condition);
      
--    UVT_DETECTED_CRITERIA
      insert into UVT_DETECTED_CRITERIA
      SELECT DISTINCT
             disease.criteria item_code,
             disease.criteria item_text
        FROM esp_disease_u disease
          where disease.criteria is not null
            and not exists (select null from uvt_detected_criteria t0 where t0.item_code=disease.criteria);
      
--    UVT_DETECTED_STATUS
      insert into UVT_DETECTED_STATUS 
      SELECT DISTINCT
             disease.status item_code,
             CASE
               WHEN disease.status = 'AR' THEN 'Awaiting Review'::varchar(80)
               WHEN disease.status = 'UR' THEN 'Under Review'::varchar(80)
               WHEN disease.status = 'RM' THEN 'Review By MD'::varchar(80)
               WHEN disease.status = 'FP' THEN 'False Positive - Do Not Process'::varchar(80)
               WHEN disease.status = 'Q'  THEN 'Confirmed Case, Transmit to Health Department'::varchar(80)
               WHEN disease.status = 'S'  THEN 'Transmitted to Health Department'::varchar(80)
               ELSE 'Not Mapped'::varchar(80)
             END item_text
        FROM esp_disease_u disease
          where not exists (select null from uvt_detected_status t0 where t0.item_code=disease.status);

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
update esp_demographic t0
  set centerid=t1.centerid,
      birth_date=t1.birth_date,
      sex=t1.sex,
      hispanic=t1.hispanic,
      race=t1.race,
      zip5=t1.zip5
  from (select *
        from esp_demographic_u) t1
  where t1.patid=t0.patid;
insert into esp_demographic select * from esp_demographic_u
   t0 where not exists (select null from esp_demographic t1 where t1.patid=t0.patid);
insert into esp_encounter select * from esp_encounter_u;
insert into esp_diagnosis select * from esp_diagnosis_u;
insert into esp_disease select * from esp_disease_u;

--now get the smoking data
drop table if exists esp_temp_smoking;
create table esp_temp_smoking as
   select case when t1.latest='Yes' then 'Current'
               when t2.yesOrQuit='Quit' then 'Former'
               when t3.passive='Passive' then 'Passive'
               when t4.never='Never' then 'Never'
               else 'Not available' 
           end as smoking, 
           t0.natural_key as patid
   from
     emr_patient t0
   left outer join 
     (select t00.tobacco_use ls atest, t00.patient_id 
      from emr_socialhistory t00
      inner join
      (select max(date) as maxdate, patient_id 
       from emr_socialhistory 
       where tobacco_use is not null and tobacco_use<>''
       group by patient_id) t01 on t00.patient_id=t01.patient_id and t00.date=t01.maxdate) t1 on t0.id=t1.patient_id
   left outer join
     (select max(val) as yesOrQuit, patient_id
      from (select 'Quit'::text as val, patient_id
            from emr_socialhistory where tobacco_use in ('Yes','Quit')) t00
            group by patient_id) t2 on t0.id=t2.patient_id
   left outer join
     (select max(val) as passive, patient_id
      from (select 'Passive'::text as val, patient_id
            from emr_socialhistory where tobacco_use ='Passive') t00
            group by patient_id) t3 on t0.id=t3.patient_id
   left outer join
     (select max(val) as never, patient_id
      from (select 'never'::text as val, patient_id
            from emr_socialhistory where tobacco_use ='Never') t00
            group by patient_id) t4 on t0.id=t4.patient_id;
alter table esp_temp_smoking add primary key (patid);
update esp_demographic
set smoking = (select smoking from esp_temp_smoking t0 where t0.patid=esp_demographic.patid);

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
