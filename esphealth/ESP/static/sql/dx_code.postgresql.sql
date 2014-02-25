--------------------------------------------------------------------------------
--
--                            Additional Indices
--
--
-- These indices provide significant performance improvements for our queries.
--
--------------------------------------------------------------------------------


-- Django does not automagically generate this, even with db_index=True,
-- because 'code' is primary key for table static_dx_code.
CREATE INDEX "static_dx_code_code_like" ON "static_dx_code" ("code" varchar_pattern_ops);

