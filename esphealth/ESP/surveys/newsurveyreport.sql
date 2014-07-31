drop TABLE if exists ContinuousVariables;

CREATE TEMPORARY TABLE ContinuousVariables(
    Question   VARCHAR(200),
    NoOfRespondents INTEGER,
    NoOfEHRRespondents INTEGER,
    SelfReportMean  DECIMAL(7,2),
    SelfReportSD  DECIMAL(7,2),
    EHRReportMean  DECIMAL(7,2),
    EHRReportSD  DECIMAL(7,2)
);
      
--ethnicity survey vs ehr no/yes
INSERT INTO ContinuousVariables(
            Question  ,   NoOfRespondents ,SelfReportMean ,SelfReportSD )
     select question, count(mrn) as "No. of Respondents",
Round( avg(response_float)::numeric,2) as "Self-Report Mean",round( stddev(response_float)::numeric,2) as  "+- SD"
from emr_surveyresponse where  response_float is not null and (question <> 'inches')
group by question ;

update ContinuousVariables set NoOfEHRRespondents = 
(select count(*) from emr_patient where date_of_birth is not null and mrn in (select distinct (mrn) from emr_surveyresponse ))
 where Question ='What is your age?';

update ContinuousVariables set EHRReportMean=
(select round(avg(date_part('year',age(emr_surveyresponse.date, date_of_birth)) )::numeric,2) 
from emr_patient , emr_surveyresponse
where emr_patient.mrn = emr_surveyresponse.mrn and question ='What is your age?'),
EHRReportSD=(select round(stddev(date_part('year',age(emr_surveyresponse.date, date_of_birth)) )::numeric,2) 
from emr_patient , emr_surveyresponse
where emr_patient.mrn = emr_surveyresponse.mrn and question ='What is your age?')
where Question ='What is your age?';

-- self height reponses, mean and sd, add responses of feet and inches.
update ContinuousVariables set NoOfRespondents = (select  count(mrn) as "No. of Respondents"
from emr_surveyresponse where  response_float is not null and question ='What is your current height in Feet and Inches?')+
(select  count(mrn) as "No. of Respondents"
from emr_surveyresponse r1 where  r1.response_float is not null and r1.question ='inches' and 
(select count(*) from emr_surveyresponse r2 where  r2.response_float is null and 
 r1.response_float is not null and r1.mrn= r2.mrn and r2.question ='What is your current height in Feet and Inches?')>0)
 where Question ='What is your current height in Feet and Inches?';

update ContinuousVariables set NoOfEHRRespondents = (select count(distinct(emr_encounter.patient_id)) from emr_patient , emr_encounter
where emr_patient.mrn in (select distinct (emr_surveyresponse.mrn) from emr_surveyresponse ) and emr_encounter.patient_id = emr_patient.id and height is not null )
where Question ='What is your current height in Feet and Inches?';

update ContinuousVariables set SelfReportMean = (select Round( avg(r1.response_float*30.48 + (select  r2.response_float*2.54
from  emr_surveyresponse r2
where r2.question = 'inches' and r2.response_float is not null and r1.mrn= r2.mrn ))::numeric,2) 
from emr_surveyresponse r1 where r1.question = 'What is your current height in Feet and Inches?'   )
where Question ='What is your current height in Feet and Inches?';

update ContinuousVariables set SelfReportSD = (select Round( stddev(r1.response_float*30.48 + (select  r2.response_float*2.54
from  emr_surveyresponse r2
where r2.question = 'inches' and r2.response_float is not null and r1.mrn= r2.mrn ))::numeric,2) 
from emr_surveyresponse r1 where r1.question = 'What is your current height in Feet and Inches?' )
where Question ='What is your current height in Feet and Inches?';

--ehr mean height and sd
update ContinuousVariables set EHRReportMean=
(select round(avg((select emr_encounter.height from emr_encounter where 
  emr_encounter.patient_id = emr_patient.id and emr_encounter.height is not null
order by emr_encounter.date desc limit 1))::numeric,2) as "EHR height mean"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse)  ),
EHRReportSD=(select round(stddev((select emr_encounter.height from emr_encounter
where emr_encounter.patient_id = emr_patient.id and emr_encounter.height is not null
order by emr_encounter.date desc limit 1))::numeric, 2) as "+- SD"
from emr_patient where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse))
where Question ='What is your current height in Feet and Inches?';

update ContinuousVariables set NoOfEHRRespondents = (select count(distinct(emr_encounter.patient_id)) from emr_patient , emr_encounter
where emr_patient.mrn in (select distinct (emr_surveyresponse.mrn) from emr_surveyresponse ) and emr_encounter.patient_id = emr_patient.id and weight is not null )
where Question ='What is your current weight in pounds?';

--mean weight and sd
update ContinuousVariables set EHRReportMean=
(select round(avg((select emr_encounter.weight from emr_encounter where 
  emr_encounter.patient_id = emr_patient.id and emr_encounter.weight is not null
order by emr_encounter.date desc limit 1))::numeric,2) as "EHR weight mean"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse)  ),
EHRReportSD=(select round(stddev((select emr_encounter.weight from emr_encounter
where emr_encounter.patient_id = emr_patient.id and emr_encounter.weight is not null
order by emr_encounter.date desc limit 1))::numeric, 2) as "+- SD"
from emr_patient where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse))
where Question ='What is your current weight in pounds?';

update ContinuousVariables set NoOfEHRRespondents = (select count(distinct(emr_encounter.patient_id)) from emr_patient , emr_encounter
where emr_patient.mrn in (select distinct (emr_surveyresponse.mrn) from emr_surveyresponse ) and emr_encounter.patient_id = emr_patient.id and bp_diastolic is not null )
where Question ='What is your last diastolic blood pressure?';

--mean diastolic and sd
update ContinuousVariables set EHRReportMean= (select round(avg((select  emr_encounter.bp_diastolic 
from  emr_encounter
where emr_encounter.patient_id = emr_patient.id and emr_encounter.bp_diastolic is not null 
order by emr_encounter.date desc limit 1))::numeric,2) as "EHR diastolic Mean"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse)  ),
EHRReportSD=(select round(stddev((select  emr_encounter.bp_diastolic 
from  emr_encounter
where emr_encounter.patient_id = emr_patient.id and emr_encounter.bp_diastolic is not null 
order by emr_encounter.date desc limit 1))::numeric,2) as "+- SD"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse))
where Question ='What is your last diastolic blood pressure?';

update ContinuousVariables set NoOfEHRRespondents = (select count(distinct(emr_encounter.patient_id)) from emr_patient , emr_encounter
where emr_patient.mrn in (select distinct (emr_surveyresponse.mrn) from emr_surveyresponse ) and emr_encounter.patient_id = emr_patient.id and bp_systolic is not null )
where Question ='What was your systolic blood pressure the last time it was measured by your doctor?';

--mean systolic and sd
update ContinuousVariables set EHRReportMean= (select round(avg((select  emr_encounter.bp_systolic 
from  emr_encounter
where emr_encounter.patient_id = emr_patient.id and emr_encounter.bp_systolic is not null 
order by emr_encounter.date desc limit 1))::numeric,2) as "EHR systolic Mean"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse) ),
EHRReportSD=(select round(stddev((select  emr_encounter.bp_systolic 
from  emr_encounter
where emr_encounter.patient_id = emr_patient.id and emr_encounter.bp_systolic is not null 
order by emr_encounter.date desc limit 1))::numeric,2) as "+- SD"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse))
where Question ='What was your systolic blood pressure the last time it was measured by your doctor?';

update ContinuousVariables set NoOfEHRRespondents = (select  count(distinct(emr_labresult.patient_id))   from emr_labresult , emr_patient 
where native_code in (select native_code from conf_labtestmap where test_name ='a1c')
and emr_labresult.patient_id = emr_patient.id and result_float is not null 
and emr_patient.mrn in (select distinct (emr_surveyresponse.mrn) from emr_surveyresponse))
where Question ='what was your most recent hemoglobin A1C value?';

--mean a1c and sd
update ContinuousVariables set EHRReportMean= (select round(avg((select result_float 
from emr_labresult
where native_code in (select native_code from conf_labtestmap where test_name ='a1c')
and emr_labresult.patient_id = emr_patient.id 
order by emr_labresult.date desc limit 1))::numeric,2) as "EHR a1c mean"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse)),
EHRReportSD=(select round(stddev((select result_float 
from emr_labresult
where native_code in (select native_code from conf_labtestmap where test_name ='a1c')
and emr_labresult.patient_id = emr_patient.id 
order by emr_labresult.date desc limit 1))::numeric,2) as "+- SD"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse))
where Question ='what was your most recent hemoglobin A1C value?';

update ContinuousVariables set NoOfEHRRespondents = (select  count(distinct(emr_labresult.patient_id))   from emr_labresult , emr_patient 
where native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl')
and emr_labresult.patient_id = emr_patient.id and result_float is not null 
and emr_patient.mrn in (select distinct(emr_surveyresponse.mrn) from emr_surveyresponse))
where Question ='What was your last LDL level?';

--mean ldl and sd
update ContinuousVariables set EHRReportMean= (select round(avg((select result_float 
from emr_labresult
where native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl')
and emr_labresult.patient_id = emr_patient.id 
order by emr_labresult.date desc limit 1))::numeric,2) as "EHR ldl mean"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse)),
EHRReportSD=( select round(stddev((select result_float 
from emr_labresult
where native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl')
and emr_labresult.patient_id = emr_patient.id 
order by emr_labresult.date desc limit 1))::numeric,2) as "+- SD"
from emr_patient 
where emr_patient.mrn in (select emr_surveyresponse.mrn from emr_surveyresponse))
where Question ='What was your last LDL level?'; 

update ContinuousVariables set NoOfRespondents =0 where NoOfRespondents is null;
update ContinuousVariables set NoOfEHRRespondents=0  where NoOfEHRRespondents is null;
update ContinuousVariables set SelfReportMean=0   where SelfReportMean is null;
update ContinuousVariables set SelfReportSD =0  where SelfReportSD is null;
update ContinuousVariables set EHRReportMean=0   where EHRReportMean is null;
update ContinuousVariables set EHRReportSD=0  where EHRReportSD is null;

drop TABLE if exists CategoricalVariables;

CREATE TEMPORARY TABLE CategoricalVariables(
    RaceEthnicity   VARCHAR(20),
    SelfReportYes INTEGER,
    SelfReportNo  INTEGER,
    EHRYes  INTEGER,
    EHRNo  INTEGER,
    PtYesEHRYes INTEGER,
    PtYesEHRNo INTEGER,
    PtNoEHRYes INTEGER,
    PtNoEHRNo INTEGER
);

INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Black');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Caucasian');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Asian');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Other');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Hispanic');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Indian');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Nat American');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Alaskan');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Native Hawai');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Unknown');
INSERT INTO CategoricalVariables ( RaceEthnicity) values ('Patient Decl');

--etnicity selfreport yes
update CategoricalVariables set SelfReportYes =( select count(*) 
  from emr_surveyresponse b
where b.question='What is your race/ethnicity?' and (
(response_choice='B' and raceethnicity=  'Black' ) or
(response_choice='W' and raceethnicity=   'Caucasian') or
(response_choice='A' and raceethnicity=   'Asian') or
(response_choice='O' and raceethnicity=   'Other') or
(response_choice='H' and raceethnicity=   'Hispanic') or
(response_choice='I' and raceethnicity=   'Indian') or
(response_choice='NA' and raceethnicity=   'Nat American') or
(response_choice='Al' and raceethnicity=   'Alaskan') or
(response_choice='NH' and raceethnicity=   'Native Hawai') or
(response_choice='PD' and raceethnicity=   'Patient Decl')
) group by response_choice);

--etnicity selfreport no
update CategoricalVariables set SelfReportNo =( select (select count(*) from emr_surveyresponse a
where a.question=b.question)- count(*) 
  from emr_surveyresponse b
where b.question='What is your race/ethnicity?' and (
(response_choice='B' and raceethnicity=  'Black' ) or
(response_choice='W' and raceethnicity=   'Caucasian') or
(response_choice='A' and raceethnicity=   'Asian') or
(response_choice='O' and raceethnicity=   'Other') or
(response_choice='H' and raceethnicity=   'Hispanic') or
(response_choice='I' and raceethnicity=   'Indian') or
(response_choice='NA' and raceethnicity=   'Nat American') or
(response_choice='Al' and raceethnicity=   'Alaskan') or
(response_choice='NH' and raceethnicity=   'Native Hawai') or
(response_choice='PD' and raceethnicity=   'Patient Decl')
) group by response_choice, b.question);

--ehr yes 
update CategoricalVariables set ehryes =( select count(*) 
  from emr_patient p
where 
p.mrn in (select mrn from emr_surveyresponse where question='What is your race/ethnicity?' ) and  (
( ( upper(race) = upper('African')or upper(race) = upper('African-American')) and raceethnicity=  'Black' ) or
(  upper(race) = upper('White') and raceethnicity=   'Caucasian') or
( ( upper(race) = upper('Multiracial')) and raceethnicity=   'Other') or
( (upper(race) = upper('Native American')) and raceethnicity=   'Nat American') or
( ( upper(race) = upper('AMERICAN INDIAN/ALASKAN NATIVE')) and raceethnicity=   'Alaskan') or
( ( upper(race) = upper('PACIFIC ISLANDER/HAWAIIAN') or upper(race) = upper('NATIVE HAWAIIAN')) and raceethnicity=   'Native Hawai') or
(upper(race) = upper(raceethnicity) ))
 group by raceethnicity);

--ehr no 
update CategoricalVariables set ehrno = (select (select count(*) from emr_patient where mrn in 
   (select mrn from emr_surveyresponse where question='What is your race/ethnicity?' ))
        - count(*) as "EHR No"
from emr_patient b 
where b.mrn in (select mrn from emr_surveyresponse where question='What is your race/ethnicity?') 
and ( upper(race) = upper(raceethnicity) or 
( (  upper(race) = upper('African')or upper(race) = upper('African-American')) and raceethnicity=  'Black' ) or
( (  upper(race) = upper('White')) and raceethnicity=   'Caucasian') or
( (  upper(race) = upper('Multiracial')) and raceethnicity=   'Other') or
( ( upper(race) = upper('Native American')) and raceethnicity=   'Nat American') or
( (  upper(race) = upper('AMERICAN INDIAN/ALASKAN NATIVE')) and raceethnicity=   'Alaskan') or
( (  upper(race) = upper('PACIFIC ISLANDER/HAWAIIAN') or upper(race) = upper('NATIVE HAWAIIAN')) and raceethnicity=   'Native Hawai') 
) group by raceethnicity);

--ethnicity: survey vs ehr yes/yes
update CategoricalVariables set ptyesehryes = (
select count(*) as "Pt yes / EHR yes" from emr_surveyresponse s, emr_patient p 
       where p.mrn=s.mrn and question='What is your race/ethnicity?'  and ( 
         ((upper(race) = upper(raceethnicity) or upper(race) = upper('African')or upper(race) = upper('African-American')) and response_choice='B' and raceethnicity=   'Black') or
	 ((upper(race) = upper(raceethnicity) or upper(race) = upper('White') ) and  response_choice='W' and raceethnicity=   'Caucasian') or 
	 ((upper(race) = upper(raceethnicity) or upper(race) = upper('Multiracial')) and response_choice='O' and raceethnicity=   'Other') or 
	 (response_choice='Al' and raceethnicity=   'Alaskan' and (upper(race) = upper(raceethnicity) or upper(race) = upper('AMERICAN INDIAN/ALASKAN NATIVE')) ) or
	(response_choice='NH' and raceethnicity=   'Native Hawai' and (upper(race) = upper(raceethnicity) or upper(race) = upper('NATIVE HAWAIIAN') or upper(race) = upper('PACIFIC ISLANDER/HAWAIIAN'))  ) or
	(response_choice='NA' and raceethnicity=   'Nat American' and (upper(race) = upper(raceethnicity) or upper(race) = upper('Native American'))) or
	(response_choice='I' and upper(race) = upper(raceethnicity) and raceethnicity=   'Indian') or
	(response_choice='PD' and upper(race) = upper(raceethnicity) and raceethnicity=   'Patient Decl') or
	(upper(race) = upper(raceethnicity) and response_choice='H' and raceethnicity=   'Hispanic') or
	(upper(race) = upper(raceethnicity) and response_choice='A' and raceethnicity=   'Asian')  ) group by raceethnicity);

--ethnicity survey vs ehr yes/no 
update CategoricalVariables set ptyesehrno = (
select count(*) as "Pt yes / EHR no" from emr_surveyresponse s, emr_patient p 
       where p.mrn=s.mrn and question='What is your race/ethnicity?' 
       and  (((upper(race) <> upper(raceethnicity) and upper(race) <> upper('African') and upper(race)<> upper('African-American') ) and response_choice='B' and raceethnicity=   'Black') or
	 ((upper(race) <> upper('White') and  upper(race) <> upper(raceethnicity)) and  response_choice='W' and raceethnicity=   'Caucasian') or 
	 (upper(race) <> upper(raceethnicity) and response_choice='A' and raceethnicity=   'Asian') or 
	 ( (upper(race) <> upper(raceethnicity) and upper(race) <> upper('Multiracial')) and response_choice='O' and raceethnicity=   'Other') or 
	 (upper(race) <> upper(raceethnicity) and response_choice='H' and raceethnicity=   'Hispanic')or 
	 (response_choice='I' and upper(race) <> upper(raceethnicity) and raceethnicity=   'Indian') or
	(response_choice='NA' and raceethnicity=   'Nat American' and (upper(race) <> upper(raceethnicity) and upper(race) <> upper('Native American'))) or
	(response_choice='Al'and raceethnicity=   'Alaskan' and (upper(race) <> upper(raceethnicity) and upper(race) <> upper('AMERICAN INDIAN/ALASKAN NATIVE')) ) or
	(response_choice='NH' and raceethnicity=   'Native Hawai' and (upper(race) <> upper(raceethnicity) and upper(race) <> upper('NATIVE HAWAIIAN') and upper(race) <> upper('PACIFIC ISLANDER/HAWAIIAN')) ) or
	(response_choice='PD' and raceethnicity=   'Patient Decl' and upper(race) <> upper(raceethnicity))  ) group by raceethnicity);
	 
--ethnicity survey vs ehr no/yes
update CategoricalVariables set ptnoehryes = (
select  count(*) as "Pt no/ EHR yes" from emr_surveyresponse s, emr_patient p 
       where p.mrn=s.mrn and question='What is your race/ethnicity?' 
       and  (((upper(race) = upper(raceethnicity) or  upper(race) = upper('African') or upper(race)= upper('African-American') ) and response_choice<>'B' and raceethnicity=   'Black') or
	 ((upper(race) = upper('White') or  upper(race) = upper(raceethnicity)) and  response_choice<>'W' and raceethnicity=   'Caucasian') or 
	 (upper(race) = upper(raceethnicity) and response_choice<>'A' and raceethnicity=   'Asian') or 
	 ( (upper(race) = upper(raceethnicity) or upper(race) = upper('Multiracial')) and response_choice<>'O' and raceethnicity=   'Other') or 
	 (upper(race) = upper(raceethnicity) and response_choice<>'H' and raceethnicity=   'Hispanic')or 
	 (response_choice<>'I' and upper(race) = upper(raceethnicity) and raceethnicity=   'Indian') or
	(response_choice<>'NA' and raceethnicity=   'Nat American' and (upper(race) = upper(raceethnicity) or upper(race) = upper('Native American'))) or
	(response_choice<>'Al'and raceethnicity=   'Alaskan' and (upper(race) = upper(raceethnicity) or upper(race) = upper('AMERICAN INDIAN/ALASKAN NATIVE')) ) or
	(response_choice<>'NH' and raceethnicity=   'Native Hawai' and (upper(race) = upper(raceethnicity) or upper(race) = upper('NATIVE HAWAIIAN') or upper(race) = upper('PACIFIC ISLANDER/HAWAIIAN')) ) or
	(response_choice<>'PD' and raceethnicity=   'Patient Decl' and upper(race) = upper(raceethnicity))  ) group by raceethnicity);

--ethnicity survey vs ehr no/no  
update CategoricalVariables set ptnoehrno = (
select count(*) as "Pt no / EHR no" from emr_surveyresponse s, emr_patient p 
        where p.mrn=s.mrn and question='What is your race/ethnicity?' 
       and  (((upper(race) <> upper(raceethnicity) and upper(race) <> upper('African') and upper(race)<> upper('African-American') ) and response_choice<>'B' and raceethnicity=   'Black') or
	 ((upper(race) <> upper('White') and  upper(race) <> upper(raceethnicity)) and  response_choice<>'W' and raceethnicity=   'Caucasian') or 
	 (upper(race) <> upper(raceethnicity) and response_choice<>'A' and raceethnicity=   'Asian') or 
	 ( (upper(race) <> upper(raceethnicity) and upper(race) <> upper('Multiracial')) and response_choice<>'O' and raceethnicity=   'Other') or 
	 (upper(race) <> upper(raceethnicity) and response_choice<>'H' and raceethnicity=   'Hispanic')or 
	 (response_choice<>'I' and upper(race) <> upper(raceethnicity) and raceethnicity=   'Indian') or
	(response_choice<>'NA' and raceethnicity=   'Nat American' and (upper(race) <> upper(raceethnicity) and upper(race) <> upper('Native American'))) or
	(response_choice<>'Al'and raceethnicity=   'Alaskan' and (upper(race) <> upper(raceethnicity) and upper(race) <> upper('AMERICAN INDIAN/ALASKAN NATIVE')) ) or
	(response_choice<>'NH' and raceethnicity=   'Native Hawai' and (upper(race) <> upper(raceethnicity) and upper(race) <> upper('NATIVE HAWAIIAN') and upper(race) <> upper('PACIFIC ISLANDER/HAWAIIAN')) ) or
	(response_choice<>'PD' and raceethnicity=   'Patient Decl' and upper(race) <> upper(raceethnicity))  ) group by raceethnicity);

--TOTALS
INSERT INTO CategoricalVariables  (RaceEthnicity  , SelfReportYes ,SelfReportNo  ,
    EHRYes ,  EHRNo ,PtYesEHRYes , PtYesEHRNo , PtNoEHRYes , PtNoEHRNo )
 select 'TOTAL', sum(selfreportyes), sum(selfreportno),sum(ehryes),sum(ehrno), sum(ptyesehryes),
  sum(ptyesehrno), sum(ptnoehryes), sum(ptnoehrno) from CategoricalVariables;

update CategoricalVariables set SelfReportYes=0  where SelfReportYes is null;
update CategoricalVariables set SelfReportNo=0  where SelfReportNo is null;
update CategoricalVariables set EHRYes=0  where EHRYes is null;
update CategoricalVariables set EHRNo=0  where EHRNo is null;
update CategoricalVariables set PtYesEHRYes=0  where PtYesEHRYes is null;
update CategoricalVariables set PtYesEHRNo=0  where PtYesEHRNo is null;
update CategoricalVariables set PtNoEHRYes=0  where PtNoEHRYes is null;
update CategoricalVariables set PtNoEHRNo=0  where PtNoEHRNo is null;
 
--yes/no/unsure questions
drop TABLE if exists YesNoUnsureQuestions;

CREATE TEMPORARY TABLE YesNoUnsureQuestions(
    Question   VARCHAR(200),
    NoOfRespondents INTEGER,
    PtYes INTEGER,
    PTNo  INTEGER,
    PTUnsure  INTEGER,
    EHRYes  INTEGER,
    EHRNo  INTEGER,
    PtYesEHRYes INTEGER,
    PtYesEHRNo INTEGER,
    PtNoEHRYes INTEGER,
    PtNoEHRNo INTEGER,
    PtUnsureEHRYes INTEGER,
    PtUnsureEHRNo INTEGER
);

INSERT INTO YesNoUnsureQuestions ( Question) values ('Male gender');
INSERT INTO YesNoUnsureQuestions ( Question) values ('Do you have diabetes?');
INSERT INTO YesNoUnsureQuestions ( Question) values ('Have you ever had your hemoglobin A1C level checked?');
INSERT INTO YesNoUnsureQuestions ( Question) values ('Have you ever been diagnosed with high blood pressure?');
INSERT INTO YesNoUnsureQuestions ( Question) values ('Are you currently being prescribed medications for high blood pressure?');
INSERT INTO YesNoUnsureQuestions ( Question) values ('Have you ever had your LDL level checked?');
INSERT INTO YesNoUnsureQuestions ( Question) values ('Do you have a history of hyperlipidemia or elevated cholesterol?');
INSERT INTO YesNoUnsureQuestions ( Question) values ('Are you currently being prescribed medications for high cholesterol?');

--Male responsonses
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question='What is your gender?' )
where question = 'Male gender';

--male pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question='What is your gender?' and response_choice = 'M' )
where question = 'Male gender';

--male pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question='What is your gender?' and response_choice <> 'M' )
where question = 'Male gender';

--NA male pt unsure 
update YesNoUnsureQuestions set PtUnsure =( select 0  )
where question = 'Male gender';

--male ehr yes 
update YesNoUnsureQuestions set ehryes =( select count(*) 
  from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse where 
question='What is your gender?' ) and  gender = 'M')
where question = 'Male gender';

--male ehr no 
update YesNoUnsureQuestions set ehrno =( select count(*) 
  from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse where 
question='What is your gender?' ) and  gender <> 'M')
where question = 'Male gender';

--male: survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes = (
select count(*) as "Pt yes / EHR yes" from emr_surveyresponse s, emr_patient p 
       where p.mrn=s.mrn and question='What is your gender?' 
         and (response_choice='M' and gender=   'M') )
where question = 'Male gender';

--male: survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno = (
select count(*) as "Pt yes / EHR no" from emr_surveyresponse s, emr_patient p 
       where p.mrn=s.mrn and question='What is your gender?' 
         and (response_choice='M' and gender<>   'M') )
where question = 'Male gender';

--male: survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes = (
select count(*) as "Pt no / EHR yes" from emr_surveyresponse s, emr_patient p 
       where p.mrn=s.mrn and question='What is your gender?' 
         and (response_choice<>'M' and gender= 'M') )
where question = 'Male gender';

--male: survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno = (
select count(*) as "Pt no / EHR no" from emr_surveyresponse s, emr_patient p 
       where p.mrn=s.mrn and question='What is your gender?' 
         and (response_choice<>'M' and gender<> 'M') )
where question = 'Male gender';

-- NA male  pt unsure ehr yes ... 
update YesNoUnsureQuestions set ptunsureehryes =( select 0  )
where question = 'Male gender';

-- NA male  pt unsure ehr no ... 
update YesNoUnsureQuestions set ptunsureehrno =( select 0  )
where question = 'Male gender';

-- hypertension norespondents 
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question )
where question = 'Have you ever been diagnosed with high blood pressure?';

-- a1c norespondents 
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question )
where question = 'Have you ever had your hemoglobin A1C level checked?';

-- ldl norespondents 
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question )
where question = 'Have you ever had your LDL level checked?';

-- diabetes norespondents 
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question )
where question = 'Do you have diabetes?';

-- meds for hyperlipidemia norespondents 
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question )
where question = 'Are you currently being prescribed medications for high cholesterol?';

-- hyperlipidemia norespondents 
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question )
where question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

-- meds for hypertension norespondents 
update YesNoUnsureQuestions set NoOfRespondents =( select count(*) 
  from emr_surveyresponse b
where b.question= YesNoUnsureQuestions.question )
where question = 'Are you currently being prescribed medications for high blood pressure?';

--hypertension pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'Y' )
where question = 'Have you ever been diagnosed with high blood pressure?';

--hypertension pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'N' )
where question = 'Have you ever been diagnosed with high blood pressure?';

--hypertension pt unsure
update YesNoUnsureQuestions set PtUnsure =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'U' )
where question = 'Have you ever been diagnosed with high blood pressure?';

--meds for hypertension pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'Y' )
where question = 'Are you currently being prescribed medications for high blood pressure?';

--meds for hypertension pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'N' )
where question = 'Are you currently being prescribed medications for high blood pressure?';

--meds for hypertension pt unsure
update YesNoUnsureQuestions set PtUnsure =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'U' )
where question = 'Are you currently being prescribed medications for high blood pressure?';

--hyperlipidemia pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'Y' )
where question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--hyperlipidemia pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'N' )
where question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--hyperlipidemia pt unsure
update YesNoUnsureQuestions set PtUnsure =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'U' )
where question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--meds for hyperlipidemia pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'Y' )
where question = 'Are you currently being prescribed medications for high cholesterol?';

--meds for hyperlipidemia pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'N' )
where question = 'Are you currently being prescribed medications for high cholesterol?';

--meds for hyperlipidemia pt unsure
update YesNoUnsureQuestions set PtUnsure =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'U' )
where question = 'Are you currently being prescribed medications for high cholesterol?';

--diabetes pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'Y' )
where question = 'Do you have diabetes?';

--diabetes pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'N' )
where question = 'Do you have diabetes?';

--diabetes pt unsure
update YesNoUnsureQuestions set PtUnsure =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'U' )
where question = 'Do you have diabetes?';

--a1c pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'Y' )
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'N' )
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c pt unsure
update YesNoUnsureQuestions set PtUnsure =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'U' )
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c ehr yes 
update YesNoUnsureQuestions set ehryes =( select count(distinct(p.mrn)) from emr_patient p, emr_labresult
where p.mrn in (select distinct(b.mrn) from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='a1c'))
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c ehr no
update YesNoUnsureQuestions set ehrno =(select count(distinct(pp.mrn)) from emr_patient pp
where pp.mrn in (select distinct(b.mrn) from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
(select count(*) from emr_patient p, emr_labresult
where p.mrn = pp.mrn and emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='a1c') )=0)
where question = 'Have you ever had your hemoglobin A1C level checked?';

--hypertension ehr yes
update YesNoUnsureQuestions set ehryes =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select distinct(b.mrn) from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and (
(select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%' )>0 or 
(select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )>=2))
where question = 'Have you ever been diagnosed with high blood pressure?';

--hyperlipedimia ehr yes  
update YesNoUnsureQuestions set ehryes =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select distinct(b.mrn) from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and (
(select count(*) from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float > 160 )> 0 or (select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0))
where question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--meds for hypertension ehr yes
update YesNoUnsureQuestions set ehryes =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select distinct(b.mrn) from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
(select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%' )>0 )
where question = 'Are you currently being prescribed medications for high blood pressure?';

--ldl pt yes
update YesNoUnsureQuestions set PtYes =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'Y' )
where question = 'Have you ever had your LDL level checked?';

--ldl pt no
update YesNoUnsureQuestions set PtNo =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'N' )
where question = 'Have you ever had your LDL level checked?';

--ldl pt unsure
update YesNoUnsureQuestions set PtUnsure =( select count(*) 
  from emr_surveyresponse b
where b.question=YesNoUnsureQuestions.question and response_choice = 'U' )
where question = 'Have you ever had your LDL level checked?';

--ldl ehr yes 
update YesNoUnsureQuestions set ehryes =( select count(distinct(p.mrn)) from emr_patient p, emr_labresult
where p.mrn in (select distinct(b.mrn) from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl'))
where question = 'Have you ever had your LDL level checked?';

--ldl ehr no
update YesNoUnsureQuestions set ehrno =(select count(distinct(pp.mrn)) from emr_patient pp
where pp.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
(select count(distinct(p.mrn)) from emr_patient p, emr_labresult
where p.mrn = pp.mrn and emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') )=0)
where question = 'Have you ever had your LDL level checked?';

--meds for hyperlipedimia ehr yes  
update YesNoUnsureQuestions set ehryes =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
((select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0))
where question = 'Are you currently being prescribed medications for high cholesterol?';

--diabetes ehr yes  
update YesNoUnsureQuestions set ehryes =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
((select count(*) from  nodis_case c
 where c.patient_id = p.id and 
condition in ('diabetes:type-2'  , 'diabetes:type-1', 'diabetes:gestational'  , 'diabetes:prediabetes'))>0))
where question = 'Do you have diabetes?';

--hypertension ehr no
update YesNoUnsureQuestions set ehrno =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
(select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%' )=0 and 
(select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )<2)
where question = 'Have you ever been diagnosed with high blood pressure?';

--hyperlipedimia ehr no  
update YesNoUnsureQuestions set ehrno =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
(select count(*) from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float >160 )=0 and (select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0)
where question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--meds for hypertension ehr no
update YesNoUnsureQuestions set ehrno =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
(select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%' )=0 )
where question = 'Are you currently being prescribed medications for high blood pressure?';

--meds for hyperlipedimia ehr no  
update YesNoUnsureQuestions set ehrno =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
((select count(*) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0))
where question = 'Are you currently being prescribed medications for high cholesterol?';

--diabetes ehr no  
update YesNoUnsureQuestions set ehrno =( select count(distinct(p.mrn)) from emr_patient p
where p.mrn in (select mrn from emr_surveyresponse b where 
b.question=YesNoUnsureQuestions.question ) and 
((select count(*) from  nodis_case c
 where c.patient_id = p.id and 
condition in ('diabetes:type-2'  , 'diabetes:type-1', 'diabetes:gestational'  , 'diabetes:prediabetes'))=0))
where question = 'Do you have diabetes?';

--diabetes ynu survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes = (select count(distinct(p.mrn)) as "Pt yes / EHR yes" 
from emr_surveyresponse s, emr_patient p , nodis_case c 
 where p.mrn=s.mrn and s.question='Do you have diabetes?' and
       c.patient_id = p.id and 
       (c.condition in ( 'diabetes:type-1','diabetes:type-2','diabetes:prediabetes','diabetes:gestational' ) 
     and response_choice='Y')  ) 
where question = 'Do you have diabetes?';

--diabetes ynu survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno = (select count(distinct(p.mrn)) as "Pt yes / EHR no" 
from emr_surveyresponse s, emr_patient p , nodis_case c 
 where p.mrn=s.mrn and s.question='Do you have diabetes?' and
       c.patient_id = p.id and 
       (c.condition not in ( 'diabetes:type-1','diabetes:type-2','diabetes:prediabetes','diabetes:gestational' ) 
     and response_choice='Y')  ) 
where question = 'Do you have diabetes?';

--diabetes ynu survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes = (select count(distinct(p.mrn)) as "Pt no / EHR yes" 
from emr_surveyresponse s, emr_patient p , nodis_case c 
 where p.mrn=s.mrn and s.question='Do you have diabetes?' and
       c.patient_id = p.id and 
       (c.condition  in ( 'diabetes:type-1','diabetes:type-2','diabetes:prediabetes','diabetes:gestational' ) 
     and response_choice='N')  ) 
where question = 'Do you have diabetes?';

--diabetes ynu survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno = (select count(distinct(p.mrn)) as "Pt no / EHR no" 
from emr_surveyresponse s, emr_patient p , nodis_case c 
 where p.mrn=s.mrn and s.question='Do you have diabetes?' and
       c.patient_id = p.id and 
       (c.condition not in ( 'diabetes:type-1','diabetes:type-2','diabetes:prediabetes','diabetes:gestational' ) 
     and response_choice='N')  ) 
where question = 'Do you have diabetes?';

--diabetes ynu survey vs ehr unsure/yes
update YesNoUnsureQuestions set ptunsureehryes = (select count(distinct(p.mrn)) as "Pt unsure / EHR yes" 
from emr_surveyresponse s, emr_patient p , nodis_case c 
 where p.mrn=s.mrn and s.question='Do you have diabetes?' and
       c.patient_id = p.id and 
       (c.condition in ( 'diabetes:type-1','diabetes:type-2','diabetes:prediabetes','diabetes:gestational' ) 
     and response_choice='U')  ) 
where question = 'Do you have diabetes?';

--diabetes ynu survey vs ehr unsure/no
update YesNoUnsureQuestions set ptunsureehrno = (select count(distinct(p.mrn)) as "Pt unsure / EHR no" 
from emr_surveyresponse s, emr_patient p , nodis_case c 
 where p.mrn=s.mrn and s.question='Do you have diabetes?' and
       c.patient_id = p.id and 
       (c.condition not in ( 'diabetes:type-1','diabetes:type-2','diabetes:prediabetes','diabetes:gestational' ) 
     and response_choice='U')  ) 
where question = 'Do you have diabetes?';

--a1c ynu survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes = (select count(distinct(p.mrn)) as "Pt yes / EHR yes" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='a1c') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='Y')  
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c ynu survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno = (select count(distinct(p.mrn)) as "Pt yes / EHR no" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code not in (select native_code from conf_labtestmap where test_name ='a1c') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='Y')  
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c ynu survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes = (select count(distinct(p.mrn)) as "Pt no / EHR yes" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code  in (select native_code from conf_labtestmap where test_name ='a1c') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='N')  
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c ynu survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno = (select count(distinct(p.mrn)) as "Pt no / EHR no" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code not in (select native_code from conf_labtestmap where test_name ='a1c') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='N')  
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c ynu survey vs ehr unsure/yes
update YesNoUnsureQuestions set ptunsureehryes = (select count(distinct(p.mrn)) as "Pt unsure / EHR yes" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code  in (select native_code from conf_labtestmap where test_name ='a1c') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='U')  
where question = 'Have you ever had your hemoglobin A1C level checked?';

--a1c ynu survey vs ehr unsure/no
update YesNoUnsureQuestions set ptunsureehrno = (select count(distinct(p.mrn)) as "Pt unsure / EHR no" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code not in (select native_code from conf_labtestmap where test_name ='a1c') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='U')  
where question = 'Have you ever had your hemoglobin A1C level checked?';

--hyperlipedimia ynu survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes =  (select count(distinct(p.mrn)) as "Pt yes / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and   (      
( select count(distinct(emr_labresult.patient_id))  from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float >160 )>0 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0))
where YesNoUnsureQuestions.question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--hyperlipedimia ynu survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno =  (select count(distinct(p.mrn)) as "Pt yes / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and  (
( select count(distinct(emr_labresult.patient_id)) from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float >160 )=0 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0))
where YesNoUnsureQuestions.question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--hyperlipedimia ynu survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes =  (select count(distinct(p.mrn)) as "Pt no / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and  (
( select count(distinct(emr_labresult.patient_id)) from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float >160 )>0 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0))
where YesNoUnsureQuestions.question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--hyperlipedimia ynu survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno =  (select count(distinct(p.mrn)) as "Pt no / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and  (
( select count(distinct(emr_labresult.patient_id)) from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float >160 )=0 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0))
where YesNoUnsureQuestions.question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--hyperlipedimia ynu survey vs ehr unsure/yes
update YesNoUnsureQuestions set ptunsureehryes =  (select count(distinct(p.mrn)) as "Pt unsure/ EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and  (
( select count(distinct(emr_labresult.patient_id)) from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float >160 )>0 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0))
where YesNoUnsureQuestions.question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--hyperlipedimia ynu survey vs ehr unsure/no
update YesNoUnsureQuestions set ptunsureehrno =  (select count(distinct(p.mrn)) as "Pt unsure/ EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and  (
( select count(distinct(emr_labresult.patient_id)) from emr_labresult where emr_labresult.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
result_float >160 )=0 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0))
where YesNoUnsureQuestions.question = 'Do you have a history of hyperlipidemia or elevated cholesterol?';

--ldl ynu survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes = (select count(distinct(p.mrn)) as "Pt yes / EHR yes" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='Y')  
where question = 'Have you ever had your LDL level checked?';

--ldl ynu survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno = (select count(distinct(p.mrn)) as "Pt yes / EHR no" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code not in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='Y')  
where question = 'Have you ever had your LDL level checked?';

--ldl ynu survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes = (select count(distinct(p.mrn)) as "Pt no / EHR yes" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code  in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='N')  
where question = 'Have you ever had your LDL level checked?';

--ldl ynu survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno = (select count(distinct(p.mrn)) as "Pt no / EHR no" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code not in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='N')  
where question = 'Have you ever had your LDL level checked?';

--ldl ynu survey vs ehr unsure/yes
update YesNoUnsureQuestions set ptunsureehryes = (select count(distinct(p.mrn)) as "Pt unsure / EHR yes" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code  in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='U')  
where question = 'Have you ever had your LDL level checked?';

--ldl ynu survey vs ehr unsure/no
update YesNoUnsureQuestions set ptunsureehrno = (select count(distinct(p.mrn)) as "Pt unsure / EHR no" 
from emr_surveyresponse s, emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and 
native_code not in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl') and 
 p.mrn=s.mrn and s.question=YesNoUnsureQuestions.question and
        response_choice='U')  
where question = 'Have you ever had your LDL level checked?';

--meds for hyperlipedimia ynu survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes =  (select count(distinct(p.mrn)) as "Pt yes / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and       
 (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high cholesterol?';

--meds hyperlipedimia ynu survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno =  (select count(distinct(p.mrn)) as "Pt yes / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high cholesterol?';


--med hyperlipedimia ynu survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes =  (select count(distinct(p.mrn)) as "Pt no / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high cholesterol?';

--med hyperlipedimia ynu survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno =  (select count(distinct(p.mrn)) as "Pt no / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and  (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high cholesterol?';

--meds hyperlipedimia ynu survey vs ehr unsure/yes
update YesNoUnsureQuestions set ptunsureehryes =  (select count(distinct(p.mrn)) as "Pt unsure/ EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and  (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high cholesterol?';

--hyperlipedimia ynu survey vs ehr unsure/no
update YesNoUnsureQuestions set ptunsureehrno =  (select count(distinct(p.mrn)) as "Pt unsure/ EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription 
where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')=0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high cholesterol?';

--hypertension ynu survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes =  (select count(distinct(p.mrn)) as "Pt yes / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and   (      
( select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )>=2
 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0))
where YesNoUnsureQuestions.question = 'Have you ever been diagnosed with high blood pressure?';

--hypertension ynu survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno =  (select count(distinct(p.mrn)) as "Pt yes / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and   (      
( select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )<2
 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')=0))
where YesNoUnsureQuestions.question = 'Have you ever been diagnosed with high blood pressure?';

--hypertension ynu survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes =  (select count(distinct(p.mrn)) as "Pt no / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and   (      
( select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )>=2
 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0))
where YesNoUnsureQuestions.question = 'Have you ever been diagnosed with high blood pressure?';

--hypertension ynu survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno =  (select count(distinct(p.mrn)) as "Pt no / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and   (      
( select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )<2
 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')=0))
where YesNoUnsureQuestions.question = 'Have you ever been diagnosed with high blood pressure?';

--hypertension ynu survey vs ehr unsure/yes
update YesNoUnsureQuestions set ptunsureehryes =  (select count(distinct(p.mrn)) as "Pt unsure / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and   (      
( select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )>=2
 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0))
where YesNoUnsureQuestions.question = 'Have you ever been diagnosed with high blood pressure?';

--hypertension ynu survey vs ehr unsure/no
update YesNoUnsureQuestions set ptunsureehrno =  (select count(distinct(p.mrn)) as "Pt unsure / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and   (      
( select count(emr_encounter.date) from emr_encounter where emr_encounter.patient_id = p.id  
and (bp_systolic >140 or bp_diastolic > 90) )<2
 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')=0))
where YesNoUnsureQuestions.question = 'Have you ever been diagnosed with high blood pressure?';

--meds for hypertension ynu survey vs ehr yes/yes
update YesNoUnsureQuestions set ptyesehryes =  (select count(distinct(p.mrn)) as "Pt yes / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high blood pressure?';

--meds hypertension ynu survey vs ehr yes/no
update YesNoUnsureQuestions set ptyesehrno =  (select count(distinct(p.mrn)) as "Pt yes / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'Y' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')=0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high blood pressure?';

--meds hypertension ynu survey vs ehr no/yes
update YesNoUnsureQuestions set ptnoehryes =  (select count(distinct(p.mrn)) as "Pt no / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high blood pressure?';

--meds hypertension ynu survey vs ehr no/no
update YesNoUnsureQuestions set ptnoehrno =  (select count(distinct(p.mrn)) as "Pt no / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'N' and  (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')=0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high blood pressure?';

--meds hypertension ynu survey vs ehr unsure/yes
update YesNoUnsureQuestions set ptunsureehryes =  (select count(distinct(p.mrn)) as "Pt unsure / EHR yes" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high blood pressure?';

--meds hypertension ynu survey vs ehr unsure/no
update YesNoUnsureQuestions set ptunsureehrno =  (select count(distinct(p.mrn)) as "Pt unsure / EHR no" 
from emr_surveyresponse s, emr_patient p 
where  p.mrn = s.mrn and s.question=YesNoUnsureQuestions.question and
s.response_choice = 'U' and   (select count(distinct(emr_prescription.patient_id)) from emr_prescription where emr_prescription.patient_id = p.id and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')=0)
where YesNoUnsureQuestions.question = 'Are you currently being prescribed medications for high blood pressure?';

--type of diabetes 
drop TABLE if exists DiabetesType;

CREATE TEMPORARY TABLE DiabetesType(
    Type   VARCHAR(80),
    SelfReportYes INTEGER,
    SelfReportNo  INTEGER,
    EHRYes  INTEGER,
    EHRNo  INTEGER,
    PtYesEHRYes INTEGER,
    PtYesEHRNo INTEGER,
    PtNoEHRYes INTEGER,
    PtNoEHRNo INTEGER
);

INSERT INTO DiabetesType ( Type) values ('Pre-diabetes');
INSERT INTO DiabetesType ( Type) values ('Type 1');
INSERT INTO DiabetesType ( Type) values ('Type 2');
INSERT INTO DiabetesType ( Type) values ('Gestational');

--diabetes type selfreport yes
update DiabetesType set SelfReportYes =( select count(*) 
  from emr_surveyresponse b
where b.question='What kind of diabetes do you have?' and (
(response_choice='PRE' and Type=  'Pre-diabetes' ) or
(response_choice='T1' and Type=   'Type 1') or
(response_choice='T2' and Type=   'Type 2') or
(response_choice='GDM' and Type=  'Gestational')  
) group by response_choice, b.question);

--diabetes type SELFreport no
update DiabetesType set SelfReportNo =( select (select count(*) from emr_surveyresponse a
where a.question=b.question)- count(*) 
  from emr_surveyresponse b
where b.question='What kind of diabetes do you have?' and (
(response_choice='PRE' and Type=  'Pre-diabetes' ) or
(response_choice='T1' and Type=   'Type 1') or
(response_choice='T2' and Type=   'Type 2') or
(response_choice='GDM' and Type=   'Gestational')  
) group by response_choice, b.question);
 
--diabetes type ehr yes 
update DiabetesType set ehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition   ='diabetes:type-1' and c.patient_id = p.id )>0  ) 
  where Type='Type 1' ;

update DiabetesType set ehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition  = 'diabetes:type-2' and c.patient_id = p.id )>0  ) 
  where Type='Type 2' ;

update DiabetesType set ehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition  = 'diabetes:prediabetes' and c.patient_id = p.id )>0  ) 
  where Type='Pre-diabetes' ;

update DiabetesType set ehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:gestational' and c.patient_id = p.id )>0  ) 
  where Type='Gestational' ;


--diabetes type ehr no, for each type
update DiabetesType set ehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition   = 'diabetes:type-1' and c.patient_id = p.id )=0  ) 
  where Type='Type 1' ;

update DiabetesType set ehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition   = 'diabetes:type-2' and c.patient_id = p.id )=0  ) 
  where Type='Type 2' ;

update DiabetesType set ehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition   = 'diabetes:prediabetes' and c.patient_id = p.id )=0  ) 
  where Type='Pre-diabetes' ;

update DiabetesType set ehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and
  (select count(*) from nodis_case c  where 
            c.condition   = 'diabetes:gestational' and c.patient_id = p.id )=0  ) 
  where Type='Gestational' ;
  

--diabetes survey vs ehr yes/yes for each type
update DiabetesType set ptyesehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='T1' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-1' and c.patient_id = p.id )>0  ) 
  where Type='Type 1' ;

update DiabetesType set ptyesehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='T2' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-2' and c.patient_id = p.id )>0  ) 
  where Type='Type 2' ;

update DiabetesType set ptyesehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='PRE' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:prediabetes' and c.patient_id = p.id )>0  ) 
  where Type='Pre-diabetes' ;

update DiabetesType set ptyesehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='GDM' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:gestational' and c.patient_id = p.id )>0  ) 
  where Type='Gestational' ;

--diabetes survey vs ehr yes/no 
update DiabetesType set ptyesehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='T1' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-1' and c.patient_id = p.id )=0  ) 
  where Type='Type 1' ;

update DiabetesType set ptyesehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='T2' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-2' and c.patient_id = p.id )=0  ) 
  where Type='Type 2' ;

update DiabetesType set ptyesehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='PRE' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:prediabetes' and c.patient_id = p.id )=0  ) 
  where Type='Pre-diabetes' ;

update DiabetesType set ptyesehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice='GDM' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:gestational' and c.patient_id = p.id )=0  ) 
  where Type='Gestational' ;

--diabetes survey vs ehr no/yes
update DiabetesType set ptnoehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'T1' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-1' and c.patient_id = p.id )>0  ) 
  where Type='Type 1' ;

update DiabetesType set ptnoehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'T2' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-2' and c.patient_id = p.id )>0  ) 
  where Type='Type 2' ;

update DiabetesType set ptnoehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'PRE' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:prediabetes' and c.patient_id = p.id )>0  ) 
  where Type='Pre-diabetes' ;

update DiabetesType set ptnoehryes =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'GDM' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:gestational' and c.patient_id = p.id )>0  ) 
  where Type='Gestational' ;

--diabetes survey vs ehr no/no 
update DiabetesType set ptnoehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'T1' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-1' and c.patient_id = p.id )=0  ) 
  where Type='Type 1' ;

update DiabetesType set ptnoehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'T2' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:type-2' and c.patient_id = p.id )=0  ) 
  where Type='Type 2' ;

update DiabetesType set ptnoehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'PRE' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:prediabetes' and c.patient_id = p.id )=0  ) 
  where Type='Pre-diabetes' ;

update DiabetesType set ptnoehrno =( select count(distinct p.mrn)  from emr_patient p, emr_surveyresponse b
where p.mrn = b.mrn and question='What kind of diabetes do you have?'  and response_choice<>'GDM' and 
  (select count(*) from nodis_case c  where 
            c.condition  ='diabetes:gestational' and c.patient_id = p.id )=0  ) 
  where Type='Gestational' ;
 	 
--diabetes type TOTALS
INSERT INTO DiabetesType  (Type  , SelfReportYes ,SelfReportNo  ,
    EHRYes ,  EHRNo ,PtYesEHRYes , PtYesEHRNo , PtNoEHRYes , PtNoEHRNo )
 select 'TOTAL', sum(selfreportyes), sum(selfreportno),sum(ehryes),sum(ehrno), sum(ptyesehryes),
  sum(ptyesehrno), sum(ptnoehryes), sum(ptnoehrno) from DiabetesType;
	 
--weight type
drop TABLE if exists WeightType;

CREATE TEMPORARY TABLE WeightType(
    Type   VARCHAR(80),
    SelfReportYes INTEGER,
    SelfReportNo  INTEGER,
    EHRYes  INTEGER,
    EHRNo  INTEGER,
    EHRMissing  INTEGER,
    PtYesEHRYes INTEGER,
    PtYesEHRNo INTEGER,
    PtNoEHRYes INTEGER,
    PtNoEHRNo INTEGER,
    PtYesEHRMissing INTEGER,
    PtNoEHRMissing INTEGER
);

INSERT INTO WeightType ( Type) values ('Low');
INSERT INTO WeightType ( Type) values ('Normal');
INSERT INTO WeightType ( Type) values ('Overweight');
INSERT INTO WeightType ( Type) values ('Obese');

--weight type selfreport yes
update WeightType set SelfReportYes =( select count(*) 
  from emr_surveyresponse b
where b.question='How would you classify your weight?' and (
(response_choice='L' and Type=  'Low' ) or
(response_choice='N' and Type=   'Normal') or
(response_choice='OW' and Type=   'Overweight') or
(response_choice='OB' and Type=  'Obese')  
) group by response_choice, b.question);

--weight selfreport no
update WeightType set SelfReportNo =( select (select count(*) from emr_surveyresponse a
where a.question=b.question)- count(*) 
  from emr_surveyresponse b
where b.question='How would you classify your weight?' and (
(response_choice='L' and Type=  'Low' ) or
(response_choice='N' and Type=   'Normal') or
(response_choice='OW' and Type=   'Overweight') or
(response_choice='OB' and Type=  'Obese')  ) group by response_choice, b.question);

--weight type ehr yes 
update WeightType set ehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >18 and bmi <25 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi<18 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >25.01 and bmi <30 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >130 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where Type = 'Obese';

--weight type ehr no 
update WeightType set ehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <18 or bmi >25 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi>18 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <25.01 or bmi >30 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <130 and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where Type = 'Obese';

--weight type ehr missing 
update WeightType set ehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?'
 order by c.date desc limit 1)>0 )where Type = 'Obese';

--weight survey vs ehr yes/yes
update WeightType set ptyesehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >18 and bmi <25 and
question='How would you classify your weight?' and response_choice='N' 
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ptyesehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi<18 and
question='How would you classify your weight?' and response_choice='L'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ptyesehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >25.01 and bmi <30 and
question='How would you classify your weight?' and response_choice='OW'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ptyesehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >130 and
question='How would you classify your weight?' and response_choice='OB'
 order by c.date desc limit 1)>0 )where Type = 'Obese';
 
--weight survey vs ehr yes/no 
update WeightType set ptyesehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <18 and bmi >25 and
question='How would you classify your weight?' and response_choice='N' 
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ptyesehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi>18 and
question='How would you classify your weight?' and response_choice='L'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ptyesehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <25.01 and bmi >30 and
question='How would you classify your weight?' and response_choice='OW'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ptyesehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <130 and
question='How would you classify your weight?' and response_choice='OB'
 order by c.date desc limit 1)>0 )where Type = 'Obese';
 	 
--weight survey vs ehr no/yes 
update WeightType set ptnoehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >18 and bmi <25 and
question='How would you classify your weight?' and response_choice<>'N' 
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ptnoehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi<18 and
question='How would you classify your weight?' and response_choice<>'L'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ptnoehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >25.01 and bmi <30 and
question='How would you classify your weight?' and response_choice<>'OW'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ptnoehryes =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi >130 and
question='How would you classify your weight?' and response_choice<>'OB'
 order by c.date desc limit 1)>0 )where Type = 'Obese';

--weight survey vs ehr no/no  
update WeightType set ptnoehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <18 and bmi >25 and
question='How would you classify your weight?' and response_choice<>'N' 
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ptnoehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi>18 and
question='How would you classify your weight?' and response_choice<>'L'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ptnoehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <25.01 and bmi >30 and
question='How would you classify your weight?' and response_choice<>'OW'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ptnoehrno =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where bmi is not null and e.mrn = c.mrn and bmi <130 and
question='How would you classify your weight?' and response_choice<>'OB'
 order by c.date desc limit 1)>0 )where Type = 'Obese';

--weight survey vs ehr yes/missing
update WeightType set ptyesehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice='N' 
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ptyesehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice='L'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ptyesehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice='OW'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ptyesehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice='OB'
 order by c.date desc limit 1)>0 )where Type = 'Obese';

--weight survey vs ehr no/missing 
update WeightType set ptnoehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice<>'N' 
 order by c.date desc limit 1)>0 ) where Type = 'Normal';

update WeightType set ptnoehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice<>'L'
 order by c.date desc limit 1)>0 )where  Type = 'Low';

update WeightType set ptnoehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice<>'OW'
 order by c.date desc limit 1)>0 )where Type = 'Overweight';

update WeightType set ptnoehrmissing =(select count(distinct e.mrn) from emr_surveyresponse e where ( 
select bmi from emr_encounter c
where  e.mrn = c.mrn and bmi is  null and
question='How would you classify your weight?' and response_choice<>'OB'
 order by c.date desc limit 1)>0 )where Type = 'Obese';

--weight type TOTALS
INSERT INTO WeightType  (Type  , SelfReportYes ,SelfReportNo  ,
    EHRYes ,  EHRNo ,EHRMissing, PtYesEHRYes , PtYesEHRNo , PtNoEHRYes , PtNoEHRNo, ptyesehrmissing,ptnoehrmissing )
 select 'TOTAL', sum(selfreportyes), sum(selfreportno),sum(ehryes),sum(ehrno), sum(ehrmissing), sum(ptyesehryes),
  sum(ptyesehrno), sum(ptnoehryes), sum(ptnoehrno), sum(ptyesehrmissing), sum(ptnoehrmissing) from WeightType;
 
--line list
drop TABLE if exists LineList;

CREATE TEMPORARY TABLE LineList(
    Patientid   VARCHAR(128),
    mrn VARCHAR(50),
    FirstName  VARCHAR(200),
    LastName  VARCHAR(200),
    DOB  timestamp with time zone,
    Survey_age INTEGER,
    EHR_age INTEGER,
    Survey_Gender  VARCHAR(20),
    EHR_gender VARCHAR(20),
    Survey_Race VARCHAR(100),
    EHR_race VARCHAR(100),
    Survey_diastolic DECIMAL(7,2),
    Survey_systolic DECIMAL(7,2),
    EHR_diastolic DECIMAL(7,2),
    EHR_systolic DECIMAL(7,2),
    Survey_BP_unsure VARCHAR(20),
    Survey_HBP VARCHAR(20),
    EHR_HBP VARCHAR(20),
    Survey_HBP_med VARCHAR(20),
    EHR_HBP_med VARCHAR(20),
    Survey_Diabetes VARCHAR(20),
    EHR_Diabetes VARCHAR(20),
    Survey_DiabetesType VARCHAR(80),
    EHR_DiabetesType1 VARCHAR(80),
    EHR_DiabetesType2 VARCHAR(80),
    EHR_DiabetesTypePRE VARCHAR(80),
    EHR_DiabetesTypeGES VARCHAR(80),
    Survey_a1c VARCHAR(20),
    EHR_a1c VARCHAR(20),
    Survey_a1c_value DECIMAL(7,2),
    EHR_a1c_value DECIMAL(7,2),
    Survey_a1c_value_unsure VARCHAR(20),
    Survey_height DECIMAL(7,2),
    EHR_height DECIMAL(7,2),
    Survey_height_unsure VARCHAR(20),
    Survey_weight DECIMAL(7,2),
    EHR_weight DECIMAL(7,2),
    Survey_weight_unsure VARCHAR(20),
    Survey_bmi VARCHAR(80),
    EHR_bmi VARCHAR(80),
    Survey_hyperlipidemia VARCHAR(20),
    EHR_hyperlipidemia VARCHAR(20),
    Survey_ldl VARCHAR(20),
    EHR_ldl VARCHAR(20),
    Survey_ldl_value DECIMAL(7,2),
    EHR_ldl_value DECIMAL(7,2),
    Survey_ldl_value_unsure VARCHAR(20),
    Survey_ldl_med VARCHAR(20),
    EHR_ldl_med VARCHAR(20)
);

INSERT INTO LineList  (Patientid  ,  mrn , FirstName , LastName , DOB,  EHR_gender , EHR_race , EHR_age ) 
  select p.natural_key, p.mrn, p.first_name, p.last_name, p.date_of_birth,
     p.gender, p.race, date_part('year',age(p.date_of_birth))
     from emr_patient p where p.mrn in (select b.mrn from  emr_surveyresponse b) ;      

update LineList set 
EHR_systolic = (select e.bp_systolic from emr_encounter as e, emr_patient where emr_patient.id = e.patient_id and LineList.mrn =emr_patient.mrn 
and e.bp_systolic is not null order by e.date desc limit 1),  
EHR_diastolic = (select e.bp_diastolic from emr_encounter as e, emr_patient where emr_patient.id = e.patient_id and LineList.mrn =emr_patient.mrn 
and e.bp_diastolic is not null order by e.date desc limit 1),  
  survey_gender = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='What is your gender?'),
  survey_race = (select case WHEN response_choice = 'B' THEN 'BLACK' WHEN response_choice = 'W' THEN 'CAUCASIAN' WHEN response_choice = 'A' THEN 'ASIAN' WHEN response_choice = 'H' THEN 'HISPANIC'
  WHEN response_choice = 'O' THEN 'OTHER' WHEN response_choice = 'I' THEN 'INDIAN' WHEN response_choice = 'NA' THEN 'NAT AMERICAN' WHEN response_choice = 'AL' THEN 'ALASKAN' WHEN response_choice = 'NH' THEN 'NATIVE HAWAI/PACIFIC ISLANDER' 
  WHEN response_choice = 'M' THEN 'MULTIRACIAL' WHEN response_choice = 'PD' THEN 'PATIENT DECL' 
    END 
    from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='What is your race/ethnicity?'),
  survey_age = (select response_float from  emr_surveyresponse b where LineList.mrn =b.mrn and question ='What is your age?'),
  Survey_diastolic =(select response_float from  emr_surveyresponse b where LineList.mrn =b.mrn and question ='What is your last diastolic blood pressure?'),
  Survey_systolic =(select response_float from  emr_surveyresponse b where LineList.mrn =b.mrn and question ='What was your systolic blood pressure the last time it was measured by your doctor?'),
  Survey_BP_unsure = (select response_boolean from emr_surveyresponse b where LineList.mrn =b.mrn and question ='systolic-diastolic / unsure'),
  Survey_HBP = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='Have you ever been diagnosed with high blood pressure?'),
  EHR_HBP = (select case when  (select count(*) from emr_encounter b where  LineList.mrn =b.mrn and (b.bp_systolic >140 or b.bp_diastolic > 90) )>2 
 or (select count(distinct(emr_prescription.patient_id)) from emr_prescription, emr_patient where 
 emr_prescription.patient_id = emr_patient.id and LineList.mrn =emr_patient.mrn and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0 THEN 'Y' ELSE 'N' END),
 Survey_HBP_med =(select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='Are you currently being prescribed medications for high blood pressure?'),    
 Survey_Diabetes = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='Do you have diabetes?'),
 Survey_DiabetesType  = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='What kind of diabetes do you have?'),
 Survey_a1c = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='Have you ever had your hemoglobin A1C level checked?'),
 Survey_a1c_value =  (select response_float from  emr_surveyresponse b where LineList.mrn =b.mrn and question ='What was your most recent hemoglobin A1C value?'),
 Survey_a1c_value_unsure = (select response_boolean from emr_surveyresponse b where LineList.mrn =b.mrn and question ='a1c unsure'),
 Survey_height =  (select response_float from  emr_surveyresponse b where LineList.mrn =b.mrn and question ='What is your current height in Feet and Inches?'),
 Survey_weight =  (select response_float from  emr_surveyresponse b where LineList.mrn =b.mrn and question ='What is your current weight in pounds?'),
 Survey_bmi = (select CASE WHEN response_choice='L' THEN 'Low' when response_choice = 'N' then 'Normal' when response_choice = 'OW' then 'Overweight'
 when response_choice = 'OB' then 'Obese' END 
    from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='How would you classify your weight?'),
 Survey_hyperlipidemia = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='Do you have a history of hyperlipidemia or elevated cholesterol?'),
 Survey_ldl = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='Have you ever had your LDL level checked?'),
 Survey_ldl_value =  (select response_float from  emr_surveyresponse b where LineList.mrn =b.mrn and question ='What was your last LDL level?'),
 Survey_ldl_med = (select response_choice  from emr_surveyresponse b  where  LineList.mrn =b.mrn and b.question='Are you currently being prescribed medications for high cholesterol?'),
 EHR_height = (select emr_encounter.height from  emr_encounter, emr_patient  where emr_patient.id = emr_encounter.patient_id and LineList.mrn = emr_encounter.mrn and emr_encounter.height is not null order by emr_encounter.date desc limit 1),
 EHR_weight = (select emr_encounter.weight from  emr_encounter, emr_patient  where emr_patient.id = emr_encounter.patient_id and LineList.mrn = emr_encounter.mrn and emr_encounter.weight is not null  order by emr_encounter.date desc limit 1),
 Survey_height_unsure =  (select response_boolean from emr_surveyresponse b where LineList.mrn =b.mrn and question ='height/unsure'),
 Survey_weight_unsure = (select response_boolean from emr_surveyresponse b where LineList.mrn =b.mrn and question ='weight/ unsure'),
 EHR_bmi = (select emr_encounter.bmi from  emr_encounter where LineList.mrn = emr_encounter.mrn order by emr_encounter.date desc limit 1),
 EHR_HBP_med = (select case when (select count(distinct(emr_prescription.patient_id)) from emr_prescription, emr_patient  
 where emr_prescription.patient_id = emr_patient.id and LineList.mrn =emr_patient.mrn and 
lower(name) similar to '%(benazepril|captopril|enalapril|fosinopril|lisinopril|moexipril|perindopril|quinapril|ramipril|trandolapril|
eplerenone|spironolactone|clonidine|doxazosin|guanfacine|methyldopa|prazosin|terazosin|candesartan|eprosartan|irbesartan|
losartan|olmesartan|telmisartan|valsartan|acebutolol|atenolol|betaxolol|bisoprolol|carvedilol|labetolol|metoprolol|nadolol|
nebivolol|oxprenolol|pindolol|propranolol|amlodipine|clevidipine|felodopine|isradipine|nicardipine|nifedipine|nisoldipine|
diltiazem|verapamil|chlorthalidone|hydrochlorothiazide|indapamide|aliskiren|fenoldopam|hydralazine)%')>0 THEN 'Y' ELSE 'N' END),
EHR_hyperlipidemia = (select case when (select count(distinct(emr_prescription.patient_id)) from emr_prescription , emr_patient 
where emr_prescription.patient_id = emr_patient.id and LineList.mrn =emr_patient.mrn and  
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0 THEN 'Y' ELSE 'N' END),
EHR_ldl = (select case when (select count(distinct(p.mrn)) from  emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and LineList.mrn =p.mrn and 
native_code  in (select native_code from conf_labtestmap where test_name ='cholesterol-ldl')  )>0 THEN 'Y' ELSE 'N' END),
EHR_a1c = (select case when (select count(distinct(p.mrn)) from  emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and LineList.mrn =p.mrn and 
native_code  in (select native_code from conf_labtestmap where test_name ='a1c') )>0 THEN 'Y' ELSE 'N' END),
EHR_Diabetes =  (select case when (select count(distinct(p.mrn)) from  emr_patient p , nodis_case c 
 where LineList.mrn =p.mrn  and  c.patient_id = p.id and 
       (c.condition in ( 'diabetes:type-1','diabetes:type-2','diabetes:prediabetes','diabetes:gestational' )))>0 THEN 'Y' ELSE 'N' END),
EHR_DiabetesType1 =  (select case when (select count(*) from  emr_patient p , nodis_case c 
 where LineList.mrn =p.mrn  and  c.patient_id = p.id and 
       (c.condition = 'diabetes:type-1' ) )>0 THEN  'Y' ELSE 'N' END),
EHR_DiabetesType2 =  (select case when (select count(*) from  emr_patient p , nodis_case c 
 where LineList.mrn =p.mrn  and  c.patient_id = p.id and 
       (c.condition ='diabetes:type-2' ) )>0 THEN  'Y' ELSE 'N' END),
EHR_DiabetesTypePRE =  (select case when (select count(*) from  emr_patient p , nodis_case c 
 where LineList.mrn =p.mrn  and  c.patient_id = p.id and 
       (c.condition ='diabetes:prediabetes') )>0 THEN  'Y' ELSE 'N' END),
EHR_DiabetesTypeGES =  (select case when (select count(*) from  emr_patient p , nodis_case c 
 where LineList.mrn =p.mrn  and  c.patient_id = p.id and 
       (c.condition ='diabetes:gestational' ) )>0 THEN  'Y' ELSE 'N' END),
EHR_ldl_value = (select c.result_float from  emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and LineList.mrn =p.mrn and native_code  in 
(select native_code from conf_labtestmap where test_name ='cholesterol-ldl') order by c.date desc limit 1 ),
EHR_a1c_value  =  (select c.result_float from  emr_patient p ,  emr_labresult c
where  c.patient_id = p.id and LineList.mrn =p.mrn and native_code  in
 (select native_code from conf_labtestmap where test_name ='a1c') order by c.date desc limit 1 ),
Survey_ldl_value_unsure =  (select response_boolean from emr_surveyresponse b where LineList.mrn =b.mrn and question ='ldl unsure'), 
EHR_ldl_med =  (select  case when (select count(distinct(emr_prescription.patient_id)) from emr_prescription , emr_patient
where emr_prescription.patient_id = emr_patient.id and LineList.mrn =emr_patient.mrn and  
lower(name) similar to '%(lovastatin|atorvastatin|fluvastatin|pravastatin|rosuvastatin|simvastatin|
bezafibrate|fenofibrate|fenofibric acid|gemfibrozil|cholestyramine|colesevelam|colestipol|niacin|ezetimibe)%')>0 THEN  'Y' ELSE 'N' END);
 
update LineList set Survey_diastolic=0 where Survey_diastolic is null;
update LineList set Survey_systolic=0 where Survey_systolic is null;
update LineList set Survey_BP_unsure='N/A' where Survey_BP_unsure is null;
update LineList set Survey_DiabetesType='N/A' where Survey_DiabetesType is null;
update LineList set Survey_a1c_value=0 where Survey_a1c_value is null;
update LineList set EHR_a1c_value=0 where EHR_a1c_value is null;
update LineList set Survey_height=0 where Survey_height is null;
update LineList set EHR_height=0 where EHR_height is null;
update LineList set Survey_weight=0 where Survey_weight is null;
update LineList set EHR_weight=0 where EHR_weight is null;
update LineList set EHR_bmi=0 where EHR_bmi is null;
update LineList set Survey_ldl='N/A' where Survey_ldl is null;
update LineList set Survey_ldl_value=0 where Survey_ldl_value is null;
update LineList set EHR_ldl_value=0 where EHR_ldl_value is null;
