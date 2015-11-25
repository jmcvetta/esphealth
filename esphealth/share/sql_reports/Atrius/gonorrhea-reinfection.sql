-- Analysis script generated on Monday, 23 Nov 2015 15:44:57 EST
-- Analysis name: Gonorrhea Test of Reinfection and Treatment Report
-- Analysis description: Gonorrhea Test of Reinfection and Treatment Report
-- Script generated for database: POSTGRESQL

--
-- Script setup section 
--

DROP TABLE IF EXISTS kregonrein_a_100027_s_9 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_10 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_11 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_12 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_13 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_14 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_15 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_16 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_17 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_18 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_19 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_20 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_21 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_22 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_23 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_24 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_25 CASCADE;

--
-- Script body 
--

-- Step 9: Query - Get All the Gonorrhea Tests For The Desired Time Period We Want To Report On
CREATE TABLE kregonrein_a_100027_s_9  AS SELECT T1.patient_id,T1.date,T1.name,T1.id hef_id,T1.object_id lab_result_id,T1.provider_id,T2.specimen_source FROM public.hef_event T1 INNER JOIN public.emr_labresult T2 ON ((T1.object_id = T2.id) AND (T1.patient_id = T2.patient_id))  WHERE T1.date >= '01-01-2014'  and name in ('lx:gonorrhea:positive', 'lx:gonorrhea:negative') ;

-- Step 10: SQL - INDEX Get details on the FIRST positive test
CREATE TABLE kregonrein_a_100027_s_10  AS SELECT DISTINCT ON (T1.patient_id) T1.patient_id,T1.date as first_pos_date,T1.lab_result_id first_pos_lab_result_id,T1.hef_id first_pos_hef_id,T1.specimen_source,
T2.natural_key as provider_id,
T2.dept as provider_location 
FROM kregonrein_a_100027_s_9 T1, public.emr_provider T2
WHERE (T1.provider_id = T2.id) 
and  T1.name =  'lx:gonorrhea:positive' 
ORDER BY T1.patient_id, T1.date, T1.hef_id;

-- Step 11: Query - SECOND POSITIVE - For those with a first positive, find any with a second positive within 0-6 days
CREATE TABLE kregonrein_a_100027_s_11  AS SELECT T1.patient_id,T1.date,T1.date second_pos_date,T1.hef_id second_pos_hef_id,T1.lab_result_id second_pos_lab_id,T1.specimen_source second_pos_specimen_source FROM kregonrein_a_100027_s_9 T1 INNER JOIN kregonrein_a_100027_s_10 T2 ON ((T1.patient_id = T2.patient_id))  WHERE  T1.name =  'lx:gonorrhea:positive' and  T1.date <= ( T2.first_pos_date + interval '6 days' ) and  T1.hef_id != T2.first_pos_hef_id;

-- Step 12: Query - REPEAT TESTS - For those with a first positive, see if they have any repeat tests (any result) between 7-365 days after the first
CREATE TABLE kregonrein_a_100027_s_12  AS SELECT T1.patient_id,T1.date,T2.first_pos_date,T1.hef_id,T1.lab_result_id,T1.specimen_source,T2.provider_id,T1.name FROM kregonrein_a_100027_s_9 T1 INNER JOIN kregonrein_a_100027_s_10 T2 ON ((T1.patient_id = T2.patient_id))  WHERE T1.date >= ( T2.first_pos_date + interval '7 days' ) and T1.date <=  ( T2.first_pos_date + interval '365 days' );

-- Step 13: Query - FIRST REPEAT TEST - Get details on FIRST REPEAT test 
CREATE TABLE kregonrein_a_100027_s_13  AS SELECT DISTINCT ON (T1.patient_id) t1.patient_id,T1.date first_repeat_date,T1.hef_id first_repeat_hef_id,T1.specimen_source first_repeat_specimen_source,T1.lab_result_id first_repeat_lab_result_id,case when T1.name = 'lx:gonorrhea:positive' then 'positive'  when T1.name = 'lx:gonorrhea:negative' then 'negative' else 'indeterminate'  end first_repeat_result,1 first_repeat FROM  kregonrein_a_100027_s_12 T1 
ORDER BY T1.patient_id, T1.date, T1.hef_id ;
-- Step 14: Query - SECOND REPEAT TEST - Get details on SECOND REPEAT test 
CREATE TABLE kregonrein_a_100027_s_14  AS SELECT DISTINCT ON (T1.patient_id) t1.patient_id,T1.date second_repeat_date,T1.hef_id second_repeat_hef_id,T1.specimen_source second_repeat_specimen_source,case when T1.name = 'lx:gonorrhea:positive' then 'positive'  when T1.name = 'lx:gonorrhea:negative' then 'negative' else 'indeterminate'  end second_repeat_result,T1.lab_result_id second_repeat_lab_result_id,1 second_repeat FROM kregonrein_a_100027_s_12 T1 INNER JOIN kregonrein_a_100027_s_13 T2 ON ((T1.patient_id = T2.patient_id))  WHERE  T1.hef_id != T2.first_repeat_hef_id
ORDER BY T1.patient_id, T1.date, T1.hef_id ;

-- Step 15: SQL - HIV TEST
CREATE TABLE kregonrein_a_100027_s_15  AS SELECT distinct(indexpat.patient_id), 1 as hiv_test_14_days from kregonrein_a_100027_s_10 indexpat, public.conf_labtestmap conf, public.emr_labresult lab
where 
conf.test_name ilike '%hiv%' and 
(lab.date >= ( indexpat.first_pos_date - interval '14 days' ) and lab.date <= ( indexpat.first_pos_date + interval '14 days' ))
and indexpat.patient_id = lab.patient_id and
conf.native_code = lab.native_code
ORDER BY indexpat.patient_id;

-- Step 16: Query - KNOWN HIV CASE
CREATE TABLE kregonrein_a_100027_s_16  AS SELECT T1.patient_id,1 known_hiv_per_esp FROM kregonrein_a_100027_s_10 T1 INNER JOIN public.nodis_case T2 ON ((T1.patient_id = T2.patient_id))  WHERE  T2.condition =  'hiv' ;

-- Step 17: SQL - PREGNANCY INFO
CREATE TABLE kregonrein_a_100027_s_17  AS select distinct patient_id, start_date, 
case when end_date is not null then end_date
when end_date is null and start_date + interval '46 weeks' > now() then now() 	
else null
end as end_date
from public.hef_timespan ht
where name='pregnancy' and exists (select null from kregonrein_a_100027_s_10 indexpat where indexpat.patient_id=ht.patient_id)
and 
case when end_date is not null then end_date 
when end_date is null and start_date + interval '46 weeks' > now() then now()
else null  end is not null;

-- Step 18: Query - KNOWN PREGNANT - Patient known to be pregnant within 14 days of the index test
CREATE TABLE kregonrein_a_100027_s_18  AS SELECT T1.patient_id,1 known_pregnant_14days FROM kregonrein_a_100027_s_10 T1 INNER JOIN kregonrein_a_100027_s_17 T2 ON ((T1.patient_id = T2.patient_id))  WHERE  T1.first_pos_date + interval '14 days' between T2.start_date and T2.end_date + interval '14 days';

-- Step 19: Query - TREATMENT INDEX CASE - Get all medications prescribed for the INDEX patients within 30 days of index date


CREATE TABLE kregonrein_a_100027_s_19  AS SELECT T1.patient_id,T1.name,T1.date,T1.directions,T2.first_pos_date FROM public.emr_prescription T1 INNER JOIN kregonrein_a_100027_s_10 T2 ON ((T1.patient_id = T2.patient_id))  WHERE (T1.date >= T2.first_pos_date ) and T1.date <= ( T2.first_pos_date + interval '30 days') 
;

-- Step 20: SQL - INDEX OTHER RX 
CREATE TABLE kregonrein_a_100027_s_20  AS select patient_id, array_agg(name) as other_meds FROM (SELECT name, patient_id FROM kregonrein_a_100027_s_19
where name not ilike '%Ceftriaxone%' and name not ilike '%Azithromycin%' and name not ilike '%Cefixime%' 
and name not ilike '%Ceftizoxime%' and name not ilike '%Cefoxitin%' and name not ilike '%Cefotaxim%' 
and name not ilike '%Doxycycline%' and name not ilike '%Gentamicin%' and name not ilike '%Gemifloxacin%'
and name not ilike '%Levofloxacin%' and name not ilike '%Ciprofloxacin%' and name not ilike '%Spectinomycin%'
order by name asc
) as all_meds group by patient_id;

-- Step 21: Query - INDEX TREATMENT VARIABLES FOR INDEX CASE
CREATE TABLE kregonrein_a_100027_s_21  AS SELECT T1.patient_id,max(case when name ilike '%ceftriaxone%' then 1 else 0 end) ceftriaxone_given,max(case when name ilike '%ceftriaxone%' then name else null end) ceftriaxone_dose,max(case when name ilike '%ceftriaxone%'  then date else null end) ceftriaxone_date,max(case when name ilike '%azithromycin%' then 1 else 0 end) azithromycin_given,max(case when name ilike '%azithromycin%' then name else null end) azithromycin_dose,max(case when name ilike '%azithromycin%' then date else null end) azithromycin_date,max(case when name ilike '%cefixime%' then 1 else 0 end) cefixime_given,max(case when name ilike '%cefixime%' then name else null end) cefixime_dose,max(case when name ilike '%cefixime%' then date else null end) cefixime_date,max(case when name ilike '%ceftizoxime%' then 1 else 0 end) ceftizoxime_given,max(case when name ilike '%ceftizoxime%' then name else null end) ceftizoxime_dose,max(case when name ilike '%ceftizoxime%' then date else null end) ceftizoxime_date,max(case when name ilike '%cefoxitin%' then 1 else 0 end) cefoxitin_given,max(case when name ilike '%cefoxitin%' then name else null end) cefoxitin_dose,max(case when name ilike '%cefoxitin%' then date else null end) cefoxitin_date,max(case when name ilike '%levofloxacin%' then 1 else 0 end) levofloxacin_given,max(case when name ilike '%levofloxacin%' then name else null end) levofloxacin_dose,max(case when name ilike '%levofloxacin%' then date else null end) levofoxacin_date,max(case when name ilike '%cefotaxim%' then 1 else 0 end) cefotaxim_given,max(case when name ilike '%cefotaxim%' then name else null end) cefotaxim_dose,max(case when name ilike '%cefotaxim%' then date else null end) cefotaxim_date,max(case when name ilike '%doxycycline%' then 1 else 0 end) doxycycline_given,max(case when name ilike '%doxycycline%' then name else null end) doxycycline_dose,max(case when name ilike '%doxycycline%' then date else null end) doxycycline_date,max(case when name ilike '%gentamicin%' then 1 else 0 end) gentamicin_given,max(case when name ilike '%gentamicin%' then name else null end) gentamicin_dose,max(case when name ilike '%gentamicin%' then date else null end) gentamicin_date,max(case when name ilike '%gemifloxacin%' then 1 else 0 end) gemifloxacin_given,max(case when name ilike '%gemifloxacin%' then name else null end) gemifloxacin_dose,max(case when name ilike '%gemifloxacin%' then date else null end) gemifloxacin_date, max(case when name ilike '%cemifloxacin%' then 1 else 0 end) cemifloxacin_given,max(case when name ilike '%cemifloxacin%' then name else null end) cemifloxacin_dose,max(case when name ilike '%cemifloxacin%' then date else null end) cemifloxacin_date,max(case when name ilike '%ciprofloxacin%' then 1 else 0 end) ciprofloxacin_given,max(case when name ilike '%ciprofloxacin%' then name else null end) ciprofloxacin_dose,max(case when name ilike '%ciprofloxacin%' then date else null end) ciprofloxacin_date,max(case when name ilike '%spectinomycin%' then 1 else 0 end) spectinomycin_given,max(case when name ilike '%spectinomycin%' then name else null end) spectinomycin_dose,max(case when name ilike '%spectinomycin%' then date else null end) spectinomycin_date FROM  kregonrein_a_100027_s_19 T1   GROUP BY T1.patient_id;

-- Step 22: SQL - FIRST REPEAT TREATMENT 
CREATE TABLE kregonrein_a_100027_s_22  AS select patient_id, array_agg(name) as first_repeat_treatment FROM (SELECT rx.name, fr.patient_id FROM public.emr_prescription rx, kregonrein_a_100027_s_13 fr
where (name ilike '%Ceftriaxone%' or name ilike '%Azithromycin%' or name ilike '%Cefixime%' 
or name ilike '%Ceftizoxime%' or name ilike '%Cefoxitin%' or name ilike '%Cefotaxim%' 
or name ilike '%Doxycycline%' or name ilike '%Gentamicin%' or name ilike '%Gemifloxacin%'
or name ilike '%Levofloxacin%' or name ilike '%Ciprofloxacin%' or name ilike '%Spectinomycin%') and ((rx.date >= fr.first_repeat_date ) and rx.date <= ( fr.first_repeat_date + interval '30 days'))
and fr.patient_id = rx.patient_id
) as all_meds
group by patient_id;

-- Step 23: SQL - SECOND REPEAT TREATMENT 
CREATE TABLE kregonrein_a_100027_s_23  AS select patient_id, array_agg(name) as second_repeat_treatment FROM (SELECT rx.name, fr.patient_id FROM public.emr_prescription rx, kregonrein_a_100027_s_14 fr
where (name ilike '%Ceftriaxone%' or name ilike '%Azithromycin%' or name ilike '%Cefixime%' 
or name ilike '%Ceftizoxime%' or name ilike '%Cefoxitin%' or name ilike '%Cefotaxim%' 
or name ilike '%Doxycycline%' or name ilike '%Gentamicin%' or name ilike '%Gemifloxacin%'
or name ilike '%Levofloxacin%' or name ilike '%Ciprofloxacin%' or name ilike '%Spectinomycin%') and ((rx.date >= fr.second_repeat_date ) and rx.date <= ( fr.second_repeat_date + interval '30 days'))
and fr.patient_id = rx.patient_id
) as all_meds
group by patient_id;

-- Step 24: SQL - FULL OUTER JOIN OF DATA ELEMENTS TOGETHER
CREATE TABLE kregonrein_a_100027_s_24  AS SELECT 
coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id, p.patient_id, it.patient_id, o.patient_id, frt.patient_id, srt.patient_id) patient_id,
coalesce(p.known_pregnant_14days, 0) as known_pregnant_14days,
coalesce(h.known_hiv_per_esp, 0) as known_hiv_per_esp,
coalesce(ht.hiv_test_14_days, 0) as hiv_test_14days, 
i.provider_id  as provider_id_index,
i.provider_location as provider_location,
i.first_pos_date,
i.specimen_source,
(case when (i.specimen_source != sp.second_pos_specimen_source or i.specimen_source is null) then sp.second_pos_specimen_source else null end) as second_pos_specimen_source,
coalesce(it.ceftriaxone_given, 0) as ceftriaxone_given,
coalesce(it.ceftriaxone_dose, null) as ceftriaxone_dose,
coalesce(it.ceftriaxone_date, null) as ceftriaxone_date,
coalesce(it.azithromycin_given, 0) as azithromycin_given,
coalesce(it.azithromycin_dose, null) as azithromycin_dose,
coalesce(it.azithromycin_date, null) as azithromycin_date,
coalesce(it.cefixime_given, 0) as cefixime_given,
coalesce(it.cefixime_dose, null) as cefixime_dose,
coalesce(it.cefixime_date, null) as cefixime_date,
coalesce(it.ceftizoxime_given, 0) as ceftizoxime_given,
coalesce(it.ceftizoxime_dose, null) as ceftizoxime_dose,
coalesce(it.ceftizoxime_date, null) as ceftizoxime_date,
coalesce(it. cefoxitin_given, 0) as  cefoxitin_given,
coalesce(it.cefoxitin_dose, null) as cefoxitin_dose,
coalesce(it.cefoxitin_date, null) as cefoxitin_date,
coalesce(it.levofloxacin_given, 0) as levofloxacin_given,
coalesce(it.levofloxacin_dose, null) as levofloxacin_dose,
coalesce(it.levofoxacin_date, null) as levofoxacin_date,
coalesce(it.cefotaxim_given, 0) as cefotaxim_given,
coalesce(it.cefotaxim_dose, null) as cefotaxim_dose,
coalesce(it.cefotaxim_date, null) as cefotaxim_date,
coalesce(it.doxycycline_given, 0) as doxycycline_given,
coalesce(it.doxycycline_dose, null) as doxycycline_dose,
coalesce(it.doxycycline_date, null) as doxycycline_date,
coalesce(it.gentamicin_given, 0) as gentamicin_given,
coalesce(it.gentamicin_dose, null) as gentamicin_dose,
coalesce(it.gentamicin_date, null) as gentamicin_date,
coalesce(it.gemifloxacin_given, 0) as gemifloxacin_given,
coalesce(it.gemifloxacin_dose, null) as gemifloxacin_dose,
coalesce(it.gemifloxacin_date, null) as gemifloxacin_date,
coalesce(it.cemifloxacin_given, 0) as cemifloxacin_given,
coalesce(it.cemifloxacin_dose, null) as cemifloxacin_dose,
coalesce(it.cemifloxacin_date, null) as cemifloxacin_date,
coalesce(it.ciprofloxacin_given, 0) as ciprofloxacin_given,
coalesce(it.ciprofloxacin_dose, null) as ciprofloxacin_dose,
coalesce(it.ciprofloxacin_date, null) as ciprofloxacin_date,
coalesce(it.spectinomycin_given, 0) as spectinomycin_given,
coalesce(it.spectinomycin_dose, null) as spectinomycin_dose,
coalesce(it.spectinomycin_date, null) as spectinomycin_date,
coalesce(o.other_meds, null) as other_rx,
case when (it.ceftriaxone_given = 1 and it.azithromycin_given = 1) then 1 else 0 end as appropriate_treatment,
coalesce(fr.first_repeat, 0) as first_repeat,
coalesce(fr.first_repeat_date, null) as first_repeat_date,
coalesce(fr.first_repeat_specimen_source, null) as first_repeat_specimen_source,
coalesce(fr.first_repeat_result, null) as first_repeat_result,
coalesce(frt.first_repeat_treatment, null) as first_repeat_treatment,
coalesce(sr.second_repeat, 0) as second_repeat,
coalesce(sr.second_repeat_date, null) as second_repeat_date,
coalesce(sr.second_repeat_specimen_source, null) as second_repeat_specimen_source,
coalesce(sr.second_repeat_result, null) as second_repeat_specimen_result,
coalesce(srt.second_repeat_treatment, null) as second_repeat_treatment

FROM kregonrein_a_100027_s_10 i
FULL OUTER JOIN kregonrein_a_100027_s_11 sp
    ON i.patient_id=sp.patient_id
FULL OUTER JOIN kregonrein_a_100027_s_13 fr
    ON fr.patient_id = coalesce(i.patient_id, sp.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_14 sr
    ON sr.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_18 p
    ON p.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_16 h
    ON h.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id, p.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_15 ht
    ON ht.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id, p.patient_id, h.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_21 it
    ON it.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id, p.patient_id, h.patient_id, ht.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_20 o
    ON o.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id, p.patient_id, h.patient_id, ht.patient_id, it.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_22 frt
    ON frt.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id, p.patient_id, h.patient_id, ht.patient_id, it.patient_id, o.patient_id)
FULL OUTER JOIN kregonrein_a_100027_s_23 srt
    ON srt.patient_id = coalesce(i.patient_id, sp.patient_id, fr.patient_id, sr.patient_id, p.patient_id, h.patient_id, ht.patient_id, it.patient_id, o.patient_id, frt.patient_id);;

-- Step 25: Query - JOIN TO PATIENT TABLE
CREATE TABLE kregonrein_a_100027_s_25  AS SELECT 
T1.id esp_patient_id,T1.mrn,date_part('year', age(T2.first_pos_date, T1.date_of_birth )) age,T1.gender,T1.race,T2.known_pregnant_14days,T2.known_hiv_per_esp,T2.hiv_test_14days,T2.provider_id_index,T2.provider_location, T2.first_pos_date,T2.specimen_source,T2.second_pos_specimen_source,T2.ceftriaxone_given,T2.ceftriaxone_dose,T2.ceftriaxone_date,T2.azithromycin_given,T2.azithromycin_dose,T2.azithromycin_date,T2.cefixime_given,T2.cefixime_dose,T2.cefixime_date,T2.ceftizoxime_given,T2.ceftizoxime_dose,T2.ceftizoxime_date,T2.cefoxitin_given,T2.cefoxitin_dose,T2.cefoxitin_date,T2.levofloxacin_given,T2.levofloxacin_dose,T2.levofoxacin_date,T2.cefotaxim_given,T2.cefotaxim_dose,T2.cefotaxim_date,T2.doxycycline_given,T2.doxycycline_dose,T2.doxycycline_date,T2.gentamicin_given,T2.gentamicin_dose,T2.gentamicin_date,T2.gemifloxacin_given,T2.gemifloxacin_dose,T2.gemifloxacin_date,T2.cemifloxacin_given,T2.cemifloxacin_dose,T2.cemifloxacin_date,T2.ciprofloxacin_given,T2.ciprofloxacin_dose,T2.ciprofloxacin_date,T2.spectinomycin_given,T2.spectinomycin_dose,T2.spectinomycin_date, T2.other_rx, T2.appropriate_treatment,T2.first_repeat,T2.first_repeat_date,T2.first_repeat_specimen_source,T2.first_repeat_result,T2.first_repeat_treatment, T2.second_repeat,T2.second_repeat_date,T2.second_repeat_specimen_source,T2.second_repeat_specimen_result, T2.second_repeat_treatment FROM public.emr_patient T1 INNER JOIN kregonrein_a_100027_s_24 T2 ON ((T1.id = T2.patient_id)) ;


\COPY (select * from kregonrein_a_100027_s_25) TO '/tmp/gonorrhea-reinfection.csv' WITH CSV HEADER

--
-- Script shutdown section 
--

DROP TABLE IF EXISTS kregonrein_a_100027_s_9 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_10 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_11 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_12 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_13 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_14 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_15 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_16 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_17 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_18 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_19 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_20 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_21 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_22 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_23 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_24 CASCADE;
DROP TABLE IF EXISTS kregonrein_a_100027_s_25 CASCADE;


