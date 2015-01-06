-- The following delete query cleans up static_dx_code of any unreferenced codes
delete from static_dx_code t0
where not exists (select null from emr_problem t1 where t1.dx_code_id=t0.code)
    and not exists (select null from emr_encounter_dx_code_codes t1 where t1.dx_code_id=t0.code)
    and not exists (select null from conf_reportabledx_code t1 where t1.dx_code_id=t0.code)
    and not exists (select null from vaers_diagnosticseventrule_heuristic_defining_codes t1 where t1.dx_code_id=t0.code)
    and not exists (select null from vaers_diagnosticseventrule_heuristic_discarding_codes t1 where t1.dx_code_id=t0.code)
    and not exists (select null from emr_hospital_problem t1 where t1.dx_code_id=t0.code);

/*Use this query to confirm the names of the foreign key constraints
  that refer to static_dx_code in the alter table statements below that drop
  the constraints.
SELECT tc.constraint_name, tc.table_name, ccu.table_name as foreign_table
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY' and ccu.table_name = 'static_dx_code';
*/

ALTER TABLE emr_encounter_dx_code_dx_code DROP CONSTRAINT emr_encounter_dx_codes_dx_code_id_fkey;

ALTER TABLE conf_reportabledx_code DROP CONSTRAINT conf_reportabledx_code_dx_code_id_fkey;

ALTER TABLE emr_problem DROP CONSTRAINT emr_problem_dx_code_id_fkey;

ALTER TABLE emr_hospital_problem DROP CONSTRAINT emr_hospital_problem_dx_code_id_fkey;

ALTER TABLE vaers_diagnosticseventrule_heuristic_defining_codes DROP CONSTRAINT vaers_diagnosticseventrule_heuristic_defining_code_dx_code_id_fkey;

ALTER TABLE vaers_diagnosticseventrule_heuristic_discarding_codes DROP CONSTRAINT vaers_diagnosticseventrule_heuristic_discarding_co_dx_code_id_fkey;

ALTER TABLE static_dx_code DROP CONSTRAINT static_dx_code_pkey;

ALTER TABLE static_dx_code rename to old_dx_code;

-- now run esp syncdb;
-- now run esp loaddata using the new json file

insert into static_dx_code (code, name, longname)
select code, name, longname from old_dx_code t0
where not exists (select null from static_dx_code t1 where t1.code=t0.code);

--now rebuild the foreign keys
ALTER TABLE vaers_diagnosticseventrule_heuristic_discarding_codes
  ADD CONSTRAINT vaers_diagnosticseventrule_heuristic_discarding_co_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE vaers_diagnosticseventrule_heuristic_defining_codes
  ADD CONSTRAINT vaers_diagnosticseventrule_heuristic_defining_code_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE emr_hospital_problem
  ADD CONSTRAINT emr_hospital_problem_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE emr_problem
  ADD CONSTRAINT emr_problem_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE conf_reportabledx_code
  ADD CONSTRAINT conf_reportabledx_code_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE emr_encounter_dx_code_codes
  ADD CONSTRAINT emr_encounter_dx_code_codes_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- don't drop old_dx_code until you've rebuilt the foreign keys.
drop table old_dx_code;

--TODO add type in here for icd10
-- now rebuilt mdphnet tables.  You'll need to disconnect from the ESP schema and connect as MDPHNET
--    UVT_DX
      alter table esp_diagnosis drop constraint esp_diagnosis_dx_fkey;
      DROP TABLE UVT_DX;
      CREATE TABLE UVT_DX AS
      SELECT DISTINCT
             diag.dx item_code,
             dx_code.name item_text
        FROM esp_diagnosis diag
               INNER JOIN public.static_dx_code dx_code ON diag.dx = dx_code.code;
        ALTER TABLE UVT_DX ADD PRIMARY KEY (item_code);

--    UVT_DX_3DIG
      alter table esp_diagnosis drop constraint esp_diagnosis_dx_code_3dig_fkey;
      DROP TABLE UVT_DX_3DIG;
      CREATE TABLE UVT_DX_3DIG AS
      SELECT DISTINCT
             diag.dx_code_3dig item_code,
             dx_code.name item_text
        FROM esp_diagnosis diag
               LEFT OUTER JOIN  (select * from public.static_dx_code
                    where strpos(trim(code),'.')<>3
                       and length(trim(code))>=3 ) dx_code 
               ON diag.dx_code_3dig = REPLACE(dx_code.code, '.', '')
        WHERE diag.dx_code_3dig is not null;
        ALTER TABLE UVT_DX_3DIG ADD PRIMARY KEY (item_code);

--    UVT_DX_4DIG
      alter table esp_diagnosis drop constraint esp_diagnosis_dx_code_4dig_fkey;
      DROP TABLE UVT_DX_4DIG;
      CREATE TABLE UVT_DX_4DIG AS
      SELECT DISTINCT
             diag.dx_code_4dig item_code,
             diag.dx_code_4dig_with_dec item_code_with_dec,
             dx_code.name item_text
        FROM esp_diagnosis diag
               LEFT OUTER JOIN  public.static_dx_code dx_code
               ON diag.dx_code_4dig_with_dec = dx_code.code
        WHERE diag.dx_code_4dig is not null;
        ALTER TABLE UVT_DX_4DIG ADD PRIMARY KEY (item_code_with_dec);
        create index uvt_dx_code_4dig_idx on uvt_dx_4dig (item_code);

--    UVT_DX_5DIG
      alter table esp_diagnosis drop constraint esp_diagnosis_dx_code_5dig_fkey;
      DROP TABLE UVT_DX_5DIG;
      CREATE TABLE UVT_DX_5DIG AS
      SELECT DISTINCT
             diag.dx_code_5dig item_code,
             diag.dx_code_5dig_with_dec item_code_with_dec,
             dx_code.name item_text
        FROM esp_diagnosis diag
               LEFT OUTER JOIN  public.static_dx_code dx_code
               ON diag.dx_code_5dig_with_dec = dx_code.code
        WHERE diag.dx_code_5dig is not null;
        ALTER TABLE UVT_DX_5DIG ADD PRIMARY KEY (item_code_with_dec);
        create index uvt_dx_code_5dig_idx on uvt_dx_5dig (item_code);

      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx) REFERENCES uvt_dx (item_code);
      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx_code_3dig)
                  REFERENCES uvt_dx_3dig (item_code);
      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx_code_4dig_with_dec)
                  REFERENCES uvt_dx_4dig (item_code_with_dec);
      ALTER TABLE esp_diagnosis ADD FOREIGN KEY (dx_code_5dig_with_dec)
                  REFERENCES uvt_dx_5dig (item_code_with_dec);