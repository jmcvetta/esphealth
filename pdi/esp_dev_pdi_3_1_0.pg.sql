--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: r_cluster; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_cluster (
    id_cluster bigint NOT NULL,
    name character varying(255),
    base_port character varying(255),
    sockets_buffer_size character varying(255),
    sockets_flush_interval character varying(255),
    sockets_compressed character(1)
);


ALTER TABLE public.r_cluster OWNER TO pdi;

--
-- Name: r_cluster_id_cluster_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_cluster_id_cluster_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_cluster_id_cluster_seq OWNER TO pdi;

--
-- Name: r_cluster_id_cluster_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_cluster_id_cluster_seq OWNED BY r_cluster.id_cluster;


--
-- Name: r_cluster_id_cluster_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_cluster_id_cluster_seq', 1, false);


--
-- Name: r_cluster_slave; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_cluster_slave (
    id_cluster_slave bigint NOT NULL,
    id_cluster integer,
    id_slave integer
);


ALTER TABLE public.r_cluster_slave OWNER TO pdi;

--
-- Name: r_cluster_slave_id_cluster_slave_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_cluster_slave_id_cluster_slave_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_cluster_slave_id_cluster_slave_seq OWNER TO pdi;

--
-- Name: r_cluster_slave_id_cluster_slave_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_cluster_slave_id_cluster_slave_seq OWNED BY r_cluster_slave.id_cluster_slave;


--
-- Name: r_cluster_slave_id_cluster_slave_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_cluster_slave_id_cluster_slave_seq', 1, false);


--
-- Name: r_condition; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_condition (
    id_condition bigint NOT NULL,
    id_condition_parent integer,
    negated character(1),
    operator character varying(255),
    left_name character varying(255),
    condition_function character varying(255),
    right_name character varying(255),
    id_value_right integer
);


ALTER TABLE public.r_condition OWNER TO pdi;

--
-- Name: r_condition_id_condition_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_condition_id_condition_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_condition_id_condition_seq OWNER TO pdi;

--
-- Name: r_condition_id_condition_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_condition_id_condition_seq OWNED BY r_condition.id_condition;


--
-- Name: r_condition_id_condition_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_condition_id_condition_seq', 1, false);


--
-- Name: r_database; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_database (
    id_database bigint NOT NULL,
    name character varying(255),
    id_database_type integer,
    id_database_contype integer,
    host_name character varying(255),
    database_name character varying(255),
    port integer,
    username character varying(255),
    password character varying(255),
    servername character varying(255),
    data_tbs character varying(255),
    index_tbs character varying(255)
);


ALTER TABLE public.r_database OWNER TO pdi;

--
-- Name: r_database_attribute; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_database_attribute (
    id_database_attribute bigint NOT NULL,
    id_database integer,
    code character varying(255),
    value_str character varying(2000000)
);


ALTER TABLE public.r_database_attribute OWNER TO pdi;

--
-- Name: r_database_attribute_id_database_attribute_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_database_attribute_id_database_attribute_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_database_attribute_id_database_attribute_seq OWNER TO pdi;

--
-- Name: r_database_attribute_id_database_attribute_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_database_attribute_id_database_attribute_seq OWNED BY r_database_attribute.id_database_attribute;


--
-- Name: r_database_attribute_id_database_attribute_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_database_attribute_id_database_attribute_seq', 1, false);


--
-- Name: r_database_contype; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_database_contype (
    id_database_contype bigint NOT NULL,
    code character varying(255),
    description character varying(255)
);


ALTER TABLE public.r_database_contype OWNER TO pdi;

--
-- Name: r_database_contype_id_database_contype_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_database_contype_id_database_contype_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_database_contype_id_database_contype_seq OWNER TO pdi;

--
-- Name: r_database_contype_id_database_contype_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_database_contype_id_database_contype_seq OWNED BY r_database_contype.id_database_contype;


--
-- Name: r_database_contype_id_database_contype_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_database_contype_id_database_contype_seq', 1, false);


--
-- Name: r_database_id_database_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_database_id_database_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_database_id_database_seq OWNER TO pdi;

--
-- Name: r_database_id_database_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_database_id_database_seq OWNED BY r_database.id_database;


--
-- Name: r_database_id_database_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_database_id_database_seq', 1, false);


--
-- Name: r_database_type; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_database_type (
    id_database_type bigint NOT NULL,
    code character varying(255),
    description character varying(255)
);


ALTER TABLE public.r_database_type OWNER TO pdi;

--
-- Name: r_database_type_id_database_type_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_database_type_id_database_type_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_database_type_id_database_type_seq OWNER TO pdi;

--
-- Name: r_database_type_id_database_type_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_database_type_id_database_type_seq OWNED BY r_database_type.id_database_type;


--
-- Name: r_database_type_id_database_type_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_database_type_id_database_type_seq', 1, false);


--
-- Name: r_dependency; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_dependency (
    id_dependency bigint NOT NULL,
    id_transformation integer,
    id_database integer,
    table_name character varying(255),
    field_name character varying(255)
);


ALTER TABLE public.r_dependency OWNER TO pdi;

--
-- Name: r_dependency_id_dependency_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_dependency_id_dependency_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_dependency_id_dependency_seq OWNER TO pdi;

--
-- Name: r_dependency_id_dependency_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_dependency_id_dependency_seq OWNED BY r_dependency.id_dependency;


--
-- Name: r_dependency_id_dependency_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_dependency_id_dependency_seq', 1, false);


--
-- Name: r_directory; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_directory (
    id_directory bigint NOT NULL,
    id_directory_parent integer,
    directory_name character varying(255)
);


ALTER TABLE public.r_directory OWNER TO pdi;

--
-- Name: r_directory_id_directory_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_directory_id_directory_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_directory_id_directory_seq OWNER TO pdi;

--
-- Name: r_directory_id_directory_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_directory_id_directory_seq OWNED BY r_directory.id_directory;


--
-- Name: r_directory_id_directory_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_directory_id_directory_seq', 1, false);


--
-- Name: r_job; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_job (
    id_job bigint NOT NULL,
    id_directory integer,
    name character varying(255),
    description character varying(2000000),
    extended_description character varying(2000000),
    job_version character varying(255),
    job_status integer,
    id_database_log integer,
    table_name_log character varying(255),
    created_user character varying(255),
    created_date timestamp without time zone,
    modified_user character varying(255),
    modified_date timestamp without time zone,
    use_batch_id character(1),
    pass_batch_id character(1),
    use_logfield character(1),
    shared_file character varying(255)
);


ALTER TABLE public.r_job OWNER TO pdi;

--
-- Name: r_job_hop; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_job_hop (
    id_job_hop bigint NOT NULL,
    id_job integer,
    id_jobentry_copy_from integer,
    id_jobentry_copy_to integer,
    enabled character(1),
    evaluation character(1),
    unconditional character(1)
);


ALTER TABLE public.r_job_hop OWNER TO pdi;

--
-- Name: r_job_hop_id_job_hop_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_job_hop_id_job_hop_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_job_hop_id_job_hop_seq OWNER TO pdi;

--
-- Name: r_job_hop_id_job_hop_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_job_hop_id_job_hop_seq OWNED BY r_job_hop.id_job_hop;


--
-- Name: r_job_hop_id_job_hop_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_job_hop_id_job_hop_seq', 1, false);


--
-- Name: r_job_id_job_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_job_id_job_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_job_id_job_seq OWNER TO pdi;

--
-- Name: r_job_id_job_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_job_id_job_seq OWNED BY r_job.id_job;


--
-- Name: r_job_id_job_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_job_id_job_seq', 1, false);


--
-- Name: r_job_note; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_job_note (
    id_job integer,
    id_note integer
);


ALTER TABLE public.r_job_note OWNER TO pdi;

--
-- Name: r_jobentry; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_jobentry (
    id_jobentry bigint NOT NULL,
    id_job integer,
    id_jobentry_type integer,
    name character varying(255),
    description character varying(2000000)
);


ALTER TABLE public.r_jobentry OWNER TO pdi;

--
-- Name: r_jobentry_attribute; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_jobentry_attribute (
    id_jobentry_attribute bigint NOT NULL,
    id_job integer,
    id_jobentry integer,
    nr integer,
    code character varying(255),
    value_num numeric(13,2),
    value_str character varying(2000000)
);


ALTER TABLE public.r_jobentry_attribute OWNER TO pdi;

--
-- Name: r_jobentry_attribute_id_jobentry_attribute_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_jobentry_attribute_id_jobentry_attribute_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_jobentry_attribute_id_jobentry_attribute_seq OWNER TO pdi;

--
-- Name: r_jobentry_attribute_id_jobentry_attribute_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_jobentry_attribute_id_jobentry_attribute_seq OWNED BY r_jobentry_attribute.id_jobentry_attribute;


--
-- Name: r_jobentry_attribute_id_jobentry_attribute_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_jobentry_attribute_id_jobentry_attribute_seq', 1, false);


--
-- Name: r_jobentry_copy; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_jobentry_copy (
    id_jobentry_copy bigint NOT NULL,
    id_jobentry integer,
    id_job integer,
    id_jobentry_type integer,
    nr smallint,
    gui_location_x integer,
    gui_location_y integer,
    gui_draw character(1),
    parallel character(1)
);


ALTER TABLE public.r_jobentry_copy OWNER TO pdi;

--
-- Name: r_jobentry_copy_id_jobentry_copy_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_jobentry_copy_id_jobentry_copy_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_jobentry_copy_id_jobentry_copy_seq OWNER TO pdi;

--
-- Name: r_jobentry_copy_id_jobentry_copy_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_jobentry_copy_id_jobentry_copy_seq OWNED BY r_jobentry_copy.id_jobentry_copy;


--
-- Name: r_jobentry_copy_id_jobentry_copy_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_jobentry_copy_id_jobentry_copy_seq', 1, false);


--
-- Name: r_jobentry_id_jobentry_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_jobentry_id_jobentry_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_jobentry_id_jobentry_seq OWNER TO pdi;

--
-- Name: r_jobentry_id_jobentry_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_jobentry_id_jobentry_seq OWNED BY r_jobentry.id_jobentry;


--
-- Name: r_jobentry_id_jobentry_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_jobentry_id_jobentry_seq', 1, false);


--
-- Name: r_jobentry_type; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_jobentry_type (
    id_jobentry_type bigint NOT NULL,
    code character varying(255),
    description character varying(255)
);


ALTER TABLE public.r_jobentry_type OWNER TO pdi;

--
-- Name: r_jobentry_type_id_jobentry_type_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_jobentry_type_id_jobentry_type_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_jobentry_type_id_jobentry_type_seq OWNER TO pdi;

--
-- Name: r_jobentry_type_id_jobentry_type_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_jobentry_type_id_jobentry_type_seq OWNED BY r_jobentry_type.id_jobentry_type;


--
-- Name: r_jobentry_type_id_jobentry_type_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_jobentry_type_id_jobentry_type_seq', 1, false);


--
-- Name: r_log; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_log (
    id_log bigint NOT NULL,
    name character varying(255),
    id_loglevel integer,
    logtype character varying(255),
    filename character varying(255),
    fileextention character varying(255),
    add_date character(1),
    add_time character(1),
    id_database_log integer,
    table_name_log character varying(255)
);


ALTER TABLE public.r_log OWNER TO pdi;

--
-- Name: r_log_id_log_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_log_id_log_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_log_id_log_seq OWNER TO pdi;

--
-- Name: r_log_id_log_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_log_id_log_seq OWNED BY r_log.id_log;


--
-- Name: r_log_id_log_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_log_id_log_seq', 1, false);


--
-- Name: r_loglevel; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_loglevel (
    id_loglevel bigint NOT NULL,
    code character varying(255),
    description character varying(255)
);


ALTER TABLE public.r_loglevel OWNER TO pdi;

--
-- Name: r_loglevel_id_loglevel_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_loglevel_id_loglevel_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_loglevel_id_loglevel_seq OWNER TO pdi;

--
-- Name: r_loglevel_id_loglevel_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_loglevel_id_loglevel_seq OWNED BY r_loglevel.id_loglevel;


--
-- Name: r_loglevel_id_loglevel_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_loglevel_id_loglevel_seq', 1, false);


--
-- Name: r_note; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_note (
    id_note bigint NOT NULL,
    value_str character varying(2000000),
    gui_location_x integer,
    gui_location_y integer,
    gui_location_width integer,
    gui_location_height integer
);


ALTER TABLE public.r_note OWNER TO pdi;

--
-- Name: r_note_id_note_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_note_id_note_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_note_id_note_seq OWNER TO pdi;

--
-- Name: r_note_id_note_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_note_id_note_seq OWNED BY r_note.id_note;


--
-- Name: r_note_id_note_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_note_id_note_seq', 1, false);


--
-- Name: r_partition; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_partition (
    id_partition bigint NOT NULL,
    id_partition_schema integer,
    partition_id character varying(255)
);


ALTER TABLE public.r_partition OWNER TO pdi;

--
-- Name: r_partition_id_partition_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_partition_id_partition_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_partition_id_partition_seq OWNER TO pdi;

--
-- Name: r_partition_id_partition_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_partition_id_partition_seq OWNED BY r_partition.id_partition;


--
-- Name: r_partition_id_partition_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_partition_id_partition_seq', 1, false);


--
-- Name: r_partition_schema; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_partition_schema (
    id_partition_schema bigint NOT NULL,
    name character varying(255),
    dynamic_definition character(1),
    partitions_per_slave character varying(255)
);


ALTER TABLE public.r_partition_schema OWNER TO pdi;

--
-- Name: r_partition_schema_id_partition_schema_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_partition_schema_id_partition_schema_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_partition_schema_id_partition_schema_seq OWNER TO pdi;

--
-- Name: r_partition_schema_id_partition_schema_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_partition_schema_id_partition_schema_seq OWNED BY r_partition_schema.id_partition_schema;


--
-- Name: r_partition_schema_id_partition_schema_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_partition_schema_id_partition_schema_seq', 1, false);


--
-- Name: r_permission; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_permission (
    id_permission bigint NOT NULL,
    code character varying(255),
    description character varying(255)
);


ALTER TABLE public.r_permission OWNER TO pdi;

--
-- Name: r_permission_id_permission_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_permission_id_permission_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_permission_id_permission_seq OWNER TO pdi;

--
-- Name: r_permission_id_permission_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_permission_id_permission_seq OWNED BY r_permission.id_permission;


--
-- Name: r_permission_id_permission_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_permission_id_permission_seq', 1, false);


--
-- Name: r_profile; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_profile (
    id_profile bigint NOT NULL,
    name character varying(255),
    description character varying(255)
);


ALTER TABLE public.r_profile OWNER TO pdi;

--
-- Name: r_profile_id_profile_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_profile_id_profile_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_profile_id_profile_seq OWNER TO pdi;

--
-- Name: r_profile_id_profile_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_profile_id_profile_seq OWNED BY r_profile.id_profile;


--
-- Name: r_profile_id_profile_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_profile_id_profile_seq', 1, false);


--
-- Name: r_profile_permission; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_profile_permission (
    id_profile integer,
    id_permission integer
);


ALTER TABLE public.r_profile_permission OWNER TO pdi;

--
-- Name: r_repository_log; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_repository_log (
    id_repository_log bigint NOT NULL,
    rep_version character varying(255),
    log_date timestamp without time zone,
    log_user character varying(255),
    operation_desc character varying(2000000)
);


ALTER TABLE public.r_repository_log OWNER TO pdi;

--
-- Name: r_repository_log_id_repository_log_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_repository_log_id_repository_log_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_repository_log_id_repository_log_seq OWNER TO pdi;

--
-- Name: r_repository_log_id_repository_log_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_repository_log_id_repository_log_seq OWNED BY r_repository_log.id_repository_log;


--
-- Name: r_repository_log_id_repository_log_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_repository_log_id_repository_log_seq', 1, false);


--
-- Name: r_slave; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_slave (
    id_slave bigint NOT NULL,
    name character varying(255),
    host_name character varying(255),
    port character varying(255),
    username character varying(255),
    password character varying(255),
    proxy_host_name character varying(255),
    proxy_port character varying(255),
    non_proxy_hosts character varying(255),
    master character(1)
);


ALTER TABLE public.r_slave OWNER TO pdi;

--
-- Name: r_slave_id_slave_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_slave_id_slave_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_slave_id_slave_seq OWNER TO pdi;

--
-- Name: r_slave_id_slave_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_slave_id_slave_seq OWNED BY r_slave.id_slave;


--
-- Name: r_slave_id_slave_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_slave_id_slave_seq', 1, false);


--
-- Name: r_step; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_step (
    id_step bigint NOT NULL,
    id_transformation integer,
    name character varying(255),
    description character varying(2000000),
    id_step_type integer,
    distribute character(1),
    copies smallint,
    gui_location_x integer,
    gui_location_y integer,
    gui_draw character(1)
);


ALTER TABLE public.r_step OWNER TO pdi;

--
-- Name: r_step_attribute; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_step_attribute (
    id_step_attribute bigint NOT NULL,
    id_transformation integer,
    id_step integer,
    nr integer,
    code character varying(255),
    value_num bigint,
    value_str character varying(2000000)
);


ALTER TABLE public.r_step_attribute OWNER TO pdi;

--
-- Name: r_step_attribute_id_step_attribute_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_step_attribute_id_step_attribute_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_step_attribute_id_step_attribute_seq OWNER TO pdi;

--
-- Name: r_step_attribute_id_step_attribute_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_step_attribute_id_step_attribute_seq OWNED BY r_step_attribute.id_step_attribute;


--
-- Name: r_step_attribute_id_step_attribute_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_step_attribute_id_step_attribute_seq', 1, false);


--
-- Name: r_step_database; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_step_database (
    id_transformation integer,
    id_step integer,
    id_database integer
);


ALTER TABLE public.r_step_database OWNER TO pdi;

--
-- Name: r_step_id_step_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_step_id_step_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_step_id_step_seq OWNER TO pdi;

--
-- Name: r_step_id_step_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_step_id_step_seq OWNED BY r_step.id_step;


--
-- Name: r_step_id_step_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_step_id_step_seq', 1, false);


--
-- Name: r_step_type; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_step_type (
    id_step_type bigint NOT NULL,
    code character varying(255),
    description character varying(255),
    helptext character varying(255)
);


ALTER TABLE public.r_step_type OWNER TO pdi;

--
-- Name: r_step_type_id_step_type_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_step_type_id_step_type_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_step_type_id_step_type_seq OWNER TO pdi;

--
-- Name: r_step_type_id_step_type_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_step_type_id_step_type_seq OWNED BY r_step_type.id_step_type;


--
-- Name: r_step_type_id_step_type_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_step_type_id_step_type_seq', 1, false);


--
-- Name: r_trans_attribute; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_trans_attribute (
    id_trans_attribute bigint NOT NULL,
    id_transformation integer,
    nr integer,
    code character varying(255),
    value_num bigint,
    value_str character varying(2000000)
);


ALTER TABLE public.r_trans_attribute OWNER TO pdi;

--
-- Name: r_trans_attribute_id_trans_attribute_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_trans_attribute_id_trans_attribute_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_trans_attribute_id_trans_attribute_seq OWNER TO pdi;

--
-- Name: r_trans_attribute_id_trans_attribute_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_trans_attribute_id_trans_attribute_seq OWNED BY r_trans_attribute.id_trans_attribute;


--
-- Name: r_trans_attribute_id_trans_attribute_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_trans_attribute_id_trans_attribute_seq', 1, false);


--
-- Name: r_trans_cluster; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_trans_cluster (
    id_trans_cluster bigint NOT NULL,
    id_transformation integer,
    id_cluster integer
);


ALTER TABLE public.r_trans_cluster OWNER TO pdi;

--
-- Name: r_trans_cluster_id_trans_cluster_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_trans_cluster_id_trans_cluster_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_trans_cluster_id_trans_cluster_seq OWNER TO pdi;

--
-- Name: r_trans_cluster_id_trans_cluster_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_trans_cluster_id_trans_cluster_seq OWNED BY r_trans_cluster.id_trans_cluster;


--
-- Name: r_trans_cluster_id_trans_cluster_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_trans_cluster_id_trans_cluster_seq', 1, false);


--
-- Name: r_trans_hop; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_trans_hop (
    id_trans_hop bigint NOT NULL,
    id_transformation integer,
    id_step_from integer,
    id_step_to integer,
    enabled character(1)
);


ALTER TABLE public.r_trans_hop OWNER TO pdi;

--
-- Name: r_trans_hop_id_trans_hop_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_trans_hop_id_trans_hop_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_trans_hop_id_trans_hop_seq OWNER TO pdi;

--
-- Name: r_trans_hop_id_trans_hop_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_trans_hop_id_trans_hop_seq OWNED BY r_trans_hop.id_trans_hop;


--
-- Name: r_trans_hop_id_trans_hop_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_trans_hop_id_trans_hop_seq', 1, false);


--
-- Name: r_trans_note; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_trans_note (
    id_transformation integer,
    id_note integer
);


ALTER TABLE public.r_trans_note OWNER TO pdi;

--
-- Name: r_trans_partition_schema; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_trans_partition_schema (
    id_trans_partition_schema bigint NOT NULL,
    id_transformation integer,
    id_partition_schema integer
);


ALTER TABLE public.r_trans_partition_schema OWNER TO pdi;

--
-- Name: r_trans_partition_schema_id_trans_partition_schema_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_trans_partition_schema_id_trans_partition_schema_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_trans_partition_schema_id_trans_partition_schema_seq OWNER TO pdi;

--
-- Name: r_trans_partition_schema_id_trans_partition_schema_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_trans_partition_schema_id_trans_partition_schema_seq OWNED BY r_trans_partition_schema.id_trans_partition_schema;


--
-- Name: r_trans_partition_schema_id_trans_partition_schema_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_trans_partition_schema_id_trans_partition_schema_seq', 1, false);


--
-- Name: r_trans_slave; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_trans_slave (
    id_trans_slave bigint NOT NULL,
    id_transformation integer,
    id_slave integer
);


ALTER TABLE public.r_trans_slave OWNER TO pdi;

--
-- Name: r_trans_slave_id_trans_slave_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_trans_slave_id_trans_slave_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_trans_slave_id_trans_slave_seq OWNER TO pdi;

--
-- Name: r_trans_slave_id_trans_slave_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_trans_slave_id_trans_slave_seq OWNED BY r_trans_slave.id_trans_slave;


--
-- Name: r_trans_slave_id_trans_slave_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_trans_slave_id_trans_slave_seq', 1, false);


--
-- Name: r_trans_step_condition; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_trans_step_condition (
    id_transformation integer,
    id_step integer,
    id_condition integer
);


ALTER TABLE public.r_trans_step_condition OWNER TO pdi;

--
-- Name: r_transformation; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_transformation (
    id_transformation bigint NOT NULL,
    id_directory integer,
    name character varying(255),
    description character varying(2000000),
    extended_description character varying(2000000),
    trans_version character varying(255),
    trans_status integer,
    id_step_read integer,
    id_step_write integer,
    id_step_input integer,
    id_step_output integer,
    id_step_update integer,
    id_database_log integer,
    table_name_log character varying(255),
    use_batchid character(1),
    use_logfield character(1),
    id_database_maxdate integer,
    table_name_maxdate character varying(255),
    field_name_maxdate character varying(255),
    offset_maxdate numeric(12,2),
    diff_maxdate numeric(12,2),
    created_user character varying(255),
    created_date timestamp without time zone,
    modified_user character varying(255),
    modified_date timestamp without time zone,
    size_rowset integer
);


ALTER TABLE public.r_transformation OWNER TO pdi;

--
-- Name: r_transformation_id_transformation_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_transformation_id_transformation_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_transformation_id_transformation_seq OWNER TO pdi;

--
-- Name: r_transformation_id_transformation_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_transformation_id_transformation_seq OWNED BY r_transformation.id_transformation;


--
-- Name: r_transformation_id_transformation_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_transformation_id_transformation_seq', 1, false);


--
-- Name: r_user; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_user (
    id_user bigint NOT NULL,
    id_profile integer,
    login character varying(255),
    password character varying(255),
    name character varying(255),
    description character varying(255),
    enabled character(1)
);


ALTER TABLE public.r_user OWNER TO pdi;

--
-- Name: r_user_id_user_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_user_id_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_user_id_user_seq OWNER TO pdi;

--
-- Name: r_user_id_user_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_user_id_user_seq OWNED BY r_user.id_user;


--
-- Name: r_user_id_user_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_user_id_user_seq', 1, false);


--
-- Name: r_value; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_value (
    id_value bigint NOT NULL,
    name character varying(255),
    value_type character varying(255),
    value_str character varying(255),
    is_null character(1)
);


ALTER TABLE public.r_value OWNER TO pdi;

--
-- Name: r_value_id_value_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_value_id_value_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_value_id_value_seq OWNER TO pdi;

--
-- Name: r_value_id_value_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_value_id_value_seq OWNED BY r_value.id_value;


--
-- Name: r_value_id_value_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_value_id_value_seq', 1, false);


--
-- Name: r_version; Type: TABLE; Schema: public; Owner: pdi; Tablespace: 
--

CREATE TABLE r_version (
    id_version bigint NOT NULL,
    major_version smallint,
    minor_version smallint,
    upgrade_date timestamp without time zone,
    is_upgrade character(1)
);


ALTER TABLE public.r_version OWNER TO pdi;

--
-- Name: r_version_id_version_seq; Type: SEQUENCE; Schema: public; Owner: pdi
--

CREATE SEQUENCE r_version_id_version_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.r_version_id_version_seq OWNER TO pdi;

--
-- Name: r_version_id_version_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pdi
--

ALTER SEQUENCE r_version_id_version_seq OWNED BY r_version.id_version;


--
-- Name: r_version_id_version_seq; Type: SEQUENCE SET; Schema: public; Owner: pdi
--

SELECT pg_catalog.setval('r_version_id_version_seq', 1, false);


--
-- Name: id_cluster; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_cluster ALTER COLUMN id_cluster SET DEFAULT nextval('r_cluster_id_cluster_seq'::regclass);


--
-- Name: id_cluster_slave; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_cluster_slave ALTER COLUMN id_cluster_slave SET DEFAULT nextval('r_cluster_slave_id_cluster_slave_seq'::regclass);


--
-- Name: id_condition; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_condition ALTER COLUMN id_condition SET DEFAULT nextval('r_condition_id_condition_seq'::regclass);


--
-- Name: id_database; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_database ALTER COLUMN id_database SET DEFAULT nextval('r_database_id_database_seq'::regclass);


--
-- Name: id_database_attribute; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_database_attribute ALTER COLUMN id_database_attribute SET DEFAULT nextval('r_database_attribute_id_database_attribute_seq'::regclass);


--
-- Name: id_database_contype; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_database_contype ALTER COLUMN id_database_contype SET DEFAULT nextval('r_database_contype_id_database_contype_seq'::regclass);


--
-- Name: id_database_type; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_database_type ALTER COLUMN id_database_type SET DEFAULT nextval('r_database_type_id_database_type_seq'::regclass);


--
-- Name: id_dependency; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_dependency ALTER COLUMN id_dependency SET DEFAULT nextval('r_dependency_id_dependency_seq'::regclass);


--
-- Name: id_directory; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_directory ALTER COLUMN id_directory SET DEFAULT nextval('r_directory_id_directory_seq'::regclass);


--
-- Name: id_job; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_job ALTER COLUMN id_job SET DEFAULT nextval('r_job_id_job_seq'::regclass);


--
-- Name: id_job_hop; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_job_hop ALTER COLUMN id_job_hop SET DEFAULT nextval('r_job_hop_id_job_hop_seq'::regclass);


--
-- Name: id_jobentry; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_jobentry ALTER COLUMN id_jobentry SET DEFAULT nextval('r_jobentry_id_jobentry_seq'::regclass);


--
-- Name: id_jobentry_attribute; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_jobentry_attribute ALTER COLUMN id_jobentry_attribute SET DEFAULT nextval('r_jobentry_attribute_id_jobentry_attribute_seq'::regclass);


--
-- Name: id_jobentry_copy; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_jobentry_copy ALTER COLUMN id_jobentry_copy SET DEFAULT nextval('r_jobentry_copy_id_jobentry_copy_seq'::regclass);


--
-- Name: id_jobentry_type; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_jobentry_type ALTER COLUMN id_jobentry_type SET DEFAULT nextval('r_jobentry_type_id_jobentry_type_seq'::regclass);


--
-- Name: id_log; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_log ALTER COLUMN id_log SET DEFAULT nextval('r_log_id_log_seq'::regclass);


--
-- Name: id_loglevel; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_loglevel ALTER COLUMN id_loglevel SET DEFAULT nextval('r_loglevel_id_loglevel_seq'::regclass);


--
-- Name: id_note; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_note ALTER COLUMN id_note SET DEFAULT nextval('r_note_id_note_seq'::regclass);


--
-- Name: id_partition; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_partition ALTER COLUMN id_partition SET DEFAULT nextval('r_partition_id_partition_seq'::regclass);


--
-- Name: id_partition_schema; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_partition_schema ALTER COLUMN id_partition_schema SET DEFAULT nextval('r_partition_schema_id_partition_schema_seq'::regclass);


--
-- Name: id_permission; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_permission ALTER COLUMN id_permission SET DEFAULT nextval('r_permission_id_permission_seq'::regclass);


--
-- Name: id_profile; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_profile ALTER COLUMN id_profile SET DEFAULT nextval('r_profile_id_profile_seq'::regclass);


--
-- Name: id_repository_log; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_repository_log ALTER COLUMN id_repository_log SET DEFAULT nextval('r_repository_log_id_repository_log_seq'::regclass);


--
-- Name: id_slave; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_slave ALTER COLUMN id_slave SET DEFAULT nextval('r_slave_id_slave_seq'::regclass);


--
-- Name: id_step; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_step ALTER COLUMN id_step SET DEFAULT nextval('r_step_id_step_seq'::regclass);


--
-- Name: id_step_attribute; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_step_attribute ALTER COLUMN id_step_attribute SET DEFAULT nextval('r_step_attribute_id_step_attribute_seq'::regclass);


--
-- Name: id_step_type; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_step_type ALTER COLUMN id_step_type SET DEFAULT nextval('r_step_type_id_step_type_seq'::regclass);


--
-- Name: id_trans_attribute; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_trans_attribute ALTER COLUMN id_trans_attribute SET DEFAULT nextval('r_trans_attribute_id_trans_attribute_seq'::regclass);


--
-- Name: id_trans_cluster; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_trans_cluster ALTER COLUMN id_trans_cluster SET DEFAULT nextval('r_trans_cluster_id_trans_cluster_seq'::regclass);


--
-- Name: id_trans_hop; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_trans_hop ALTER COLUMN id_trans_hop SET DEFAULT nextval('r_trans_hop_id_trans_hop_seq'::regclass);


--
-- Name: id_trans_partition_schema; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_trans_partition_schema ALTER COLUMN id_trans_partition_schema SET DEFAULT nextval('r_trans_partition_schema_id_trans_partition_schema_seq'::regclass);


--
-- Name: id_trans_slave; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_trans_slave ALTER COLUMN id_trans_slave SET DEFAULT nextval('r_trans_slave_id_trans_slave_seq'::regclass);


--
-- Name: id_transformation; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_transformation ALTER COLUMN id_transformation SET DEFAULT nextval('r_transformation_id_transformation_seq'::regclass);


--
-- Name: id_user; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_user ALTER COLUMN id_user SET DEFAULT nextval('r_user_id_user_seq'::regclass);


--
-- Name: id_value; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_value ALTER COLUMN id_value SET DEFAULT nextval('r_value_id_value_seq'::regclass);


--
-- Name: id_version; Type: DEFAULT; Schema: public; Owner: pdi
--

ALTER TABLE r_version ALTER COLUMN id_version SET DEFAULT nextval('r_version_id_version_seq'::regclass);


--
-- Data for Name: r_cluster; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_cluster (id_cluster, name, base_port, sockets_buffer_size, sockets_flush_interval, sockets_compressed) FROM stdin;
\.


--
-- Data for Name: r_cluster_slave; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_cluster_slave (id_cluster_slave, id_cluster, id_slave) FROM stdin;
\.


--
-- Data for Name: r_condition; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_condition (id_condition, id_condition_parent, negated, operator, left_name, condition_function, right_name, id_value_right) FROM stdin;
1	0	N	-      	loinc_num	IS NOT NULL	\N	-1
2	0	N	-      	loinc_num	IS NOT NULL	\N	-1
\.


--
-- Data for Name: r_database; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_database (id_database, name, id_database_type, id_database_contype, host_name, database_name, port, username, password, servername, data_tbs, index_tbs) FROM stdin;
1	ESP	36	1	localhost	esp	3306	ESP	Encrypted 616568693769654d6f6f546836546f6f71756f6832617535d1e1c0a708c69ba9a21aa629df9aa4d5	\N	\N	\N
2	ESP Staging (PostgreSQL)	6	1	localhost	esp_staging	5432	esp_kettle	Encrypted 58764e513733394a387441756d304e79534e6c6736556a65c9edff8e25e1b9aea011b445c88bf68f	\N	\N	\N
3	ESP Warehouse (PostgreSQL)	6	1	localhost	esp_warehouse	5432	esp_kettle	Encrypted 58764e513733394a387441756d304e79534e6c6736556a65c9edff8e25e1b9aea011b445c88bf68f	\N	\N	\N
4	ESP (MySQL)	36	1	localhost	esp	3306	ESP	Encrypted 616568693769654d6f6f546836546f6f71756f6832617535d1e1c0a708c69ba9a21aa629df9aa4d5	\N	\N	\N
5	ESP (PostgreSQL)	6	1	localhost	esp	5432	esp	Encrypted 5236307a547a73376f336a6f776b32595053703652474a6a5478376d385858686a6eedf49ba42fc1b1bc8a40f667f0bf84e3	\N	\N	\N
6	ESP Beast (MySQL)	36	1	localhost	esp_beast	3306	rejmv	Encrypted 2be98c8a70cd2918fb216bb62cd97a3dc	\N	\N	\N
7	esp_beast@localhost (MySQL)	36	1	localhost	esp_beast	3306	rejmv	Encrypted 2be98c8a70cd2918fb216bb62cd97a3dc	\N	\N	\N
8	esp@beast (MySQL)	36	1	beast	esp	3306	espuser	Encrypted 2be98afc86a948194be0aab628cc2ff8c	\N	\N	\N
9	esp_northadams@localhost (MySQL)	36	1	localhost	esp_northadams	3306	ESP	Encrypted 616568693769654d6f6f546836546f6f71756f6832617535d1e1c0a708c69ba9a21aa629df9aa4d5	\N	\N	\N
\.


--
-- Data for Name: r_database_attribute; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_database_attribute (id_database_attribute, id_database, code, value_str) FROM stdin;
253	9	SQL_CONNECT	\N
254	9	STREAM_RESULTS	Y
255	9	USE_POOLING	N
256	9	FORCE_IDENTIFIERS_TO_LOWERCASE	N
257	9	IS_CLUSTERED	N
258	9	QUOTE_ALL_FIELDS	N
259	9	FORCE_IDENTIFIERS_TO_UPPERCASE	N
260	9	PORT_NUMBER	3306
190	1	SQL_CONNECT	\N
191	1	STREAM_RESULTS	Y
192	1	USE_POOLING	N
193	1	FORCE_IDENTIFIERS_TO_LOWERCASE	N
194	1	IS_CLUSTERED	N
195	1	QUOTE_ALL_FIELDS	N
196	1	FORCE_IDENTIFIERS_TO_UPPERCASE	N
197	1	PORT_NUMBER	3306
198	2	SQL_CONNECT	\N
199	2	USE_POOLING	N
200	2	FORCE_IDENTIFIERS_TO_LOWERCASE	N
201	2	IS_CLUSTERED	N
202	2	QUOTE_ALL_FIELDS	N
203	2	FORCE_IDENTIFIERS_TO_UPPERCASE	N
204	2	PORT_NUMBER	5432
205	3	SQL_CONNECT	\N
206	3	USE_POOLING	N
207	3	FORCE_IDENTIFIERS_TO_LOWERCASE	N
208	3	IS_CLUSTERED	N
209	3	QUOTE_ALL_FIELDS	N
210	3	FORCE_IDENTIFIERS_TO_UPPERCASE	N
211	3	PORT_NUMBER	5432
212	4	SQL_CONNECT	\N
213	4	STREAM_RESULTS	Y
214	4	USE_POOLING	N
215	4	FORCE_IDENTIFIERS_TO_LOWERCASE	N
216	4	QUOTE_ALL_FIELDS	N
217	4	IS_CLUSTERED	N
218	4	FORCE_IDENTIFIERS_TO_UPPERCASE	N
219	4	PORT_NUMBER	3306
220	5	INITIAL_POOL_SIZE	5
221	5	MAXIMUM_POOL_SIZE	20
222	5	USE_POOLING	Y
223	5	IS_CLUSTERED	N
224	5	PORT_NUMBER	5432
225	5	FORCE_IDENTIFIERS_TO_UPPERCASE	N
226	5	FORCE_IDENTIFIERS_TO_LOWERCASE	N
227	5	SQL_CONNECT	\N
228	5	QUOTE_ALL_FIELDS	N
229	6	SQL_CONNECT	\N
230	6	STREAM_RESULTS	Y
231	6	USE_POOLING	N
232	6	FORCE_IDENTIFIERS_TO_LOWERCASE	N
233	6	IS_CLUSTERED	N
234	6	QUOTE_ALL_FIELDS	N
235	6	FORCE_IDENTIFIERS_TO_UPPERCASE	N
236	6	PORT_NUMBER	3306
237	7	SQL_CONNECT	\N
238	7	STREAM_RESULTS	Y
239	7	USE_POOLING	N
240	7	FORCE_IDENTIFIERS_TO_LOWERCASE	N
241	7	QUOTE_ALL_FIELDS	N
242	7	IS_CLUSTERED	N
243	7	FORCE_IDENTIFIERS_TO_UPPERCASE	N
244	7	PORT_NUMBER	3306
245	8	SQL_CONNECT	\N
246	8	STREAM_RESULTS	Y
247	8	USE_POOLING	N
248	8	FORCE_IDENTIFIERS_TO_LOWERCASE	N
249	8	QUOTE_ALL_FIELDS	N
250	8	IS_CLUSTERED	N
251	8	FORCE_IDENTIFIERS_TO_UPPERCASE	N
252	8	PORT_NUMBER	3306
\.


--
-- Data for Name: r_database_contype; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_database_contype (id_database_contype, code, description) FROM stdin;
1	Native	Native (JDBC)
2	ODBC	ODBC
3	OCI	OCI
4	Plugin	Plugin specific access method
5	JNDI	JNDI
\.


--
-- Data for Name: r_database_type; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_database_type (id_database_type, code, description) FROM stdin;
1	ORACLE	Oracle
2	AS/400	AS/400
3	MSACCESS	MS Access
4	MSSQL	MS SQL Server
5	DB2	IBM DB2
6	POSTGRESQL	PostgreSQL
7	CACHE	Intersystems Cache
8	INFORMIX	Informix
9	SYBASE	Sybase
10	SYBASEIQ	SybaseIQ
11	SQLBASE	Gupta SQL Base
12	DBASE	dBase III, IV or 5
13	FIREBIRD	Firebird SQL
14	SAPDB	MaxDB (SAP DB)
15	HYPERSONIC	Hypersonic
16	GENERIC	Generic database
17	SAPR3	SAP R/3 System
18	INGRES	Ingres
19	INTERBASE	Borland Interbase
20	EXTENDB	ExtenDB
21	TERADATA	Teradata
22	ORACLERDB	Oracle RDB
23	H2	H2
24	NETEZZA	Netezza
25	UNIVERSE	UniVerse database
26	SQLITE	SQLite
27	DERBY	Apache Derby
28	REMEDY-AR-SYSTEM	Remedy Action Request System
29	PALO	Palo MOLAP Server
30	SYBASEIQ	SybaseIQ
31	GREENPLUM	Greenplum
32	MONETDB	MonetDB
33	KINGBASEES	KingbaseES
34	VERTICA	Vertica
35	NEOVIEW	Neoview
36	MYSQL	MYSQL
\.


--
-- Data for Name: r_dependency; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_dependency (id_dependency, id_transformation, id_database, table_name, field_name) FROM stdin;
\.


--
-- Data for Name: r_directory; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_directory (id_directory, id_directory_parent, directory_name) FROM stdin;
1	0	Misc
\.


--
-- Data for Name: r_job; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_job (id_job, id_directory, name, description, extended_description, job_version, job_status, id_database_log, table_name_log, created_user, created_date, modified_user, modified_date, use_batch_id, pass_batch_id, use_logfield, shared_file) FROM stdin;
\.


--
-- Data for Name: r_job_hop; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_job_hop (id_job_hop, id_job, id_jobentry_copy_from, id_jobentry_copy_to, enabled, evaluation, unconditional) FROM stdin;
\.


--
-- Data for Name: r_job_note; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_job_note (id_job, id_note) FROM stdin;
\.


--
-- Data for Name: r_jobentry; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_jobentry (id_jobentry, id_job, id_jobentry_type, name, description) FROM stdin;
\.


--
-- Data for Name: r_jobentry_attribute; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_jobentry_attribute (id_jobentry_attribute, id_job, id_jobentry, nr, code, value_num, value_str) FROM stdin;
\.


--
-- Data for Name: r_jobentry_copy; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_jobentry_copy (id_jobentry_copy, id_jobentry, id_job, id_jobentry_type, nr, gui_location_x, gui_location_y, gui_draw, parallel) FROM stdin;
\.


--
-- Data for Name: r_jobentry_type; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_jobentry_type (id_jobentry_type, code, description) FROM stdin;
1	TRANS	Transformation
2	JOB	Job
3	SHELL	Shell
4	MAIL	Mail
5	SQL	SQL
6	FTP	Get a file with FTP
7	TABLE_EXISTS	Table exists
8	FILE_EXISTS	File Exists
9	EVAL	JavaScript
10	SPECIAL	Special entries
11	SFTP	Get a file with SFTP
12	HTTP	HTTP
13	CREATE_FILE	Create file
14	DELETE_FILE	Delete file
15	WAIT_FOR_FILE	Wait for file
16	SFTPPUT	Put a file with SFTP
17	FILE_COMPARE	File Compare
18	MYSQL_BULK_LOAD	BulkLoad into Mysql
19	MSGBOX_INFO	Display Msgbox Info
20	DELAY	Wait for
21	ZIP_FILE	Zip file
22	XSLT	XSL Transformation
23	MYSQL_BULK_FILE	BulkLoad from Mysql into file
24	ABORT	Abort job
25	GET_POP	Get mails from POP
26	PING	Ping a host
27	DELETE_FILES	Delete files
28	SUCCESS	Success
29	XSD_VALIDATOR	XSD Validator
30	WRITE_TO_LOG	Write To Log
31	COPY_FILES	Copy Files
32	DTD_VALIDATOR	DTD Validator
33	FTP_PUT	Put a file with FTP
34	UNZIP	Unzip file
35	CREATE_FOLDER	Create a folder
36	FOLDER_IS_EMPTY	Check if a folder is empty
37	FILES_EXIST	Checks if files exist
38	FOLDERS_COMPARE	Compare folders
39	ADD_RESULT_FILENAMES	Add filenames to result
40	DELETE_RESULT_FILENAMES	Delete filenames from result
41	MSSQL_BULK_LOAD	BulkLoad into MSSQL
42	MOVE_FILES	Move Files
43	COPY_MOVE_RESULT_FILENAMES	Copy or Move result filenames
44	XML_WELL_FORMED	Check if XML file is well formed
45	SSH2_GET	SSH2 Get
46	SSH2_PUT	SSH2 Put
47	FTP_DELETE	FTP Delete
48	DELETE_FOLDERS	Delete folders
49	COLUMNS_EXIST	Columns exist in a table
50	EXPORT_REPOSITORY	Export repository to XML file
51	CONNECTED_TO_REPOSITORY	Check if connected to repository
52	TRUNCATE_TABLES	Truncate tables
53	SET_VARIABLES	Set variables
54	MS_ACCESS_BULK_LOAD	MS Access Bulk Load
55	DummyJob	Dummy plugin
\.


--
-- Data for Name: r_log; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_log (id_log, name, id_loglevel, logtype, filename, fileextention, add_date, add_time, id_database_log, table_name_log) FROM stdin;
\.


--
-- Data for Name: r_loglevel; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_loglevel (id_loglevel, code, description) FROM stdin;
1	Error	Error logging only
2	Minimal	Minimal logging
3	Basic	Basic logging
4	Detailed	Detailed logging
5	Debug	Debugging
6	Rowlevel	Rowlevel (very detailed)
\.


--
-- Data for Name: r_note; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_note (id_note, value_str, gui_location_x, gui_location_y, gui_location_width, gui_location_height) FROM stdin;
\.


--
-- Data for Name: r_partition; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_partition (id_partition, id_partition_schema, partition_id) FROM stdin;
\.


--
-- Data for Name: r_partition_schema; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_partition_schema (id_partition_schema, name, dynamic_definition, partitions_per_slave) FROM stdin;
\.


--
-- Data for Name: r_permission; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_permission (id_permission, code, description) FROM stdin;
1	READONLY	Read only access
2	ADMIN	Administrator
3	TRANS	Use transformations
4	JOB	Use jobs
5	SCHEMA	Use schemas
\.


--
-- Data for Name: r_profile; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_profile (id_profile, name, description) FROM stdin;
1	Administrator	Administrator profile, manage users
2	User	Normal user, all tools
3	Read-only	Read-only users
\.


--
-- Data for Name: r_profile_permission; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_profile_permission (id_profile, id_permission) FROM stdin;
1	2
1	3
1	4
1	5
2	3
2	4
2	5
\.


--
-- Data for Name: r_repository_log; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_repository_log (id_repository_log, rep_version, log_date, log_user, operation_desc) FROM stdin;
1	3.0	2009-04-01 13:39:57.835	admin	Creation of the Kettle repository
2	3.0	2009-04-01 13:41:40.123	esp	save transformation 'Load LOINC db'
3	3.0	2009-04-01 13:44:35.248	esp	save transformation 'Load LOINC db'
4	3.0	2009-04-01 13:46:10.774	esp	save transformation 'Load LOINC Additions'
5	3.0	2009-04-01 13:46:24.676	esp	save transformation 'Load LOINC Additions'
6	3.0	2009-04-01 13:46:38.412	esp	save transformation 'Load LOINC Additions'
7	3.0	2009-04-01 14:11:27.543	esp	save transformation 'Load External Code to LOINC Maps -- Atrius'
8	3.0	2009-04-01 14:14:10.754	esp	save transformation 'Load External Code to LOINC Maps -- Atrius'
9	3.0	2009-04-01 14:15:10.747	esp	save transformation 'Load External Code to LOINC Maps -- Atrius'
10	3.0	2009-04-01 14:15:28.133	esp	save transformation 'Load External Code to LOINC Maps -- Atrius'
11	3.0	2009-04-01 14:17:24.933	esp	save transformation 'Load External Code to LOINC Maps -- Atrius'
12	3.0	2009-04-01 14:17:41.957	esp	save transformation 'Load External Code to LOINC Maps -- Atrius'
13	3.0	2009-04-01 14:18:07.031	esp	save transformation 'Load External Code to LOINC Maps -- Atrius'
14	3.0	2009-04-02 16:14:44.177	esp	save transformation 'Load External Code to LOINC Maps -- North Adams'
15	3.0	2009-04-02 16:14:53.625	esp	save transformation 'Load External Code to LOINC Maps -- North Adams'
16	3.0	2009-04-02 16:17:19.073	esp	save transformation 'Load External Code to LOINC Maps -- North Adams'
\.


--
-- Data for Name: r_slave; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_slave (id_slave, name, host_name, port, username, password, proxy_host_name, proxy_port, non_proxy_hosts, master) FROM stdin;
\.


--
-- Data for Name: r_step; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_step (id_step, id_transformation, name, description, id_step_type, distribute, copies, gui_location_x, gui_location_y, gui_draw) FROM stdin;
1	1	Read LOINCDB.txt	\N	3	Y	1	110	52	Y
2	1	Select values	\N	15	Y	1	115	160	Y
3	1	Write conf_loinc	\N	21	Y	1	119	280	Y
4	2	Read loinc_additions.txt	\N	3	Y	1	140	40	Y
5	2	Select values	\N	15	Y	1	140	140	Y
6	2	Write core_loinc	\N	21	Y	1	140	260	Y
20	5	Abort	\N	19	Y	1	320	320	Y
21	5	Get ESP_SOURCE_SYSTEM	\N	44	Y	1	121	665	Y
22	5	LOINC number found?	\N	25	N	1	180	320	Y
23	5	Lookup  system_id	\N	30	Y	1	278	658	Y
24	5	Lookup LOINC	\N	30	N	1	180	200	Y
25	5	Read North Adams LOINC Code map	\N	3	Y	1	180	80	Y
26	5	Select values	\N	15	Y	1	540	540	Y
27	5	Wait for all LOINCs to pass	\N	49	Y	1	180	440	Y
28	5	Write to core_external_to_loinc_map	\N	21	Y	1	540	660	Y
7	3	Abort	\N	19	Y	1	700	240	Y
8	3	Add id	\N	20	Y	1	560	456	Y
9	3	Ext_code from CPT + Comp	\N	35	Y	1	560	40	Y
10	3	Get ESP_SOURCE_SYSTEM	\N	44	Y	1	260	40	Y
11	3	Get system data	\N	27	Y	1	123	171	Y
12	3	LOINC number found?	\N	25	N	1	560	240	Y
13	3	Lookup  system_id	\N	30	Y	1	133	284	Y
14	3	Lookup LOINC	\N	30	N	1	560	140	Y
15	3	Read mapping file	\N	16	Y	1	60	40	Y
16	3	Select values	\N	15	Y	1	559	546	Y
17	3	Validate system_id not null	\N	78	Y	1	173	405	Y
18	3	Wait for all LOINCs to pass	\N	49	Y	1	560	360	Y
19	3	Write to conf_ext_to_loinc	\N	21	Y	1	558	644	Y
\.


--
-- Data for Name: r_step_attribute; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_step_attribute (id_step_attribute, id_transformation, id_step, nr, code, value_num, value_str) FROM stdin;
1099	5	27	0	compress	0	Y
1100	5	27	0	cluster_schema	0	\N
1101	5	28	0	PARTITIONING_SCHEMA	0	\N
1102	5	28	0	PARTITIONING_METHOD	0	none
1103	5	28	0	id_connection	9	\N
1104	5	28	0	schema	0	\N
1105	5	28	0	table	0	conf_ext_to_loinc
1106	5	28	0	commit	1	\N
1107	5	28	0	truncate	0	Y
1108	5	28	0	ignore_errors	0	N
1109	5	28	0	use_batch	0	N
1110	5	28	0	partitioning_enabled	0	N
1111	5	28	0	partitioning_field	0	\N
1112	5	28	0	partitioning_daily	0	N
1113	5	28	0	partitioning_monthly	0	Y
1114	5	28	0	tablename_in_field	0	N
1115	5	28	0	tablename_field	0	\N
1116	5	28	0	tablename_in_table	0	Y
1117	5	28	0	return_keys	0	N
1118	5	28	0	return_field	0	\N
1119	5	28	0	cluster_schema	0	\N
637	2	4	0	PARTITIONING_SCHEMA	0	\N
638	2	4	0	PARTITIONING_METHOD	0	none
639	2	4	0	filename	0	/home/rejmv/work/git-esp/src/esp/data/loinc_additions.txt
640	2	4	0	filename_field	0	\N
641	2	4	0	rownum_field	0	\N
642	2	4	0	include_filename	0	N
643	2	4	0	separator	0	\t
644	2	4	0	enclosure	0	"
645	2	4	0	buffer_size	0	50000
646	2	4	0	header	0	Y
647	2	4	0	lazy_conversion	0	Y
648	2	4	0	add_filename_result	0	N
649	2	4	0	parallel	0	N
650	2	4	0	encoding	0	\N
651	2	4	0	field_name	0	loinc_num
652	2	4	0	field_type	0	String
653	2	4	0	field_format	0	\N
654	2	4	0	field_currency	0	\N
655	2	4	0	field_decimal	0	\N
656	2	4	0	field_group	0	\N
657	2	4	0	field_length	-1	\N
658	2	4	0	field_precision	-1	\N
659	2	4	0	field_trim_type	0	none
660	2	4	1	field_name	0	long_name
661	2	4	1	field_type	0	String
662	2	4	1	field_format	0	\N
663	2	4	1	field_currency	0	\N
664	2	4	1	field_decimal	0	\N
665	2	4	1	field_group	0	\N
666	2	4	1	field_length	-1	\N
667	2	4	1	field_precision	-1	\N
668	2	4	1	field_trim_type	0	none
669	2	4	0	cluster_schema	0	\N
670	2	5	0	PARTITIONING_SCHEMA	0	\N
671	2	5	0	PARTITIONING_METHOD	0	none
672	2	5	0	field_name	0	loinc_num
673	2	5	0	field_rename	0	loinc_num
674	2	5	0	field_length	-1	\N
675	2	5	0	field_precision	-1	\N
676	2	5	1	field_name	0	long_name
677	2	5	1	field_rename	0	long_common_name
678	2	5	1	field_length	-1	\N
679	2	5	1	field_precision	-1	\N
680	2	5	0	select_unspecified	0	N
681	2	5	0	cluster_schema	0	\N
682	2	6	0	PARTITIONING_SCHEMA	0	\N
683	2	6	0	PARTITIONING_METHOD	0	none
684	2	6	0	id_connection	8	\N
685	2	6	0	schema	0	\N
686	2	6	0	table	0	conf_loinc
687	2	6	0	commit	100	\N
688	2	6	0	truncate	0	N
689	2	6	0	ignore_errors	0	N
690	2	6	0	use_batch	0	N
691	2	6	0	partitioning_enabled	0	N
692	2	6	0	partitioning_field	0	\N
693	2	6	0	partitioning_daily	0	N
694	2	6	0	partitioning_monthly	0	Y
695	2	6	0	tablename_in_field	0	N
696	2	6	0	tablename_field	0	\N
697	2	6	0	tablename_in_table	0	Y
698	2	6	0	return_keys	0	N
699	2	6	0	return_field	0	\N
700	2	6	0	cluster_schema	0	\N
1	1	1	0	PARTITIONING_SCHEMA	0	\N
2	1	1	0	PARTITIONING_METHOD	0	none
3	1	1	0	filename	0	/home/rejmv/work/git-esp/src/esp/data/LOINCDB.TXT
4	1	1	0	filename_field	0	\N
5	1	1	0	rownum_field	0	\N
6	1	1	0	include_filename	0	N
7	1	1	0	separator	0	\t
8	1	1	0	enclosure	0	"
9	1	1	0	buffer_size	0	50000
10	1	1	0	header	0	Y
11	1	1	0	lazy_conversion	0	Y
12	1	1	0	add_filename_result	0	N
13	1	1	0	parallel	0	N
14	1	1	0	encoding	0	\N
15	1	1	0	field_name	0	LOINC_NUM
16	1	1	0	field_type	0	String
17	1	1	0	field_format	0	\N
18	1	1	0	field_currency	0	\N
19	1	1	0	field_decimal	0	\N
20	1	1	0	field_group	0	\N
21	1	1	0	field_length	0	\N
22	1	1	0	field_precision	0	\N
23	1	1	0	field_trim_type	0	none
24	1	1	1	field_name	0	COMPONENT
25	1	1	1	field_type	0	String
26	1	1	1	field_format	0	\N
27	1	1	1	field_currency	0	\N
28	1	1	1	field_decimal	0	\N
29	1	1	1	field_group	0	\N
30	1	1	1	field_length	0	\N
31	1	1	1	field_precision	0	\N
32	1	1	1	field_trim_type	0	none
33	1	1	2	field_name	0	PROPERTY
34	1	1	2	field_type	0	String
35	1	1	2	field_format	0	\N
36	1	1	2	field_currency	0	\N
37	1	1	2	field_decimal	0	\N
38	1	1	2	field_group	0	\N
39	1	1	2	field_length	0	\N
40	1	1	2	field_precision	0	\N
41	1	1	2	field_trim_type	0	none
42	1	1	3	field_name	0	TIME_ASPCT
43	1	1	3	field_type	0	String
44	1	1	3	field_format	0	\N
45	1	1	3	field_currency	0	\N
46	1	1	3	field_decimal	0	\N
47	1	1	3	field_group	0	\N
48	1	1	3	field_length	0	\N
49	1	1	3	field_precision	0	\N
50	1	1	3	field_trim_type	0	none
51	1	1	4	field_name	0	SYSTEM
52	1	1	4	field_type	0	String
53	1	1	4	field_format	0	\N
54	1	1	4	field_currency	0	\N
55	1	1	4	field_decimal	0	\N
56	1	1	4	field_group	0	\N
57	1	1	4	field_length	0	\N
58	1	1	4	field_precision	0	\N
59	1	1	4	field_trim_type	0	none
60	1	1	5	field_name	0	SCALE_TYP
61	1	1	5	field_type	0	String
62	1	1	5	field_format	0	\N
63	1	1	5	field_currency	0	\N
64	1	1	5	field_decimal	0	\N
65	1	1	5	field_group	0	\N
66	1	1	5	field_length	0	\N
67	1	1	5	field_precision	0	\N
68	1	1	5	field_trim_type	0	none
69	1	1	6	field_name	0	METHOD_TYP
70	1	1	6	field_type	0	String
71	1	1	6	field_format	0	\N
72	1	1	6	field_currency	0	\N
73	1	1	6	field_decimal	0	\N
74	1	1	6	field_group	0	\N
75	1	1	6	field_length	0	\N
76	1	1	6	field_precision	0	\N
77	1	1	6	field_trim_type	0	none
78	1	1	7	field_name	0	RELAT_NMS
79	1	1	7	field_type	0	String
80	1	1	7	field_format	0	\N
81	1	1	7	field_currency	0	\N
82	1	1	7	field_decimal	0	\N
83	1	1	7	field_group	0	\N
84	1	1	7	field_length	0	\N
85	1	1	7	field_precision	0	\N
86	1	1	7	field_trim_type	0	none
87	1	1	8	field_name	0	CLASS
88	1	1	8	field_type	0	String
89	1	1	8	field_format	0	\N
90	1	1	8	field_currency	0	\N
91	1	1	8	field_decimal	0	\N
92	1	1	8	field_group	0	\N
93	1	1	8	field_length	0	\N
94	1	1	8	field_precision	0	\N
95	1	1	8	field_trim_type	0	none
96	1	1	9	field_name	0	SOURCE
97	1	1	9	field_type	0	String
98	1	1	9	field_format	0	\N
99	1	1	9	field_currency	0	\N
100	1	1	9	field_decimal	0	\N
101	1	1	9	field_group	0	\N
102	1	1	9	field_length	0	\N
103	1	1	9	field_precision	0	\N
104	1	1	9	field_trim_type	0	none
105	1	1	10	field_name	0	DT_LAST_CH
106	1	1	10	field_type	0	String
107	1	1	10	field_format	0	\N
108	1	1	10	field_currency	0	\N
109	1	1	10	field_decimal	0	\N
110	1	1	10	field_group	0	\N
111	1	1	10	field_length	0	\N
112	1	1	10	field_precision	0	\N
113	1	1	10	field_trim_type	0	none
114	1	1	11	field_name	0	CHNG_TYPE
115	1	1	11	field_type	0	String
116	1	1	11	field_format	0	\N
117	1	1	11	field_currency	0	\N
118	1	1	11	field_decimal	0	\N
119	1	1	11	field_group	0	\N
120	1	1	11	field_length	0	\N
121	1	1	11	field_precision	0	\N
122	1	1	11	field_trim_type	0	none
123	1	1	12	field_name	0	COMMENTS
124	1	1	12	field_type	0	String
125	1	1	12	field_format	0	\N
126	1	1	12	field_currency	0	\N
127	1	1	12	field_decimal	0	\N
128	1	1	12	field_group	0	\N
129	1	1	12	field_length	0	\N
130	1	1	12	field_precision	0	\N
131	1	1	12	field_trim_type	0	none
132	1	1	13	field_name	0	ANSWERLIST
133	1	1	13	field_type	0	String
134	1	1	13	field_format	0	\N
135	1	1	13	field_currency	0	\N
136	1	1	13	field_decimal	0	\N
137	1	1	13	field_group	0	\N
138	1	1	13	field_length	0	\N
139	1	1	13	field_precision	0	\N
140	1	1	13	field_trim_type	0	none
141	1	1	14	field_name	0	STATUS
142	1	1	14	field_type	0	String
143	1	1	14	field_format	0	\N
144	1	1	14	field_currency	0	\N
145	1	1	14	field_decimal	0	\N
146	1	1	14	field_group	0	\N
147	1	1	14	field_length	0	\N
148	1	1	14	field_precision	0	\N
149	1	1	14	field_trim_type	0	none
150	1	1	15	field_name	0	MAP_TO
151	1	1	15	field_type	0	String
152	1	1	15	field_format	0	\N
153	1	1	15	field_currency	0	\N
154	1	1	15	field_decimal	0	\N
155	1	1	15	field_group	0	\N
156	1	1	15	field_length	0	\N
157	1	1	15	field_precision	0	\N
158	1	1	15	field_trim_type	0	none
159	1	1	16	field_name	0	SCOPE
160	1	1	16	field_type	0	String
161	1	1	16	field_format	0	\N
162	1	1	16	field_currency	0	\N
163	1	1	16	field_decimal	0	\N
164	1	1	16	field_group	0	\N
165	1	1	16	field_length	0	\N
166	1	1	16	field_precision	0	\N
167	1	1	16	field_trim_type	0	none
168	1	1	17	field_name	0	NORM_RANGE
169	1	1	17	field_type	0	String
170	1	1	17	field_format	0	\N
171	1	1	17	field_currency	0	\N
172	1	1	17	field_decimal	0	\N
173	1	1	17	field_group	0	\N
174	1	1	17	field_length	0	\N
175	1	1	17	field_precision	0	\N
176	1	1	17	field_trim_type	0	none
177	1	1	18	field_name	0	IPCC_UNITS
178	1	1	18	field_type	0	String
179	1	1	18	field_format	0	\N
180	1	1	18	field_currency	0	\N
181	1	1	18	field_decimal	0	\N
182	1	1	18	field_group	0	\N
183	1	1	18	field_length	0	\N
184	1	1	18	field_precision	0	\N
185	1	1	18	field_trim_type	0	none
186	1	1	19	field_name	0	REFERENCE
187	1	1	19	field_type	0	String
188	1	1	19	field_format	0	\N
189	1	1	19	field_currency	0	\N
190	1	1	19	field_decimal	0	\N
191	1	1	19	field_group	0	\N
192	1	1	19	field_length	0	\N
193	1	1	19	field_precision	0	\N
194	1	1	19	field_trim_type	0	none
195	1	1	20	field_name	0	EXACT_CMP_SY
196	1	1	20	field_type	0	String
197	1	1	20	field_format	0	\N
198	1	1	20	field_currency	0	\N
199	1	1	20	field_decimal	0	\N
200	1	1	20	field_group	0	\N
201	1	1	20	field_length	0	\N
202	1	1	20	field_precision	0	\N
203	1	1	20	field_trim_type	0	none
204	1	1	21	field_name	0	MOLAR_MASS
205	1	1	21	field_type	0	String
206	1	1	21	field_format	0	\N
207	1	1	21	field_currency	0	\N
208	1	1	21	field_decimal	0	\N
209	1	1	21	field_group	0	\N
210	1	1	21	field_length	0	\N
211	1	1	21	field_precision	0	\N
212	1	1	21	field_trim_type	0	none
213	1	1	22	field_name	0	CLASSTYPE
214	1	1	22	field_type	0	String
215	1	1	22	field_format	0	\N
216	1	1	22	field_currency	0	\N
217	1	1	22	field_decimal	0	\N
218	1	1	22	field_group	0	\N
219	1	1	22	field_length	0	\N
220	1	1	22	field_precision	0	\N
221	1	1	22	field_trim_type	0	none
222	1	1	23	field_name	0	FORMULA
223	1	1	23	field_type	0	String
224	1	1	23	field_format	0	\N
225	1	1	23	field_currency	0	\N
226	1	1	23	field_decimal	0	\N
227	1	1	23	field_group	0	\N
228	1	1	23	field_length	0	\N
229	1	1	23	field_precision	0	\N
230	1	1	23	field_trim_type	0	none
231	1	1	24	field_name	0	SPECIES
232	1	1	24	field_type	0	String
233	1	1	24	field_format	0	\N
234	1	1	24	field_currency	0	\N
235	1	1	24	field_decimal	0	\N
236	1	1	24	field_group	0	\N
237	1	1	24	field_length	0	\N
238	1	1	24	field_precision	0	\N
239	1	1	24	field_trim_type	0	none
240	1	1	25	field_name	0	EXMPL_ANSWERS
241	1	1	25	field_type	0	String
242	1	1	25	field_format	0	\N
243	1	1	25	field_currency	0	\N
244	1	1	25	field_decimal	0	\N
245	1	1	25	field_group	0	\N
246	1	1	25	field_length	0	\N
247	1	1	25	field_precision	0	\N
248	1	1	25	field_trim_type	0	none
249	1	1	26	field_name	0	ACSSYM
250	1	1	26	field_type	0	String
251	1	1	26	field_format	0	\N
252	1	1	26	field_currency	0	\N
253	1	1	26	field_decimal	0	\N
254	1	1	26	field_group	0	\N
255	1	1	26	field_length	0	\N
256	1	1	26	field_precision	0	\N
257	1	1	26	field_trim_type	0	none
258	1	1	27	field_name	0	BASE_NAME
259	1	1	27	field_type	0	String
260	1	1	27	field_format	0	\N
261	1	1	27	field_currency	0	\N
262	1	1	27	field_decimal	0	\N
263	1	1	27	field_group	0	\N
264	1	1	27	field_length	0	\N
265	1	1	27	field_precision	0	\N
266	1	1	27	field_trim_type	0	none
267	1	1	28	field_name	0	FINAL
268	1	1	28	field_type	0	String
269	1	1	28	field_format	0	\N
270	1	1	28	field_currency	0	\N
271	1	1	28	field_decimal	0	\N
272	1	1	28	field_group	0	\N
273	1	1	28	field_length	0	\N
274	1	1	28	field_precision	0	\N
275	1	1	28	field_trim_type	0	none
276	1	1	29	field_name	0	NAACCR_ID
277	1	1	29	field_type	0	String
278	1	1	29	field_format	0	\N
279	1	1	29	field_currency	0	\N
280	1	1	29	field_decimal	0	\N
281	1	1	29	field_group	0	\N
282	1	1	29	field_length	0	\N
283	1	1	29	field_precision	0	\N
284	1	1	29	field_trim_type	0	none
285	1	1	30	field_name	0	CODE_TABLE
286	1	1	30	field_type	0	String
287	1	1	30	field_format	0	\N
288	1	1	30	field_currency	0	\N
289	1	1	30	field_decimal	0	\N
290	1	1	30	field_group	0	\N
291	1	1	30	field_length	0	\N
292	1	1	30	field_precision	0	\N
293	1	1	30	field_trim_type	0	none
294	1	1	31	field_name	0	SETROOT
295	1	1	31	field_type	0	String
296	1	1	31	field_format	0	\N
297	1	1	31	field_currency	0	\N
298	1	1	31	field_decimal	0	\N
299	1	1	31	field_group	0	\N
300	1	1	31	field_length	0	\N
301	1	1	31	field_precision	0	\N
302	1	1	31	field_trim_type	0	none
303	1	1	32	field_name	0	PANELELEMENTS
304	1	1	32	field_type	0	String
305	1	1	32	field_format	0	\N
306	1	1	32	field_currency	0	\N
307	1	1	32	field_decimal	0	\N
308	1	1	32	field_group	0	\N
309	1	1	32	field_length	0	\N
310	1	1	32	field_precision	0	\N
311	1	1	32	field_trim_type	0	none
312	1	1	33	field_name	0	SURVEY_QUEST_TEXT
313	1	1	33	field_type	0	String
314	1	1	33	field_format	0	\N
315	1	1	33	field_currency	0	\N
316	1	1	33	field_decimal	0	\N
317	1	1	33	field_group	0	\N
318	1	1	33	field_length	0	\N
319	1	1	33	field_precision	0	\N
320	1	1	33	field_trim_type	0	none
321	1	1	34	field_name	0	SURVEY_QUEST_SRC
322	1	1	34	field_type	0	String
323	1	1	34	field_format	0	\N
324	1	1	34	field_currency	0	\N
325	1	1	34	field_decimal	0	\N
326	1	1	34	field_group	0	\N
327	1	1	34	field_length	0	\N
328	1	1	34	field_precision	0	\N
329	1	1	34	field_trim_type	0	none
330	1	1	35	field_name	0	UNITSREQUIRED
331	1	1	35	field_type	0	String
332	1	1	35	field_format	0	\N
333	1	1	35	field_currency	0	\N
334	1	1	35	field_decimal	0	\N
335	1	1	35	field_group	0	\N
336	1	1	35	field_length	0	\N
337	1	1	35	field_precision	0	\N
338	1	1	35	field_trim_type	0	none
339	1	1	36	field_name	0	SUBMITTED_UNITS
340	1	1	36	field_type	0	String
341	1	1	36	field_format	0	\N
342	1	1	36	field_currency	0	\N
343	1	1	36	field_decimal	0	\N
344	1	1	36	field_group	0	\N
345	1	1	36	field_length	0	\N
346	1	1	36	field_precision	0	\N
347	1	1	36	field_trim_type	0	none
348	1	1	37	field_name	0	RELATEDNAMES2
349	1	1	37	field_type	0	String
350	1	1	37	field_format	0	\N
351	1	1	37	field_currency	0	\N
352	1	1	37	field_decimal	0	\N
353	1	1	37	field_group	0	\N
354	1	1	37	field_length	0	\N
355	1	1	37	field_precision	0	\N
356	1	1	37	field_trim_type	0	none
357	1	1	38	field_name	0	SHORTNAME
358	1	1	38	field_type	0	String
359	1	1	38	field_format	0	\N
360	1	1	38	field_currency	0	\N
361	1	1	38	field_decimal	0	\N
362	1	1	38	field_group	0	\N
363	1	1	38	field_length	0	\N
364	1	1	38	field_precision	0	\N
365	1	1	38	field_trim_type	0	none
366	1	1	39	field_name	0	ORDER_OBS
367	1	1	39	field_type	0	String
368	1	1	39	field_format	0	\N
369	1	1	39	field_currency	0	\N
370	1	1	39	field_decimal	0	\N
371	1	1	39	field_group	0	\N
372	1	1	39	field_length	0	\N
373	1	1	39	field_precision	0	\N
374	1	1	39	field_trim_type	0	none
375	1	1	40	field_name	0	CDISC_COMMON_TESTS
376	1	1	40	field_type	0	String
377	1	1	40	field_format	0	\N
378	1	1	40	field_currency	0	\N
379	1	1	40	field_decimal	0	\N
380	1	1	40	field_group	0	\N
381	1	1	40	field_length	0	\N
382	1	1	40	field_precision	0	\N
383	1	1	40	field_trim_type	0	none
384	1	1	41	field_name	0	HL7_FIELD_SUBFIELD_ID
385	1	1	41	field_type	0	String
386	1	1	41	field_format	0	\N
387	1	1	41	field_currency	0	\N
388	1	1	41	field_decimal	0	\N
389	1	1	41	field_group	0	\N
390	1	1	41	field_length	0	\N
391	1	1	41	field_precision	0	\N
392	1	1	41	field_trim_type	0	none
393	1	1	42	field_name	0	EXTERNAL_COPYRIGHT_NOTICE
394	1	1	42	field_type	0	String
395	1	1	42	field_format	0	\N
396	1	1	42	field_currency	0	\N
397	1	1	42	field_decimal	0	\N
398	1	1	42	field_group	0	\N
399	1	1	42	field_length	0	\N
400	1	1	42	field_precision	0	\N
401	1	1	42	field_trim_type	0	none
402	1	1	43	field_name	0	EXAMPLE_UNITS
403	1	1	43	field_type	0	String
404	1	1	43	field_format	0	\N
405	1	1	43	field_currency	0	\N
406	1	1	43	field_decimal	0	\N
407	1	1	43	field_group	0	\N
408	1	1	43	field_length	0	\N
409	1	1	43	field_precision	0	\N
410	1	1	43	field_trim_type	0	none
411	1	1	44	field_name	0	INPC_PERCENTAGE
412	1	1	44	field_type	0	String
413	1	1	44	field_format	0	\N
414	1	1	44	field_currency	0	\N
415	1	1	44	field_decimal	0	\N
416	1	1	44	field_group	0	\N
417	1	1	44	field_length	0	\N
418	1	1	44	field_precision	0	\N
419	1	1	44	field_trim_type	0	none
420	1	1	45	field_name	0	LONG_COMMON_NAME
421	1	1	45	field_type	0	String
422	1	1	45	field_format	0	\N
423	1	1	45	field_currency	0	\N
424	1	1	45	field_decimal	0	\N
425	1	1	45	field_group	0	\N
426	1	1	45	field_length	0	\N
427	1	1	45	field_precision	0	\N
428	1	1	45	field_trim_type	0	none
429	1	1	0	cluster_schema	0	\N
430	1	2	0	PARTITIONING_SCHEMA	0	\N
431	1	2	0	PARTITIONING_METHOD	0	none
432	1	2	0	field_name	0	LOINC_NUM
433	1	2	0	field_rename	0	loinc_num
434	1	2	0	field_length	-1	\N
435	1	2	0	field_precision	-1	\N
436	1	2	1	field_name	0	COMPONENT
437	1	2	1	field_rename	0	component
438	1	2	1	field_length	-1	\N
439	1	2	1	field_precision	-1	\N
440	1	2	2	field_name	0	PROPERTY
441	1	2	2	field_rename	0	property
442	1	2	2	field_length	-1	\N
443	1	2	2	field_precision	-1	\N
444	1	2	3	field_name	0	TIME_ASPCT
445	1	2	3	field_rename	0	time_aspct
446	1	2	3	field_length	-1	\N
447	1	2	3	field_precision	-1	\N
448	1	2	4	field_name	0	SYSTEM
449	1	2	4	field_rename	0	system
450	1	2	4	field_length	-1	\N
451	1	2	4	field_precision	-1	\N
452	1	2	5	field_name	0	SCALE_TYP
453	1	2	5	field_rename	0	scale_typ
454	1	2	5	field_length	-1	\N
455	1	2	5	field_precision	-1	\N
456	1	2	6	field_name	0	METHOD_TYP
457	1	2	6	field_rename	0	method_typ
458	1	2	6	field_length	-1	\N
459	1	2	6	field_precision	-1	\N
460	1	2	7	field_name	0	RELAT_NMS
461	1	2	7	field_rename	0	relat_nms
462	1	2	7	field_length	-1	\N
463	1	2	7	field_precision	-1	\N
464	1	2	8	field_name	0	CLASS
465	1	2	8	field_rename	0	loinc_class_field
466	1	2	8	field_length	-1	\N
467	1	2	8	field_precision	-1	\N
468	1	2	9	field_name	0	SOURCE
469	1	2	9	field_rename	0	source
470	1	2	9	field_length	-1	\N
471	1	2	9	field_precision	-1	\N
472	1	2	10	field_name	0	DT_LAST_CH
473	1	2	10	field_rename	0	dt_last_ch
474	1	2	10	field_length	-1	\N
475	1	2	10	field_precision	-1	\N
476	1	2	11	field_name	0	CHNG_TYPE
477	1	2	11	field_rename	0	chng_type
478	1	2	11	field_length	-1	\N
479	1	2	11	field_precision	-1	\N
480	1	2	12	field_name	0	COMMENTS
481	1	2	12	field_rename	0	comments
482	1	2	12	field_length	-1	\N
483	1	2	12	field_precision	-1	\N
484	1	2	13	field_name	0	ANSWERLIST
485	1	2	13	field_rename	0	answerlist
486	1	2	13	field_length	-1	\N
487	1	2	13	field_precision	-1	\N
488	1	2	14	field_name	0	STATUS
489	1	2	14	field_rename	0	status
490	1	2	14	field_length	-1	\N
491	1	2	14	field_precision	-1	\N
492	1	2	15	field_name	0	MAP_TO
493	1	2	15	field_rename	0	map_to
494	1	2	15	field_length	-1	\N
495	1	2	15	field_precision	-1	\N
496	1	2	16	field_name	0	SCOPE
497	1	2	16	field_rename	0	scope
498	1	2	16	field_length	-1	\N
499	1	2	16	field_precision	-1	\N
500	1	2	17	field_name	0	NORM_RANGE
501	1	2	17	field_rename	0	norm_range
502	1	2	17	field_length	-1	\N
503	1	2	17	field_precision	-1	\N
504	1	2	18	field_name	0	IPCC_UNITS
505	1	2	18	field_rename	0	ipcc_units
506	1	2	18	field_length	-1	\N
507	1	2	18	field_precision	-1	\N
508	1	2	19	field_name	0	REFERENCE
509	1	2	19	field_rename	0	reference
510	1	2	19	field_length	-1	\N
511	1	2	19	field_precision	-1	\N
512	1	2	20	field_name	0	EXACT_CMP_SY
513	1	2	20	field_rename	0	exact_cmp_sy
514	1	2	20	field_length	-1	\N
515	1	2	20	field_precision	-1	\N
516	1	2	21	field_name	0	MOLAR_MASS
517	1	2	21	field_rename	0	molar_mass
518	1	2	21	field_length	-1	\N
519	1	2	21	field_precision	-1	\N
520	1	2	22	field_name	0	CLASSTYPE
521	1	2	22	field_rename	0	classtype
522	1	2	22	field_length	-1	\N
523	1	2	22	field_precision	-1	\N
524	1	2	23	field_name	0	FORMULA
525	1	2	23	field_rename	0	formula
526	1	2	23	field_length	-1	\N
527	1	2	23	field_precision	-1	\N
528	1	2	24	field_name	0	SPECIES
529	1	2	24	field_rename	0	species
530	1	2	24	field_length	-1	\N
531	1	2	24	field_precision	-1	\N
532	1	2	25	field_name	0	EXMPL_ANSWERS
533	1	2	25	field_rename	0	exmpl_answers
534	1	2	25	field_length	-1	\N
535	1	2	25	field_precision	-1	\N
536	1	2	26	field_name	0	ACSSYM
537	1	2	26	field_rename	0	acssym
538	1	2	26	field_length	-1	\N
539	1	2	26	field_precision	-1	\N
540	1	2	27	field_name	0	BASE_NAME
541	1	2	27	field_rename	0	base_name
542	1	2	27	field_length	-1	\N
543	1	2	27	field_precision	-1	\N
544	1	2	28	field_name	0	FINAL
545	1	2	28	field_rename	0	final
546	1	2	28	field_length	-1	\N
547	1	2	28	field_precision	-1	\N
548	1	2	29	field_name	0	NAACCR_ID
549	1	2	29	field_rename	0	naaccr_id
550	1	2	29	field_length	-1	\N
551	1	2	29	field_precision	-1	\N
552	1	2	30	field_name	0	CODE_TABLE
553	1	2	30	field_rename	0	code_table
554	1	2	30	field_length	-1	\N
555	1	2	30	field_precision	-1	\N
556	1	2	31	field_name	0	SETROOT
557	1	2	31	field_rename	0	setroot
558	1	2	31	field_length	-1	\N
559	1	2	31	field_precision	-1	\N
560	1	2	32	field_name	0	PANELELEMENTS
561	1	2	32	field_rename	0	panelelements
562	1	2	32	field_length	-1	\N
563	1	2	32	field_precision	-1	\N
564	1	2	33	field_name	0	SURVEY_QUEST_TEXT
565	1	2	33	field_rename	0	survey_quest_text
566	1	2	33	field_length	-1	\N
567	1	2	33	field_precision	-1	\N
568	1	2	34	field_name	0	SURVEY_QUEST_SRC
569	1	2	34	field_rename	0	survey_quest_src
570	1	2	34	field_length	-1	\N
571	1	2	34	field_precision	-1	\N
572	1	2	35	field_name	0	UNITSREQUIRED
573	1	2	35	field_rename	0	unitsrequired
574	1	2	35	field_length	-1	\N
575	1	2	35	field_precision	-1	\N
576	1	2	36	field_name	0	SUBMITTED_UNITS
577	1	2	36	field_rename	0	submitted_units
578	1	2	36	field_length	-1	\N
579	1	2	36	field_precision	-1	\N
580	1	2	37	field_name	0	RELATEDNAMES2
581	1	2	37	field_rename	0	relatednames2
582	1	2	37	field_length	-1	\N
583	1	2	37	field_precision	-1	\N
584	1	2	38	field_name	0	SHORTNAME
585	1	2	38	field_rename	0	shortname
586	1	2	38	field_length	-1	\N
587	1	2	38	field_precision	-1	\N
588	1	2	39	field_name	0	ORDER_OBS
589	1	2	39	field_rename	0	order_obs
590	1	2	39	field_length	-1	\N
591	1	2	39	field_precision	-1	\N
592	1	2	40	field_name	0	CDISC_COMMON_TESTS
593	1	2	40	field_rename	0	cdisc_common_tests
594	1	2	40	field_length	-1	\N
595	1	2	40	field_precision	-1	\N
596	1	2	41	field_name	0	HL7_FIELD_SUBFIELD_ID
597	1	2	41	field_rename	0	hl7_field_subfield_id
598	1	2	41	field_length	-1	\N
599	1	2	41	field_precision	-1	\N
600	1	2	42	field_name	0	EXTERNAL_COPYRIGHT_NOTICE
601	1	2	42	field_rename	0	external_copyright_notice
602	1	2	42	field_length	-1	\N
603	1	2	42	field_precision	-1	\N
604	1	2	43	field_name	0	EXAMPLE_UNITS
605	1	2	43	field_rename	0	example_units
606	1	2	43	field_length	-1	\N
607	1	2	43	field_precision	-1	\N
608	1	2	44	field_name	0	INPC_PERCENTAGE
609	1	2	44	field_rename	0	inpc_percentage
610	1	2	44	field_length	-1	\N
611	1	2	44	field_precision	-1	\N
612	1	2	45	field_name	0	LONG_COMMON_NAME
613	1	2	45	field_rename	0	long_common_name
614	1	2	45	field_length	-1	\N
615	1	2	45	field_precision	-1	\N
616	1	2	0	select_unspecified	0	N
617	1	2	0	cluster_schema	0	\N
618	1	3	0	PARTITIONING_SCHEMA	0	\N
619	1	3	0	PARTITIONING_METHOD	0	none
620	1	3	0	id_connection	8	\N
621	1	3	0	schema	0	\N
622	1	3	0	table	0	conf_loinc
623	1	3	0	commit	1000	\N
624	1	3	0	truncate	0	N
625	1	3	0	ignore_errors	0	N
626	1	3	0	use_batch	0	N
627	1	3	0	partitioning_enabled	0	N
628	1	3	0	partitioning_field	0	\N
629	1	3	0	partitioning_daily	0	N
630	1	3	0	partitioning_monthly	0	Y
631	1	3	0	tablename_in_field	0	N
632	1	3	0	tablename_field	0	\N
633	1	3	0	tablename_in_table	0	Y
634	1	3	0	return_keys	0	N
635	1	3	0	return_field	0	\N
636	1	3	0	cluster_schema	0	\N
951	5	20	0	PARTITIONING_SCHEMA	0	\N
952	5	20	0	PARTITIONING_METHOD	0	none
953	5	20	0	row_threshold	0	0
954	5	20	0	message	0	LOINC Number not found!
955	5	20	0	always_log_rows	0	Y
956	5	20	0	cluster_schema	0	\N
957	5	21	0	PARTITIONING_SCHEMA	0	\N
958	5	21	0	PARTITIONING_METHOD	0	none
959	5	21	0	field_name	0	source_system
960	5	21	0	field_variable	0	${ESP_SOURCE_SYSTEM}
961	5	21	0	cluster_schema	0	\N
962	5	22	0	PARTITIONING_SCHEMA	0	\N
963	5	22	0	PARTITIONING_METHOD	0	none
964	5	22	0	id_condition	2	\N
965	5	22	0	send_true_to	0	Wait for all LOINCs to pass
966	5	22	0	send_false_to	0	Abort
967	5	22	0	cluster_schema	0	\N
968	5	23	0	PARTITIONING_SCHEMA	0	\N
969	5	23	0	PARTITIONING_METHOD	0	none
970	5	23	0	id_connection	5	\N
971	5	23	0	cache	0	Y
972	5	23	0	cache_load_all	0	N
973	5	23	0	cache_size	0	\N
974	5	23	0	lookup_schema	0	\N
975	5	23	0	lookup_table	0	core_source_system
976	5	23	0	lookup_orderby	0	\N
977	5	23	0	fail_on_multiple	0	N
978	5	23	0	eat_row_on_failure	0	Y
979	5	23	0	lookup_key_name	0	source_system
980	5	23	0	lookup_key_field	0	name
981	5	23	0	lookup_key_condition	0	LIKE
982	5	23	0	lookup_key_name2	0	\N
983	5	23	0	return_value_name	0	id
984	5	23	0	return_value_rename	0	system_id
985	5	23	0	return_value_default	0	\N
986	5	23	0	return_value_type	0	Integer
987	5	23	0	cluster_schema	0	\N
988	5	24	0	PARTITIONING_SCHEMA	0	\N
989	5	24	0	PARTITIONING_METHOD	0	none
990	5	24	0	id_connection	5	\N
991	5	24	0	cache	0	N
992	5	24	0	cache_load_all	0	N
993	5	24	0	cache_size	0	\N
994	5	24	0	lookup_schema	0	\N
995	5	24	0	lookup_table	0	core_loinc
996	5	24	0	lookup_orderby	0	\N
997	5	24	0	fail_on_multiple	0	N
998	5	24	0	eat_row_on_failure	0	N
999	5	24	0	lookup_key_name	0	LOINC
1000	5	24	0	lookup_key_field	0	loinc_num
1001	5	24	0	lookup_key_condition	0	LIKE
1002	5	24	0	lookup_key_name2	0	\N
1003	5	24	0	return_value_name	0	loinc_num
1004	5	24	0	return_value_rename	0	loinc_num
1005	5	24	0	return_value_default	0	\N
1006	5	24	0	return_value_type	0	String
1007	5	24	0	cluster_schema	0	\N
1008	5	25	0	PARTITIONING_SCHEMA	0	\N
1009	5	25	0	PARTITIONING_METHOD	0	none
1010	5	25	0	filename	0	/home/rejmv/work/dev-esp/NORTH_ADAMS/NorthAdamsLocal-LOINCmapMay2008.redacted.xls
1011	5	25	0	filename_field	0	\N
1012	5	25	0	rownum_field	0	\N
1013	5	25	0	include_filename	0	N
1014	5	25	0	separator	0	\t
1015	5	25	0	enclosure	0	"
1016	5	25	0	buffer_size	0	50000
1017	5	25	0	header	0	Y
1018	5	25	0	lazy_conversion	0	Y
1019	5	25	0	add_filename_result	0	N
1020	5	25	0	parallel	0	N
1021	5	25	0	encoding	0	\N
1022	5	25	0	field_name	0	Dept
1023	5	25	0	field_type	0	String
1024	5	25	0	field_format	0	\N
1025	5	25	0	field_currency	0	\N
1026	5	25	0	field_decimal	0	\N
1027	5	25	0	field_group	0	\N
701	3	7	0	PARTITIONING_SCHEMA	0	\N
702	3	7	0	PARTITIONING_METHOD	0	none
703	3	7	0	row_threshold	0	0
704	3	7	0	message	0	LOINC Number not found!
705	3	7	0	always_log_rows	0	Y
706	3	7	0	cluster_schema	0	\N
707	3	8	0	PARTITIONING_SCHEMA	0	\N
708	3	8	0	PARTITIONING_METHOD	0	none
709	3	8	0	valuename	0	id
710	3	8	0	use_database	0	N
711	3	8	0	id_connection	8	\N
712	3	8	0	schema	0	\N
713	3	8	0	seqname	0	core_external_to_loinc_map_id_seq
714	3	8	0	use_counter	0	Y
715	3	8	0	counter_name	0	\N
716	3	8	0	start_at	0	1
717	3	8	0	increment_by	0	1
718	3	8	0	max_value	0	999999999
719	3	8	0	cluster_schema	0	\N
720	3	9	0	PARTITIONING_SCHEMA	0	\N
1028	5	25	0	field_length	0	\N
1029	5	25	0	field_precision	0	\N
721	3	9	0	PARTITIONING_METHOD	0	none
722	3	9	0	compatible	0	Y
723	3	9	0	jsScript_name	0	Script 1
724	3	9	0	jsScript_script	0	var comp = Component.getString();\nvar ext_code = '';\n\nif (comp != null) {\n\text_code = CPT.getString() + "--" + comp;\n} else {\n\text_code = CPT.getString();\n};\n
725	3	9	0	jsScript_type	0	\N
726	3	9	0	field_name	0	ext_code
727	3	9	0	field_rename	0	ext_code
728	3	9	0	field_type	0	String
729	3	9	0	field_length	-1	\N
730	3	9	0	field_precision	-1	\N
731	3	9	0	cluster_schema	0	\N
732	3	10	0	PARTITIONING_SCHEMA	0	\N
733	3	10	0	PARTITIONING_METHOD	0	none
734	3	10	0	field_name	0	source_system
735	3	10	0	field_variable	0	${ESP_SOURCE_SYSTEM}
736	3	10	0	cluster_schema	0	\N
737	3	11	0	PARTITIONING_SCHEMA	0	\N
738	3	11	0	PARTITIONING_METHOD	0	none
739	3	11	0	field_name	0	created_timestamp
740	3	11	0	field_type	0	system date (fixed)
741	3	11	1	field_name	0	updated_timestamp
742	3	11	1	field_type	0	system date (fixed)
743	3	11	2	field_name	0	hostname
744	3	11	2	field_type	0	Hostname
745	3	11	3	field_name	0	timestamp
746	3	11	3	field_type	0	system date (fixed)
747	3	11	0	cluster_schema	0	\N
748	3	12	0	PARTITIONING_SCHEMA	0	\N
749	3	12	0	PARTITIONING_METHOD	0	none
750	3	12	0	id_condition	1	\N
751	3	12	0	send_true_to	0	Wait for all LOINCs to pass
752	3	12	0	send_false_to	0	Abort
753	3	12	0	cluster_schema	0	\N
754	3	13	0	PARTITIONING_SCHEMA	0	\N
755	3	13	0	PARTITIONING_METHOD	0	none
756	3	13	0	id_connection	5	\N
757	3	13	0	cache	0	Y
758	3	13	0	cache_load_all	0	N
759	3	13	0	cache_size	0	\N
760	3	13	0	lookup_schema	0	\N
761	3	13	0	lookup_table	0	core_source_system
762	3	13	0	lookup_orderby	0	\N
763	3	13	0	fail_on_multiple	0	N
764	3	13	0	eat_row_on_failure	0	Y
765	3	13	0	lookup_key_name	0	source_system
766	3	13	0	lookup_key_field	0	name
767	3	13	0	lookup_key_condition	0	LIKE
768	3	13	0	lookup_key_name2	0	\N
769	3	13	0	return_value_name	0	id
770	3	13	0	return_value_rename	0	system_id
771	3	13	0	return_value_default	0	\N
772	3	13	0	return_value_type	0	Integer
773	3	13	0	cluster_schema	0	\N
774	3	14	0	PARTITIONING_SCHEMA	0	\N
775	3	14	0	PARTITIONING_METHOD	0	none
776	3	14	0	id_connection	8	\N
777	3	14	0	cache	0	N
778	3	14	0	cache_load_all	0	N
779	3	14	0	cache_size	0	\N
780	3	14	0	lookup_schema	0	\N
781	3	14	0	lookup_table	0	conf_loinc
782	3	14	0	lookup_orderby	0	\N
783	3	14	0	fail_on_multiple	0	N
784	3	14	0	eat_row_on_failure	0	N
785	3	14	0	lookup_key_name	0	LOINC
786	3	14	0	lookup_key_field	0	loinc_num
787	3	14	0	lookup_key_condition	0	LIKE
788	3	14	0	lookup_key_name2	0	\N
789	3	14	0	return_value_name	0	loinc_num
790	3	14	0	return_value_rename	0	loinc_num
791	3	14	0	return_value_default	0	\N
792	3	14	0	return_value_type	0	String
793	3	14	0	cluster_schema	0	\N
794	3	15	0	PARTITIONING_SCHEMA	0	\N
795	3	15	0	PARTITIONING_METHOD	0	none
796	3	15	0	accept_filenames	0	N
797	3	15	0	accept_field	0	\N
798	3	15	0	accept_stepname	0	\N
799	3	15	0	separator	0	\t
800	3	15	0	enclosure	0	\N
801	3	15	0	enclosure_breaks	0	N
802	3	15	0	escapechar	0	\N
803	3	15	0	header	0	Y
804	3	15	0	nr_headerlines	0	\N
805	3	15	0	footer	0	N
806	3	15	0	nr_footerlines	1	\N
807	3	15	0	line_wrapped	0	N
808	3	15	0	nr_wraps	0	\N
809	3	15	0	layout_paged	0	N
810	3	15	0	nr_lines_per_page	0	\N
811	3	15	0	nr_lines_doc_header	0	\N
812	3	15	0	noempty	0	Y
813	3	15	0	include	0	N
814	3	15	0	include_field	0	filepath
815	3	15	0	rownum	0	N
816	3	15	0	rownumByFile	0	N
817	3	15	0	rownum_field	0	\N
818	3	15	0	format	0	Unix
819	3	15	0	encoding	0	\N
820	3	15	0	add_to_result_filenames	0	N
821	3	15	0	limit	0	\N
822	3	15	0	file_name	0	/home/rejmv/work/dev-esp/src/ESP/data/atrius-map.csv
823	3	15	0	file_mask	0	\N
824	3	15	0	file_required	0	\N
825	3	15	0	file_type	0	CSV
826	3	15	0	compression	0	None
827	3	15	0	field_name	0	CPT
828	3	15	0	field_type	0	String
829	3	15	0	field_format	0	\N
830	3	15	0	field_currency	0	\N
831	3	15	0	field_decimal	0	\N
832	3	15	0	field_group	0	\N
833	3	15	0	field_nullif	0	\N
834	3	15	0	field_ifnull	0	\N
835	3	15	0	field_position	-1	\N
836	3	15	0	field_length	-1	\N
837	3	15	0	field_precision	-1	\N
838	3	15	0	field_trim_type	0	none
839	3	15	0	field_repeat	0	N
840	3	15	1	field_name	0	Component
841	3	15	1	field_type	0	String
842	3	15	1	field_format	0	\N
843	3	15	1	field_currency	0	\N
844	3	15	1	field_decimal	0	\N
845	3	15	1	field_group	0	\N
846	3	15	1	field_nullif	0	\N
847	3	15	1	field_ifnull	0	\N
848	3	15	1	field_position	-1	\N
849	3	15	1	field_length	-1	\N
850	3	15	1	field_precision	-1	\N
851	3	15	1	field_trim_type	0	none
852	3	15	1	field_repeat	0	N
853	3	15	2	field_name	0	LOINC
854	3	15	2	field_type	0	String
855	3	15	2	field_format	0	\N
856	3	15	2	field_currency	0	\N
857	3	15	2	field_decimal	0	\N
858	3	15	2	field_group	0	\N
859	3	15	2	field_nullif	0	\N
860	3	15	2	field_ifnull	0	\N
861	3	15	2	field_position	-1	\N
862	3	15	2	field_length	-1	\N
863	3	15	2	field_precision	-1	\N
864	3	15	2	field_trim_type	0	none
865	3	15	2	field_repeat	0	N
866	3	15	0	error_ignored	0	N
867	3	15	0	error_line_skipped	0	N
868	3	15	0	error_count_field	0	\N
869	3	15	0	error_fields_field	0	\N
870	3	15	0	error_text_field	0	\N
871	3	15	0	bad_line_files_dest_dir	0	\N
872	3	15	0	bad_line_files_ext	0	warning
873	3	15	0	error_line_files_dest_dir	0	\N
874	3	15	0	error_line_files_ext	0	error
875	3	15	0	line_number_files_dest_dir	0	\N
876	3	15	0	line_number_files_ext	0	line
877	3	15	0	date_format_lenient	0	Y
878	3	15	0	date_format_locale	0	en_us
879	3	15	0	cluster_schema	0	\N
880	3	16	0	PARTITIONING_SCHEMA	0	\N
881	3	16	0	PARTITIONING_METHOD	0	none
882	3	16	0	field_name	0	loinc_num
883	3	16	0	field_rename	0	loinc_id
884	3	16	0	field_length	-1	\N
885	3	16	0	field_precision	-1	\N
886	3	16	1	field_name	0	ext_code
887	3	16	1	field_rename	0	\N
888	3	16	1	field_length	-1	\N
889	3	16	1	field_precision	-1	\N
890	3	16	2	field_name	0	id
891	3	16	2	field_rename	0	\N
892	3	16	2	field_length	-1	\N
893	3	16	2	field_precision	-1	\N
894	3	16	0	select_unspecified	0	N
895	3	16	0	cluster_schema	0	\N
896	3	17	0	PARTITIONING_SCHEMA	0	\N
897	3	17	0	PARTITIONING_METHOD	0	none
898	3	17	0	validator_field_name	0	system_id
899	3	17	0	validator_field_validation_name	0	system_id not null
900	3	17	0	validator_field_max_length	-1	\N
901	3	17	0	validator_field_min_length	-1	\N
902	3	17	0	validator_field_null_allowed	0	N
903	3	17	0	validator_field_only_null_allowed	0	N
904	3	17	0	validator_field_only_numeric_allowed	0	N
905	3	17	0	validator_field_data_type	0	Integer
906	3	17	0	validator_field_data_type_verified	0	N
907	3	17	0	validator_field_conversion_mask	0	\N
908	3	17	0	validator_field_decimal_symbol	0	\N
909	3	17	0	validator_field_grouping_symbol	0	\N
910	3	17	0	validator_field_max_value	0	\N
911	3	17	0	validator_field_min_value	0	\N
912	3	17	0	validator_field_start_string	0	\N
913	3	17	0	validator_field_end_string	0	\N
914	3	17	0	validator_field_start_string_not_allowed	0	\N
915	3	17	0	validator_field_end_string_not_allowed	0	\N
916	3	17	0	validator_field_regular_expression	0	\N
917	3	17	0	validator_field_regular_expression_not_allowed	0	\N
918	3	17	0	validator_field_error_code	0	\N
919	3	17	0	validator_field_error_description	0	system_id must not be null
920	3	17	0	validator_field_is_sourcing_values	0	N
921	3	17	0	validator_field_sourcing_step	0	\N
922	3	17	0	validator_field_sourcing_field	0	\N
923	3	17	0	cluster_schema	0	\N
924	3	18	0	PARTITIONING_SCHEMA	0	\N
925	3	18	0	PARTITIONING_METHOD	0	none
926	3	18	0	pass_all_rows	0	Y
927	3	18	0	directory	0	%%java.io.tmpdir%%
928	3	18	0	prefix	0	block
929	3	18	0	cache_size	5000	\N
930	3	18	0	compress	0	Y
931	3	18	0	cluster_schema	0	\N
932	3	19	0	PARTITIONING_SCHEMA	0	\N
933	3	19	0	PARTITIONING_METHOD	0	none
934	3	19	0	id_connection	8	\N
935	3	19	0	schema	0	\N
936	3	19	0	table	0	conf_ext_to_loinc
937	3	19	0	commit	1	\N
938	3	19	0	truncate	0	Y
939	3	19	0	ignore_errors	0	N
940	3	19	0	use_batch	0	N
941	3	19	0	partitioning_enabled	0	N
942	3	19	0	partitioning_field	0	\N
943	3	19	0	partitioning_daily	0	N
944	3	19	0	partitioning_monthly	0	Y
945	3	19	0	tablename_in_field	0	N
946	3	19	0	tablename_field	0	\N
947	3	19	0	tablename_in_table	0	Y
948	3	19	0	return_keys	0	N
949	3	19	0	return_field	0	\N
950	3	19	0	cluster_schema	0	\N
1030	5	25	0	field_trim_type	0	none
1031	5	25	1	field_name	0	AttrCode
1032	5	25	1	field_type	0	String
1033	5	25	1	field_format	0	\N
1034	5	25	1	field_currency	0	\N
1035	5	25	1	field_decimal	0	\N
1036	5	25	1	field_group	0	\N
1037	5	25	1	field_length	0	\N
1038	5	25	1	field_precision	0	\N
1039	5	25	1	field_trim_type	0	none
1040	5	25	2	field_name	0	AttrMnemonic
1041	5	25	2	field_type	0	String
1042	5	25	2	field_format	0	\N
1043	5	25	2	field_currency	0	\N
1044	5	25	2	field_decimal	0	\N
1045	5	25	2	field_group	0	\N
1046	5	25	2	field_length	0	\N
1047	5	25	2	field_precision	0	\N
1048	5	25	2	field_trim_type	0	none
1049	5	25	3	field_name	0	AttrName
1050	5	25	3	field_type	0	String
1051	5	25	3	field_format	0	\N
1052	5	25	3	field_currency	0	\N
1053	5	25	3	field_decimal	0	\N
1054	5	25	3	field_group	0	\N
1055	5	25	3	field_length	0	\N
1056	5	25	3	field_precision	0	\N
1057	5	25	3	field_trim_type	0	none
1058	5	25	4	field_name	0	LOINC
1059	5	25	4	field_type	0	String
1060	5	25	4	field_format	0	\N
1061	5	25	4	field_currency	0	\N
1062	5	25	4	field_decimal	0	\N
1063	5	25	4	field_group	0	\N
1064	5	25	4	field_length	0	\N
1065	5	25	4	field_precision	0	\N
1066	5	25	4	field_trim_type	0	none
1067	5	25	5	field_name	0	LOINC Name
1068	5	25	5	field_type	0	String
1069	5	25	5	field_format	0	\N
1070	5	25	5	field_currency	0	\N
1071	5	25	5	field_decimal	0	\N
1072	5	25	5	field_group	0	\N
1073	5	25	5	field_length	0	\N
1074	5	25	5	field_precision	0	\N
1075	5	25	5	field_trim_type	0	none
1076	5	25	0	cluster_schema	0	\N
1077	5	26	0	PARTITIONING_SCHEMA	0	\N
1078	5	26	0	PARTITIONING_METHOD	0	none
1079	5	26	0	field_name	0	AttrCode
1080	5	26	0	field_rename	0	ext_code
1081	5	26	0	field_length	-1	\N
1082	5	26	0	field_precision	-1	\N
1083	5	26	1	field_name	0	AttrName
1084	5	26	1	field_rename	0	ext_name
1085	5	26	1	field_length	-1	\N
1086	5	26	1	field_precision	-1	\N
1087	5	26	2	field_name	0	loinc_num
1088	5	26	2	field_rename	0	loinc_id
1089	5	26	2	field_length	-1	\N
1090	5	26	2	field_precision	-1	\N
1091	5	26	0	select_unspecified	0	N
1092	5	26	0	cluster_schema	0	\N
1093	5	27	0	PARTITIONING_SCHEMA	0	\N
1094	5	27	0	PARTITIONING_METHOD	0	none
1095	5	27	0	pass_all_rows	0	Y
1096	5	27	0	directory	0	%%java.io.tmpdir%%
1097	5	27	0	prefix	0	block
1098	5	27	0	cache_size	5000	\N
\.


--
-- Data for Name: r_step_database; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_step_database (id_transformation, id_step, id_database) FROM stdin;
\.


--
-- Data for Name: r_step_type; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_step_type (id_step_type, code, description, helptext) FROM stdin;
1	CubeOutput	Serialize to file	Write rows of data to a data cube
2	ClosureGenerator	Closure Generator	This step allows you to generates a closure table using parent-child relationships.
3	CsvInput	CSV file input	Simple CSV file input
4	FixedInput	Fixed file input	Fixed file input
5	FieldSplitter	Split Fields	When you want to split a single field into more then one, use this step type.
6	CubeInput	De-serialize from file	Read rows of data from a data cube.
7	ValueMapper	Value Mapper	Maps values of a certain field from one value to another
8	WebServiceLookup	Web services lookup	Look up information using web services (WSDL)
9	RowGenerator	Generate Rows	Generate a number of empty or equal rows.
10	Dummy	Dummy (do nothing)	This step type doesn't do anything.\nIt's useful however when testing things or in certain situations where you want to split streams.
11	Append	Append streams	Append 2 streams in an ordered way
12	TableInput	Table input	Read information from a database table.
13	SocketReader	Socket reader	Socket reader.  A socket client that connects to a server (Socket Writer step).
14	SocketWriter	Socket writer	Socket writer.  A socket server that can send rows of data to a socket reader.
15	SelectValues	Select values	Select or remove fields in a row.\nOptionally, set the field meta-data: type, length and precision.
16	TextFileInput	Text file input	Read data from a text file in several formats.\nThis data can then be passed on to the next step(s)...
17	Calculator	Calculator	Create new fields by performing simple calculations
18	Constant	Add constants	Add one or more constants to the input rows
19	Abort	Abort	Abort a transformation
20	Sequence	Add sequence	Get the next value from an sequence
21	TableOutput	Table output	Write information to a database table
22	SortRows	Sort rows	Sort rows based upon field values (ascending or descending)
23	OraBulkLoader	Oracle Bulk Loader	Use Oracle Bulk Loader to load data
24	Injector	Injector	Injector step to allow to inject rows into the transformation through the java API
25	FilterRows	Filter rows	Filter rows using simple equations
26	TextFileOutput	Text file output	Write rows to a text file.
27	SystemInfo	Get System Info	Get information from the system like system date, arguments, etc.
28	StreamLookup	Stream lookup	Look up values coming from another stream in the transformation.
29	Unique	Unique rows	Remove double rows and leave only unique occurrences.\nThis works only on a sorted input.\nIf the input is not sorted, only double consecutive rows are handled correctly.
30	DBLookup	Database lookup	Look up values in a database using field values
31	DBJoin	Database join	Execute a database query using stream values as parameters
32	DimensionLookup	Dimension lookup/update	Update a slowly changing dimension in a data warehouse.\nAlternatively, look up information in this dimension.
33	ExcelInput	Excel Input	Read data from a Microsoft Excel Workbook.  This works with Excel sheets of Excel 95, 97 and 2000.
34	CombinationLookup	Combination lookup/update	Update a junk dimension in a data warehouse.\nAlternatively, look up information in this dimension.\nThe primary key of a junk dimension are all the fields.
35	ScriptValueMod	Modified Java Script Value	This is a modified plugin for the Scripting Values with improved interface and performance.\nWritten & donated to open source by Martin Lange, Proconis : http://www.proconis.de
36	JoinRows	Join Rows (cartesian product)	The output of this step is the cartesian product of the input streams.\nThe number of rows is the multiplication of the number of rows in the input streams.
37	Update	Update	Update data in a database table based upon keys
38	InsertUpdate	Insert / Update	Update or insert rows in a database based upon keys.
39	Delete	Delete	Delete data in a database table based upon keys
40	MappingInput	Mapping input specification	Specify the input interface of a mapping
41	Mapping	Mapping (sub-transformation)	Run a mapping (sub-transformation), use MappingInput and MappingOutput to specify the fields interface
42	MappingOutput	Mapping output specification	Specify the output interface of a mapping
43	SetVariable	Set Variables	Set environment variables based on a single input row.
44	GetVariable	Get Variables	Determine the values of certain (environment or Kettle) variables and put them in field values.
45	NullIf	Null if...	Sets a field value to null if it is equal to a constant value
46	ExecSQL	Execute SQL script	Execute an SQL script, optionally parameterized using input rows
47	RowsFromResult	Get rows from result	This allows you to read rows from a previous entry in a job.
48	RowsToResult	Copy rows to result	Use this step to write rows to the executing job.\nThe information will then be passed to the next entry in this job.
49	BlockingStep	Blocking Step	This step blocks until all incoming rows have been processed.  Subsequent steps only recieve the last input row to this step.
50	HTTP	HTTP client	Call a web service over HTTP by supplying a base URL by allowing parameters to be set dynamically
51	MergeRows	Merge Rows (diff)	Merge two streams of rows, sorted on a certain key.  The two streams are compared and the equals, changed, deleted and new rows are flagged.
52	GetFileNames	Get File Names	Get file names from the operating system and send them to the next step.
53	FilesFromResult	Get files from result	This step allows you to read filenames used or generated in a previous entry in a job.
54	FilesToResult	Set files in result	This step allows you to set filenames in the result of this transformation.\nSubsequent job entries can then use this information.
55	GroupBy	Group by	Builds aggregates in a group by fashion.\nThis works only on a sorted input.\nIf the input is not sorted, only double consecutive rows are handled correctly.
56	MergeJoin	Merge Join	Joins two streams on a given key and outputs a joined set. The input streams must be sorted on the join key
57	SortedMerge	Sorted Merge	Sorted Merge
58	XMLInput	XML Input	Read data from an XML file
59	XMLInputSax	Streaming XML Input	Read data from an XML file in a streaming fashing, working faster and consuming less memory
60	XMLOutput	XML Output	Write data to an XML file
61	ExcelOutput	Excel Output	Stores records into an Excel (XLS) document with formatting information.
62	DBProc	Call DB Procedure	Get back information by calling a database procedure.
63	Denormaliser	Row denormaliser	Denormalises rows by looking up key-value pairs and by assigning them to new fields in the output rows.\nThis method aggregates and needs the input rows to be sorted on the grouping fields
64	Normaliser	Row Normaliser	De-normalised information can be normalised using this step type.
65	Flattener	Row flattener	Flattens consecutive rows based on the order in which they appear in the input stream
66	XBaseInput	XBase input	Reads records from an XBase type of database file (DBF)
67	AccessOutput	Access Output	Stores records into an MS-Access database table.
68	RegexEval	Regex Evaluation	Regular expression Evaluation\nThis step uses a regular expression to evaluate a field. It can also extract new fields out of an existing field with capturing groups.
69	AccessInput	Access Input	Read data from a Microsoft Access file
70	AddXML	Add XML	Encode several fields into an XML fragment
71	AggregateRows	Aggregate Rows	This step type allows you to aggregate rows.\nIt can't do groupings.
72	MondrianInput	Mondrian Input	Execute and retrive data using an MDX query against a Pentaho Analyses OLAP server (Mondrian)
73	GetFilesRowsCount	Get Files Rows Count	Get Files Rows Count
74	LDAPInput	LDAP Input	Read data from LDAP host
75	getXMLData	Get data from XML	Get data from XML file by using XPath.\n This step also allows you to parse XML defined in a previous field.
76	XSDValidator	XSD Validator	Validate XML source (files or streams) against XML Schema Definition.
77	XSLT	XSL Transformation	Transform XML stream using XSL (eXtensible Stylesheet Language).
78	Validator	Data Validator	Validates passing data based on a set of rules
79	SQLFileOutput	SQL File Output	Output SQL INSERT statements to file
80	SplitFieldToRows3	Split field to rows	Splits a single string field by delimiter and creates a new row for each split term
81	PropertyInput	Property Input	Read data (key, value) from properties files.
82	GPBulkLoader	Greenplum Bulk Loader	Greenplum Bulk Loader
83	PGBulkLoader	PostgreSQL Bulk Loader	PostgreSQL Bulk Loader
84	LDIFInput	LDIF Input	Read data from LDIF files
85	PropertyOutput	Properties Output	Write data to properties file
86	SwitchCase	Switch / Case	Switch a row to a certain target step based on the case value in a field.
87	XMLJoin	XML Join	Joins a stream of XML-Tags into a target XML string
88	StepMetastructure	Metadata structure of stream	This is a step to read the metadata of the incoming stream.
89	TableExists	Table exists	Check if a table exists on a specified connection
90	ColumnExists	Check if a column exists	Check if a column exists in a table on a specified connection.
91	FileExists	File exists	Check if a file exists
92	CloneRow	Clone row	Clone a row as many times as needed
93	Delay	Delay row	Output each input row after a delay
94	CheckSum	Add a checksum	Add a checksum column for each input row
95	RandomValue	Generate random value	Generate random value
96	GetSubFolders	Get SubFolder names	Read a parent folder and return all subfolders
97	MonetDBBulkLoader	MonetDB Bulk Loader	Load data into MonetDB by using their bulk load command in streaming mode.
98	MailValidator	Mail Validator	Check if an email address is valid.
99	Mail	Mail	Send eMail.
100	CreditCardValidator	Credit card validator	The Credit card validator step will help you tell:\n(1) if a credit card number is valid (uses LUHN10 (MOD-10) algorithm)\n(2) which credit card vendor handles that number\n(VISA, MasterCard, Diners Club, EnRoute, American Express (AMEX),...)
101	DummyPlugin	Dummy plugin	This is a dummy plugin test step
102	ShapeFileReader	ESRI Shapefile Reader	Reads shape file data from an ESRI shape file and linked DBF file
\.


--
-- Data for Name: r_trans_attribute; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_attribute (id_trans_attribute, id_transformation, nr, code, value_num, value_str) FROM stdin;
1	1	0	UNIQUE_CONNECTIONS	0	N
2	1	0	FEEDBACK_SHOWN	0	Y
3	1	0	FEEDBACK_SIZE	0	\N
4	1	0	USING_THREAD_PRIORITIES	0	Y
5	1	0	SHARED_FILE	0	\N
6	1	0	CAPTURE_STEP_PERFORMANCE	0	N
7	1	0	STEP_PERFORMANCE_CAPTURING_DELAY	0	\N
8	1	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
25	5	0	UNIQUE_CONNECTIONS	0	N
26	5	0	FEEDBACK_SHOWN	0	Y
27	5	0	FEEDBACK_SIZE	0	\N
28	5	0	USING_THREAD_PRIORITIES	0	Y
29	5	0	SHARED_FILE	0	\N
30	5	0	CAPTURE_STEP_PERFORMANCE	0	N
31	5	0	STEP_PERFORMANCE_CAPTURING_DELAY	0	\N
32	5	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
9	2	0	UNIQUE_CONNECTIONS	0	N
10	2	0	FEEDBACK_SHOWN	0	Y
11	2	0	FEEDBACK_SIZE	50000	\N
12	2	0	USING_THREAD_PRIORITIES	0	Y
13	2	0	SHARED_FILE	0	\N
14	2	0	CAPTURE_STEP_PERFORMANCE	0	N
15	2	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
16	2	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
17	3	0	UNIQUE_CONNECTIONS	0	N
18	3	0	FEEDBACK_SHOWN	0	Y
19	3	0	FEEDBACK_SIZE	0	\N
20	3	0	USING_THREAD_PRIORITIES	0	Y
21	3	0	SHARED_FILE	0	\N
22	3	0	CAPTURE_STEP_PERFORMANCE	0	N
23	3	0	STEP_PERFORMANCE_CAPTURING_DELAY	0	\N
24	3	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
\.


--
-- Data for Name: r_trans_cluster; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_cluster (id_trans_cluster, id_transformation, id_cluster) FROM stdin;
\.


--
-- Data for Name: r_trans_hop; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_hop (id_trans_hop, id_transformation, id_step_from, id_step_to, enabled) FROM stdin;
1	1	1	2	Y
2	1	2	3	Y
3	2	4	5	Y
4	2	5	6	Y
14	5	26	28	Y
15	5	25	24	Y
16	5	24	22	Y
17	5	22	20	Y
18	5	22	27	Y
19	5	27	26	Y
5	3	16	19	Y
6	3	14	12	Y
7	3	12	7	Y
8	3	12	18	Y
9	3	15	10	Y
10	3	9	14	Y
11	3	18	8	Y
12	3	8	16	Y
13	3	10	9	Y
\.


--
-- Data for Name: r_trans_note; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_note (id_transformation, id_note) FROM stdin;
\.


--
-- Data for Name: r_trans_partition_schema; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_partition_schema (id_trans_partition_schema, id_transformation, id_partition_schema) FROM stdin;
\.


--
-- Data for Name: r_trans_slave; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_slave (id_trans_slave, id_transformation, id_slave) FROM stdin;
\.


--
-- Data for Name: r_trans_step_condition; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_step_condition (id_transformation, id_step, id_condition) FROM stdin;
3	12	1
5	22	2
\.


--
-- Data for Name: r_transformation; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_transformation (id_transformation, id_directory, name, description, extended_description, trans_version, trans_status, id_step_read, id_step_write, id_step_input, id_step_output, id_step_update, id_database_log, table_name_log, use_batchid, use_logfield, id_database_maxdate, table_name_maxdate, field_name_maxdate, offset_maxdate, diff_maxdate, created_user, created_date, modified_user, modified_date, size_rowset) FROM stdin;
1	1	Load LOINC db	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	\N	esp	2009-04-01 13:44:35.167	10000
2	1	Load LOINC Additions	\N	\N	\N	1	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-20 17:25:14.602	esp	2009-04-01 13:46:38.307	10000
3	1	Load External Code to LOINC Maps -- Atrius	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	\N	esp	2009-04-01 14:18:06.967	10000
5	1	Load External Code to LOINC Maps -- North Adams	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	\N	esp	2009-04-02 16:17:19.019	10000
\.


--
-- Data for Name: r_user; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_user (id_user, id_profile, login, password, name, description, enabled) FROM stdin;
1	1	admin	2be98afc86aa7f2e4cb79ce71da9fa6d4	Administrator	User manager	Y
2	3	guest	2be98afc86aa7f2e4cb79ce77cb97bcce	Guest account	Read-only guest account	Y
3	2	esp	\N	ESP user	\N	Y
\.


--
-- Data for Name: r_value; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_value (id_value, name, value_type, value_str, is_null) FROM stdin;
\.


--
-- Data for Name: r_version; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_version (id_version, major_version, minor_version, upgrade_date, is_upgrade) FROM stdin;
1	3	0	2009-04-01 13:39:57.898	N
\.


--
-- Name: idx_database_attribute_ak; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE UNIQUE INDEX idx_database_attribute_ak ON r_database_attribute USING btree (id_database, code);


--
-- Name: idx_directory_ak; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE UNIQUE INDEX idx_directory_ak ON r_directory USING btree (id_directory_parent, directory_name);


--
-- Name: idx_jobentry_attribute_lookup; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE UNIQUE INDEX idx_jobentry_attribute_lookup ON r_jobentry_attribute USING btree (id_jobentry_attribute, code, nr);


--
-- Name: idx_profile_permission_pk; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE UNIQUE INDEX idx_profile_permission_pk ON r_profile_permission USING btree (id_profile, id_permission);


--
-- Name: idx_step_attribute_lookup; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE UNIQUE INDEX idx_step_attribute_lookup ON r_step_attribute USING btree (id_step, code, nr);


--
-- Name: idx_step_database_lu1; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE INDEX idx_step_database_lu1 ON r_step_database USING btree (id_transformation);


--
-- Name: idx_step_database_lu2; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE INDEX idx_step_database_lu2 ON r_step_database USING btree (id_database);


--
-- Name: idx_trans_attribute_lookup; Type: INDEX; Schema: public; Owner: pdi; Tablespace: 
--

CREATE UNIQUE INDEX idx_trans_attribute_lookup ON r_trans_attribute USING btree (id_transformation, code, nr);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

