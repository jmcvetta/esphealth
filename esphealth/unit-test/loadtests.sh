./bin/esp load_epic --input ./unit-test/chlamydia --reload
./bin/esp load_epic --input ./unit-test/lyme --reload
./bin/esp load_epic --input ./unit-test/pid --reload
./bin/esp load_epic --input ./unit-test/asthma --reload
./bin/esp load_epic --input ./unit-test/giardiasis --reload
./bin/esp load_epic --input ./unit-test/gonorrhea --reload
./bin/esp load_epic --input ./unit-test/pertussis --reload
./bin/esp load_epic --input ./unit-test/syphilis --reload
./bin/esp load_epic --input ./unit-test/tb --reload
./bin/esp load_epic --input ./unit-test/ili --reload
./bin/esp load_epic --input ./unit-test/empty --reload
./bin/esp load_epic --input ./unit-test/vaers --reload
./bin/esp load_epic --input ./unit-test/acute_hep_a --reload
./bin/esp load_epic --input ./unit-test/acute_hep_b --reload
./bin/esp load_epic --input ./unit-test/acute_hep_c --reload
./bin/esp load_epic --input ./unit-test/diabetes/frank --reload
./bin/esp load_epic --input ./unit-test/diabetes/gestational-diabetes --reload
./bin/esp load_epic --input ./unit-test/diabetes/pre --reload

./bin/esp concordance 
./bin/esp hef
./bin/esp nodis
./bin/esp case_report --status=AR --mdph
./bin/esp report diabetes:frank
./bin/esp report diabetes:gestational
./bin/esp report diabetes:prediabetes

