select * from (
select groups.site_id, groups.week,
       max(case groups.age_group when '0-4' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_0_4,
       max(case groups.age_group when '5-24' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_5_24,
       max(case groups.age_group when '25-49' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_25_49,
       max(case groups.age_group when '50-64' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_50_64,
       max(case groups.age_group when '65+' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_65_up,
       case when sum(tot_counts) is null then 0 else sum(tot_counts) end as total_visits,
       '0' revised_report
 from
  (select case when cdc_site_id is null then center else cdc_site_id end as site_id,
          week,
          age_group,
          ili_counts,
          tot_counts
   from esp_mdphnet.ili_summary) as ili
  right join (select * from 
                (select distinct case when cdc_site_id is null then center else cdc_site_id end as site_id
                   from esp_mdphnet.ili_summary
                   where case when cdc_site_id is null then center else cdc_site_id end is not null) as sites,   
                (select distinct week 
                   from esp_mdphnet.ili_summary where week is not null) as weeks, 
                (select distinct age_group 
                   from esp_mdphnet.ili_summary where age_group is not null) as age_group) as groups 
     on ili.site_id=groups.site_id and ili.week=groups.week and ili.age_group=groups.age_group
group by groups.week, groups.site_id) cdc_ili
order by site_id, week;

