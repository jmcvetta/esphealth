--since we're updating tables, we want things to stop if there are problems:
\set ON_ERROR_STOP


--drop all the  tables used in a prior pass
drop table if exists mdphnet_updated_patients;
drop table if exists esp_demographic_u;
drop table if exists esp_encounter_u;
drop table if exists esp_diagnosis_u;
--drop table if exists esp_disease_u;
drop table if exists mdphnet_updated_patients;
drop table if exists mdphnet_updated_encounters;
--drop table if exists mdphnet_updated_diseases;

create temp table starttime as select current_timestamp starttime;
 
insert into mdphnet_schema_update_history (latest_update_start)
  select starttime from starttime;

--create the table of patients who have been updated
create table mdphnet_updated_patients as select t0.natural_key as patid from emr_patient t0,
  (select max(latest_update_start) as updated_timestamp from mdphnet_schema_update_history where latest_update_complete is not null) t1 
  where t0.updated_timestamp>=t1.updated_timestamp;
alter table mdphnet_updated_patients 
  add constraint mdphnet_updated_patients_pkey primary key (patid);
vacuum analyze mdphnet_updated_patients;

--create the demog table
CREATE table esp_demographic_u AS
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
       zip5
  FROM public.emr_patient pat
  inner join mdphnet_updated_patients updtpats on updtpats.patid=pat.natural_key
  inner join public.emr_provenance prvn on pat.provenance_id=prvn.provenance_id 
  where prvn.source ilike 'epicmem%'
    and exists (select null from emr_encounter t0 where t0.patient_id=pat.id); --patient must have at least one encounter record
  

--create the table of encounter ids that have been updated
create table mdphnet_updated_encounters as select t0.natural_key as encounterid from emr_encounter t0,
  (select max(latest_update_start) as updated_timestamp from mdphnet_schema_update_history where latest_update_complete is not null) t1 
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
       age_at_year_start(enc.date, pat.date_of_birth::date) age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth::date)::varchar(5) age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN public.emr_patient pat ON enc.patient_id = pat.id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id
         inner join mdphnet_updated_encounters updts on updts.encounterid=enc.natural_key
         inner join public.emr_provenance prvn on pat.provenance_id=prvn.provenance_id 
         where prvn.source ilike 'epicmem%';

--diagnoses are based on encounter ICD9 data, so same subset
CREATE table esp_diagnosis_u AS
SELECT '1'::varchar(1) centerid,
       pat.natural_key patid,
       enc.natural_key encounterid,
       enc.date - ('1960-01-01'::date) a_date,
       prov.natural_key provider,
       'AV'::varchar(10) enc_type, --this is initial value for Mass League data
       substr(diag.dx_code_id,6) dx,
       icd9_prefix(diag.dx_code_id, 3)::varchar(4) dx_code_3dig,
       icd9_prefix(diag.dx_code_id, 4)::varchar(5) dx_code_4dig,
       case 
         when length(icd9_prefix(diag.dx_code_id, 4))=5
	   then substr(diag.dx_code_id,6,6)
         else substr(diag.dx_code_id,6,5)
       end as dx_code_4dig_with_dec,
       icd9_prefix(diag.dx_code_id, 5)::varchar(6) dx_code_5dig,
       case 
         when length(icd9_prefix(diag.dx_code_id, 4))=6
	   then substr(diag.dx_code_id,6,7)
         else substr(diag.dx_code_id,6,6)
       end as dx_code_5dig_with_dec,
       enc.site_name facility_location,
       enc.site_natural_key facility_code,
       date_part('year', enc.date)::integer enc_year,
       age_at_year_start(enc.date, pat.date_of_birth::date) age_at_enc_year,
       age_group_5yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_5yr,
       age_group_10yr(enc.date, pat.date_of_birth::date)::varchar(5) age_group_10yr,
       age_group_ms(enc.date, pat.date_of_birth::date)::varchar(5) age_group_ms
  FROM public.emr_encounter enc
         INNER JOIN public.emr_patient pat ON enc.patient_id = pat.id
         INNER JOIN (select * from public.emr_encounter_dx_codes 
                     where strpos(trim(dx_code_id),'.')<>3
                       and length(trim(dx_code_id))>=3 ) diag ON enc.id = diag.encounter_id
         LEFT JOIN public.emr_provider prov ON enc.provider_id = prov.id
         inner join mdphnet_updated_encounters updtencs on updtencs.encounterid=enc.natural_key
         inner join public.emr_provenance prvn on pat.provenance_id=prvn.provenance_id 
         where prvn.source ilike 'epicmem%';


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

--   UVT_RACE_ETHNICITY
     insert into uvt_race_ethnicity
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
     from esp_demographic_U pat
     where not exists (select null from uvt_race_ethnicity t0 where t0.item_code=pat.race_ethnicity) ;


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
               INNER JOIN public.static_dx_code icd9 ON diag.dx = icd9.code
           where not exists (select null from uvt_dx t0 where t0.item_code=diag.dx)
                and icd9.type='icd9';

--    UVT_DX_3DIG
      insert into UVT_DX_3DIG
      SELECT DISTINCT
             diag.dx_code_3dig item_code,
             icd9.name item_text
        FROM esp_diagnosis_u diag
               LEFT OUTER JOIN  (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 
                       and type='icd9') icd9 
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
               LEFT OUTER JOIN  (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
               ON diag.dx_code_4dig = REPLACE(icd9.code, '.', '')
        WHERE diag.dx_code_4dig is not null and icd9.name not like '%load_epic%' and icd9.type='icd9'
         and not exists (select null from uvt_dx_4dig t0 where t0.item_code=diag.dx_code_4dig);

--    UVT_DX_5DIG
      insert into UVT_DX_5DIG
      SELECT DISTINCT
             diag.dx_code_5dig item_code,
             diag.dx_code_5dig_with_dec item_code_with_dec,
             icd9.name item_text
        FROM esp_diagnosis_u diag
               LEFT OUTER JOIN  (select * from public.static_dx_code
                    where   strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) icd9
               ON diag.dx_code_5dig = REPLACE(icd9.code, '.', '')
        WHERE diag.dx_code_5dig is not null and icd9.name not like '%load_epic%' and icd9.type='icd9'
          and not exists (select null from uvt_dx_5dig t0 where t0.item_code=diag.dx_code_5dig);


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
      race_ethnicity=t1.race_ethnicity,
      zip5=t1.zip5
  from (select *
        from esp_demographic_u) t1
  where t1.patid=t0.patid;

insert into esp_demographic (centerid, patid, sex, hispanic, race, zip5, birth_date, race_ethnicity)
  (select centerid, patid, sex, hispanic, race, zip5, birth_date, race_ethnicity
  from esp_demographic_u
   t0 where not exists (select null from esp_demographic t1 where t1.patid=t0.patid));
insert into esp_encounter select * from esp_encounter_u;
insert into esp_diagnosis select * from esp_diagnosis_u;
--insert into esp_disease select * from esp_disease_u;

--now get the smoking data
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
update esp_demographic
set smoking = (select smoking from esp_temp_smoking t0 where t0.patid=esp_demographic.patid);

--    UVT_SMOKING
      insert into UVT_SMOKING
      select distinct 
             pat.smoking item_code,
             null::varchar(10) item_text
      from esp_demographic pat
      where not exists (select null from uvt_smoking t0 where t0.item_code=pat.smoking);

--now vacuum analyze each table
vacuum analyze esp_demographic;
vacuum analyze esp_encounter;
vacuum analyze esp_diagnosis;
--vacuum analyse esp_disease;

--Now that update sets are pulled,
--add timestamp to current history as the point where the updates completed
update mdphnet_schema_update_history
  set latest_update_complete= current_timestamp, patients_replaced = (select count(*) from mdphnet_updated_patients)
  where latest_update_start = (select starttime from starttime);


--NOW rebuild the esp_disease table and UVT tables from scratch

drop table if exists esp_current_asthma_cases cascade;
create table esp_current_asthma_cases AS
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

create index esp_current_asthma_cases_caseid_idx on esp_current_asthma_cases (id);
vacuum analyze esp_current_asthma_cases;

CREATE or replace VIEW esp_disease_v AS
SELECT pat.center_id centerid,
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
         INNER JOIN public.emr_patient pat ON disease.patient_id = pat.id
         INNER JOIN public.emr_provenance prvn on pat.provenance_id = prvn.provenance_id
  WHERE prvn.source like 'epicmem%'
	and (disease.condition in ('depression', 'ili', 'diabetes:type-1', 'diabetes:type-2', 'diabetes:gestational', 'diabetes:prediabetes')
        or disease.id in (select id from esp_current_asthma_cases));

drop table if exists esp_disease_r cascade;
create table esp_disease_r as select t0.* from esp_disease_v
	as t0 inner join esp_demographic as t1
	on t0.patid=t1.patid;

INSERT INTO esp_disease_r (select t0.* from esp_condition
       as t0 inner join esp_demographic as t1
       on t0.patid=t1.patid
       where (current_date-('1960-01-01'::date) - t0.date <= 365) and t0.condition in ('benzodiarx', 'opioidrx', 'benzopiconcurrent'));

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
alter table esp_disease_r add foreign key (patid) references esp_demographic (patid);
drop view if exists esp_disease_v;

--    UVT_DETECTED_CONDITION
      DROP TABLE if exists UVT_DETECTED_CONDITION_r;
	 CREATE TABLE UVT_DETECTED_CONDITION_r AS
		SELECT DISTINCT disease.condition as item_code,
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
      SELECT DISTINCT disease.status as item_code,
    CASE
WHEN disease.status = 'AR' THEN 'Awaiting Review'::varchar(80)
WHEN disease.status = 'UR' THEN 'Under Review'::varchar(80)
WHEN disease.status = 'RM' THEN 'Review By MD'::varchar(80)
WHEN disease.status = 'FP' THEN 'False Positive - Do Not Process'::varchar(80)
WHEN disease.status = 'Q'  THEN 'Confirmed Case, Transmit to Health Department'::varchar(80)
WHEN disease.status = 'S'  THEN 'Transmitted to Health Department'::varchar(80) ELSE 'Not Mapped'::varchar(80)
 END as item_text
 FROM esp_disease_r disease;
 ALTER TABLE UVT_DETECTED_STATUS_r ADD PRIMARY KEY (item_code);

drop table if exists esp_disease cascade; alter table esp_disease_r rename to esp_disease;

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

vacuum analyze esp_disease;


