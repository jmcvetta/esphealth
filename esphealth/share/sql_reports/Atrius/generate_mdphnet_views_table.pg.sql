drop table if exists esp_temp_smoking cascade;
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
     (select t00.tobacco_use as latest, t00.patient_id 
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
      from (select 'Never'::text as val, patient_id
            from emr_socialhistory where tobacco_use ='Never') t00
            group by patient_id) t4 on t0.id=t4.patient_id;
alter table esp_temp_smoking add primary key (patid);
drop view if exists esp_demographic_v;
CREATE OR REPLACE VIEW esp_demographic_v AS
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       (pat.date_of_birth::date - ('1960-01-01'::date))::integer birth_date,
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
       case 
         when upper(race)='HISPANIC' then 6 
         when UPPER(race) = 'CAUCASIAN' then 5
         when UPPER(race) in ('ASIAN','INDIAN','NATIVE HAWAI') then 2
         when UPPER(race) = 'BLACK'then 3
         when UPPER(race) in ('NAT AMERICAN','ALASKAN') then 1
         else 0
       end as race_ethnicity,
       pat.zip5,
       smk.smoking
  FROM public.emr_patient pat,
       public.emr_provenance prvn,
       esp_temp_smoking smk
  WHERE pat.provenance_id=prvn.provenance_id and prvn.source ilike 'epicmem%'
        and pat.natural_key=smk.patid 
        and exists (select null from emr_encounter t0 where t0.patient_id=pat.id); --patient must have at least one encounter record;

-- Instantiate table from previously created view
drop table if exists esp_demographic cascade;
create table esp_demographic as select * from esp_demographic_v;
create unique index esp_demographic_patid_unique_idx on esp_demographic (patid);
create index esp_demographic_centerid_idx on esp_demographic (centerid);
create index esp_demographic_birth_date_idx on esp_demographic (birth_date);
create index esp_demographic_sex_idx on esp_demographic (sex);
create index esp_demographic_hispanic_idx on esp_demographic (hispanic);
create index esp_demographic_race_idx on esp_demographic (race);
create index esp_demog_race_eth_idx on esp_demographic (race_ethnicity);
create index esp_demographic_zip5_idx on esp_demographic (zip5);
alter table esp_demographic add primary key (patid);

drop view if exists esp_encounter_v;
CREATE OR REPLACE VIEW esp_encounter_v AS
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
       age_at_year_start(enc.date, pat.date_of_birth::date) age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth::date)::varchar(5) age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN (select t0.* from public.emr_patient t0 join esp_demographic t1 on t1.patid=t0.natural_key) pat ON enc.patient_id = pat.id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id;

drop view if exists esp_diagnosis_v;
CREATE OR REPLACE VIEW esp_diagnosis_v AS
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       enc.natural_key encounterid,
       enc.date - ('1960-01-01'::date) a_date,
       prov.natural_key provider,
       'AV'::varchar(10) enc_type, --this is initial value for Mass League data
       diag.dx_code_id dx,
       icd9_prefix(diag.dx_code_id, 3)::varchar(4) dx_code_3dig,
       icd9_prefix(diag.dx_code_id, 4)::varchar(5) dx_code_4dig,
       case 
         when length(icd9_prefix(diag.dx_code_id, 4))=5
	   then substr(diag.dx_code_id,1,6)
         else substr(diag.dx_code_id,1,5)
       end as dx_code_4dig_with_dec,
       icd9_prefix(diag.dx_code_id, 5)::varchar(6) dx_code_5dig,
       case 
         when length(icd9_prefix(diag.dx_code_id, 4))=6
	   then substr(diag.dx_code_id,1,7)
         else substr(diag.dx_code_id,1,6)
       end as dx_code_5dig_with_dec,
       enc.site_name facility_location,
       enc.site_natural_key facility_code,
       date_part('year', enc.date)::integer enc_year,
       age_at_year_start(enc.date, pat.date_of_birth::date) age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth::date)::varchar(5) age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN (select t0.* from public.emr_patient t0 join esp_demographic t1 on t1.patid=t0.natural_key) pat ON enc.patient_id = pat.id
         INNER JOIN (select * from public.emr_encounter_dx_codes 
                     where strpos(trim(dx_code_id),'.')<>3
                       and length(trim(dx_code_id))>=3 ) diag ON enc.id = diag.encounter_id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id;

drop view if exists esp_disease_v;
CREATE OR REPLACE VIEW esp_disease_v AS
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       disease.condition,
       disease.date - ('1960-01-01'::date) date,
       age_at_year_start(disease.date, pat.date_of_birth::date) age_at_detect_year,
       age_group_5yr(disease.date, pat.date_of_birth::date)::varchar(5) age_group_5yr,
       age_group_10yr(disease.date, pat.date_of_birth::date)::varchar(5) age_group_10yr,
       age_group_ms(disease.date, pat.date_of_birth::date)::varchar(5) age_group_ms,
       disease.criteria,
       disease.status,
       disease.notes
  FROM public.nodis_case disease
         INNER JOIN (select t0.* from public.emr_patient t0 join esp_demographic t1 on t1.patid=t0.natural_key) pat ON disease.patient_id = pat.id;

-- Instantiate table from previously created view
drop table if exists esp_encounter cascade;
create table esp_encounter as select * from esp_encounter_v;
create index esp_encounter_centerid_idx on esp_encounter (centerid);
create index esp_encounter_patid_idx on esp_encounter (patid);
create unique index esp_encounter_encounterid_idx on esp_encounter (encounterid);
create index esp_encounter_a_date_idx on esp_encounter (a_date);
create index esp_encounter_d_date_idx on esp_encounter (d_date);
create index esp_encounter_provider_idx on esp_encounter (provider);
create index esp_encounter_facility_location_idx on esp_encounter (facility_location);
create index esp_encounter_facility_code_idx on esp_encounter (facility_code);
create index esp_encounter_enc_year_idx on esp_encounter (enc_year);
create index esp_encounter_age_at_enc_year_idx on esp_encounter (age_at_enc_year);
create index esp_encounter_age_group_5yr_idx on esp_encounter (age_group_5yr);
create index esp_encounter_age_group_10yr_idx on esp_encounter (age_group_10yr);
create index esp_encounter_age_group_ms_idx on esp_encounter (age_group_ms);
alter table esp_encounter add primary key (encounterid);
alter table esp_encounter add foreign key (patid) references esp_demographic (patid);

drop table if exists esp_diagnosis cascade;
create table esp_diagnosis as select * from esp_diagnosis_v;
create index esp_diagnosis_dx_idx on esp_diagnosis (dx);
CREATE INDEX esp_diagnosis_dx_like_idx ON esp_diagnosis USING btree (dx varchar_pattern_ops);
create index esp_diagnosis_centerid_idx on esp_diagnosis (centerid);
create index esp_diagnosis_patid_idx on esp_diagnosis (patid);
create index esp_diagnosis_encounterid_idx on esp_diagnosis (encounterid);
create index esp_diagnosis_provider_idx on esp_diagnosis (provider);
create index esp_diagnosis_enc_type_idx on esp_diagnosis (enc_type);
create index esp_diagnosis_dx_code_3dig_idx on esp_diagnosis (dx_code_3dig);
create index esp_diagnosis_dx_code_4dig_idx on esp_diagnosis (dx_code_4dig);
create index esp_diagnosis_dx_code_5dig_idx on esp_diagnosis (dx_code_5dig);
create index esp_diagnosis_dx_code_4dig_with_dec_idx on esp_diagnosis (dx_code_4dig_with_dec);
create index esp_diagnosis_dx_code_5dig_with_dec_idx on esp_diagnosis (dx_code_5dig_with_dec);
create index esp_diagnosis_dx_code_5dig_like_idx on esp_diagnosis using btree (dx_code_5dig varchar_pattern_ops);
create index esp_diagnosis_facility_loc_idx on esp_diagnosis (facility_location);
create index esp_diagnosis_facility_code_idx on esp_diagnosis (facility_code);
create index esp_diagnosis_enc_year_idx on esp_diagnosis (enc_year);
create index esp_diagnosis_age_at_enc_year_idx on esp_diagnosis (age_at_enc_year);
create index esp_diagnosis_age_group_5yr_idx on esp_diagnosis (age_group_5yr);
create index esp_diagnosis_age_group_10yr_idx on esp_diagnosis (age_group_10yr);
create index esp_diagnosis_age_group_ms_idx on esp_diagnosis (age_group_ms);
alter table esp_diagnosis add primary key (patid, encounterid, dx);
alter table esp_diagnosis add foreign key (patid) references esp_demographic (patid);
alter table esp_diagnosis add foreign key (encounterid) references esp_encounter (encounterid);

drop table if exists esp_disease cascade;
create table esp_disease as select * from esp_disease_v;
create index esp_disease_age_group_10yr_idx on esp_disease (age_group_10yr);
create index esp_disease_age_group_5yr_idx on esp_disease (age_group_5yr);
create index esp_disease_age_group_ms_idx on esp_disease (age_group_ms);
create index esp_disease_centerid_idx on esp_disease (centerid);
create index esp_disease_patid_idx on esp_disease (patid);
create index esp_disease_condition_idx on esp_disease (condition);
create index esp_disease_date_idx on esp_disease (date);
create index esp_disease_age_at_detect_year_idx on esp_disease (age_at_detect_year);
create index esp_disease_criteria_idx on esp_disease (criteria);
create index esp_disease_status_idx on esp_disease (status);
alter table esp_disease add primary key (patid, condition, date);
alter table esp_disease add foreign key (patid) references esp_demographic (patid);

drop view if exists esp_disease_v;
drop view if exists esp_diagnosis_v;
drop view if exists esp_encounter_v;
drop view if exists esp_demographic_v;

--now vacuum analyze each table
vacuum analyze esp_demographic;
vacuum analyze esp_encounter;
vacuum analyse esp_diagnosis;
vacuum analyse esp_disease;

/*
-- Create the summary table for 3-digit ICD9 codes and populate it with information for the 5 year age groups
DROP TABLE if exists esp_diagnosis_icd9_3dig cascade;
CREATE TABLE esp_diagnosis_icd9_3dig AS
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 5yr'::varchar(15) age_group_type, diag.age_group_5yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_3dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_5yr, pat.sex, diag.enc_year, diag.dx_code_3dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
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
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
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
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
                       and length(trim(code))>=3) icd9
                 ON t1.code_ = replace(icd9.code, '.', '');
create index diag3dig_centerid_idx on esp_diagnosis_icd9_3dig (centerid);
create index diag3dig_age_group_type_idx on esp_diagnosis_icd9_3dig (age_group_type);
create index diag3dig_age_group_idx on esp_diagnosis_icd9_3dig (age_group);
create index diag3dig_sex_idx on esp_diagnosis_icd9_3dig (sex);
create index diag3dig_period_idx on esp_diagnosis_icd9_3dig (period);
create index diag3dig_code_idx on esp_diagnosis_icd9_3dig (code_);
create index diag3dig_setting_idx on esp_diagnosis_icd9_3dig (setting);


-- Create the summary table for 4-digit ICD9 codes and populate it with information for the 5 year age groups
DROP TABLE if exists esp_diagnosis_icd9_4dig cascade;
CREATE TABLE esp_diagnosis_icd9_4dig AS
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 5yr'::varchar(15) age_group_type, diag.age_group_5yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_4dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_5yr, pat.sex, diag.enc_year, diag.dx_code_4dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
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
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
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
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
                       and length(trim(code))>=3) icd9
                 ON t1.code_ = replace(icd9.code, '.', '');
create index diag4dig_centerid_idx on esp_diagnosis_icd9_4dig (centerid);
create index diag4dig_age_group_type_idx on esp_diagnosis_icd9_4dig (age_group_type);
create index diag4dig_age_group_idx on esp_diagnosis_icd9_4dig (age_group);
create index diag4dig_sex_idx on esp_diagnosis_icd9_4dig (sex);
create index diag4dig_period_idx on esp_diagnosis_icd9_4dig (period);
create index diag4dig_code_idx on esp_diagnosis_icd9_4dig (code_);
create index diag4dig_setting_idx on esp_diagnosis_icd9_4dig (setting);


-- Create the summary table for 5-digit ICD9 codes and populate it with information for the 5 year age groups
DROP TABLE if exists esp_diagnosis_icd9_5dig cascade;
CREATE TABLE esp_diagnosis_icd9_5dig AS
SELECT t1.*, icd9.name dx_name
  FROM (SELECT diag.centerid, 'Age Group 5yr'::varchar(15) age_group_type, diag.age_group_5yr age_group,
               pat.sex, diag.enc_year period, diag.dx_code_5dig code_, diag.enc_type setting,
               count(distinct diag.patid) members,
               count(distinct diag.encounterid) events
          FROM esp_diagnosis diag
                 INNER JOIN esp_demographic pat ON diag.patid = pat.patid
        GROUP BY diag.centerid, diag.age_group_5yr, pat.sex, diag.enc_year, diag.dx_code_5dig,
                 diag.enc_type) t1
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
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
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
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
         LEFT JOIN (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '');
create index diag5dig_centerid_idx on esp_diagnosis_icd9_5dig (centerid);
create index diag5dig_age_group_type_idx on esp_diagnosis_icd9_5dig (age_group_type);
create index diag5dig_age_group_idx on esp_diagnosis_icd9_5dig (age_group);
create index diag5dig_sex_idx on esp_diagnosis_icd9_5dig (sex);
create index diag5dig_period_idx on esp_diagnosis_icd9_5dig (period);
create index diag5dig_code_idx on esp_diagnosis_icd9_5dig (code_);
create index diag5dig_setting_idx on esp_diagnosis_icd9_5dig (setting);
*/

-- UVT_TABLES
--    UVT_SEX
      DROP TABLE if exists UVT_SEX;
      CREATE TABLE UVT_SEX AS
      SELECT DISTINCT
             pat.sex item_code,
             CASE
               WHEN pat.sex = 'M' THEN 'Male'::varchar(10)
               WHEN pat.sex = 'F' THEN 'Female'::varchar(10)
               WHEN pat.sex = 'U' THEN 'Unknown'::varchar(10)
               ELSE 'Not Mapped'::varchar(10)
             END item_text
        FROM esp_demographic pat;
        ALTER TABLE UVT_SEX ADD PRIMARY KEY (item_code);

--    UVT_RACE
      DROP TABLE if exists UVT_RACE;
      CREATE TABLE UVT_RACE AS
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
        FROM esp_demographic pat;
        ALTER TABLE UVT_RACE ADD PRIMARY KEY (item_code);

--    UVT_RACE_ETHNICITY
      drop table if exists UVT_RACE_ETHNICITY;
      create table uvt_race_ethnicity as
      select distinct 
             pat.race_ethnicity item_code,
             case
               when pat.race_ethnicity=5 then 'White'::varchar(50)
               when pat.race_ethnicity=3 then 'Black'::varchar(50)
               when pat.race_ethnicity=2 then 'Asian'::varchar(50)
               when pat.race_ethnicity=6 then 'Hispanic'::varchar(50)
               when pat.race_ethnicity=1 then 'Native American'::varchar(50)
               when pat.race_ethnicity=0 then 'Unknown'::varchar(50)
             end item_text
     from esp_mdphnet.esp_demographic pat;
     alter table esp_mdphnet.uvt_race_ethnicity add primary key (item_code);
        
--    UVT_ZIP5
      DROP TABLE if exists uvt_zip5;
      create table uvt_zip5 as 
      select distinct 
             zip5 as item_code, 
	         null::varchar(10) item_text
      from esp_demographic where zip5 is not null;
      alter table uvt_zip5 add primary key (item_code);

--    UVT_SMOKING
      DROP TABLE if exists uvt_smoking;
      create table uvt_smoking as 
      select distinct 
             smoking as item_code, 
	         null::varchar(10) item_text
      from esp_demographic where smoking is not null;
      alter table uvt_smoking add primary key (item_code);

--    UVT_PROVIDER
      DROP TABLE if exists UVT_PROVIDER;
      CREATE TABLE UVT_PROVIDER AS
      SELECT DISTINCT
             enc.provider item_code,
             ''::varchar(10) item_text
        FROM esp_encounter enc;
        ALTER TABLE UVT_PROVIDER ADD PRIMARY KEY (item_code);

--    UVT_SITE
      DROP TABLE if exists UVT_SITE;
      CREATE TABLE UVT_SITE AS
      SELECT DISTINCT
             enc.facility_code item_code,
             enc.facility_location item_text
        FROM esp_encounter enc 
      WHERE enc.facility_code is not null;
        ALTER TABLE UVT_SITE ADD PRIMARY KEY (item_code);

--    UVT_CENTER
      DROP TABLE if exists UVT_CENTER;
      CREATE TABLE UVT_CENTER AS
      SELECT DISTINCT
             pat.centerid item_code,
             pat.centerid item_text
        FROM esp_demographic pat;
        ALTER TABLE UVT_CENTER ADD PRIMARY KEY (item_code);

--    UVT_PERIOD
      DROP TABLE if exists UVT_PERIOD;
      CREATE TABLE UVT_PERIOD AS
      SELECT DISTINCT
             enc.enc_year item_code,
             enc.enc_year::varchar(4) item_text
        FROM esp_encounter enc;
        ALTER TABLE UVT_PERIOD ADD PRIMARY KEY (item_code);

--    UVT_ENCOUNTER
      DROP TABLE if exists UVT_ENCOUNTER;
      CREATE TABLE UVT_ENCOUNTER AS
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
        FROM esp_encounter enc;
        ALTER TABLE UVT_ENCOUNTER ADD PRIMARY KEY (item_code);

--    UVT_AGEGROUP_5YR
      DROP TABLE if exists UVT_AGEGROUP_5YR;
      CREATE TABLE UVT_AGEGROUP_5YR AS
      SELECT DISTINCT
             enc.age_group_5yr item_code,
             enc.age_group_5yr::varchar(5) item_text
        FROM esp_encounter enc
      WHERE enc.age_group_5yr is not null;
        ALTER TABLE UVT_AGEGROUP_5YR ADD PRIMARY KEY (item_code);

--    UVT_AGEGROUP_10YR
      DROP TABLE if exists UVT_AGEGROUP_10YR;
      CREATE TABLE UVT_AGEGROUP_10YR AS
      SELECT DISTINCT
             enc.age_group_10yr item_code,
             enc.age_group_10yr::varchar(5) item_text
        FROM esp_encounter enc
      WHERE enc.age_group_10yr is not null;
        ALTER TABLE UVT_AGEGROUP_10YR ADD PRIMARY KEY (item_code);

--    UVT_AGEGROUP_MS
      DROP TABLE if exists UVT_AGEGROUP_MS;
      CREATE TABLE UVT_AGEGROUP_MS AS
      SELECT DISTINCT
             enc.age_group_ms item_code,
             enc.age_group_ms::varchar(5) item_text
        FROM esp_encounter enc
      WHERE enc.age_group_ms is not null;
        ALTER TABLE UVT_AGEGROUP_MS ADD PRIMARY KEY (item_code);

--    UVT_DX
      DROP TABLE if exists UVT_DX;
      CREATE TABLE UVT_DX AS
      SELECT DISTINCT
             diag.dx item_code,
             icd9.name item_text
        FROM esp_diagnosis diag
               INNER JOIN public.static_dx_code icd9 ON diag.dx = icd9.code;
        ALTER TABLE UVT_DX ADD PRIMARY KEY (item_code);

--    UVT_DX_3DIG
      DROP TABLE if exists UVT_DX_3DIG;
      CREATE TABLE UVT_DX_3DIG AS
      SELECT DISTINCT
             diag.dx_code_3dig item_code,
             icd9.name item_text
        FROM esp_diagnosis diag
               LEFT OUTER JOIN  (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9 
               ON diag.dx_code_3dig = REPLACE(icd9.code, '.', '')
        WHERE diag.dx_code_3dig is not null;
        ALTER TABLE UVT_DX_3DIG ADD PRIMARY KEY (item_code);

--    UVT_DX_4DIG
      DROP TABLE if exists UVT_DX_4DIG;
      CREATE TABLE UVT_DX_4DIG AS
      SELECT DISTINCT
             diag.dx_code_4dig item_code,
             diag.dx_code_4dig_with_dec item_code_with_dec,
             icd9.name item_text
        FROM esp_diagnosis diag
               LEFT OUTER JOIN  public.static_dx_code icd9
               ON diag.dx_code_4dig_with_dec = icd9.code
        WHERE diag.dx_code_4dig is not null;
        ALTER TABLE UVT_DX_4DIG ADD PRIMARY KEY (item_code_with_dec);
        create index uvt_dx_code_4dig_idx on uvt_dx_4dig (item_code);

--    UVT_DX_5DIG
      DROP TABLE if exists UVT_DX_5DIG;
      CREATE TABLE UVT_DX_5DIG AS
      SELECT DISTINCT
             diag.dx_code_5dig item_code,
             diag.dx_code_5dig_with_dec item_code_with_dec,
             icd9.name item_text
        FROM esp_diagnosis diag
               LEFT OUTER JOIN  public.static_dx_code icd9
               ON diag.dx_code_5dig_with_dec = icd9.code
        WHERE diag.dx_code_5dig is not null;
        ALTER TABLE UVT_DX_5DIG ADD PRIMARY KEY (item_code_with_dec);
        create index uvt_dx_code_5dig_idx on uvt_dx_5dig (item_code);

--    UVT_DETECTED_CONDITION
      DROP TABLE if exists UVT_DETECTED_CONDITION;
      CREATE TABLE UVT_DETECTED_CONDITION AS
      SELECT DISTINCT
             disease.condition item_code,
             disease.condition item_text
        FROM esp_disease disease;
        ALTER TABLE UVT_DETECTED_CONDITION ADD PRIMARY KEY (item_code);

--    UVT_DETECTED_CRITERIA
      DROP TABLE if exists UVT_DETECTED_CRITERIA;
      CREATE TABLE UVT_DETECTED_CRITERIA AS
      SELECT DISTINCT
             disease.criteria item_code,
             disease.criteria item_text
        FROM esp_disease disease
      WHERE criteria is not null;
        ALTER TABLE UVT_DETECTED_CRITERIA ADD PRIMARY KEY (item_code);
      
--    UVT_DETECTED_STATUS
      DROP TABLE if exists UVT_DETECTED_STATUS;
      CREATE TABLE UVT_DETECTED_STATUS AS
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
        FROM esp_disease disease;
        ALTER TABLE UVT_DETECTED_STATUS ADD PRIMARY KEY (item_code);

--    REMOTE KEYS USING UVTs
      ALTER TABLE esp_demographic ADD FOREIGN KEY (sex) REFERENCES uvt_sex (item_code);
      ALTER TABLE esp_demographic ADD FOREIGN KEY (race) REFERENCES uvt_race (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (provider) REFERENCES uvt_provider (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (facility_code) REFERENCES uvt_site (item_code);
      ALTER TABLE esp_demographic ADD FOREIGN KEY (centerid) REFERENCES uvt_center (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (enc_year) REFERENCES uvt_period (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (enc_type) REFERENCES uvt_encounter (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (age_group_5yr) 
                  REFERENCES uvt_agegroup_5yr (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (age_group_10yr) 
                  REFERENCES uvt_agegroup_10yr (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (age_group_ms) 
                  REFERENCES uvt_agegroup_ms (item_code);
      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx) REFERENCES uvt_dx (item_code);

      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx_code_3dig)
                  REFERENCES uvt_dx_3dig (item_code);
      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx_code_4dig_with_dec)
                  REFERENCES uvt_dx_4dig (item_code_with_dec);
      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx_code_5dig_with_dec)
                  REFERENCES uvt_dx_5dig (item_code_with_dec);

      ALTER TABLE esp_disease ADD FOREIGN KEY (condition) 
                  REFERENCES uvt_detected_condition (item_code);
      ALTER TABLE esp_disease ADD FOREIGN KEY (criteria) 
                  REFERENCES uvt_detected_criteria (item_code);
      ALTER TABLE esp_disease ADD FOREIGN KEY (status) 
                  REFERENCES uvt_detected_status (item_code);
