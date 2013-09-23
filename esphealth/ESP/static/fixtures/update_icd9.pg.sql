/*Use this query to confirm the names of the foreign key constraints
  that refer to static_icd9 in the alter table statements below that drop
  the constraints.
SELECT tc.constraint_name, tc.table_name, ccu.table_name as foreign_table
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY' and ccu.table_name = 'static_icd9';
*/

ALTER TABLE emr_encounter_icd9_codes DROP CONSTRAINT emr_encounter_icd9_codes_icd9_id_fkey;

ALTER TABLE conf_reportableicd9 DROP CONSTRAINT conf_reportableicd9_icd9_id_fkey;

ALTER TABLE emr_problem DROP CONSTRAINT emr_problem_icd9_id_fkey;

ALTER TABLE emr_hospital_problem DROP CONSTRAINT emr_hospital_problem_icd9_id_fkey;

ALTER TABLE vaers_diagnosticseventrule_heuristic_defining_codes DROP CONSTRAINT vaers_diagnosticseventrule_heuristic_defining_code_icd9_id_fkey;

ALTER TABLE vaers_diagnosticseventrule_heuristic_discarding_codes DROP CONSTRAINT vaers_diagnosticseventrule_heuristic_discarding_co_icd9_id_fkey;

ALTER TABLE static_icd9 DROP CONSTRAINT static_icd9_pkey;

ALTER TABLE static_icd9 rename to old_icd9;

-- now run esp syncdb;
-- now run esp loaddata using the new json file

-- The following delete query is for old IDC tables with 2-digit icd9 procedure codes
/*
delete from old_icd9 
where name not like '%load_epic$'
  and ((code ~ '^\d' and (position('.' in code)=3 or length(code)=2)) 
    or (code ~ '^\D' and (position('.' in code)=4 or length(code)=3)));

*/

insert into static_icd9 (code, name, longname)
select code, name, longname from old_icd9 t0
where not exists (select null from static_icd9 t1 where t1.code=t0.code)

-- don't drop old_icd9 until you've checked the new table.
drop table old_icd9;

--now rebuild the foreign keys
ALTER TABLE vaers_diagnosticseventrule_heuristic_discarding_codes
  ADD CONSTRAINT vaers_diagnosticseventrule_heuristic_discarding_co_icd9_id_fkey FOREIGN KEY (icd9_id)
      REFERENCES static_icd9 (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE vaers_diagnosticseventrule_heuristic_defining_codes
  ADD CONSTRAINT vaers_diagnosticseventrule_heuristic_defining_code_icd9_id_fkey FOREIGN KEY (icd9_id)
      REFERENCES static_icd9 (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE emr_hospital_problem
  ADD CONSTRAINT emr_hospital_problem_icd9_id_fkey FOREIGN KEY (icd9_id)
      REFERENCES static_icd9 (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE emr_problem
  ADD CONSTRAINT emr_problem_icd9_id_fkey FOREIGN KEY (icd9_id)
      REFERENCES static_icd9 (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE conf_reportableicd9
  ADD CONSTRAINT conf_reportableicd9_icd9_id_fkey FOREIGN KEY (icd9_id)
      REFERENCES static_icd9 (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE emr_encounter_icd9_codes
  ADD CONSTRAINT emr_encounter_icd9_codes_icd9_id_fkey FOREIGN KEY (icd9_id)
      REFERENCES static_icd9 (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;


