The files in this directory can be used to generate and maintain a schema of
reporting functions, tables and views for MDPHNET, as well as some additional
reports for ILI surveillance, gestational diabetes, the general population 
reports, etc.  

To some extent, these scripts may be modified for site specific data and 
installation paths, and so are maintained in separate site specific 
repositories.

General instructions are:

To generate the MDPHNET schema, first create the mdphnet user and schema. 
As a superuser (postgres) connect to the database in which the user and schema 
will be created.  

Create the user: CREATE USER esp_mdphnet WITH PASSWORD 'xxxx'
Then create the schema: CREATE SCHEMA esp_mdphnet AUTHORIZATION esp_mdphnet;
Grant the esp_mdphnet user select on all ESP tables. Generate and execute a 
script:

SELECT 'GRANT SELECT ON '||tablename||' TO esp_mdphnet;'
FROM pg_tables WHERE schemaname = '[name of esp system schema]';

Modify gen_mdphnet.sh to reflect the local database name and esp_mdphnet schema 
owner (authorized user).

The gen_mdphnet.sh script need only be run once.  This populates the 
esp_mdphnet schema with mdphnet reporting tables.

If there is a linux user esp_mdphnet, modify pg_hba.conf to enable psql scripts 
to be run via crontab without a requiring a password.  Otherwise, modify 
pg_hba.conf and pg_idnet.conf to enable the a linux user other than esp_mdphnet 
to run psql scripts without requiring a password.schema.

Modify update_mdphnet.sh to reflext the local database name and esp_mdphnet
schema owner (authorized user).

Add an entry in crontab to run update_mdphnet.sh.  If you wish to enure that 
this runs on completion of daily ESP data load, you should create a separate
script that runs update_mdphnet.sh contingent on successful completion of the
ESP load.  (Use the && operator).

Part of the mdphnet schema are a set of summary tables that are not currently 
used, but which require considerable resources to keep up to date.  It is 
advised to update these tables over the weekend, when system resources are 
typically under used. This is weekly_update_mdphnet_summary_tables.pg.sql. 
Add a crontab entry to run this weekly over the weekend.

The ILI report is based on a SUN-SAT week structure.  The report script 
ili_report.sh should be run after data from SAT has been loaded.  Modify
script variables as appropriate.

There is also script for running the general population report.  
