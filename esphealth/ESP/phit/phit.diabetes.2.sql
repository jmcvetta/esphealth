BEGIN;

DROP TABLE IF EXISTS analysis.pt_events;
DROP TABLE IF EXISTS analysis.month_encs;


CREATE TABLE analysis.pt_events AS
    SELECT DISTINCT patient_id
    , date_trunc('month', e.date) AS month
    , 'any_glucose_test' AS test
    FROM hef_event AS e
    WHERE e.event_type_id IN (
        SELECT name
        FROM hef_eventtype
        WHERE name LIKE 'ogtt%--any_result'
            OR name LIKE 'a1c--any_result'
            OR name LIKE 'glucose_fasting--any_result'
        )
    GROUP BY patient_id, month;

INSERT INTO analysis.pt_events
    SELECT DISTINCT patient_id
    , date_trunc('month', e.date) AS month
    , 'a1c' AS test
    FROM hef_event AS e
    JOIN emr_patient AS p
        ON p.id = e.patient_id
    WHERE e.event_type_id IN (
        SELECT name
        FROM hef_eventtype
        WHERE name = 'a1c--any_result'
        )
    GROUP BY patient_id, month;

INSERT INTO analysis.pt_events
    SELECT DISTINCT patient_id
    , date_trunc('month', e.date) AS month
    , 'ogtt' as test
    FROM hef_event AS e
    JOIN emr_patient AS p
        ON p.id = e.patient_id
    WHERE e.event_type_id IN (
        SELECT name
        FROM hef_eventtype
        WHERE name LIKE 'ogtt%--any_result'
        )
    GROUP BY patient_id, month;

INSERT INTO analysis.pt_events
    SELECT DISTINCT patient_id
    , date_trunc('month', e.date) AS month
    , 'glucose_fasting' AS test
    FROM hef_event AS e
    WHERE e.event_type_id IN (
        SELECT name
        FROM hef_eventtype
        WHERE name = 'glucose_fasting--any_result'
        )
    GROUP BY patient_id, month;

CREATE TABLE analysis.month_encs AS
    SELECT date_trunc('month', date) AS month
    , COUNT(*) AS total_encounters
    , COUNT(DISTINCT patient_id) AS patients_with_encounter
    FROM emr_encounter
    GROUP BY month;

CREATE INDEX pt_events_month ON analysis.pt_events ( month );
CREATE INDEX pt_events_test ON analysis.pt_events ( test );
CREATE INDEX pt_events_test_lik ON analysis.pt_events ( test varchar_pattern_ops);
CREATE INDEX pt_events_patient ON analysis.pt_events ( patient_id );
CREATE INDEX pt_events_patient_test ON analysis.pt_events ( patient_id, test );
CREATE INDEX pt_events_patient_month_test ON analysis.pt_events ( patient_id, month, test );
CREATE INDEX pt_events_month_patient ON analysis.pt_events ( month, patient_id );
CREATE INDEX pt_events_month_patient_test ON analysis.pt_events ( month, patient_id, test );
CREATE INDEX pt_events_test_month_patient ON analysis.pt_events ( test, month, patient_id );
CREATE INDEX pt_events_test_patient_month ON analysis.pt_events ( test, patient_id, month );
COMMIT;
