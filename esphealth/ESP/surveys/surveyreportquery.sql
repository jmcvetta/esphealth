select question as "Questions", noofrespondents as "No. of Respondents", 
NoOfEHRRespondents as "No. of EHR Respondents",
selfreportmean::text   as "Self-Report Mean",  ' +/- ' || selfreportsd::text  as "SD",
EHRReportMean::text  as "EHR Mean",  ' +/- ' || EHRReportSD::text as "SD"
 from ContinuousVariables where selfreportmean>0;

select  RaceEthnicity as "Race-Ethnicity" , SelfReportYes as "Self-Report Yes",
SelfReportNo  as "Self-Report No",    EHRYes as "EHR Yes",  EHRNo as "EHR No" ,
PtYesEHRYes as "Pt Yes / EHR Yes", PtYesEHRNo as "Pt Yes / EHR No", 
PtNoEHRYes as "Pt No / EHR Yes", PtNoEHRNo as "Pt No / EHR No" from CategoricalVariables;

select Question, NoOfRespondents as "No. of Respondents", PtYes as "Pt Yes",
PTNo  as "Pt No",  PtUnsure as "Pt Unsure",  EHRYes as "EHR Yes",  EHRNo as "EHR No" ,
PtYesEHRYes as "Pt Yes / EHR Yes", PtYesEHRNo as "Pt Yes / EHR No", 
PtNoEHRYes as "Pt No / EHR Yes", PtNoEHRNo as "Pt No / EHR No",
PtUnsureEHRYes as "Pt Unsure / EHR Yes", PtUnsureEHRNo as "Pt Unsure / EHR Yes" from YesNoUnsureQuestions order by question;

select type as "Diabetes Type", SelfReportYes as "Self-Report Yes",
SelfReportNo  as "Self-Report No", EHRYes as "EHR Yes",  EHRNo as "EHR No" ,
PtYesEHRYes as "Pt Yes / EHR Yes", PtYesEHRNo as "Pt Yes / EHR No", 
PtNoEHRYes as "Pt No / EHR Yes", PtNoEHRNo as "Pt No / EHR No" from DiabetesType;

select type as "BMI Category", SelfReportYes as "Self-Report Yes",
SelfReportNo  as "Self-Report No",  EHRYes as "EHR Yes",  EHRNo as "EHR No" ,EHRMissing as "EHR Missing",
PtYesEHRYes as "Pt Yes / EHR Yes", PtYesEHRNo as "Pt Yes / EHR No", 
PtNoEHRYes as "Pt No / EHR Yes", PtNoEHRNo as "Pt No / EHR No",
ptyesehrmissing as "Pt Yes / EHR Missing", ptnoehrmissing as "Pt No / EHR Missing" from WeightType;

select  Patientid  ,  mrn , FirstName , LastName , DOB, Survey_Gender ,EHR_gender , Survey_Race,EHR_race ,  
 Survey_age ,EHR_age ,   Survey_diastolic ,  Survey_systolic ,    EHR_diastolic ,  EHR_systolic , Survey_BP_unsure,
    Survey_HBP ,    EHR_HBP ,    Survey_HBP_med ,    EHR_HBP_med ,    Survey_Diabetes ,    EHR_Diabetes ,   Survey_DiabetesType ,    EHR_DiabetesType ,
    Survey_a1c ,    EHR_a1c ,    Survey_a1c_value ,    EHR_a1c_value , Survey_a1c_value_unsure,
    Survey_height ,    EHR_height ,  Survey_height_unsure,  Survey_weight ,    EHR_weight , Survey_weight_unsure,   Survey_bmi ,    EHR_bmi ,
    Survey_hyperlipidemia ,    EHR_hyperlipidemia ,    Survey_ldl ,    EHR_ldl ,    Survey_ldl_value ,
    EHR_ldl_value ,  Survey_ldl_value_unsure,  Survey_ldl_med ,    EHR_ldl_med from LineList order by Patientid;

