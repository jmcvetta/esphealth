--
-- Pregnancy Inference Analysis
--

select distinct pg.patient_id, pg.start_date, pg.end_date
from hef_pregnancy pg
left join emr_encounter e
	on e.patient_id = pg.patient_id
	and pg.start_date >= e.edc - interval '280 days'
	and pg.end_date <= e.edc + interval '6 months'
	and e.id is null
order by pg.patient_id, pg.start_date