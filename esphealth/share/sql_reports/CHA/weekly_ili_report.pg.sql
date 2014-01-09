   select * from (
select * from (
select period_end::date as week_end_date,
       week,
       'All'::varchar as zip_code_of_center,
       'All'::varchar as center,
       'All'::varchar as age_group,
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
where period_end=(select max(period_end) from esp_mdphnet.ili_summary)
group by period_end::date, week
         ) alltab
union
select * from (
select groups.period_end::date as week_end_date,
       groups.week,
       groups.zip5 as zip_code_of_center,
       groups.center,
       'All'::varchar as age_group,
       case
          when sum(ili.ili_counts) is not null then sum(ili.ili_counts)
          else 0
       end as number_of_ILI_visits,
       case
          when sum(ili.tot_counts) is not null then sum(ili.tot_counts)
          else 0
       end as Total_number_of_visits,
       round(((case 
          when sum(ili.ili_counts) is not null then sum(ili.ili_counts)
          else 0
       end)::numeric/sum(ili.tot_counts)::numeric)*100,2) as Percent_of_visits_for_ILI
from esp_mdphnet.ili_summary as ili
   right join (select center, zip5, period_end, week from 
                 (select distinct center, zip5 from esp_mdphnet.ili_summary) as centers,
                 (select distinct period_end, week from esp_mdphnet.ili_summary) as dates) groups
       on ili.period_end::date=groups.period_end::date 
      and ili.center=groups.center
--last full week of data
where groups.period_end=(select max(period_end) from esp_mdphnet.ili_summary)
group by groups.period_end::date, groups.week, groups.zip5, groups.center
         ) sitesumtab
union
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
from esp_mdphnet.ili_summary,
     (select max(date) as maxdate from emr_encounter) mdate
--last full week of data
where period_end=(select max(period_end) from esp_mdphnet.ili_summary)
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
select groups.period_end::date as week_end_date, 
       groups.week, 
       groups.zip5 as zip_code_of_center,
       groups.center,
       groups.age_group,
       case 
          when ili.ili_counts is not null then ili.ili_counts
          else 0
       end as number_of_ILI_visits,
       case
          when ili.tot_counts is not null then ili.tot_counts
          else 0
       end as Total_number_of_visits,
       round(((case 
          when ili.ili_counts is not null then ili.ili_counts
          else 0
       end)::numeric/ili.tot_counts::numeric)*100,2) as Percent_of_visits_for_ILI
from esp_mdphnet.ili_summary as ili
   right join (select age_group, center, zip5, period_end, week from 
                 (select distinct age_group from esp_mdphnet.ili_summary) as age_groups,
                 (select distinct center, zip5 from esp_mdphnet.ili_summary) as centers,
                 (select distinct period_end, week from esp_mdphnet.ili_summary) as dates) groups
       on ili.age_group=groups.age_group 
      and ili.period_end::date=groups.period_end::date 
      and ili.center=groups.center
--last full week of data
where groups.period_end=(select max(period_end) from esp_mdphnet.ili_summary)
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
                when 'All' then 6
         end;
