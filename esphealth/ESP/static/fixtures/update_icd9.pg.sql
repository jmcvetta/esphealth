-- The following delete query cleans up static_icd9 of any unreferenced codes
delete from static_icd9 t0
where not exists (select null from emr_problem t1 where t1.icd9_id=t0.code)
    and not exists (select null from emr_encounter_icd9_codes t1 where t1.icd9_id=t0.code)
    and not exists (select null from conf_reportableicd9 t1 where t1.icd9_id=t0.code)
    and not exists (select null from vaers_diagnosticseventrule_heuristic_defining_codes t1 where t1.icd9_id=t0.code)
    and not exists (select null from vaers_diagnosticseventrule_heuristic_discarding_codes t1 where t1.icd9_id=t0.code)
    and not exists (select null from emr_hospital_problem t1 where t1.icd9_id=t0.code);


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

insert into static_icd9 (code, name, longname)
select code, name, longname from old_icd9 t0
where not exists (select null from static_icd9 t1 where t1.code=t0.code)

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

-- don't drop old_icd9 until you've rebuilt the foreign keys.
drop table old_icd9;
