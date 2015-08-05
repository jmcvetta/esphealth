/*--------------------------------------------------------------------------------
--
--                                ESP Health
--                         General Population Report
--
--------------------------------------------------------------------------------
--
-- @author: Bob Zambarano <bzambarano@commoninf.com>
-- @organization: Commonwealth Informatics <http://www.commoninf.com>
-- @contact: http://esphealth.org
-- @copyright: (c) 2012 Commonwealth Informatics
-- @license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
--
--------------------------------------------------------------------------------*/
--select max(counts) from ( select count(*) as counts from (
SELECT 
  gpr_pat.patient_id 
, gpr_pat.mrn
, date_part('year', age(gpr_pat.last_enc_date)) as years_since_last_enc
, gpr_pat.age
, gpr_pat.gender 
, gpr_pat.race
, case
    when substring(gpr_pat.zip,6,1)='-' then substring(gpr_pat.zip,1,5)
    else gpr_pat.zip
  end as zip
, gpr_bmi.bmi
, gpr_bmi.bmipct
, gpr_bmi.date 
, gpr_curpreg.currently_pregnant
, gpr_recpreg1.recent_pregnancy as recent_pregnancy1
, gpr_recpreg2.recent_pregnancy as recent_pregnancy2
, gpr_gdm.current_gdm
, gpr_recgdm1.recent_gdm as recent_gdm1
, gpr_recgdm2.recent_gdm as recent_gdm2
, gpr_bp1.max_bp_systolic as max_bp_systolic1
, gpr_bp1.max_bp_diastolic as max_bp_diastolic1
, gpr_bp1.map as map1
, gpr_bp1.syspct as syspct1
, gpr_bp1.diapct as diapct1
, gpr_bp2.max_bp_systolic as max_bp_systolic2
, gpr_bp2.max_bp_diastolic as max_bp_diastolic2
, gpr_bp2.map as map2
, gpr_bp2.syspct as syspct2
, gpr_bp2.diapct as diapct2
, gpr_bp3.max_bp_systolic as max_bp_systolic3
, gpr_bp3.max_bp_diastolic as max_bp_diastolic3
, gpr_bp3.map as map3 
, gpr_bp3.syspct as syspct3
, gpr_bp3.diapct as diapct3
, gpr_recbp.bp_systolic
, gpr_recbp.bp_diastolic
, gpr_recbp.date as rec_bp_date
, gpr_recbp.map 
, gpr_recbp.syspct
, gpr_recbp.diapct
, gpr_ldl.recent_ldl
, gpr_ldl.date as ldl_date
, gpr_ldl1.max_ldl1
, gpr_ldl2.max_ldl2
, gpr_ldl3.max_ldl3
, gpr_a1c.recent_a1c
, gpr_a1c.date as a1c_date
, gpr_a1c1.max_a1c1
, gpr_a1c2.max_a1c2
, gpr_a1c3.max_a1c3
, gpr_trig.recent_tgl
, gpr_trig.date as trig_date
, gpr_trig1.max_trig1
, gpr_trig2.max_trig2
, gpr_trig3.max_trig3
, gpr_predm.prediabetes
, gpr_type1.type_1_diabetes
, gpr_type2.type_2_diabetes
, gpr_insulin.insulin
, gpr_metformin.metformin
, gpr_flu_cur.influenza_vaccine as cur_flu_vax
, gpr_flu_prev.influenza_vaccine as prev_flu_vax
, gpr_chlamydia.recent_chlamydia
, gpr_asthma.asthma
, gpr_smoking.smoking
, gpr_enc.nvis
, gpr_depression.depression
, gpr_opi.any_opi
, gpr_opi.any_benzo
, gpr_opi.concur_opi_benzo
, gpr_opi.high_dose_opi
FROM gpr_pat 
--
-- Max blood pressure between two and three years
--  using most recent max mean aterial pressure for the period
--
LEFT JOIN gpr_bp3
	ON gpr_bp3.patient_id = gpr_pat.patient_id
--
-- Max blood pressure between one and two years
--  using most recent max mean aterial pressure for the period
--
LEFT JOIN gpr_bp2
	ON gpr_bp2.patient_id = gpr_pat.patient_id
--
-- Max blood pressure between now and one years
--  using most recent max mean aterial pressure for the period
--
LEFT JOIN gpr_bp1
	ON gpr_bp1.patient_id = gpr_pat.patient_id
--
-- most recent blood pressure 
--
LEFT JOIN gpr_recbp
	ON gpr_recbp.patient_id = gpr_pat.patient_id
--
-- most recent BMI 
--
LEFT JOIN gpr_bmi
	ON gpr_bmi.patient_id = gpr_pat.patient_id
--
-- Recent A1C lab result
--
LEFT JOIN gpr_a1c
	ON gpr_a1c.patient_id = gpr_pat.patient_id
--
-- Max A1C lab result last year
--
LEFT JOIN gpr_a1c1
	ON gpr_a1c1.patient_id = gpr_pat.patient_id
--
-- Max A1C lab result between 1 and 2 years ago
--
LEFT JOIN gpr_a1c2
	ON gpr_a1c2.patient_id = gpr_pat.patient_id
--
-- Max A1C lab result between 2 and 3 years ago
--
LEFT JOIN gpr_a1c3
	ON gpr_a1c3.patient_id = gpr_pat.patient_id
--
-- Recent cholesterol LDL lab result
--
LEFT JOIN gpr_ldl
	ON gpr_ldl.patient_id = gpr_pat.patient_id
--
-- Max ldl lab result last year
--
LEFT JOIN gpr_ldl1
	ON gpr_ldl1.patient_id = gpr_pat.patient_id
--
-- Max ldl lab result between 1 and 2 years ago
--
LEFT JOIN gpr_ldl2
	ON gpr_ldl2.patient_id = gpr_pat.patient_id
--
-- Max ldl lab result between 2 and 3 years ago
--
LEFT JOIN gpr_ldl3
	ON gpr_ldl3.patient_id = gpr_pat.patient_id
--
-- Recent Triglycerides lab result
--
LEFT JOIN gpr_trig
	ON gpr_trig.patient_id = gpr_pat.patient_id
--
-- Max trig lab result last year
--
LEFT JOIN gpr_trig1
	ON gpr_trig1.patient_id = gpr_pat.patient_id
--
-- Max trig lab result between 1 and 2 years ago
--
LEFT JOIN gpr_trig2
	ON gpr_trig2.patient_id = gpr_pat.patient_id
--
-- Max trig lab result between 2 and 3 years ago
--
LEFT JOIN gpr_trig3
	ON gpr_trig3.patient_id = gpr_pat.patient_id
--
-- Prediabetes
--
LEFT JOIN gpr_predm
	ON gpr_predm.patient_id = gpr_pat.patient_id
--
-- Type 1 Diabetes
--
LEFT JOIN gpr_type1
	ON gpr_type1.patient_id = gpr_pat.patient_id

--
-- Type 2 Diabetes
--
LEFT JOIN gpr_type2
	ON gpr_type2.patient_id = gpr_pat.patient_id

--
-- Current Gestational diabetes
--
LEFT JOIN gpr_gdm
	ON gpr_gdm.patient_id = gpr_pat.patient_id
--
-- Recent Gestational diabetes 1 year
--
LEFT JOIN gpr_recgdm1
	ON gpr_recgdm1.patient_id = gpr_pat.patient_id
--
-- Recent Gestational diabetes 2 year
--
LEFT JOIN gpr_recgdm2
	ON gpr_recgdm2.patient_id = gpr_pat.patient_id
--
-- Recent pregnancy 2 year
--
LEFT JOIN gpr_recpreg2
	ON gpr_recpreg2.patient_id = gpr_pat.patient_id
--
-- Recent pregnancy 1 year
--
LEFT JOIN gpr_recpreg1
	ON gpr_recpreg1.patient_id = gpr_pat.patient_id
--
-- Current pregnancy
--
LEFT JOIN gpr_curpreg
	ON gpr_curpreg.patient_id = gpr_pat.patient_id
--
-- Insulin
--    Prescription for insulin within the previous year
--
LEFT JOIN gpr_insulin
	ON gpr_insulin.patient_id = gpr_pat.patient_id
--
-- Metformin
--     Prescription for metformin within the previous year
--
LEFT JOIN gpr_metformin
	ON gpr_metformin.patient_id = gpr_pat.patient_id
--
-- Influenza vaccine
--     Prescription for influenza vaccine current flu season
--
LEFT JOIN gpr_flu_cur
	ON gpr_flu_cur.patient_id = gpr_pat.patient_id
--
-- Influenza vaccine
--     Prescription for influenza vaccine previous flu season
--
LEFT JOIN gpr_flu_prev
	ON gpr_flu_prev.patient_id = gpr_pat.patient_id
--
-- Most recent chlamydia test
--
LEFT JOIN gpr_chlamydia
	ON gpr_chlamydia.patient_id = gpr_pat.patient_id
--
-- Smoking
--
LEFT JOIN gpr_smoking 
        ON gpr_smoking.patient_id = gpr_pat.patient_id
--
-- asthma
--
LEFT JOIN gpr_asthma
        on gpr_asthma.patient_id = gpr_pat.patient_id
--
-- n visits
--
LEFT JOIN gpr_enc
        on gpr_enc.patient_id = gpr_pat.patient_id
--
-- depression
--
LEFT JOIN gpr_depression
        on gpr_depression.patient_id = gpr_pat.patient_id

--
-- Opioid
--
LEFT JOIN gpr_opi
        on gpr_opi.patient_id = gpr_pat.patient_id

--
-- Ordering
--
ORDER BY gpr_pat.patient_id
;
