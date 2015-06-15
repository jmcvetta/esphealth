--------------------------------------------------------------------------------
--
--                           Multi-Column Indices
--
--
-- These indices provide significant performance improvements for our queries.
--------------------------------------------------------------------------------
CREATE INDEX hef_event_patient_name ON hef_event (patient_id, name);
CREATE INDEX hef_event_name_date ON hef_event (name, date);
CREATE INDEX hef_event_patient_name_date ON hef_event (patient_id, name, date);
-- CREATE INDEX hef_timespan_patient_name ON hef_timespan (patient_id, name);
-- CREATE INDEX hef_timespan_patient_name_dates ON hef_timespan (patient_id, name, start_date, end_date);
