/*--------------------------------------------------------------------------------
--
--                                ESP Health
--                         General Population Report
--
--------------------------------------------------------------------------------
--
-- @author: Jason McVetta <jason.mcvetta@gmail.com> Bob Zambarano <bzambarano@commoninf.com>
-- @organization: Commonwealth Informatics <http://www.commoninf.com>
-- @contact: http://esphealth.org
-- @copyright: (c) 2012 Commonwealth Informatics
-- @license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
--
--------------------------------------------------------------------------------
--
-- This query contains some PostgreSQL-specific functions.  It will probably 
-- not run on other RDBMS without porting.
--
--------------------------------------------------------------------------------*/
--select max(counts) from ( select count(*) as counts from (
SELECT 
  pat.id AS patient_id
, pat.mrn
, date_part('year', age(lastenc.last_enc_date)) as years_since_last_enc
, date_part('year', age(pat.date_of_birth)) as age
, pat.gender 
, pat.race
, case
    when substring(pat.zip,6,1)='-' then substring(pat.zip,1,5)
    else pat.zip
  end zip
, bmi.bmi
, bmi.bmipct
, bmi.date 
, curpreg.currently_pregnant
, recpreg1.recent_pregnancy as recent_pregnancy1
, recpreg2.recent_pregnancy as recent_pregnancy2
, gdm.current_gdm
, recgdm1.recent_gdm as recent_gdm1
, recgdm2.recent_gdm as recent_gdm2
, bp1.max_bp_systolic as max_bp_systolic1
, bp1.max_bp_diastolic as max_bp_diastolic1
, bp1.map as map1
, bp1.syspct as syspct1
, bp1.diapct as diapct1
, bp2.max_bp_systolic as max_bp_systolic2
, bp2.max_bp_diastolic as max_bp_diastolic2
, bp2.map as map2
, bp2.syspct as syspct2
, bp2.diapct as diapct2
, bp3.max_bp_systolic as max_bp_systolic3
, bp3.max_bp_diastolic as max_bp_diastolic3
, bp3.map as map3 
, bp3.syspct as syspct3
, bp3.diapct as diapct3
, recbp.bp_systolic
, recbp.bp_diastolic
, recbp.date as rec_bp_date
, recbp.map 
, recbp.syspct
, recbp.diapct
, ldl.recent_ldl
, ldl.date as ldl_date
, ldl1.max_ldl1
, ldl2.max_ldl2
, ldl3.max_ldl3
, a1c.recent_a1c
, a1c.date as a1c_date
, a1c1.max_a1c1
, a1c2.max_a1c2
, a1c3.max_a1c3
, trig.recent_tgl
, trig.date as trig_date
, trig1.max_trig1
, trig2.max_trig2
, trig3.max_trig3
, predm.prediabetes
, type1.type_1_diabetes
, type2.type_2_diabetes
, insulin.insulin
, metformin.metformin
, flu_cur.influenza_vaccine as cur_flu_vax
, flu_prev.influenza_vaccine as prev_flu_vax
FROM emr_patient AS pat 
--
-- Last encounter
--
LEFT JOIN (
	SELECT 
	  patient_id
	, MAX(date) AS last_enc_date
	FROM emr_encounter
	GROUP BY patient_id
) AS lastenc
	ON lastenc.patient_id = pat.id
--
-- Max blood pressure between two and three years
--  using most recent max mean aterial pressure for the period
--
LEFT JOIN ( select * from (
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
        where rownum=1
) AS bp3
	ON bp3.patient_id = pat.id
--
-- Max blood pressure between one and two years
--  using most recent max mean aterial pressure for the period
--
LEFT JOIN ( select * from (
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
        where rownum=1
) AS bp2
	ON bp2.patient_id = pat.id
--
-- Max blood pressure between now and one years
--  using most recent max mean aterial pressure for the period
--
LEFT JOIN ( select * from (
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
        where rownum=1
) AS bp1
	ON bp1.patient_id = pat.id
--
-- most recent blood pressure 
--
LEFT JOIN (
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
	GROUP BY t0.patient_id, t0.date
) AS recbp
	ON recbp.patient_id = pat.id
--
-- most recent BMI 
--
LEFT JOIN (
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
	      where is weight is not null and height not null
	      group by patient_id) t1
	WHERE t0.date >= ( now() - interval '2 years' )
	  and t0.weight is not null and t0.height is not null
	  and t0.date=t1.date
	  and t0.patient_id=t1.patient_id
	GROUP BY t0.patient_id, t0.date
) t0,
  emr_patient as pat
  where t0.patient_id=pat.id
)
 AS bmi
	ON bmi.patient_id = pat.id
--
-- Recent A1C lab result
--
LEFT JOIN (
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
	  l0.patient_id, l0.date
) AS a1c
	ON a1c.patient_id = pat.id
--
-- Max A1C lab result last year
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_a1c1
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'a1c'
	  AND l0.date between ( now() - interval '1 years' ) and now()
	GROUP BY 
	  l0.patient_id
) AS a1c1
	ON a1c1.patient_id = pat.id
--
-- Max A1C lab result between 1 and 2 years ago
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_a1c2
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'a1c'
	  AND l0.date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
	GROUP BY 
	  l0.patient_id
) AS a1c2
	ON a1c2.patient_id = pat.id
--
-- Max A1C lab result between 2 and 3 years ago
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_a1c3
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'a1c'
	  AND l0.date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id
) AS a1c3
	ON a1c3.patient_id = pat.id
--
-- Recent cholesterol LDL lab result
--
LEFT JOIN (
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
	  l0.patient_id, l0.date
) AS ldl
	ON ldl.patient_id = pat.id
--
-- Max ldl lab result last year
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_ldl1
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'cholesterol-ldl'
	  AND l0.date between ( now() - interval '1 years' ) and now()
	GROUP BY 
	  l0.patient_id
) AS ldl1
	ON ldl1.patient_id = pat.id
--
-- Max ldl lab result between 1 and 2 years ago
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_ldl2
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'cholesterol-ldl'
	  AND l0.date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
	GROUP BY 
	  l0.patient_id
) AS ldl2
	ON ldl2.patient_id = pat.id
--
-- Max ldl lab result between 2 and 3 years ago
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_ldl3
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'cholesterol-ldl'
	  AND l0.date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id
) AS ldl3
	ON ldl3.patient_id = pat.id
--
-- Recent Triglycerides lab result
--
LEFT JOIN (
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
	  l0.patient_id, l0.date
) AS trig
	ON trig.patient_id = pat.id
--
-- Max trig lab result last year
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_trig1
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'triglycerides'
	  AND l0.date between ( now() - interval '1 years' ) and now()
	GROUP BY 
	  l0.patient_id
) AS trig1
	ON trig1.patient_id = pat.id
--
-- Max trig lab result between 1 and 2 years ago
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_trig2
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'triglycerides'
	  AND l0.date between ( now() - interval '2 years' ) and ( now() - interval '1 years' )
	GROUP BY 
	  l0.patient_id
) AS trig2
	ON trig2.patient_id = pat.id
--
-- Max trig lab result between 2 and 3 years ago
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS max_trig3
	FROM emr_labresult l0
	INNER JOIN conf_labtestmap m0
		ON m0.native_code = l0.native_code
	WHERE m0.test_name = 'triglycerides'
	  AND l0.date between ( now() - interval '3 years' ) and ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id
) AS trig3
	ON trig3.patient_id = pat.id
--
-- Prediabetes
--
LEFT JOIN (
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
	                         and c3.condition in ('diabetes:type-1','diabetes:type-2'))
) AS predm
	ON predm.patient_id = pat.id

--
-- Type 1 Diabetes
--
LEFT JOIN (
	SELECT 
	DISTINCT patient_id
	, 1 AS type_1_diabetes
	FROM nodis_case
	WHERE condition = 'diabetes:type-1'
) AS type1
	ON type1.patient_id = pat.id

--
-- Type 2 Diabetes
--
LEFT JOIN (
	SELECT 
	DISTINCT patient_id
	, 1 AS type_2_diabetes
	FROM nodis_case
	WHERE condition = 'diabetes:type-2'
) AS type2
	ON type2.patient_id = pat.id

--
-- Current Gestational diabetes
--
LEFT JOIN (
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
            AND ( ts0.end_date >= now() OR ts0.end_date IS NULL)
) AS gdm
	ON gdm.patient_id = pat.id
--
-- Recent Gestational diabetes 1 year
--
LEFT JOIN (
	SELECT distinct
	c0.patient_id
	, 1 AS recent_gdm
	FROM nodis_case AS c0
        INNER JOIN nodis_case_timespans AS nct0
            ON nct0.case_id = c0.id
        INNER JOIN hef_timespan AS ts0
            ON nct0.timespan_id = ts0.id
	WHERE c0.condition = 'diabetes:gestational' and
	             ((start_date between (now() - interval '1 years') and now() and end_date <= now())
	           or end_date between (now() - interval '1 years') and now())
) AS recgdm1
	ON recgdm1.patient_id = pat.id
--
-- Recent Gestational diabetes 2 year
--
LEFT JOIN (
	SELECT distinct
	c0.patient_id
	, 1 AS recent_gdm
	FROM nodis_case AS c0
        INNER JOIN nodis_case_timespans AS nct0
            ON nct0.case_id = c0.id
        INNER JOIN hef_timespan AS ts0
            ON nct0.timespan_id = ts0.id
	WHERE c0.condition = 'diabetes:gestational' and
	             ((start_date between (now() - interval '2 years') and (now() - interval '1 year') and end_date <= (now() - interval '1 year'))
	           or end_date between (now() - interval '2 years') and (now() - interval '1 year'))
) AS recgdm2
	ON recgdm2.patient_id = pat.id
--
-- Recent pregnancy 2 year
--
LEFT JOIN (
	SELECT
	  patient_id
	, 1 AS recent_pregnancy -- if there is more than one pregnancy in the period, take the last one
	FROM hef_timespan
	WHERE name = 'pregnancy' and 
	             ((start_date between (now() - interval '2 years') and (now() - interval '1 year') and end_date <= (now() - interval '1 year'))
	           or end_date between (now() - interval '2 years') and (now() - interval '1 year'))
	GROUP BY patient_id
) AS recpreg2
	ON recpreg2.patient_id = pat.id
--
-- Recent pregnancy 1 year
--
LEFT JOIN (
	SELECT
	  patient_id
	, 1 AS recent_pregnancy
	FROM hef_timespan
	WHERE name = 'pregnancy' and 
	             ((start_date between (now() - interval '1 years') and now() and end_date <= now())
	           or end_date between (now() - interval '1 years') and now())
	GROUP BY patient_id
) AS recpreg1
	ON recpreg1.patient_id = pat.id
--
-- Current pregnancy
--
LEFT JOIN (
	SELECT
	  DISTINCT ts.patient_id
	, 1 AS currently_pregnant
	FROM hef_timespan ts
	WHERE name = 'pregnancy'
            AND start_date between (now() - interval ' 9 months') and now() 
            AND ( end_date >= now() OR end_date IS NULL)
) AS curpreg
	ON curpreg.patient_id = pat.id
--
-- Insulin
--    Prescription for insulin within the previous year
--
LEFT JOIN (
	SELECT 
	  DISTINCT patient_id
	, 1 AS insulin
	FROM emr_prescription
	WHERE name ILIKE '%insulin%'
            AND date >= ( now() - interval '1 year' )
) AS insulin
	ON insulin.patient_id = pat.id
--
-- Metformin
--     Prescription for metformin within the previous year
--
LEFT JOIN (
	SELECT 
	  DISTINCT patient_id
	, 1 AS metformin
	FROM emr_prescription
	WHERE name ILIKE '%metformin%'
            AND date >= ( now() - interval '1 year' )
) AS metformin
	ON metformin.patient_id = pat.id
--
-- Influenza vaccine
--     Prescription for influenza vaccine current flu season
--
LEFT JOIN (
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
	    end
) AS flu_cur
	ON flu_cur.patient_id = pat.id
--
-- Influenza vaccine
--     Prescription for influenza vaccine previous flu season
--
LEFT JOIN (
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
	    end
) AS flu_prev
	ON flu_prev.patient_id = pat.id
--
-- WHERE criteria 
--
WHERE pat.date_of_death IS NULL
--
-- Ordering
--
ORDER BY pat.id
--) counts group by patient_id) maxcnts
;


