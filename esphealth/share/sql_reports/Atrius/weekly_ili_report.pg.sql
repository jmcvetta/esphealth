select * from (
select * from (
select period_end::date as week_end_date, 
       week, 
       'All'::varchar as zip_code_of_center,
       'All'::varchar as center,
       age_group,
       case 
          when sum(ili_counts) is not null then sum(ili_counts)
          else 0
       end as number_of_ILI_visits,
       sum(tot_counts) as Total_number_of_visits,
       round(((case 
          when sum(ili_counts) is not null then sum(ili_counts)
          else 0
       end)/sum(tot_counts))*100,2) as Percent_of_visits_for_ILI
from esp_mdphnet.ili_summary
--last full week of data
where period_end=date_trunc('week',current_date - interval '7 days') + interval '5 days'
group by period_end::date, week, age_group
order by case (age_group) 
                when '0-4' then 1
                when '5-24' then 2
                when '25-49' then 3
                when '50-64' then 4
                when '65+' then 5
         end) sumtab
union
Select * from (
select period_end::date as week_end_date, 
       week, 
       zip5 as zip_code_of_center,
       center,
       age_group,
       case 
          when ili_counts is not null then ili_counts
          else 0
       end as number_of_ILI_visits,
       tot_counts as Total_number_of_visits,
       round(((case 
          when ili_counts is not null then ili_counts
          else 0
       end)/tot_counts)*100,2) as Percent_of_visits_for_ILI
from esp_mdphnet.ili_summary
--last full week of data
where period_end=date_trunc('week',current_date - interval '7 days') + interval '5 days'
) deetstab ) unioned
order by case (center)
                when 'All' then '0'
                else center
         end,
         case (age_group) 
                when '0-4' then 1
                when '5-24' then 2
                when '25-49' then 3
                when '50-64' then 4
                when '65+' then 5
         end;
