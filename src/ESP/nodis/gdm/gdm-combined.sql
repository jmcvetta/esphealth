--
-- Combined GDM
--

select combined.date, combined.alogrithm,
	pt.id as patient_id, pt.mrn, pt.last_name, pt.first_name,
	l.native_code, l.native_name, l.result_string,
	e.id as event_id, e.name as event_name

from (
	-- Glucose Fasting
	select distinct e.date, e.patient_id, 'glucose_fasting' as alogrithm
	from hef_event e 
	inner join hef_pregnancy pg 
		on e.patient_id = pg.patient_id 
		and pg.start_date <= e.date 
		and pg.end_date >= e.date 
	where e.name like 'glucose_fasting%'
	and e.name not like '%_pos'
	-- OGTT50
	union
	select distinct e.date, e.patient_id, 'ogtt50_intrapartum' as alogrithm
	from hef_event e 
	inner join hef_pregnancy pg 
		on e.patient_id = pg.patient_id 
		and pg.start_date <= e.date 
		and pg.end_date >= e.date 
	where e.name like 'ogtt50%'
	and e.name not like '%_pos'
	-- OGTT75 Intrapartum
	union
	select s1.date, s1.patient_id, 'ogtt75_intrapartum' as alogrithm
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
	where s1.count > 1
	-- OGTT75 Postpartum
	union 
	select distinct e.date, e.patient_id, 'ogtt75_postpartum' as alogrithm
	from hef_event e 
	inner join emr_patient pt
		on e.patient_id = pt.id
		and pt.gender = 'F'
	left join hef_pregnancy pg 
		on e.patient_id = pg.patient_id 
		and pg.start_date <= e.date 
		and pg.end_date >= e.date 
	where pg.id is null
		and e.name like 'ogtt75%'
		and e.name not like '%_pos'
	-- OGTT100 Intrapartum
	union
	select s1.date, s1.patient_id, 'ogtt100_intrapartum' as alogrithm
	from (
		select date, patient_id, count(*) 
		from (
			select distinct e.date, e.name, e.patient_id 
			from hef_event e 
			inner join hef_pregnancy pg 
				on e.patient_id = pg.patient_id 
				and pg.start_date <= e.date 
				and pg.end_date >= e.date 
			where e.name like 'ogtt100%_pos' 
		) s0 
		group by date, patient_id 
	) s1
	where s1.count > 1
) combined
join emr_patient pt
	on combined.patient_id = pt.id
left join emr_labresult l
	on l.patient_id = combined.patient_id
	and l.date = combined.date
	and l.native_code in (
		select native_code 
		from conf_codemap
		where heuristic like 'ogtt%'
		or heuristic like 'glucose-fasting%'
	)
left join hef_event e
	on l.id = e.object_id
	and e.content_type_id = 13
order by pt.mrn, combined.date