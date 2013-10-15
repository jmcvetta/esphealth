select * from (
select groups.site_id, groups.week as week_num,
       max(case groups.age_group when '0-4' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_in_0_4,
       max(case groups.age_group when '5-24' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_in_5_24,
       max(case groups.age_group when '25-49' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_in_25_49,
       max(case groups.age_group when '50-64' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_in_50_64,
       max(case groups.age_group when '65+' then 
                (case when ili_counts is null then 0 else ili_counts end) else 0 end) ili_in_65_plus,
       case when sum(tot_counts) is null then 0 else sum(tot_counts) end as total_vis_any_age,
       '0' revised_report
 from
  (select cdc_site_id as site_id,
          week,
          age_group,
          ili_counts,
          tot_counts
   from esp_mdphnet.ili_summary
   where period_end=(select max(period_end) from esp_mdphnet.ili_summary)
         and cdc_site_id is not null) as ili
  right join (select * from 
                (select distinct cdc_site_id as site_id
                   from esp_mdphnet.ili_summary
                   where cdc_site_id is not null) as sites,   
                (select distinct week 
                   from esp_mdphnet.ili_summary where week is not null
                        and period_end=(select max(period_end) from esp_mdphnet.ili_summary)) as weeks, 
                (select distinct age_group 
                   from esp_mdphnet.ili_summary where age_group is not null) as age_group) as groups 
     on ili.site_id=groups.site_id and ili.week=groups.week and ili.age_group=groups.age_group
group by groups.week, groups.site_id) cdc_ili
order by site_id, week_num;

