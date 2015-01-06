
--
-- PostgreSQL database dump
--

-- Started on 2012-02-09 08:23:16 PST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

--
-- TOC entry 2202 (class 0 OID 0)
-- Dependencies: 1789
-- Name: static_fakevitals_fakevitals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: esp
--

SELECT pg_catalog.setval('static_fakevitals_fakevitals_id_seq', 8, true);


--
-- TOC entry 2199 (class 0 OID 220590)
-- Dependencies: 1790
-- Data for Name: static_fakevitals; Type: TABLE DATA; Schema: public; Owner: esp
--

INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (1, 'bmi', 'body mass index', 18, 25, 'unit', 16, 40);
INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (2, 'temp', 'temperature', 97, 99, 'deg F', 94, 102);
INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (3, 'weight', 'body weight', 118, 180, 'lb', 100, 300);
INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (4, 'height', 'body height', 60, 78, 'inches', 36, 84);
INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (5, 'bp_systolic', NULL, 90, 120, 'mmHg', 80, 140);
INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (6, 'bp_diastolic', NULL, 60, 80, 'mmHg', 50, 90);
INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (7, 'o2_stat', 'oxygen saturation', 95, 99, '%', 90, 100);
INSERT INTO static_fakevitals (fakevitals_id, short_name, long_name, normal_low, normal_high, units, very_low, very_high) VALUES (8, 'peak_flow', 'peak expiratory flow', 400, 600, 'L/min', 200, 700);


-- Completed on 2012-02-09 08:23:16 PST

--
-- PostgreSQL database dump complete
--
