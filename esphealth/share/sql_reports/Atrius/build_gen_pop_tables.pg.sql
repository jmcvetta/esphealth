/*--------------------------------------------------------------------------------
--
--                                ESP Health
--                         General Population Report
--
--------------------------------------------------------------------------------
--
-- @author: Bob Zambarano <bzambarano@commoninf.com>
-- @organization: Commonwealth Informatics <http://www.commoninf.com>
-- @contact: http://esphealth.org
-- @copyright: (c) 2013 Commonwealth Informatics
-- @license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
--
--------------------------------------------------------------------------------
--
-- This query contains some PostgreSQL-specific functions.  It will 
-- not run on other RDBMS without porting.
--
--------------------------------------------------------------------------------*/
drop table if exists gpr_pat;
create table gpr_pat as
SELECT 
  pat.id AS patient_id, pat.mrn, date_part('year', age(pat.date_of_birth)) as age, pat.gender, pat.race, 
  case
    when substring(pat.zip,6,1)='-' then substring(pat.zip,1,5)
    else pat.zip
  end as zip, lastenc.last_enc_date
FROM emr_patient pat
join 
   (SELECT 
	  patient_id
	, MAX(date) AS last_enc_date
	FROM emr_encounter
	GROUP BY patient_id) lastenc
on pat.id=lastenc.patient_id 
--
-- WHERE criteria 
--
WHERE pat.date_of_death IS NULL;
--
-- Max blood pressure between two and three years
--  using most recent max mean aterial pressure for the period
--
drop table if exists gpr_bp3;
create table gpr_bp3 as 
      select * from (
	SELECT 
	  t0.patient_id
	 , t0.bp_systolic AS max_bp_systolic
	, t0.bp_diastolic AS max_bp_diastolic
        , t1.max_mean_arterial as map
        , gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_systolic::numeric, 
					 'SYS'::varchar, 
					 'BPPCT'::varchar) as syspct
        , gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_diastolic::numeric, 
					 'DIA'::varchar, 
					 'BPPCT'::varchar) as diapct
        , row_number() over (partition by t0.patient_id order by t0.date desc) as rownum
	FROM emr_encounter t0,
             (select patient_id, max((2*bp_diastolic + bp_systolic)/3) as max_mean_arterial
              from emr_encounter
              WHERE date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
              group by patient_id) as t1,
             emr_patient as pat
	WHERE t0.date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
	and (2*bp_diastolic + bp_systolic)/3 = max_mean_arterial and t0.patient_id=t1.patient_id
        and t0.patient_id=pat.id) as t
        where rownum=1;
--
-- Max blood pressure between one and two years
--  using most recent max mean aterial pressure for the period
--
drop table if exists gpr_bp2;
create table gpr_bp2 as 
     select * from (
	SELECT 
	  t0.patient_id
	, t0.bp_systolic AS max_bp_systolic
	, t0.bp_diastolic AS max_bp_diastolic
        , t1.max_mean_arterial as map
        , gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_systolic::numeric, 
					 'SYS'::varchar, 
					 'BPPCT'::varchar) as syspct
        , gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_diastolic::numeric, 
					 'DIA'::varchar, 
					 'BPPCT'::varchar) as diapct
        , row_number() over (partition by t0.patient_id order by t0.date desc) as rownum
	FROM emr_encounter t0,
             (select patient_id, max((2*bp_diastolic + bp_systolic)/3) as max_mean_arterial
              from emr_encounter
              WHERE date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
              group by patient_id) as t1,
             emr_patient as pat
	 WHERE t0.date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
	and (2*bp_diastolic + bp_systolic)/3 = max_mean_arterial and t0.patient_id=t1.patient_id
        and t0.patient_id=pat.id) as t
        where rownum=1;
--
-- Max blood pressure between now and one years
--  using most recent max mean aterial pressure for the period
--
drop table if exists gpr_bp1;
create table gpr_bp1 as
     select * from (
	SELECT 
	  t0.patient_id
	, t0.bp_systolic AS max_bp_systolic
	, t0.bp_diastolic AS max_bp_diastolic
        , t1.max_mean_arterial as map
        , gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_systolic::numeric, 
					 'SYS'::varchar, 
					 'BPPCT'::varchar) as syspct
        , gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_diastolic::numeric, 
					 'DIA'::varchar, 
					 'BPPCT'::varchar) as diapct
        , row_number() over (partition by t0.patient_id order by t0.date desc) as rownum
	FROM emr_encounter t0,
             (select patient_id, max((2*bp_diastolic + bp_systolic)/3) as max_mean_arterial
              from emr_encounter
              WHERE date between ( now() - interval '1 years' ) and now()
              group by patient_id) as t1,
             emr_patient as pat
	WHERE t0.date between ( now() - interval '1 years' ) and now() 
	and (2*bp_diastolic + bp_systolic)/3 = max_mean_arterial and t0.patient_id=t1.patient_id
        and t0.patient_id=pat.id) as t
        where rownum=1;
--
-- most recent blood pressure 
--
drop table if exists gpr_recbp;
create table gpr_recbp as
	SELECT 
	  t0.patient_id
	, max(t0.bp_systolic) as bp_systolic
	, max(t0.bp_diastolic) as bp_diastolic
        , max(gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_systolic::numeric, 
					 'SYS'::varchar, 
					 'BPPCT'::varchar)) as syspct
        , max(gen_pop_tools.NHBP(extract(year from age(t0.date, pat.date_of_birth))::numeric, 
                     pat.gender, 
                     gen_pop_tools.cdc_hgt((extract(year from age(t0.date, pat.date_of_birth))*12 + 
                                            extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
			         (case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
					 t0.height::numeric, 
					 'HTZ'::varchar ), 
					 t0.bp_diastolic::numeric, 
					 'DIA'::varchar, 
					 'BPPCT'::varchar)) as diapct
	, t0.date
        , max((2*t0.bp_diastolic + t0.bp_systolic)/3) as map
	FROM emr_encounter as t0,
	     (select patient_id, max(date) as date from emr_encounter 
	           where bp_systolic is not null and bp_diastolic is not null
	           group by patient_id) as t1,
             emr_patient as pat
	WHERE t0.bp_systolic is not null and t0.bp_diastolic is not null and 
	   t0.patient_id=t1.patient_id and
	   t0.date = t1.date and t0.date >= now() - interval '2 years'
           and t0.patient_id=pat.id
	GROUP BY t0.patient_id, t0.date;
--
-- most recent BMI 
--
drop table if exists gpr_bmi;
create table gpr_bmi as
        select t0.*
        , gen_pop_tools.cdc_bmi((extract(year from age(t0.date, pat.date_of_birth))*12 
                               + extract(month from age(t0.date, pat.date_of_birth)))::numeric, 
		(case when pat.gender='M' then '1' when pat.gender='F' then 2 else null end)::varchar, 
		null::numeric, 
		null::numeric, 
		t0.bmi::numeric, 
		'BMIPCT'::varchar ) as bmipct
      from (
	SELECT 
	  t0.patient_id,
	  t0.date
	, MAX( t0.weight / (t0.height/100)^2 ) AS bmi
	FROM emr_encounter t0,
	     (select patient_id, max(date) as date
	      from emr_encounter 
	      where weight is not null and height is not null
	      group by patient_id) t1
	WHERE t0.date >= ( now() - interval '2 years' )
	  and t0.weight is not null and t0.height is not null
	  and t0.date=t1.date
	  and t0.patient_id=t1.patient_id
	GROUP BY t0.patient_id, t0.date
) t0,
  emr_patient as pat
  where t0.patient_id=pat.id;
--
-- Recent A1C lab result
--
drop table if exists gpr_a1c;
create table gpr_a1c as
	SELECT 
	  l0.patient_id
	, l0.date  
	, MAX(l0.result_float) AS recent_a1c
	FROM emr_labresult l0,
	  conf_labtestmap m0,
	(
		SELECT 
		  l1.patient_id
		, m1.test_name
		, MAX(l1.date) AS date
		FROM emr_labresult l1
		INNER JOIN conf_labtestmap m1
			ON m1.native_code = l1.native_code
		where m1.test_name = 'a1c'
		    and l1.result_float is not null
		GROUP BY 
		  l1.patient_id
		, m1.test_name
	) u0
	WHERE m0.test_name = 'a1c'
	  and u0.patient_id = l0.patient_id
		AND u0.test_name = m0.test_name
		AND u0.date=l0.date
	  and m0.native_code = l0.native_code
	  AND l0.date >= ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id, l0.date;
--
-- Max A1C lab result last year
--
drop table if exists gpr_a1c1;
create table gpr_a1c1 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_a1c1
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'a1c'
	  AND l0.date between ( now() - interval '1 years' ) and now()
	GROUP BY 
	  l0.patient_id;
--
-- Max A1C lab result between 1 and 2 years ago
--
drop table if exists gpr_a1c2;
create table gpr_a1c2 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_a1c2
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'a1c'
	  AND l0.date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
	GROUP BY 
	  l0.patient_id;
--
-- Max A1C lab result between 2 and 3 years ago
--
drop table if exists gpr_a1c3;
create table gpr_a1c3 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_a1c3
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'a1c'
	  AND l0.date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id;
--
-- Recent cholesterol LDL lab result
--
drop table if exists gpr_ldl;
create table gpr_ldl as
	SELECT 
	  l0.patient_id
	, l0.date
	, MAX(l0.result_float) AS recent_ldl
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	INNER JOIN (
		SELECT 
		  l1.patient_id
		, m1.test_name
		, MAX(l1.date) AS date
		FROM emr_labresult l1
		INNER JOIN conf_labtestmap m1
			ON m1.native_code = l1.native_code
        where m1.test_name = 'cholesterol-ldl'
           and l1.result_float is not null
		GROUP BY 
		  l1.patient_id
		, m1.test_name
	) u0
		ON u0.patient_id = l0.patient_id
		AND u0.test_name = m0.test_name
		AND u0.date = l0.date
	WHERE m0.test_name = 'cholesterol-ldl'
	AND l0.date >= ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id, l0.date;
--
-- Max ldl lab result last year
--
drop table if exists gpr_ldl1;
create table gpr_ldl1 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_ldl1
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'cholesterol-ldl'
	  AND l0.date between ( now() - interval '1 years' ) and now()
	GROUP BY 
	  l0.patient_id;
--
-- Max ldl lab result between 1 and 2 years ago
--
drop table if exists gpr_ldl2;
create table gpr_ldl2 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_ldl2
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'cholesterol-ldl'
	  AND l0.date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
	GROUP BY 
	  l0.patient_id;
--
-- Max ldl lab result between 2 and 3 years ago
--
drop table if exists gpr_ldl3;
create table gpr_ldl3 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_ldl3
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'cholesterol-ldl'
	  AND l0.date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id;
--
-- Recent Triglycerides lab result
--
drop table if exists gpr_trig;
create table gpr_trig as
	SELECT 
	  l0.patient_id
	, l0.date
	, MAX(l0.result_float) AS recent_tgl 
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	INNER JOIN (
		SELECT 
		  l1.patient_id
		, m1.test_name
		, MAX(l1.date) AS date
		FROM emr_labresult l1
		INNER JOIN conf_labtestmap m1
			ON m1.native_code = l1.native_code
		where m1.test_name = 'triglycerides'
		   and l1.result_float is not null
		GROUP BY 
		  l1.patient_id
		, m1.test_name
	) u0
		ON u0.patient_id = l0.patient_id
		AND u0.test_name = m0.test_name
		AND u0.date = l0.date
	WHERE m0.test_name = 'triglycerides'
	AND l0.date >= ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id, l0.date;
--
-- Max trig lab result last year
--
drop table if exists gpr_trig1;
create table gpr_trig1 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_trig1
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'triglycerides'
	  AND l0.date between ( now() - interval '1 years' ) and now()
	GROUP BY 
	  l0.patient_id;
--
-- Max trig lab result between 1 and 2 years ago
--
drop table if exists gpr_trig2;
create table gpr_trig2 as 
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_trig2
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'triglycerides'
	  AND l0.date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
	GROUP BY 
	  l0.patient_id;
--
-- Max trig lab result between 2 and 3 years ago
--
drop table if exists gpr_trig3;
create table gpr_trig3 as
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_trig3
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'triglycerides'
	  AND l0.date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id;
--
-- Prediabetes
--
drop table if exists gpr_predm;
create table gpr_predm as
	SELECT 
	  DISTINCT c0.patient_id
	, 1 AS prediabetes
	FROM nodis_case c0
	INNER JOIN nodis_case c1
		ON c1.patient_id = c0.patient_id
		AND c1.condition NOT LIKE 'diabetes:type-%'
	WHERE c0.condition = 'diabetes:prediabetes'
	     and not exists (select null from nodis_case c2 
	                     where c2.date <= to_date('2008-01-01','yyyy-mm-dd')
	                         and c2.patient_id=c0.patient_id
	                         and c2.condition = 'diabetes:prediabetes')
	     and not exists (select null from nodis_case c3
	                     where c3.patient_id=c0.patient_id
	                         and c3.condition in ('diabetes:type-1','diabetes:type-2'));
--
-- Type 1 Diabetes
--
drop table if exists gpr_type1;
create table gpr_type1 as
	SELECT 
	DISTINCT patient_id
	, 1 AS type_1_diabetes
	FROM nodis_case
	WHERE condition = 'diabetes:type-1';
--
-- Type 2 Diabetes
--
drop table if exists gpr_type2;
create table gpr_type2 as
	SELECT 
	DISTINCT patient_id
	, 1 AS type_2_diabetes
	FROM nodis_case
	WHERE condition = 'diabetes:type-2';
--
-- Current Gestational diabetes
--
drop table if exists gpr_gdm;
create table gpr_gdm as
	SELECT distinct
	c0.patient_id
	, 1 AS current_gdm
	FROM nodis_case AS c0
        INNER JOIN nodis_case_timespans AS nct0
            ON nct0.case_id = c0.id
        INNER JOIN hef_timespan AS ts0
            ON nct0.timespan_id = ts0.id
	WHERE c0.condition = 'diabetes:gestational'
            AND ts0.start_date <= now()
            AND ( ts0.end_date >= now() OR ts0.end_date IS NULL);
--
-- Recent Gestational diabetes 1 year
--
drop table if exists gpr_recgdm1;
create table gpr_recgdm1 as
	SELECT distinct
	c0.patient_id
	, 1 AS recent_gdm
	FROM nodis_case AS c0
        INNER JOIN nodis_case_timespans AS nct0
            ON nct0.case_id = c0.id
        INNER JOIN hef_timespan AS ts0
            ON nct0.timespan_id = ts0.id
	WHERE c0.condition = 'diabetes:gestational' and
	             ((start_date between (now() - interval '1 years')  and now() and (end_date >= start_date or end_date is null))
	           or end_date between (now() - interval '1 years') and now());
--
-- Recent Gestational diabetes 2 year
--
drop table if exists gpr_recgdm2;
create table gpr_recgdm2 as
	SELECT distinct
	c0.patient_id
	, 1 AS recent_gdm
	FROM nodis_case AS c0
        INNER JOIN nodis_case_timespans AS nct0
            ON nct0.case_id = c0.id
        INNER JOIN hef_timespan AS ts0
            ON nct0.timespan_id = ts0.id
	WHERE c0.condition = 'diabetes:gestational' and
	             ((start_date between (now() - interval '2 years') and now() and (end_date >= start_date or end_date is null))
	           or end_date between (now() - interval '2 years') and now());
--
-- Recent pregnancy 2 year
--
drop table if exists gpr_recpreg2;
create table gpr_recpreg2 as
	SELECT
	  patient_id
	, 1 AS recent_pregnancy -- if there is more than one pregnancy in the period, take the last one
	FROM hef_timespan
	WHERE name = 'pregnancy' and 
	             ((start_date between (now() - interval '2 years') and now() and (end_date >= start_date or end_date is null))
	           or end_date between (now() - interval '2 years') and now())
	GROUP BY patient_id;
--
-- Recent pregnancy 1 year
--
drop table if exists gpr_recpreg1;
create table gpr_recpreg1 as
	SELECT
	  patient_id
	, 1 AS recent_pregnancy
	FROM hef_timespan
	WHERE name = 'pregnancy' and 
	             ((start_date between (now() - interval '1 years') and now() and (end_date >= start_date or end_date is null))
	           or end_date between (now() - interval '1 years') and now())
	GROUP BY patient_id;
--
-- Current pregnancy
--
drop table if exists gpr_curpreg;
create table gpr_curpreg as
	SELECT
	  DISTINCT ts.patient_id
	, 1 AS currently_pregnant
	FROM hef_timespan ts
	WHERE name = 'pregnancy'
            AND start_date between (now() - interval ' 9 months') and now() 
            AND ( end_date >= now() OR end_date IS NULL);
--
-- Insulin
--    Prescription for insulin within the previous year
--
drop table if exists gpr_insulin;
create table gpr_insulin as
	SELECT 
	  DISTINCT patient_id
	, 1 AS insulin
	FROM emr_prescription
	WHERE name ILIKE '%insulin%'
            AND date >= ( now() - interval '1 year' );
--
-- Metformin
--     Prescription for metformin within the previous year
--
drop table if exists gpr_metformin;
create table gpr_metformin as 
	SELECT 
	  DISTINCT patient_id
	, 1 AS metformin
	FROM emr_prescription
	WHERE name ILIKE '%metformin%'
            AND date >= ( now() - interval '1 year' );
--
-- Influenza vaccine
--     Prescription for influenza vaccine current flu season
--
drop table if exists gpr_flu_cur;
create table gpr_flu_cur as
	SELECT 
	  DISTINCT patient_id
	, 1 AS influenza_vaccine
	FROM emr_immunization
	WHERE name ILIKE '%influenza%'
	AND case
		  when extract(quarter from now())=4 then extract(year from now())+1
		  else extract(year from now())
	    end =
	    case
		  when extract(quarter from date)=4 then extract(year from date)+1
		  else extract(year from date)
	    end;
--
-- Influenza vaccine
--     Prescription for influenza vaccine previous flu season
--
drop table if exists gpr_flu_prev;
create table gpr_flu_prev as
	SELECT 
	  DISTINCT patient_id
	, 1 AS influenza_vaccine
	FROM emr_immunization
	WHERE name ILIKE '%influenza%'
	AND case
		  when extract(quarter from (now()-interval '1 years'))=4 then extract(year from (now()-interval '1 years'))+1
		  else extract(year from (now()-interval '1 years'))
	    end =
	    case
		  when extract(quarter from date)=4 then extract(year from date)+1
		  else extract(year from date)
	    end;
--
-- most recent chlamydia lab result
--
drop table if exists gpr_chlamydia;
create table gpr_chlamydia as
	SELECT 
	  l0.patient_id
	, case 
            when l0.date >= ( now() - interval '1 year' ) then '1'
            when l0.date >= ( now() - interval '2 years' ) then '2'
            else '3'     
          end  AS recent_chlamydia 
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	INNER JOIN (
		SELECT 
		  l1.patient_id
		, MAX(l1.date) AS date
		FROM emr_labresult l1
		INNER JOIN conf_labtestmap m1
			ON m1.native_code = l1.native_code
		where m1.test_name = 'chlamydia'
		GROUP BY 
		  l1.patient_id
		, m1.test_name
	) u0
		ON u0.patient_id = l0.patient_id
		AND u0.date = l0.date
	WHERE m0.test_name = 'chlamydia'
	GROUP BY 
	  l0.patient_id, l0.date;
--
-- Smoking
--
drop table if exists gpr_smoking;
create table gpr_smoking as
   select case when t1.latest='Yes' then '1'
               when t2.yesOrQuit='Quit' then '2'
               when t3.passive='Passive' then '4'
               when t4.never='Never' then '3'
               else '5' 
           end as smoking,
           t1.patient_id
   from
     (select t00.tobacco_use as latest, t00.patient_id 
      from emr_socialhistory t00
      inner join
      (select max(date) as maxdate, patient_id 
       from emr_socialhistory 
       where tobacco_use is not null and tobacco_use<>''
       group by patient_id) t01 on t00.patient_id=t01.patient_id and t00.date=t01.maxdate) t1
   left outer join
     (select max(val) as yesOrQuit, patient_id
      from (select 'Quit'::text as val, patient_id
            from emr_socialhistory where tobacco_use in ('Yes','Quit')) t00
            group by patient_id) t2 on t1.patient_id=t2.patient_id
   left outer join
     (select max(val) as passive, patient_id
      from (select 'Passive'::text as val, patient_id
            from emr_socialhistory where tobacco_use ='Passive') t00
            group by patient_id) t3 on t1.patient_id=t3.patient_id
   left outer join
     (select max(val) as never, patient_id
      from (select 'Never'::text as val, patient_id
            from emr_socialhistory where tobacco_use ='Never') t00
            group by patient_id) t4 on t1.patient_id=t4.patient_id;
--
-- Asthma
--
drop table if exists gpr_asthma;
create table gpr_asthma as
  select case when count(*) > 0 then 1 else 2 end as asthma,
  patient_id
from nodis_case
where condition='asthma'
group by patient_id;
--
-- Number of encounters last year
--
drop table if exists gpr_enc;
create table gpr_enc as
  select case when count(*) >= 2 then 2
              else count(*) end as nvis,
  patient_id
  from emr_encounter
  where date>=current_date - interval '1 year'
  group by patient_id;        

