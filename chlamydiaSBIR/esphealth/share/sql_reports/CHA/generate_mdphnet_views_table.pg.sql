alter table esp_demographic add column smoking varchar(13);
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
      from (select 'never'::text as val, patient_id
            from emr_socialhistory where tobacco_use ='Never') t00
            group by patient_id) t4 on t0.id=t4.patient_id;
alter table esp_temp_smoking add primary key (patid);
update esp_demographic
set smoking = (select smoking from esp_temp_smoking t0 where t0.patid=esp_demographic.patid);
update esp_demographic
set smoking = 'Not available' where smoking is null;

