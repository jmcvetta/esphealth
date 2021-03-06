﻿--here are all the hef events we want for pos chlamydia;
-- ~30 seconds
drop table if exists temp_hef_poschlamyd;
CREATE TEMPORARY TABLE temp_hef_poschlamyd as
  select distinct patient_id, provider_id, date from hef_event where name = 'lx:chlamydia:positive' ;
alter table temp_hef_poschlamyd add primary key (patient_id,provider_id,date);
create index on temp_hef_poschlamyd (patient_id);
create index on temp_hef_poschlamyd (provider_id);
create index on temp_hef_poschlamyd (date);
analyze temp_hef_poschlamyd;
--select * from temp_hef_poschlamyd

--I'm going to get the list of patients with chlamydia episodes -- it gets used a few times.
-- less than a second
drop table if exists temp_chlamyd_pats;
CREATE TEMP TABLE temp_chlamyd_pats as
select distinct patient_id from temp_hef_poschlamyd;
alter table temp_chlamyd_pats add primary key (patient_id);
analyze temp_chlamyd_pats;
-- select * from temp_chlamyd_pats

--here are the ALL chlamyd tests.  If there are multiple results from the same day, I take the max of pos=1, neg=0, indet=-1
-- ~10 seconds
drop table if exists temp_hef_chlamyd;
CREATE TEMPORARY TABLE temp_hef_chlamyd as
  select patient_id,provider_id, date, 
    max(case when substr(name,14)='positive' then 1 when substr(name,14)='negative' then 0 else -1 end) as result
  from hef_event 
  where name like 'lx:chlamydia%'
  group by patient_id, provider_id, date;
alter table temp_hef_chlamyd add primary key (patient_id,provider_id,date);
create index on temp_hef_chlamyd (date);
analyze temp_hef_chlamyd;
--select * from temp_hef_chlamyd

--Gonorrhea results
-- less than a second
drop table if exists temp_hef_gonpos;
CREATE TEMPORARY TABLE temp_hef_gonpos as
  select distinct patient_id,provider_id, date from hef_event where name = 'lx:gonorrhea:positive' ;
alter table temp_hef_gonpos add primary key (patient_id,provider_id,date);
create index on temp_hef_gonpos (date);
analyze temp_hef_gonpos;
--select * from temp_hef_gonpos

--here is the preg results.
-- less than a second
--I think we need start AND end date, to determine if a patient is pregnant within 14 days of chlamydia pos result.
--Have to goose end_date where it's missing.  
--I am assuming from what little I know that missing end date can either mean ongoing pregnancy, or no info about termination/delivery
drop table if exists temp_preg;
CREATE TEMP TABLE temp_preg as
select distinct patient_id, start_date, 
  case
    when end_date is not null then end_date
    when end_date is null and start_date + interval '46 weeks' > now() then now() --40 is average gestation + 6 weeks is 3 StDevs. 
    else null
  end as end_date
from hef_timespan ht
where name='pregnancy' and exists (select null from temp_chlamyd_pats tcp where tcp.patient_id=ht.patient_id)
   and case
    when end_date is not null then end_date
    when end_date is null and start_date + interval '46 weeks' > now() then now()
    else null
  end is not null; 
alter table temp_preg add primary key (patient_id, start_date, end_date);
analyze temp_preg;

--here are ICD9 results
--this is a perfect example of the utility of temp tables.  
--The encounter table and dx tables are HUGE, but by limiting this temp table to just the columns and rows we need,
--and by imposing a single restriction that uses a normal to low-cardinaltiy index on the one table and joins via a 
--foreign key relationship, the result is generated relatively quickly and is then much more efficient to use subsequently 
--I'm not bothering to join with the temp chalmydia pats, since that would add to this query's complexity and the vast
--majority of these patients will already be in the chlamyd pats table.  The result here is small enough that a 
--subsequent join to the chlamydia pats table will be very fast.  As is, this query currently takes ~15 min.
--If we only need one of these dx codes (per your original script) it's way faster.  If you tried to embed this in a larger
--query, it would become less and less efficient as you added complexity.
drop table if exists temp_dx;
create temp table temp_dx as
select enc.patient_id, enc.provider_id, enc.date 
from emr_encounter enc 
  join emr_encounter_dx_codes dx on enc.id=dx.encounter_id 
  where dx.dx_code_id in ('icd9:078.88', 'icd9:079.88', 'icd9:079.98', 'icd9:099.5', 'icd9:099.50' ,'icd9:099.51','icd9:099.52','icd9:099.53','icd9:099.54','icd9:099.55','icd9:099.56','icd9:099.59');
--Another trick -- deleting duplicates here (on a small table) is way faster than imposing a distinct condition in prior query
--Careful with this.  If the result is large, or the result is a substantial portion of the original table, the distinct condition is faster.
delete from temp_dx dx
where dx.ctid <> (select min(dups.ctid) from temp_dx dups where dx.patient_id=dups.patient_id and dx.provider_id=dups.provider_id and dx.date=dups.date);
alter table temp_dx add primary key (patient_id, provider_id, date);
vacuum 
analyze temp_dx;
--select * from temp_dx;

--now doing the similar for chlamydia reportable dx codes
--this takes about 20 minutes.  
drop table if exists temp_rep_dx;
create temp table temp_rep_dx as
select distinct enc.patient_id, enc.date, dx.dx_code_id 
from emr_encounter enc 
  join emr_encounter_dx_codes dx on enc.id=dx.encounter_id 
  join conf_reportabledx_code rep on dx.dx_code_id=rep.dx_code_id 
  join temp_chlamyd_pats tcp on enc.patient_id=tcp.patient_id
  where rep.condition_id='chlamydia'; 
alter table temp_rep_dx add primary key (patient_id, date, dx_code_id);
create index on temp_rep_dx (date);
analyze temp_rep_dx;
--select * from temp_rep_dx;

--here is rx
--this one takes about 12 minutes.
drop table if exists temp_rx;
create temp table temp_rx as
select pre.patient_id, pre.provider_id, pre.date from emr_prescription pre join temp_chlamyd_pats cpat on cpat.patient_id=pre.patient_id  
where lower(pre.name) like '%azithromycin%' and lower(pre.name) like '%chlamydia%';
delete from temp_rx rx
where rx.ctid <> (select min(dups.ctid) from temp_rx dups where rx.patient_id=dups.patient_id and rx.provider_id=dups.provider_id and rx.date=dups.date);
alter table temp_rx add primary key (patient_id, provider_id, date);
vacuum 
analyze temp_rx;
--select * from temp_rx

--here is lb for EPT order extension plus the lab results for medication type. 
--I put all the info in one row to simplify things. 
--If the order_extension table gets big this query will become inefficient.
-- ~ 20 seconds, 
-- change result date to be the encounter date
drop table if exists temp_ept_lb;
CREATE TEMP TABLE temp_ept_lb as
  select ept0.patient_id,ept0.provider_id,ept0.date , lb.result_date, string_agg(distinct lb.native_code,',' order by lb.native_code) as native_code
      from emr_order_extension ept0 
      left join emr_labresult lb on ept0.order_natural_key=lb.order_natural_key and ept0.patient_id=lb.patient_id
      --where lb.native_code != '355804--' 
      group by ept0.patient_id,lb.result_date,ept0.provider_id,ept0.date, lb.result_date;
alter table temp_ept_lb add primary key (patient_id, provider_id, date);
analyze temp_ept_lb;
--select * from temp_ept_lb;

--Now I build most of the episode table, using the parts and pieces I assembled above.
--This would be terribly inefficient without the temp tables (small, compact, quickly queryable).
--This runs in approx ~10 seconds
--I use an anonymous block, which permits you to drop in plpgsql function/procedure language into sql code. 
--I don't know a better way to get patient-specific, dynamic temporal windows, but maybe there is. 
drop table if exists temp_chlamyd_episode;
create temporary table temp_chlamyd_episode 
( patient_id integer
  ,provider_id integer
  ,date date
  ,pstart_date date
  ,pend_date date
  ,dx_prov_id integer
  ,dx_date date
  ,rx_prov_id integer
  ,rx_date date
  ,ept_yn varchar(3)
  ,ept_date date
  ,ept_prvd varchar(3)
  ,ept_type varchar(20)
  ,ept_time varchar(20)
 ); 
--here's the anonymous block.  You could write this as a stored procedure, but unless you're going to call
-- the procedure a number of times, I prefer to see it in-line -- you don't have to go look at it elsewhere to see what it's doing
do $$
  declare
  pat_id int;
  insrtxt text;
  epi_date date;
  dx_date date;
  cursrow record;
  pregcursrow record;
  dxcursrow record;
  dx_ept_found boolean;
  eptcursrow record;
  rxcursrow record;
  epttxt text;
  foundit integer;
  begin
    for pat_id in select patient_id from temp_chlamyd_pats 
    -- these have to match what's in temp_hef_poschlamyd, because we just built the list from there
    loop
      epi_date:=null;
      dx_date:=null;
      for cursrow in execute 'select distinct date, provider_id from temp_hef_poschlamyd where patient_id=' || pat_id || ' order by date'
      loop
      
        if epi_date is null or cursrow.date > epi_date + interval '1 year' then
          dx_ept_found:=FALSE; -- set this to false just in case it could get carried over from prior loop iteration
          epi_date:=cursrow.date;
          insrtxt:='insert into temp_chlamyd_episode (patient_id, provider_id, date, pstart_date, pend_date, dx_prov_id, dx_date, rx_prov_id, rx_date, ept_yn, ept_date, ept_prvd, ept_type, ept_time) values (' ||
             pat_id || ',' || cursrow.provider_id || ',''' || to_char(epi_date,'yyyy-mm-dd') || '''::date, ';
          execute 'select patient_id, start_date, end_date from temp_preg prg where ''' ||
                  to_char(epi_date,'yyyy-mm-dd') || '''::date + interval ''14 days'' between start_date and end_date + interval ''14 days''' ||
              ' and patient_id=' || pat_id || ' order by start_date limit 1' into pregcursrow;
          get diagnostics foundit = ROW_COUNT;
          if foundit<>1 then
            insrtxt:=insrtxt || 'null::date, null::date, ';
          else
            insrtxt:=insrtxt || '''' || to_char(pregcursrow.start_date,'yyyy-mm-dd') || '''::date, ''' || 
                to_char(pregcursrow.end_date,'yyyy-mm-dd') || '''::date, ';  
            if insrtxt is null then raise notice '%', 'check line 188'; end if;
          end if;
          execute 'select provider_id, date from temp_dx where date between ''' || 
              to_char(epi_date,'yyyy-mm-dd') || '''::date and ''' || to_char(epi_date,'yyyy-mm-dd') || '''::date + interval ''365 days''' ||
              ' and patient_id=' || pat_id || ' order by date limit 1' into dxcursrow; 
          get diagnostics foundit = ROW_COUNT;
          if foundit<>1 then
            insrtxt:=insrtxt || 'null, null::date, ';
          else
            insrtxt:=insrtxt || dxcursrow.provider_id || ', ''' || to_char(dxcursrow.date,'yyyy-mm-dd') || '''::date, ';
            if insrtxt is null then raise notice '%', 'check line 198'; end if;
            --ept is associated with dx or rx. Check for dx first.  Use plus or minus one day.  Is that OK?
            execute 'select patient_id, date,  native_code, result_date from temp_ept_lb where patient_id=' || pat_id || ' and date between ''' || to_char(dxcursrow.date,'yyyy-mm-dd') || 
                     '''::date - interval ''1 days'' and ''' || to_char(dxcursrow.date,'yyyy-mm-dd') || '''::date + interval ''1 days''' into eptcursrow;
            get diagnostics foundit = ROW_COUNT;
            if foundit<>1 then
              dx_ept_found:=FALSE;
            else
              dx_ept_found:=TRUE; --the ept fields get inserted after the rx fields in any case, so I just need a boolian here to let me know I have the ept already
            end if;
          end if;
          execute 'select provider_id, date from temp_rx where date between ''' || 
              to_char(epi_date,'yyyy-mm-dd') || '''::date and ''' || to_char(epi_date,'yyyy-mm-dd') || '''::date + interval ''365 days''' ||
              ' and patient_id=' || pat_id || ' order by date limit 1' into rxcursrow; 
          get diagnostics foundit = ROW_COUNT;
          if foundit<>1 then
            insrtxt:=insrtxt || 'null, null::date, ';
            if dx_ept_found then
              if eptcursrow.native_code='355805--'  then epttxt:='1'', ''Floor Meds Dispensed'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              elsif eptcursrow.native_code='355806--' then epttxt:='1'', ''Print Rx Manual Fax'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              elsif eptcursrow.native_code='355805--,355806--' then epttxt:='1'', ''Floor Meds Dispensed and Print Rx Manual Fax'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              elsif eptcursrow.native_code='355804--' then epttxt:='0'', ''Declined'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              else epttxt:='0'', null, null)';
              end if;
              insrtxt:=insrtxt || '''1'', ''' || to_char(eptcursrow.date,'yyyy-mm-dd') || '''::date, ''' || epttxt;
              if insrtxt is null then raise notice '%', 'check line 223'; end if;
            else
              insrtxt:=insrtxt || '''0'', null::date, null, null, null)';
            end if;
          else
            insrtxt:=insrtxt || rxcursrow.provider_id || ', ''' || to_char(rxcursrow.date,'yyyy-mm-dd') || '''::date, ';
            if insrtxt is null then raise notice '%', 'check line 229'; end if;
            if dx_ept_found then
              if eptcursrow.native_code='355805--'  then epttxt:='1'', ''Floor Meds Dispensed'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              elsif eptcursrow.native_code='355806--' then epttxt:='1'', ''Print Rx Manual Fax'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              elsif eptcursrow.native_code='355805--,355806--'  then epttxt:='1'', ''Floor Meds Dispensed and Print Rx Manual Fax'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              elsif eptcursrow.native_code='355804--' then epttxt:='0'', ''Declined'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              else epttxt:='0'', null, null)';
              end if;
              insrtxt:=insrtxt || '''1'', ''' || to_char(eptcursrow.date,'yyyy-mm-dd') || '''::date, ''' || epttxt;
              if insrtxt is null then raise notice 'check line 237: %, %',  date_part('hour',eptcursrow.result_date); end if;
            else
              execute 'select patient_id, date,  native_code, result_date from temp_ept_lb where patient_id=' || pat_id || 'and date between ''' ||
                 to_char(rxcursrow.date,'yyyy-mm-dd') || '''::date - interval ''1 days'' and ''' || to_char(rxcursrow.date,'yyyy-mm-dd') || '''::date + interval ''1 days'''
                 into eptcursrow;
              get diagnostics foundit = ROW_COUNT;
              if foundit<>1 then
                insrtxt:=insrtxt || '0, null::date, null, null, null)';
              else
                if eptcursrow.native_code='355805--'  then epttxt:='1'', ''Floor Meds Dispensed'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
                elsif eptcursrow.native_code='355806--' then epttxt:='1'', ''Print Rx Manual Fax'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
                elsif eptcursrow.native_code='355805--,355806--'  then epttxt:='1'', ''Floor Meds Dispensed and Print Rx Manual Fax'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
                elsif eptcursrow.native_code='355804--' then epttxt:='0'', ''Declined'', ''' || COALESCE(to_char(date_part('hour',eptcursrow.result_date),'99'),'') || ''')';
              else epttxt:='0'', null, null)';
                end if;
                insrtxt:=insrtxt || '''1'', ''' || to_char(eptcursrow.date,'yyyy-mm-dd') || '''::date, ''' || epttxt;
                if insrtxt is null then raise notice '%', 'check line 252'; end if;
              end if;
            end if;
          end if;
          execute insrtxt;
        end if;
      end loop;
    end loop;
  end;
$$ language plpgsql;
alter table temp_chlamyd_episode add primary key (patient_id, date);
analyze temp_chlamyd_episode;
--select * from temp_chlamyd_episode

--now build the report query from epi and the patient and provider tables.
copy (
select  pat.id as ESP_patid,
        pat.mrn as Atrius_patid,
       epi.date as dateposchlamydia, 
       date_part('year', age(epi.date,pat.date_of_birth)) as ageatchlamydiapos,
       pat.gender, 
       pat.race, 
       case 
         when lower(pat.race) like '%hispanic%' and lower(pat.race) not like '%non%' then 'HISPANIC' 
         when lower(pat.race) like '%hispanic%' and  lower(pat.race)  like '%non%' then 'NON-HISPANIC' 
         else '' 
       end as ethnicityvalues, -- calculated from race
       case when epi.pstart_date is not null then '1'
       else '0'
       end as pregnantwhenposchla,
       epi.provider_id  as providerposchla,
       pro1.dept as providerlocposchla,
       epi.dx_date as datedxchla,
       epi.dx_prov_id as providerdxchla,
       pro2.dept as providerlocdxchla,
       epi.rx_date as daterxchla,
       epi.rx_prov_id as providerrxchla,
       pro3.dept as providerlocrxchla,
       epi.ept_yn as eptdata, 
       epi.ept_prvd as eptprovided,
       epi.ept_type as typeept, 
       epi.ept_date as dateept,
       'not available',--epi.ept_time as timeofdayept,
       case when gon.patient_id is not null then '1' else '0' end as positivegonorrhea, 
       null as hashiv, --place holder until condition is completed
       null as hivtest, --place holder until condition is completed
       case when rep.patient_id is not null then '1' else '0' end as repeatchlamydia,
       rep.date as daterepeatchla,
       case when rep.result=1 then 'Positive' when rep.result=0 then 'Negative' when rep.result=-1 then 'Indeterminate' else null end as resultrepeatchla,
       case when reppos.patient_id is not null then '1' else '0' end as repeatposchla,
       reppos.date as daterepeatposchla ,
       rep2.date as scndrep_date,
       case when rep2.result=1 then 'Positive' when rep2.result=0 then 'Negative' when rep2.result=-1 then 'Indeterminate' else null end as scndrep_res,
       case when rep2.edate is not null then 1 when rep2.date is not null then 0 end as scndrep_ept,
       rep2.edate as scndrep_eptdate,
       rep2.ept_type as scndrep_type,
       rep3.date as thrdrep_date,
       case when rep3.result=1 then 'Positive' when rep3.result=0 then 'Negative' when rep3.result=-1 then 'Indeterminate' else null end as thrdrep_res,
       case when rep3.edate is not null then 1  when rep3.date is not null then 0 end as thrdrep_ept,
       rep3.edate as thrdrep_eptdate,
       rep3.ept_type as thrdrep_type,
       case when symp.icd9_099_40 is null then 0 else symp.icd9_099_40 end icd9_099_40,
       case when symp.icd9_597_80 is null then 0 else symp.icd9_597_80 end icd9_597_80,
       case when symp.icd9_616_0 is null then 0 else symp.icd9_616_0 end icd9_616_0,
       case when symp.icd9_616_10 is null then 0 else symp.icd9_616_10 end icd9_616_10,
       case when symp.icd9_623_5 is null then 0 else  symp.icd9_623_5 end  icd9_623_5,
       case when symp.icd9_780_6 is null then 0 else symp.icd9_780_6 end icd9_780_6,
       case when symp.icd9_780_60 is null then 0 else symp.icd9_780_60 end icd9_780_60,
       case when symp.icd9_788_7 is null then 0 else symp.icd9_788_7 end icd9_788_7,
       case when symp.icd9_789_00 is null then 0 else symp.icd9_789_00 end icd9_789_00,
       case when symp.icd9_789_03 is null then 0 else symp.icd9_789_03 end icd9_789_03,
       case when symp.icd9_789_04 is null then 0 else symp.icd9_789_04 end icd9_789_04,
       case when symp.icd9_789_07 is null then 0 else symp.icd9_789_07 end icd9_789_07,
       case when symp.icd9_789_09 is null then 0 else symp.icd9_789_09 end icd9_789_09
 from emr_patient pat 
      join temp_chlamyd_pats tcp on tcp.patient_id=pat.id
      join temp_chlamyd_episode epi on tcp.patient_id=epi.patient_id
      join emr_provider pro1 on epi.provider_id=pro1.id 
      left join emr_provider pro2 on epi.dx_prov_id=pro2.id
      left join emr_provider pro3 on epi.rx_prov_id=pro3.id
      left join (select distinct gon.patient_id, epi.date as edate from temp_hef_gonpos gon 
                  join temp_chlamyd_episode epi on gon.patient_id=epi.patient_id 
                  where gon.date between epi.date - interval '14 days' and epi.date + interval '14 days') gon 
                  on epi.patient_id=gon.patient_id and epi.date=gon.edate
      left join (with row_sumry as 
                 (select thc.patient_id, thc.date, thc.result, epi.date as edate, 
                  row_number() over (partition by epi.patient_id, epi.date order by thc.date) as rn
                  from temp_hef_chlamyd thc 
                  join temp_chlamyd_episode epi on thc.patient_id=epi.patient_id 
                  where thc.date between epi.date + interval '14 days' and epi.date + interval '365 days'
                 ) select rs.patient_id, rs.date, rs.result, rs.edate from row_sumry rs where rs.rn=1  --order by rs.patient_id, rs.date
                ) rep on rep.patient_id=epi.patient_id and rep.edate=epi.date
      left join (with row_sumry as
                 (select reppos.patient_id, reppos.date, epi.date as edate, 
                  row_number() over (partition by epi.patient_id, epi.date order by reppos.date) as rn
                  from temp_hef_poschlamyd reppos
                  join temp_chlamyd_episode epi on reppos.patient_id=epi.patient_id
                 where reppos.date between epi.date + interval '14 days' and epi.date + interval '365 days')
                 select rs.patient_id, rs.date, rs.edate from row_sumry rs where rs.rn=1
                 ) reppos on reppos.patient_id=epi.patient_id and reppos.edate=epi.date
       left join (with row_sumry as 
                 (select thc.patient_id, thc.date, thc.result, ept.date as edate, epi.date as epidate,
                  case
                    when ept.native_code='355805--'  then 'Floor Meds Dispensed'
                    when ept.native_code='355806--' then 'Print Rx Manual Fax'
                    when ept.native_code='355805--,355806--' then 'Floor Meds Dispensed and Print Rx Manual Fax'
                    when ept.native_code='355804--' then 'Declined'
                  end as ept_type,
                  row_number() over (partition by epi.patient_id, epi.date order by thc.date) as rn
                  from temp_hef_chlamyd thc 
                  join temp_chlamyd_episode epi on thc.patient_id=epi.patient_id
             left join temp_ept_lb ept on thc.patient_id=ept.patient_id and epi.date between ept.date - interval '1 days' and ept.date + interval '1 days'                   
                  where thc.date between epi.date + interval '14 days' and epi.date + interval '365 days'
                 ) select rs.patient_id, rs.date, rs.result, rs.edate, rs.ept_type, rs.epidate from row_sumry rs where rs.rn=2  
                ) rep2 on rep2.patient_id=epi.patient_id and rep2.epidate=epi.date
       left join (with row_sumry as 
                 (select thc.patient_id, thc.date, thc.result, ept.date as edate, epi.date as epidate, 
                  case
                    when ept.native_code='355805--'  then 'Floor Meds Dispensed'
                    when ept.native_code='355806--' then 'Print Rx Manual Fax'
                    when ept.native_code='355805--,355806--' then 'Floor Meds Dispensed and Print Rx Manual Fax'
                    when ept.native_code='355804--' then 'Declined'
                  end as ept_type,
                  row_number() over (partition by epi.patient_id, epi.date order by thc.date) as rn
                  from temp_hef_chlamyd thc 
                  join temp_chlamyd_episode epi on thc.patient_id=epi.patient_id
             left join temp_ept_lb ept on thc.patient_id=ept.patient_id and epi.date between ept.date - interval '1 days' and ept.date + interval '1 days'                   
                  where thc.date between epi.date + interval '14 days' and epi.date + interval '365 days'
                 ) select rs.patient_id, rs.date, rs.result, rs.edate, rs.ept_type, rs.epidate from row_sumry rs where rs.rn=3  
                ) rep3 on rep3.patient_id=epi.patient_id and rep3.epidate=epi.date
       left join (select trd.patient_id, epi.date as edate,
                    max(case when trd.dx_code_id='icd9:099.40' then 1 else 0 end) as icd9_099_40,
                    max(case when trd.dx_code_id='icd9:597.80' then 1 else 0 end) as icd9_597_80,
                    max(case when trd.dx_code_id='icd9:616.0' then 1 else 0 end) as icd9_616_0,
                    max(case when trd.dx_code_id='icd9:616.10' then 1 else 0 end) as icd9_616_10,
                    max(case when trd.dx_code_id='icd9:623.5' then 1 else 0 end) as icd9_623_5,
                    max(case when trd.dx_code_id='icd9:780.6' then 1 else 0 end) as icd9_780_6,
                    max(case when trd.dx_code_id='icd9:780.60' then 1 else 0 end) as icd9_780_60,
                    max(case when trd.dx_code_id='icd9:788.7' then 1 else 0 end) as icd9_788_7,
                    max(case when trd.dx_code_id='icd9:789.00' then 1 else 0 end) as icd9_789_00,
                    max(case when trd.dx_code_id='icd9:789.03' then 1 else 0 end) as icd9_789_03,
                    max(case when trd.dx_code_id='icd9:789.04' then 1 else 0 end) as icd9_789_04,
                    max(case when trd.dx_code_id='icd9:789.07' then 1 else 0 end) as icd9_789_07,
                    max(case when trd.dx_code_id='icd9:789.09' then 1 else 0 end) as icd9_789_09
                  from temp_rep_dx trd
                  join temp_chlamyd_episode epi on trd.patient_id=epi.patient_id 
                 where trd.date between epi.date - interval '14 days' and epi.date + interval '14 days' --from conf_conditionconfig
                 group by trd.patient_id, epi.date  order by trd.patient_id, epi.date ) symp on symp.patient_id=epi.patient_id and symp.edate=epi.date
where epi.date >= '12-01-2014'  
 order by epi.date
 )to '/tmp/07_07_2015_chlamydia_reinfection.csv' with (format csv, header);
