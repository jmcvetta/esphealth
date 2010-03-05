--
-- GDM based on ICD9 or lancets and test strips
--

select e.date as event_date, e.name as event, e.patient_id,
	pt.mrn, pt.last_name, pt.first_name, 
	pg.start_date as preg_start, pg.end_date as preg_end,
	enc.edc
from hef_event e 
inner join hef_pregnancy pg 
	on e.patient_id = pg.patient_id 
	and pg.start_date <= e.date 
	and pg.end_date >= e.date 
inner join emr_patient pt
	on e.patient_id = pt.id
left join emr_encounter enc
	on e.object_id = enc.id
	and e.content_type_id = 15
where e.name in ('gdm_diagnosis', 'lancets_rx', 'test_strips_rx')
	