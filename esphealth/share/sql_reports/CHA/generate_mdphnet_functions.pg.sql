CREATE OR REPLACE FUNCTION center(fake_patid varchar) RETURNS varchar AS $$
DECLARE
   c char;
   center varchar(10) := '';
BEGIN
   c := UPPER(SUBSTR(fake_patid, 6, 1));

   CASE
     WHEN c >= '0' and c <= '9' THEN center := 'Center 0-9';
     WHEN c >= 'A' and c <= 'M' THEN center := 'Center A-M';
     WHEN c >= 'N' and c <= 'Z' THEN center := 'Center N-Z';
     ELSE center = 'UNKNOWN';
   END CASE;

   RETURN center;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION age_at_year_start(encounterdate date, birthdate date)
RETURNS integer AS $$
DECLARE
   age_at_year_start integer;
BEGIN
   IF encounterdate IS NULL OR birthdate IS NULL THEN
      RETURN NULL;
   END IF;

   age_at_year_start := date_part('year',
                                  age(date_trunc('year', encounterdate),
                                      birthdate));

   RETURN age_at_year_start;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION age_group_5yr(encounterdate date, birthdate date)
RETURNS varchar AS $$
DECLARE
   age integer;
   age_group varchar(5) := '';
BEGIN
   IF encounterdate IS NULL OR birthdate IS NULL THEN
      RETURN NULL;
   END IF;

   age := age_at_year_start(encounterdate, birthdate);

   CASE
     WHEN age <= 4  THEN age_group := '0-4';
     WHEN age <= 9  THEN age_group := '5-9'; 
     WHEN age <= 14 THEN age_group := '10-14'; 
     WHEN age <= 19 THEN age_group := '15-19'; 
     WHEN age <= 24 THEN age_group := '20-24'; 
     WHEN age <= 29 THEN age_group := '25-29'; 
     WHEN age <= 34 THEN age_group := '30-34'; 
     WHEN age <= 39 THEN age_group := '35-39'; 
     WHEN age <= 44 THEN age_group := '40-44'; 
     WHEN age <= 49 THEN age_group := '45-49'; 
     WHEN age <= 54 THEN age_group := '50-54'; 
     WHEN age <= 59 THEN age_group := '55-59'; 
     WHEN age <= 64 THEN age_group := '60-64'; 
     WHEN age <= 69 THEN age_group := '65-69'; 
     WHEN age <= 74 THEN age_group := '70-74'; 
     WHEN age <= 79 THEN age_group := '75-79'; 
     WHEN age <= 84 THEN age_group := '80-84'; 
     WHEN age <= 89 THEN age_group := '85-89'; 
     WHEN age <= 94 THEN age_group := '90-94'; 
     WHEN age <= 99 THEN age_group := '95-99'; 
     ELSE age_group := '100+'; 
   END CASE;

   RETURN age_group;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION age_group_10yr(encounterdate date, birthdate date)
RETURNS varchar AS $$
DECLARE
   age integer;
   age_group varchar(5) := '';
BEGIN
   IF encounterdate IS NULL OR birthdate IS NULL THEN
      RETURN NULL;
   END IF;

   age := age_at_year_start(encounterdate, birthdate);

   CASE
     WHEN age <= 9  THEN age_group := '0-9'; 
     WHEN age <= 19 THEN age_group := '10-19'; 
     WHEN age <= 29 THEN age_group := '20-29'; 
     WHEN age <= 39 THEN age_group := '30-39'; 
     WHEN age <= 49 THEN age_group := '40-49'; 
     WHEN age <= 59 THEN age_group := '50-59'; 
     WHEN age <= 69 THEN age_group := '60-69'; 
     WHEN age <= 79 THEN age_group := '70-79'; 
     WHEN age <= 89 THEN age_group := '80-89'; 
     WHEN age <= 99 THEN age_group := '90-99'; 
     ELSE age_group := '100+'; 
   END CASE;

   RETURN age_group;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION age_group_ms(encounterdate date, birthdate date)
RETURNS varchar AS $$
DECLARE
   age integer;
   age_group varchar(5) := '';
BEGIN
   IF encounterdate IS NULL OR birthdate IS NULL THEN
      RETURN NULL;
   END IF;

   age := age_at_year_start(encounterdate, birthdate);

   CASE
     WHEN age <= 1  THEN age_group := '0-1';
     WHEN age <= 4  THEN age_group := '2-4'; 
     WHEN age <= 9  THEN age_group := '5-9'; 
     WHEN age <= 14 THEN age_group := '10-14'; 
     WHEN age <= 18 THEN age_group := '15-18'; 
     WHEN age <= 21 THEN age_group := '19-21'; 
     WHEN age <= 44 THEN age_group := '22-44'; 
     WHEN age <= 64 THEN age_group := '45-64'; 
     WHEN age <= 74 THEN age_group := '65-74'; 
     ELSE age_group := '75+'; 
   END CASE;

   RETURN age_group;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION icd9_prefix(icd9_code varchar, len integer)
RETURNS varchar AS $$
DECLARE
   first_char varchar(1) := '';
   adjusted_len int := len;
   icd9_no_period varchar(20);
BEGIN
   IF icd9_code IS NULL THEN
      RETURN NULL;
   END IF;

   first_char := substr(icd9_code, 6, 1);
   IF first_char NOT IN ('0','1','2','3','4','5','6','7','8','9') THEN
      adjusted_len := adjusted_len + 1;
   ELSIF strpos(substr(icd9_code,6),'.')=3 THEN
      adjusted_len := adjusted_len - 1;
   END IF;

   icd9_no_period = replace(substr(icd9_code,6), '.', '');

   RETURN substr(icd9_no_period, 1, adjusted_len);
END;
$$ LANGUAGE plpgsql;
