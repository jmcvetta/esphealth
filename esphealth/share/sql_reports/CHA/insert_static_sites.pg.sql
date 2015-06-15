--this code assumes that static_sitegroups has been loaded
--sitegroups should be a small table completely specified on a site-specific
--basis.  Either manually entered, or loaded from CSV.
--Also required is a table that maps encounter sites to the sitegroups.
--This is named bz_sites below.  
﻿insert into static_site (name, group_id, ili_site)
select t1.site_name, t2.group, TRUE 
from bz_sites t0,
     (select distinct site_name, site_natural_key from emr_encounter) t1,
     static_sitegroup t2
where t2.zip5=t0.zip 
      and t0.site_id=t1.site_natural_key;
insert into static_site (name, group_id, ili_site)
select distinct t1.site_name, t2.group, FALSE
from bz_sites t0,
     (select distinct site_name, site_natural_key from emr_encounter) t1,
     static_sitegroup t2
where t0.site_id=t1.site_natural_key
      and position(t2.location in t1.site_name) > 0
      and not exists (select null from static_site t3
                      where t3.name = t1.site_name);
