--------------------------------------------------------------------------------
--
--                           Multi-Column Indices
--
--
-- These indices provide significant performance improvements for our queries.
--------------------------------------------------------------------------------
-- Optimization for reporting
CREATE INDEX emr_prescription_ts_name_like ON emr_prescription (updated_timestamp, name text_pattern_ops);
