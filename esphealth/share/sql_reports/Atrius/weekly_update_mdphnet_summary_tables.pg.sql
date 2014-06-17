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
                       and length(trim(code))>=3  ) icd9 
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
                       and length(trim(code))>=3  ) icd9
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
                       and length(trim(code))>=3  ) icd9
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
                       and length(trim(code))>=3  ) icd9
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
                       and length(trim(code))>=3  ) icd9
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
                       and length(trim(code))>=3  ) icd9
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
                       and length(trim(code))>=3  ) icd9
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
                       and length(trim(code))>=3  ) icd9
                 ON t1.code_ = replace(icd9.code, '.', '');
create index diag5dig_centerid_idx on esp_diagnosis_icd9_5dig (centerid);
create index diag5dig_age_group_type_idx on esp_diagnosis_icd9_5dig (age_group_type);
create index diag5dig_age_group_idx on esp_diagnosis_icd9_5dig (age_group);
create index diag5dig_sex_idx on esp_diagnosis_icd9_5dig (sex);
create index diag5dig_period_idx on esp_diagnosis_icd9_5dig (period);
create index diag5dig_code_idx on esp_diagnosis_icd9_5dig (code_);
create index diag5dig_setting_idx on esp_diagnosis_icd9_5dig (setting);

create table ili_summary
as select t0.cdc_site_id, t0.group as center, t0.zip5, 
          t1.week, t1.period_end, 
          t2.age_group, count(t2.ili) as ili_cnt, count(t2.*) as visit_count
from public.static_sitegroup t0,
     

drop table if exists ili_summary;
-- this takes on the order of 10 hours to complete
create table esp_mdphnet.ili_summary as
select t1.age_group, t1.weekdate as period_end, t1.week, t1.zip5, t1.center, t0.cdc_site_id, t1.ili_counts, t1.tot_counts
from static_sitegroup t0 right join
(select t1.age_group, t1.weekdate, t1.week, t1.zip5, t1.center, t0.ili_counts, t1.tot_counts
from (
select age_group, weekdate, week, zip5, center, count(visit_id) as ili_counts 
from (
select case 
            when to_char(visit.date,'d')='7' then visit.date
            when to_char(visit.date,'d')='6' then visit.date+interval '1 day'
            when to_char(visit.date,'d')='5' then visit.date+interval '2 days'
            when to_char(visit.date,'d')='4' then visit.date+interval '3 days'
            when to_char(visit.date,'d')='3' then visit.date+interval '4 days'
            when to_char(visit.date,'d')='2' then visit.date+interval '5 days'
            when to_char(visit.date,'d')='1' then visit.date+interval '6 days'
        end as weekdate
  , esp_mdphnet.mmwrwkn(visit.date) week
  , groups.zip5
  , groups.group as center
  , case 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) < 5 then '0-4'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 5 and 24 then '5-24' 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 25 and 49 then '25-49'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 50 and 64 then '50-64'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) > 64 then '65+'
    end age_group
  , visit.id visit_id
FROM emr_encounter visit 
       INNER JOIN emr_patient pat on (visit.patient_id = pat.id)
       INNER JOIN static_site sites on (visit.site_name=sites.name)
       INNER JOIN static_sitegroup groups on (sites.group_id=groups.group)
WHERE visit.date >= ('2010-01-03'::date)
   AND sites.ili_site
   AND visit.id in (SELECT min(vis.id) as id
                   FROM nodis_case cases
                     INNER JOIN nodis_case_events cev ON (cases.id = cev.case_id)
                     INNER JOIN hef_event hef ON (cev.event_id = hef.id)
                     INNER JOIN emr_encounter vis ON (hef.object_id = vis.id)
                   WHERE cases.condition = 'ili'
                     AND hef.name = 'dx:ili'
                     AND cases.date = hef.date
                     AND cases.patient_id=pat.id
                   GROUP BY cases.id)
) ili_by_yearsite 
group by age_group, weekdate, week, zip5, center
) t0
right join 
(
select age_group, weekdate, week, zip5, center, count(visit_id) as tot_counts 
from (
select case 
            when to_char(visit.date,'d')='7' then visit.date
            when to_char(visit.date,'d')='6' then visit.date+interval '1 day'
            when to_char(visit.date,'d')='5' then visit.date+interval '2 days'
            when to_char(visit.date,'d')='4' then visit.date+interval '3 days'
            when to_char(visit.date,'d')='3' then visit.date+interval '4 days'
            when to_char(visit.date,'d')='2' then visit.date+interval '5 days'
            when to_char(visit.date,'d')='1' then visit.date+interval '6 days'
        end as weekdate
  , esp_mdphnet.mmwrwkn(visit.date) week
  , groups.zip5
  , groups.group as center
  , case 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) < 5 then '0-4'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 5 and 24 then '5-24' 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 25 and 49 then '25-49'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 50 and 64 then '50-64'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) > 64 then '65+'
    end age_group
  , visit.id visit_id
FROM emr_encounter visit 
       INNER JOIN emr_patient pat on (visit.patient_id = pat.id)
       INNER JOIN static_site sites on (visit.site_name=sites.name)
       INNER JOIN static_sitegroup groups on (sites.group_id=groups.group)
WHERE visit.date >= ('2010-01-03'::date) and pat.date_of_birth is not null
   AND sites.ili_site
) ili_by_yearsite 
group by age_group, weekdate, week, zip5, center
) t1 on t0.age_group=t1.age_group and t0.weekdate=t1.weekdate and t0.week=t1.week 
         and t0.zip5=t1.zip5 and t0.center=t1.center) t1 on t1.center=t0.group;
ALTER TABLE ili_summary ADD CONSTRAINT ili_summary_pk PRIMARY KEY (age_group, week, center);
GRANT SELECT ON TABLE ili_summary TO esp30;

