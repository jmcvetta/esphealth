drop table if exists mdphnet_schema_update_history;
CREATE TABLE mdphnet_schema_update_history
(
  latest_update timestamp without time zone NOT NULL,
  patients_replaced integer,
  CONSTRAINT update_timestamp_pk PRIMARY KEY (latest_update)
);
insert into mdphnet_schema_update_history
select current_timestamp, 0;
drop view if exists esp_demographic_v;
drop table if exists esp_temp_smoking;
create table esp_temp_smoking as
   select distinct case when upper(t1.latest)='YES' then 'Current'
               when upper(t2.yesOrQuit)='QUIT' then 'Former'
               when upper(t3.passive)='PASSIVE' then 'Passive'
               when upper(t4.never)='NEVER' then 'Never'
               else 'Not available' 
           end as smoking, 
           t0.natural_key as patid
   from
     emr_patient t0
   left outer join 
     (select patient_id, case when bool_or(upper(latest)='YES') then 'YES' else 'NO' end as latest from
      (select t00.tobacco_use as latest, t00.patient_id 
      from emr_socialhistory t00
      inner join
      (select max(date) as maxdate, patient_id 
       from emr_socialhistory 
       where tobacco_use is not null and tobacco_use<>''
       group by patient_id) t01 on t00.patient_id=t01.patient_id and t00.date=t01.maxdate) t11 group by patient_id) t1 on t0.id=t1.patient_id
   left outer join
     (select max(val) as yesOrQuit, patient_id
      from (select 'QUIT'::text as val, patient_id
            from emr_socialhistory where upper(tobacco_use) in ('YES','QUIT')) t00
            group by patient_id) t2 on t0.id=t2.patient_id
   left outer join
     (select max(val) as passive, patient_id
      from (select 'PASSIVE'::text as val, patient_id
            from emr_socialhistory where upper(tobacco_use) ='PASSIVE') t00
            group by patient_id) t3 on t0.id=t3.patient_id
   left outer join
     (select max(val) as never, patient_id
      from (select 'NEVER'::text as val, patient_id
            from emr_socialhistory where upper(tobacco_use) ='NEVER') t00
            group by patient_id) t4 on t0.id=t4.patient_id;
alter table esp_temp_smoking add primary key (patid);

DROP TABLE if exists esp_current_asthma_cases cascade;
CREATE TABLE esp_current_asthma_cases AS
	select id, patient_id from
	(select max(public.hef_event.date) as MAXEVTDT, public.nodis_case.patient_id, public.nodis_case.id from hef_event, public.nodis_case where 
	condition = 'asthma'
	and
	public.hef_event.patient_id = public.nodis_case.patient_id
	and public.hef_event.name in ('dx:asthma', 'rx:albuterol', 'rx:alvesco', 'rx:pulmicort', 'rx:flovent', 'rx:asmanex', 'rx:aerobid', 'rx:montelukast','rx:intal','rx:zafirlukast', 'rx:zileuton', 'rx:ipratropium','rx:tiotropium','rx:omalizumab', 'rx:fluticasone-inh', 'rx:mometasone-inh','rx:budesonide-inh','rx:ciclesonide-inh','rx:flunisolide-inh','rx:cromolyn-inh','rx:pirbuterol','rx:levalbuterol','rx:arformoterol','rx:formeterol','rx:indacaterol','rx:salmeterol',
'rx:beclomethasone','rx:fluticasone-salmeterol:generic','rx:albuterol-ipratropium:generic','rx:mometasone-formeterol:generic',
'rx:budesonide-formeterol:generic', 'rx:fluticasone-salmeterol:trade','rx:albuterol-ipratropium:trade','rx:mometasone-formeterol:trade','rx:budesonide-formeterol:trade') group by public.nodis_case.patient_id, public.nodis_case.id) A 
	where
	current_date - MAXEVTDT <= (365.25*2);
CREATE INDEX esp_current_asthma_cases_caseid_idx on esp_current_asthma_cases (id);
VACUUM ANALYZE esp_current_asthma_cases;
ALTER TABLE esp_current_asthma_cases add primary key (patient_id);


CREATE OR REPLACE VIEW esp_demographic_v AS
SELECT '1'::varchar(1) as centerid,
       pat.natural_key as patid,
       pat.date_of_birth::date - ('1960-01-01'::date) as birth_date,
       CASE
         WHEN UPPER(gender) in ('M','MALE') THEN 'M'::char(1)
         WHEN UPPER(gender) in ('F','FEMALE') THEN 'F'::char(1)
         WHEN UPPER(gender) = 'U' THEN 'U'::char(1)
         ELSE 'U'::char(1)
       END as sex,
       CASE
         WHEN UPPER(race) = 'HISPANIC' THEN 'Y'::char(1)
         WHEN ETHNICITY = 'Y' then 'Y'::char(1)
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
       case 
         when upper(race)='HISPANIC' then 6 
         when ethnicity = 'Y' then 6
         when UPPER(race) in ('CAUCASIAN','WHITE') then 5
         when UPPER(race) in ('ASIAN','INDIAN','NATIVE HAWAI') then 2
         when UPPER(race) = 'BLACK'then 3
         when UPPER(race) in ('NAT AMERICAN','ALASKAN','AMERICAN INDIAN/ALASKAN NATIVE') then 1
         else 0
       end as race_ethnicity,
       pat.zip5,
       smk.smoking
  FROM public.emr_patient pat,
       public.emr_provenance prvn,
       esp_temp_smoking smk,
       (select distinct patient_id from emr_encounter) encpat
  WHERE pat.provenance_id=prvn.provenance_id and prvn.source ilike 'epicmem%' and pat.id=encpat.patient_id
        and pat.natural_key=smk.patid;

drop view if exists esp_encounter_v;
CREATE OR REPLACE VIEW esp_encounter_v AS
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
       esp_mdphnet.age_at_year_start(enc.date, pat.date_of_birth::date) as age_at_enc_year,
       esp_mdphnet.age_group_5yr(enc.date, pat.date_of_birth::date)::varchar(5) as age_group_5yr,
       esp_mdphnet.age_group_10yr(enc.date, pat.date_of_birth::date)::varchar(5) as age_group_10yr,
       esp_mdphnet.age_group_ms(enc.date, pat.date_of_birth::date)::varchar(5) as age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN public.emr_patient pat ON enc.patient_id = pat.id
         INNER JOIN public.emr_provenance prvn ON pat.provenance_id = prvn.provenance_id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id
  WHERE prvn.source ilike 'epicmem%';

drop view if exists esp_diagnosis_v;
CREATE OR REPLACE VIEW esp_diagnosis_v AS
SELECT '1'::varchar(1) as centerid,
       pat.natural_key as patid,
       enc.natural_key as encounterid,
       enc.date - ('1960-01-01'::date) as a_date,
       prov.natural_key as provider,
       'AV'::varchar(10) as enc_type, --this is initial value for Mass League data
       split_part(dx_code_id,':', 2) dx,
       split_part(dx_code_id, ':', 1) dx_type,
       enc.site_name as facility_location,
       enc.site_natural_key as facility_code,
       date_part('year', enc.date)::integer as enc_year,
       esp_mdphnet.age_at_year_start(enc.date, pat.date_of_birth::date) as age_at_enc_year,
       esp_mdphnet.age_group_5yr(enc.date, pat.date_of_birth::date)::varchar(5) as age_group_5yr,
       esp_mdphnet.age_group_10yr(enc.date, pat.date_of_birth::date)::varchar(5) as age_group_10yr,
       esp_mdphnet.age_group_ms(enc.date, pat.date_of_birth::date)::varchar(5) as age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN public.emr_patient pat ON enc.patient_id = pat.id
         INNER JOIN public.emr_provenance prvn ON pat.provenance_id = prvn.provenance_id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id
  WHERE prvn.source ilike 'epicmem%';

drop view if exists esp_disease_v;
CREATE OR REPLACE VIEW esp_disease_v AS
SELECT '1'::varchar(1) as centerid,
       pat.natural_key as patid,
       disease.condition,
       disease.date - ('1960-01-01'::date) as date,
       esp_mdphnet.age_at_year_start(disease.date, pat.date_of_birth::date) as age_at_detect_year,
       esp_mdphnet.age_group_5yr(disease.date, pat.date_of_birth::date)::varchar(5) as age_group_5yr,
       esp_mdphnet.age_group_10yr(disease.date, pat.date_of_birth::date)::varchar(5) as age_group_10yr,
       esp_mdphnet.age_group_ms(disease.date, pat.date_of_birth::date)::varchar(5) as age_group_ms,
       disease.criteria,
       disease.status,
       disease.notes
  FROM public.nodis_case disease
         INNER JOIN public.emr_patient pat ON disease.patient_id = pat.id
         INNER JOIN public.emr_provenance prvn ON pat.provenance_id = prvn.provenance_id
  WHERE prvn.source ilike 'epicmem%'
        and (disease.condition in ('depression', 'ili', 'diabetes:type-1', 'diabetes:type-2', 'diabetes:gestational', 'diabetes:prediabetes')
        or disease.id in (select id from esp_current_asthma_cases));

-- Instantiate tables from previously created views
drop table if exists esp_demographic_r cascade;
create table esp_demographic_r as select * from esp_demographic_v;
create unique index esp_demographic_patid_unique_idx_r on esp_demographic_r (patid);
create index esp_demographic_centerid_idx_r on esp_demographic_r (centerid);
create index esp_demographic_birth_date_idx_r on esp_demographic_r (birth_date);
create index esp_demographic_sex_idx_r on esp_demographic_r (sex);
create index esp_demographic_hispanic_idx_r on esp_demographic_r (hispanic);
create index esp_demographic_race_idx_r on esp_demographic_r (race);
create index esp_demographic_race_eth_idx_r on esp_demographic_r (race_ethnicity);
create index esp_demographic_zip5_idx_r on esp_demographic_r (zip5);
create index esp_demographic_smk_idx_r on esp_demographic_r (smoking);
alter table esp_demographic_r add primary key (patid);

drop table if exists esp_encounter_r cascade;
create table esp_encounter_r as select t0.* from esp_encounter_v 
            as t0 inner join esp_demographic_r as t1 
            on t0.patid=t1.patid;
create index esp_encounter_centerid_idx_r on esp_encounter_r (centerid);
create index esp_encounter_patid_idx_r on esp_encounter_r (patid);
create unique index esp_encounter_encounterid_idx_r on esp_encounter_r (encounterid);
create index esp_encounter_a_date_idx_r on esp_encounter_r (a_date);
create index esp_encounter_d_date_idx_r on esp_encounter_r (d_date);
create index esp_encounter_provider_idx_r on esp_encounter_r (provider);
create index esp_encounter_facility_location_idx_r on esp_encounter_r (facility_location);
create index esp_encounter_facility_code_idx_r on esp_encounter_r (facility_code);
create index esp_encounter_enc_year_idx_r on esp_encounter_r (enc_year);
create index esp_encounter_age_at_enc_year_idx_r on esp_encounter_r (age_at_enc_year);
create index esp_encounter_age_group_5yr_idx_r on esp_encounter_r (age_group_5yr);
create index esp_encounter_age_group_10yr_idx_r on esp_encounter_r (age_group_10yr);
create index esp_encounter_age_group_ms_idx_r on esp_encounter_r (age_group_ms);
alter table esp_encounter_r add primary key (encounterid);
alter table esp_encounter_r add foreign key (patid) references esp_demographic_r (patid);

drop table if exists esp_diagnosis_r cascade;
create table esp_diagnosis_r as select t0.* from esp_diagnosis_v
            as t0 inner join esp_demographic_r as t1
            on t0.patid=t1.patid;
create index esp_diagnosis_dx_idx_r on esp_diagnosis_r (dx);
CREATE INDEX esp_diagnosis_dx_like_idx_r ON esp_diagnosis_r USING btree (dx varchar_pattern_ops);
create index esp_diagnosis_centerid_idx_r on esp_diagnosis_r (centerid);
create index esp_diagnosis_patid_idx_r on esp_diagnosis_r (patid);
create index esp_diagnosis_encounterid_idx_r on esp_diagnosis_r (encounterid);
create index esp_diagnosis_provider_idx_r on esp_diagnosis_r (provider);
create index esp_diagnosis_enc_type_idx_r on esp_diagnosis_r (enc_type);
create index esp_diagnosis_facility_loc_idx_r on esp_diagnosis_r (facility_location);
create index esp_diagnosis_facility_code_idx_r on esp_diagnosis_r (facility_code);
create index esp_diagnosis_enc_year_idx_r on esp_diagnosis_r (enc_year);
create index esp_diagnosis_age_at_enc_year_idx_r on esp_diagnosis_r (age_at_enc_year);
create index esp_diagnosis_age_group_5yr_idx_r on esp_diagnosis_r (age_group_5yr);
create index esp_diagnosis_age_group_10yr_idx_r on esp_diagnosis_r (age_group_10yr);
create index esp_diagnosis_age_group_ms_idx_r on esp_diagnosis_r (age_group_ms);
alter table esp_diagnosis_r add primary key (patid, encounterid, dx);
alter table esp_diagnosis_r add foreign key (patid) references esp_demographic_r (patid);
alter table esp_diagnosis_r add foreign key (encounterid) references esp_encounter_r (encounterid);

drop table if exists esp_disease_r cascade;
create table esp_disease_r as select t0.* from esp_disease_v
            as t0 inner join esp_demographic_r as t1
            on t0.patid=t1.patid;
--POPULATE THE ESP DISEASE VIEW WITH OPIOID/BENZO CONDITIONS FOR THE LAST 365 DAYS (FROM ESP_CONDITION TABLE)
INSERT INTO esp_disease_r (select t0.* from esp_condition
            as t0 inner join esp_demographic_r as t1
            on t0.patid=t1.patid
            where (current_date-('1960-01-01'::date) - t0.date <= 365));
create index esp_disease_age_group_10yr_idx_r on esp_disease_r (age_group_10yr);
create index esp_disease_age_group_5yr_idx_r on esp_disease_r (age_group_5yr);
create index esp_disease_age_group_ms_idx_r on esp_disease_r (age_group_ms);
create index esp_disease_centerid_idx_r on esp_disease_r (centerid);
create index esp_disease_patid_idx_r on esp_disease_r (patid);
create index esp_disease_condition_idx_r on esp_disease_r (condition);
create index esp_disease_date_idx_r on esp_disease_r (date);
create index esp_disease_age_at_detect_year_idx_r on esp_disease_r (age_at_detect_year);
create index esp_disease_criteria_idx_r on esp_disease_r (criteria);
create index esp_disease_status_idx_r on esp_disease_r (status);
alter table esp_disease_r add primary key (patid, condition, date);
alter table esp_disease_r add foreign key (patid) references esp_demographic_r (patid);

drop view if exists esp_disease_v;
drop view if exists esp_diagnosis_v;
drop view if exists esp_encounter_v;
drop view if exists esp_demographic_v;

-- UVT_TABLES
--    UVT_SEX
      DROP TABLE if exists UVT_SEX_r;
      CREATE TABLE UVT_SEX_r AS
      SELECT DISTINCT
             pat.sex as item_code,
             CASE
               WHEN pat.sex = 'M' THEN 'Male'::varchar(10)
               WHEN pat.sex = 'F' THEN 'Female'::varchar(10)
               WHEN pat.sex = 'U' THEN 'Unknown'::varchar(10)
               ELSE 'Not Mapped'::varchar(10)
             END as item_text
        FROM esp_demographic_r pat;
        ALTER TABLE UVT_SEX_r ADD PRIMARY KEY (item_code);

--    UVT_RACE
      DROP TABLE if exists UVT_RACE_r;
      CREATE TABLE UVT_RACE_r AS
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
        FROM esp_demographic_r pat;
        ALTER TABLE UVT_RACE_r ADD PRIMARY KEY (item_code);
        

--   UVT_RACE_ETHNICITY
     drop table if exists uvt_race_ethnicity_r;
     create table uvt_race_ethnicity_r as
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
     from esp_demographic_r pat;
     alter table uvt_race_ethnicity_r add primary key (item_code);


--    UVT_ZIP5
      DROP TABLE if exists uvt_zip5_r;
      create table uvt_zip5_r as 
      select distinct 
             zip5 as item_code, 
	         null::varchar(10) as item_text
      from esp_demographic_r where zip5 is not null;
      alter table uvt_zip5_r add primary key (item_code);

--    UVT_PROVIDER
      DROP TABLE if exists UVT_PROVIDER_r;
      CREATE TABLE UVT_PROVIDER_r AS
      SELECT DISTINCT
             enc.provider as item_code,
             ''::varchar(10) as item_text
        FROM esp_encounter_r enc;
        ALTER TABLE UVT_PROVIDER_r ADD PRIMARY KEY (item_code);

--    UVT_SITE
      DROP TABLE if exists UVT_SITE_r;
      CREATE TABLE UVT_SITE_r AS
      SELECT DISTINCT
             enc.facility_code as item_code,
             enc.facility_location as item_text
        FROM esp_encounter_r enc 
      WHERE enc.facility_code is not null and enc.facility_location is not null;
        ALTER TABLE UVT_SITE_r ADD PRIMARY KEY (item_code, item_text);

--    UVT_CENTER
      DROP TABLE if exists UVT_CENTER_r;
      CREATE TABLE UVT_CENTER_r AS
      SELECT DISTINCT
             pat.centerid as item_code,
             pat.centerid as item_text
        FROM esp_demographic pat;
        ALTER TABLE UVT_CENTER_r ADD PRIMARY KEY (item_code);

--    UVT_PERIOD
      DROP TABLE if exists UVT_PERIOD_r;
      CREATE TABLE UVT_PERIOD_r AS
      SELECT DISTINCT
             enc.enc_year as item_code,
             enc.enc_year::varchar(4) as item_text
        FROM esp_encounter_r enc;
        ALTER TABLE UVT_PERIOD_r ADD PRIMARY KEY (item_code);

--    UVT_ENCOUNTER
      DROP TABLE if exists UVT_ENCOUNTER_r;
      CREATE TABLE UVT_ENCOUNTER_r AS
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
        FROM esp_encounter_r enc;
        ALTER TABLE UVT_ENCOUNTER_r ADD PRIMARY KEY (item_code);

--    UVT_AGEGROUP_5YR
      DROP TABLE if exists UVT_AGEGROUP_5YR_r;
      CREATE TABLE UVT_AGEGROUP_5YR_r AS
      SELECT DISTINCT
             enc.age_group_5yr as item_code,
             enc.age_group_5yr::varchar(5) as item_text
        FROM esp_encounter_r enc
      WHERE enc.age_group_5yr is not null;
        ALTER TABLE UVT_AGEGROUP_5YR_r ADD PRIMARY KEY (item_code);

--    UVT_AGEGROUP_10YR
      DROP TABLE if exists UVT_AGEGROUP_10YR_r;
      CREATE TABLE UVT_AGEGROUP_10YR_r AS
      SELECT DISTINCT
             enc.age_group_10yr as item_code,
             enc.age_group_10yr::varchar(5) as item_text
        FROM esp_encounter_r enc
      WHERE enc.age_group_10yr is not null;
        ALTER TABLE UVT_AGEGROUP_10YR_r ADD PRIMARY KEY (item_code);

--    UVT_AGEGROUP_MS
      DROP TABLE if exists UVT_AGEGROUP_MS_r;
      CREATE TABLE UVT_AGEGROUP_MS_r AS
      SELECT DISTINCT
             enc.age_group_ms as item_code,
             enc.age_group_ms::varchar(5) as item_text
        FROM esp_encounter_r enc
      WHERE enc.age_group_ms is not null;
        ALTER TABLE UVT_AGEGROUP_MS_r ADD PRIMARY KEY (item_code);


--    UVT_DETECTED_CONDITION
      DROP TABLE if exists UVT_DETECTED_CONDITION_r;
      CREATE TABLE UVT_DETECTED_CONDITION_r AS
      SELECT DISTINCT
             disease.condition as item_code,
             disease.condition as item_text
        FROM esp_disease_r disease;
        ALTER TABLE UVT_DETECTED_CONDITION_r ADD PRIMARY KEY (item_code);

--    UVT_DETECTED_CRITERIA
      DROP TABLE if exists UVT_DETECTED_CRITERIA_r;
      CREATE TABLE UVT_DETECTED_CRITERIA_r AS
      SELECT DISTINCT
             disease.criteria as item_code,
             disease.criteria as item_text
        FROM esp_disease_r disease
      WHERE criteria is not null;
        ALTER TABLE UVT_DETECTED_CRITERIA_r ADD PRIMARY KEY (item_code);
      
--    UVT_DETECTED_STATUS
      DROP TABLE if exists UVT_DETECTED_STATUS_r;
      CREATE TABLE UVT_DETECTED_STATUS_r AS
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
        FROM esp_disease_r disease;
        ALTER TABLE UVT_DETECTED_STATUS_r ADD PRIMARY KEY (item_code);

        drop table if exists esp_demographic cascade;
        alter table esp_demographic_r rename to esp_demographic;
        alter index esp_demographic_patid_unique_idx_r rename to esp_demographic_patid_unique_idx;
        alter index esp_demographic_centerid_idx_r rename to esp_demographic_centerid_idx;
        alter index esp_demographic_birth_date_idx_r rename to esp_demographic_birth_date_idx;
        alter index esp_demographic_sex_idx_r rename to esp_demographic_sex_idx;
        alter index esp_demographic_hispanic_idx_r rename to esp_demographic_hispanic_idx;
        alter index esp_demographic_zip5_idx_r rename to esp_demographic_zip5_idx;
        alter index esp_demographic_race_idx_r rename to esp_demographic_race_idx;
        alter index esp_demographic_race_eth_idx_r rename to esp_demographic_race_eth_idx;
        alter index esp_demographic_smk_idx_r rename to esp_demographic_smk_idx;

        drop table if exists esp_encounter cascade;
        alter table esp_encounter_r rename to esp_encounter;
        alter index esp_encounter_centerid_idx_r rename to esp_encounter_centerid_idx;
        alter index esp_encounter_patid_idx_r rename to esp_encounter_patid_idx;
        alter index esp_encounter_encounterid_idx_r rename to esp_encounter_encounterid_idx;
        alter index esp_encounter_a_date_idx_r rename to esp_encounter_a_date_idx;
        alter index esp_encounter_d_date_idx_r rename to esp_encounter_d_date_idx;
        alter index esp_encounter_provider_idx_r rename to esp_encounter_provider_idx;
        alter index esp_encounter_facility_location_idx_r rename to esp_encounter_facility_location_idx;
        alter index esp_encounter_facility_code_idx_r rename to esp_encounter_facility_code_idx;
        alter index esp_encounter_enc_year_idx_r rename to esp_encounter_enc_year_idx;
        alter index esp_encounter_age_at_enc_year_idx_r rename to esp_encounter_age_at_enc_year_idx;
        alter index esp_encounter_age_group_5yr_idx_r rename to esp_encounter_age_group_5yr_idx;
        alter index esp_encounter_age_group_10yr_idx_r rename to esp_encounter_age_group_10yr_idx;
        alter index esp_encounter_age_group_ms_idx_r rename to esp_encounter_age_group_ms_idx;

        drop table if exists esp_diagnosis cascade;
        alter table esp_diagnosis_r rename to esp_diagnosis;
        alter index esp_diagnosis_dx_idx_r rename to esp_diagnosis_dx_idx;
        alter index esp_diagnosis_dx_like_idx_r rename to esp_diagnosis_dx_like_idx;
        alter index esp_diagnosis_centerid_idx_r rename to esp_diagnosis_centerid_idx;
        alter index esp_diagnosis_patid_idx_r rename to esp_diagnosis_patid_idx;
        alter index esp_diagnosis_encounterid_idx_r rename to esp_diagnosis_encounterid_idx;
        alter index esp_diagnosis_enc_type_idx_r rename to esp_diagnosis_enc_type_idx;
        alter index esp_diagnosis_provider_idx_r rename to esp_diagnosis_provider_idx;
        alter index esp_diagnosis_facility_code_idx_r rename to esp_diagnosis_facility_code_idx;
        alter index esp_diagnosis_facility_loc_idx_r rename to esp_diagnosis_facility_loc_idx;
        alter index esp_diagnosis_enc_year_idx_r rename to esp_diagnosis_enc_year_idx;
        alter index esp_diagnosis_age_at_enc_year_idx_r rename to esp_diagnosis_age_at_enc_year_idx;
        alter index esp_diagnosis_age_group_5yr_idx_r rename to esp_diagnosis_age_group_5yr_idx;
        alter index esp_diagnosis_age_group_10yr_idx_r rename to esp_diagnosis_age_group_10yr_idx;
        alter index esp_diagnosis_age_group_ms_idx_r rename to esp_diagnosis_age_group_ms_idx;
        
        drop table if exists esp_disease cascade;
        alter table esp_disease_r rename to esp_disease;
        alter index esp_disease_age_group_10yr_idx_r rename to esp_disease_age_group_10yr_idx;
        alter index esp_disease_age_group_5yr_idx_r rename to esp_disease_age_group_5yr_idx;
        alter index esp_disease_age_group_ms_idx_r rename to esp_disease_age_group_ms_idx;
        alter index esp_disease_centerid_idx_r rename to esp_disease_centerid_idx;
        alter index esp_disease_patid_idx_r rename to esp_disease_patid_idx;
        alter index esp_disease_condition_idx_r rename to esp_disease_condition_idx;
        alter index esp_disease_date_idx_r rename to esp_disease_date_idx;
        alter index esp_disease_age_at_detect_year_idx_r rename to esp_disease_age_at_detect_year_idx;
        alter index esp_disease_criteria_idx_r rename to esp_disease_criteria_idx;
        alter index esp_disease_status_idx_r rename to esp_disease_status_idx;

        drop table if exists UVT_SEX;
        alter table  UVT_SEX_r rename to UVT_SEX;
        drop table if exists UVT_RACE;
        alter table UVT_RACE_r rename to UVT_RACE;
        drop table if exists UVT_RACE_ETHNICITY;
        alter table UVT_RACE_ETHNICITY_r rename to UVT_RACE_ETHNICITY;
        drop table if exists UVT_ZIP5;
        alter table uvt_zip5_r rename to UVT_ZIP5;
        drop table if exists UVT_PROVIDER;
        alter table UVT_PROVIDER_r rename to UVT_PROVIDER;
        drop table if exists UVT_SITE;
        alter table UVT_SITE_r rename to UVT_SITE;
        drop table if exists UVT_CENTER;
        alter table UVT_CENTER_r rename to UVT_CENTER;
        drop table if exists UVT_PERIOD;
        alter table UVT_PERIOD_r rename to UVT_PERIOD;
        drop table if exists UVT_ENCOUNTER;
        alter table UVT_ENCOUNTER_r rename to UVT_ENCOUNTER;
        drop table if exists UVT_AGEGROUP_5YR;
        alter table UVT_AGEGROUP_5YR_r rename to UVT_AGEGROUP_5YR;
        drop table if exists UVT_AGEGROUP_10YR;
        alter table UVT_AGEGROUP_10YR_r rename to UVT_AGEGROUP_10YR;
        drop table if exists UVT_AGEGROUP_MS;
        alter table UVT_AGEGROUP_MS_r rename to UVT_AGEGROUP_MS;
        drop table if exists UVT_DETECTED_CONDITION;
        alter table UVT_DETECTED_CONDITION_r rename to UVT_DETECTED_CONDITION;
        drop table if exists UVT_DETECTED_CRITERIA;
        alter table UVT_DETECTED_CRITERIA_r rename to UVT_DETECTED_CRITERIA;
        drop table if exists UVT_DETECTED_STATUS;
        alter table UVT_DETECTED_STATUS_r rename to UVT_DETECTED_STATUS;

        GRANT SELECT ON esp_demographic TO mdphnet_user;
        GRANT SELECT ON esp_diagnosis TO mdphnet_user;
        GRANT SELECT ON esp_disease TO mdphnet_user;
        GRANT SELECT ON esp_encounter TO mdphnet_user;
        GRANT SELECT ON mdphnet_schema_update_history TO mdphnet_user;
        GRANT SELECT ON mdphnet_updated_patients TO mdphnet_user;
        GRANT SELECT ON uvt_agegroup_10yr TO mdphnet_user;
        GRANT SELECT ON uvt_agegroup_5yr TO mdphnet_user;
        GRANT SELECT ON uvt_agegroup_ms TO mdphnet_user;
        GRANT SELECT ON uvt_center TO mdphnet_user;
        GRANT SELECT ON uvt_detected_condition TO mdphnet_user;
        GRANT SELECT ON uvt_detected_criteria TO mdphnet_user;
        GRANT SELECT ON uvt_detected_status TO mdphnet_user;
        GRANT SELECT ON uvt_site TO mdphnet_user;
        GRANT SELECT ON uvt_encounter TO mdphnet_user;
        GRANT SELECT ON uvt_period TO mdphnet_user;
        GRANT SELECT ON uvt_provider TO mdphnet_user;
        GRANT SELECT ON uvt_race TO mdphnet_user;
        GRANT SELECT ON uvt_race_ethnicity TO mdphnet_user;
        GRANT SELECT ON uvt_sex TO mdphnet_user;
        GRANT SELECT ON uvt_site TO mdphnet_user;
        GRANT SELECT ON uvt_zip5 TO mdphnet_user;

--    FOREIGN KEYS USING UVTs
      ALTER TABLE esp_demographic ADD FOREIGN KEY (sex) REFERENCES uvt_sex (item_code);
      ALTER TABLE esp_demographic ADD FOREIGN KEY (race) REFERENCES uvt_race (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (provider) REFERENCES uvt_provider (item_code);
      ALTER TABLE esp_demographic ADD FOREIGN KEY (centerid) REFERENCES uvt_center (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (enc_year) REFERENCES uvt_period (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (enc_type) REFERENCES uvt_encounter (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (age_group_5yr) 
                  REFERENCES uvt_agegroup_5yr (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (age_group_10yr) 
                  REFERENCES uvt_agegroup_10yr (item_code);
      ALTER TABLE esp_encounter ADD FOREIGN KEY (age_group_ms) 
                  REFERENCES uvt_agegroup_ms (item_code);

      ALTER TABLE esp_disease ADD FOREIGN KEY (condition) 
                  REFERENCES uvt_detected_condition (item_code);
      ALTER TABLE esp_disease ADD FOREIGN KEY (criteria) 
                  REFERENCES uvt_detected_criteria (item_code);
      ALTER TABLE esp_disease ADD FOREIGN KEY (status) 
                  REFERENCES uvt_detected_status (item_code);
