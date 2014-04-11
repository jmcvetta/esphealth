 ALTER TABLE  conf_reportabledx_code
 ADD CONSTRAINT conf_reportabledx_code_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (combotypecode);

ALTER TABLE  emr_encounter_icd9_codes 
 ADD  CONSTRAINT emr_encounter_dx_codes_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (combotypecode) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

 ALTER TABLE emr_problem 
 ADD CONSTRAINT emr_problem_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (combotypecode);

 ALTER TABLE emr_hospital_problem
 ADD CONSTRAINT emr_hospital_problem_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (combotypecode);

ALTER TABLE   vaers_diagnosticseventrule_heuristic_defining_codes
 ADD CONSTRAINT vaers_diagnosticseventrule_heuristic_defining_c_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (combotypecode) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE  vaers_diagnosticseventrule_heuristic_discarding_codes 
 ADD CONSTRAINT vaers_diagnosticseventrule_heuristic_discarding_dx_code_id_fkey FOREIGN KEY (dx_code_id)
      REFERENCES static_dx_code (combotypecode) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
 
