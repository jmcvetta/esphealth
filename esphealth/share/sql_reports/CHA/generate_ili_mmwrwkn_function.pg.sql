CREATE OR REPLACE FUNCTION mmwrwkn(date4week date) RETURNS varchar AS $$
DECLARE
   yr integer;
   adjyr integer;
   mth integer;
   dy integer;
   tdys integer;
   wk integer;
   doyr integer;
   priorleap boolean;
   Jan1weekday integer;
   curweekday integer;
   wwyyv varchar(40);
BEGIN
   yr := to_char(date4week,'yyyy');
   mth := to_char(date4week,'mm');
   dy := to_char(date4week,'dd');
   if (yr % 4 = 0  and  yr % 100 != 0) or yr % 400 = 0 then
      tdys := 366;
   else
      tdys := 365;
   end if;
   if ((yr-1) % 4 = 0 and (yr-1) % 100 != 0) or (yr-1) % 400 = 0 then
      priorleap := True;
   else
      priorleap := False;
   end if;
   doyr := extract(doy from date4week);
   jan1weekday := extract(dow from (yr||'-01-01')::date)+1;
   curweekday:= extract(dow from date4week)+1;
   if doyr <= (8-jan1weekday) and jan1weekday > 4 then
      adjyr := yr - 1;
      if jan1weekday = 5 or (jan1weekday = 6 and priorleap) then
         wk = 53;
      else 
         wk = 52;
      end if;
   else 
       adjyr := yr;
   end if;
   if adjyr = yr and (tdys - doyr) < (4 - curweekday) then
      adjyr = yr + 1;
      wk = 1;
   end if;
   if adjyr = yr then
      wk := (doyr + (7 - curweekday) + (jan1weekday -1))/7;
      if jan1weekday > 4 then
         wk := wk - 1;
      end if;
   end if;
   wwyyv := substring(trim(to_char(adjyr,'9999')),3,2)||trim(to_char(wk,'00'));
   return wwyyv;
END;
$$ LANGUAGE plpgsql;
