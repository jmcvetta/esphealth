drop table if exists ili_visits;
create table ili_visits as
SELECT distinct respcodes.id from
                   (select ilivis.id
                    from public.emr_encounter ilivis,
                         public.emr_encounter_dx_codes iliRcodes,
                         public.static_ili_encounter_type types
                    where iliRcodes.encounter_id=ilivis.id and upper(types.raw_encounter_type)=upper(ilivis.raw_encounter_type)
                          and iliRcodes.dx_code_id in ('icd9:079.3','icd9:079.89','icd9:079.99','icd9:460','icd9:462','icd9:464.00','icd9:464.01','icd9:464.10','icd9:464.11','icd9:464.20',
                                              'icd9:464.21','icd9:465.0','icd9:465.8','icd9:465.9','icd9:466.0','icd9:466.19','icd9:478.9','icd9:480.8','icd9:480.9','icd9:481','icd9:482.40',
                                              'icd9:482.41','icd9:482.42','icd9:482.49','icd9:484.8','icd9:485','icd9:486','icd9:487.0','icd9:487.1','icd9:487.8','icd9:784.1','icd9:786.2'))
                    respcodes
                    left outer join
                    (select id
                     from public.emr_encounter
                     where temperature >= 100)
                    fevvis on respcodes.id=fevvis.id
                    left outer join
                    (select ilivis.id
                     from public.emr_encounter ilivis,
                         public.emr_encounter_dx_codes iliFcodes
                     where iliFcodes.encounter_id=ilivis.id
                          and ilivis.temperature is null
                          and iliFcodes.dx_code_id in ('icd9:780.6','icd9:780.31'))
                     fevcodes on respcodes.id=fevcodes.id
                 where fevvis.id is not null or fevcodes.id is not null;
alter table ili_visits add primary key (id);
drop table if exists ili_summary;
-- this takes on the order of 4 hours to complete
create table esp_mdphnet.ili_summary as
select t1.age_group, t1.weekdate as period_end, t1.week, t1.zip5, t1.center, t0.cdc_site_id, t1.ili_counts, t1.tot_counts
from public.static_sitegroup t0 right join
(select t1.age_group, t1.weekdate, t1.week, t1.zip5, t1.center, t0.ili_counts, t1.tot_counts
from (
select age_group, weekdate, week, zip5, center, count(id) as ili_counts 
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
  , esp_mdphnet.mmwrwkn(visit.date) as week
  , groups.zip5
  , groups.group as center
  , case 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) < 5 then '0-4'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 5 and 24 then '5-24' 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 25 and 49 then '25-49'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 50 and 64 then '50-64'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) > 64 then '65+'
    end as age_group
  , visit.id
FROM (select t00.date, t00.site_name, t00.patient_id, t00.id 
      from emr_encounter t00 
       inner join ili_visits t01 on t00.id=t01.id
       inner join public.static_ili_encounter_type t02 
         on upper(t00.raw_encounter_type)=upper(t02.raw_encounter_type)) visit 
       INNER JOIN emr_patient pat on (visit.patient_id = pat.id)
       INNER JOIN static_site sites on (visit.site_name=sites.name)
       INNER JOIN static_sitegroup groups on (sites.group_id=groups.group)
WHERE visit.date >= ('2010-01-03'::date) and pat.date_of_birth is not null AND sites.ili_site
      and visit.date<=date_trunc('week',(select max(date) from emr_encounter)- interval '5 days') + interval '5 days'
) ili_by_yearsite 
group by age_group, weekdate, week, zip5, center
) t0
right join 
(
select age_group, weekdate, week, zip5, center, count(id) as tot_counts 
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
  , esp_mdphnet.mmwrwkn(visit.date) as week
  , groups.zip5
  , groups.group as center
  , case 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) < 5 then '0-4'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 5 and 24 then '5-24' 
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 25 and 49 then '25-49'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) between 50 and 64 then '50-64'
      when extract(YEAR FROM age(visit.date::timestamp, pat.date_of_birth::timestamp)) > 64 then '65+'
    end as age_group
  , visit.id
FROM (select t00.date, t00.site_name, t00.patient_id, t00.id 
      from emr_encounter t00 
       inner join public.static_ili_encounter_type t02 
         on upper(t00.raw_encounter_type)=upper(t02.raw_encounter_type)) visit 
       INNER JOIN emr_patient pat on (visit.patient_id = pat.id)
       INNER JOIN static_site sites on (visit.site_name=sites.name)
       INNER JOIN static_sitegroup groups on (sites.group_id=groups.group)
WHERE visit.date >= ('2010-01-03'::date) and pat.date_of_birth is not null AND sites.ili_site 
   and visit.date<=date_trunc('week',(select max(date) from emr_encounter)- interval '5 days') + interval '5 days'
) ili_by_yearsite 
group by age_group, weekdate, week, zip5, center
) t1 on t0.age_group=t1.age_group and t0.weekdate=t1.weekdate and t0.week=t1.week 
         and t0.zip5=t1.zip5 and t0.center=t1.center) t1 on t1.center=t0.group;
ALTER TABLE ili_summary ADD CONSTRAINT ili_summary_pk PRIMARY KEY (age_group, week, center);
GRANT SELECT ON TABLE ili_summary TO esp3;
