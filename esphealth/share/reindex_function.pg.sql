create or replace function reindex_if_bloated() returns void as $$
declare
  bloat cursor for SELECT
                     schemaname, iname, 
                     ROUND(CASE WHEN iotta=0 OR ipages=0 THEN 0.0 ELSE ipages/iotta::numeric END,1) AS ibloat
                   FROM ( SELECT
                            schemaname, tablename, cc.reltuples, cc.relpages, bs,
                            COALESCE(c2.relname,'?') AS iname, COALESCE(c2.reltuples,0) AS ituples, COALESCE(c2.relpages,0) AS ipages,
                            COALESCE(CEIL((c2.reltuples*(datahdr-12))/(bs-20::float)),0) AS iotta 
                          FROM ( SELECT
                                   ma,bs,schemaname,tablename,
                                   (datawidth+(hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)))::numeric AS datahdr
                                 FROM ( SELECT
                                          schemaname, tablename, hdr, ma, bs,
                                          SUM((1-null_frac)*avg_width) AS datawidth
                                        FROM pg_stats s, ( SELECT
                                                             (SELECT current_setting('block_size')::numeric) AS bs,
                                                             CASE WHEN substring(v,12,3) IN ('8.0','8.1','8.2') THEN 27 ELSE 23 END AS hdr,
                                                             CASE WHEN v ~ 'mingw32' THEN 8 ELSE 4 END AS ma
                                                           FROM (SELECT version() AS v) AS foo
                                                         ) AS constants
                                        GROUP BY 1,2,3,4,5
                                      ) AS foo
                               ) AS rs
                          JOIN pg_class cc ON cc.relname = rs.tablename
                          JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname AND nn.nspname <> 'information_schema'
                          JOIN pg_index i ON indrelid = cc.oid
                          JOIN pg_class c2 ON c2.oid = i.indexrelid
                        ) AS sml
                   ORDER BY ibloat desc;
begin
  FOR indrec in bloat loop
    if indrec.ibloat > 2 then
      execute immediate 'reindex index ' || indrec.schemaname || '.' || indrec.iname;
    else 
      exit;
    end if;
  end loop; 
end;
$$ language plpgsql;
