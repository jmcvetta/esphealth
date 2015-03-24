unit test documentation for esp
author: carolina chacin
updated: dec 7 2011


VAERS
definitions.py defines SYNDROME_NAMES ('ili', 'haemotological','lymphatic','rash','lesions',
'respiratory','lower_gi': 'Lower GI',, 'upper_gi','neuro') 
which is the list of type of events that it can generate. 
once per installation run ./bin/esp set_rules to load the heuristics.
to run vaers run the main.py program with the parameters defined in the main.py: 
-b[egin_date] -e[nd_date]  { [-d --detect],[-r --reports] } | [-f --full]
ie run the main.py -b 19980604 -e 20111202 -a -c -d -r
if the list of sites are not loaded the command will load the list of sites listed in definitions.py 
to trigger vaers events, a patient must have an encounter associated (siteid, sitename) with one of the sites
that is not specialty clinic in the list above (ones without the asterisks) , event type = URGENT CARE and
have one or more icd9 codes referred to in this definitions.py and have occurred within the dates passed in.

SS
to run SS run the main.py with the parameters defined in main.py:
-b[start_date as 20090101] -e[end_date] { [-d --detect],[-r --reports], [-s --syndrome def all], 
  [-i', '--individual'],[-t', '--satscan'],  [--hsph'] }| [-f --full] [-c --consolidate]"""
ie run the main.py -b 19980604 -e 20111202 -d -s ili -c -r
the detection is based on the syndrome heuristics defined in heuristics.py, 
and the type of events  are the same as VAERS SYNDROME_NAMES also defined in heuristics.py
to trigger these events, a patient must have an encounter with one of the sites that is not a specialty clinic,
and event type = URGENT CARE, have occurred within the passed in date, have the conditions defined in the heuristics, 
for ili must have temperature >100 and one ili icd9 fever codes as defined in InfluenzaHeuristic, 
for hematological and rash they are defined in OptionalFeverSyndromeHeuristic,
the rest are as defined in SyndromeHeuristic which just checks that the icd9 code name contains the name of the syndrome

for all the diseases below load the ETL files from the corresponding folder using the load epic command, 
and run hef and nodis

ili

chlamydia

pertussis

tb

acute hep a

syphillis

