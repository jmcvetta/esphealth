#!/usr/bin/env python

import time, string, fileinput
from time import strftime
from ESP.nodis.models import Case

f = open("mh_chlamydia_hl7.txt", "w")

for c in Case.objects.filter(condition='chlamydia'):

    pd = {"lab_seq_no":"0123456789", "mrn":c.patient.mrn, "last_name":c.patient.last_name, "first_name":c.patient.first_name, \
          "middle_name":c.patient.middle_name, "suffix":c.patient.suffix, "date_of_birth":c.patient.date_of_birth, "gender":c.patient.gender, \
          "race":c.patient.race, "address1":c.patient.address1, "address2":c.patient.address2, "city":c.patient.city, "state":c.patient.state, \
          "zip":c.patient.zip, "country":c.patient.country, "areacode":c.patient.areacode, "tel":c.patient.tel, "tel_ext":c.patient.tel_ext}
    pd['get_long_date'] = strftime("%Y-%m-%d %H:%M:%S")
    pd['get_short_date'] = strftime("%Y-%m-%d")
    
    MSH = string.Template("MSH|^~\\&||MetroHealth System Laboratory^36D0336261^CLIA|OHDOH|OH|$get_long_date||ORU^ R01|$get_short_date$lab_seq_num|T|2.3.1<hex 0D0A>\n")
    PID = string.Template("PID|1||$mrn^^^^^||$last_name^$first_name^$middle_name^$suffix||$date_of_birth|$gender||$race|$address1^$address2^$city^$state^$zip^$country^||^^^^^$areacode^$tel^$tel_ext|||||||||||||||||| |<hex 0D0A>\n" )
    NK1 = string.Template("NK1||||||<hex 0D0A>\n")
    ORC = string.Template("ORC|||||||||||||||||||||MetroHealth System|||||<hex 0D0A>\n")
    
    print "keith"
    #print PID.substitute(pd)
    #print NKI.substitute(pd)
    #print ORC.substitute(pd)
    
    for d in c.lab_results.all():
        ld = {"specimen_num":d.specimen_num, "native_code":d.native_code, "native_name":d.native_name, "lab_date":d.date, \
              "status":d.status, "result_float":d.result_float, "ref_unit":d.ref_unit, "ref_low":d.ref_low, "ref_high":d.ref_high}
        
    OBR = string.Template("OBR|1||$specimen_num|^^^$native-code^$native_name^L|||$lab_date||||||||||||||||||$status<hex0D0A\n")
    OBX = string.Template("OBX|1|NM|^^^$native_code^$native_name^L|1|$float|$ref_unit^^ISO|$ref_low-$ref_low|||||$status||||$lab_date|hex 0D0A\n")
        
#f.close()
 #f.write
