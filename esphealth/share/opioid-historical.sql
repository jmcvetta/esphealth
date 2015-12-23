-- Analysis script generated on Wednesday, 08 Jul 2015 13:34:16 EDT
-- Analysis name: opioidrx
-- Analysis description: opioidrx
-- Script generated for database: POSTGRESQL

--
-- Script setup section 
--

BEGIN;

DROP TABLE IF EXISTS public.opi_a_100007_s_6 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_7 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_8 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_9 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_10 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_11 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_12 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_13 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_14 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_15 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_16 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_18 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_19 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_20 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_21 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_22 CASCADE;
DROP TABLE IF EXISTS public.opi_a_100007_s_23 CASCADE;
DROP TABLE IF EXISTS public.highopi_temp_1;
DROP TABLE IF EXISTS public.highopi_temp_2;
DROP TABLE IF EXISTS public.highopi_temp_3;
DROP TABLE IF EXISTS public.highopi_temp_4;
DROP TABLE IF EXISTS public.highopi_temp_5;
DROP TABLE IF EXISTS public.highopi_temp_6;


DROP TABLE IF EXISTS ccda_opibenzo CASCADE;

--
-- Script body 
--

--Steps 1-5: Part of initial access for script build and not required in production.

-- Step 6: Join - BASE Prescription Records for the Last Year -- Join the prescription table on the patient table. Limit by records with a start_date within the last year and have a valid status
CREATE TABLE public.opi_a_100007_s_6  AS SELECT T1.patient_id,T1.name,T2.date_of_birth,T2.cdate_of_birth,T1.start_date,T2.natural_key,T1.end_date,T1.quantity_float,T1.quantity,T1.quantity_type,CASE WHEN refills~E'^\\d+$' THEN refills::real ELSE 0 END  refills, T1.natural_key rx_natural_key FROM public.emr_prescription T1 INNER JOIN public.emr_patient T2 ON ((T1.patient_id = T2.id))
WHERE (start_date >= '2004-01-01' and start_date < '2005-01-01')  
and (T1.patient_class is null or T1.patient_class = '1');

-- Step 7: Join - BASE Join (limit) on drugs in the drug_lookup table
CREATE TABLE public.opi_a_100007_s_7  AS SELECT T1.patient_id,T2.name,T2.type,T1.date_of_birth,T1.start_date,T1.natural_key,T1.end_date,T1.quantity_float,T1.quantity,T1.quantity_type,T2.conversion_factor,T2.dosage_strength,T1.refills, T1.rx_natural_key FROM public.opi_a_100007_s_6 T1 INNER JOIN public.static_rx_lookup T2 ON ((T1.name = T2.name)) ;

-- Step 8: Join - BenzOpiConcurrent Find patients who have a prescription for BOTH an opioid and a benzo within 30 days of each other
CREATE TABLE public.opi_a_100007_s_8  AS SELECT T1.patient_id,T1.type,T1.natural_key,CASE WHEN (T1.start_date < TSELF.start_date) THEN T1.start_date ELSE TSELF.start_date END disease_date,T1.date_of_birth FROM public.opi_a_100007_s_7 T1 INNER JOIN public.opi_a_100007_s_7 TSELF ON ((T1.patient_id = TSELF.patient_id))  WHERE (T1.type =1 and TSELF.type = 2) and ((T1.start_date - TSELF.start_date) BETWEEN -30 and 30);

-- Step 9: SQL - BenzOpiConcurrent - Just select the earliest matching prescription
CREATE TABLE public.opi_a_100007_s_9  AS SELECT patient_id,  type, natural_key, date_of_birth, MIN(disease_date) as disease_date FROM public.opi_a_100007_s_8 GROUP BY patient_id, type, natural_key, date_of_birth;

-- Step 10: Derive Columns - BenzOpiConcurrent - Assign Condition Name, Criteria, Status, Notes, & Start Date in mdphnet format
CREATE TABLE public.opi_a_100007_s_10  AS SELECT T1.*,text('benzopiconcurrent') local_condition,text('a prescription for a benzodiazepine within 30 days before or after a prescription for an opioid within the past year') local_criteria,disease_date  - ('1960-01-01'::date) start_date_mdphnet FROM public.opi_a_100007_s_9 T1;

-- Step 11: SQL - OpioidRx, BenzodiaenzoRx - Query for only the record with the earliest date for the first prescription (disease_date) 
CREATE TABLE public.opi_a_100007_s_11  AS SELECT patient_id,  type, natural_key, date_of_birth, MIN(start_date) AS "disease_date" FROM public.opi_a_100007_s_7 GROUP BY patient_id, type, natural_key, date_of_birth;

-- Step 12: Filter - OpioidRx, BenzodiaRx - Prescription for Opioid or Benzo 
CREATE TABLE public.opi_a_100007_s_12 AS SELECT * FROM public.opi_a_100007_s_11 WHERE type in (1,2);

-- Step 13: Derive Columns - OpioidRx, BenzodiaRx - Assign Condition Name, Criteria, Status, Notes, & Start Date in mdphnet format
CREATE TABLE public.opi_a_100007_s_13  AS SELECT T1.*,CASE when  (type) = 1  THEN  text('opioidrx')
when (type) = 2  THEN  text('benzodiarx')
END local_condition,CASE when  (type) = 1  THEN  text('>= 1 prescription for opioid within the last year')
when (type) = 2  THEN  text('>= 1 prescription for benzodiazepine within the last year')
END local_criteria,disease_date  - ('1960-01-01'::date)  start_date_mdphnet FROM public.opi_a_100007_s_12 T1;

-- Step 14: Filter - HighOpioidDose - Just get the opioid prescriptions with valid quantity_types 
CREATE TABLE public.opi_a_100007_s_14  AS SELECT * FROM public.opi_a_100007_s_7 WHERE  type = 1 and (quantity_type similar to '%(cc|cap|count|each|film|lozenge|ml|patch|pill|strip|suppos|tab|unit)%' or quantity_type is null or quantity_type = '') and dosage_strength is not null and quantity_float > 0;


-- Step 15: Derive Columns - HighOpioidUse - Compute script_days & proper refill amount (1 refill means 2 prescriptions)
CREATE TABLE public.opi_a_100007_s_15  AS SELECT T1.*,CASE when (cast(refills as real) = 0) then 1 else (cast(refills as real) + 1) end mod_refills,CASE when ((end_date - start_date) > 0) then (end_date - start_date) else 30 end script_days FROM public.opi_a_100007_s_14 T1;

-- Step 16: Derive Columns - HighOpioidUse - Compute morphine equiv per day
CREATE TABLE public.opi_a_100007_s_16  AS SELECT T1.*,(((quantity_float*dosage_strength)*conversion_factor)*mod_refills) /  script_days  morphine_equiv FROM public.opi_a_100007_s_15 T1;

-- Step 17: Aggregate - HighOpioidUse - Patients prescribed ≥100 milligrams of morphine equivalents per day for ≥90 days within the past year
CREATE TABLE public.highopi_temp_1 AS SELECT patient_id, name, date_of_birth, natural_key, rx_natural_key, start_date, end_date, morphine_equiv FROM  public.opi_a_100007_s_16 where 1=2; --stub table for subsequent inserts

do 
$$
  declare
    currow record;
    patid integer;
    enddt date;
    insrtprfx text;
  begin
    insrtprfx:='INSERT INTO public.highopi_temp_1 (patient_id, name, date_of_birth, natural_key, rx_natural_key, start_date, end_date, morphine_equiv) values (';
    for patid in SELECT DISTINCT patient_id FROM public.opi_a_100007_s_16 
   loop
      enddt:=null; --set this values to null for each new patid
      for currow in execute 'SELECT patient_id, name, natural_key, date_of_birth, rx_natural_key, start_date, start_date + script_days as end_date, morphine_equiv, '
                            || ' lead(start_date,1) over (partition by patient_id order by start_date, start_date + script_days, rx_natural_key) as next_start '
                             || ' FROM public.opi_a_100007_s_16 WHERE patient_id = ' || trim(to_char(patid, '9999999999')) || ' and type=1 and morphine_equiv is not null order by start_date, start_date + script_days, rx_natural_key'
     loop
       if currow.morphine_equiv>=100 or currow.end_date >= currow.next_start or currow.start_date <= enddt then
          execute insrtprfx || to_char(patid, '9999999999') || ',
          ''' || currow.name ||''',
          ''' || COALESCE(quote_literal(currow.date_of_birth),'1900-01-01')::date ||''' ,
          ''' || currow.natural_key || ''',
          ''' || currow.rx_natural_key || ''',
          ''' || to_char(currow.start_date,'yyyy-mm-dd') || '''::date,
          ''' || to_char(currow.end_date,'yyyy-mm-dd') || '''::date,
          ' || to_char(currow.morphine_equiv, '99999.999') || ')';   
        end if;
        enddt := greatest(currow.end_date, coalesce(enddt,'1900-01-01'::date));
      end loop;
    end loop;
  end;
$$ language plpgsql;

CREATE TABLE public.highopi_temp_2 AS
SELECT generate_series(min(start_date)::date,max(end_date)::date,interval '1 day')::date as dates
FROM public.highopi_temp_1;

CREATE TABLE public.highopi_temp_3 AS
SELECT t0.*, t1.dates
FROM public.highopi_temp_1 t0 JOIN public.highopi_temp_2 t1 ON t1.dates between t0.start_date and t0.end_date;

CREATE TABLE public.highopi_temp_4 AS
SELECT patient_id, date_of_birth, natural_key, dates, array_agg(rx_natural_key order by rx_natural_key) as keys, sum(morphine_equiv) as morphine_tots
FROM public.highopi_temp_3
GROUP BY patient_id, date_of_birth, natural_key, dates
HAVING SUM(morphine_equiv) >= 100;

CREATE TABLE public.highopi_temp_5 AS
SELECT patient_id, date_of_birth, natural_key, keys, min(dates) as start_date, max(dates) as end_date, avg(morphine_tots) as morphine_tots
FROM public.highopi_temp_4
GROUP BY patient_id, date_of_birth, natural_key, keys;

CREATE TABLE public.highopi_temp_6 as
SELECT patient_id, sum(end_date-start_date) days
FROM public.highopi_temp_5 
GROUP BY patient_id
HAVING SUM (end_date-start_date) >=90;

-- Step 18: Derive Columns - HighOpioidDose - Assign Condition Name, Criteria, & Start Date in mdphnet format
CREATE TABLE public.opi_a_100007_s_18 AS
SELECT T1.patient_id,
min(start_date) as disease_date,
T2.date_of_birth,
T2.natural_key,
text('prescribed >= 100 milligrams of morphine equivalents per day for >= 90 days within the past year') criteria,
text('highopioiduse') local_condition,
min(start_date) - ('1960-01-01'::date)  start_date_mdphnet
FROM public.highopi_temp_6 T1 INNER JOIN public.highopi_temp_5 T2 ON ((T1.patient_id = T2.patient_id)) 
group by T1.patient_id, T2.date_of_birth, T2.natural_key
order by T1.patient_id;

-- Step 19: Union - UNION the results together and exclude duplicates
CREATE TABLE public.opi_a_100007_s_19  AS (SELECT patient_id,natural_key,date_of_birth,disease_date,local_condition,local_criteria,start_date_mdphnet FROM public.opi_a_100007_s_10) UNION (SELECT patient_id,natural_key,date_of_birth,disease_date,local_condition,local_criteria,start_date_mdphnet FROM public.opi_a_100007_s_13) UNION (SELECT patient_id,natural_key,date_of_birth,disease_date,local_condition,criteria,start_date_mdphnet FROM public.opi_a_100007_s_18);

-- Step 20: Join - STANDARD - Find patients who don't already have this condition starting on this date.
CREATE TABLE public.opi_a_100007_s_20  AS SELECT T1.patient_id,T1.natural_key,T1.disease_date,T1.date_of_birth,T1.start_date_mdphnet,T1.local_condition,T1.local_criteria FROM public.opi_a_100007_s_19 T1 LEFT OUTER JOIN public.esp_condition T2 ON ((T1.natural_key = T2.patid) AND (T1.start_date_mdphnet = T2.date) AND (T1.local_condition = T2.condition))  WHERE (T2.patid is null) ;

-- Step 21: Derive Columns - STANDARD - local_notes, local_status, age_at_detect_year, centerid
CREATE TABLE public.opi_a_100007_s_21  AS SELECT T1.*,
case when date_of_birth = '1900-01-01' then null else date_part('year', disease_date) - date_part('year', date_of_birth) end age_at_detect_year,
'1'::varchar(1) centerid,text('') local_notes,text('NO') local_status 
FROM public.opi_a_100007_s_20 T1;

-- Step 22: Derive Columns - STANDRD - age_group_10yr, age_group_5yr, age_group_ms
CREATE TABLE public.opi_a_100007_s_22  AS SELECT T1.*,CASE when (age_at_detect_year <= 9) then '0-9'
when (age_at_detect_year <=19) then '10-19' 
when (age_at_detect_year <=29) then '20-29' 
when (age_at_detect_year <=39) then '30-39' 
when (age_at_detect_year <=49) then '40-49' 
when (age_at_detect_year <=59) then '50-59' 
when (age_at_detect_year <=69) then '60-69' 
when (age_at_detect_year <=79) then '70-79' 
when (age_at_detect_year <=89) then '80-89' 
when (age_at_detect_year <=99) then '90-99' 
else
'100+'
end age_group_10yr,CASE when  (age_at_detect_year) <= 4  THEN  '0-4'
when age_at_detect_year <= 9  THEN '5-9'
when age_at_detect_year <= 14 THEN '10-14'
when age_at_detect_year <= 19 THEN '15-19'
when age_at_detect_year <= 24 THEN '20-24'
when age_at_detect_year <= 29 THEN '25-29'
when age_at_detect_year <= 34 THEN '30-34'
when age_at_detect_year <= 39 THEN '35-39'
when age_at_detect_year <= 44 THEN '40-44'
when age_at_detect_year <= 49 THEN '45-49'
when age_at_detect_year <= 54 THEN '50-54'
when age_at_detect_year <= 59 THEN '55-59'
when age_at_detect_year <= 64 THEN '60-64'
when age_at_detect_year <= 69 THEN '65-69'
when age_at_detect_year <= 74 THEN '70-74'
when age_at_detect_year <= 79 THEN '75-79'
when age_at_detect_year <= 84 THEN '80-84'
when age_at_detect_year <= 89 THEN '85-89'
when age_at_detect_year <= 94 THEN '90-94'
when age_at_detect_year <= 99 THEN '95-99'
ELSE
'100+'
END age_group_5yr,CASE when age_at_detect_year <= 1  THEN '0-1'
when age_at_detect_year <= 4 THEN '2-4'
when age_at_detect_year <= 9 THEN '5-9'
when age_at_detect_year <= 14 THEN '10-14'
when age_at_detect_year <= 18 THEN '15-18'
when age_at_detect_year <= 21 THEN '19-21'
when age_at_detect_year <= 44 THEN '22-44'
when age_at_detect_year <= 64 THEN '45-64'
when age_at_detect_year <= 74 THEN '65-74'
ELSE
'75+'
END  age_group_ms FROM public.opi_a_100007_s_21 T1;

-- Step 23: Subset Columns - STANDARD - Prepare Output
CREATE TABLE public.opi_a_100007_s_23  AS SELECT "centerid","natural_key","local_condition","start_date_mdphnet","age_at_detect_year","age_group_5yr","age_group_10yr","age_group_ms","local_criteria","local_status","local_notes" FROM public.opi_a_100007_s_22;

-- Step 24: Save - STANARD-- Populate ccda_opibenzo table
CREATE TABLE ccda_opibenzo  AS SELECT * FROM public.opi_a_100007_s_23;

-- Populate the ESP Condition Table
INSERT INTO esp_condition (SELECT * from ccda_opibenzo);

--
-- Script shutdown section 
--
--DROP TABLE IF EXISTS public.opi_a_100007_s_6 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_7 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_8 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_9 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_10 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_11 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_12 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_13 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_14 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_15 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_16 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_18 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_19 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_20 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_21 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_22 CASCADE;
--DROP TABLE IF EXISTS public.opi_a_100007_s_23 CASCADE;
--DROP TABLE IF EXISTS public.highopi_temp_1;
--DROP TABLE IF EXISTS public.highopi_temp_2;
--DROP TABLE IF EXISTS public.highopi_temp_3;
--DROP TABLE IF EXISTS public.highopi_temp_4;
--DROP TABLE IF EXISTS public.highopi_temp_5;
--DROP TABLE IF EXISTS public.highopi_temp_6;


COMMIT;


