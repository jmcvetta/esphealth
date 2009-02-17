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
1	0	N	-      	last update	IS NOT NULL	\N	-1
2	0	N	-      	\N	=	\N	-1
3	2	N	-      	ext_physician_id	IS NOT NULL	\N	-1
4	2	N	AND    	ext_physician_id	<>	\N	1
5	0	N	-      	loinc_num	IS NOT NULL	\N	-1
\.


--
-- Data for Name: r_database; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_database (id_database, name, id_database_type, id_database_contype, host_name, database_name, port, username, password, servername, data_tbs, index_tbs) FROM stdin;
1	ESP	36	1	localhost	esp	3306	ESP	Encrypted 616568693769654d6f6f546836546f6f71756f6832617535d1e1c0a708c69ba9a21aa629df9aa4d5	\N	\N	\N
4	ESP Staging (PostgreSQL)	6	1	localhost	esp_staging	5432	esp_kettle	Encrypted 58764e513733394a387441756d304e79534e6c6736556a65c9edff8e25e1b9aea011b445c88bf68f	\N	\N	\N
5	ESP Warehouse (PostgreSQL)	6	1	localhost	esp_warehouse	5432	esp_kettle	Encrypted 58764e513733394a387441756d304e79534e6c6736556a65c9edff8e25e1b9aea011b445c88bf68f	\N	\N	\N
6	ESP (MySQL)	36	1	localhost	esp	3306	ESP	Encrypted 616568693769654d6f6f546836546f6f71756f6832617535d1e1c0a708c69ba9a21aa629df9aa4d5	\N	\N	\N
7	ESP (PostgreSQL)	6	1	localhost	esp	5432	esp	Encrypted 5236307a547a73376f336a6f776b32595053703652474a6a5478376d385858686a6eedf49ba42fc1b1bc8a40f667f0bf84e3	\N	\N	\N
\.


--
-- Data for Name: r_database_attribute; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_database_attribute (id_database_attribute, id_database, code, value_str) FROM stdin;
357	1	SQL_CONNECT	\N
358	1	STREAM_RESULTS	Y
359	1	USE_POOLING	N
360	1	FORCE_IDENTIFIERS_TO_LOWERCASE	N
361	1	IS_CLUSTERED	N
362	1	QUOTE_ALL_FIELDS	N
363	1	FORCE_IDENTIFIERS_TO_UPPERCASE	N
364	1	PORT_NUMBER	3306
365	4	SQL_CONNECT	\N
366	4	USE_POOLING	N
367	4	FORCE_IDENTIFIERS_TO_LOWERCASE	N
368	4	IS_CLUSTERED	N
369	4	QUOTE_ALL_FIELDS	N
370	4	FORCE_IDENTIFIERS_TO_UPPERCASE	N
371	4	PORT_NUMBER	5432
372	5	SQL_CONNECT	\N
373	5	USE_POOLING	N
149	3	SQL_CONNECT	\N
150	3	STREAM_RESULTS	Y
151	3	USE_POOLING	N
152	3	FORCE_IDENTIFIERS_TO_LOWERCASE	N
153	3	IS_CLUSTERED	N
154	3	QUOTE_ALL_FIELDS	N
155	3	FORCE_IDENTIFIERS_TO_UPPERCASE	N
156	3	PORT_NUMBER	3306
374	5	FORCE_IDENTIFIERS_TO_LOWERCASE	N
375	5	IS_CLUSTERED	N
376	5	QUOTE_ALL_FIELDS	N
377	5	FORCE_IDENTIFIERS_TO_UPPERCASE	N
378	5	PORT_NUMBER	5432
379	6	SQL_CONNECT	\N
380	6	STREAM_RESULTS	Y
381	6	USE_POOLING	N
382	6	FORCE_IDENTIFIERS_TO_LOWERCASE	N
383	6	QUOTE_ALL_FIELDS	N
384	6	IS_CLUSTERED	N
385	6	FORCE_IDENTIFIERS_TO_UPPERCASE	N
386	6	PORT_NUMBER	3306
387	7	SQL_CONNECT	\N
388	7	USE_POOLING	N
389	7	FORCE_IDENTIFIERS_TO_LOWERCASE	N
390	7	QUOTE_ALL_FIELDS	N
391	7	IS_CLUSTERED	N
392	7	FORCE_IDENTIFIERS_TO_UPPERCASE	N
393	7	PORT_NUMBER	5432
72	2	SQL_CONNECT	\N
73	2	STREAM_RESULTS	Y
74	2	USE_POOLING	N
75	2	FORCE_IDENTIFIERS_TO_LOWERCASE	N
76	2	IS_CLUSTERED	N
77	2	QUOTE_ALL_FIELDS	N
78	2	FORCE_IDENTIFIERS_TO_UPPERCASE	N
79	2	PORT_NUMBER	3306
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
1	0	Atrius
2	0	esp_warehouse
3	0	esp
4	3	staging
5	4	epic
6	3	load
\.


--
-- Data for Name: r_job; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_job (id_job, id_directory, name, description, extended_description, job_version, job_status, id_database_log, table_name_log, created_user, created_date, modified_user, modified_date, use_batch_id, pass_batch_id, use_logfield, shared_file) FROM stdin;
2	1	Atrius Data Import	\N	\N	\N	0	-1	\N	jason	2009-01-26 13:29:42.753	jason	2009-01-26 15:41:13.23	Y	N	Y	\N
\.


--
-- Data for Name: r_job_hop; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_job_hop (id_job_hop, id_job, id_jobentry_copy_from, id_jobentry_copy_to, enabled, evaluation, unconditional) FROM stdin;
1	2	1	2	Y	Y	Y
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
1	2	10	START	Special entries
2	2	5	Truncate and reload staging tables	SQL
\.


--
-- Data for Name: r_jobentry_attribute; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_jobentry_attribute (id_jobentry_attribute, id_job, id_jobentry, nr, code, value_num, value_str) FROM stdin;
1	2	1	0	start	0.00	Y
2	2	1	0	dummy	0.00	N
3	2	1	0	repeat	0.00	N
4	2	1	0	schedulerType	0.00	\N
5	2	1	0	intervalSeconds	0.00	\N
6	2	1	0	intervalMinutes	60.00	\N
7	2	1	0	hour	12.00	\N
8	2	1	0	minutes	0.00	\N
9	2	1	0	weekDay	1.00	\N
10	2	1	0	dayOfMonth	1.00	\N
11	2	2	0	connection	0.00	ESP
12	2	2	0	sql	0.00	truncate esp_demog;\ninsert into esp_demog select * from esp.esp_demog;\n
13	2	2	0	useVariableSubstitution	0.00	F
14	2	2	0	sqlfromfile	0.00	F
15	2	2	0	sqlfilename	0.00	\N
16	282	0	0	server	0.00	localhost
17	282	0	0	port	0.00	\N
18	282	0	0	destination	0.00	jason.mcvetta@channing.harvard.edu
19	282	0	0	destinationCc	0.00	\N
20	282	0	0	destinationBCc	0.00	\N
21	282	0	0	replyto	0.00	jason.mcvetta@channing.harvard.edu
22	282	0	0	replytoname	0.00	External Code to LOINC Map Loader
23	282	0	0	subject	0.00	LOINC Number Not Found
24	282	0	0	include_date	0.00	Y
25	282	0	0	include_subfolders	0.00	N
26	282	0	0	zipFilenameDynamic	0.00	N
27	282	0	0	isFilenameDynamic	0.00	N
28	282	0	0	dynamicFieldname	0.00	\N
29	282	0	0	dynamicWildcard	0.00	\N
30	282	0	0	dynamicZipFilename	0.00	\N
31	282	0	0	sourcefilefoldername	0.00	\N
32	282	0	0	sourcewildcard	0.00	\N
33	282	0	0	contact_person	0.00	\N
34	282	0	0	contact_phone	0.00	\N
35	282	0	0	comment	0.00	The following LOINC number was not found:
36	282	0	0	encoding	0.00	UTF-8
37	282	0	0	priority	0.00	normal
38	282	0	0	importance	0.00	normal
39	282	0	0	include_files	0.00	N
40	282	0	0	use_auth	0.00	N
41	282	0	0	use_secure_auth	0.00	N
42	282	0	0	auth_user	0.00	\N
43	282	0	0	auth_password	0.00	Encrypted 
44	282	0	0	only_comment	0.00	N
45	282	0	0	use_HTML	0.00	Y
46	282	0	0	use_Priority	0.00	N
47	282	0	0	secureconnectiontype	0.00	SSL
48	282	0	0	zip_files	0.00	N
49	282	0	0	zip_name	0.00	\N
50	282	0	0	zip_limit_size	0.00	0
\.


--
-- Data for Name: r_jobentry_copy; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_jobentry_copy (id_jobentry_copy, id_jobentry, id_job, id_jobentry_type, nr, gui_location_x, gui_location_y, gui_draw, parallel) FROM stdin;
1	1	2	10	0	185	44	Y	N
2	2	2	5	0	187	156	Y	N
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
1	This transformation converts the code map document provided\nby North Adams to a CSV file suitable for use with preLoader.py	345	39	374	36
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
1	3.0	2009-01-22 15:17:10.339	admin	Creation of the Kettle repository
2	3.0	2009-01-23 10:20:13.836	jason	save transformation 'North Adams code map'
3	3.0	2009-01-23 10:30:25.831	jason	save transformation 'North Adams code map'
4	3.0	2009-01-23 16:07:30.622	jason	save transformation 'North Adams code map'
5	3.0	2009-01-23 16:07:48.356	jason	save transformation 'North Adams code map'
6	3.0	2009-01-23 16:11:27.597	jason	save transformation 'North Adams code map'
7	3.0	2009-01-23 16:14:42.899	jason	save transformation 'North Adams code map'
8	3.0	2009-01-26 13:29:42.879	jason	save job 'Job 1'
9	3.0	2009-01-26 13:30:25.224	jason	save job 'Atrius Data Import'
10	3.0	2009-01-26 13:32:27.654	jason	save transformation 'Atrius Immunizations'
11	3.0	2009-01-26 13:44:08.139	jason	save transformation 'Atrius Immunizations'
12	3.0	2009-01-26 13:47:12.495	jason	save transformation 'Atrius Immunizations'
13	3.0	2009-01-26 13:55:37.062	jason	save transformation 'Read Atrius Demographic Info'
14	3.0	2009-01-26 15:05:29.615	jason	save transformation 'Read Atrius Demographic Info'
15	3.0	2009-01-26 15:05:57.297	jason	save transformation 'Atrius Immunizations'
16	3.0	2009-01-26 15:18:03.67	jason	save transformation 'Prepare Staging Area'
17	3.0	2009-01-26 15:30:53.97	jason	save job 'Atrius Data Import'
18	3.0	2009-01-26 15:31:16.434	jason	save job 'Atrius Data Import'
19	3.0	2009-01-26 15:41:13.299	jason	save job 'Atrius Data Import'
20	3.0	2009-01-26 15:47:30.497	jason	save transformation 'Read Atrius Demographic Info'
21	3.0	2009-01-26 15:48:17.672	jason	save transformation 'Read Atrius Demographic Info'
22	3.0	2009-01-26 15:51:40.869	jason	save transformation 'Read Atrius Demographic Info'
23	3.0	2009-01-26 15:52:59.994	jason	save transformation 'Load Atrius demographics to staging'
24	3.0	2009-01-26 15:54:49.272	jason	save transformation 'Read Atrius Demographic Info'
25	3.0	2009-01-26 16:00:54.122	jason	save transformation 'Read Atrius Demographic Info'
26	3.0	2009-01-26 16:07:03.361	jason	save transformation 'Read Atrius Demographic Info'
27	3.0	2009-01-26 16:11:22.548	jason	save transformation 'Read Atrius Demographic Info'
28	3.0	2009-01-26 16:35:08.872	jason	save transformation 'Read Atrius Demographic Info'
29	3.0	2009-01-26 16:35:36.739	jason	save transformation 'Read Atrius Demographic Info'
30	3.0	2009-01-26 16:36:08.734	jason	save transformation 'Read Atrius Demographic Info'
31	3.0	2009-01-26 16:39:24.367	jason	save transformation 'Read Atrius Demographic Info'
32	3.0	2009-01-26 16:40:11.424	jason	save transformation 'Read Atrius Demographic Info'
33	3.0	2009-01-26 16:59:18.406	jason	save transformation 'Read Atrius Demographic Info'
34	3.0	2009-01-27 11:12:31.334	jason	save transformation 'North Adams code map - straight to db'
35	3.0	2009-01-27 11:15:57.581	jason	save transformation 'North Adams code map - straight to db'
36	3.0	2009-01-27 11:16:27.01	jason	save transformation 'North Adams code map - straight to db'
37	3.0	2009-01-27 11:17:40.981	jason	save transformation 'North Adams code map - straight to db'
38	3.0	2009-01-27 11:19:20.491	jason	save transformation 'North Adams code map - straight to db'
39	3.0	2009-01-27 11:27:07.096	jason	save transformation 'North Adams code map - straight to db'
40	3.0	2009-01-27 11:31:32.114	jason	save transformation 'North Adams code map - straight to db'
41	3.0	2009-01-27 11:43:23.145	jason	save transformation 'North Adams code map'
42	3.0	2009-01-27 11:45:00.39	jason	save transformation 'North Adams code map'
43	3.0	2009-01-27 11:46:27.224	jason	save transformation 'North Adams code map'
44	3.0	2009-01-27 12:42:38.892	jason	save transformation 'North Adams code map'
45	3.0	2009-01-27 12:44:54.85	jason	save transformation 'North Adams code map'
46	3.0	2009-01-27 12:45:14.351	jason	save transformation 'North Adams code map'
47	3.0	2009-01-27 12:45:49.929	jason	save transformation 'North Adams code map'
48	3.0	2009-01-27 15:18:17.778	jason	save transformation 'North Adams code map'
49	3.0	2009-02-05 10:15:32.371	jason	save transformation 'Load Patient Dimension'
50	3.0	2009-02-05 10:16:26.298	jason	save transformation 'Load Patient Dimension'
51	3.0	2009-02-05 10:17:13.033	jason	save transformation 'Load Patient Dimension'
52	3.0	2009-02-05 10:30:41.415	jason	save transformation 'Load Patient Dimension'
53	3.0	2009-02-05 10:31:59.996	jason	save transformation 'Load Patient Dimension'
54	3.0	2009-02-05 10:33:03.525	jason	save transformation 'Load Patient Dimension'
55	3.0	2009-02-05 10:34:01.859	jason	save transformation 'Load Patient Dimension'
56	3.0	2009-02-05 10:34:42.747	jason	save transformation 'Load Patient Dimension'
57	3.0	2009-02-05 10:36:07.364	jason	save transformation 'Load Patient Dimension'
58	3.0	2009-02-05 10:38:50.104	jason	save transformation 'Load Patient Dimension'
59	3.0	2009-02-05 10:39:55.047	jason	save transformation 'Load Patient Dimension'
60	3.0	2009-02-05 10:54:12.672	jason	save transformation 'Load Patient Dimension'
61	3.0	2009-02-05 11:00:05.943	jason	save transformation 'Load Patient Dimension'
62	3.0	2009-02-05 11:01:56.64	jason	save transformation 'Load Patient Dimension'
63	3.0	2009-02-05 11:11:51.91	jason	save transformation 'Load Patient Dimension'
64	3.0	2009-02-05 11:12:38.152	jason	save transformation 'Load Patient Dimension'
65	3.0	2009-02-05 11:20:45.088	jason	save transformation 'Load Patient Dimension'
66	3.0	2009-02-05 11:21:05.204	jason	save transformation 'Load Patient Dimension'
67	3.0	2009-02-05 11:22:22.517	jason	save transformation 'Load Patient Dimension'
68	3.0	2009-02-05 11:23:06.844	jason	save transformation 'Load Patient Dimension'
69	3.0	2009-02-05 11:23:45.23	jason	save transformation 'Load Provider Dimension'
70	3.0	2009-02-05 11:42:33.976	jason	save transformation 'Load Patient Dimension'
71	3.0	2009-02-05 12:54:18.763	jason	save transformation 'Load Patient Dimension'
72	3.0	2009-02-05 13:00:22.791	jason	save transformation 'Load Provider Dimension'
73	3.0	2009-02-05 13:01:06.69	jason	save transformation 'Load Patient Dimension'
74	3.0	2009-02-05 13:01:46.847	jason	save transformation 'Load Patient Dimension'
75	3.0	2009-02-05 13:03:28.896	jason	save transformation 'Load Patient Dimension'
76	3.0	2009-02-05 13:09:17.578	jason	save transformation 'Load Patient Dimension'
77	3.0	2009-02-05 13:10:09.664	jason	save transformation 'Load Patient Dimension'
78	3.0	2009-02-05 13:10:58.706	jason	save transformation 'Load Patient Dimension'
79	3.0	2009-02-05 13:12:09.723	jason	save transformation 'Load Provider Dimension'
80	3.0	2009-02-05 13:12:40.309	jason	save transformation 'Load Provider Dimension'
81	3.0	2009-02-05 13:15:57.821	jason	save transformation 'Load Lab Result Fact'
82	3.0	2009-02-05 13:49:25.748	jason	save transformation 'Load Lab Result Fact'
83	3.0	2009-02-05 13:53:01.936	jason	save transformation 'Load Lab Result Fact'
84	3.0	2009-02-05 13:54:44.685	jason	save transformation 'Load Lab Result Fact'
85	3.0	2009-02-05 13:55:11.538	jason	save transformation 'Load Lab Result Fact'
86	3.0	2009-02-05 13:57:57.166	jason	save transformation 'Load Lab Result Fact'
87	3.0	2009-02-05 14:01:02.825	jason	save transformation 'Load Lab Result Fact'
88	3.0	2009-02-05 14:01:45.203	jason	save transformation 'Load Lab Result Fact'
89	3.0	2009-02-05 14:02:59.716	jason	save transformation 'Load Lab Result Fact'
90	3.0	2009-02-05 14:04:17.818	jason	save transformation 'Load Lab Result Fact'
91	3.0	2009-02-05 14:04:34.213	jason	save transformation 'Load Provider Dimension'
92	3.0	2009-02-05 14:04:46.677	jason	save transformation 'Load Patient Dimension'
93	3.0	2009-02-05 14:05:17.508	jason	save transformation 'Load Patient Dimension'
94	3.0	2009-02-05 14:06:31.72	jason	save transformation 'Load Provider Dimension'
95	3.0	2009-02-05 14:06:59.802	jason	save transformation 'Load Provider Dimension'
96	3.0	2009-02-05 14:09:04.23	jason	save transformation 'Load Patient Dimension'
97	3.0	2009-02-05 14:09:31.054	jason	save transformation 'Load Patient Dimension'
98	3.0	2009-02-05 14:10:36.20	jason	save transformation 'Load Lab Result Fact'
99	3.0	2009-02-05 14:11:22.436	jason	save transformation 'Load Lab Result Fact'
100	3.0	2009-02-05 14:12:00.643	jason	save transformation 'Load Lab Result Fact'
101	3.0	2009-02-05 14:13:37.859	jason	save transformation 'Load Lab Result Fact'
102	3.0	2009-02-05 14:14:35.894	jason	save transformation 'Load Lab Result Fact'
103	3.0	2009-02-05 14:15:27.586	jason	save transformation 'Load Provider Dimension'
104	3.0	2009-02-05 14:15:53.016	jason	save transformation 'Load Patient Dimension'
105	3.0	2009-02-05 14:15:59.106	jason	save transformation 'Load Lab Result Fact'
106	3.0	2009-02-05 14:20:39.926	jason	save transformation 'Load Provider Dimension'
107	3.0	2009-02-05 14:21:15.875	jason	save transformation 'Load Provider Dimension'
108	3.0	2009-02-05 14:24:44.406	jason	save transformation 'Load Lab Result Fact'
109	3.0	2009-02-05 14:27:05.863	jason	save transformation 'Load Lab Result Fact'
110	3.0	2009-02-05 14:29:49.16	jason	save transformation 'Load Lab Result Fact'
111	3.0	2009-02-05 14:39:14.65	jason	save transformation 'Load Lab Result Fact'
112	3.0	2009-02-05 14:41:44.021	jason	save transformation 'Load Lab Result Fact'
113	3.0	2009-02-05 14:41:56.412	jason	save transformation 'Load Lab Result Fact'
114	3.0	2009-02-05 14:47:13.664	jason	save transformation 'Load Lab Result Fact'
115	3.0	2009-02-05 14:48:10.082	jason	save transformation 'Load Lab Result Fact'
116	3.0	2009-02-05 14:49:32.366	jason	save transformation 'Load Lab Result Fact'
117	3.0	2009-02-05 15:00:01.915	jason	save transformation 'Transformation 1'
118	3.0	2009-02-05 15:01:04.139	jason	save transformation 'Transformation 1'
119	3.0	2009-02-05 15:02:17.037	jason	save transformation 'Transformation 1'
120	3.0	2009-02-05 15:02:56.824	jason	save transformation 'Transformation 1'
121	3.0	2009-02-05 15:16:22.098	jason	save transformation 'Load Lab Result Fact'
122	3.0	2009-02-05 15:16:35.13	jason	save transformation 'Load Lab Result Fact'
123	3.0	2009-02-05 15:29:07.495	jason	save transformation 'Load Lab Result Fact'
124	3.0	2009-02-05 15:30:10.732	jason	save transformation 'Load Lab Result Fact'
125	3.0	2009-02-05 15:36:18.864	jason	save transformation 'Load Lab Result Fact'
126	3.0	2009-02-05 15:36:44.405	jason	save transformation 'Load Lab Result Fact'
127	3.0	2009-02-05 15:44:34.749	jason	save transformation 'Load Lab Result Fact'
128	3.0	2009-02-05 15:54:06.111	jason	save transformation 'Load Lab Result Fact'
129	3.0	2009-02-05 15:55:50.303	jason	save transformation 'Load Lab Result Fact'
130	3.0	2009-02-05 15:57:15.903	jason	save transformation 'Load Lab Result Fact'
131	3.0	2009-02-05 15:57:35.655	jason	save transformation 'Load Lab Result Fact'
132	3.0	2009-02-05 15:58:46.251	jason	save transformation 'Load Lab Result Fact'
133	3.0	2009-02-05 16:01:03.70	jason	save transformation 'Load Lab Result Fact'
134	3.0	2009-02-05 16:03:10.351	jason	save transformation 'Load Lab Result Fact'
135	3.0	2009-02-05 16:04:11.008	jason	save transformation 'Load Lab Result Fact'
136	3.0	2009-02-05 16:04:35.262	jason	save transformation 'Load Lab Result Fact'
137	3.0	2009-02-05 16:08:15.38	jason	save transformation 'Load Patient Dimension'
138	3.0	2009-02-05 16:08:23.60	jason	save transformation 'Load Provider Dimension'
139	3.0	2009-02-05 16:08:36.206	jason	save transformation 'Load Lab Result Fact'
140	3.0	2009-02-05 16:10:21.314	jason	Updating database connection 'ESP Warehouse (PostgreSQL)'
141	3.0	2009-02-05 16:10:23.285	jason	save transformation 'Load Lab Result Fact'
142	3.0	2009-02-05 16:12:11.38	jason	save transformation 'Load Lab Result Fact'
143	3.0	2009-02-05 16:12:31.523	jason	save transformation 'Load Lab Result Fact'
144	3.0	2009-02-05 16:15:08.297	jason	save transformation 'Load Lab Result Fact'
145	3.0	2009-02-05 16:35:42.842	jason	save transformation 'Load External Code to LOINC map'
146	3.0	2009-02-05 16:38:29.291	jason	save transformation 'Load External Code to LOINC map'
147	3.0	2009-02-05 16:46:08.162	jason	save transformation 'Load Lab Result Fact'
148	3.0	2009-02-09 09:50:08.008	jason	save transformation 'Load Epic Patient to Staging'
149	3.0	2009-02-09 09:53:36.94	jason	save transformation 'Load Epic Patient to Staging'
150	3.0	2009-02-09 09:54:47.306	jason	save transformation 'Load Epic Patient to Staging'
151	3.0	2009-02-09 09:56:46.386	jason	save transformation 'Load Epic Patient to Staging'
152	3.0	2009-02-09 09:58:37.604	jason	Updating database connection 'ESP'
153	3.0	2009-02-09 09:58:46.723	jason	Updating database connection 'ESP (MySQL)'
154	3.0	2009-02-09 09:59:15.365	jason	Creating new database 'ESP (PostgreSQL)'
155	3.0	2009-02-09 10:00:56.177	jason	save transformation 'Load Epic Patient to Staging'
156	3.0	2009-02-09 15:17:53.017	jason	save transformation 'Load Patient'
157	3.0	2009-02-09 15:44:25.871	jason	save transformation 'Load Patient'
158	3.0	2009-02-09 15:46:02.969	jason	save transformation 'Load Patient'
159	3.0	2009-02-09 15:46:50.764	jason	save transformation 'Load Patient'
160	3.0	2009-02-09 15:49:38.533	jason	save transformation 'Load Patient'
161	3.0	2009-02-09 15:50:03.896	jason	save transformation 'Load Patient'
162	3.0	2009-02-09 16:11:35.226	jason	save transformation 'Load Patient'
163	3.0	2009-02-09 16:13:43.567	jason	save transformation 'Load Patient'
164	3.0	2009-02-09 16:14:36.334	jason	save transformation 'Load Patient'
165	3.0	2009-02-09 16:15:15.043	jason	save transformation 'Load Patient'
166	3.0	2009-02-09 16:15:42.737	jason	save transformation 'Load Patient'
167	3.0	2009-02-09 16:18:23.679	jason	Updating database connection 'ESP (PostgreSQL)'
168	3.0	2009-02-09 16:18:59.843	jason	Updating database connection 'ESP (PostgreSQL)'
169	3.0	2009-02-09 16:29:23.432	jason	save transformation 'Add Stock Variables'
170	3.0	2009-02-09 16:29:47.851	jason	save transformation 'Add Stock Variables'
171	3.0	2009-02-09 16:29:50.191	jason	save transformation 'Load Patient'
172	3.0	2009-02-09 16:31:01.067	jason	save transformation 'Load Patient'
173	3.0	2009-02-09 16:31:56.18	jason	save transformation 'Load Patient'
174	3.0	2009-02-09 16:34:50.626	jason	save transformation 'Load Patient'
175	3.0	2009-02-09 16:36:22.997	jason	save transformation 'Add Stock Variables'
176	3.0	2009-02-09 16:37:39.777	jason	save transformation 'Add Stock Variables'
177	3.0	2009-02-09 16:38:40.772	jason	save transformation 'Add Stock Variables'
178	3.0	2009-02-09 16:40:31.125	jason	save transformation 'Add Stock Variables'
179	3.0	2009-02-09 16:41:04.626	jason	save transformation 'Load Patient'
180	3.0	2009-02-09 16:42:17.692	jason	save transformation 'Load Patient'
181	3.0	2009-02-09 16:43:13.181	jason	save transformation 'Load Patient'
182	3.0	2009-02-09 16:43:40.955	jason	save transformation 'Add Stock Variables'
183	3.0	2009-02-09 16:44:06.432	jason	save transformation 'Add Stock Variables'
184	3.0	2009-02-09 16:44:39.505	jason	save transformation 'Add Stock Variables'
185	3.0	2009-02-09 16:45:40.665	jason	save transformation 'Add Stock Variables'
186	3.0	2009-02-09 16:46:02.731	jason	save transformation 'Add Stock Variables'
187	3.0	2009-02-09 16:46:29.108	jason	save transformation 'Add Stock Variables'
188	3.0	2009-02-09 16:46:46.52	jason	save transformation 'Load Patient'
189	3.0	2009-02-09 16:48:27.593	jason	save transformation 'Load Patient'
190	3.0	2009-02-09 16:49:24.899	jason	save transformation 'Add Stock Variables'
191	3.0	2009-02-09 16:49:31.963	jason	save transformation 'Load Patient'
192	3.0	2009-02-09 16:50:30.40	jason	save transformation 'Load Patient'
193	3.0	2009-02-09 16:51:16.663	jason	save transformation 'Load Patient'
194	3.0	2009-02-09 16:51:45.197	jason	save transformation 'Load Patient'
195	3.0	2009-02-09 16:52:54.269	jason	save transformation 'Load Patient'
196	3.0	2009-02-09 16:53:33.335	jason	save transformation 'Add Stock Variables'
197	3.0	2009-02-09 16:54:10.045	jason	save transformation 'Load Patient'
198	3.0	2009-02-09 16:55:24.126	jason	save transformation 'Load Patient'
199	3.0	2009-02-09 16:55:59.925	jason	save transformation 'Load Patient'
200	3.0	2009-02-09 16:56:47.522	jason	save transformation 'Load Patient'
201	3.0	2009-02-09 16:57:49.546	jason	save transformation 'Load Patient'
202	3.0	2009-02-09 16:58:24.797	jason	save transformation 'Load Patient'
203	3.0	2009-02-09 16:59:00.191	jason	save transformation 'Load Patient'
204	3.0	2009-02-09 17:01:08.28	jason	save transformation 'Load Patient'
205	3.0	2009-02-09 17:04:48.665	jason	save transformation 'Load Patient'
206	3.0	2009-02-09 17:07:31.374	jason	save transformation 'Load Patient'
207	3.0	2009-02-10 09:37:22.564	jason	save transformation 'Add Stock Variables'
208	3.0	2009-02-10 09:44:00.36	jason	save transformation 'Load Patient'
209	3.0	2009-02-10 10:02:58.786	jason	save transformation 'Load Patient'
210	3.0	2009-02-10 10:57:48.695	jason	save transformation 'Add Stock Variables'
211	3.0	2009-02-10 10:58:17.021	jason	save transformation 'Add Stock Variables'
212	3.0	2009-02-10 10:58:55.92	jason	save transformation 'Load Patient'
213	3.0	2009-02-10 10:59:11.927	jason	save transformation 'Load Patient'
214	3.0	2009-02-10 10:59:57.804	jason	save transformation 'Add Stock Variables'
215	3.0	2009-02-10 11:00:41.878	jason	save transformation 'Add Stock Variables'
216	3.0	2009-02-10 11:01:19.768	jason	save transformation 'Add Stock Variables'
217	3.0	2009-02-10 11:01:56.575	jason	save transformation 'Load Patient'
218	3.0	2009-02-10 11:03:03.563	jason	save transformation 'Add Stock Variables'
219	3.0	2009-02-10 11:03:26.364	jason	save transformation 'Load Patient'
220	3.0	2009-02-10 11:04:08.341	jason	save transformation 'Load Patient'
221	3.0	2009-02-10 11:04:38.90	jason	save transformation 'Load Patient'
222	3.0	2009-02-10 11:05:06.726	jason	save transformation 'Load Patient'
223	3.0	2009-02-10 11:06:08.351	jason	save transformation 'Load Patient'
224	3.0	2009-02-12 16:53:19.282	jason	save transformation 'Load LOINC db'
225	3.0	2009-02-12 16:55:30.559	jason	save transformation 'Load LOINC db'
226	3.0	2009-02-17 16:57:47.428	jason	save transformation 'Load External Code to LOINC Maps'
227	3.0	2009-02-17 17:09:49.281	jason	save transformation 'Load External Code to LOINC Maps'
228	3.0	2009-02-17 17:10:32.365	jason	save transformation 'Load External Code to LOINC Maps'
229	3.0	2009-02-17 17:11:27.814	jason	save transformation 'Load External Code to LOINC Maps'
230	3.0	2009-02-17 17:21:33.655	jason	save transformation 'Load External Code to LOINC Maps'
231	3.0	2009-02-17 17:34:13.278	jason	save transformation 'Load External Code to LOINC Maps'
232	3.0	2009-02-17 17:34:24.812	jason	save transformation 'Load External Code to LOINC Maps'
233	3.0	2009-02-17 17:34:45.676	jason	save transformation 'Load External Code to LOINC Maps'
234	3.0	2009-02-17 17:37:49.404	jason	save transformation 'Load External Code to LOINC Maps'
235	3.0	2009-02-17 17:40:56.811	jason	save transformation 'Load External Code to LOINC Maps'
236	3.0	2009-02-17 17:41:55.505	jason	save transformation 'Load External Code to LOINC Maps'
237	3.0	2009-02-17 17:42:17.099	jason	save transformation 'Load External Code to LOINC Maps'
238	3.0	2009-02-17 17:47:31.657	jason	save transformation 'Load External Code to LOINC Maps'
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
10	3	Read Atrius Demographic File	\N	8	Y	1	228	72	Y
11	3	Select values	\N	15	Y	1	228	275	Y
12	3	add created date	\N	27	Y	1	392	69	Y
13	3	Insert / Update staging demog table	\N	38	Y	1	230	382	Y
14	3	Filter rows	\N	25	N	1	311	158	Y
15	3	add last update date	\N	27	Y	1	448	169	Y
16	3	use constant last update	\N	15	Y	1	416	268	Y
269	13	Add stock variables	\N	41	Y	1	136	209	N
270	13	Insert / Update	\N	38	Y	1	137	529	Y
271	13	Mapping (sub-transformation)	\N	41	Y	1	177	253	Y
272	13	Read patient files	\N	16	Y	1	114	68	Y
273	13	Select values	\N	15	Y	1	140	424	Y
8	2	Read Imm File	\N	8	Y	1	138	59	Y
9	2	Mapping (sub-transformation)	\N	41	Y	1	383	68	Y
101	10	Read Order file	\N	8	Y	1	203	90	Y
23	1	Add ID sequence	\N	20	Y	1	164	310	Y
24	1	Read North Adams code map document	\N	8	Y	1	164	40	Y
25	1	Select values	\N	15	Y	1	164	490	Y
26	1	Sort rows	\N	22	Y	1	164	130	Y
27	1	Text file output	\N	26	Y	1	164	580	Y
28	1	Unique rows	\N	29	Y	1	164	220	Y
29	1	add null cpt component	\N	18	Y	1	164	400	Y
17	6	Add ID sequence	\N	20	Y	1	200	412	Y
18	6	North Adams code map CSV	\N	8	Y	1	183	79	Y
19	6	Select values	\N	15	Y	1	201	506	Y
20	6	Sort rows	\N	22	Y	1	190	168	Y
21	6	Unique rows	\N	29	Y	1	192	281	Y
22	6	write to esp_cptloincmap	\N	21	Y	1	201	615	Y
148	11	Add ID seq	\N	20	Y	1	240	360	Y
102	10	Lookup & Update order_dim	\N	32	Y	1	360	476	Y
103	10	Add ext_emr_system	\N	18	Y	1	350	263	Y
149	11	North Adams code map CSV	\N	8	Y	1	241	55	Y
150	11	Select values	\N	15	Y	1	240	459	Y
151	11	Sort rows	\N	22	Y	1	240	160	Y
152	11	Unique rows	\N	29	Y	1	240	260	Y
153	11	ext_code_to_loinc	\N	21	Y	1	400	460	Y
154	9	Add ext_emr_system	\N	18	Y	1	80	100	Y
155	9	Lookup/update Impression	\N	34	Y	1	540	540	Y
156	9	Lookup Order	\N	32	Y	1	380	420	Y
157	9	Lookup Patient	\N	32	Y	1	240	420	Y
158	9	Lookup Provider	\N	32	Y	1	80	420	Y
159	9	Lookup/update Note	\N	34	Y	1	380	540	Y
160	9	Lookup/update Result	\N	34	Y	1	240	540	Y
161	9	Lookup/update Test	\N	34	Y	1	80	540	Y
162	9	Read Lab Result file	\N	8	Y	1	80	20	Y
163	9	Select values	\N	15	Y	1	81	731	Y
164	9	lab_result	\N	21	Y	1	241	730	Y
165	9	Lookup/update Date	\N	34	Y	1	240	220	Y
166	9	Calculate Order Date Hierarchy	\N	35	Y	1	80	220	Y
167	9	date_id --> order_date_id	\N	15	Y	1	380	220	Y
168	9	Lookup/update Date 2	\N	34	Y	1	240	320	Y
169	9	Calculate Result Date Hierarchy	\N	35	Y	1	80	320	Y
170	9	date_id --> result_date_id	\N	15	Y	1	380	320	Y
171	9	Lookup/update Medical Record	\N	34	Y	1	740	540	Y
172	12	Read Patient CSV file	\N	8	Y	1	179	60	Y
173	12	Write to EpicPatient table	\N	21	Y	1	178	330	Y
122	8	Add ext_emr_system	\N	18	Y	1	247	205	Y
123	8	Lookup/update patient dimension	\N	32	Y	1	255	375	Y
124	8	Read Patient CSV file	\N	8	Y	1	238	64	Y
125	7	Add ext_emr_system	\N	18	Y	1	210	154	Y
126	7	Discard records w/o physician code	\N	10	Y	1	416	344	Y
127	7	Lookup/update Provider dimension	\N	32	Y	1	214	453	Y
128	7	Must have physician_code	\N	25	N	1	211	295	Y
129	7	Read provider CSV file	\N	8	Y	1	206	43	Y
274	15	Read LOINCDB.txt	\N	8	Y	1	110	52	Y
275	15	Select values	\N	15	Y	1	171	253	Y
276	15	write esp_loinc	\N	21	Y	1	218	432	Y
277	16	Read North Adams LOINC Code map	\N	8	Y	1	180	80	Y
278	16	Write to esp_external_to_loinc_map	\N	21	Y	1	180	620	Y
279	16	Select values	\N	15	Y	1	180	540	Y
280	16	Lookup LOINC	\N	30	N	1	180	200	Y
281	16	LOINC number found?	\N	25	N	1	180	320	Y
282	16	Abort	\N	19	Y	1	320	320	Y
283	16	Wait for all LOINCs to pass	\N	49	Y	1	180	440	Y
264	14	Database lookup	\N	30	Y	1	485	264	Y
265	14	Get EMR name	\N	44	Y	1	483	137	Y
266	14	Get System Info	\N	27	Y	1	487	433	Y
267	14	Mapping input specification	\N	40	Y	1	227	131	Y
268	14	Mapping output specification	\N	42	Y	1	267	450	Y
\.


--
-- Data for Name: r_step_attribute; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_step_attribute (id_step_attribute, id_transformation, id_step, nr, code, value_num, value_str) FROM stdin;
9034	9	165	4	lookup_key_field	0	year
9035	9	165	5	lookup_key_name	0	quarter
9036	9	165	5	lookup_key_field	0	quarter
9037	9	165	6	lookup_key_name	0	name_day
9038	9	165	6	lookup_key_field	0	name_day
9039	9	165	7	lookup_key_name	0	name_month
9040	9	165	7	lookup_key_field	0	name_month
9041	9	165	0	return_name	0	date_id
9042	9	165	0	sequence	0	\N
9043	9	165	0	creation_method	0	tablemax
9044	9	165	0	use_autoinc	0	N
9045	9	165	0	cluster_schema	0	\N
9046	9	166	0	PARTITIONING_SCHEMA	0	\N
9047	9	166	0	PARTITIONING_METHOD	0	none
9048	9	166	0	compatible	0	Y
9049	9	166	0	jsScript_name	0	Script 1
9050	9	166	0	jsScript_script	0	// Adapted from _Building data warehouses using open source technologies_\n// by Michel Jansen <mjansen@betterbe.com>\n// http://source.pentaho.org/svnkettleroot/Kettle/trunk/docs/English/Building-data-warehouses-using-open-source-technologies.pdf\n\nvar dateTime = order_date;\n\nvar day_of_month;\nvar week_of_year;\nvar month_of_year;\nvar year;\nvar quarter;\nvar name_day;\nvar name_month;\n// Calculate!\nday_of_month = dateTime.Clone().dat2str("dd");\nweek_of_year = dateTime.Clone().Clone().dat2str("ww");\nmonth_of_year = dateTime.Clone().dat2str("MM");\nyear = dateTime.Clone().dat2str("yyyy");\nname_day = dateTime.Clone().dat2str("E").getString();\nname_month = dateTime.Clone().dat2str("MMMM").getString();\nif(month_of_year <= 3) {\n       quarter = "Q1";\n}\nelse if(month_of_year <= 6) {\n       quarter = "Q2";\n}\nelse if(month_of_year <= 9) {\n       quarter = "Q3";\n}\nelse {\n       quarter = "Q4";\n}\n
9051	9	166	0	jsScript_type	0	\N
9052	9	166	0	field_name	0	dateTime
9053	9	166	0	field_rename	0	dateTime
9054	9	166	0	field_type	0	String
9055	9	166	0	field_length	-1	\N
9056	9	166	0	field_precision	-1	\N
9057	9	166	1	field_name	0	day_of_month
9058	9	166	1	field_rename	0	day_of_month
9059	9	166	1	field_type	0	String
9060	9	166	1	field_length	-1	\N
9061	9	166	1	field_precision	-1	\N
9062	9	166	2	field_name	0	week_of_year
9063	9	166	2	field_rename	0	week_of_year
9064	9	166	2	field_type	0	String
9065	9	166	2	field_length	-1	\N
9066	9	166	2	field_precision	-1	\N
9067	9	166	3	field_name	0	month_of_year
9068	9	166	3	field_rename	0	month_of_year
9069	9	166	3	field_type	0	String
9070	9	166	3	field_length	-1	\N
9071	9	166	3	field_precision	-1	\N
9072	9	166	4	field_name	0	year
9073	9	166	4	field_rename	0	year
9074	9	166	4	field_type	0	String
9075	9	166	4	field_length	-1	\N
9076	9	166	4	field_precision	-1	\N
9077	9	166	5	field_name	0	quarter
9078	9	166	5	field_rename	0	quarter
9079	9	166	5	field_type	0	String
9080	9	166	5	field_length	-1	\N
9081	9	166	5	field_precision	-1	\N
9082	9	166	6	field_name	0	name_day
9083	9	166	6	field_rename	0	name_day
9084	9	166	6	field_type	0	String
9085	9	166	6	field_length	-1	\N
9086	9	166	6	field_precision	-1	\N
9087	9	166	7	field_name	0	name_month
9088	9	166	7	field_rename	0	name_month
9089	9	166	7	field_type	0	String
9090	9	166	7	field_length	-1	\N
9091	9	166	7	field_precision	-1	\N
9092	9	166	0	cluster_schema	0	\N
9093	9	167	0	PARTITIONING_SCHEMA	0	\N
9094	9	167	0	PARTITIONING_METHOD	0	none
9095	9	167	0	field_name	0	ext_patient_id
9096	9	167	0	field_rename	0	\N
9097	9	167	0	field_length	-2	\N
9098	9	167	0	field_precision	-2	\N
9099	9	167	1	field_name	0	medical_record_num
9100	9	167	1	field_rename	0	\N
9101	9	167	1	field_length	-2	\N
9102	9	167	1	field_precision	-2	\N
1240	6	18	4	field_trim_type	0	none
1241	6	18	5	field_name	0	LOINC Name
1242	6	18	5	field_type	0	String
1243	6	18	5	field_format	0	\N
1244	6	18	5	field_currency	0	\N
1245	6	18	5	field_decimal	0	\N
1246	6	18	5	field_group	0	\N
1247	6	18	5	field_length	92	\N
1248	6	18	5	field_precision	-1	\N
1249	6	18	5	field_trim_type	0	right
1250	6	18	0	cluster_schema	0	\N
1251	6	19	0	PARTITIONING_SCHEMA	0	\N
1252	6	19	0	PARTITIONING_METHOD	0	none
1253	6	19	0	field_name	0	LOINC
1254	6	19	0	field_rename	0	Loinc
1255	6	19	0	field_length	-1	\N
1256	6	19	0	field_precision	-1	\N
1257	6	19	1	field_name	0	id
1258	6	19	1	field_rename	0	id
1259	6	19	1	field_length	-1	\N
1260	6	19	1	field_precision	-1	\N
1261	6	19	2	field_name	0	AttrCode
1262	6	19	2	field_rename	0	CPT
1263	6	19	2	field_length	-1	\N
1264	6	19	2	field_precision	-1	\N
1265	6	19	0	select_unspecified	0	N
1266	6	19	0	cluster_schema	0	\N
1267	6	20	0	PARTITIONING_SCHEMA	0	\N
1268	6	20	0	PARTITIONING_METHOD	0	none
1269	6	20	0	directory	0	%%java.io.tmpdir%%
1270	6	20	0	prefix	0	out
1271	6	20	0	sort_size	0	\N
1272	6	20	0	free_memory	0	25
1273	6	20	0	compress	0	N
1274	6	20	0	compress_variable	0	\N
1275	6	20	0	unique_rows	0	N
1276	6	20	0	field_name	0	AttrCode
1277	6	20	0	field_ascending	0	Y
1278	6	20	0	field_case_sensitive	0	N
1279	6	20	0	cluster_schema	0	\N
1280	6	21	0	PARTITIONING_SCHEMA	0	\N
1281	6	21	0	PARTITIONING_METHOD	0	none
1282	6	21	0	count_rows	0	N
1283	6	21	0	count_fields	0	\N
1284	6	21	0	field_name	0	AttrCode
1285	6	21	0	case_insensitive	0	N
1286	6	21	0	cluster_schema	0	\N
9103	9	167	2	field_name	0	ext_order_id
9104	9	167	2	field_rename	0	\N
9105	9	167	2	field_length	-2	\N
9106	9	167	2	field_precision	-2	\N
9107	9	167	3	field_name	0	order_date
9108	9	167	3	field_rename	0	\N
9109	9	167	3	field_length	-2	\N
9110	9	167	3	field_precision	-2	\N
9111	9	167	4	field_name	0	result_date
9112	9	167	4	field_rename	0	\N
9113	9	167	4	field_length	-2	\N
9114	9	167	4	field_precision	-2	\N
9115	9	167	5	field_name	0	ext_physician_id
9116	9	167	5	field_rename	0	\N
9117	9	167	5	field_length	-2	\N
9118	9	167	5	field_precision	-2	\N
9119	9	167	6	field_name	0	order_type
9120	9	167	6	field_rename	0	\N
9121	9	167	6	field_length	-2	\N
9122	9	167	6	field_precision	-2	\N
9123	9	167	7	field_name	0	ext_test_code
9124	9	167	7	field_rename	0	\N
9125	9	167	7	field_length	-2	\N
9126	9	167	7	field_precision	-2	\N
9127	9	167	8	field_name	0	ext_test_subcode
9128	9	167	8	field_rename	0	\N
9129	9	167	8	field_length	-2	\N
9130	9	167	8	field_precision	-2	\N
9131	9	167	9	field_name	0	ext_test_name
9132	9	167	9	field_rename	0	\N
9133	9	167	9	field_length	-2	\N
9134	9	167	9	field_precision	-2	\N
9135	9	167	10	field_name	0	result
9136	9	167	10	field_rename	0	\N
9137	9	167	10	field_length	-2	\N
9138	9	167	10	field_precision	-2	\N
9139	9	167	11	field_name	0	normal_flag
9140	9	167	11	field_rename	0	\N
9141	9	167	11	field_length	-2	\N
9142	9	167	11	field_precision	-2	\N
9143	9	167	12	field_name	0	reference_low
9144	9	167	12	field_rename	0	\N
9145	9	167	12	field_length	-2	\N
9146	9	167	12	field_precision	-2	\N
9147	9	167	13	field_name	0	reference_high
9148	9	167	13	field_rename	0	\N
9149	9	167	13	field_length	-2	\N
9150	9	167	13	field_precision	-2	\N
9151	9	167	14	field_name	0	reference_units
9152	9	167	14	field_rename	0	\N
9153	9	167	14	field_length	-2	\N
9154	9	167	14	field_precision	-2	\N
1287	6	22	0	PARTITIONING_SCHEMA	0	\N
1288	6	22	0	PARTITIONING_METHOD	0	none
1289	6	22	0	id_connection	1	\N
1290	6	22	0	schema	0	\N
1291	6	22	0	table	0	esp_cptloincmap
1292	6	22	0	commit	100	\N
1293	6	22	0	truncate	0	Y
1294	6	22	0	ignore_errors	0	N
1295	6	22	0	use_batch	0	N
1296	6	22	0	partitioning_enabled	0	N
1297	6	22	0	partitioning_field	0	\N
1298	6	22	0	partitioning_daily	0	N
1299	6	22	0	partitioning_monthly	0	Y
1300	6	22	0	tablename_in_field	0	N
1301	6	22	0	tablename_field	0	\N
1302	6	22	0	tablename_in_table	0	Y
1303	6	22	0	return_keys	0	N
1304	6	22	0	return_field	0	\N
1305	6	22	0	cluster_schema	0	\N
9155	9	167	15	field_name	0	status
9156	9	167	15	field_rename	0	\N
9157	9	167	15	field_length	-2	\N
9158	9	167	15	field_precision	-2	\N
9159	9	167	16	field_name	0	notes
590	3	10	0	PARTITIONING_SCHEMA	0	\N
591	3	10	0	PARTITIONING_METHOD	0	none
592	3	10	0	filename	0	/esp/data/Atrius/incoming/epicmem.esp.${FILE_DATE}
593	3	10	0	filename_field	0	\N
594	3	10	0	rownum_field	0	\N
595	3	10	0	include_filename	0	N
596	3	10	0	separator	0	^
597	3	10	0	enclosure	0	"
598	3	10	0	buffer_size	0	50000
599	3	10	0	header	0	N
600	3	10	0	lazy_conversion	0	N
601	3	10	0	add_filename_result	0	N
602	3	10	0	parallel	0	N
603	3	10	0	encoding	0	\N
604	3	10	0	field_name	0	patient identifier
605	3	10	0	field_type	0	Number
606	3	10	0	field_format	0	\N
607	3	10	0	field_currency	0	\N
608	3	10	0	field_decimal	0	\N
609	3	10	0	field_group	0	\N
9160	9	167	16	field_rename	0	\N
9161	9	167	16	field_length	-2	\N
9162	9	167	16	field_precision	-2	\N
9163	9	167	17	field_name	0	accessnum
9164	9	167	17	field_rename	0	\N
9165	9	167	17	field_length	-2	\N
9166	9	167	17	field_precision	-2	\N
9167	9	167	18	field_name	0	impression
9168	9	167	18	field_rename	0	\N
9169	9	167	18	field_length	-2	\N
9170	9	167	18	field_precision	-2	\N
9171	9	167	19	field_name	0	ext_emr_system
9172	9	167	19	field_rename	0	\N
9173	9	167	19	field_length	-2	\N
9174	9	167	19	field_precision	-2	\N
9175	9	167	20	field_name	0	date_id
9176	9	167	20	field_rename	0	order_date_id
9177	9	167	20	field_length	-2	\N
9178	9	167	20	field_precision	-2	\N
9179	9	167	0	select_unspecified	0	N
9180	9	167	0	cluster_schema	0	\N
9181	9	168	0	PARTITIONING_SCHEMA	0	\N
9182	9	168	0	PARTITIONING_METHOD	0	none
9183	9	168	0	schema	0	\N
9184	9	168	0	table	0	date_dim
9185	9	168	0	id_connection	5	\N
9186	9	168	0	commit	100	\N
9187	9	168	0	cache_size	9999	\N
9188	9	168	0	replace	0	N
9189	9	168	0	crc	0	N
9190	9	168	0	crcfield	0	hashcode
9191	9	168	0	lookup_key_name	0	dateTime
9192	9	168	0	lookup_key_field	0	dateTime
9193	9	168	1	lookup_key_name	0	day_of_month
9194	9	168	1	lookup_key_field	0	day_of_month
9195	9	168	2	lookup_key_name	0	week_of_year
9196	9	168	2	lookup_key_field	0	week_of_year
9197	9	168	3	lookup_key_name	0	month_of_year
9198	9	168	3	lookup_key_field	0	month_of_year
9199	9	168	4	lookup_key_name	0	year
9200	9	168	4	lookup_key_field	0	year
9201	9	168	5	lookup_key_name	0	quarter
9202	9	168	5	lookup_key_field	0	quarter
9203	9	168	6	lookup_key_name	0	name_day
9204	9	168	6	lookup_key_field	0	name_day
9205	9	168	7	lookup_key_name	0	name_month
9206	9	168	7	lookup_key_field	0	name_month
9207	9	168	0	return_name	0	date_id
9208	9	168	0	sequence	0	\N
9209	9	168	0	creation_method	0	tablemax
9210	9	168	0	use_autoinc	0	N
9211	9	168	0	cluster_schema	0	\N
9212	9	169	0	PARTITIONING_SCHEMA	0	\N
9213	9	169	0	PARTITIONING_METHOD	0	none
9214	9	169	0	compatible	0	Y
9215	9	169	0	jsScript_name	0	Script 1
9406	12	172	2	field_length	-1	\N
9407	12	172	2	field_precision	-1	\N
610	3	10	0	field_length	-1	\N
611	3	10	0	field_precision	-1	\N
612	3	10	0	field_trim_type	0	none
613	3	10	1	field_name	0	medical record number
614	3	10	1	field_type	0	String
615	3	10	1	field_format	0	\N
616	3	10	1	field_currency	0	\N
617	3	10	1	field_decimal	0	\N
618	3	10	1	field_group	0	\N
619	3	10	1	field_length	-1	\N
620	3	10	1	field_precision	-1	\N
621	3	10	1	field_trim_type	0	none
622	3	10	2	field_name	0	last name
623	3	10	2	field_type	0	String
624	3	10	2	field_format	0	\N
625	3	10	2	field_currency	0	\N
626	3	10	2	field_decimal	0	\N
627	3	10	2	field_group	0	\N
628	3	10	2	field_length	-1	\N
629	3	10	2	field_precision	-1	\N
630	3	10	2	field_trim_type	0	none
631	3	10	3	field_name	0	first name
632	3	10	3	field_type	0	String
633	3	10	3	field_format	0	\N
634	3	10	3	field_currency	0	\N
635	3	10	3	field_decimal	0	\N
636	3	10	3	field_group	0	\N
637	3	10	3	field_length	-1	\N
638	3	10	3	field_precision	-1	\N
639	3	10	3	field_trim_type	0	none
640	3	10	4	field_name	0	middle initial
641	3	10	4	field_type	0	String
642	3	10	4	field_format	0	\N
643	3	10	4	field_currency	0	\N
644	3	10	4	field_decimal	0	\N
645	3	10	4	field_group	0	\N
646	3	10	4	field_length	-1	\N
647	3	10	4	field_precision	-1	\N
648	3	10	4	field_trim_type	0	none
649	3	10	5	field_name	0	address1
650	3	10	5	field_type	0	String
651	3	10	5	field_format	0	\N
652	3	10	5	field_currency	0	\N
653	3	10	5	field_decimal	0	\N
654	3	10	5	field_group	0	\N
655	3	10	5	field_length	-1	\N
656	3	10	5	field_precision	-1	\N
657	3	10	5	field_trim_type	0	none
658	3	10	6	field_name	0	address2
659	3	10	6	field_type	0	String
660	3	10	6	field_format	0	\N
661	3	10	6	field_currency	0	\N
662	3	10	6	field_decimal	0	\N
663	3	10	6	field_group	0	\N
664	3	10	6	field_length	-1	\N
665	3	10	6	field_precision	-1	\N
666	3	10	6	field_trim_type	0	none
667	3	10	7	field_name	0	city
668	3	10	7	field_type	0	String
669	3	10	7	field_format	0	\N
670	3	10	7	field_currency	0	\N
671	3	10	7	field_decimal	0	\N
672	3	10	7	field_group	0	\N
673	3	10	7	field_length	-1	\N
674	3	10	7	field_precision	-1	\N
675	3	10	7	field_trim_type	0	none
676	3	10	8	field_name	0	state
677	3	10	8	field_type	0	String
678	3	10	8	field_format	0	\N
679	3	10	8	field_currency	0	\N
680	3	10	8	field_decimal	0	\N
681	3	10	8	field_group	0	\N
682	3	10	8	field_length	-1	\N
683	3	10	8	field_precision	-1	\N
684	3	10	8	field_trim_type	0	none
685	3	10	9	field_name	0	zip
686	3	10	9	field_type	0	String
687	3	10	9	field_format	0	\N
688	3	10	9	field_currency	0	\N
689	3	10	9	field_decimal	0	\N
690	3	10	9	field_group	0	\N
691	3	10	9	field_length	-1	\N
692	3	10	9	field_precision	-1	\N
693	3	10	9	field_trim_type	0	none
694	3	10	10	field_name	0	country
695	3	10	10	field_type	0	String
696	3	10	10	field_format	0	\N
697	3	10	10	field_currency	0	\N
698	3	10	10	field_decimal	0	\N
699	3	10	10	field_group	0	\N
700	3	10	10	field_length	-1	\N
701	3	10	10	field_precision	-1	\N
702	3	10	10	field_trim_type	0	none
703	3	10	11	field_name	0	area code
704	3	10	11	field_type	0	String
705	3	10	11	field_format	0	\N
706	3	10	11	field_currency	0	\N
707	3	10	11	field_decimal	0	\N
708	3	10	11	field_group	0	\N
709	3	10	11	field_length	-1	\N
710	3	10	11	field_precision	-1	\N
711	3	10	11	field_trim_type	0	none
712	3	10	12	field_name	0	telephone
713	3	10	12	field_type	0	String
714	3	10	12	field_format	0	\N
715	3	10	12	field_currency	0	\N
716	3	10	12	field_decimal	0	\N
717	3	10	12	field_group	0	\N
718	3	10	12	field_length	-1	\N
719	3	10	12	field_precision	-1	\N
720	3	10	12	field_trim_type	0	none
721	3	10	13	field_name	0	tel extension
722	3	10	13	field_type	0	String
723	3	10	13	field_format	0	\N
724	3	10	13	field_currency	0	\N
725	3	10	13	field_decimal	0	\N
726	3	10	13	field_group	0	\N
727	3	10	13	field_length	-1	\N
728	3	10	13	field_precision	-1	\N
729	3	10	13	field_trim_type	0	none
730	3	10	14	field_name	0	date of birth
731	3	10	14	field_type	0	Number
732	3	10	14	field_format	0	\N
733	3	10	14	field_currency	0	\N
734	3	10	14	field_decimal	0	\N
735	3	10	14	field_group	0	\N
736	3	10	14	field_length	-1	\N
737	3	10	14	field_precision	-1	\N
738	3	10	14	field_trim_type	0	none
739	3	10	15	field_name	0	gender
740	3	10	15	field_type	0	String
741	3	10	15	field_format	0	\N
742	3	10	15	field_currency	0	\N
743	3	10	15	field_decimal	0	\N
744	3	10	15	field_group	0	\N
745	3	10	15	field_length	-1	\N
746	3	10	15	field_precision	-1	\N
747	3	10	15	field_trim_type	0	none
748	3	10	16	field_name	0	race
749	3	10	16	field_type	0	String
750	3	10	16	field_format	0	\N
751	3	10	16	field_currency	0	\N
752	3	10	16	field_decimal	0	\N
753	3	10	16	field_group	0	\N
754	3	10	16	field_length	-1	\N
755	3	10	16	field_precision	-1	\N
756	3	10	16	field_trim_type	0	none
757	3	10	17	field_name	0	home language
758	3	10	17	field_type	0	String
759	3	10	17	field_format	0	\N
760	3	10	17	field_currency	0	\N
761	3	10	17	field_decimal	0	\N
762	3	10	17	field_group	0	\N
763	3	10	17	field_length	-1	\N
764	3	10	17	field_precision	-1	\N
765	3	10	17	field_trim_type	0	none
766	3	10	18	field_name	0	ssn
767	3	10	18	field_type	0	String
768	3	10	18	field_format	0	\N
769	3	10	18	field_currency	0	\N
770	3	10	18	field_decimal	0	\N
771	3	10	18	field_group	0	\N
772	3	10	18	field_length	-1	\N
773	3	10	18	field_precision	-1	\N
774	3	10	18	field_trim_type	0	none
775	3	10	19	field_name	0	marital status
776	3	10	19	field_type	0	String
777	3	10	19	field_format	0	\N
778	3	10	19	field_currency	0	\N
779	3	10	19	field_decimal	0	\N
780	3	10	19	field_group	0	\N
781	3	10	19	field_length	-1	\N
782	3	10	19	field_precision	-1	\N
783	3	10	19	field_trim_type	0	none
784	3	10	20	field_name	0	religion
785	3	10	20	field_type	0	String
786	3	10	20	field_format	0	\N
787	3	10	20	field_currency	0	\N
788	3	10	20	field_decimal	0	\N
789	3	10	20	field_group	0	\N
790	3	10	20	field_length	-1	\N
791	3	10	20	field_precision	-1	\N
792	3	10	20	field_trim_type	0	none
793	3	10	21	field_name	0	aliases
794	3	10	21	field_type	0	String
795	3	10	21	field_format	0	\N
796	3	10	21	field_currency	0	\N
797	3	10	21	field_decimal	0	\N
798	3	10	21	field_group	0	\N
799	3	10	21	field_length	-1	\N
800	3	10	21	field_precision	-1	\N
801	3	10	21	field_trim_type	0	none
802	3	10	22	field_name	0	mother mrn
803	3	10	22	field_type	0	String
804	3	10	22	field_format	0	\N
805	3	10	22	field_currency	0	\N
806	3	10	22	field_decimal	0	\N
807	3	10	22	field_group	0	\N
808	3	10	22	field_length	-1	\N
809	3	10	22	field_precision	-1	\N
810	3	10	22	field_trim_type	0	none
811	3	10	23	field_name	0	death date
812	3	10	23	field_type	0	String
813	3	10	23	field_format	0	\N
814	3	10	23	field_currency	0	\N
497	2	8	0	PARTITIONING_SCHEMA	0	\N
498	2	8	0	PARTITIONING_METHOD	0	none
499	2	8	0	filename	0	/esp/data/Atrius/incoming/epicimm.esp.01022009
500	2	8	0	filename_field	0	\N
501	2	8	0	rownum_field	0	\N
502	2	8	0	include_filename	0	N
503	2	8	0	separator	0	^
504	2	8	0	enclosure	0	"
505	2	8	0	buffer_size	0	50000
506	2	8	0	header	0	Y
507	2	8	0	lazy_conversion	0	Y
508	2	8	0	add_filename_result	0	N
509	2	8	0	parallel	0	N
510	2	8	0	encoding	0	\N
511	2	8	0	field_name	0	pid
512	2	8	0	field_type	0	Number
513	2	8	0	field_format	0	\N
514	2	8	0	field_currency	0	\N
515	2	8	0	field_decimal	0	\N
516	2	8	0	field_group	0	\N
517	2	8	0	field_length	-1	\N
518	2	8	0	field_precision	-1	\N
519	2	8	0	field_trim_type	0	none
520	2	8	1	field_name	0	tp
521	2	8	1	field_type	0	Number
522	2	8	1	field_format	0	\N
523	2	8	1	field_currency	0	\N
524	2	8	1	field_decimal	0	\N
525	2	8	1	field_group	0	\N
526	2	8	1	field_length	-1	\N
527	2	8	1	field_precision	-1	\N
528	2	8	1	field_trim_type	0	none
529	2	8	2	field_name	0	name
530	2	8	2	field_type	0	String
531	2	8	2	field_format	0	\N
532	2	8	2	field_currency	0	\N
533	2	8	2	field_decimal	0	\N
534	2	8	2	field_group	0	\N
535	2	8	2	field_length	-1	\N
536	2	8	2	field_precision	-1	\N
537	2	8	2	field_trim_type	0	none
538	2	8	3	field_name	0	date
539	2	8	3	field_type	0	Number
540	2	8	3	field_format	0	\N
541	2	8	3	field_currency	0	\N
542	2	8	3	field_decimal	0	\N
543	2	8	3	field_group	0	\N
544	2	8	3	field_length	-1	\N
545	2	8	3	field_precision	-1	\N
546	2	8	3	field_trim_type	0	none
547	2	8	4	field_name	0	dose
548	2	8	4	field_type	0	String
549	2	8	4	field_format	0	\N
550	2	8	4	field_currency	0	\N
551	2	8	4	field_decimal	0	\N
552	2	8	4	field_group	0	\N
553	2	8	4	field_length	-1	\N
554	2	8	4	field_precision	-1	\N
555	2	8	4	field_trim_type	0	none
556	2	8	5	field_name	0	manufacturer
557	2	8	5	field_type	0	String
558	2	8	5	field_format	0	\N
559	2	8	5	field_currency	0	\N
560	2	8	5	field_decimal	0	\N
561	2	8	5	field_group	0	\N
562	2	8	5	field_length	-1	\N
563	2	8	5	field_precision	-1	\N
564	2	8	5	field_trim_type	0	none
565	2	8	6	field_name	0	lot
566	2	8	6	field_type	0	String
567	2	8	6	field_format	0	\N
568	2	8	6	field_currency	0	\N
569	2	8	6	field_decimal	0	\N
570	2	8	6	field_group	0	\N
571	2	8	6	field_length	-1	\N
572	2	8	6	field_precision	-1	\N
573	2	8	6	field_trim_type	0	none
574	2	8	7	field_name	0	recid
575	2	8	7	field_type	0	String
576	2	8	7	field_format	0	\N
577	2	8	7	field_currency	0	\N
578	2	8	7	field_decimal	0	\N
579	2	8	7	field_group	0	\N
580	2	8	7	field_length	-1	\N
581	2	8	7	field_precision	-1	\N
582	2	8	7	field_trim_type	0	none
583	2	8	0	cluster_schema	0	\N
584	2	9	0	PARTITIONING_SCHEMA	0	\N
585	2	9	0	PARTITIONING_METHOD	0	none
586	2	9	0	filename	0	\N
587	2	9	0	trans_name	0	Read Atrius Demographic Info
588	2	9	0	directory_path	0	/Atrius
589	2	9	0	cluster_schema	0	\N
815	3	10	23	field_decimal	0	\N
816	3	10	23	field_group	0	\N
817	3	10	23	field_length	-1	\N
818	3	10	23	field_precision	-1	\N
819	3	10	23	field_trim_type	0	none
820	3	10	24	field_name	0	provider id
821	3	10	24	field_type	0	String
822	3	10	24	field_format	0	\N
823	3	10	24	field_currency	0	\N
824	3	10	24	field_decimal	0	\N
825	3	10	24	field_group	0	\N
826	3	10	24	field_length	-1	\N
827	3	10	24	field_precision	-1	\N
828	3	10	24	field_trim_type	0	none
829	3	10	25	field_name	0	last update
830	3	10	25	field_type	0	String
831	3	10	25	field_format	0	\N
832	3	10	25	field_currency	0	\N
833	3	10	25	field_decimal	0	\N
834	3	10	25	field_group	0	\N
835	3	10	25	field_length	-1	\N
836	3	10	25	field_precision	-1	\N
837	3	10	25	field_trim_type	0	none
838	3	10	0	cluster_schema	0	\N
839	3	11	0	PARTITIONING_SCHEMA	0	\N
840	3	11	0	PARTITIONING_METHOD	0	none
841	3	11	0	field_name	0	patient identifier
842	3	11	0	field_rename	0	DemogPatient_Identifier
843	3	11	0	field_length	-1	\N
844	3	11	0	field_precision	-1	\N
845	3	11	1	field_name	0	medical record number
846	3	11	1	field_rename	0	DemogMedical_Record_Number
847	3	11	1	field_length	-1	\N
848	3	11	1	field_precision	-1	\N
849	3	11	2	field_name	0	last name
850	3	11	2	field_rename	0	DemogLast_Name
851	3	11	2	field_length	-1	\N
852	3	11	2	field_precision	-1	\N
853	3	11	3	field_name	0	first name
854	3	11	3	field_rename	0	DemogFirst_Name
855	3	11	3	field_length	-1	\N
856	3	11	3	field_precision	-1	\N
857	3	11	4	field_name	0	middle initial
858	3	11	4	field_rename	0	DemogMiddle_Initial
859	3	11	4	field_length	-1	\N
860	3	11	4	field_precision	-1	\N
861	3	11	5	field_name	0	address1
862	3	11	5	field_rename	0	DemogAddress1
863	3	11	5	field_length	-1	\N
864	3	11	5	field_precision	-1	\N
865	3	11	6	field_name	0	address2
866	3	11	6	field_rename	0	DemogAddress2
867	3	11	6	field_length	-1	\N
868	3	11	6	field_precision	-1	\N
869	3	11	7	field_name	0	city
870	3	11	7	field_rename	0	DemogCity
871	3	11	7	field_length	-1	\N
872	3	11	7	field_precision	-1	\N
873	3	11	8	field_name	0	state
874	3	11	8	field_rename	0	DemogState
875	3	11	8	field_length	-1	\N
876	3	11	8	field_precision	-1	\N
877	3	11	9	field_name	0	zip
878	3	11	9	field_rename	0	DemogZip
879	3	11	9	field_length	-1	\N
880	3	11	9	field_precision	-1	\N
881	3	11	10	field_name	0	country
882	3	11	10	field_rename	0	DemogCountry
883	3	11	10	field_length	-1	\N
884	3	11	10	field_precision	-1	\N
885	3	11	11	field_name	0	area code
886	3	11	11	field_rename	0	DemogAreaCode
887	3	11	11	field_length	-1	\N
888	3	11	11	field_precision	-1	\N
889	3	11	12	field_name	0	telephone
890	3	11	12	field_rename	0	DemogTel
891	3	11	12	field_length	-1	\N
892	3	11	12	field_precision	-1	\N
893	3	11	13	field_name	0	date of birth
894	3	11	13	field_rename	0	DemogDeath_Date
895	3	11	13	field_length	-1	\N
896	3	11	13	field_precision	-1	\N
897	3	11	14	field_name	0	gender
898	3	11	14	field_rename	0	DemogGender
899	3	11	14	field_length	-1	\N
900	3	11	14	field_precision	-1	\N
901	3	11	15	field_name	0	race
902	3	11	15	field_rename	0	DemogRace
903	3	11	15	field_length	-1	\N
904	3	11	15	field_precision	-1	\N
905	3	11	16	field_name	0	home language
906	3	11	16	field_rename	0	DemogHome_Language
907	3	11	16	field_length	-1	\N
908	3	11	16	field_precision	-1	\N
909	3	11	17	field_name	0	ssn
910	3	11	17	field_rename	0	DemogSSN
911	3	11	17	field_length	-1	\N
912	3	11	17	field_precision	-1	\N
913	3	11	18	field_name	0	marital status
914	3	11	18	field_rename	0	DemogMaritalStat
915	3	11	18	field_length	-1	\N
916	3	11	18	field_precision	-1	\N
917	3	11	19	field_name	0	religion
918	3	11	19	field_rename	0	DemogReligion
919	3	11	19	field_length	-1	\N
920	3	11	19	field_precision	-1	\N
921	3	11	20	field_name	0	aliases
922	3	11	20	field_rename	0	DemogAliases
923	3	11	20	field_length	-1	\N
924	3	11	20	field_precision	-1	\N
925	3	11	21	field_name	0	mother mrn
926	3	11	21	field_rename	0	DemogMotherMRN
927	3	11	21	field_length	-1	\N
928	3	11	21	field_precision	-1	\N
929	3	11	22	field_name	0	death date
930	3	11	22	field_rename	0	DemogDeath_Indicator
931	3	11	22	field_length	-1	\N
932	3	11	22	field_precision	-1	\N
933	3	11	23	field_name	0	provider id
934	3	11	23	field_rename	0	DemogProvider_id
935	3	11	23	field_length	-1	\N
936	3	11	23	field_precision	-1	\N
937	3	11	24	field_name	0	last update
938	3	11	24	field_rename	0	lastUpDate
939	3	11	24	field_length	-1	\N
940	3	11	24	field_precision	-1	\N
941	3	11	25	field_name	0	created date
942	3	11	25	field_rename	0	createdDate
943	3	11	25	field_length	-1	\N
944	3	11	25	field_precision	-1	\N
945	3	11	26	field_name	0	tel extension
946	3	11	26	field_rename	0	DemogExt
947	3	11	26	field_length	-1	\N
948	3	11	26	field_precision	-1	\N
949	3	11	0	select_unspecified	0	N
950	3	11	0	cluster_schema	0	\N
951	3	12	0	PARTITIONING_SCHEMA	0	\N
952	3	12	0	PARTITIONING_METHOD	0	none
953	3	12	0	field_name	0	created date
954	3	12	0	field_type	0	system date (fixed)
955	3	12	0	cluster_schema	0	\N
956	3	13	0	PARTITIONING_SCHEMA	0	\N
957	3	13	0	PARTITIONING_METHOD	0	none
958	3	13	0	id_connection	2	\N
959	3	13	0	commit	100	\N
960	3	13	0	schema	0	\N
961	3	13	0	table	0	esp_demog
962	3	13	0	update_bypassed	0	N
963	3	13	0	key_name	0	DemogPatient_Identifier
964	3	13	0	key_field	0	DemogPatient_Identifier
965	3	13	0	key_condition	0	=
966	3	13	0	key_name2	0	\N
967	3	13	0	value_name	0	DemogPatient_Identifier
968	3	13	0	value_rename	0	DemogPatient_Identifier
969	3	13	0	value_update	0	Y
970	3	13	1	value_name	0	DemogMedical_Record_Number
971	3	13	1	value_rename	0	DemogMedical_Record_Number
972	3	13	1	value_update	0	Y
973	3	13	2	value_name	0	DemogLast_Name
974	3	13	2	value_rename	0	DemogLast_Name
975	3	13	2	value_update	0	Y
976	3	13	3	value_name	0	DemogFirst_Name
977	3	13	3	value_rename	0	DemogFirst_Name
978	3	13	3	value_update	0	Y
979	3	13	4	value_name	0	DemogMiddle_Initial
980	3	13	4	value_rename	0	DemogMiddle_Initial
981	3	13	4	value_update	0	Y
982	3	13	5	value_name	0	DemogAddress1
983	3	13	5	value_rename	0	DemogAddress1
984	3	13	5	value_update	0	Y
985	3	13	6	value_name	0	DemogAddress2
986	3	13	6	value_rename	0	DemogAddress2
987	3	13	6	value_update	0	Y
988	3	13	7	value_name	0	DemogCity
989	3	13	7	value_rename	0	DemogCity
990	3	13	7	value_update	0	Y
991	3	13	8	value_name	0	DemogState
992	3	13	8	value_rename	0	DemogState
993	3	13	8	value_update	0	Y
994	3	13	9	value_name	0	DemogZip
995	3	13	9	value_rename	0	DemogZip
996	3	13	9	value_update	0	Y
997	3	13	10	value_name	0	DemogCountry
998	3	13	10	value_rename	0	DemogCountry
999	3	13	10	value_update	0	Y
1000	3	13	11	value_name	0	DemogAreaCode
1001	3	13	11	value_rename	0	DemogAreaCode
1002	3	13	11	value_update	0	Y
1003	3	13	12	value_name	0	DemogTel
1004	3	13	12	value_rename	0	DemogTel
1005	3	13	12	value_update	0	Y
1006	3	13	13	value_name	0	DemogDeath_Date
1007	3	13	13	value_rename	0	DemogDeath_Date
1008	3	13	13	value_update	0	Y
1009	3	13	14	value_name	0	DemogGender
1010	3	13	14	value_rename	0	DemogGender
1011	3	13	14	value_update	0	Y
1012	3	13	15	value_name	0	DemogRace
1013	3	13	15	value_rename	0	DemogRace
1014	3	13	15	value_update	0	Y
1015	3	13	16	value_name	0	DemogHome_Language
1016	3	13	16	value_rename	0	DemogHome_Language
1017	3	13	16	value_update	0	Y
1018	3	13	17	value_name	0	DemogSSN
1019	3	13	17	value_rename	0	DemogSSN
1020	3	13	17	value_update	0	Y
1021	3	13	18	value_name	0	DemogMaritalStat
1022	3	13	18	value_rename	0	DemogMaritalStat
1023	3	13	18	value_update	0	Y
1024	3	13	19	value_name	0	DemogReligion
1025	3	13	19	value_rename	0	DemogReligion
1026	3	13	19	value_update	0	Y
1027	3	13	20	value_name	0	DemogAliases
1028	3	13	20	value_rename	0	DemogAliases
1029	3	13	20	value_update	0	Y
1030	3	13	21	value_name	0	DemogMotherMRN
1031	3	13	21	value_rename	0	DemogMotherMRN
1032	3	13	21	value_update	0	Y
1033	3	13	22	value_name	0	DemogDeath_Indicator
1034	3	13	22	value_rename	0	DemogDeath_Indicator
1035	3	13	22	value_update	0	Y
1036	3	13	23	value_name	0	DemogProvider_id
1037	3	13	23	value_rename	0	DemogProvider_id
1038	3	13	23	value_update	0	Y
1039	3	13	24	value_name	0	lastUpDate
1040	3	13	24	value_rename	0	lastUpDate
1041	3	13	24	value_update	0	Y
1042	3	13	25	value_name	0	DemogExt
1043	3	13	25	value_rename	0	DemogExt
1044	3	13	25	value_update	0	Y
1045	3	13	0	cluster_schema	0	\N
1046	3	14	0	PARTITIONING_SCHEMA	0	\N
1047	3	14	0	PARTITIONING_METHOD	0	none
1048	3	14	0	id_condition	1	\N
1049	3	14	0	send_true_to	0	Select values
1050	3	14	0	send_false_to	0	add last update date
1051	3	14	0	cluster_schema	0	\N
1052	3	15	0	PARTITIONING_SCHEMA	0	\N
1053	3	15	0	PARTITIONING_METHOD	0	none
1054	3	15	0	field_name	0	last update constant
1055	3	15	0	field_type	0	system date (fixed)
1056	3	15	0	cluster_schema	0	\N
1057	3	16	0	PARTITIONING_SCHEMA	0	\N
1058	3	16	0	PARTITIONING_METHOD	0	none
1059	3	16	0	field_name	0	patient identifier
1060	3	16	0	field_rename	0	\N
1061	3	16	0	field_length	-2	\N
1062	3	16	0	field_precision	-2	\N
1063	3	16	1	field_name	0	medical record number
1064	3	16	1	field_rename	0	\N
1065	3	16	1	field_length	-2	\N
1066	3	16	1	field_precision	-2	\N
1067	3	16	2	field_name	0	last name
1068	3	16	2	field_rename	0	\N
1069	3	16	2	field_length	-2	\N
1070	3	16	2	field_precision	-2	\N
1071	3	16	3	field_name	0	first name
1072	3	16	3	field_rename	0	\N
1073	3	16	3	field_length	-2	\N
1074	3	16	3	field_precision	-2	\N
1075	3	16	4	field_name	0	middle initial
1076	3	16	4	field_rename	0	\N
1077	3	16	4	field_length	-2	\N
1078	3	16	4	field_precision	-2	\N
1079	3	16	5	field_name	0	address1
1080	3	16	5	field_rename	0	\N
1081	3	16	5	field_length	-2	\N
1082	3	16	5	field_precision	-2	\N
1083	3	16	6	field_name	0	address2
1084	3	16	6	field_rename	0	\N
1085	3	16	6	field_length	-2	\N
1086	3	16	6	field_precision	-2	\N
1087	3	16	7	field_name	0	city
1088	3	16	7	field_rename	0	\N
1089	3	16	7	field_length	-2	\N
1090	3	16	7	field_precision	-2	\N
1091	3	16	8	field_name	0	state
1092	3	16	8	field_rename	0	\N
1093	3	16	8	field_length	-2	\N
1094	3	16	8	field_precision	-2	\N
1095	3	16	9	field_name	0	zip
1096	3	16	9	field_rename	0	\N
1097	3	16	9	field_length	-2	\N
1098	3	16	9	field_precision	-2	\N
1099	3	16	10	field_name	0	country
1100	3	16	10	field_rename	0	\N
1101	3	16	10	field_length	-2	\N
1102	3	16	10	field_precision	-2	\N
1103	3	16	11	field_name	0	area code
1104	3	16	11	field_rename	0	\N
1105	3	16	11	field_length	-2	\N
1106	3	16	11	field_precision	-2	\N
1107	3	16	12	field_name	0	telephone
1108	3	16	12	field_rename	0	\N
1109	3	16	12	field_length	-2	\N
1110	3	16	12	field_precision	-2	\N
1111	3	16	13	field_name	0	tel extension
1112	3	16	13	field_rename	0	\N
1113	3	16	13	field_length	-2	\N
1114	3	16	13	field_precision	-2	\N
1115	3	16	14	field_name	0	date of birth
1116	3	16	14	field_rename	0	\N
1117	3	16	14	field_length	-2	\N
1118	3	16	14	field_precision	-2	\N
1119	3	16	15	field_name	0	gender
1120	3	16	15	field_rename	0	\N
1121	3	16	15	field_length	-2	\N
1122	3	16	15	field_precision	-2	\N
1123	3	16	16	field_name	0	race
1124	3	16	16	field_rename	0	\N
1125	3	16	16	field_length	-2	\N
1126	3	16	16	field_precision	-2	\N
1127	3	16	17	field_name	0	home language
1128	3	16	17	field_rename	0	\N
1129	3	16	17	field_length	-2	\N
1130	3	16	17	field_precision	-2	\N
1131	3	16	18	field_name	0	ssn
1132	3	16	18	field_rename	0	\N
1133	3	16	18	field_length	-2	\N
1134	3	16	18	field_precision	-2	\N
1135	3	16	19	field_name	0	marital status
1136	3	16	19	field_rename	0	\N
1137	3	16	19	field_length	-2	\N
1138	3	16	19	field_precision	-2	\N
1139	3	16	20	field_name	0	religion
1140	3	16	20	field_rename	0	\N
1141	3	16	20	field_length	-2	\N
1142	3	16	20	field_precision	-2	\N
1143	3	16	21	field_name	0	aliases
1144	3	16	21	field_rename	0	\N
1145	3	16	21	field_length	-2	\N
1146	3	16	21	field_precision	-2	\N
1147	3	16	22	field_name	0	mother mrn
1148	3	16	22	field_rename	0	\N
1149	3	16	22	field_length	-2	\N
1150	3	16	22	field_precision	-2	\N
1151	3	16	23	field_name	0	death date
1152	3	16	23	field_rename	0	\N
1153	3	16	23	field_length	-2	\N
1154	3	16	23	field_precision	-2	\N
1155	3	16	24	field_name	0	provider id
1156	3	16	24	field_rename	0	\N
1157	3	16	24	field_length	-2	\N
1158	3	16	24	field_precision	-2	\N
1159	3	16	25	field_name	0	created date
1160	3	16	25	field_rename	0	\N
1161	3	16	25	field_length	-2	\N
1162	3	16	25	field_precision	-2	\N
1163	3	16	26	field_name	0	last update constant
1164	3	16	26	field_rename	0	last update
1165	3	16	26	field_length	-2	\N
1166	3	16	26	field_precision	-2	\N
1167	3	16	0	select_unspecified	0	N
1168	3	16	0	cluster_schema	0	\N
9216	9	169	0	jsScript_script	0	// Adapted from _Building data warehouses using open source technologies_\n// by Michel Jansen <mjansen@betterbe.com>\n// http://source.pentaho.org/svnkettleroot/Kettle/trunk/docs/English/Building-data-warehouses-using-open-source-technologies.pdf\n\nvar dateTime = result_date;\n\nvar day_of_month;\nvar week_of_year;\nvar month_of_year;\nvar year;\nvar quarter;\nvar name_day;\nvar name_month;\n// Calculate!\nday_of_month = dateTime.Clone().dat2str("dd");\nweek_of_year = dateTime.Clone().Clone().dat2str("ww");\nmonth_of_year = dateTime.Clone().dat2str("MM");\nyear = dateTime.Clone().dat2str("yyyy");\nname_day = dateTime.Clone().dat2str("E").getString();\nname_month = dateTime.Clone().dat2str("MMMM").getString();\nif(month_of_year <= 3) {\n       quarter = "Q1";\n}\nelse if(month_of_year <= 6) {\n       quarter = "Q2";\n}\nelse if(month_of_year <= 9) {\n       quarter = "Q3";\n}\nelse {\n       quarter = "Q4";\n}\n
9217	9	169	0	jsScript_type	0	\N
1438	1	27	0	file_add_partnr	0	N
1439	1	27	0	file_add_date	0	N
1440	1	27	0	date_time_format	0	\N
1441	1	27	0	SpecifyFormat	0	N
1442	1	27	0	add_to_result_filenames	0	Y
1443	1	27	0	file_add_time	0	N
1444	1	27	0	file_pad	0	N
1445	1	27	0	file_fast_dump	0	N
1446	1	27	0	fileNameInField	0	N
1447	1	27	0	fileNameField	0	\N
1448	1	27	0	field_name	0	id
1449	1	27	0	field_type	0	Integer
1450	1	27	0	field_format	0	\N
1451	1	27	0	field_currency	0	\N
1452	1	27	0	field_decimal	0	\N
1453	1	27	0	field_group	0	\N
1454	1	27	0	field_trim_type	0	none
1455	1	27	0	field_nullif	0	\N
1456	1	27	0	field_length	-1	\N
1457	1	27	0	field_precision	0	\N
1458	1	27	1	field_name	0	CPT
1459	1	27	1	field_type	0	String
1460	1	27	1	field_format	0	\N
1461	1	27	1	field_currency	0	\N
1462	1	27	1	field_decimal	0	\N
1463	1	27	1	field_group	0	\N
1464	1	27	1	field_trim_type	0	none
1465	1	27	1	field_nullif	0	\N
1466	1	27	1	field_length	-1	\N
1467	1	27	1	field_precision	-1	\N
1468	1	27	2	field_name	0	cpt component
1469	1	27	2	field_type	0	String
1470	1	27	2	field_format	0	\N
1471	1	27	2	field_currency	0	\N
1472	1	27	2	field_decimal	0	\N
1473	1	27	2	field_group	0	\N
1474	1	27	2	field_trim_type	0	none
1475	1	27	2	field_nullif	0	\N
1476	1	27	2	field_length	-1	\N
1477	1	27	2	field_precision	-1	\N
1478	1	27	3	field_name	0	Loinc
1479	1	27	3	field_type	0	String
1480	1	27	3	field_format	0	\N
1481	1	27	3	field_currency	0	\N
1482	1	27	3	field_decimal	0	\N
1483	1	27	3	field_group	0	\N
1484	1	27	3	field_trim_type	0	none
1485	1	27	3	field_nullif	0	\N
1486	1	27	3	field_length	-1	\N
1487	1	27	3	field_precision	-1	\N
1488	1	27	0	endedLine	0	\N
1489	1	27	0	cluster_schema	0	\N
1490	1	28	0	PARTITIONING_SCHEMA	0	\N
1491	1	28	0	PARTITIONING_METHOD	0	none
1492	1	28	0	count_rows	0	N
1493	1	28	0	count_fields	0	\N
1494	1	28	0	field_name	0	AttrCode
1495	1	28	0	case_insensitive	0	N
1496	1	28	0	cluster_schema	0	\N
1497	1	29	0	PARTITIONING_SCHEMA	0	\N
1498	1	29	0	PARTITIONING_METHOD	0	none
1499	1	29	0	field_name	0	cpt component
1500	1	29	0	field_type	0	String
1501	1	29	0	field_format	0	\N
1502	1	29	0	field_currency	0	\N
1503	1	29	0	field_decimal	0	\N
1504	1	29	0	field_group	0	\N
1505	1	29	0	field_nullif	0	\N
1506	1	29	0	field_length	-1	\N
1507	1	29	0	field_precision	-1	\N
1508	1	29	0	cluster_schema	0	\N
9408	12	172	2	field_trim_type	0	none
9409	12	172	3	field_name	0	first_name
9410	12	172	3	field_type	0	String
9411	12	172	3	field_format	0	\N
9412	12	172	3	field_currency	0	\N
9413	12	172	3	field_decimal	0	\N
9414	12	172	3	field_group	0	\N
9415	12	172	3	field_length	-1	\N
9416	12	172	3	field_precision	-1	\N
9417	12	172	3	field_trim_type	0	none
9418	12	172	4	field_name	0	middle_name
9419	12	172	4	field_type	0	String
9420	12	172	4	field_format	0	\N
9421	12	172	4	field_currency	0	\N
9422	12	172	4	field_decimal	0	\N
9423	12	172	4	field_group	0	\N
9424	12	172	4	field_length	-1	\N
9425	12	172	4	field_precision	-1	\N
9426	12	172	4	field_trim_type	0	none
9427	12	172	5	field_name	0	address_1
9428	12	172	5	field_type	0	String
9429	12	172	5	field_format	0	\N
9430	12	172	5	field_currency	0	\N
9431	12	172	5	field_decimal	0	\N
9432	12	172	5	field_group	0	\N
9433	12	172	5	field_length	-1	\N
9434	12	172	5	field_precision	-1	\N
9435	12	172	5	field_trim_type	0	none
9436	12	172	6	field_name	0	address_2
9437	12	172	6	field_type	0	String
9438	12	172	6	field_format	0	\N
9439	12	172	6	field_currency	0	\N
9440	12	172	6	field_decimal	0	\N
9441	12	172	6	field_group	0	\N
9442	12	172	6	field_length	-1	\N
9443	12	172	6	field_precision	-1	\N
9444	12	172	6	field_trim_type	0	none
9445	12	172	7	field_name	0	city
9446	12	172	7	field_type	0	String
9447	12	172	7	field_format	0	\N
9448	12	172	7	field_currency	0	\N
9449	12	172	7	field_decimal	0	\N
9450	12	172	7	field_group	0	\N
9451	12	172	7	field_length	-1	\N
9452	12	172	7	field_precision	-1	\N
9453	12	172	7	field_trim_type	0	none
9454	12	172	8	field_name	0	state
9455	12	172	8	field_type	0	String
9456	12	172	8	field_format	0	\N
9457	12	172	8	field_currency	0	\N
9458	12	172	8	field_decimal	0	\N
9459	12	172	8	field_group	0	\N
9460	12	172	8	field_length	-1	\N
9461	12	172	8	field_precision	-1	\N
9462	12	172	8	field_trim_type	0	none
9463	12	172	9	field_name	0	zip
9464	12	172	9	field_type	0	String
9465	12	172	9	field_format	0	\N
9466	12	172	9	field_currency	0	\N
9467	12	172	9	field_decimal	0	\N
9468	12	172	9	field_group	0	\N
9469	12	172	9	field_length	-1	\N
9470	12	172	9	field_precision	-1	\N
9471	12	172	9	field_trim_type	0	none
9472	12	172	10	field_name	0	country
9473	12	172	10	field_type	0	String
9474	12	172	10	field_format	0	\N
9475	12	172	10	field_currency	0	\N
7131	8	122	0	PARTITIONING_SCHEMA	0	\N
7132	8	122	0	PARTITIONING_METHOD	0	none
7133	8	122	0	field_name	0	ext_emr_system
7134	8	122	0	field_type	0	String
7135	8	122	0	field_format	0	\N
7136	8	122	0	field_currency	0	\N
7137	8	122	0	field_decimal	0	\N
7138	8	122	0	field_group	0	\N
7139	8	122	0	field_nullif	0	North Adams
7140	8	122	0	field_length	-1	\N
7141	8	122	0	field_precision	-1	\N
7142	8	122	0	cluster_schema	0	\N
7143	8	123	0	PARTITIONING_SCHEMA	0	\N
7144	8	123	0	PARTITIONING_METHOD	0	none
7145	8	123	0	schema	0	\N
7146	8	123	0	table	0	patient_dim
7147	8	123	0	id_connection	5	\N
7148	8	123	0	commit	100	\N
7149	8	123	0	update	0	Y
7150	8	123	0	lookup_key_name	0	ext_patient_id
7151	8	123	0	lookup_key_field	0	ext_patient_id
7152	8	123	1	lookup_key_name	0	ext_emr_system
7153	8	123	1	lookup_key_field	0	ext_emr_system
7154	8	123	0	date_name	0	\N
7155	8	123	0	date_from	0	date_from
7156	8	123	0	date_to	0	date_to
7157	8	123	0	field_name	0	medical_record_num
7158	8	123	0	field_lookup	0	medical_record_num
7159	8	123	0	field_update	0	Insert
7160	8	123	1	field_name	0	last_name
7161	8	123	1	field_lookup	0	last_name
7162	8	123	1	field_update	0	Insert
7163	8	123	2	field_name	0	first_name
7164	8	123	2	field_lookup	0	first_name
1306	1	23	0	PARTITIONING_SCHEMA	0	\N
1307	1	23	0	PARTITIONING_METHOD	0	none
1308	1	23	0	valuename	0	id
1309	1	23	0	use_database	0	N
1310	1	23	0	id_connection	1	\N
1311	1	23	0	schema	0	\N
1312	1	23	0	seqname	0	SEQ_
1313	1	23	0	use_counter	0	Y
1314	1	23	0	counter_name	0	\N
1315	1	23	0	start_at	0	1
1316	1	23	0	increment_by	0	1
1317	1	23	0	max_value	0	999999999
1318	1	23	0	cluster_schema	0	\N
1319	1	24	0	PARTITIONING_SCHEMA	0	\N
1320	1	24	0	PARTITIONING_METHOD	0	none
1321	1	24	0	filename	0	/home/rejmv/work/esp/NORTH_ADAMS/NorthAdamsLocal-LOINCmapMay2008.redacted.xls
1322	1	24	0	filename_field	0	\N
1323	1	24	0	rownum_field	0	\N
1324	1	24	0	include_filename	0	N
1325	1	24	0	separator	0	\t
1326	1	24	0	enclosure	0	"
1327	1	24	0	buffer_size	0	50000
1328	1	24	0	header	0	Y
1329	1	24	0	lazy_conversion	0	Y
1330	1	24	0	add_filename_result	0	N
1331	1	24	0	parallel	0	N
1332	1	24	0	encoding	0	\N
1333	1	24	0	field_name	0	Dept
1334	1	24	0	field_type	0	String
1335	1	24	0	field_format	0	\N
1336	1	24	0	field_currency	0	\N
1337	1	24	0	field_decimal	0	\N
1338	1	24	0	field_group	0	\N
1169	6	17	0	PARTITIONING_SCHEMA	0	\N
1170	6	17	0	PARTITIONING_METHOD	0	none
1171	6	17	0	valuename	0	id
1172	6	17	0	use_database	0	N
1173	6	17	0	id_connection	1	\N
1174	6	17	0	schema	0	\N
1175	6	17	0	seqname	0	SEQ_
1176	6	17	0	use_counter	0	Y
1177	6	17	0	counter_name	0	\N
1178	6	17	0	start_at	0	1
1179	6	17	0	increment_by	0	1
1180	6	17	0	max_value	0	999999999
1181	6	17	0	cluster_schema	0	\N
1182	6	18	0	PARTITIONING_SCHEMA	0	\N
1183	6	18	0	PARTITIONING_METHOD	0	none
1184	6	18	0	filename	0	/home/rejmv/work/esp/NORTH_ADAMS/NorthAdamsLocal-LOINCmapMay2008.redacted.xls
1185	6	18	0	filename_field	0	\N
1186	6	18	0	rownum_field	0	\N
1187	6	18	0	include_filename	0	N
1188	6	18	0	separator	0	\t
1189	6	18	0	enclosure	0	"
1190	6	18	0	buffer_size	0	50000
1191	6	18	0	header	0	Y
1192	6	18	0	lazy_conversion	0	Y
1193	6	18	0	add_filename_result	0	N
1194	6	18	0	parallel	0	N
1195	6	18	0	encoding	0	\N
1196	6	18	0	field_name	0	Dept
1197	6	18	0	field_type	0	String
1198	6	18	0	field_format	0	\N
1199	6	18	0	field_currency	0	\N
1200	6	18	0	field_decimal	0	\N
1201	6	18	0	field_group	0	\N
1202	6	18	0	field_length	5	\N
1203	6	18	0	field_precision	-1	\N
1204	6	18	0	field_trim_type	0	none
1205	6	18	1	field_name	0	AttrCode
1206	6	18	1	field_type	0	String
1207	6	18	1	field_format	0	\N
1208	6	18	1	field_currency	0	\N
1209	6	18	1	field_decimal	0	\N
1210	6	18	1	field_group	0	\N
1211	6	18	1	field_length	9	\N
1212	6	18	1	field_precision	-1	\N
1213	6	18	1	field_trim_type	0	none
1214	6	18	2	field_name	0	AttrMnemonic
1215	6	18	2	field_type	0	String
1216	6	18	2	field_format	0	\N
1217	6	18	2	field_currency	0	\N
1218	6	18	2	field_decimal	0	\N
1219	6	18	2	field_group	0	\N
1220	6	18	2	field_length	14	\N
1221	6	18	2	field_precision	-1	\N
1222	6	18	2	field_trim_type	0	none
1223	6	18	3	field_name	0	AttrName
1224	6	18	3	field_type	0	String
1225	6	18	3	field_format	0	\N
1226	6	18	3	field_currency	0	\N
1227	6	18	3	field_decimal	0	\N
1228	6	18	3	field_group	0	\N
1229	6	18	3	field_length	32	\N
1230	6	18	3	field_precision	-1	\N
1231	6	18	3	field_trim_type	0	right
1232	6	18	4	field_name	0	LOINC
1233	6	18	4	field_type	0	String
1234	6	18	4	field_format	0	\N
1235	6	18	4	field_currency	0	\N
1236	6	18	4	field_decimal	0	\N
1237	6	18	4	field_group	0	\N
1238	6	18	4	field_length	77	\N
1239	6	18	4	field_precision	-1	\N
1339	1	24	0	field_length	5	\N
1340	1	24	0	field_precision	-1	\N
1341	1	24	0	field_trim_type	0	none
1342	1	24	1	field_name	0	AttrCode
1343	1	24	1	field_type	0	String
1344	1	24	1	field_format	0	\N
1345	1	24	1	field_currency	0	\N
1346	1	24	1	field_decimal	0	\N
1347	1	24	1	field_group	0	\N
1348	1	24	1	field_length	9	\N
1349	1	24	1	field_precision	-1	\N
1350	1	24	1	field_trim_type	0	none
1351	1	24	2	field_name	0	AttrMnemonic
1352	1	24	2	field_type	0	String
1353	1	24	2	field_format	0	\N
1354	1	24	2	field_currency	0	\N
1355	1	24	2	field_decimal	0	\N
1356	1	24	2	field_group	0	\N
1357	1	24	2	field_length	14	\N
1358	1	24	2	field_precision	-1	\N
1359	1	24	2	field_trim_type	0	none
1360	1	24	3	field_name	0	AttrName
1361	1	24	3	field_type	0	String
1362	1	24	3	field_format	0	\N
1363	1	24	3	field_currency	0	\N
1364	1	24	3	field_decimal	0	\N
1365	1	24	3	field_group	0	\N
1366	1	24	3	field_length	32	\N
1367	1	24	3	field_precision	-1	\N
1368	1	24	3	field_trim_type	0	right
1369	1	24	4	field_name	0	LOINC
1370	1	24	4	field_type	0	String
1371	1	24	4	field_format	0	\N
1372	1	24	4	field_currency	0	\N
1373	1	24	4	field_decimal	0	\N
1374	1	24	4	field_group	0	\N
1375	1	24	4	field_length	77	\N
1376	1	24	4	field_precision	-1	\N
1377	1	24	4	field_trim_type	0	none
1378	1	24	5	field_name	0	LOINC Name
1379	1	24	5	field_type	0	String
1380	1	24	5	field_format	0	\N
1381	1	24	5	field_currency	0	\N
1382	1	24	5	field_decimal	0	\N
1383	1	24	5	field_group	0	\N
1384	1	24	5	field_length	92	\N
1385	1	24	5	field_precision	-1	\N
1386	1	24	5	field_trim_type	0	right
1387	1	24	0	cluster_schema	0	\N
1388	1	25	0	PARTITIONING_SCHEMA	0	\N
1389	1	25	0	PARTITIONING_METHOD	0	none
1390	1	25	0	field_name	0	LOINC
1391	1	25	0	field_rename	0	Loinc
1392	1	25	0	field_length	-1	\N
1393	1	25	0	field_precision	-1	\N
1394	1	25	1	field_name	0	id
1395	1	25	1	field_rename	0	\N
1396	1	25	1	field_length	-1	\N
1397	1	25	1	field_precision	-1	\N
1398	1	25	2	field_name	0	AttrCode
1399	1	25	2	field_rename	0	CPT
1400	1	25	2	field_length	-1	\N
1401	1	25	2	field_precision	-1	\N
1402	1	25	3	field_name	0	cpt component
1403	1	25	3	field_rename	0	\N
1404	1	25	3	field_length	-2	\N
1405	1	25	3	field_precision	-2	\N
1406	1	25	0	select_unspecified	0	N
1407	1	25	0	cluster_schema	0	\N
1408	1	26	0	PARTITIONING_SCHEMA	0	\N
1409	1	26	0	PARTITIONING_METHOD	0	none
1410	1	26	0	directory	0	%%java.io.tmpdir%%
1411	1	26	0	prefix	0	out
1412	1	26	0	sort_size	0	\N
1413	1	26	0	free_memory	0	25
1414	1	26	0	compress	0	N
1415	1	26	0	compress_variable	0	\N
1416	1	26	0	unique_rows	0	N
1417	1	26	0	field_name	0	AttrCode
1418	1	26	0	field_ascending	0	Y
1419	1	26	0	field_case_sensitive	0	N
1420	1	26	0	cluster_schema	0	\N
1421	1	27	0	PARTITIONING_SCHEMA	0	\N
1422	1	27	0	PARTITIONING_METHOD	0	none
1423	1	27	0	separator	0	\t
1424	1	27	0	enclosure	0	"
1425	1	27	0	enclosure_forced	0	N
1426	1	27	0	header	0	N
1427	1	27	0	footer	0	N
1428	1	27	0	format	0	Unix
1429	1	27	0	compression	0	None
1430	1	27	0	encoding	0	UTF-8
1431	1	27	0	file_name	0	/home/rejmv/work/esp/NORTH_ADAMS/preLoaderData/esp_cptloincmap
1432	1	27	0	file_is_command	0	N
1433	1	27	0	do_not_open_new_file_init	0	N
1434	1	27	0	file_extention	0	txt
1435	1	27	0	file_append	0	N
1436	1	27	0	file_split	0	\N
1437	1	27	0	file_add_stepnr	0	N
9476	12	172	10	field_decimal	0	\N
9477	12	172	10	field_group	0	\N
9478	12	172	10	field_length	-1	\N
9479	12	172	10	field_precision	-1	\N
9480	12	172	10	field_trim_type	0	none
9481	12	172	11	field_name	0	telephone
9482	12	172	11	field_type	0	String
9483	12	172	11	field_format	0	\N
9484	12	172	11	field_currency	0	\N
9485	12	172	11	field_decimal	0	\N
9486	12	172	11	field_group	0	\N
9487	12	172	11	field_length	-1	\N
9488	12	172	11	field_precision	-1	\N
9489	12	172	11	field_trim_type	0	none
9490	12	172	12	field_name	0	tel_ext
9491	12	172	12	field_type	0	String
9492	12	172	12	field_format	0	\N
9493	12	172	12	field_currency	0	\N
9494	12	172	12	field_decimal	0	\N
9495	12	172	12	field_group	0	\N
9496	12	172	12	field_length	-1	\N
9497	12	172	12	field_precision	-1	\N
9498	12	172	12	field_trim_type	0	none
9499	12	172	13	field_name	0	dob
9500	12	172	13	field_type	0	Date
9501	12	172	13	field_format	0	\N
9502	12	172	13	field_currency	0	\N
9503	12	172	13	field_decimal	0	\N
9504	12	172	13	field_group	0	\N
9505	12	172	13	field_length	-1	\N
9506	12	172	13	field_precision	-1	\N
9507	12	172	13	field_trim_type	0	none
9508	12	172	14	field_name	0	gender
9509	12	172	14	field_type	0	String
9510	12	172	14	field_format	0	\N
9511	12	172	14	field_currency	0	\N
9512	12	172	14	field_decimal	0	\N
9513	12	172	14	field_group	0	\N
9514	12	172	14	field_length	-1	\N
9515	12	172	14	field_precision	-1	\N
9516	12	172	14	field_trim_type	0	none
9517	12	172	15	field_name	0	race
9518	12	172	15	field_type	0	String
9519	12	172	15	field_format	0	\N
9520	12	172	15	field_currency	0	\N
9521	12	172	15	field_decimal	0	\N
9522	12	172	15	field_group	0	\N
9523	12	172	15	field_length	-1	\N
9524	12	172	15	field_precision	-1	\N
9525	12	172	15	field_trim_type	0	none
9526	12	172	16	field_name	0	lang
9527	12	172	16	field_type	0	String
9528	12	172	16	field_format	0	\N
9529	12	172	16	field_currency	0	\N
9530	12	172	16	field_decimal	0	\N
9531	12	172	16	field_group	0	\N
9532	12	172	16	field_length	-1	\N
9533	12	172	16	field_precision	-1	\N
9534	12	172	16	field_trim_type	0	none
9535	12	172	17	field_name	0	ssn
9536	12	172	17	field_type	0	String
9537	12	172	17	field_format	0	\N
9538	12	172	17	field_currency	0	\N
9539	12	172	17	field_decimal	0	\N
9540	12	172	17	field_group	0	\N
9541	12	172	17	field_length	-1	\N
9542	12	172	17	field_precision	-1	\N
9543	12	172	17	field_trim_type	0	none
9544	12	172	18	field_name	0	phy
9545	12	172	18	field_type	0	String
9546	12	172	18	field_format	0	\N
9547	12	172	18	field_currency	0	\N
9548	12	172	18	field_decimal	0	\N
9549	12	172	18	field_group	0	\N
9550	12	172	18	field_length	-1	\N
9551	12	172	18	field_precision	-1	\N
9552	12	172	18	field_trim_type	0	none
9553	12	172	19	field_name	0	marital_status
9554	12	172	19	field_type	0	String
9555	12	172	19	field_format	0	\N
9556	12	172	19	field_currency	0	\N
9557	12	172	19	field_decimal	0	\N
9558	12	172	19	field_group	0	\N
9559	12	172	19	field_length	-1	\N
7165	8	123	2	field_update	0	Insert
7166	8	123	3	field_name	0	middle_name
9560	12	172	19	field_precision	-1	\N
9561	12	172	19	field_trim_type	0	none
9562	12	172	20	field_name	0	religion
9563	12	172	20	field_type	0	String
9564	12	172	20	field_format	0	\N
9565	12	172	20	field_currency	0	\N
9566	12	172	20	field_decimal	0	\N
9567	12	172	20	field_group	0	\N
9568	12	172	20	field_length	-1	\N
9569	12	172	20	field_precision	-1	\N
9570	12	172	20	field_trim_type	0	none
9571	12	172	21	field_name	0	mom
9572	12	172	21	field_type	0	String
9573	12	172	21	field_format	0	\N
9574	12	172	21	field_currency	0	\N
9575	12	172	21	field_decimal	0	\N
9576	12	172	21	field_group	0	\N
9577	12	172	21	field_length	-1	\N
9578	12	172	21	field_precision	-1	\N
9579	12	172	21	field_trim_type	0	none
7167	8	123	3	field_lookup	0	middle_name
7168	8	123	3	field_update	0	Insert
7169	8	123	4	field_name	0	address_1
7170	8	123	4	field_lookup	0	address_1
7171	8	123	4	field_update	0	Insert
7172	8	123	5	field_name	0	address_2
7173	8	123	5	field_lookup	0	address_2
7174	8	123	5	field_update	0	Insert
7175	8	123	6	field_name	0	city
7176	8	123	6	field_lookup	0	city
7177	8	123	6	field_update	0	Insert
7178	8	123	7	field_name	0	state
7179	8	123	7	field_lookup	0	state
7180	8	123	7	field_update	0	Insert
7181	8	123	8	field_name	0	zip
7182	8	123	8	field_lookup	0	zip
7183	8	123	8	field_update	0	Insert
7184	8	123	9	field_name	0	country
7185	8	123	9	field_lookup	0	country
7186	8	123	9	field_update	0	Insert
7187	8	123	10	field_name	0	telephone
7188	8	123	10	field_lookup	0	telephone
7189	8	123	10	field_update	0	Insert
7190	8	123	11	field_name	0	tel_ext
7191	8	123	11	field_lookup	0	tel_ext
7192	8	123	11	field_update	0	Insert
7193	8	123	12	field_name	0	dob
7194	8	123	12	field_lookup	0	dob
7195	8	123	12	field_update	0	Insert
7196	8	123	13	field_name	0	gender
7197	8	123	13	field_lookup	0	gender
7198	8	123	13	field_update	0	Insert
7199	8	123	14	field_name	0	race
7200	8	123	14	field_lookup	0	race
7201	8	123	14	field_update	0	Insert
7202	8	123	15	field_name	0	lang
7203	8	123	15	field_lookup	0	lang
7204	8	123	15	field_update	0	Insert
7205	8	123	16	field_name	0	ssn
7206	8	123	16	field_lookup	0	ssn
7207	8	123	16	field_update	0	Insert
7208	8	123	17	field_name	0	phy
7209	8	123	17	field_lookup	0	phy
7210	8	123	17	field_update	0	Insert
7211	8	123	18	field_name	0	marital_status
7212	8	123	18	field_lookup	0	marital_status
7213	8	123	18	field_update	0	Insert
7214	8	123	19	field_name	0	religion
7215	8	123	19	field_lookup	0	religion
7216	8	123	19	field_update	0	Insert
7217	8	123	20	field_name	0	mom
7218	8	123	20	field_lookup	0	mom
7219	8	123	20	field_update	0	Insert
7220	8	123	21	field_name	0	death
7221	8	123	21	field_lookup	0	death
7222	8	123	21	field_update	0	Insert
7223	8	123	22	field_name	0	row_num
7224	8	123	22	field_lookup	0	row_num
7225	8	123	22	field_update	0	Insert
7226	8	123	0	return_name	0	patient_id
7227	8	123	0	return_rename	0	\N
7228	8	123	0	creation_method	0	sequence
7229	8	123	0	use_autoinc	0	N
7230	8	123	0	version_field	0	version
7231	8	123	0	sequence	0	patient_dim_patient_id_seq
7232	8	123	0	min_year	1900	\N
7233	8	123	0	max_year	2199	\N
7234	8	123	0	cache_size	5000	\N
7235	8	123	0	cluster_schema	0	\N
7236	8	124	0	PARTITIONING_SCHEMA	0	\N
7237	8	124	0	PARTITIONING_METHOD	0	none
7238	8	124	0	filename	0	/home/rejmv/work/new-esp/src/esp/test_data/epicmem.esp.02032009
7239	8	124	0	filename_field	0	\N
7240	8	124	0	rownum_field	0	row_num
7241	8	124	0	include_filename	0	N
7242	8	124	0	separator	0	^
7243	8	124	0	enclosure	0	"
7244	8	124	0	buffer_size	0	50000
7245	8	124	0	header	0	N
7246	8	124	0	lazy_conversion	0	N
7247	8	124	0	add_filename_result	0	N
7248	8	124	0	parallel	0	N
7249	8	124	0	encoding	0	\N
7250	8	124	0	field_name	0	ext_patient_id
7251	8	124	0	field_type	0	String
7252	8	124	0	field_format	0	\N
7253	8	124	0	field_currency	0	\N
7254	8	124	0	field_decimal	0	\N
7255	8	124	0	field_group	0	\N
7256	8	124	0	field_length	-1	\N
7257	8	124	0	field_precision	-1	\N
7258	8	124	0	field_trim_type	0	none
7259	8	124	1	field_name	0	medical_record_num
7260	8	124	1	field_type	0	String
7261	8	124	1	field_format	0	\N
7262	8	124	1	field_currency	0	\N
7263	8	124	1	field_decimal	0	\N
7264	8	124	1	field_group	0	\N
7265	8	124	1	field_length	-1	\N
7266	8	124	1	field_precision	-1	\N
7267	8	124	1	field_trim_type	0	none
7268	8	124	2	field_name	0	last_name
7269	8	124	2	field_type	0	String
7270	8	124	2	field_format	0	\N
7271	8	124	2	field_currency	0	\N
7272	8	124	2	field_decimal	0	\N
7273	8	124	2	field_group	0	\N
7274	8	124	2	field_length	-1	\N
7275	8	124	2	field_precision	-1	\N
7276	8	124	2	field_trim_type	0	none
7277	8	124	3	field_name	0	first_name
7278	8	124	3	field_type	0	String
7279	8	124	3	field_format	0	\N
7280	8	124	3	field_currency	0	\N
7281	8	124	3	field_decimal	0	\N
7282	8	124	3	field_group	0	\N
7283	8	124	3	field_length	-1	\N
7284	8	124	3	field_precision	-1	\N
7285	8	124	3	field_trim_type	0	none
7286	8	124	4	field_name	0	middle_name
7287	8	124	4	field_type	0	String
7288	8	124	4	field_format	0	\N
7289	8	124	4	field_currency	0	\N
7290	8	124	4	field_decimal	0	\N
7291	8	124	4	field_group	0	\N
7292	8	124	4	field_length	-1	\N
7293	8	124	4	field_precision	-1	\N
7294	8	124	4	field_trim_type	0	none
7295	8	124	5	field_name	0	address_1
7296	8	124	5	field_type	0	String
7297	8	124	5	field_format	0	\N
7298	8	124	5	field_currency	0	\N
7299	8	124	5	field_decimal	0	\N
7300	8	124	5	field_group	0	\N
7301	8	124	5	field_length	-1	\N
7302	8	124	5	field_precision	-1	\N
7303	8	124	5	field_trim_type	0	none
9580	12	172	22	field_name	0	death
9581	12	172	22	field_type	0	String
9582	12	172	22	field_format	0	\N
9583	12	172	22	field_currency	0	\N
9584	12	172	22	field_decimal	0	\N
9585	12	172	22	field_group	0	\N
9586	12	172	22	field_length	-1	\N
9587	12	172	22	field_precision	-1	\N
9588	12	172	22	field_trim_type	0	none
9589	12	172	0	cluster_schema	0	\N
9590	12	173	0	PARTITIONING_SCHEMA	0	\N
9591	12	173	0	PARTITIONING_METHOD	0	none
9592	12	173	0	id_connection	7	\N
9593	12	173	0	schema	0	\N
9594	12	173	0	table	0	epic_mem
9595	12	173	0	commit	100	\N
9596	12	173	0	truncate	0	N
9597	12	173	0	ignore_errors	0	N
9598	12	173	0	use_batch	0	Y
9599	12	173	0	partitioning_enabled	0	N
9600	12	173	0	partitioning_field	0	\N
9601	12	173	0	partitioning_daily	0	N
9602	12	173	0	partitioning_monthly	0	Y
9603	12	173	0	tablename_in_field	0	N
9604	12	173	0	tablename_field	0	\N
9605	12	173	0	tablename_in_table	0	Y
9606	12	173	0	return_keys	0	N
9607	12	173	0	return_field	0	\N
9608	12	173	0	cluster_schema	0	\N
15539	15	274	10	field_type	0	String
15540	15	274	10	field_format	0	\N
15541	15	274	10	field_currency	0	\N
15542	15	274	10	field_decimal	0	\N
15543	15	274	10	field_group	0	\N
15544	15	274	10	field_length	-1	\N
15545	15	274	10	field_precision	-1	\N
15546	15	274	10	field_trim_type	0	none
15547	15	274	11	field_name	0	CHNG_TYPE
15548	15	274	11	field_type	0	String
15549	15	274	11	field_format	0	\N
15550	15	274	11	field_currency	0	\N
15551	15	274	11	field_decimal	0	\N
15552	15	274	11	field_group	0	\N
15553	15	274	11	field_length	-1	\N
15554	15	274	11	field_precision	-1	\N
15555	15	274	11	field_trim_type	0	none
15556	15	274	12	field_name	0	COMMENTS
15557	15	274	12	field_type	0	String
15558	15	274	12	field_format	0	\N
15559	15	274	12	field_currency	0	\N
15560	15	274	12	field_decimal	0	\N
15561	15	274	12	field_group	0	\N
15562	15	274	12	field_length	-1	\N
15563	15	274	12	field_precision	-1	\N
15564	15	274	12	field_trim_type	0	none
15565	15	274	13	field_name	0	ANSWERLIST
15566	15	274	13	field_type	0	String
15567	15	274	13	field_format	0	\N
15568	15	274	13	field_currency	0	\N
15569	15	274	13	field_decimal	0	\N
15570	15	274	13	field_group	0	\N
15571	15	274	13	field_length	-1	\N
15572	15	274	13	field_precision	-1	\N
7304	8	124	6	field_name	0	address_2
15573	15	274	13	field_trim_type	0	none
15574	15	274	14	field_name	0	STATUS
15575	15	274	14	field_type	0	String
15576	15	274	14	field_format	0	\N
15577	15	274	14	field_currency	0	\N
15578	15	274	14	field_decimal	0	\N
15579	15	274	14	field_group	0	\N
15580	15	274	14	field_length	-1	\N
15581	15	274	14	field_precision	-1	\N
15582	15	274	14	field_trim_type	0	none
15583	15	274	15	field_name	0	MAP_TO
15584	15	274	15	field_type	0	String
15585	15	274	15	field_format	0	\N
15586	15	274	15	field_currency	0	\N
15587	15	274	15	field_decimal	0	\N
15588	15	274	15	field_group	0	\N
15589	15	274	15	field_length	-1	\N
15590	15	274	15	field_precision	-1	\N
15591	15	274	15	field_trim_type	0	none
15592	15	274	16	field_name	0	SCOPE
15593	15	274	16	field_type	0	String
15594	15	274	16	field_format	0	\N
15595	15	274	16	field_currency	0	\N
15596	15	274	16	field_decimal	0	\N
15597	15	274	16	field_group	0	\N
15598	15	274	16	field_length	-1	\N
15599	15	274	16	field_precision	-1	\N
15600	15	274	16	field_trim_type	0	none
15601	15	274	17	field_name	0	NORM_RANGE
15602	15	274	17	field_type	0	String
15603	15	274	17	field_format	0	\N
15604	15	274	17	field_currency	0	\N
15605	15	274	17	field_decimal	0	\N
15606	15	274	17	field_group	0	\N
15607	15	274	17	field_length	-1	\N
15608	15	274	17	field_precision	-1	\N
15609	15	274	17	field_trim_type	0	none
15610	15	274	18	field_name	0	IPCC_UNITS
15611	15	274	18	field_type	0	String
15612	15	274	18	field_format	0	\N
15613	15	274	18	field_currency	0	\N
15614	15	274	18	field_decimal	0	\N
15615	15	274	18	field_group	0	\N
15616	15	274	18	field_length	-1	\N
15617	15	274	18	field_precision	-1	\N
15618	15	274	18	field_trim_type	0	none
15619	15	274	19	field_name	0	REFERENCE
15620	15	274	19	field_type	0	String
15621	15	274	19	field_format	0	\N
15622	15	274	19	field_currency	0	\N
15623	15	274	19	field_decimal	0	\N
15624	15	274	19	field_group	0	\N
15625	15	274	19	field_length	-1	\N
15626	15	274	19	field_precision	-1	\N
15627	15	274	19	field_trim_type	0	none
15628	15	274	20	field_name	0	EXACT_CMP_SY
15629	15	274	20	field_type	0	String
15630	15	274	20	field_format	0	\N
15631	15	274	20	field_currency	0	\N
15632	15	274	20	field_decimal	0	\N
15633	15	274	20	field_group	0	\N
15634	15	274	20	field_length	-1	\N
15635	15	274	20	field_precision	-1	\N
15636	15	274	20	field_trim_type	0	none
15637	15	274	21	field_name	0	MOLAR_MASS
15638	15	274	21	field_type	0	String
15639	15	274	21	field_format	0	\N
15640	15	274	21	field_currency	0	\N
15641	15	274	21	field_decimal	0	\N
15642	15	274	21	field_group	0	\N
15643	15	274	21	field_length	-1	\N
15644	15	274	21	field_precision	-1	\N
15645	15	274	21	field_trim_type	0	none
15646	15	274	22	field_name	0	CLASSTYPE
15647	15	274	22	field_type	0	String
15648	15	274	22	field_format	0	\N
15649	15	274	22	field_currency	0	\N
15650	15	274	22	field_decimal	0	\N
15651	15	274	22	field_group	0	\N
15652	15	274	22	field_length	-1	\N
15653	15	274	22	field_precision	-1	\N
15654	15	274	22	field_trim_type	0	none
15655	15	274	23	field_name	0	FORMULA
15656	15	274	23	field_type	0	String
15657	15	274	23	field_format	0	\N
15658	15	274	23	field_currency	0	\N
15659	15	274	23	field_decimal	0	\N
15660	15	274	23	field_group	0	\N
15661	15	274	23	field_length	-1	\N
15662	15	274	23	field_precision	-1	\N
15663	15	274	23	field_trim_type	0	none
15664	15	274	24	field_name	0	SPECIES
15665	15	274	24	field_type	0	String
15666	15	274	24	field_format	0	\N
15667	15	274	24	field_currency	0	\N
15668	15	274	24	field_decimal	0	\N
15669	15	274	24	field_group	0	\N
15670	15	274	24	field_length	-1	\N
15671	15	274	24	field_precision	-1	\N
15672	15	274	24	field_trim_type	0	none
15673	15	274	25	field_name	0	EXMPL_ANSWERS
15674	15	274	25	field_type	0	String
15675	15	274	25	field_format	0	\N
15676	15	274	25	field_currency	0	\N
15677	15	274	25	field_decimal	0	\N
15678	15	274	25	field_group	0	\N
15679	15	274	25	field_length	-1	\N
15680	15	274	25	field_precision	-1	\N
15681	15	274	25	field_trim_type	0	none
15682	15	274	26	field_name	0	ACSSYM
15683	15	274	26	field_type	0	String
15684	15	274	26	field_format	0	\N
15685	15	274	26	field_currency	0	\N
15686	15	274	26	field_decimal	0	\N
15687	15	274	26	field_group	0	\N
15688	15	274	26	field_length	-1	\N
15689	15	274	26	field_precision	-1	\N
15690	15	274	26	field_trim_type	0	none
15691	15	274	27	field_name	0	BASE_NAME
15692	15	274	27	field_type	0	String
15693	15	274	27	field_format	0	\N
15694	15	274	27	field_currency	0	\N
15695	15	274	27	field_decimal	0	\N
15696	15	274	27	field_group	0	\N
15697	15	274	27	field_length	-1	\N
15698	15	274	27	field_precision	-1	\N
15699	15	274	27	field_trim_type	0	none
15700	15	274	28	field_name	0	FINAL
15701	15	274	28	field_type	0	String
15702	15	274	28	field_format	0	\N
15703	15	274	28	field_currency	0	\N
15704	15	274	28	field_decimal	0	\N
15705	15	274	28	field_group	0	\N
15706	15	274	28	field_length	-1	\N
15707	15	274	28	field_precision	-1	\N
15708	15	274	28	field_trim_type	0	none
15709	15	274	29	field_name	0	NAACCR_ID
15710	15	274	29	field_type	0	String
15711	15	274	29	field_format	0	\N
15712	15	274	29	field_currency	0	\N
15713	15	274	29	field_decimal	0	\N
15714	15	274	29	field_group	0	\N
15715	15	274	29	field_length	-1	\N
15716	15	274	29	field_precision	-1	\N
15717	15	274	29	field_trim_type	0	none
15718	15	274	30	field_name	0	CODE_TABLE
15719	15	274	30	field_type	0	String
15720	15	274	30	field_format	0	\N
15721	15	274	30	field_currency	0	\N
15722	15	274	30	field_decimal	0	\N
15723	15	274	30	field_group	0	\N
15724	15	274	30	field_length	-1	\N
15725	15	274	30	field_precision	-1	\N
15726	15	274	30	field_trim_type	0	none
15727	15	274	31	field_name	0	SETROOT
15728	15	274	31	field_type	0	String
15729	15	274	31	field_format	0	\N
15730	15	274	31	field_currency	0	\N
15731	15	274	31	field_decimal	0	\N
15732	15	274	31	field_group	0	\N
15733	15	274	31	field_length	-1	\N
15734	15	274	31	field_precision	-1	\N
15735	15	274	31	field_trim_type	0	none
15736	15	274	32	field_name	0	PANELELEMENTS
15737	15	274	32	field_type	0	String
15738	15	274	32	field_format	0	\N
15739	15	274	32	field_currency	0	\N
15740	15	274	32	field_decimal	0	\N
15741	15	274	32	field_group	0	\N
15742	15	274	32	field_length	-1	\N
15743	15	274	32	field_precision	-1	\N
15744	15	274	32	field_trim_type	0	none
6133	10	101	0	PARTITIONING_SCHEMA	0	\N
6134	10	101	0	PARTITIONING_METHOD	0	none
6135	10	101	0	filename	0	/home/rejmv/work/new-esp/src/esp/test_data/order.hvma.txt
6136	10	101	0	filename_field	0	\N
6137	10	101	0	rownum_field	0	\N
6138	10	101	0	include_filename	0	N
6139	10	101	0	separator	0	^
6140	10	101	0	enclosure	0	"
6141	10	101	0	buffer_size	0	50000
6142	10	101	0	header	0	N
6143	10	101	0	lazy_conversion	0	N
6144	10	101	0	add_filename_result	0	N
6145	10	101	0	parallel	0	N
6146	10	101	0	encoding	0	\N
6147	10	101	0	field_name	0	ext_patient_id
6148	10	101	0	field_type	0	String
6149	10	101	0	field_format	0	\N
6150	10	101	0	field_currency	0	\N
6151	10	101	0	field_decimal	0	\N
6152	10	101	0	field_group	0	\N
6153	10	101	0	field_length	-1	\N
6154	10	101	0	field_precision	-1	\N
6155	10	101	0	field_trim_type	0	none
6156	10	101	1	field_name	0	medical_record_num
6157	10	101	1	field_type	0	String
6158	10	101	1	field_format	0	\N
6159	10	101	1	field_currency	0	\N
6160	10	101	1	field_decimal	0	\N
6161	10	101	1	field_group	0	\N
6162	10	101	1	field_length	-1	\N
6163	10	101	1	field_precision	-1	\N
6164	10	101	1	field_trim_type	0	none
6165	10	101	2	field_name	0	ext_order_id
6166	10	101	2	field_type	0	String
6167	10	101	2	field_format	0	\N
6168	10	101	2	field_currency	0	\N
6169	10	101	2	field_decimal	0	\N
6170	10	101	2	field_group	0	\N
6171	10	101	2	field_length	-1	\N
6172	10	101	2	field_precision	-1	\N
6173	10	101	2	field_trim_type	0	none
6174	10	101	3	field_name	0	ext_test_code
6175	10	101	3	field_type	0	String
6176	10	101	3	field_format	0	\N
6177	10	101	3	field_currency	0	\N
6178	10	101	3	field_decimal	0	\N
6179	10	101	3	field_group	0	\N
6180	10	101	3	field_length	-1	\N
6181	10	101	3	field_precision	-1	\N
6182	10	101	3	field_trim_type	0	none
6183	10	101	4	field_name	0	ext_test_subcode
6184	10	101	4	field_type	0	String
6185	10	101	4	field_format	0	\N
6186	10	101	4	field_currency	0	\N
6187	10	101	4	field_decimal	0	\N
6188	10	101	4	field_group	0	\N
6189	10	101	4	field_length	-1	\N
6190	10	101	4	field_precision	-1	\N
6191	10	101	4	field_trim_type	0	none
6192	10	101	5	field_name	0	accessnum
6193	10	101	5	field_type	0	String
6194	10	101	5	field_format	0	\N
6195	10	101	5	field_currency	0	\N
6196	10	101	5	field_decimal	0	\N
6197	10	101	5	field_group	0	\N
6198	10	101	5	field_length	-1	\N
6199	10	101	5	field_precision	-1	\N
6200	10	101	5	field_trim_type	0	none
6201	10	101	6	field_name	0	order date
6202	10	101	6	field_type	0	String
6203	10	101	6	field_format	0	\N
6204	10	101	6	field_currency	0	\N
6205	10	101	6	field_decimal	0	\N
6206	10	101	6	field_group	0	\N
6207	10	101	6	field_length	-1	\N
6208	10	101	6	field_precision	-1	\N
6209	10	101	6	field_trim_type	0	none
6210	10	101	7	field_name	0	order type
6211	10	101	7	field_type	0	String
6212	10	101	7	field_format	0	\N
6213	10	101	7	field_currency	0	\N
6214	10	101	7	field_decimal	0	\N
6215	10	101	7	field_group	0	\N
6216	10	101	7	field_length	-1	\N
6217	10	101	7	field_precision	-1	\N
6218	10	101	7	field_trim_type	0	none
6219	10	101	8	field_name	0	ext_physician_code
6220	10	101	8	field_type	0	String
6221	10	101	8	field_format	0	\N
6222	10	101	8	field_currency	0	\N
6223	10	101	8	field_decimal	0	\N
6224	10	101	8	field_group	0	\N
6225	10	101	8	field_length	-1	\N
6226	10	101	8	field_precision	-1	\N
6227	10	101	8	field_trim_type	0	none
6228	10	101	0	cluster_schema	0	\N
6229	10	102	0	PARTITIONING_SCHEMA	0	\N
6230	10	102	0	PARTITIONING_METHOD	0	none
6231	10	102	0	schema	0	\N
6232	10	102	0	table	0	order_dim
6233	10	102	0	id_connection	5	\N
6234	10	102	0	commit	100	\N
6235	10	102	0	update	0	Y
6236	10	102	0	lookup_key_name	0	ext_order_id
6237	10	102	0	lookup_key_field	0	ext_order_id
6238	10	102	1	lookup_key_name	0	ext_emr_system
6239	10	102	1	lookup_key_field	0	ext_emr_system
6240	10	102	0	date_name	0	\N
6241	10	102	0	date_from	0	date_from
6242	10	102	0	date_to	0	date_to
6243	10	102	0	field_name	0	ext_patient_id
6244	10	102	0	field_lookup	0	ext_patient_id
6245	10	102	0	field_update	0	Insert
6246	10	102	1	field_name	0	medical_record_num
6247	10	102	1	field_lookup	0	medical_record_num
6248	10	102	1	field_update	0	Insert
6249	10	102	2	field_name	0	ext_test_code
6250	10	102	2	field_lookup	0	ext_test_code
6251	10	102	2	field_update	0	Insert
6252	10	102	3	field_name	0	ext_test_subcode
6253	10	102	3	field_lookup	0	ext_test_subcode
6254	10	102	3	field_update	0	Insert
6255	10	102	4	field_name	0	accessnum
6256	10	102	4	field_lookup	0	accessnum
6257	10	102	4	field_update	0	Insert
6258	10	102	5	field_name	0	order date
6259	10	102	5	field_lookup	0	order date
6260	10	102	5	field_update	0	Insert
6261	10	102	6	field_name	0	order type
6262	10	102	6	field_lookup	0	order type
6263	10	102	6	field_update	0	Insert
6264	10	102	7	field_name	0	ext_physician_code
6265	10	102	7	field_lookup	0	ext_physician_code
6266	10	102	7	field_update	0	Insert
6267	10	102	0	return_name	0	order_id
6268	10	102	0	return_rename	0	\N
6269	10	102	0	creation_method	0	tablemax
6270	10	102	0	use_autoinc	0	N
6271	10	102	0	version_field	0	version
6272	10	102	0	sequence	0	\N
6273	10	102	0	min_year	1900	\N
6274	10	102	0	max_year	2199	\N
6275	10	102	0	cache_size	5000	\N
6276	10	102	0	cluster_schema	0	\N
6277	10	103	0	PARTITIONING_SCHEMA	0	\N
6278	10	103	0	PARTITIONING_METHOD	0	none
15745	15	274	33	field_name	0	SURVEY_QUEST_TEXT
15746	15	274	33	field_type	0	String
15747	15	274	33	field_format	0	\N
15748	15	274	33	field_currency	0	\N
15749	15	274	33	field_decimal	0	\N
15750	15	274	33	field_group	0	\N
15751	15	274	33	field_length	-1	\N
15752	15	274	33	field_precision	-1	\N
15753	15	274	33	field_trim_type	0	none
15754	15	274	34	field_name	0	SURVEY_QUEST_SRC
15755	15	274	34	field_type	0	String
15756	15	274	34	field_format	0	\N
15757	15	274	34	field_currency	0	\N
15758	15	274	34	field_decimal	0	\N
15759	15	274	34	field_group	0	\N
15760	15	274	34	field_length	-1	\N
15761	15	274	34	field_precision	-1	\N
15762	15	274	34	field_trim_type	0	none
15763	15	274	35	field_name	0	UNITSREQUIRED
15764	15	274	35	field_type	0	String
15765	15	274	35	field_format	0	\N
15766	15	274	35	field_currency	0	\N
15767	15	274	35	field_decimal	0	\N
15768	15	274	35	field_group	0	\N
15769	15	274	35	field_length	-1	\N
15770	15	274	35	field_precision	-1	\N
15771	15	274	35	field_trim_type	0	none
7305	8	124	6	field_type	0	String
7306	8	124	6	field_format	0	\N
7307	8	124	6	field_currency	0	\N
7308	8	124	6	field_decimal	0	\N
15772	15	274	36	field_name	0	SUBMITTED_UNITS
15773	15	274	36	field_type	0	String
15774	15	274	36	field_format	0	\N
15775	15	274	36	field_currency	0	\N
15776	15	274	36	field_decimal	0	\N
9218	9	169	0	field_name	0	dateTime
9219	9	169	0	field_rename	0	dateTime
9220	9	169	0	field_type	0	String
9221	9	169	0	field_length	-1	\N
9222	9	169	0	field_precision	-1	\N
9223	9	169	1	field_name	0	day_of_month
9224	9	169	1	field_rename	0	day_of_month
9225	9	169	1	field_type	0	String
9226	9	169	1	field_length	-1	\N
9227	9	169	1	field_precision	-1	\N
9228	9	169	2	field_name	0	week_of_year
9229	9	169	2	field_rename	0	week_of_year
9230	9	169	2	field_type	0	String
9231	9	169	2	field_length	-1	\N
9232	9	169	2	field_precision	-1	\N
9233	9	169	3	field_name	0	month_of_year
9234	9	169	3	field_rename	0	month_of_year
9235	9	169	3	field_type	0	String
9236	9	169	3	field_length	-1	\N
9237	9	169	3	field_precision	-1	\N
9238	9	169	4	field_name	0	year
9239	9	169	4	field_rename	0	year
9240	9	169	4	field_type	0	String
9241	9	169	4	field_length	-1	\N
9242	9	169	4	field_precision	-1	\N
9243	9	169	5	field_name	0	quarter
9244	9	169	5	field_rename	0	quarter
9245	9	169	5	field_type	0	String
9246	9	169	5	field_length	-1	\N
9247	9	169	5	field_precision	-1	\N
9248	9	169	6	field_name	0	name_day
9249	9	169	6	field_rename	0	name_day
9250	9	169	6	field_type	0	String
9251	9	169	6	field_length	-1	\N
9252	9	169	6	field_precision	-1	\N
9253	9	169	7	field_name	0	name_month
9254	9	169	7	field_rename	0	name_month
9255	9	169	7	field_type	0	String
9256	9	169	7	field_length	-1	\N
9257	9	169	7	field_precision	-1	\N
9258	9	169	0	cluster_schema	0	\N
9259	9	170	0	PARTITIONING_SCHEMA	0	\N
9260	9	170	0	PARTITIONING_METHOD	0	none
9261	9	170	0	field_name	0	ext_patient_id
9262	9	170	0	field_rename	0	\N
9263	9	170	0	field_length	-2	\N
9264	9	170	0	field_precision	-2	\N
9265	9	170	1	field_name	0	medical_record_num
9266	9	170	1	field_rename	0	\N
9267	9	170	1	field_length	-2	\N
9268	9	170	1	field_precision	-2	\N
9269	9	170	2	field_name	0	ext_order_id
9270	9	170	2	field_rename	0	\N
9271	9	170	2	field_length	-2	\N
9272	9	170	2	field_precision	-2	\N
9273	9	170	3	field_name	0	order_date
9274	9	170	3	field_rename	0	\N
9275	9	170	3	field_length	-2	\N
9276	9	170	3	field_precision	-2	\N
9277	9	170	4	field_name	0	result_date
9278	9	170	4	field_rename	0	\N
9279	9	170	4	field_length	-2	\N
9280	9	170	4	field_precision	-2	\N
9281	9	170	5	field_name	0	ext_physician_id
9282	9	170	5	field_rename	0	\N
9283	9	170	5	field_length	-2	\N
9284	9	170	5	field_precision	-2	\N
9285	9	170	6	field_name	0	order_type
9286	9	170	6	field_rename	0	\N
9287	9	170	6	field_length	-2	\N
9288	9	170	6	field_precision	-2	\N
9289	9	170	7	field_name	0	ext_test_code
9290	9	170	7	field_rename	0	\N
9291	9	170	7	field_length	-2	\N
9292	9	170	7	field_precision	-2	\N
9293	9	170	8	field_name	0	ext_test_subcode
9294	9	170	8	field_rename	0	\N
9295	9	170	8	field_length	-2	\N
9296	9	170	8	field_precision	-2	\N
9297	9	170	9	field_name	0	ext_test_name
9298	9	170	9	field_rename	0	\N
9299	9	170	9	field_length	-2	\N
9300	9	170	9	field_precision	-2	\N
9301	9	170	10	field_name	0	result
9302	9	170	10	field_rename	0	\N
9303	9	170	10	field_length	-2	\N
9304	9	170	10	field_precision	-2	\N
9305	9	170	11	field_name	0	normal_flag
9306	9	170	11	field_rename	0	\N
9307	9	170	11	field_length	-2	\N
9308	9	170	11	field_precision	-2	\N
9309	9	170	12	field_name	0	reference_low
9310	9	170	12	field_rename	0	\N
9311	9	170	12	field_length	-2	\N
9312	9	170	12	field_precision	-2	\N
9313	9	170	13	field_name	0	reference_high
9314	9	170	13	field_rename	0	\N
9315	9	170	13	field_length	-2	\N
9316	9	170	13	field_precision	-2	\N
9317	9	170	14	field_name	0	reference_units
9318	9	170	14	field_rename	0	\N
9319	9	170	14	field_length	-2	\N
9320	9	170	14	field_precision	-2	\N
9321	9	170	15	field_name	0	status
9322	9	170	15	field_rename	0	\N
9323	9	170	15	field_length	-2	\N
9324	9	170	15	field_precision	-2	\N
9325	9	170	16	field_name	0	notes
9326	9	170	16	field_rename	0	\N
9327	9	170	16	field_length	-2	\N
9328	9	170	16	field_precision	-2	\N
9329	9	170	17	field_name	0	accessnum
9330	9	170	17	field_rename	0	\N
9331	9	170	17	field_length	-2	\N
9332	9	170	17	field_precision	-2	\N
9333	9	170	18	field_name	0	impression
9334	9	170	18	field_rename	0	\N
9335	9	170	18	field_length	-2	\N
9336	9	170	18	field_precision	-2	\N
9337	9	170	19	field_name	0	ext_emr_system
9338	9	170	19	field_rename	0	\N
9339	9	170	19	field_length	-2	\N
9340	9	170	19	field_precision	-2	\N
6279	10	103	0	field_name	0	ext_emr_system
6280	10	103	0	field_type	0	String
6281	10	103	0	field_format	0	\N
6282	10	103	0	field_currency	0	\N
6283	10	103	0	field_decimal	0	\N
6284	10	103	0	field_group	0	\N
6285	10	103	0	field_nullif	0	North Adams
6286	10	103	0	field_length	-1	\N
6287	10	103	0	field_precision	-1	\N
6288	10	103	0	cluster_schema	0	\N
9341	9	170	20	field_name	0	order_date_id
9342	9	170	20	field_rename	0	\N
9343	9	170	20	field_length	-2	\N
9344	9	170	20	field_precision	-2	\N
9345	9	170	21	field_name	0	date_id
9346	9	170	21	field_rename	0	result_date_id
9347	9	170	21	field_length	-2	\N
9348	9	170	21	field_precision	-2	\N
9349	9	170	0	select_unspecified	0	N
9350	9	170	0	cluster_schema	0	\N
9351	9	171	0	PARTITIONING_SCHEMA	0	\N
9352	9	171	0	PARTITIONING_METHOD	0	none
9353	9	171	0	schema	0	\N
9354	9	171	0	table	0	medical_record_dim
9355	9	171	0	id_connection	5	\N
9356	9	171	0	commit	100	\N
9357	9	171	0	cache_size	9999	\N
9358	9	171	0	replace	0	N
9359	9	171	0	crc	0	N
9360	9	171	0	crcfield	0	hashcode
9361	9	171	0	lookup_key_name	0	medical_record_num
9362	9	171	0	lookup_key_field	0	medical_record_num
9363	9	171	0	return_name	0	medical_record_id
9364	9	171	0	sequence	0	\N
9365	9	171	0	creation_method	0	tablemax
9366	9	171	0	use_autoinc	0	N
9367	9	171	0	cluster_schema	0	\N
15777	15	274	36	field_group	0	\N
15778	15	274	36	field_length	-1	\N
15779	15	274	36	field_precision	-1	\N
15780	15	274	36	field_trim_type	0	none
15781	15	274	37	field_name	0	RELATEDNAMES2
15782	15	274	37	field_type	0	String
15783	15	274	37	field_format	0	\N
15784	15	274	37	field_currency	0	\N
15785	15	274	37	field_decimal	0	\N
15786	15	274	37	field_group	0	\N
15787	15	274	37	field_length	-1	\N
15788	15	274	37	field_precision	-1	\N
15789	15	274	37	field_trim_type	0	none
15790	15	274	38	field_name	0	SHORTNAME
15791	15	274	38	field_type	0	String
15792	15	274	38	field_format	0	\N
15793	15	274	38	field_currency	0	\N
15794	15	274	38	field_decimal	0	\N
15795	15	274	38	field_group	0	\N
15796	15	274	38	field_length	-1	\N
15797	15	274	38	field_precision	-1	\N
15798	15	274	38	field_trim_type	0	none
15799	15	274	39	field_name	0	ORDER_OBS
15800	15	274	39	field_type	0	String
15801	15	274	39	field_format	0	\N
15802	15	274	39	field_currency	0	\N
15803	15	274	39	field_decimal	0	\N
15804	15	274	39	field_group	0	\N
15805	15	274	39	field_length	-1	\N
15806	15	274	39	field_precision	-1	\N
15807	15	274	39	field_trim_type	0	none
15808	15	274	40	field_name	0	CDISC_COMMON_TESTS
15809	15	274	40	field_type	0	String
15810	15	274	40	field_format	0	\N
15811	15	274	40	field_currency	0	\N
15812	15	274	40	field_decimal	0	\N
15813	15	274	40	field_group	0	\N
15814	15	274	40	field_length	-1	\N
15815	15	274	40	field_precision	-1	\N
15816	15	274	40	field_trim_type	0	none
15817	15	274	41	field_name	0	HL7_FIELD_SUBFIELD_ID
15818	15	274	41	field_type	0	String
15819	15	274	41	field_format	0	\N
15820	15	274	41	field_currency	0	\N
15821	15	274	41	field_decimal	0	\N
15822	15	274	41	field_group	0	\N
15823	15	274	41	field_length	-1	\N
15824	15	274	41	field_precision	-1	\N
15825	15	274	41	field_trim_type	0	none
15826	15	274	42	field_name	0	EXTERNAL_COPYRIGHT_NOTICE
15827	15	274	42	field_type	0	String
15828	15	274	42	field_format	0	\N
15829	15	274	42	field_currency	0	\N
15830	15	274	42	field_decimal	0	\N
15831	15	274	42	field_group	0	\N
15832	15	274	42	field_length	-1	\N
15833	15	274	42	field_precision	-1	\N
15834	15	274	42	field_trim_type	0	none
15835	15	274	43	field_name	0	EXAMPLE_UNITS
15836	15	274	43	field_type	0	String
15837	15	274	43	field_format	0	\N
15838	15	274	43	field_currency	0	\N
15839	15	274	43	field_decimal	0	\N
15840	15	274	43	field_group	0	\N
15841	15	274	43	field_length	-1	\N
15842	15	274	43	field_precision	-1	\N
15843	15	274	43	field_trim_type	0	none
15844	15	274	44	field_name	0	INPC_PERCENTAGE
15845	15	274	44	field_type	0	String
15846	15	274	44	field_format	0	\N
15847	15	274	44	field_currency	0	\N
15848	15	274	44	field_decimal	0	\N
15849	15	274	44	field_group	0	\N
15850	15	274	44	field_length	-1	\N
15851	15	274	44	field_precision	-1	\N
15852	15	274	44	field_trim_type	0	none
15853	15	274	45	field_name	0	LONG_COMMON_NAME
15854	15	274	45	field_type	0	String
15855	15	274	45	field_format	0	\N
15856	15	274	45	field_currency	0	\N
15857	15	274	45	field_decimal	0	\N
15858	15	274	45	field_group	0	\N
15859	15	274	45	field_length	-1	\N
7309	8	124	6	field_group	0	\N
7310	8	124	6	field_length	-1	\N
7311	8	124	6	field_precision	-1	\N
7312	8	124	6	field_trim_type	0	none
7313	8	124	7	field_name	0	city
7314	8	124	7	field_type	0	String
7315	8	124	7	field_format	0	\N
7316	8	124	7	field_currency	0	\N
7317	8	124	7	field_decimal	0	\N
7318	8	124	7	field_group	0	\N
7319	8	124	7	field_length	-1	\N
7320	8	124	7	field_precision	-1	\N
7321	8	124	7	field_trim_type	0	none
7322	8	124	8	field_name	0	state
7323	8	124	8	field_type	0	String
7324	8	124	8	field_format	0	\N
7325	8	124	8	field_currency	0	\N
7326	8	124	8	field_decimal	0	\N
7327	8	124	8	field_group	0	\N
7328	8	124	8	field_length	-1	\N
7329	8	124	8	field_precision	-1	\N
7330	8	124	8	field_trim_type	0	none
7331	8	124	9	field_name	0	zip
7332	8	124	9	field_type	0	String
7333	8	124	9	field_format	0	\N
7334	8	124	9	field_currency	0	\N
7335	8	124	9	field_decimal	0	\N
7336	8	124	9	field_group	0	\N
7337	8	124	9	field_length	-1	\N
7338	8	124	9	field_precision	-1	\N
7339	8	124	9	field_trim_type	0	none
7340	8	124	10	field_name	0	country
7341	8	124	10	field_type	0	String
7342	8	124	10	field_format	0	\N
7343	8	124	10	field_currency	0	\N
7344	8	124	10	field_decimal	0	\N
7345	8	124	10	field_group	0	\N
7346	8	124	10	field_length	-1	\N
7347	8	124	10	field_precision	-1	\N
7348	8	124	10	field_trim_type	0	none
7349	8	124	11	field_name	0	telephone
7350	8	124	11	field_type	0	String
7351	8	124	11	field_format	0	\N
7352	8	124	11	field_currency	0	\N
7353	8	124	11	field_decimal	0	\N
7354	8	124	11	field_group	0	\N
7355	8	124	11	field_length	-1	\N
7356	8	124	11	field_precision	-1	\N
7357	8	124	11	field_trim_type	0	none
15860	15	274	45	field_precision	-1	\N
15861	15	274	45	field_trim_type	0	none
15862	15	274	0	cluster_schema	0	\N
15863	15	275	0	PARTITIONING_SCHEMA	0	\N
15864	15	275	0	PARTITIONING_METHOD	0	none
15865	15	275	0	field_name	0	LOINC_NUM
15866	15	275	0	field_rename	0	loinc_num
15867	15	275	0	field_length	-1	\N
15868	15	275	0	field_precision	-1	\N
15869	15	275	1	field_name	0	COMPONENT
15870	15	275	1	field_rename	0	component
15871	15	275	1	field_length	-1	\N
15872	15	275	1	field_precision	-1	\N
15873	15	275	2	field_name	0	PROPERTY
7358	8	124	12	field_name	0	tel_ext
7359	8	124	12	field_type	0	String
7360	8	124	12	field_format	0	\N
7361	8	124	12	field_currency	0	\N
7362	8	124	12	field_decimal	0	\N
7363	8	124	12	field_group	0	\N
7364	8	124	12	field_length	-1	\N
7365	8	124	12	field_precision	-1	\N
7366	8	124	12	field_trim_type	0	none
7367	8	124	13	field_name	0	dob
7368	8	124	13	field_type	0	Date
7369	8	124	13	field_format	0	\N
7370	8	124	13	field_currency	0	\N
7371	8	124	13	field_decimal	0	\N
7372	8	124	13	field_group	0	\N
7373	8	124	13	field_length	-1	\N
7374	8	124	13	field_precision	-1	\N
7375	8	124	13	field_trim_type	0	none
7376	8	124	14	field_name	0	gender
7377	8	124	14	field_type	0	String
7378	8	124	14	field_format	0	\N
7379	8	124	14	field_currency	0	\N
7380	8	124	14	field_decimal	0	\N
7381	8	124	14	field_group	0	\N
7382	8	124	14	field_length	-1	\N
7383	8	124	14	field_precision	-1	\N
7384	8	124	14	field_trim_type	0	none
7385	8	124	15	field_name	0	race
7386	8	124	15	field_type	0	String
7387	8	124	15	field_format	0	\N
7388	8	124	15	field_currency	0	\N
7389	8	124	15	field_decimal	0	\N
7390	8	124	15	field_group	0	\N
7391	8	124	15	field_length	-1	\N
7392	8	124	15	field_precision	-1	\N
7393	8	124	15	field_trim_type	0	none
7394	8	124	16	field_name	0	lang
7395	8	124	16	field_type	0	String
7396	8	124	16	field_format	0	\N
7397	8	124	16	field_currency	0	\N
7398	8	124	16	field_decimal	0	\N
7399	8	124	16	field_group	0	\N
7400	8	124	16	field_length	-1	\N
7401	8	124	16	field_precision	-1	\N
7402	8	124	16	field_trim_type	0	none
7403	8	124	17	field_name	0	ssn
7404	8	124	17	field_type	0	String
7405	8	124	17	field_format	0	\N
7406	8	124	17	field_currency	0	\N
7407	8	124	17	field_decimal	0	\N
7408	8	124	17	field_group	0	\N
7409	8	124	17	field_length	-1	\N
7410	8	124	17	field_precision	-1	\N
7411	8	124	17	field_trim_type	0	none
7412	8	124	18	field_name	0	phy
7413	8	124	18	field_type	0	String
7414	8	124	18	field_format	0	\N
7415	8	124	18	field_currency	0	\N
7416	8	124	18	field_decimal	0	\N
7417	8	124	18	field_group	0	\N
7418	8	124	18	field_length	-1	\N
7419	8	124	18	field_precision	-1	\N
7420	8	124	18	field_trim_type	0	none
7421	8	124	19	field_name	0	marital_status
7422	8	124	19	field_type	0	String
7423	8	124	19	field_format	0	\N
7424	8	124	19	field_currency	0	\N
7425	8	124	19	field_decimal	0	\N
7426	8	124	19	field_group	0	\N
7427	8	124	19	field_length	-1	\N
7428	8	124	19	field_precision	-1	\N
7429	8	124	19	field_trim_type	0	none
7430	8	124	20	field_name	0	religion
7431	8	124	20	field_type	0	String
7432	8	124	20	field_format	0	\N
7433	8	124	20	field_currency	0	\N
7434	8	124	20	field_decimal	0	\N
7435	8	124	20	field_group	0	\N
7436	8	124	20	field_length	-1	\N
7437	8	124	20	field_precision	-1	\N
7438	8	124	20	field_trim_type	0	none
7439	8	124	21	field_name	0	mom
7440	8	124	21	field_type	0	String
7441	8	124	21	field_format	0	\N
7442	8	124	21	field_currency	0	\N
7443	8	124	21	field_decimal	0	\N
7444	8	124	21	field_group	0	\N
7445	8	124	21	field_length	-1	\N
7446	8	124	21	field_precision	-1	\N
7447	8	124	21	field_trim_type	0	none
7448	8	124	22	field_name	0	death
7449	8	124	22	field_type	0	String
7450	8	124	22	field_format	0	\N
7451	8	124	22	field_currency	0	\N
7452	8	124	22	field_decimal	0	\N
7453	8	124	22	field_group	0	\N
7454	8	124	22	field_length	-1	\N
7455	8	124	22	field_precision	-1	\N
7456	8	124	22	field_trim_type	0	none
7457	8	124	0	cluster_schema	0	\N
7458	7	125	0	PARTITIONING_SCHEMA	0	\N
7459	7	125	0	PARTITIONING_METHOD	0	none
7460	7	125	0	field_name	0	ext_emr_system
7461	7	125	0	field_type	0	String
7462	7	125	0	field_format	0	\N
7463	7	125	0	field_currency	0	\N
7464	7	125	0	field_decimal	0	\N
7465	7	125	0	field_group	0	\N
7466	7	125	0	field_nullif	0	North Adams
7467	7	125	0	field_length	-1	\N
7468	7	125	0	field_precision	-1	\N
7469	7	125	0	cluster_schema	0	\N
7470	7	126	0	PARTITIONING_SCHEMA	0	\N
7471	7	126	0	PARTITIONING_METHOD	0	none
7472	7	126	0	cluster_schema	0	\N
7473	7	127	0	PARTITIONING_SCHEMA	0	\N
7474	7	127	0	PARTITIONING_METHOD	0	none
7475	7	127	0	schema	0	\N
7476	7	127	0	table	0	provider_dim
7477	7	127	0	id_connection	5	\N
7478	7	127	0	commit	100	\N
7479	7	127	0	update	0	Y
7480	7	127	0	lookup_key_name	0	ext_physician_id
7481	7	127	0	lookup_key_field	0	ext_physician_id
7482	7	127	1	lookup_key_name	0	ext_emr_system
7483	7	127	1	lookup_key_field	0	ext_emr_system
7484	7	127	0	date_name	0	\N
7485	7	127	0	date_from	0	date_from
7486	7	127	0	date_to	0	date_to
7487	7	127	0	field_name	0	last_name
7488	7	127	0	field_lookup	0	last_name
7489	7	127	0	field_update	0	Insert
7490	7	127	1	field_name	0	first_name
7491	7	127	1	field_lookup	0	first_name
7492	7	127	1	field_update	0	Insert
7493	7	127	2	field_name	0	middle_name
7494	7	127	2	field_lookup	0	middle_name
7495	7	127	2	field_update	0	Insert
7496	7	127	3	field_name	0	title
7497	7	127	3	field_lookup	0	title
7498	7	127	3	field_update	0	Insert
7499	7	127	4	field_name	0	dept_id
7500	7	127	4	field_lookup	0	dept_id
7501	7	127	4	field_update	0	Insert
7502	7	127	5	field_name	0	dept_name
7503	7	127	5	field_lookup	0	dept_name
7504	7	127	5	field_update	0	Insert
7505	7	127	6	field_name	0	dept_address_1
7506	7	127	6	field_lookup	0	dept_address_1
7507	7	127	6	field_update	0	Insert
7508	7	127	7	field_name	0	dept_address_2
7509	7	127	7	field_lookup	0	dept_address_2
7510	7	127	7	field_update	0	Insert
7511	7	127	8	field_name	0	dept_city
7512	7	127	8	field_lookup	0	dept_city
7513	7	127	8	field_update	0	Insert
7514	7	127	9	field_name	0	dept_state
7515	7	127	9	field_lookup	0	dept_state
7516	7	127	9	field_update	0	Insert
7517	7	127	10	field_name	0	dept_zip
7518	7	127	10	field_lookup	0	dept_zip
7519	7	127	10	field_update	0	Insert
7520	7	127	11	field_name	0	tel_area_code
7521	7	127	11	field_lookup	0	tel_area_code
7522	7	127	11	field_update	0	Insert
7523	7	127	12	field_name	0	tel
7524	7	127	12	field_lookup	0	tel
7525	7	127	12	field_update	0	Insert
7526	7	127	0	return_name	0	provider_id
7527	7	127	0	return_rename	0	\N
7528	7	127	0	creation_method	0	sequence
7529	7	127	0	use_autoinc	0	N
7530	7	127	0	version_field	0	version
7531	7	127	0	sequence	0	provider_dim_provider_id_seq
7532	7	127	0	min_year	1900	\N
7533	7	127	0	max_year	2199	\N
7534	7	127	0	cache_size	5000	\N
7535	7	127	0	cluster_schema	0	\N
7536	7	128	0	PARTITIONING_SCHEMA	0	\N
7537	7	128	0	PARTITIONING_METHOD	0	none
7538	7	128	0	id_condition	2	\N
7539	7	128	0	send_true_to	0	Lookup/update Provider dimension
7540	7	128	0	send_false_to	0	Discard records w/o physician code
7541	7	128	0	cluster_schema	0	\N
7542	7	129	0	PARTITIONING_SCHEMA	0	\N
7543	7	129	0	PARTITIONING_METHOD	0	none
7544	7	129	0	filename	0	/home/rejmv/work/new-esp/src/esp/test_data/provider.hvma.txt
7545	7	129	0	filename_field	0	\N
7546	7	129	0	rownum_field	0	\N
7547	7	129	0	include_filename	0	N
7548	7	129	0	separator	0	^
7549	7	129	0	enclosure	0	"
7550	7	129	0	buffer_size	0	50000
7551	7	129	0	header	0	N
7552	7	129	0	lazy_conversion	0	N
7553	7	129	0	add_filename_result	0	N
7554	7	129	0	parallel	0	N
7555	7	129	0	encoding	0	\N
7556	7	129	0	field_name	0	ext_physician_id
7557	7	129	0	field_type	0	String
7558	7	129	0	field_format	0	\N
7559	7	129	0	field_currency	0	\N
7560	7	129	0	field_decimal	0	\N
7561	7	129	0	field_group	0	\N
7562	7	129	0	field_length	-1	\N
7563	7	129	0	field_precision	-1	\N
7564	7	129	0	field_trim_type	0	none
7565	7	129	1	field_name	0	last_name
7566	7	129	1	field_type	0	String
7567	7	129	1	field_format	0	\N
7568	7	129	1	field_currency	0	\N
7569	7	129	1	field_decimal	0	\N
7570	7	129	1	field_group	0	\N
7571	7	129	1	field_length	-1	\N
7572	7	129	1	field_precision	-1	\N
7573	7	129	1	field_trim_type	0	none
7574	7	129	2	field_name	0	first_name
7575	7	129	2	field_type	0	String
7576	7	129	2	field_format	0	\N
7577	7	129	2	field_currency	0	\N
7578	7	129	2	field_decimal	0	\N
7579	7	129	2	field_group	0	\N
7580	7	129	2	field_length	-1	\N
7581	7	129	2	field_precision	-1	\N
7582	7	129	2	field_trim_type	0	none
7583	7	129	3	field_name	0	middle_name
7584	7	129	3	field_type	0	String
7585	7	129	3	field_format	0	\N
7586	7	129	3	field_currency	0	\N
7587	7	129	3	field_decimal	0	\N
7588	7	129	3	field_group	0	\N
7589	7	129	3	field_length	-1	\N
7590	7	129	3	field_precision	-1	\N
7591	7	129	3	field_trim_type	0	none
7592	7	129	4	field_name	0	title
7593	7	129	4	field_type	0	String
7594	7	129	4	field_format	0	\N
7595	7	129	4	field_currency	0	\N
7596	7	129	4	field_decimal	0	\N
7597	7	129	4	field_group	0	\N
7598	7	129	4	field_length	-1	\N
7599	7	129	4	field_precision	-1	\N
7600	7	129	4	field_trim_type	0	none
7601	7	129	5	field_name	0	dept_id
7602	7	129	5	field_type	0	String
7603	7	129	5	field_format	0	\N
7604	7	129	5	field_currency	0	\N
7605	7	129	5	field_decimal	0	\N
7606	7	129	5	field_group	0	\N
7607	7	129	5	field_length	-1	\N
7608	7	129	5	field_precision	-1	\N
7609	7	129	5	field_trim_type	0	none
7610	7	129	6	field_name	0	dept_name
7611	7	129	6	field_type	0	String
7612	7	129	6	field_format	0	\N
7613	7	129	6	field_currency	0	\N
7614	7	129	6	field_decimal	0	\N
7615	7	129	6	field_group	0	\N
7616	7	129	6	field_length	-1	\N
7617	7	129	6	field_precision	-1	\N
7618	7	129	6	field_trim_type	0	none
7619	7	129	7	field_name	0	dept_address_1
7620	7	129	7	field_type	0	String
7621	7	129	7	field_format	0	\N
7622	7	129	7	field_currency	0	\N
7623	7	129	7	field_decimal	0	\N
7624	7	129	7	field_group	0	\N
7625	7	129	7	field_length	-1	\N
7626	7	129	7	field_precision	-1	\N
7627	7	129	7	field_trim_type	0	none
7628	7	129	8	field_name	0	dept_address_2
7629	7	129	8	field_type	0	String
7630	7	129	8	field_format	0	\N
7631	7	129	8	field_currency	0	\N
7632	7	129	8	field_decimal	0	\N
7633	7	129	8	field_group	0	\N
7634	7	129	8	field_length	-1	\N
7635	7	129	8	field_precision	-1	\N
7636	7	129	8	field_trim_type	0	none
7637	7	129	9	field_name	0	dept_city
7638	7	129	9	field_type	0	String
7639	7	129	9	field_format	0	\N
7640	7	129	9	field_currency	0	\N
7641	7	129	9	field_decimal	0	\N
7642	7	129	9	field_group	0	\N
7643	7	129	9	field_length	-1	\N
7644	7	129	9	field_precision	-1	\N
7645	7	129	9	field_trim_type	0	none
7646	7	129	10	field_name	0	dept_state
7647	7	129	10	field_type	0	String
7648	7	129	10	field_format	0	\N
7649	7	129	10	field_currency	0	\N
7650	7	129	10	field_decimal	0	\N
7651	7	129	10	field_group	0	\N
7652	7	129	10	field_length	-1	\N
7653	7	129	10	field_precision	-1	\N
7654	7	129	10	field_trim_type	0	none
7655	7	129	11	field_name	0	dept_zip
7656	7	129	11	field_type	0	String
7657	7	129	11	field_format	0	\N
7658	7	129	11	field_currency	0	\N
7659	7	129	11	field_decimal	0	\N
7660	7	129	11	field_group	0	\N
7661	7	129	11	field_length	-1	\N
7662	7	129	11	field_precision	-1	\N
7663	7	129	11	field_trim_type	0	none
7664	7	129	12	field_name	0	tel_area_code
7665	7	129	12	field_type	0	String
7666	7	129	12	field_format	0	\N
7667	7	129	12	field_currency	0	\N
7668	7	129	12	field_decimal	0	\N
7669	7	129	12	field_group	0	\N
7670	7	129	12	field_length	-1	\N
7671	7	129	12	field_precision	-1	\N
7672	7	129	12	field_trim_type	0	none
7673	7	129	13	field_name	0	tel
7674	7	129	13	field_type	0	String
7675	7	129	13	field_format	0	\N
7676	7	129	13	field_currency	0	\N
7677	7	129	13	field_decimal	0	\N
7678	7	129	13	field_group	0	\N
7679	7	129	13	field_length	-1	\N
7680	7	129	13	field_precision	-1	\N
7681	7	129	13	field_trim_type	0	none
7682	7	129	0	cluster_schema	0	\N
15874	15	275	2	field_rename	0	property
15875	15	275	2	field_length	-1	\N
15876	15	275	2	field_precision	-1	\N
15877	15	275	3	field_name	0	TIME_ASPCT
15878	15	275	3	field_rename	0	time_aspct
15879	15	275	3	field_length	-1	\N
15880	15	275	3	field_precision	-1	\N
15881	15	275	4	field_name	0	SYSTEM
15882	15	275	4	field_rename	0	system
15883	15	275	4	field_length	-1	\N
15884	15	275	4	field_precision	-1	\N
15885	15	275	5	field_name	0	SCALE_TYP
15886	15	275	5	field_rename	0	scale_typ
15887	15	275	5	field_length	-1	\N
15888	15	275	5	field_precision	-1	\N
15889	15	275	6	field_name	0	METHOD_TYP
15890	15	275	6	field_rename	0	method_typ
15891	15	275	6	field_length	-1	\N
15892	15	275	6	field_precision	-1	\N
15893	15	275	7	field_name	0	RELAT_NMS
15894	15	275	7	field_rename	0	relat_nms
15895	15	275	7	field_length	-1	\N
15896	15	275	7	field_precision	-1	\N
15897	15	275	8	field_name	0	CLASS
15898	15	275	8	field_rename	0	loinc_class_field
15899	15	275	8	field_length	-1	\N
15900	15	275	8	field_precision	-1	\N
15901	15	275	9	field_name	0	SOURCE
15902	15	275	9	field_rename	0	source
15903	15	275	9	field_length	-1	\N
15904	15	275	9	field_precision	-1	\N
15905	15	275	10	field_name	0	DT_LAST_CH
15906	15	275	10	field_rename	0	dt_last_ch
15907	15	275	10	field_length	-1	\N
15908	15	275	10	field_precision	-1	\N
15909	15	275	11	field_name	0	CHNG_TYPE
15910	15	275	11	field_rename	0	chng_type
15911	15	275	11	field_length	-1	\N
15912	15	275	11	field_precision	-1	\N
15913	15	275	12	field_name	0	COMMENTS
15914	15	275	12	field_rename	0	comments
15915	15	275	12	field_length	-1	\N
15916	15	275	12	field_precision	-1	\N
15917	15	275	13	field_name	0	ANSWERLIST
15918	15	275	13	field_rename	0	answerlist
15919	15	275	13	field_length	-1	\N
15920	15	275	13	field_precision	-1	\N
15921	15	275	14	field_name	0	STATUS
15922	15	275	14	field_rename	0	status
15923	15	275	14	field_length	-1	\N
15924	15	275	14	field_precision	-1	\N
15925	15	275	15	field_name	0	MAP_TO
15926	15	275	15	field_rename	0	map_to
15927	15	275	15	field_length	-1	\N
15928	15	275	15	field_precision	-1	\N
15929	15	275	16	field_name	0	SCOPE
15930	15	275	16	field_rename	0	scope
15931	15	275	16	field_length	-1	\N
15932	15	275	16	field_precision	-1	\N
15933	15	275	17	field_name	0	NORM_RANGE
15934	15	275	17	field_rename	0	norm_range
15935	15	275	17	field_length	-1	\N
15936	15	275	17	field_precision	-1	\N
15937	15	275	18	field_name	0	IPCC_UNITS
15938	15	275	18	field_rename	0	ipcc_units
15939	15	275	18	field_length	-1	\N
15940	15	275	18	field_precision	-1	\N
15941	15	275	19	field_name	0	REFERENCE
15942	15	275	19	field_rename	0	reference
15943	15	275	19	field_length	-1	\N
15944	15	275	19	field_precision	-1	\N
15945	15	275	20	field_name	0	EXACT_CMP_SY
15946	15	275	20	field_rename	0	exact_cmp_sy
15947	15	275	20	field_length	-1	\N
15948	15	275	20	field_precision	-1	\N
15949	15	275	21	field_name	0	MOLAR_MASS
15950	15	275	21	field_rename	0	molar_mass
15951	15	275	21	field_length	-1	\N
15952	15	275	21	field_precision	-1	\N
15953	15	275	22	field_name	0	CLASSTYPE
15954	15	275	22	field_rename	0	classtype
15955	15	275	22	field_length	-1	\N
15956	15	275	22	field_precision	-1	\N
15957	15	275	23	field_name	0	FORMULA
15958	15	275	23	field_rename	0	formula
15959	15	275	23	field_length	-1	\N
15960	15	275	23	field_precision	-1	\N
15961	15	275	24	field_name	0	SPECIES
15962	15	275	24	field_rename	0	species
15963	15	275	24	field_length	-1	\N
15964	15	275	24	field_precision	-1	\N
15965	15	275	25	field_name	0	EXMPL_ANSWERS
15966	15	275	25	field_rename	0	exmpl_answers
15967	15	275	25	field_length	-1	\N
15968	15	275	25	field_precision	-1	\N
15969	15	275	26	field_name	0	ACSSYM
15970	15	275	26	field_rename	0	acssym
15971	15	275	26	field_length	-1	\N
15972	15	275	26	field_precision	-1	\N
15973	15	275	27	field_name	0	BASE_NAME
15974	15	275	27	field_rename	0	base_name
15975	15	275	27	field_length	-1	\N
15976	15	275	27	field_precision	-1	\N
15977	15	275	28	field_name	0	FINAL
15978	15	275	28	field_rename	0	final
15979	15	275	28	field_length	-1	\N
15980	15	275	28	field_precision	-1	\N
15981	15	275	29	field_name	0	NAACCR_ID
15982	15	275	29	field_rename	0	naaccr_id
15983	15	275	29	field_length	-1	\N
15984	15	275	29	field_precision	-1	\N
15985	15	275	30	field_name	0	CODE_TABLE
15986	15	275	30	field_rename	0	code_table
15987	15	275	30	field_length	-1	\N
15988	15	275	30	field_precision	-1	\N
15989	15	275	31	field_name	0	SETROOT
15990	15	275	31	field_rename	0	setroot
15991	15	275	31	field_length	-1	\N
15992	15	275	31	field_precision	-1	\N
15993	15	275	32	field_name	0	PANELELEMENTS
15994	15	275	32	field_rename	0	panelelements
15995	15	275	32	field_length	-1	\N
15996	15	275	32	field_precision	-1	\N
15997	15	275	33	field_name	0	SURVEY_QUEST_TEXT
15998	15	275	33	field_rename	0	survey_quest_text
15999	15	275	33	field_length	-1	\N
16000	15	275	33	field_precision	-1	\N
16001	15	275	34	field_name	0	SURVEY_QUEST_SRC
16002	15	275	34	field_rename	0	survey_quest_src
16003	15	275	34	field_length	-1	\N
16004	15	275	34	field_precision	-1	\N
16005	15	275	35	field_name	0	UNITSREQUIRED
16006	15	275	35	field_rename	0	unitsrequired
16007	15	275	35	field_length	-1	\N
16008	15	275	35	field_precision	-1	\N
16009	15	275	36	field_name	0	SUBMITTED_UNITS
16010	15	275	36	field_rename	0	submitted_units
16011	15	275	36	field_length	-1	\N
16012	15	275	36	field_precision	-1	\N
16013	15	275	37	field_name	0	RELATEDNAMES2
16014	15	275	37	field_rename	0	relatednames2
16015	15	275	37	field_length	-1	\N
16016	15	275	37	field_precision	-1	\N
16017	15	275	38	field_name	0	SHORTNAME
16018	15	275	38	field_rename	0	shortname
16019	15	275	38	field_length	-1	\N
16020	15	275	38	field_precision	-1	\N
16021	15	275	39	field_name	0	ORDER_OBS
16022	15	275	39	field_rename	0	order_obs
16023	15	275	39	field_length	-1	\N
16024	15	275	39	field_precision	-1	\N
16025	15	275	40	field_name	0	CDISC_COMMON_TESTS
16026	15	275	40	field_rename	0	cdisc_common_tests
16027	15	275	40	field_length	-1	\N
16028	15	275	40	field_precision	-1	\N
16029	15	275	41	field_name	0	HL7_FIELD_SUBFIELD_ID
16030	15	275	41	field_rename	0	hl7_field_subfield_id
16031	15	275	41	field_length	-1	\N
16032	15	275	41	field_precision	-1	\N
16033	15	275	42	field_name	0	EXTERNAL_COPYRIGHT_NOTICE
16034	15	275	42	field_rename	0	external_copyright_notice
16035	15	275	42	field_length	-1	\N
16036	15	275	42	field_precision	-1	\N
16037	15	275	43	field_name	0	EXAMPLE_UNITS
16038	15	275	43	field_rename	0	example_units
16039	15	275	43	field_length	-1	\N
16040	15	275	43	field_precision	-1	\N
16041	15	275	44	field_name	0	INPC_PERCENTAGE
16042	15	275	44	field_rename	0	inpc_percentage
16043	15	275	44	field_length	-1	\N
16044	15	275	44	field_precision	-1	\N
16045	15	275	45	field_name	0	LONG_COMMON_NAME
16046	15	275	45	field_rename	0	long_common_name
16047	15	275	45	field_length	-1	\N
16048	15	275	45	field_precision	-1	\N
16049	15	275	0	select_unspecified	0	N
16050	15	275	0	cluster_schema	0	\N
16051	15	276	0	PARTITIONING_SCHEMA	0	\N
16052	15	276	0	PARTITIONING_METHOD	0	none
16053	15	276	0	id_connection	6	\N
16054	15	276	0	schema	0	\N
16055	15	276	0	table	0	esp_loinc
16056	15	276	0	commit	1000	\N
16057	15	276	0	truncate	0	Y
16058	15	276	0	ignore_errors	0	N
16059	15	276	0	use_batch	0	Y
16060	15	276	0	partitioning_enabled	0	N
16061	15	276	0	partitioning_field	0	\N
16062	15	276	0	partitioning_daily	0	N
16063	15	276	0	partitioning_monthly	0	Y
16064	15	276	0	tablename_in_field	0	N
16065	15	276	0	tablename_field	0	\N
16066	15	276	0	tablename_in_table	0	Y
16067	15	276	0	return_keys	0	N
16068	15	276	0	return_field	0	\N
16069	15	276	0	cluster_schema	0	\N
14817	13	269	0	PARTITIONING_SCHEMA	0	\N
14818	13	269	0	PARTITIONING_METHOD	0	none
14819	13	269	0	filename	0	\N
14820	13	269	0	trans_name	0	Add Stock Variables
14821	13	269	0	directory_path	0	/esp/load
14822	13	269	0	cluster_schema	0	\N
14823	13	270	0	PARTITIONING_SCHEMA	0	\N
14824	13	270	0	PARTITIONING_METHOD	0	none
14825	13	270	0	id_connection	7	\N
14826	13	270	0	commit	1000	\N
14827	13	270	0	schema	0	\N
14828	13	270	0	table	0	core_patient
14829	13	270	0	update_bypassed	0	N
14830	13	270	0	key_name	0	ext_patient_id
14831	13	270	0	key_field	0	ext_patient_id
14832	13	270	0	key_condition	0	=
14833	13	270	0	key_name2	0	\N
14834	13	270	1	key_name	0	emr_id
14835	13	270	1	key_field	0	emr_id
14836	13	270	1	key_condition	0	=
14837	13	270	1	key_name2	0	\N
14838	13	270	0	value_name	0	ext_patient_id
14839	13	270	0	value_rename	0	ext_patient_id
14840	13	270	0	value_update	0	Y
14841	13	270	1	value_name	0	ext_medical_record_num
14842	13	270	1	value_rename	0	ext_medical_record_num
14843	13	270	1	value_update	0	Y
14844	13	270	2	value_name	0	last_name
14845	13	270	2	value_rename	0	last_name
14846	13	270	2	value_update	0	Y
14847	13	270	3	value_name	0	first_name
14848	13	270	3	value_rename	0	first_name
14849	13	270	3	value_update	0	Y
14850	13	270	4	value_name	0	middle_name
14851	13	270	4	value_rename	0	middle_name
9368	12	172	0	PARTITIONING_SCHEMA	0	\N
9369	12	172	0	PARTITIONING_METHOD	0	none
9370	12	172	0	filename	0	/home/rejmv/work/new-esp/src/esp/test_data/epicmem.esp.02032009
9371	12	172	0	filename_field	0	\N
9372	12	172	0	rownum_field	0	row_num
9373	12	172	0	include_filename	0	N
9374	12	172	0	separator	0	^
9375	12	172	0	enclosure	0	"
9376	12	172	0	buffer_size	0	50000
9377	12	172	0	header	0	N
9378	12	172	0	lazy_conversion	0	N
9379	12	172	0	add_filename_result	0	N
9380	12	172	0	parallel	0	N
9381	12	172	0	encoding	0	\N
9382	12	172	0	field_name	0	patient_id
9383	12	172	0	field_type	0	String
9384	12	172	0	field_format	0	\N
9385	12	172	0	field_currency	0	\N
9386	12	172	0	field_decimal	0	\N
9387	12	172	0	field_group	0	\N
9388	12	172	0	field_length	-1	\N
9389	12	172	0	field_precision	-1	\N
9390	12	172	0	field_trim_type	0	none
9391	12	172	1	field_name	0	medical_record_num
9392	12	172	1	field_type	0	String
9393	12	172	1	field_format	0	\N
9394	12	172	1	field_currency	0	\N
9395	12	172	1	field_decimal	0	\N
9396	12	172	1	field_group	0	\N
9397	12	172	1	field_length	-1	\N
9398	12	172	1	field_precision	-1	\N
9399	12	172	1	field_trim_type	0	none
9400	12	172	2	field_name	0	last_name
9401	12	172	2	field_type	0	String
9402	12	172	2	field_format	0	\N
9403	12	172	2	field_currency	0	\N
9404	12	172	2	field_decimal	0	\N
8453	11	148	0	PARTITIONING_SCHEMA	0	\N
8454	11	148	0	PARTITIONING_METHOD	0	none
8455	11	148	0	valuename	0	id
8456	11	148	0	use_database	0	N
8457	11	148	0	id_connection	1	\N
8458	11	148	0	schema	0	\N
8459	11	148	0	seqname	0	SEQ_
8460	11	148	0	use_counter	0	Y
8461	11	148	0	counter_name	0	\N
8462	11	148	0	start_at	0	1
8463	11	148	0	increment_by	0	1
8464	11	148	0	max_value	0	999999999
8465	11	148	0	cluster_schema	0	\N
8466	11	149	0	PARTITIONING_SCHEMA	0	\N
8467	11	149	0	PARTITIONING_METHOD	0	none
8468	11	149	0	filename	0	/home/rejmv/work/new-esp/src/esp/test_data/north-adams.loinc-map.csv
8469	11	149	0	filename_field	0	\N
8470	11	149	0	rownum_field	0	\N
8471	11	149	0	include_filename	0	N
8472	11	149	0	separator	0	\t
8473	11	149	0	enclosure	0	"
8474	11	149	0	buffer_size	0	50000
8475	11	149	0	header	0	Y
8476	11	149	0	lazy_conversion	0	Y
8477	11	149	0	add_filename_result	0	N
8478	11	149	0	parallel	0	N
8479	11	149	0	encoding	0	\N
8480	11	149	0	field_name	0	Dept
8481	11	149	0	field_type	0	String
8482	11	149	0	field_format	0	\N
8483	11	149	0	field_currency	0	\N
8484	11	149	0	field_decimal	0	\N
8485	11	149	0	field_group	0	\N
8486	11	149	0	field_length	5	\N
8487	11	149	0	field_precision	-1	\N
8488	11	149	0	field_trim_type	0	none
8489	11	149	1	field_name	0	AttrCode
8490	11	149	1	field_type	0	String
8491	11	149	1	field_format	0	\N
8492	11	149	1	field_currency	0	\N
8493	11	149	1	field_decimal	0	\N
8494	11	149	1	field_group	0	\N
8495	11	149	1	field_length	9	\N
8496	11	149	1	field_precision	-1	\N
8497	11	149	1	field_trim_type	0	none
8498	11	149	2	field_name	0	AttrMnemonic
8499	11	149	2	field_type	0	String
8500	11	149	2	field_format	0	\N
8501	11	149	2	field_currency	0	\N
8502	11	149	2	field_decimal	0	\N
8503	11	149	2	field_group	0	\N
8504	11	149	2	field_length	14	\N
8505	11	149	2	field_precision	-1	\N
8506	11	149	2	field_trim_type	0	none
8507	11	149	3	field_name	0	AttrName
8508	11	149	3	field_type	0	String
8509	11	149	3	field_format	0	\N
8510	11	149	3	field_currency	0	\N
8511	11	149	3	field_decimal	0	\N
8512	11	149	3	field_group	0	\N
8513	11	149	3	field_length	32	\N
8514	11	149	3	field_precision	-1	\N
8515	11	149	3	field_trim_type	0	right
8516	11	149	4	field_name	0	LOINC
8517	11	149	4	field_type	0	String
8518	11	149	4	field_format	0	\N
9405	12	172	2	field_group	0	\N
8519	11	149	4	field_currency	0	\N
8520	11	149	4	field_decimal	0	\N
8521	11	149	4	field_group	0	\N
8522	11	149	4	field_length	77	\N
8523	11	149	4	field_precision	-1	\N
8524	11	149	4	field_trim_type	0	none
8525	11	149	5	field_name	0	LOINC Name
8526	11	149	5	field_type	0	String
8527	11	149	5	field_format	0	\N
8528	11	149	5	field_currency	0	\N
8529	11	149	5	field_decimal	0	\N
8530	11	149	5	field_group	0	\N
8531	11	149	5	field_length	92	\N
8532	11	149	5	field_precision	-1	\N
8533	11	149	5	field_trim_type	0	right
8534	11	149	0	cluster_schema	0	\N
8535	11	150	0	PARTITIONING_SCHEMA	0	\N
8536	11	150	0	PARTITIONING_METHOD	0	none
8537	11	150	0	field_name	0	id
8538	11	150	0	field_rename	0	\N
8539	11	150	0	field_length	-2	\N
8540	11	150	0	field_precision	-2	\N
8541	11	150	1	field_name	0	AttrCode
8542	11	150	1	field_rename	0	ext_code
8543	11	150	1	field_length	-2	\N
8544	11	150	1	field_precision	-2	\N
8545	11	150	2	field_name	0	AttrName
8546	11	150	2	field_rename	0	ext_name
8547	11	150	2	field_length	-2	\N
8548	11	150	2	field_precision	-2	\N
8549	11	150	3	field_name	0	LOINC
8550	11	150	3	field_rename	0	loinc_code
8551	11	150	3	field_length	-2	\N
8552	11	150	3	field_precision	-2	\N
8553	11	150	4	field_name	0	LOINC Name
8554	11	150	4	field_rename	0	loinc_name
8555	11	150	4	field_length	-2	\N
8556	11	150	4	field_precision	-2	\N
8557	11	150	0	select_unspecified	0	N
8558	11	150	0	cluster_schema	0	\N
8559	11	151	0	PARTITIONING_SCHEMA	0	\N
8560	11	151	0	PARTITIONING_METHOD	0	none
8561	11	151	0	directory	0	%%java.io.tmpdir%%
8562	11	151	0	prefix	0	out
8563	11	151	0	sort_size	0	\N
8564	11	151	0	free_memory	0	25
8565	11	151	0	compress	0	N
8566	11	151	0	compress_variable	0	\N
8567	11	151	0	unique_rows	0	N
8568	11	151	0	field_name	0	AttrCode
8569	11	151	0	field_ascending	0	Y
8570	11	151	0	field_case_sensitive	0	N
8571	11	151	0	cluster_schema	0	\N
8572	11	152	0	PARTITIONING_SCHEMA	0	\N
8573	11	152	0	PARTITIONING_METHOD	0	none
8574	11	152	0	count_rows	0	N
8575	11	152	0	count_fields	0	\N
8576	11	152	0	field_name	0	AttrCode
8577	11	152	0	case_insensitive	0	N
8578	11	152	0	cluster_schema	0	\N
8579	11	153	0	PARTITIONING_SCHEMA	0	\N
8580	11	153	0	PARTITIONING_METHOD	0	none
8581	11	153	0	id_connection	5	\N
8582	11	153	0	schema	0	\N
8583	11	153	0	table	0	ext_code_to_loinc
8584	11	153	0	commit	100	\N
8585	11	153	0	truncate	0	N
8586	11	153	0	ignore_errors	0	N
8587	11	153	0	use_batch	0	Y
8588	11	153	0	partitioning_enabled	0	N
8589	11	153	0	partitioning_field	0	\N
8590	11	153	0	partitioning_daily	0	N
8591	11	153	0	partitioning_monthly	0	Y
8592	11	153	0	tablename_in_field	0	N
8593	11	153	0	tablename_field	0	\N
8594	11	153	0	tablename_in_table	0	Y
8595	11	153	0	return_keys	0	N
8596	11	153	0	return_field	0	\N
8597	11	153	0	cluster_schema	0	\N
8598	9	154	0	PARTITIONING_SCHEMA	0	\N
8599	9	154	0	PARTITIONING_METHOD	0	none
8600	9	154	0	field_name	0	ext_emr_system
8601	9	154	0	field_type	0	String
8602	9	154	0	field_format	0	\N
8603	9	154	0	field_currency	0	\N
8604	9	154	0	field_decimal	0	\N
8605	9	154	0	field_group	0	\N
8606	9	154	0	field_nullif	0	North Adams
8607	9	154	0	field_length	-1	\N
8608	9	154	0	field_precision	-1	\N
8609	9	154	0	cluster_schema	0	\N
8610	9	155	0	PARTITIONING_SCHEMA	0	\N
8611	9	155	0	PARTITIONING_METHOD	0	none
8612	9	155	0	schema	0	\N
8613	9	155	0	table	0	impression_dim
8614	9	155	0	id_connection	5	\N
8615	9	155	0	commit	100	\N
8616	9	155	0	cache_size	9999	\N
8617	9	155	0	replace	0	N
8618	9	155	0	crc	0	N
8619	9	155	0	crcfield	0	hashcode
8620	9	155	0	lookup_key_name	0	impression
8621	9	155	0	lookup_key_field	0	impression
8622	9	155	1	lookup_key_name	0	test_id
8623	9	155	1	lookup_key_field	0	test_id
8624	9	155	0	return_name	0	impression_id
8625	9	155	0	sequence	0	\N
8626	9	155	0	creation_method	0	tablemax
8627	9	155	0	use_autoinc	0	N
8628	9	155	0	cluster_schema	0	\N
8629	9	156	0	PARTITIONING_SCHEMA	0	\N
8630	9	156	0	PARTITIONING_METHOD	0	none
8631	9	156	0	schema	0	\N
8632	9	156	0	table	0	order_dim
8633	9	156	0	id_connection	5	\N
8634	9	156	0	commit	100	\N
8635	9	156	0	update	0	Y
8636	9	156	0	lookup_key_name	0	ext_order_id
8637	9	156	0	lookup_key_field	0	ext_order_id
8638	9	156	1	lookup_key_name	0	ext_emr_system
8639	9	156	1	lookup_key_field	0	ext_emr_system
8640	9	156	0	date_name	0	\N
8641	9	156	0	date_from	0	date_from
8642	9	156	0	date_to	0	date_to
8643	9	156	0	return_name	0	order_id
8644	9	156	0	return_rename	0	\N
8645	9	156	0	creation_method	0	tablemax
8646	9	156	0	use_autoinc	0	N
8647	9	156	0	version_field	0	version
8648	9	156	0	sequence	0	\N
8649	9	156	0	min_year	1900	\N
8650	9	156	0	max_year	2199	\N
8651	9	156	0	cache_size	5000	\N
8652	9	156	0	cluster_schema	0	\N
8653	9	157	0	PARTITIONING_SCHEMA	0	\N
8654	9	157	0	PARTITIONING_METHOD	0	none
8655	9	157	0	schema	0	\N
8656	9	157	0	table	0	patient_dim
8657	9	157	0	id_connection	5	\N
8658	9	157	0	commit	100	\N
8659	9	157	0	update	0	Y
8660	9	157	0	lookup_key_name	0	ext_patient_id
8661	9	157	0	lookup_key_field	0	ext_patient_id
8662	9	157	1	lookup_key_name	0	ext_emr_system
8663	9	157	1	lookup_key_field	0	ext_emr_system
8664	9	157	0	date_name	0	\N
8665	9	157	0	date_from	0	date_from
8666	9	157	0	date_to	0	date_to
8667	9	157	0	return_name	0	patient_id
8668	9	157	0	return_rename	0	\N
8669	9	157	0	creation_method	0	sequence
8670	9	157	0	use_autoinc	0	N
8671	9	157	0	version_field	0	version
8672	9	157	0	sequence	0	patient_dim_patient_id_seq
8673	9	157	0	min_year	1900	\N
8674	9	157	0	max_year	2199	\N
8675	9	157	0	cache_size	5000	\N
8676	9	157	0	cluster_schema	0	\N
8677	9	158	0	PARTITIONING_SCHEMA	0	\N
8678	9	158	0	PARTITIONING_METHOD	0	none
8679	9	158	0	schema	0	\N
8680	9	158	0	table	0	provider_dim
8681	9	158	0	id_connection	5	\N
8682	9	158	0	commit	100	\N
8683	9	158	0	update	0	Y
8684	9	158	0	lookup_key_name	0	ext_physician_id
8685	9	158	0	lookup_key_field	0	ext_physician_id
8686	9	158	1	lookup_key_name	0	ext_emr_system
8687	9	158	1	lookup_key_field	0	ext_emr_system
8688	9	158	0	date_name	0	\N
8689	9	158	0	date_from	0	date_from
8690	9	158	0	date_to	0	date_to
8691	9	158	0	return_name	0	provider_id
8692	9	158	0	return_rename	0	\N
8693	9	158	0	creation_method	0	sequence
8694	9	158	0	use_autoinc	0	N
8695	9	158	0	version_field	0	version
8696	9	158	0	sequence	0	provider_dim_provider_id_seq
8697	9	158	0	min_year	1900	\N
8698	9	158	0	max_year	2199	\N
8699	9	158	0	cache_size	5000	\N
8700	9	158	0	cluster_schema	0	\N
8701	9	159	0	PARTITIONING_SCHEMA	0	\N
8702	9	159	0	PARTITIONING_METHOD	0	none
8703	9	159	0	schema	0	\N
8704	9	159	0	table	0	note_dim
8705	9	159	0	id_connection	5	\N
8706	9	159	0	commit	100	\N
8707	9	159	0	cache_size	9999	\N
8708	9	159	0	replace	0	N
8709	9	159	0	crc	0	N
8710	9	159	0	crcfield	0	hashcode
8711	9	159	0	lookup_key_name	0	notes
8712	9	159	0	lookup_key_field	0	notes
8713	9	159	1	lookup_key_name	0	test_id
8714	9	159	1	lookup_key_field	0	test_id
8715	9	159	0	return_name	0	note_id
8716	9	159	0	sequence	0	\N
8717	9	159	0	creation_method	0	tablemax
8718	9	159	0	use_autoinc	0	N
8719	9	159	0	cluster_schema	0	\N
8720	9	160	0	PARTITIONING_SCHEMA	0	\N
8721	9	160	0	PARTITIONING_METHOD	0	none
8722	9	160	0	schema	0	\N
8723	9	160	0	table	0	result_dim
8724	9	160	0	id_connection	5	\N
8725	9	160	0	commit	100	\N
8726	9	160	0	cache_size	9999	\N
8727	9	160	0	replace	0	N
8728	9	160	0	crc	0	N
8729	9	160	0	crcfield	0	hashcode
8730	9	160	0	lookup_key_name	0	result
8731	9	160	0	lookup_key_field	0	result
8732	9	160	1	lookup_key_name	0	test_id
8733	9	160	1	lookup_key_field	0	test_id
8734	9	160	0	return_name	0	result_id
8735	9	160	0	sequence	0	result_dim_result_id_seq
8736	9	160	0	creation_method	0	sequence
8737	9	160	0	use_autoinc	0	N
8738	9	160	0	cluster_schema	0	\N
8739	9	161	0	PARTITIONING_SCHEMA	0	\N
8740	9	161	0	PARTITIONING_METHOD	0	none
8741	9	161	0	schema	0	\N
8742	9	161	0	table	0	test_dim
8743	9	161	0	id_connection	5	\N
8744	9	161	0	commit	100	\N
8745	9	161	0	cache_size	9999	\N
8746	9	161	0	replace	0	N
8747	9	161	0	crc	0	N
8748	9	161	0	crcfield	0	hashcode
8749	9	161	0	lookup_key_name	0	ext_test_code
8750	9	161	0	lookup_key_field	0	ext_test_code
8751	9	161	1	lookup_key_name	0	ext_test_subcode
8752	9	161	1	lookup_key_field	0	ext_test_subcode
8753	9	161	2	lookup_key_name	0	ext_test_name
8754	9	161	2	lookup_key_field	0	ext_test_name
8755	9	161	3	lookup_key_name	0	ext_emr_system
8756	9	161	3	lookup_key_field	0	ext_emr_system
8757	9	161	0	return_name	0	test_id
8758	9	161	0	sequence	0	test_dim_test_id_seq
8759	9	161	0	creation_method	0	sequence
8760	9	161	0	use_autoinc	0	N
8761	9	161	0	cluster_schema	0	\N
8762	9	162	0	PARTITIONING_SCHEMA	0	\N
8763	9	162	0	PARTITIONING_METHOD	0	none
8764	9	162	0	filename	0	/home/rejmv/work/new-esp/src/esp/test_data/result.hvma.txt
8765	9	162	0	filename_field	0	\N
8766	9	162	0	rownum_field	0	\N
8767	9	162	0	include_filename	0	N
8768	9	162	0	separator	0	^
8769	9	162	0	enclosure	0	"
8770	9	162	0	buffer_size	0	50000
8771	9	162	0	header	0	N
8772	9	162	0	lazy_conversion	0	N
8773	9	162	0	add_filename_result	0	N
8774	9	162	0	parallel	0	N
8775	9	162	0	encoding	0	\N
8776	9	162	0	field_name	0	ext_patient_id
8777	9	162	0	field_type	0	String
8778	9	162	0	field_format	0	\N
8779	9	162	0	field_currency	0	\N
8780	9	162	0	field_decimal	0	\N
8781	9	162	0	field_group	0	\N
8782	9	162	0	field_length	-1	\N
8783	9	162	0	field_precision	-1	\N
8784	9	162	0	field_trim_type	0	none
8785	9	162	1	field_name	0	medical_record_num
8786	9	162	1	field_type	0	String
8787	9	162	1	field_format	0	\N
8788	9	162	1	field_currency	0	\N
8789	9	162	1	field_decimal	0	\N
8790	9	162	1	field_group	0	\N
8791	9	162	1	field_length	-1	\N
8792	9	162	1	field_precision	-1	\N
8793	9	162	1	field_trim_type	0	none
8794	9	162	2	field_name	0	ext_order_id
8795	9	162	2	field_type	0	String
8796	9	162	2	field_format	0	\N
8797	9	162	2	field_currency	0	\N
8798	9	162	2	field_decimal	0	\N
8799	9	162	2	field_group	0	\N
8800	9	162	2	field_length	-1	\N
8801	9	162	2	field_precision	-1	\N
8802	9	162	2	field_trim_type	0	none
8803	9	162	3	field_name	0	order_date
8804	9	162	3	field_type	0	Date
8805	9	162	3	field_format	0	yyyyMMdd
8806	9	162	3	field_currency	0	\N
8807	9	162	3	field_decimal	0	\N
8808	9	162	3	field_group	0	\N
8809	9	162	3	field_length	-1	\N
8810	9	162	3	field_precision	-1	\N
8811	9	162	3	field_trim_type	0	none
8812	9	162	4	field_name	0	result_date
8813	9	162	4	field_type	0	Date
8814	9	162	4	field_format	0	yyyyMMdd
8815	9	162	4	field_currency	0	\N
8816	9	162	4	field_decimal	0	\N
8817	9	162	4	field_group	0	\N
8818	9	162	4	field_length	-1	\N
8819	9	162	4	field_precision	-1	\N
8820	9	162	4	field_trim_type	0	none
8821	9	162	5	field_name	0	ext_physician_id
8822	9	162	5	field_type	0	String
8823	9	162	5	field_format	0	\N
8824	9	162	5	field_currency	0	\N
8825	9	162	5	field_decimal	0	\N
8826	9	162	5	field_group	0	\N
8827	9	162	5	field_length	-1	\N
8828	9	162	5	field_precision	-1	\N
8829	9	162	5	field_trim_type	0	none
8830	9	162	6	field_name	0	order_type
8831	9	162	6	field_type	0	String
8832	9	162	6	field_format	0	\N
8833	9	162	6	field_currency	0	\N
8834	9	162	6	field_decimal	0	\N
8835	9	162	6	field_group	0	\N
8836	9	162	6	field_length	-1	\N
8837	9	162	6	field_precision	-1	\N
8838	9	162	6	field_trim_type	0	none
8839	9	162	7	field_name	0	ext_test_code
8840	9	162	7	field_type	0	String
8841	9	162	7	field_format	0	\N
8842	9	162	7	field_currency	0	\N
8843	9	162	7	field_decimal	0	\N
8844	9	162	7	field_group	0	\N
8845	9	162	7	field_length	-1	\N
8846	9	162	7	field_precision	-1	\N
8847	9	162	7	field_trim_type	0	none
8848	9	162	8	field_name	0	ext_test_subcode
8849	9	162	8	field_type	0	String
8850	9	162	8	field_format	0	\N
8851	9	162	8	field_currency	0	\N
8852	9	162	8	field_decimal	0	\N
8853	9	162	8	field_group	0	\N
8854	9	162	8	field_length	-1	\N
8855	9	162	8	field_precision	-1	\N
8856	9	162	8	field_trim_type	0	none
8857	9	162	9	field_name	0	ext_test_name
8858	9	162	9	field_type	0	String
8859	9	162	9	field_format	0	\N
8860	9	162	9	field_currency	0	\N
8861	9	162	9	field_decimal	0	\N
8862	9	162	9	field_group	0	\N
8863	9	162	9	field_length	-1	\N
8864	9	162	9	field_precision	-1	\N
8865	9	162	9	field_trim_type	0	none
8866	9	162	10	field_name	0	result
8867	9	162	10	field_type	0	String
8868	9	162	10	field_format	0	\N
8869	9	162	10	field_currency	0	\N
8870	9	162	10	field_decimal	0	\N
8871	9	162	10	field_group	0	\N
8872	9	162	10	field_length	-1	\N
8873	9	162	10	field_precision	-1	\N
8874	9	162	10	field_trim_type	0	none
8875	9	162	11	field_name	0	normal_flag
8876	9	162	11	field_type	0	String
8877	9	162	11	field_format	0	\N
8878	9	162	11	field_currency	0	\N
8879	9	162	11	field_decimal	0	\N
8880	9	162	11	field_group	0	\N
8881	9	162	11	field_length	-1	\N
8882	9	162	11	field_precision	-1	\N
8883	9	162	11	field_trim_type	0	none
8884	9	162	12	field_name	0	reference_low
8885	9	162	12	field_type	0	String
8886	9	162	12	field_format	0	\N
8887	9	162	12	field_currency	0	\N
8888	9	162	12	field_decimal	0	\N
8889	9	162	12	field_group	0	\N
8890	9	162	12	field_length	-1	\N
8891	9	162	12	field_precision	-1	\N
8892	9	162	12	field_trim_type	0	none
8893	9	162	13	field_name	0	reference_high
8894	9	162	13	field_type	0	String
8895	9	162	13	field_format	0	\N
8896	9	162	13	field_currency	0	\N
8897	9	162	13	field_decimal	0	\N
8898	9	162	13	field_group	0	\N
8899	9	162	13	field_length	-1	\N
8900	9	162	13	field_precision	-1	\N
8901	9	162	13	field_trim_type	0	none
8902	9	162	14	field_name	0	reference_units
8903	9	162	14	field_type	0	String
8904	9	162	14	field_format	0	\N
8905	9	162	14	field_currency	0	\N
8906	9	162	14	field_decimal	0	\N
8907	9	162	14	field_group	0	\N
8908	9	162	14	field_length	-1	\N
8909	9	162	14	field_precision	-1	\N
8910	9	162	14	field_trim_type	0	none
8911	9	162	15	field_name	0	status
8912	9	162	15	field_type	0	String
8913	9	162	15	field_format	0	\N
8914	9	162	15	field_currency	0	\N
8915	9	162	15	field_decimal	0	\N
8916	9	162	15	field_group	0	\N
8917	9	162	15	field_length	-1	\N
8918	9	162	15	field_precision	-1	\N
8919	9	162	15	field_trim_type	0	none
8920	9	162	16	field_name	0	notes
8921	9	162	16	field_type	0	String
8922	9	162	16	field_format	0	\N
8923	9	162	16	field_currency	0	\N
8924	9	162	16	field_decimal	0	\N
8925	9	162	16	field_group	0	\N
8926	9	162	16	field_length	-1	\N
8927	9	162	16	field_precision	-1	\N
8928	9	162	16	field_trim_type	0	none
8929	9	162	17	field_name	0	accessnum
8930	9	162	17	field_type	0	String
8931	9	162	17	field_format	0	\N
8932	9	162	17	field_currency	0	\N
8933	9	162	17	field_decimal	0	\N
8934	9	162	17	field_group	0	\N
8935	9	162	17	field_length	-1	\N
8936	9	162	17	field_precision	-1	\N
8937	9	162	17	field_trim_type	0	none
8938	9	162	18	field_name	0	impression
8939	9	162	18	field_type	0	String
8940	9	162	18	field_format	0	\N
8941	9	162	18	field_currency	0	\N
8942	9	162	18	field_decimal	0	\N
8943	9	162	18	field_group	0	\N
8944	9	162	18	field_length	-1	\N
8945	9	162	18	field_precision	-1	\N
8946	9	162	18	field_trim_type	0	none
8947	9	162	0	cluster_schema	0	\N
8948	9	163	0	PARTITIONING_SCHEMA	0	\N
8949	9	163	0	PARTITIONING_METHOD	0	none
8950	9	163	0	field_name	0	ext_emr_system
8951	9	163	0	field_rename	0	\N
8952	9	163	0	field_length	-2	\N
8953	9	163	0	field_precision	-2	\N
8954	9	163	1	field_name	0	order_date_id
8955	9	163	1	field_rename	0	\N
8956	9	163	1	field_length	-2	\N
8957	9	163	1	field_precision	-2	\N
8958	9	163	2	field_name	0	result_date_id
8959	9	163	2	field_rename	0	\N
8960	9	163	2	field_length	-2	\N
8961	9	163	2	field_precision	-2	\N
8962	9	163	3	field_name	0	provider_id
8963	9	163	3	field_rename	0	\N
8964	9	163	3	field_length	-2	\N
8965	9	163	3	field_precision	-2	\N
8966	9	163	4	field_name	0	patient_id
8967	9	163	4	field_rename	0	\N
8968	9	163	4	field_length	-2	\N
8969	9	163	4	field_precision	-2	\N
8970	9	163	5	field_name	0	order_id
8971	9	163	5	field_rename	0	\N
8972	9	163	5	field_length	-2	\N
8973	9	163	5	field_precision	-2	\N
8974	9	163	6	field_name	0	test_id
8975	9	163	6	field_rename	0	\N
8976	9	163	6	field_length	-2	\N
8977	9	163	6	field_precision	-2	\N
8978	9	163	7	field_name	0	result_id
8979	9	163	7	field_rename	0	\N
8980	9	163	7	field_length	-2	\N
8981	9	163	7	field_precision	-2	\N
8982	9	163	8	field_name	0	note_id
8983	9	163	8	field_rename	0	\N
8984	9	163	8	field_length	-2	\N
8985	9	163	8	field_precision	-2	\N
8986	9	163	9	field_name	0	impression_id
8987	9	163	9	field_rename	0	\N
8988	9	163	9	field_length	-2	\N
8989	9	163	9	field_precision	-2	\N
8990	9	163	10	field_name	0	medical_record_id
8991	9	163	10	field_rename	0	\N
8992	9	163	10	field_length	-2	\N
8993	9	163	10	field_precision	-2	\N
8994	9	163	0	select_unspecified	0	N
8995	9	163	0	cluster_schema	0	\N
8996	9	164	0	PARTITIONING_SCHEMA	0	\N
8997	9	164	0	PARTITIONING_METHOD	0	none
8998	9	164	0	id_connection	5	\N
8999	9	164	0	schema	0	\N
9000	9	164	0	table	0	lab_result
9001	9	164	0	commit	100	\N
9002	9	164	0	truncate	0	N
9003	9	164	0	ignore_errors	0	N
9004	9	164	0	use_batch	0	Y
9005	9	164	0	partitioning_enabled	0	N
9006	9	164	0	partitioning_field	0	\N
9007	9	164	0	partitioning_daily	0	N
9008	9	164	0	partitioning_monthly	0	Y
9009	9	164	0	tablename_in_field	0	N
9010	9	164	0	tablename_field	0	\N
9011	9	164	0	tablename_in_table	0	Y
9012	9	164	0	return_keys	0	N
9013	9	164	0	return_field	0	\N
9014	9	164	0	cluster_schema	0	\N
9015	9	165	0	PARTITIONING_SCHEMA	0	\N
9016	9	165	0	PARTITIONING_METHOD	0	none
9017	9	165	0	schema	0	\N
9018	9	165	0	table	0	date_dim
9019	9	165	0	id_connection	5	\N
9020	9	165	0	commit	100	\N
9021	9	165	0	cache_size	9999	\N
9022	9	165	0	replace	0	N
9023	9	165	0	crc	0	N
9024	9	165	0	crcfield	0	hashcode
9025	9	165	0	lookup_key_name	0	dateTime
9026	9	165	0	lookup_key_field	0	dateTime
9027	9	165	1	lookup_key_name	0	day_of_month
9028	9	165	1	lookup_key_field	0	day_of_month
9029	9	165	2	lookup_key_name	0	week_of_year
9030	9	165	2	lookup_key_field	0	week_of_year
9031	9	165	3	lookup_key_name	0	month_of_year
9032	9	165	3	lookup_key_field	0	month_of_year
9033	9	165	4	lookup_key_name	0	year
14852	13	270	4	value_update	0	Y
14853	13	270	5	value_name	0	address1
14854	13	270	5	value_rename	0	address1
14855	13	270	5	value_update	0	Y
14856	13	270	6	value_name	0	address2
14857	13	270	6	value_rename	0	address2
14858	13	270	6	value_update	0	Y
14859	13	270	7	value_name	0	city
14860	13	270	7	value_rename	0	city
14861	13	270	7	value_update	0	Y
14862	13	270	8	value_name	0	state
14863	13	270	8	value_rename	0	state
14864	13	270	8	value_update	0	Y
14865	13	270	9	value_name	0	zip
14866	13	270	9	value_rename	0	zip
14867	13	270	9	value_update	0	Y
14868	13	270	10	value_name	0	country
14869	13	270	10	value_rename	0	country
14870	13	270	10	value_update	0	Y
14871	13	270	11	value_name	0	tel
14872	13	270	11	value_rename	0	tel
14873	13	270	11	value_update	0	Y
14874	13	270	12	value_name	0	gender
14875	13	270	12	value_rename	0	gender
14876	13	270	12	value_update	0	Y
14877	13	270	13	value_name	0	race
14878	13	270	13	value_rename	0	race
14879	13	270	13	value_update	0	Y
14880	13	270	14	value_name	0	home_language
14881	13	270	14	value_rename	0	home_language
14882	13	270	14	value_update	0	Y
14883	13	270	15	value_name	0	ssn
14884	13	270	15	value_rename	0	ssn
14885	13	270	15	value_update	0	Y
14886	13	270	16	value_name	0	marital_stat
14887	13	270	16	value_rename	0	marital_stat
14888	13	270	16	value_update	0	Y
14889	13	270	17	value_name	0	religion
14890	13	270	17	value_rename	0	religion
14891	13	270	17	value_update	0	Y
14892	13	270	18	value_name	0	mothermrn
14893	13	270	18	value_rename	0	mothermrn
14894	13	270	18	value_update	0	Y
14895	13	270	19	value_name	0	death_date
14896	13	270	19	value_rename	0	death_date
14897	13	270	19	value_update	0	Y
14898	13	270	20	value_name	0	time_created
14899	13	270	20	value_rename	0	time_created
14900	13	270	20	value_update	0	Y
14901	13	270	21	value_name	0	date_of_birth
14902	13	270	21	value_rename	0	date_of_birth
14903	13	270	21	value_update	0	Y
14904	13	270	22	value_name	0	time_updated
14905	13	270	22	value_rename	0	time_updated
14906	13	270	22	value_update	0	Y
14907	13	270	23	value_name	0	emr_id
14908	13	270	23	value_rename	0	emr_id
14909	13	270	23	value_update	0	Y
14910	13	270	24	value_name	0	tel_ext
14911	13	270	24	value_rename	0	tel_ext
14912	13	270	24	value_update	0	Y
14913	13	270	0	cluster_schema	0	\N
14914	13	271	0	PARTITIONING_SCHEMA	0	\N
14915	13	271	0	PARTITIONING_METHOD	0	none
14916	13	271	0	filename	0	\N
14917	13	271	0	trans_name	0	Add Stock Variables
14918	13	271	0	directory_path	0	/esp/load
14919	13	271	0	input_input_step	0	Read patient files
14920	13	271	0	input_output_step	0	Mapping input specification
14921	13	271	0	input_main_path	0	Y
14922	13	271	0	input_rename_on_output	0	N
14923	13	271	0	input_description	0	\N
14924	13	271	0	input_nr_renames	23	\N
14925	13	271	0	input_rename_parent_0	0	patient_id
14926	13	271	0	input_rename_child_0	0	String
14927	13	271	0	input_rename_parent_1	0	medical_record_num
14928	13	271	0	input_rename_child_1	0	String
14929	13	271	0	input_rename_parent_2	0	last_name
14930	13	271	0	input_rename_child_2	0	String
14931	13	271	0	input_rename_parent_3	0	first_name
14932	13	271	0	input_rename_child_3	0	String
14933	13	271	0	input_rename_parent_4	0	middle_name
14934	13	271	0	input_rename_child_4	0	String
14935	13	271	0	input_rename_parent_5	0	address_1
14936	13	271	0	input_rename_child_5	0	String
14937	13	271	0	input_rename_parent_6	0	address_2
14938	13	271	0	input_rename_child_6	0	String
14939	13	271	0	input_rename_parent_7	0	city
14940	13	271	0	input_rename_child_7	0	String
14941	13	271	0	input_rename_parent_8	0	state
14942	13	271	0	input_rename_child_8	0	String
14943	13	271	0	input_rename_parent_9	0	zip
14944	13	271	0	input_rename_child_9	0	String
14945	13	271	0	input_rename_parent_10	0	country
14946	13	271	0	input_rename_child_10	0	String
14947	13	271	0	input_rename_parent_11	0	telephone
14948	13	271	0	input_rename_child_11	0	String
14949	13	271	0	input_rename_parent_12	0	tel_ext
14950	13	271	0	input_rename_child_12	0	String
14951	13	271	0	input_rename_parent_13	0	dob
14952	13	271	0	input_rename_child_13	0	Date
14953	13	271	0	input_rename_parent_14	0	gender
14954	13	271	0	input_rename_child_14	0	String
14955	13	271	0	input_rename_parent_15	0	race
14956	13	271	0	input_rename_child_15	0	String
14957	13	271	0	input_rename_parent_16	0	lang
14958	13	271	0	input_rename_child_16	0	String
14959	13	271	0	input_rename_parent_17	0	ssn
14960	13	271	0	input_rename_child_17	0	String
14961	13	271	0	input_rename_parent_18	0	phy
14962	13	271	0	input_rename_child_18	0	String
14963	13	271	0	input_rename_parent_19	0	marital_status
14964	13	271	0	input_rename_child_19	0	String
14965	13	271	0	input_rename_parent_20	0	religion
14966	13	271	0	input_rename_child_20	0	String
14967	13	271	0	input_rename_parent_21	0	mom
14968	13	271	0	input_rename_child_21	0	String
14969	13	271	0	input_rename_parent_22	0	death
14970	13	271	0	input_rename_child_22	0	String
14971	13	271	0	output_input_step	0	Mapping output specification
14972	13	271	0	output_output_step	0	Select values
14973	13	271	0	output_main_path	0	Y
14974	13	271	0	output_rename_on_output	0	N
14975	13	271	0	output_description	0	\N
14976	13	271	0	output_nr_renames	3	\N
14977	13	271	0	output_rename_parent_0	0	emr_id
14978	13	271	0	output_rename_child_0	0	emr_id
14979	13	271	0	output_rename_parent_1	0	current_timestamp
14980	13	271	0	output_rename_child_1	0	time_created
14981	13	271	0	output_rename_parent_2	0	current_timestamp
14982	13	271	0	output_rename_child_2	0	time_updated
14983	13	271	0	cluster_schema	0	\N
14984	13	272	0	PARTITIONING_SCHEMA	0	\N
14985	13	272	0	PARTITIONING_METHOD	0	none
14986	13	272	0	accept_filenames	0	N
14987	13	272	0	accept_field	0	\N
14988	13	272	0	accept_stepname	0	\N
14989	13	272	0	separator	0	^
14990	13	272	0	enclosure	0	"
14991	13	272	0	enclosure_breaks	0	N
14992	13	272	0	escapechar	0	\N
14993	13	272	0	header	0	N
14994	13	272	0	nr_headerlines	1	\N
14995	13	272	0	footer	0	N
14996	13	272	0	nr_footerlines	1	\N
14997	13	272	0	line_wrapped	0	N
14998	13	272	0	nr_wraps	1	\N
14999	13	272	0	layout_paged	0	N
15000	13	272	0	nr_lines_per_page	80	\N
15001	13	272	0	nr_lines_doc_header	0	\N
15002	13	272	0	noempty	0	Y
15003	13	272	0	include	0	N
15004	13	272	0	include_field	0	\N
15005	13	272	0	rownum	0	N
15006	13	272	0	rownumByFile	0	N
15007	13	272	0	rownum_field	0	\N
15008	13	272	0	format	0	Unix
15009	13	272	0	encoding	0	\N
15010	13	272	0	add_to_result_filenames	0	Y
15011	13	272	0	limit	0	\N
15012	13	272	0	file_name	0	${INCOMING_DIR}
15013	13	272	0	file_mask	0	epicmem.*
15014	13	272	0	file_required	0	N
15015	13	272	0	file_type	0	CSV
15016	13	272	0	compression	0	None
15017	13	272	0	field_name	0	patient_id
15018	13	272	0	field_type	0	String
15019	13	272	0	field_format	0	\N
15020	13	272	0	field_currency	0	\N
15021	13	272	0	field_decimal	0	\N
15022	13	272	0	field_group	0	none
15023	13	272	0	field_nullif	0	\N
15024	13	272	0	field_ifnull	0	\N
15025	13	272	0	field_position	-1	\N
15026	13	272	0	field_length	-1	\N
15027	13	272	0	field_precision	-1	\N
15028	13	272	0	field_trim_type	0	none
15029	13	272	0	field_repeat	0	N
15030	13	272	1	field_name	0	medical_record_num
15031	13	272	1	field_type	0	String
15032	13	272	1	field_format	0	\N
15033	13	272	1	field_currency	0	\N
15034	13	272	1	field_decimal	0	\N
15035	13	272	1	field_group	0	none
15036	13	272	1	field_nullif	0	\N
15037	13	272	1	field_ifnull	0	\N
15038	13	272	1	field_position	-1	\N
15039	13	272	1	field_length	-1	\N
15040	13	272	1	field_precision	-1	\N
15041	13	272	1	field_trim_type	0	none
15042	13	272	1	field_repeat	0	N
15043	13	272	2	field_name	0	last_name
15044	13	272	2	field_type	0	String
15045	13	272	2	field_format	0	\N
15046	13	272	2	field_currency	0	\N
15047	13	272	2	field_decimal	0	\N
15048	13	272	2	field_group	0	none
15049	13	272	2	field_nullif	0	\N
15050	13	272	2	field_ifnull	0	\N
15051	13	272	2	field_position	-1	\N
15052	13	272	2	field_length	-1	\N
15053	13	272	2	field_precision	-1	\N
15054	13	272	2	field_trim_type	0	none
15055	13	272	2	field_repeat	0	N
15056	13	272	3	field_name	0	first_name
15057	13	272	3	field_type	0	String
15058	13	272	3	field_format	0	\N
15059	13	272	3	field_currency	0	\N
15060	13	272	3	field_decimal	0	\N
15061	13	272	3	field_group	0	none
15062	13	272	3	field_nullif	0	\N
15063	13	272	3	field_ifnull	0	\N
15064	13	272	3	field_position	-1	\N
15065	13	272	3	field_length	-1	\N
15066	13	272	3	field_precision	-1	\N
15067	13	272	3	field_trim_type	0	none
15068	13	272	3	field_repeat	0	N
15069	13	272	4	field_name	0	middle_name
15070	13	272	4	field_type	0	String
15071	13	272	4	field_format	0	\N
15072	13	272	4	field_currency	0	\N
15073	13	272	4	field_decimal	0	\N
15074	13	272	4	field_group	0	none
15075	13	272	4	field_nullif	0	\N
15076	13	272	4	field_ifnull	0	\N
15077	13	272	4	field_position	-1	\N
15078	13	272	4	field_length	-1	\N
15079	13	272	4	field_precision	-1	\N
15080	13	272	4	field_trim_type	0	none
15081	13	272	4	field_repeat	0	N
15082	13	272	5	field_name	0	address_1
15083	13	272	5	field_type	0	String
15084	13	272	5	field_format	0	\N
15085	13	272	5	field_currency	0	\N
15086	13	272	5	field_decimal	0	\N
15087	13	272	5	field_group	0	none
15088	13	272	5	field_nullif	0	\N
15089	13	272	5	field_ifnull	0	\N
15090	13	272	5	field_position	-1	\N
15091	13	272	5	field_length	-1	\N
15092	13	272	5	field_precision	-1	\N
15093	13	272	5	field_trim_type	0	none
15094	13	272	5	field_repeat	0	N
15095	13	272	6	field_name	0	address_2
15096	13	272	6	field_type	0	String
15097	13	272	6	field_format	0	\N
15098	13	272	6	field_currency	0	\N
15099	13	272	6	field_decimal	0	\N
15100	13	272	6	field_group	0	none
15101	13	272	6	field_nullif	0	\N
15102	13	272	6	field_ifnull	0	\N
15103	13	272	6	field_position	-1	\N
15104	13	272	6	field_length	-1	\N
15105	13	272	6	field_precision	-1	\N
15106	13	272	6	field_trim_type	0	none
15107	13	272	6	field_repeat	0	N
15108	13	272	7	field_name	0	city
15109	13	272	7	field_type	0	String
15110	13	272	7	field_format	0	\N
15111	13	272	7	field_currency	0	\N
15112	13	272	7	field_decimal	0	\N
15113	13	272	7	field_group	0	none
15114	13	272	7	field_nullif	0	\N
15115	13	272	7	field_ifnull	0	\N
15116	13	272	7	field_position	-1	\N
15117	13	272	7	field_length	-1	\N
15118	13	272	7	field_precision	-1	\N
15119	13	272	7	field_trim_type	0	none
15120	13	272	7	field_repeat	0	N
15121	13	272	8	field_name	0	state
15122	13	272	8	field_type	0	String
15123	13	272	8	field_format	0	\N
15124	13	272	8	field_currency	0	\N
15125	13	272	8	field_decimal	0	\N
15126	13	272	8	field_group	0	none
15127	13	272	8	field_nullif	0	\N
15128	13	272	8	field_ifnull	0	\N
15129	13	272	8	field_position	-1	\N
15130	13	272	8	field_length	-1	\N
15131	13	272	8	field_precision	-1	\N
15132	13	272	8	field_trim_type	0	none
15133	13	272	8	field_repeat	0	N
15134	13	272	9	field_name	0	zip
15135	13	272	9	field_type	0	String
15136	13	272	9	field_format	0	\N
15137	13	272	9	field_currency	0	\N
15138	13	272	9	field_decimal	0	\N
15139	13	272	9	field_group	0	none
15140	13	272	9	field_nullif	0	\N
15141	13	272	9	field_ifnull	0	\N
15142	13	272	9	field_position	-1	\N
15143	13	272	9	field_length	-1	\N
15144	13	272	9	field_precision	-1	\N
15145	13	272	9	field_trim_type	0	none
15146	13	272	9	field_repeat	0	N
15147	13	272	10	field_name	0	country
15148	13	272	10	field_type	0	String
15149	13	272	10	field_format	0	\N
15150	13	272	10	field_currency	0	\N
15151	13	272	10	field_decimal	0	\N
15152	13	272	10	field_group	0	none
15153	13	272	10	field_nullif	0	\N
15154	13	272	10	field_ifnull	0	\N
15155	13	272	10	field_position	-1	\N
15156	13	272	10	field_length	-1	\N
15157	13	272	10	field_precision	-1	\N
15158	13	272	10	field_trim_type	0	none
15159	13	272	10	field_repeat	0	N
15160	13	272	11	field_name	0	telephone
15161	13	272	11	field_type	0	String
15162	13	272	11	field_format	0	\N
15163	13	272	11	field_currency	0	\N
15164	13	272	11	field_decimal	0	\N
15165	13	272	11	field_group	0	none
15166	13	272	11	field_nullif	0	\N
15167	13	272	11	field_ifnull	0	\N
15168	13	272	11	field_position	-1	\N
15169	13	272	11	field_length	-1	\N
15170	13	272	11	field_precision	-1	\N
15171	13	272	11	field_trim_type	0	none
15172	13	272	11	field_repeat	0	N
15173	13	272	12	field_name	0	tel_ext
15174	13	272	12	field_type	0	String
15175	13	272	12	field_format	0	\N
15176	13	272	12	field_currency	0	\N
15177	13	272	12	field_decimal	0	\N
15178	13	272	12	field_group	0	none
15179	13	272	12	field_nullif	0	\N
15180	13	272	12	field_ifnull	0	\N
15181	13	272	12	field_position	-1	\N
15182	13	272	12	field_length	-1	\N
15183	13	272	12	field_precision	-1	\N
15184	13	272	12	field_trim_type	0	none
15185	13	272	12	field_repeat	0	N
15186	13	272	13	field_name	0	dob
15187	13	272	13	field_type	0	Date
15188	13	272	13	field_format	0	\N
15189	13	272	13	field_currency	0	\N
15190	13	272	13	field_decimal	0	\N
15191	13	272	13	field_group	0	none
15192	13	272	13	field_nullif	0	\N
15193	13	272	13	field_ifnull	0	\N
15194	13	272	13	field_position	-1	\N
15195	13	272	13	field_length	-1	\N
15196	13	272	13	field_precision	-1	\N
15197	13	272	13	field_trim_type	0	none
15198	13	272	13	field_repeat	0	N
15199	13	272	14	field_name	0	gender
15200	13	272	14	field_type	0	String
15201	13	272	14	field_format	0	\N
15202	13	272	14	field_currency	0	\N
15203	13	272	14	field_decimal	0	\N
15204	13	272	14	field_group	0	none
15205	13	272	14	field_nullif	0	\N
15206	13	272	14	field_ifnull	0	\N
15207	13	272	14	field_position	-1	\N
15208	13	272	14	field_length	-1	\N
15209	13	272	14	field_precision	-1	\N
15210	13	272	14	field_trim_type	0	none
15211	13	272	14	field_repeat	0	N
15212	13	272	15	field_name	0	race
15213	13	272	15	field_type	0	String
15214	13	272	15	field_format	0	\N
15215	13	272	15	field_currency	0	\N
15216	13	272	15	field_decimal	0	\N
15217	13	272	15	field_group	0	none
15218	13	272	15	field_nullif	0	\N
15219	13	272	15	field_ifnull	0	\N
15220	13	272	15	field_position	-1	\N
15221	13	272	15	field_length	-1	\N
15222	13	272	15	field_precision	-1	\N
15223	13	272	15	field_trim_type	0	none
15224	13	272	15	field_repeat	0	N
15225	13	272	16	field_name	0	lang
15226	13	272	16	field_type	0	String
15227	13	272	16	field_format	0	\N
15228	13	272	16	field_currency	0	\N
15229	13	272	16	field_decimal	0	\N
15230	13	272	16	field_group	0	none
15231	13	272	16	field_nullif	0	\N
15232	13	272	16	field_ifnull	0	\N
15233	13	272	16	field_position	-1	\N
15234	13	272	16	field_length	-1	\N
15235	13	272	16	field_precision	-1	\N
15236	13	272	16	field_trim_type	0	none
15237	13	272	16	field_repeat	0	N
15238	13	272	17	field_name	0	ssn
15239	13	272	17	field_type	0	String
15240	13	272	17	field_format	0	\N
15241	13	272	17	field_currency	0	\N
15242	13	272	17	field_decimal	0	\N
15243	13	272	17	field_group	0	none
15244	13	272	17	field_nullif	0	\N
15245	13	272	17	field_ifnull	0	\N
15246	13	272	17	field_position	-1	\N
15247	13	272	17	field_length	-1	\N
15248	13	272	17	field_precision	-1	\N
15249	13	272	17	field_trim_type	0	none
15250	13	272	17	field_repeat	0	N
15251	13	272	18	field_name	0	phy
15252	13	272	18	field_type	0	String
15253	13	272	18	field_format	0	\N
15254	13	272	18	field_currency	0	\N
15255	13	272	18	field_decimal	0	\N
15256	13	272	18	field_group	0	none
15257	13	272	18	field_nullif	0	\N
15258	13	272	18	field_ifnull	0	\N
15259	13	272	18	field_position	-1	\N
15260	13	272	18	field_length	-1	\N
15261	13	272	18	field_precision	-1	\N
15262	13	272	18	field_trim_type	0	none
15263	13	272	18	field_repeat	0	N
15264	13	272	19	field_name	0	marital_status
15265	13	272	19	field_type	0	String
15266	13	272	19	field_format	0	\N
15267	13	272	19	field_currency	0	\N
15268	13	272	19	field_decimal	0	\N
15269	13	272	19	field_group	0	none
15270	13	272	19	field_nullif	0	\N
15271	13	272	19	field_ifnull	0	\N
15272	13	272	19	field_position	-1	\N
15273	13	272	19	field_length	-1	\N
15274	13	272	19	field_precision	-1	\N
15275	13	272	19	field_trim_type	0	none
15276	13	272	19	field_repeat	0	N
15277	13	272	20	field_name	0	religion
15278	13	272	20	field_type	0	String
15279	13	272	20	field_format	0	\N
15280	13	272	20	field_currency	0	\N
15281	13	272	20	field_decimal	0	\N
15282	13	272	20	field_group	0	none
15283	13	272	20	field_nullif	0	\N
15284	13	272	20	field_ifnull	0	\N
15285	13	272	20	field_position	-1	\N
15286	13	272	20	field_length	-1	\N
15287	13	272	20	field_precision	-1	\N
15288	13	272	20	field_trim_type	0	none
15289	13	272	20	field_repeat	0	N
15290	13	272	21	field_name	0	mom
15291	13	272	21	field_type	0	String
15292	13	272	21	field_format	0	\N
15293	13	272	21	field_currency	0	\N
15294	13	272	21	field_decimal	0	\N
15295	13	272	21	field_group	0	none
15296	13	272	21	field_nullif	0	\N
15297	13	272	21	field_ifnull	0	\N
15298	13	272	21	field_position	-1	\N
15299	13	272	21	field_length	-1	\N
15300	13	272	21	field_precision	-1	\N
15301	13	272	21	field_trim_type	0	none
15302	13	272	21	field_repeat	0	N
15303	13	272	22	field_name	0	death
15304	13	272	22	field_type	0	String
15305	13	272	22	field_format	0	\N
15306	13	272	22	field_currency	0	\N
15307	13	272	22	field_decimal	0	\N
15308	13	272	22	field_group	0	none
15309	13	272	22	field_nullif	0	\N
15310	13	272	22	field_ifnull	0	\N
15311	13	272	22	field_position	-1	\N
15312	13	272	22	field_length	-1	\N
15313	13	272	22	field_precision	-1	\N
15314	13	272	22	field_trim_type	0	none
15315	13	272	22	field_repeat	0	N
15316	13	272	0	error_ignored	0	N
15317	13	272	0	error_line_skipped	0	N
15318	13	272	0	error_count_field	0	\N
15319	13	272	0	error_fields_field	0	\N
15320	13	272	0	error_text_field	0	\N
15321	13	272	0	bad_line_files_dest_dir	0	\N
15322	13	272	0	bad_line_files_ext	0	warning
15323	13	272	0	error_line_files_dest_dir	0	\N
15324	13	272	0	error_line_files_ext	0	error
15325	13	272	0	line_number_files_dest_dir	0	\N
15326	13	272	0	line_number_files_ext	0	line
15327	13	272	0	date_format_lenient	0	Y
15328	13	272	0	date_format_locale	0	en_us
15329	13	272	0	cluster_schema	0	\N
15330	13	273	0	PARTITIONING_SCHEMA	0	\N
15331	13	273	0	PARTITIONING_METHOD	0	none
15332	13	273	0	field_name	0	patient_id
15333	13	273	0	field_rename	0	ext_patient_id
15334	13	273	0	field_length	-1	\N
15335	13	273	0	field_precision	-1	\N
15336	13	273	1	field_name	0	medical_record_num
15337	13	273	1	field_rename	0	ext_medical_record_num
15338	13	273	1	field_length	-1	\N
15339	13	273	1	field_precision	-1	\N
15340	13	273	2	field_name	0	last_name
15341	13	273	2	field_rename	0	last_name
15342	13	273	2	field_length	-1	\N
15343	13	273	2	field_precision	-1	\N
15344	13	273	3	field_name	0	first_name
15345	13	273	3	field_rename	0	first_name
15346	13	273	3	field_length	-1	\N
15347	13	273	3	field_precision	-1	\N
15348	13	273	4	field_name	0	middle_name
15349	13	273	4	field_rename	0	middle_name
15350	13	273	4	field_length	-1	\N
15351	13	273	4	field_precision	-1	\N
15352	13	273	5	field_name	0	address_1
15353	13	273	5	field_rename	0	address1
15354	13	273	5	field_length	-1	\N
15355	13	273	5	field_precision	-1	\N
15356	13	273	6	field_name	0	address_2
15357	13	273	6	field_rename	0	address2
15358	13	273	6	field_length	-1	\N
15359	13	273	6	field_precision	-1	\N
15360	13	273	7	field_name	0	city
15361	13	273	7	field_rename	0	city
15362	13	273	7	field_length	-1	\N
15363	13	273	7	field_precision	-1	\N
15364	13	273	8	field_name	0	state
15365	13	273	8	field_rename	0	state
15366	13	273	8	field_length	-1	\N
15367	13	273	8	field_precision	-1	\N
15368	13	273	9	field_name	0	zip
15369	13	273	9	field_rename	0	zip
15370	13	273	9	field_length	-1	\N
15371	13	273	9	field_precision	-1	\N
15372	13	273	10	field_name	0	country
15373	13	273	10	field_rename	0	country
15374	13	273	10	field_length	-1	\N
15375	13	273	10	field_precision	-1	\N
15376	13	273	11	field_name	0	telephone
15377	13	273	11	field_rename	0	tel
15378	13	273	11	field_length	-1	\N
15379	13	273	11	field_precision	-1	\N
15380	13	273	12	field_name	0	gender
15381	13	273	12	field_rename	0	gender
15382	13	273	12	field_length	-1	\N
15383	13	273	12	field_precision	-1	\N
15384	13	273	13	field_name	0	race
15385	13	273	13	field_rename	0	race
15386	13	273	13	field_length	-1	\N
15387	13	273	13	field_precision	-1	\N
15388	13	273	14	field_name	0	lang
15389	13	273	14	field_rename	0	home_language
15390	13	273	14	field_length	-1	\N
15391	13	273	14	field_precision	-1	\N
15392	13	273	15	field_name	0	ssn
15393	13	273	15	field_rename	0	ssn
15394	13	273	15	field_length	-1	\N
15395	13	273	15	field_precision	-1	\N
15396	13	273	16	field_name	0	marital_status
15397	13	273	16	field_rename	0	marital_stat
15398	13	273	16	field_length	-1	\N
15399	13	273	16	field_precision	-1	\N
15400	13	273	17	field_name	0	religion
15401	13	273	17	field_rename	0	religion
15402	13	273	17	field_length	-1	\N
15403	13	273	17	field_precision	-1	\N
15404	13	273	18	field_name	0	mom
15405	13	273	18	field_rename	0	mothermrn
15406	13	273	18	field_length	-1	\N
15407	13	273	18	field_precision	-1	\N
15408	13	273	19	field_name	0	death
15409	13	273	19	field_rename	0	death_date
15410	13	273	19	field_length	-1	\N
15411	13	273	19	field_precision	-1	\N
15412	13	273	20	field_name	0	current_date
15413	13	273	20	field_rename	0	time_created
15414	13	273	20	field_length	-1	\N
15415	13	273	20	field_precision	-1	\N
15416	13	273	21	field_name	0	dob
15417	13	273	21	field_rename	0	date_of_birth
15418	13	273	21	field_length	-1	\N
15419	13	273	21	field_precision	-1	\N
15420	13	273	22	field_name	0	current_date
15421	13	273	22	field_rename	0	time_updated
15422	13	273	22	field_length	-1	\N
15423	13	273	22	field_precision	-1	\N
15424	13	273	23	field_name	0	emr_id
15425	13	273	23	field_rename	0	emr_id
15426	13	273	23	field_length	-1	\N
15427	13	273	23	field_precision	-1	\N
15428	13	273	24	field_name	0	tel_ext
15429	13	273	24	field_rename	0	tel_ext
15430	13	273	24	field_length	-1	\N
15431	13	273	24	field_precision	-1	\N
15432	13	273	0	select_unspecified	0	N
15433	13	273	0	cluster_schema	0	\N
16070	16	277	0	PARTITIONING_SCHEMA	0	\N
16071	16	277	0	PARTITIONING_METHOD	0	none
14780	14	264	0	PARTITIONING_SCHEMA	0	\N
14781	14	264	0	PARTITIONING_METHOD	0	none
14782	14	264	0	id_connection	7	\N
14783	14	264	0	cache	0	Y
14784	14	264	0	cache_load_all	0	N
14785	14	264	0	cache_size	0	\N
14786	14	264	0	lookup_schema	0	\N
14787	14	264	0	lookup_table	0	core_emrsystem
14788	14	264	0	lookup_orderby	0	\N
14789	14	264	0	fail_on_multiple	0	N
14790	14	264	0	eat_row_on_failure	0	Y
14791	14	264	0	lookup_key_name	0	emr_name
14792	14	264	0	lookup_key_field	0	name
14793	14	264	0	lookup_key_condition	0	=
14794	14	264	0	lookup_key_name2	0	\N
14795	14	264	0	return_value_name	0	id
14796	14	264	0	return_value_rename	0	emr_id
14797	14	264	0	return_value_default	0	\N
14798	14	264	0	return_value_type	0	Integer
14799	14	264	0	cluster_schema	0	\N
14800	14	265	0	PARTITIONING_SCHEMA	0	\N
14801	14	265	0	PARTITIONING_METHOD	0	none
14802	14	265	0	field_name	0	emr_name
14803	14	265	0	field_variable	0	${EMR}
14804	14	265	0	cluster_schema	0	\N
14805	14	266	0	PARTITIONING_SCHEMA	0	\N
14806	14	266	0	PARTITIONING_METHOD	0	none
14807	14	266	0	field_name	0	current_timestamp
14808	14	266	0	field_type	0	system date (variable)
14809	14	266	0	cluster_schema	0	\N
14810	14	267	0	PARTITIONING_SCHEMA	0	\N
14811	14	267	0	PARTITIONING_METHOD	0	none
14812	14	267	0	select_unspecified	0	Y
14813	14	267	0	cluster_schema	0	\N
14814	14	268	0	PARTITIONING_SCHEMA	0	\N
14815	14	268	0	PARTITIONING_METHOD	0	none
14816	14	268	0	cluster_schema	0	\N
16072	16	277	0	filename	0	/home/rejmv/work/north_adams_simple-esp/NORTH_ADAMS/NorthAdamsLocal-LOINCmapMay2008.redacted.xls
16073	16	277	0	filename_field	0	\N
16074	16	277	0	rownum_field	0	\N
16075	16	277	0	include_filename	0	N
16076	16	277	0	separator	0	\t
16077	16	277	0	enclosure	0	"
16078	16	277	0	buffer_size	0	50000
16079	16	277	0	header	0	Y
16080	16	277	0	lazy_conversion	0	Y
16081	16	277	0	add_filename_result	0	N
16082	16	277	0	parallel	0	N
16083	16	277	0	encoding	0	\N
16084	16	277	0	field_name	0	Dept
16085	16	277	0	field_type	0	String
16086	16	277	0	field_format	0	\N
16087	16	277	0	field_currency	0	\N
16088	16	277	0	field_decimal	0	\N
16089	16	277	0	field_group	0	\N
16090	16	277	0	field_length	-1	\N
16091	16	277	0	field_precision	-1	\N
16092	16	277	0	field_trim_type	0	none
16093	16	277	1	field_name	0	AttrCode
16094	16	277	1	field_type	0	String
16095	16	277	1	field_format	0	\N
16096	16	277	1	field_currency	0	\N
16097	16	277	1	field_decimal	0	\N
16098	16	277	1	field_group	0	\N
16099	16	277	1	field_length	-1	\N
16100	16	277	1	field_precision	-1	\N
16101	16	277	1	field_trim_type	0	none
16102	16	277	2	field_name	0	AttrMnemonic
16103	16	277	2	field_type	0	String
16104	16	277	2	field_format	0	\N
16105	16	277	2	field_currency	0	\N
16106	16	277	2	field_decimal	0	\N
16107	16	277	2	field_group	0	\N
16108	16	277	2	field_length	-1	\N
16109	16	277	2	field_precision	-1	\N
16110	16	277	2	field_trim_type	0	none
16111	16	277	3	field_name	0	AttrName
16112	16	277	3	field_type	0	String
16113	16	277	3	field_format	0	\N
16114	16	277	3	field_currency	0	\N
16115	16	277	3	field_decimal	0	\N
16116	16	277	3	field_group	0	\N
16117	16	277	3	field_length	-1	\N
16118	16	277	3	field_precision	-1	\N
16119	16	277	3	field_trim_type	0	none
16120	16	277	4	field_name	0	LOINC
16121	16	277	4	field_type	0	String
16122	16	277	4	field_format	0	\N
16123	16	277	4	field_currency	0	\N
16124	16	277	4	field_decimal	0	\N
16125	16	277	4	field_group	0	\N
16126	16	277	4	field_length	-1	\N
16127	16	277	4	field_precision	-1	\N
16128	16	277	4	field_trim_type	0	none
16129	16	277	5	field_name	0	LOINC Name
16130	16	277	5	field_type	0	String
16131	16	277	5	field_format	0	\N
16132	16	277	5	field_currency	0	\N
16133	16	277	5	field_decimal	0	\N
16134	16	277	5	field_group	0	\N
16135	16	277	5	field_length	-1	\N
16136	16	277	5	field_precision	-1	\N
16137	16	277	5	field_trim_type	0	none
16138	16	277	0	cluster_schema	0	\N
16139	16	278	0	PARTITIONING_SCHEMA	0	\N
16140	16	278	0	PARTITIONING_METHOD	0	none
16141	16	278	0	id_connection	6	\N
16142	16	278	0	schema	0	\N
16143	16	278	0	table	0	esp_external_to_loinc_map
16144	16	278	0	commit	100	\N
16145	16	278	0	truncate	0	Y
16146	16	278	0	ignore_errors	0	N
16147	16	278	0	use_batch	0	Y
16148	16	278	0	partitioning_enabled	0	N
16149	16	278	0	partitioning_field	0	\N
16150	16	278	0	partitioning_daily	0	N
16151	16	278	0	partitioning_monthly	0	Y
16152	16	278	0	tablename_in_field	0	N
16153	16	278	0	tablename_field	0	\N
16154	16	278	0	tablename_in_table	0	Y
16155	16	278	0	return_keys	0	N
16156	16	278	0	return_field	0	\N
16157	16	278	0	cluster_schema	0	\N
16158	16	279	0	PARTITIONING_SCHEMA	0	\N
16159	16	279	0	PARTITIONING_METHOD	0	none
16160	16	279	0	field_name	0	AttrCode
16161	16	279	0	field_rename	0	ext_code
16162	16	279	0	field_length	-1	\N
16163	16	279	0	field_precision	-1	\N
16164	16	279	1	field_name	0	AttrName
16165	16	279	1	field_rename	0	ext_name
16166	16	279	1	field_length	-1	\N
16167	16	279	1	field_precision	-1	\N
16168	16	279	2	field_name	0	loinc_num
16169	16	279	2	field_rename	0	loinc_id
16170	16	279	2	field_length	-1	\N
16171	16	279	2	field_precision	-1	\N
16172	16	279	0	select_unspecified	0	N
16173	16	279	0	cluster_schema	0	\N
16174	16	280	0	PARTITIONING_SCHEMA	0	\N
16175	16	280	0	PARTITIONING_METHOD	0	none
16176	16	280	0	id_connection	6	\N
16177	16	280	0	cache	0	N
16178	16	280	0	cache_load_all	0	N
16179	16	280	0	cache_size	0	\N
16180	16	280	0	lookup_schema	0	\N
16181	16	280	0	lookup_table	0	esp_loinc
16182	16	280	0	lookup_orderby	0	\N
16183	16	280	0	fail_on_multiple	0	N
16184	16	280	0	eat_row_on_failure	0	N
16185	16	280	0	lookup_key_name	0	LOINC
16186	16	280	0	lookup_key_field	0	loinc_num
16187	16	280	0	lookup_key_condition	0	=
16188	16	280	0	lookup_key_name2	0	\N
16189	16	280	0	return_value_name	0	loinc_num
16190	16	280	0	return_value_rename	0	loinc_num
16191	16	280	0	return_value_default	0	\N
16192	16	280	0	return_value_type	0	String
16193	16	280	0	cluster_schema	0	\N
16194	16	281	0	PARTITIONING_SCHEMA	0	\N
16195	16	281	0	PARTITIONING_METHOD	0	none
16196	16	281	0	id_condition	5	\N
16197	16	281	0	send_true_to	0	Wait for all LOINCs to pass
16198	16	281	0	send_false_to	0	Abort
16199	16	281	0	cluster_schema	0	\N
16200	16	282	0	PARTITIONING_SCHEMA	0	\N
16201	16	282	0	PARTITIONING_METHOD	0	none
16202	16	282	0	row_threshold	0	0
16203	16	282	0	message	0	LOINC Number not found!
16204	16	282	0	always_log_rows	0	Y
16205	16	282	0	cluster_schema	0	\N
16206	16	283	0	PARTITIONING_SCHEMA	0	\N
16207	16	283	0	PARTITIONING_METHOD	0	none
16208	16	283	0	pass_all_rows	0	Y
16209	16	283	0	directory	0	%%java.io.tmpdir%%
16210	16	283	0	prefix	0	block
16211	16	283	0	cache_size	5000	\N
16212	16	283	0	compress	0	Y
16213	16	283	0	cluster_schema	0	\N
15434	15	274	0	PARTITIONING_SCHEMA	0	\N
15435	15	274	0	PARTITIONING_METHOD	0	none
15436	15	274	0	filename	0	/home/rejmv/work/north_adams_simple-esp/src/ESP/utils/LOINCDB.TXT
15437	15	274	0	filename_field	0	\N
15438	15	274	0	rownum_field	0	\N
15439	15	274	0	include_filename	0	N
15440	15	274	0	separator	0	\t
15441	15	274	0	enclosure	0	"
15442	15	274	0	buffer_size	0	50000
15443	15	274	0	header	0	Y
15444	15	274	0	lazy_conversion	0	Y
15445	15	274	0	add_filename_result	0	N
15446	15	274	0	parallel	0	N
15447	15	274	0	encoding	0	\N
15448	15	274	0	field_name	0	LOINC_NUM
15449	15	274	0	field_type	0	String
15450	15	274	0	field_format	0	\N
15451	15	274	0	field_currency	0	\N
15452	15	274	0	field_decimal	0	\N
15453	15	274	0	field_group	0	\N
15454	15	274	0	field_length	-1	\N
15455	15	274	0	field_precision	-1	\N
15456	15	274	0	field_trim_type	0	none
15457	15	274	1	field_name	0	COMPONENT
15458	15	274	1	field_type	0	String
15459	15	274	1	field_format	0	\N
15460	15	274	1	field_currency	0	\N
15461	15	274	1	field_decimal	0	\N
15462	15	274	1	field_group	0	\N
15463	15	274	1	field_length	-1	\N
15464	15	274	1	field_precision	-1	\N
15465	15	274	1	field_trim_type	0	none
15466	15	274	2	field_name	0	PROPERTY
15467	15	274	2	field_type	0	String
15468	15	274	2	field_format	0	\N
15469	15	274	2	field_currency	0	\N
15470	15	274	2	field_decimal	0	\N
15471	15	274	2	field_group	0	\N
15472	15	274	2	field_length	-1	\N
15473	15	274	2	field_precision	-1	\N
15474	15	274	2	field_trim_type	0	none
15475	15	274	3	field_name	0	TIME_ASPCT
15476	15	274	3	field_type	0	String
15477	15	274	3	field_format	0	\N
15478	15	274	3	field_currency	0	\N
15479	15	274	3	field_decimal	0	\N
15480	15	274	3	field_group	0	\N
15481	15	274	3	field_length	-1	\N
15482	15	274	3	field_precision	-1	\N
15483	15	274	3	field_trim_type	0	none
15484	15	274	4	field_name	0	SYSTEM
15485	15	274	4	field_type	0	String
15486	15	274	4	field_format	0	\N
15487	15	274	4	field_currency	0	\N
15488	15	274	4	field_decimal	0	\N
15489	15	274	4	field_group	0	\N
15490	15	274	4	field_length	-1	\N
15491	15	274	4	field_precision	-1	\N
15492	15	274	4	field_trim_type	0	none
15493	15	274	5	field_name	0	SCALE_TYP
15494	15	274	5	field_type	0	String
15495	15	274	5	field_format	0	\N
15496	15	274	5	field_currency	0	\N
15497	15	274	5	field_decimal	0	\N
15498	15	274	5	field_group	0	\N
15499	15	274	5	field_length	-1	\N
15500	15	274	5	field_precision	-1	\N
15501	15	274	5	field_trim_type	0	none
15502	15	274	6	field_name	0	METHOD_TYP
15503	15	274	6	field_type	0	String
15504	15	274	6	field_format	0	\N
15505	15	274	6	field_currency	0	\N
15506	15	274	6	field_decimal	0	\N
15507	15	274	6	field_group	0	\N
15508	15	274	6	field_length	-1	\N
15509	15	274	6	field_precision	-1	\N
15510	15	274	6	field_trim_type	0	none
15511	15	274	7	field_name	0	RELAT_NMS
15512	15	274	7	field_type	0	String
15513	15	274	7	field_format	0	\N
15514	15	274	7	field_currency	0	\N
15515	15	274	7	field_decimal	0	\N
15516	15	274	7	field_group	0	\N
15517	15	274	7	field_length	-1	\N
15518	15	274	7	field_precision	-1	\N
15519	15	274	7	field_trim_type	0	none
15520	15	274	8	field_name	0	CLASS
15521	15	274	8	field_type	0	String
15522	15	274	8	field_format	0	\N
15523	15	274	8	field_currency	0	\N
15524	15	274	8	field_decimal	0	\N
15525	15	274	8	field_group	0	\N
15526	15	274	8	field_length	-1	\N
15527	15	274	8	field_precision	-1	\N
15528	15	274	8	field_trim_type	0	none
15529	15	274	9	field_name	0	SOURCE
15530	15	274	9	field_type	0	String
15531	15	274	9	field_format	0	\N
15532	15	274	9	field_currency	0	\N
15533	15	274	9	field_decimal	0	\N
15534	15	274	9	field_group	0	\N
15535	15	274	9	field_length	-1	\N
15536	15	274	9	field_precision	-1	\N
15537	15	274	9	field_trim_type	0	none
15538	15	274	10	field_name	0	DT_LAST_CH
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
1	ValueMapper	Value Mapper	Maps values of a certain field from one value to another
2	RowGenerator	Generate Rows	Generate a number of empty or equal rows.
3	FieldSplitter	Split Fields	When you want to split a single field into more then one, use this step type.
4	FixedInput	Fixed file input	Fixed file input
5	CubeOutput	Serialize to file	Write rows of data to a data cube
6	ClosureGenerator	Closure Generator	This step allows you to generates a closure table using parent-child relationships.
7	CubeInput	De-serialize from file	Read rows of data from a data cube.
8	CsvInput	CSV file input	Simple CSV file input
9	WebServiceLookup	Web services lookup	Look up information using web services (WSDL)
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
425	14	0	UNIQUE_CONNECTIONS	0	N
426	14	0	FEEDBACK_SHOWN	0	Y
427	14	0	FEEDBACK_SIZE	50000	\N
428	14	0	USING_THREAD_PRIORITIES	0	Y
429	14	0	SHARED_FILE	0	\N
430	14	0	CAPTURE_STEP_PERFORMANCE	0	N
431	14	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
432	14	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
441	15	0	UNIQUE_CONNECTIONS	0	N
442	15	0	FEEDBACK_SHOWN	0	Y
443	15	0	FEEDBACK_SIZE	50000	\N
444	15	0	USING_THREAD_PRIORITIES	0	Y
445	15	0	SHARED_FILE	0	\N
446	15	0	CAPTURE_STEP_PERFORMANCE	0	N
447	15	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
448	15	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
25	2	0	UNIQUE_CONNECTIONS	0	N
26	2	0	FEEDBACK_SHOWN	0	Y
27	2	0	FEEDBACK_SIZE	50000	\N
28	2	0	USING_THREAD_PRIORITIES	0	Y
29	2	0	SHARED_FILE	0	\N
30	2	0	CAPTURE_STEP_PERFORMANCE	0	N
31	2	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
32	2	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
33	4	0	UNIQUE_CONNECTIONS	0	N
34	4	0	FEEDBACK_SHOWN	0	Y
35	4	0	FEEDBACK_SIZE	50000	\N
36	4	0	USING_THREAD_PRIORITIES	0	Y
37	4	0	SHARED_FILE	0	\N
38	4	0	CAPTURE_STEP_PERFORMANCE	0	N
39	4	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
40	4	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
265	11	0	UNIQUE_CONNECTIONS	0	N
266	11	0	FEEDBACK_SHOWN	0	Y
267	11	0	FEEDBACK_SIZE	50000	\N
268	11	0	USING_THREAD_PRIORITIES	0	Y
269	11	0	SHARED_FILE	0	\N
270	11	0	CAPTURE_STEP_PERFORMANCE	0	N
271	11	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
272	11	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
225	10	0	UNIQUE_CONNECTIONS	0	N
226	10	0	FEEDBACK_SHOWN	0	Y
73	1	0	UNIQUE_CONNECTIONS	0	N
74	1	0	FEEDBACK_SHOWN	0	Y
75	1	0	FEEDBACK_SIZE	50000	\N
76	1	0	USING_THREAD_PRIORITIES	0	Y
77	1	0	SHARED_FILE	0	\N
78	1	0	CAPTURE_STEP_PERFORMANCE	0	N
79	1	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
80	1	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
65	6	0	UNIQUE_CONNECTIONS	0	N
66	6	0	FEEDBACK_SHOWN	0	Y
67	6	0	FEEDBACK_SIZE	50000	\N
68	6	0	USING_THREAD_PRIORITIES	0	Y
69	6	0	SHARED_FILE	0	\N
70	6	0	CAPTURE_STEP_PERFORMANCE	0	N
71	6	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
72	6	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
49	5	0	UNIQUE_CONNECTIONS	0	N
50	5	0	FEEDBACK_SHOWN	0	Y
51	5	0	FEEDBACK_SIZE	50000	\N
52	5	0	USING_THREAD_PRIORITIES	0	Y
53	5	0	SHARED_FILE	0	\N
54	5	0	CAPTURE_STEP_PERFORMANCE	0	N
55	5	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
56	5	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
57	3	0	UNIQUE_CONNECTIONS	0	N
58	3	0	FEEDBACK_SHOWN	0	Y
59	3	0	FEEDBACK_SIZE	50000	\N
60	3	0	USING_THREAD_PRIORITIES	0	Y
61	3	0	SHARED_FILE	0	\N
62	3	0	CAPTURE_STEP_PERFORMANCE	0	N
63	3	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
64	3	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
449	16	0	UNIQUE_CONNECTIONS	0	N
450	16	0	FEEDBACK_SHOWN	0	Y
451	16	0	FEEDBACK_SIZE	50000	\N
452	16	0	USING_THREAD_PRIORITIES	0	Y
453	16	0	SHARED_FILE	0	\N
454	16	0	CAPTURE_STEP_PERFORMANCE	0	N
455	16	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
456	16	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
227	10	0	FEEDBACK_SIZE	50000	\N
228	10	0	USING_THREAD_PRIORITIES	0	Y
229	10	0	SHARED_FILE	0	\N
230	10	0	CAPTURE_STEP_PERFORMANCE	0	N
231	10	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
232	10	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
273	9	0	UNIQUE_CONNECTIONS	0	N
274	9	0	FEEDBACK_SHOWN	0	Y
275	9	0	FEEDBACK_SIZE	50000	\N
276	9	0	USING_THREAD_PRIORITIES	0	Y
277	9	0	SHARED_FILE	0	\N
278	9	0	CAPTURE_STEP_PERFORMANCE	0	N
279	9	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
280	9	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
241	8	0	UNIQUE_CONNECTIONS	0	N
242	8	0	FEEDBACK_SHOWN	0	Y
243	8	0	FEEDBACK_SIZE	50000	\N
244	8	0	USING_THREAD_PRIORITIES	0	Y
245	8	0	SHARED_FILE	0	\N
246	8	0	CAPTURE_STEP_PERFORMANCE	0	N
247	8	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
248	8	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
249	7	0	UNIQUE_CONNECTIONS	0	N
250	7	0	FEEDBACK_SHOWN	0	Y
251	7	0	FEEDBACK_SIZE	50000	\N
252	7	0	USING_THREAD_PRIORITIES	0	Y
253	7	0	SHARED_FILE	0	\N
254	7	0	CAPTURE_STEP_PERFORMANCE	0	Y
255	7	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
256	7	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
281	12	0	UNIQUE_CONNECTIONS	0	N
282	12	0	FEEDBACK_SHOWN	0	Y
283	12	0	FEEDBACK_SIZE	50000	\N
284	12	0	USING_THREAD_PRIORITIES	0	Y
285	12	0	SHARED_FILE	0	\N
286	12	0	CAPTURE_STEP_PERFORMANCE	0	N
287	12	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
288	12	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
433	13	0	UNIQUE_CONNECTIONS	0	N
434	13	0	FEEDBACK_SHOWN	0	Y
435	13	0	FEEDBACK_SIZE	50000	\N
436	13	0	USING_THREAD_PRIORITIES	0	Y
437	13	0	SHARED_FILE	0	\N
438	13	0	CAPTURE_STEP_PERFORMANCE	0	N
439	13	0	STEP_PERFORMANCE_CAPTURING_DELAY	1000	\N
440	13	0	STEP_PERFORMANCE_LOG_TABLE	0	\N
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
10	6	19	22	Y
11	6	17	19	Y
12	6	18	20	Y
13	6	20	21	Y
14	6	21	17	Y
134	12	172	173	Y
70	10	101	103	Y
71	10	103	102	Y
209	16	279	278	Y
210	16	277	280	Y
200	14	264	266	Y
201	14	265	264	Y
3	3	10	12	Y
4	3	11	13	Y
5	3	12	14	Y
6	3	14	11	Y
7	3	14	15	Y
8	3	15	16	Y
9	3	16	11	Y
202	14	267	265	Y
203	14	266	268	Y
211	16	280	281	Y
212	16	281	282	Y
213	16	281	283	Y
214	16	283	279	Y
89	8	124	122	Y
15	1	24	26	Y
16	1	26	28	Y
17	1	28	23	Y
18	1	25	27	Y
19	1	23	29	Y
20	1	29	25	Y
90	8	122	123	Y
91	7	128	127	Y
92	7	128	126	Y
93	7	129	125	Y
94	7	125	128	Y
204	13	273	270	Y
205	13	272	271	Y
206	13	271	273	Y
207	15	274	275	Y
112	11	148	150	Y
113	11	149	151	Y
114	11	151	152	Y
115	11	152	148	Y
116	11	150	153	Y
117	9	162	154	Y
118	9	158	157	Y
119	9	161	160	Y
120	9	160	159	Y
121	9	159	155	Y
122	9	163	164	Y
123	9	157	156	Y
124	9	156	161	Y
125	9	154	166	Y
126	9	166	165	Y
127	9	165	167	Y
128	9	168	170	Y
129	9	169	168	Y
208	15	275	276	Y
130	9	167	169	Y
131	9	170	158	Y
132	9	155	171	Y
133	9	171	163	Y
\.


--
-- Data for Name: r_trans_note; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_trans_note (id_transformation, id_note) FROM stdin;
1	1
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
3	14	1
7	128	2
16	281	5
\.


--
-- Data for Name: r_transformation; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_transformation (id_transformation, id_directory, name, description, extended_description, trans_version, trans_status, id_step_read, id_step_write, id_step_input, id_step_output, id_step_update, id_database_log, table_name_log, use_batchid, use_logfield, id_database_maxdate, table_name_maxdate, field_name_maxdate, offset_maxdate, diff_maxdate, created_user, created_date, modified_user, modified_date, size_rowset) FROM stdin;
14	6	Add Stock Variables	\N	\N	\N	1	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-09 16:29:23.362	jason	2009-02-10 11:03:03.521	10000
2	1	Atrius Immunizations	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-01-26 13:32:27.581	jason	2009-01-26 15:05:57.235	10000
4	0	Prepare Staging Area	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-01-26 15:18:03.574	jason	2009-01-26 15:18:03.574	10000
13	6	Load Patient	\N	\N	\N	1	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-09 15:17:52.867	jason	2009-02-10 11:06:08.303	10000
5	1	Load Atrius demographics to staging	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-01-26 15:52:59.826	jason	2009-01-26 15:52:59.826	10000
15	6	Load LOINC db	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-12 16:53:19.161	jason	2009-02-12 16:55:30.498	10000
8	2	Load Patient Dimension	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-05 11:12:38.005	jason	2009-02-05 16:08:15.316	10000
7	2	Load Provider Dimension	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-05 10:15:32.152	jason	2009-02-05 16:08:23.559	10000
3	1	Read Atrius Demographic Info	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-01-26 13:55:36.942	jason	2009-01-26 16:59:18.354	10000
11	2	Load External Code to LOINC map	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-05 16:35:42.653	jason	2009-02-05 16:38:29.238	10000
9	2	Load Lab Result Fact	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-05 13:15:57.756	jason	2009-02-05 16:46:07.881	10000
6	0	North Adams code map - straight to db	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-01-23 10:20:13.692	jason	2009-01-27 11:31:32.026	10000
12	5	Load Epic Patient to Staging	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-09 09:50:07.793	jason	2009-02-09 10:00:56.125	10000
16	6	Load External Code to LOINC Maps	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-17 16:57:47.253	jason	2009-02-17 17:47:31.617	10000
1	0	North Adams code map	\N	\N	\N	0	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-01-23 10:20:13.692	jason	2009-01-27 15:18:17.674	10000
10	0	Transformation 1	\N	\N	\N	-1	-1	-1	-1	-1	-1	-1	\N	Y	N	-1	\N	\N	0.00	0.00	jason	2009-02-05 15:00:01.879	jason	2009-02-05 15:02:56.554	10000
\.


--
-- Data for Name: r_user; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_user (id_user, id_profile, login, password, name, description, enabled) FROM stdin;
1	1	admin	2be98afc86aa7f2e4cb79ce71da9fa6d4	Administrator	User manager	Y
2	3	guest	2be98afc86aa7f2e4cb79ce77cb97bcce	Guest account	Read-only guest account	Y
3	2	jason	\N	Jason Mcvetta	\N	Y
\.


--
-- Data for Name: r_value; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_value (id_value, name, value_type, value_str, is_null) FROM stdin;
1	constant	String	UNKNOWN	N
\.


--
-- Data for Name: r_version; Type: TABLE DATA; Schema: public; Owner: pdi
--

COPY r_version (id_version, major_version, minor_version, upgrade_date, is_upgrade) FROM stdin;
1	3	0	2009-01-22 15:17:10.351	N
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

