--------------------------------------------------------------------------------
--
--                           Multi-Column Indices
--
--
-- These indices provide significant performance improvements for our queries.
--------------------------------------------------------------------------------
CREATE INDEX new_hef_event_heuristic_content_type ON new_hef_event (heuristic_id, content_type_id);
