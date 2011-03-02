BEGIN;

DROP TABLE IF EXISTS analysis.practice_patients;


CREATE TABLE analysis.practice_patients AS
    SELECT month
    , COUNT(patient_id) AS practice_patients
    FROM (
        SELECT DISTINCT e0.month
        , e1.patient_id
        , COUNT(e1.enc_id)
        FROM (
            SELECT DISTINCT date_trunc('month', date) AS month
            FROM emr_encounter
            WHERE date >= 'June 1 2009'
            ) AS e0
        LEFT JOIN (
            SELECT patient_id
            , date_trunc('month', date) AS month
            , id AS enc_id
            FROM emr_encounter
            ) AS e1
            ON e1.month <= e0.month
                AND e1.month >= e0.month - interval '2 years'
        GROUP BY e0.month, e1.patient_id
        ORDER BY e0.month
        ) AS u0
    WHERE u0.count > 2
    GROUP BY u0.month
    UNION
    SELECT DISTINCT date_trunc('month', date) as month
    , (
        SELECT COUNT(DISTINCT e2.patient_id)
        FROM (
            SELECT patient_id
            , COUNT(*)
            FROM emr_encounter
            WHERE date < 'June 1 2009'
            GROUP BY patient_id
            ) AS e2
            WHERE e2.count > 2
        ) AS count
    FROM emr_encounter
    WHERE date < 'June 1 2009'
    ORDER BY month;

CREATE INDEX practice_patients_month ON analysis.practice_patients ( month );

COMMIT;
