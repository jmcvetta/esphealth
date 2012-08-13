--------------------------------------------------------------------------------
--
--                            Additional Indices
--
--
-- These indices provide significant performance improvements for our queries.
--
--------------------------------------------------------------------------------


-- Django does not automagically generate this, even with db_index=True,
-- because 'code' is primary key for table static_icd9.
CREATE INDEX "static_icd9_code_like" ON "static_icd9" ("code" varchar_pattern_ops);

