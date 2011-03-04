ALTER TABLE emr_patient ALTER COLUMN created_timestamp SET DEFAULT NOW();
ALTER TABLE emr_provider ALTER COLUMN created_timestamp SET DEFAULT NOW();
ALTER TABLE emr_patient ALTER COLUMN updated_by SET DEFAULT '[database default]';
ALTER TABLE emr_provider ALTER COLUMN updated_by SET DEFAULT '[database default]';

