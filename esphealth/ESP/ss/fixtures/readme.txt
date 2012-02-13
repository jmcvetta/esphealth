load the site_atrius.json file after running syncdb or at any point to load the clinics

create the ss_site table by installing the ss app

Site(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    zip_code = models.CharField(max_length=10, db_index=True)

    
or running the following sql script:
        
-- Table: ss_site

-- DROP TABLE ss_site;

CREATE TABLE ss_site
(
  code character varying(20) NOT NULL,
  "name" character varying(200) NOT NULL,
  zip_code character varying(10) NOT NULL,
  CONSTRAINT ss_site_pkey PRIMARY KEY (code),
  CONSTRAINT ss_site_name_key UNIQUE (name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE ss_site OWNER TO esp;

-- Index: ss_site_zip_code

-- DROP INDEX ss_site_zip_code;

CREATE INDEX ss_site_zip_code
  ON ss_site
  USING btree
  (zip_code);

-- Index: ss_site_zip_code_like

-- DROP INDEX ss_site_zip_code_like;

CREATE INDEX ss_site_zip_code_like
  ON ss_site
  USING btree
  (zip_code varchar_pattern_ops);

run this command to load the data:
./bin/esp loaddata --database <dbname> site.json