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
  p.id AS patient_id
, p.mrn
, u7.last_enc_date
, date_part('year', age(p.date_of_birth))
, p.gender
, p.race
, p.zip
, u6.currently_pregnant
, u6.current_gdm
, u5.recent_pregnancy
, enc0.max_bp_systolic
, enc0.max_bp_diastolic
, u0.recent_a1c
, u1.recent_ldl
, u2.prediabetes
, u3.type_1_diabetes
, u4.type_2_diabetes
FROM emr_patient AS p

--
-- Encounter aggregates
--
LEFT JOIN (
	SELECT 
	  patient_id
	, MAX(date) AS last_enc_date
	, MAX(bp_systolic) AS max_bp_systolic
	, MAX(bp_diastolic) AS max_bp_diastolic
	FROM emr_encounter
	WHERE date >= now() - interval '2 years'
	GROUP BY patient_id
) AS u7
	ON enc0.patient_id = p.id

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
	AND l0.date >= now() - interval '2 years'
	GROUP BY 
	  l0.patient_id
) u0
	ON u0.patient_id = p.id

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
	AND l0.date >= now() - interval '2 years'
	GROUP BY 
	  l0.patient_id
) u1
	ON u1.patient_id = p.id

--
-- Prediabetes
--
LEFT JOIN (
	SELECT 
	  DISTINCT c0.patient_id
	, TRUE AS prediabetes
	FROM nodis_case c0
	INNER JOIN nodis_case c1
		ON c1.patient_id = c0.patient_id
		AND c1.condition NOT LIKE 'diabetes:type-%'
	WHERE c0.condition = 'diabetes:prediabetes'
) u2
	ON u2.patient_id = p.id

--
-- Type 1 Diabetes
--
LEFT JOIN (
	SELECT 
	DISTINCT patient_id
	, TRUE AS type_1_diabetes
	FROM nodis_case
	WHERE condition = 'diabetes:type-1'
) u3
	ON u3.patient_id = p.id

--
-- Type 2 Diabetes
--
LEFT JOIN (
	SELECT 
	patient_id
	, TRUE AS type_2_diabetes
	FROM nodis_case
	WHERE condition = 'diabetes:type-2'
) u4
	ON u4.patient_id = p.id

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
) AS u5
	ON u5.patient_id = p.id

--
-- Current pregnancy
--
LEFT JOIN (
	SELECT
	  DISTINCT ts.patient_id
	, true AS currently_pregnant
	, CASE 
		WHEN c.id IS NOT NULL THEN TRUE
		ELSE FALSE 
		END AS current_gdm
	FROM hef_timespan ts
	LEFT JOIN nodis_case c
		ON c.patient_id = ts.patient_id
		AND c.date >= ts.start_date
		AND c.date <= ts.end_date
		AND c.condition = 'diabetes:gestational'
	WHERE name = 'pregnancy'
	AND start_date <= now()
	AND end_date >= now()

) AS u6
	ON u4.patient_id = p.id

--
-- Insulin
--    Prescription for insulin within the previous year
--
LEFT JOIN (
	SELECT 
	  DISTINCT patient_id
	, TRUE AS insulin
	FROM emr_prescription
	WHERE name ILIKE '%insulin%'
	AND date >= now() - interval '1 year'
) u7
	ON u7.patient_id = p.id


--
-- Metformin
--     Prescription for metformin within the previous year
--
LEFT JOIN (
	SELECT 
	  DISTINCT patient_id
	, TRUE AS metformin
	FROM emr_prescription
	WHERE name ILIKE '%metformin%'
	AND date >= now() - interval '1 year'
) u8
	ON u8.patient_id = p.id


--
-- Influenza vaccine
--     Prescription for influenza vaccine current flu season
--     FIXME: Current SQL looks at previous year, not current flu season.
--            What are the official dates for flu season?
--
LEFT JOIN (
	SELECT 
	  DISTINCT patient_id
	, TRUE AS metformin
	FROM emr_immunization
	WHERE name ILIKE '%influenza%'
	AND date >= now() - interval '1 year'
) u9
	ON u9.patient_id = p.id

--
-- Ordering
--
ORDER BY p.id
