--------------------------------------------------------------------------------
--
--                                ESP Health
--                         General Population Report
--
--------------------------------------------------------------------------------
--
-- @author: Jason McVetta <jason.mcvetta@gmail.com>
-- @organization: Channing Laboratory - http://www.channing.harvard.edu
-- @contact: http://esphealth.org
-- @copyright: (c) 2011 Channing Laboratory
-- @license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
--
--------------------------------------------------------------------------------
--
-- This query contains some PostgreSQL-specific functions.  It will probably 
-- not run on other RDBMS without porting.
--
--------------------------------------------------------------------------------


SELECT 
  pat.id AS patient_id
, pat.mrn
, date_part('year', age(lastenc.last_enc_date)) AS years_since_last_enc
, date_part('year', age(pat.date_of_birth)) AS age
, pat.gender
, pat.race
, pat.zip
, bmi.bmi
, curpreg.currently_pregnant
, gdm.current_gdm
, recpreg.recent_pregnancy
, bp.max_bp_systolic
, bp.max_bp_diastolic
, a1c.recent_a1c
, ldl.recent_ldl
, predm.prediabetes
, type1.type_1_diabetes
, type2.type_2_diabetes
, insulin.insulin
, metformin.metformin
, flu.influenza_vaccine
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
-- Max blood pressure in past 2 years
--
LEFT JOIN (
	SELECT 
	  patient_id
	, MAX(bp_systolic) AS max_bp_systolic
	, MAX(bp_diastolic) AS max_bp_diastolic
	FROM emr_encounter
	WHERE date >= ( now() - interval '2 years' )
	GROUP BY patient_id
) AS bp
	ON bp.patient_id = pat.id

--
-- BMI 
--
LEFT JOIN (
	SELECT 
	  patient_id
	, MAX(bmi) AS bmi
	FROM emr_encounter
	WHERE date >= ( now() - interval '1 years' )
	GROUP BY patient_id
) AS bmi
	ON bmi.patient_id = pat.id
	AND age(pat.date_of_birth) >= '12 years'

--
-- Recent A1C lab result
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
	, MAX(l0.result_float) AS recent_a1c
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
		GROUP BY 
		  l1.patient_id
		, m1.test_name
	) u0
		ON u0.patient_id = l0.patient_id
		AND u0.test_name = m0.test_name
	WHERE m0.test_name = 'a1c'
	AND l0.date >= ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id
) AS a1c
	ON a1c.patient_id = pat.id

--
-- Recent cholesterol LDL lab result
--
LEFT JOIN (
	SELECT 
	  l0.patient_id
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
		GROUP BY 
		  l1.patient_id
		, m1.test_name
	) u0
		ON u0.patient_id = l0.patient_id
		AND u0.test_name = m0.test_name
	WHERE m0.test_name = 'cholesterol-ldl'
	AND l0.date >= ( now() - interval '2 years' )
	GROUP BY 
	  l0.patient_id
) AS ldl
	ON ldl.patient_id = pat.id

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
	patient_id
	, 1 AS type_2_diabetes
	FROM nodis_case
	WHERE condition = 'diabetes:type-2'
) AS type2
	ON type2.patient_id = pat.id

--
-- Gestational diabetes
--
LEFT JOIN (
	SELECT 
	c0.patient_id
	, 1 AS current_gdm
	FROM nodis_case AS c0
        INNER JOIN nodis_case_timespans AS nct0
            ON nct0.case_id = c0.id
        INNER JOIN hef_timespan AS ts0
            ON nct0.timespan_id = ts0.id
	WHERE c0.condition = 'diabetes:gestational'
            AND ts0.start_date <= now()
            AND ts0.end_date >= now()
) AS gdm
	ON gdm.patient_id = pat.id

--
-- Recent pregnancy
--
LEFT JOIN (
	SELECT
	  patient_id
	, MAX(start_date) AS recent_pregnancy
	FROM hef_timespan
	WHERE name = 'pregnancy'
	GROUP BY patient_id
) AS recpreg
	ON recpreg.patient_id = pat.id

--
-- Current pregnancy
--
LEFT JOIN (
	SELECT
	  DISTINCT ts.patient_id
	, 1 AS currently_pregnant
	FROM hef_timespan ts
	WHERE name = 'pregnancy'
            AND start_date <= now()
            AND end_date >= now()
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
	AND date >= ( now() - interval '10 months' )
	AND date_part('month', date) >= 7
	AND date_part('month', date) <= 8
) AS flu
	ON flu.patient_id = pat.id

--
-- Ordering
--
ORDER BY pat.id
