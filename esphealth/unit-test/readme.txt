unit test documentation for esp
author: carolina chacin
updated: dec 9 2011


VAERS
Definitions.py defines SYNDROME_NAMES ('ili', 'haemotological','lymphatic','rash','lesions',
'respiratory','lower_gi': 'Lower GI',  'upper_gi','neuro') 
this is the list of type of events that esp can generate. 
Once per installation run ./bin/esp set_rules to load the heuristics.
to run vaers run the main.py program with the parameters defined in the main.py: 
-b[egin_date] -e[nd_date]  { [-d --detect],[-r --reports] } | [-f --full]
ie run the main.py -b 19980604 -e 20111202 -a -c -d -r
if the list of sites are not loaded, the command will load the list of sites listed in definitions.py 
to trigger vaers events, a patient must have an encounter associated (siteid, sitename) with one of the sites
which is not a specialty clinic (ones without the asterisks in the code), event type has to be URGENT CARE and
have one or more icd9 codes referred to in definitions.py and have occurred within the dates passed in.

SS
to run SS run the main.py with the parameters defined in main.py:
-b[start_date as 20090101] -e[end_date] { [-d --detect],[-r --reports], [-s --syndrome def all], 
  [-i', '--individual'],[-t', '--satscan'],  [--hsph'] }| [-f --full] [-c --consolidate]"""
ie run the main.py -b 19980604 -e 20111202 -d -s ili -c -r
Detection is based on the syndrome heuristics defined in heuristics.py, 
and the type of events are the same as VAERS SYNDROME_NAMES also defined in heuristics.py
to trigger these events, a patient must have an encounter with one of the sites that is not a specialty clinic,
and have event type = URGENT CARE, have occurred within the passed in date, have the conditions defined in the heuristics, 
for ili it must have temperature >100 and one ili icd9 fever codes as defined in InfluenzaHeuristic, 
for hematological and rash they are defined in OptionalFeverSyndromeHeuristic,
the rest are as defined in SyndromeHeuristic which just checks that the icd9 code name contains the name of the syndrome

to test that we can generate events and cases for all the diseases below, 
load the ETL files from the corresponding folder using the load_epic command, 
and then run concordance, map the lab if necessary, run hef and nodis: (assuming you are on the esp3)
./bin/esp load_epic --input /home/esp/workspace/esp3/doc/unit-test/<disease name>

to extract more cases from data loaded: run the extract_epic command it outputs to /srv/esp-data/fake

the folders below have the files with patients, labs, meds, providers and encounters and vaccinations
they only test some basic events/cases, not all the heuristics are included. 
Definitions for the heuristics can be found in nodis/events.py and hef/defs.py in 2.2 
in esp 3 they are under src/disease-<d name>/<d name>.py and 
heuristics and disease notification base definitions are under hef and nodis folders in the base.py
ili/vaers
chlamydia
pertussis
tb
acute hep a
syphillis

