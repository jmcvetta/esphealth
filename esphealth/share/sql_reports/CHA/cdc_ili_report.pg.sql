select * from (
select case 
         when cdc_site_id is null then center 
         else cdc_site_id 
       end as site_id, week,
       max(case age_group when '0-4' then ili_counts else 0 end) ili_0_4,
       max(case age_group when '5-24' then ili_counts else 0 end) ili_5_24,
       max(case age_group when '25-49' then ili_counts else 0 end) ili_25_49,
       max(case age_group when '50-64' then ili_counts else 0 end) ili_50_64,
       max(case age_group when '65+' then ili_counts else 0 end) ili_65_up,
       sum(tot_counts) total_visits,
       '0' revised_report
 from
esp_mdphnet.ili_summary
group by week, case 
         when cdc_site_id is null then center 
         else cdc_site_id 
       end) cdc_ili
order by site_id, week;
