
SELECT date_part('month', ppt.month) AS month
, date_part('year', ppt.month) AS year
, ppt.practice_patients
, me.total_encounters
, me.patients_with_encounter
, u1.patient_id
, u1.any_glucose_test
, u2.a1c
, u3.ogtt
, u4.glucose_fasting
, pat.mrn
, pat.last_name
, pat.first_name
, age(ppt.month, pat.date_of_birth)
, pat.race
, pat.gender
FROM analysis.practice_patients AS ppt
JOIN analysis.month_encs AS me
    ON me.month = ppt.month
LEFT JOIN (
    SELECT DISTINCT patient_id
    , month
    , true AS any_glucose_test
    FROM analysis.pt_events
    WHERE test = 'any_glucose_test'
    ) AS u1
    ON u1.month = ppt.month
LEFT JOIN (
    SELECT DISTINCT patient_id
    , month
    , TRUE as a1c
    FROM analysis.pt_events
    WHERE test = 'a1c'
    GROUP BY patient_id, month
    ) AS u2
    ON u2.month = ppt.month
        AND u2.patient_id = u1.patient_id
LEFT JOIN (
    SELECT DISTINCT patient_id
    , month
    , true AS ogtt
    FROM analysis.pt_events
    WHERE test = 'ogtt'
    GROUP BY patient_id, month
    ) AS u3
    ON u3.month = ppt.month
        AND u3.patient_id = u1.patient_id
        AND u2.month = u1.month
LEFT JOIN (
    SELECT DISTINCT patient_id
    , month
    , true AS glucose_fasting
    FROM analysis.pt_events
    WHERE test = 'glucose_fasting'
    GROUP BY patient_id, month
    ) AS u4
    ON u4.month = ppt.month
        AND u4.patient_id = u1.patient_id
JOIN emr_patient AS pat
    ON u1.patient_id = pat.id
ORDER BY ppt.month;


