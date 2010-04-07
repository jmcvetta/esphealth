SELECT preg.id AS pregnancy_id
, pat.mrn
, pat.last_name
, pat.first_name
, preg.start_date
, preg.end_date
, preg.pattern
FROM hef_pregnancy preg
JOIN emr_patient pat 
ON pat.id = preg.patient_id
ORDER BY start_date;