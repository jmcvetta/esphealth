--------------------------------------------------------------------------------
--
--                           Multi-Column Indices
--
--
-- These indices provide significant performance improvements for our queries.
--------------------------------------------------------------------------------
CREATE INDEX hef_event_patient_eventtype ON hef_event (patient_id, event_type_id);
CREATE INDEX hef_event_eventtype_date ON hef_event (event_type_id, date);
CREATE INDEX hef_event_patient_eventtype_date ON hef_event (patient_id, event_type_id, date);
-- CREATE INDEX hef_timespan_patient_event_type ON hef_timespan (patient_id, event_type_id);
-- CREATE INDEX hef_timespan_patient_event_type_dates ON hef_timespan (patient_id, event_type_id, start_date, end_date);
