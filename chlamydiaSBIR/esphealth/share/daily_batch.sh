#!/bin/bash
if [ "$(ls -A /srv/esp/data/epic/incoming)" ]; then
  cd /srv/esp/data/epic/incoming
  set -e
  (
    flock -e -w 10 201
    sleep 1m
    find -type f -size 0 -delete
    /srv/esp/prod/bin/esp load_epic -l 
    ( for line in `/srv/esp/prod/bin/esp hef --list`; do
        sleep 5
        sqlProc=$(psql esp30 -c "select count(*) from pg_stat_activity" -t | tr -d ' \n') 
        while [ "$sqlProc" -ge "9" ]; do
            sleep 5
            sqlProc=$(psql esp30 -c "select count(*) from pg_stat_activity" -t | tr -d ' \n')
        done
        ( /srv/esp/prod/bin/esp hef "$line" ) &
      done 
      wait ) && \
    ( nodislis=( pertussis tuberculosis )
      for nodisval in "${nodislis[@]}"; do
        sleep 5
        sqlProc=$(psql esp30 -c "select count(*) from pg_stat_activity" -t | tr -d ' \n')
        while [ "$sqlProc" -ge "9" ]; do
            sleep 5
            sqlProc=$(psql esp30 -c "select count(*) from pg_stat_activity" -t | tr -d ' \n')
        done
        ( /srv/esp/prod/bin/esp nodis $nodisval ) &
      done
      wait ) && \
    /srv/esp/prod/bin/esp status_report --send-mail
  ) 201>/home/esp31/LCK..esp31
fi
