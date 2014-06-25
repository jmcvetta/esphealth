./bin/esp load_epic --input /srv/esp-data/fake/chlamydia --reload
./bin/esp load_epic --input /srv/esp-data/fake/lyme --reload
./bin/esp load_epic --input /srv/esp-data/fake/pid --reload
./bin/esp load_epic --input /srv/esp-data/fake/asthma --reload
./bin/esp load_epic --input /srv/esp-data/fake/giardiasis --reload
./bin/esp load_epic --input /srv/esp-data/fake/gonorrhea --reload
./bin/esp load_epic --input /srv/esp-data/fake/pertussis --reload
./bin/esp load_epic --input /srv/esp-data/fake/syphilis --reload
./bin/esp load_epic --input /srv/esp-data/fake/tb --reload
./bin/esp load_epic --input /srv/esp-data/fake/ili --reload
./bin/esp load_epic --input /srv/esp-data/fake/empty --reload
./bin/esp load_epic --input /srv/esp-data/fake/vaers --reload
./bin/esp load_epic --input /srv/esp-data/fake/acute_hep_a --reload
./bin/esp load_epic --input /srv/esp-data/fake/acute_hep_b --reload
./bin/esp load_epic --input /srv/esp-data/fake/acute_hep_c --reload
./bin/esp load_epic --input /srv/esp-data/fake/diabetes/frank --reload
./bin/esp load_epic --input /srv/esp-data/fake/diabetes/gestational-diabetes --reload
./bin/esp load_epic --input /srv/esp-data/fake/diabetes/pre --reload

./bin/esp concordance 
./bin/esp hef
./bin/esp nodis
./bin/esp case_report --status=AR --mdph
./bin/esp report diabetes:frank
./bin/esp report diabetes:gestational
./bin/esp report diabetes:prediabetes

