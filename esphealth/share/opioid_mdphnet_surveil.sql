-- Analysis script generated on Tuesday, 01 Sep 2015 14:24:33 EDT
-- Analysis name: Opioid MDPHnet Surveillance 
-- Analysis description: Opioid MDPHnet Surveillance 
-- Script generated for database: POSTGRESQL

BEGIN;

--
-- Script setup section 
--
DROP TABLE IF EXISTS public.opisurv_a_100009_s_7 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_7 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_8 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_8 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_9 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_9 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_10 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_10 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_11 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_11 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_12 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_12 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_13 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_13 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_14 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_14 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_15 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_15 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_16 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_16 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_17 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_17 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_18 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_18 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_19 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_19 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_20 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_20 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_21 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_21 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_22 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_22 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_23 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_23 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_24 CASCADE;
DROP VIEW IF EXISTS public.opisurv_a_100009_s_24 CASCADE;

DROP TABLE IF EXISTS opioid_mdphnet_surveillance CASCADE;
DROP VIEW IF EXISTS opioid_mdphnet_surveillance CASCADE;

--
-- Script body 
--



-- Step 7: SQL - RESULT COLUMN A Count the number of distinct patients with ≥1 encounters within the past 1 year (from mdphnet)
CREATE TABLE public.opisurv_a_100009_s_7  AS select count(distinct(patid)) as enc_count from esp_mdphnet.esp_encounter where (a_date  + ('1960-01-01'::date))  >=(date ( current_date) -integer '365');

-- Step 8: Join - Prescription Records for the Last Year -- Join the prescription table on the patient table. Limit by records with a start_date within the last year and valid prescription status
CREATE TABLE public.opisurv_a_100009_s_8  AS SELECT T1.id,T2.name,T1.natural_key,T2.quantity_type,T2.start_date,T2.end_date,T2.quantity,T2.quantity_float,CASE WHEN refills~E'^\\d+$' THEN refills::real ELSE 0 END  refills FROM public.emr_patient T1 INNER JOIN public.emr_prescription T2 ON ((T1.id = T2.patient_id))  WHERE (start_date >= date ( current_date) -integer '365');

-- Step 9: Join - BASE Join (limit) on drugs in the drug_lookup table
CREATE TABLE public.opisurv_a_100009_s_9  AS SELECT T1.natural_key,T1.id,T1.name,T2.conversion_factor,T2.dosage_strength,T2.type,T1.quantity_type,T1.start_date,T1.end_date,T1.quantity,T1.quantity_float,T1.refills,T1.id id_1 FROM public.opisurv_a_100009_s_8 T1 INNER JOIN public.static_rx_lookup T2 ON ((T1.name = T2.name)) ;

-- Step 10: SQL - Select condition and count of highopioiduse, opioidrx, benzopiconcurrent, and benzodiarx conditions within the last year.
CREATE TABLE public.opisurv_a_100009_s_10  AS select condition, count(*) from public.esp_condition where condition in ('highopioiduse', 'opioidrx', 'benzopiconcurrent', 'benzodiarx') and (date  + ('1960-01-01'::date))  >=(date ( current_date) -integer '365') group by condition;

-- Step 11: Query - Compute the count of prescriptions per patient by type
CREATE TABLE public.opisurv_a_100009_s_11  AS SELECT count(natural_key) count_per_patient,T1.natural_key,T1.type FROM  public.opisurv_a_100009_s_9 T1   GROUP BY T1.natural_key,T1.type;

-- Step 12: Aggregate - Average number of prescriptions per patient by type
CREATE TABLE public.opisurv_a_100009_s_12  AS SELECT T1.type,avg( count_per_patient ) avg_number_per_patient FROM  public.opisurv_a_100009_s_11 T1   GROUP BY T1.type;

-- Step 13: Derive Columns - Compute Script Days & Proper Refills (1 refill means 2 prescriptions)
CREATE TABLE public.opisurv_a_100009_s_13  AS SELECT T1.*,CASE when (cast(refills as real) = 0) then 1 else (cast(refills as real) + 1) end mod_refills,CASE when ((end_date - start_date) > 0) then (end_date - start_date) else 30 end script_days FROM public.opisurv_a_100009_s_9 T1;

-- Step 14: Aggregate - Compute Total Script Days for Each Patient By Type
CREATE TABLE public.opisurv_a_100009_s_14  AS SELECT T1.natural_key,T1.type,sum(script_days) total_script_days FROM  public.opisurv_a_100009_s_13 T1   GROUP BY T1.type,T1.natural_key;

-- Step 15: Aggregate - Compute the Mean / standard deviation for duration of prescription per patient
CREATE TABLE public.opisurv_a_100009_s_15  AS SELECT T1.type,avg(total_script_days)  avg_script_days,stddev_pop(total_script_days)  std_dev_script_days FROM  public.opisurv_a_100009_s_14 T1   GROUP BY T1.type;

-- Step 16: Filter - FILTERED RX: For morphine or loraz equiv checks, prescriptions must have a quantity and be of the right type.
CREATE TABLE public.opisurv_a_100009_s_16  AS SELECT * FROM public.opisurv_a_100009_s_13 WHERE (quantity_type similar to '%(cc|cap|count|each|film|lozenge|ml|patch|pill|strip|suppos|tab|unit)%' or quantity_type is null or quantity_type = '') and dosage_strength is not null and quantity_float > 0;

-- Step 17: Derive Columns - FILTERED RX: Compute drug equivalents per day for each prescription
CREATE TABLE public.opisurv_a_100009_s_17  AS SELECT T1.*,(((quantity_float*dosage_strength)*conversion_factor)*mod_refills) /  script_days  drug_equiv FROM public.opisurv_a_100009_s_16 T1;

-- Step 18: Aggregate - FILTERED RX: Compute total drug_equiv per day and total script_days per patient
CREATE TABLE public.opisurv_a_100009_s_18  AS SELECT sum(script_days) total_script_days,T1.natural_key,sum(drug_equiv) total_drug_equiv,T1.type FROM  public.opisurv_a_100009_s_17 T1   GROUP BY T1.natural_key,T1.type;

-- Step 19: Aggregate - FILTERED RX: Compute Average number of drug equivalents per patient per day
CREATE TABLE public.opisurv_a_100009_s_19  AS SELECT T1.type,avg(total_drug_equiv) avg_drug_equiv FROM  public.opisurv_a_100009_s_18 T1   GROUP BY T1.type;

-- Step 20: SQL - Median / 25th percentile / 75th percentile duration of Opi prescription per patient 
CREATE TABLE public.opisurv_a_100009_s_20  AS select type,
    max(case when ntile = 25 then total_script_days end) as percentile_25,
    max(case when ntile = 50 then total_script_days end) as median_percentile_50,
    max(case when ntile = 75 then total_script_days end) as percentile_75,
    max(case when ntile = 100 then total_script_days end) as percentile_100
from (
    select 
        type,
        total_script_days,
        NTILE(100) over (order by total_script_days asc) as ntile
    from public.opisurv_a_100009_s_14 where type = 1
) as tmp group by type;

-- Step 21: SQL - Median / 25th percentile / 75th percentile duration of Benzo prescription per patient 
CREATE TABLE public.opisurv_a_100009_s_21  AS select type,
    max(case when ntile = 25 then total_script_days end) as percentile_25,
    max(case when ntile = 50 then total_script_days end) as median_percentile_50,
    max(case when ntile = 75 then total_script_days end) as percentile_75,
    max(case when ntile = 100 then total_script_days end) as percentile_100
from (
    select 
        type,
        total_script_days,
        NTILE(100) over (order by total_script_days asc) as ntile
    from public.opisurv_a_100009_s_14 where type = 2
) as tmp group by type;

-- Step 22: Join - Rate of patients by condition per 1000 patients

CREATE TABLE public.opisurv_a_100009_s_22  AS SELECT T1.enc_count,T2.condition,T2.count,( cast(T2.count as real) / cast(T1.enc_count as real) ) * 1000 rate_per_1000 FROM public.opisurv_a_100009_s_7 T1 LEFT OUTER JOIN public.opisurv_a_100009_s_10 T2 ON ((T1.enc_count > T2.count)) ;

-- Step 23: SQL - Build Output Master
CREATE TABLE public.opisurv_a_100009_s_23  AS SELECT (SELECT enc_count FROM public.opisurv_a_100009_s_7) AS num_of_patients_with_encounters_within_last_year,
(SELECT count FROM public.opisurv_a_100009_s_10 where condition = 'opioidrx') AS num_of_patients_with_any_opioid_rx,
(SELECT count FROM public.opisurv_a_100009_s_10 where condition = 'benzodiarx') AS num_of_patients_with_any_benzo_rx,
(SELECT count FROM public.opisurv_a_100009_s_10 where condition = 'highopioiduse') AS num_of_patients_with_high_dose_opioid,
(SELECT count FROM public.opisurv_a_100009_s_10 where condition = 'benzopiconcurrent') AS num_of_patients_with_concurrent_opioid_benzo,
(SELECT avg_number_per_patient FROM public.opisurv_a_100009_s_12 where type=1) as avg_number_of_opioid_prescriptions_pp,
(SELECT avg_number_per_patient FROM public.opisurv_a_100009_s_12 where type=2) as avg_number_of_benzo_prescriptions_pp,
(SELECT avg_drug_equiv FROM public.opisurv_a_100009_s_19 where type = 1) as avg_num_of_morphine_equivs_pp_per_day,
(SELECT avg_script_days FROM public.opisurv_a_100009_s_15 where type = 1) as opioid_avg_script_days,
(SELECT std_dev_script_days FROM public.opisurv_a_100009_s_15 where type = 1) as opioid_st_dev_script_days,
(SELECT avg_drug_equiv FROM public.opisurv_a_100009_s_19 where type = 2) as avg_num_of_loraz_equivs_pp_per_day,
(SELECT avg_script_days FROM public.opisurv_a_100009_s_15 where type = 2) as benzo_avg_script_days,
(SELECT std_dev_script_days FROM public.opisurv_a_100009_s_15 where type = 2) as benzo_st_dev_script_days,
(SELECT percentile_25 FROM public.opisurv_a_100009_s_20) as opioid_25_percentile,
(SELECT median_percentile_50 FROM public.opisurv_a_100009_s_20) as opioid_median,
(SELECT percentile_75 FROM public.opisurv_a_100009_s_20) as opioid_75_percentile,
(SELECT percentile_25 FROM public.opisurv_a_100009_s_21) as benzo_25_percentile,
(SELECT median_percentile_50 FROM public.opisurv_a_100009_s_21) as benzo_median,
(SELECT percentile_75 FROM public.opisurv_a_100009_s_21) as benzo_75_percentile,
(SELECT rate_per_1000 FROM public.opisurv_a_100009_s_22 where condition = 'opioidrx') as rate_of_patients_with_opioid_per_1000_patients,
(SELECT rate_per_1000 FROM public.opisurv_a_100009_s_22 where condition = 'benzodiarx') as rate_of_patients_with_benzo_per_1000_patients,
(SELECT rate_per_1000 FROM public.opisurv_a_100009_s_22 where condition = 'highopioiduse') as rate_of_patients_with_highopioiduse_per_1000_patients,
(SELECT rate_per_1000 FROM public.opisurv_a_100009_s_22 where condition = 'benzopiconcurrent' )as
rate_of_patients_with_concurrent_opioidbenzo_per_1000_patients;

-- Step 24: Subset Columns - Order Output
CREATE TABLE public.opisurv_a_100009_s_24  AS SELECT "num_of_patients_with_encounters_within_last_year","num_of_patients_with_any_opioid_rx","avg_number_of_opioid_prescriptions_pp","avg_num_of_morphine_equivs_pp_per_day","opioid_avg_script_days","opioid_st_dev_script_days","opioid_median","opioid_25_percentile","opioid_75_percentile","num_of_patients_with_high_dose_opioid","num_of_patients_with_any_benzo_rx","avg_number_of_benzo_prescriptions_pp","avg_num_of_loraz_equivs_pp_per_day","benzo_avg_script_days","benzo_st_dev_script_days","benzo_median","benzo_25_percentile","benzo_75_percentile","num_of_patients_with_concurrent_opioid_benzo","rate_of_patients_with_opioid_per_1000_patients","rate_of_patients_with_benzo_per_1000_patients","rate_of_patients_with_highopioiduse_per_1000_patients","rate_of_patients_with_concurrent_opioidbenzo_per_1000_patients" FROM public.opisurv_a_100009_s_23;

-- Step 25: Save - opioid_mdphnet_surveillance
CREATE TABLE opioid_mdphnet_surveillance  AS SELECT * FROM public.opisurv_a_100009_s_24;

--
-- Script shutdown section 
--

DROP TABLE IF EXISTS public.opisurv_a_100009_s_7 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_8 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_9 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_10 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_11 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_12 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_13 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_14 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_15 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_16 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_17 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_18 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_19 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_20 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_21 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_22 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_23 CASCADE;

DROP TABLE IF EXISTS public.opisurv_a_100009_s_24 CASCADE;


COMMIT;


