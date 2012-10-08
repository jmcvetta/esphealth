-- ----------------------------------------------------------------
-- 2012-10-08
-- ----------------------------------------------------------------
ALTER TABLE emr_provenance
   ADD COLUMN data_date date;

-- Populate the data_date for provenance records that already exist.
UPDATE emr_provenance
   SET data_date = to_date(substring(source, E'.*\\.(\\d{8})$'),
                           'MMDDYYYY')
 WHERE data_date is null
   AND char_length(substring(source, E'.*\\.(\\d{8})$')) = 8;
COMMIT;

