--
-- PostgreSQL database dump
--
--TODO split this file into separate ones for each of the tables that it fills out.
-- Started on 2012-02-09 08:22:27 PST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

--
-- TOC entry 2202 (class 0 OID 0)
-- Dependencies: 1787
-- Name: static_fakelabs_fakelabs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: esp
--

SELECT pg_catalog.setval('static_fakelabs_fakelabs_id_seq', 117, true);


--
-- TOC entry 2199 (class 0 OID 220579)
-- Dependencies: 1788
-- Data for Name: static_fakelabs; Type: TABLE DATA; Schema: public; Owner: esp
--

INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (66, 'BILI_IND', 'total bilirubin indirect', 'Numeric', 0.29999999999999999, 1, 'mg/dL', 0.01, 3, '80076', NULL, NULL, '80076--478');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (68, 'hitobilidi', 'high total direct bilirun', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '80076', 'true;false;yes;no', NULL, '80076--206');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (69, 'CREATININE', 'creatinine', 'Numeric', 0.5, 1.5, 'mg/dL', 0.10000000000000001, 50, '82565', NULL, NULL, '82565:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (70, 'CREAT', 'creatinine', 'Numeric', 0.5, 1.5, 'mg/dL', 0.10000000000000001, 50, '82565', NULL, NULL, '82565:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (71, 'CREG', 'creatinine', 'Numeric', 0.5, 1.5, 'mg/dL', 0.10000000000000001, 50, '82565', NULL, NULL, '82565:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (72, 'HGBA1C', 'hemoglobin A1C', 'Numeric (percentage)', 4, 6, '%', 2, 20, '83036', NULL, NULL, '83036:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (73, 'HBA1c', 'hemoglobin A1C', 'Numeric (percentage)', 4, 6, '%', 2, 20, '83036', NULL, NULL, '83036:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (74, 'A1C', 'hemoglobin A1C', 'Numeric (percentage)', 4, 6, '%', 2, 20, '83036', NULL, NULL, '83036:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (75, 'LIPASE', 'lipase', 'Numeric', 7, 60, 'U/L', 0, 200, '83690', NULL, NULL, '83690:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (76, 'ALP', 'alkaline phosphatase', 'Numeric', 30, 120, 'IU/L', 10, 3000, '84075', NULL, NULL, '84075:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (77, 'ALK PHOS', 'alkaline phosphatase', 'Numeric', 30, 120, 'IU/L', 10, 3000, '84075', NULL, NULL, '84075:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (80, 'SGPT', 'alanine aminotransferase', 'Numeric', 10, 65, 'IU/L', 1, 400, '84460', NULL, NULL, '84460:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (81, 'HGB', 'hemoglobin', 'Numeric', 12, 16, 'g/dL', 1, 25, '85018', NULL, NULL, '85018:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (82, 'Hemaglobin', 'hemoglobin', 'Numeric', 12, 16, 'g/dL', 1, 25, '85018', NULL, NULL, '85018:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (83, 'ANC', 'absolute neutrophil count', 'Numeric', 1500, 8000, '/mm3', 500, 10000, '85025', NULL, NULL, '85025:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (84, 'D_DIMER', 'd dimer', 'Numeric', 100, 500, 'ng/ml', 0, 2000, '85379', NULL, NULL, '85379:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (85, 'INR', 'international normalised ratio?', 'Numeric', 0.90000000000000002, 1.3, '(none)', 0.5, 20, '85610', NULL, NULL, '85610:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (86, 'rpr', 'RPR test', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86593', '1:1;1:2;1:4;1:8;1:16;1:32;1:64;1;128;1:256;1:512;1:1024', NULL, '86593:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (87, 'lymwbg', 'lyme Western Blot', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86617', 'pos;neg', NULL, '86617:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (88, 'lymelisa', 'lyme ELISA', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86618', 'confirm;not', NULL, '86618:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (89, 'lymigg', 'lyme IGG', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86618', 'pos;neg', NULL, '86618:2');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (90, 'lymem', 'Lyme IGM (EIA)', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86618', 'pos;neg', NULL, '86618:3');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (96, 'ttpa', 'TTPA test', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86780', 'pos;neg', NULL, '86780:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (97, 'fta_abs', 'FTA-ABS test', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86780', 'pos;neg', NULL, '86780:2');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (98, 'hepeab', 'hepatitis E antibody', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86790', 'reactiv;nr', NULL, '86790:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (102, 'gon', 'gonorrhea', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87081', 'pos;neg', NULL, '87081:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (103, 'chlam', 'chlamydia', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87081', 'pos;neg', NULL, '87081:2');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (104, 'perc', 'Culture for pertussis', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87081', 'pos;neg', NULL, '87081:3');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (105, 'tb_lab', 'Tuberculosis lab order', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87116', 'pos;neg', NULL, '87116:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (106, 'giardiasis_antigen', 'Giardiasis Antigen', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87329', 'detec;non', NULL, '87329:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (108, 'lympcr', 'lyme PCR', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87476', 'reactiv;nr', NULL, '87476:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (111, 'rperpc', 'Pertussis PCR test', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87798', 'pos;neg', NULL, '87798:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (101, 'hepcriba', 'hepatitis C RIBA', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86804', 'pos;neg', NULL, '86804--1867');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (99, 'hepcsco', 'hepatitis c signal cutoff', 'Numeric', 1, 3.7999999999999998, NULL, 0, 15, '80074', NULL, NULL, '80074--251');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (93, 'hepbsag', 'hepatitis B surface antigen', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '80055', 'confirm;not', NULL, '80055--223');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (91, 'hepbcigm', 'hepatitis B core igm antibody', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86705', 'reactiv;nr', NULL, '86705--4870');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (107, 'hepbeag', 'hepatitis B e antigen', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87350', 'pos;neg', NULL, '87350:1');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (92, 'hepbca ', 'hepatitis B core general antibody', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86705', 'pos;neg', NULL, '86705--4');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (94, 'hep_a_igm', 'hepatitis A IGM antibody', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86705', 'detec;non', NULL, '86705--4329');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (100, 'hepcelisa', 'hepatitis C ELISA, ab', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '86803', 'pos;neg', NULL, '86803--217');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (79, 'alt', 'alanine aminotransferase', 'Numeric', 10, 65, 'IU/L', 1, 400, '84460', NULL, NULL, '84460--1728');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (95, 'hepav_tot', 'hepatitis A total antibody', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '80074', 'pos;neg', NULL, '80074--213');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (110, 'hepcrna', 'hepatitis C RNA', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87522', 'pos;neg', NULL, '87522--1627');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (67, 'TBIL', 'total bilirubin', 'Numeric', 0.29999999999999999, 1, 'mg/dL', 0.01, 3, '82247', NULL, NULL, '82247--2893');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (78, 'ast', 'blood ast level', NULL, 10, 40, 'IU/L', 1, 200, '82947', NULL, NULL, '82947--57');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (109, 'hepbvdna', 'hepatitis B viral dna', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '87517', 'pos;neg', NULL, '87517--7643');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (112, 'fasting glucose', 'fasting glucose', 'Numeric', 20, 99, NULL, 10, 200, '82948', NULL, NULL, '82948:560');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (113, 'random glucose', 'random glucose', 'Numeric', 20, 99, NULL, 10, 300, '82947', NULL, NULL, '82947:1795');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (117, 'ogtt 100 fasting urine', 'component Positive OGTT 100', 'Qualitative', NULL, NULL, NULL, NULL, NULL, '82951', 'pos;neg', NULL, '82951:64');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (116, 'ogtt 100 2h', 'ogtt glucose test 100', 'Numeric', 30, 180, 'u', 10, 190, '82951', NULL, NULL, '82951:159');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (114, 'ogtt 50 random', 'oggtt glucose test 50 random', 'Numeric', 30, 180, 'u', 10, 190, '82950', NULL, NULL, '82950:161');
INSERT INTO static_fakelabs (fakelabs_id, short_name, long_name, data_type, normal_low, normal_high, units, very_low, very_high, cpt_code, qualitative_values, weight, native_code) VALUES (115, 'ogtt 75 1h', 'ogtt glucose test 75', 'Numeric', 30, 180, 'uu', 10, 190, '82951', NULL, NULL, '82951:2862');


