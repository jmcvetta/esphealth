--
-- OGTT75 Intrapartum
--

select s1.date as case_date, s1.count, 
	pt.id as patient_id, pt.mrn, pt.last_name, pt.first_name, 
	l.date as order_date, l.result_date as result_date, l.native_code, l.native_name, l.result_string, e.name
from (
	select date, patient_id, count(*) 
	from ( 
		select distinct e.date, e.name, e.patient_id from hef_event e 
			inner join hef_pregnancy pg 
				on e.patient_id = pg.patient_id 
				and pg.start_date <= e.date 
				and pg.end_date >= e.date 
			where e.name like 'ogtt75%_pos'
	) s0 
	group by date, patient_id 
) s1 
left join emr_patient pt on pt.id = s1.patient_id 
left join emr_labresult l
	on l.patient_id = s1.patient_id
	and l.result_date = s1.date
	and l.native_code in (
		select native_code 
		from conf_codemap
		where heuristic like 'ogtt75%'
		)
left join hef_event e
	on l.id = e.object_id
	and e.content_type_id = 13
where s1.count > 1;
