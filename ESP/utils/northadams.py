"""
# configuration data for hl7_to_etl.py
# North Adams HL7
# parse sudha's messages
# ross lazarus
# march 2008
# for the ESP project
# moving to North Adams
# message type ADT^A04 has obx vital signs, allergies, demog and pcp
# ORU^R01 has lab results and each test may have multiple lines of report that
# need to be stitched together...
# VXU^V04 is immunization with RXA
# PPR^PC1 has PRB
# OMP^O09 has RXO
Plan is to collect these messages as they arrive over a period and
process them all into the Atrius ETL format - so 1 (and only 1!) record for each
PCP and demographic record in each period, with as many Ex, Rx, Lx, Imx, Allergy
file rows as needed.


We need
1) a new encounter record for each unique PVX PID/visit with all the diagnoses for that visit
2) a new Rx record for each unique RXO record in each OMP message
3) a new Lx record for each unique OBX test code in each ORU message
4) a new allergy record for each new ADT message
5) a new immunization record for each RXA in any VXU message

"""

sdelim = '|'
sfdelim = '^'
etldelim = '^'
msh = 'MSH'
OURSTATE = 'MA' # for pcp state if applicable
OURCOUNTRY = 'USA' # for demog country if desired

# some constants for local use - these depend on the specifications
PATIENT_ID = 'Patient_ID' # this may need adjustment - we use the constant in code so it can be changed here
PCP_NPI = 'Attending_Provider_NPI'
FACILITY_NAME = 'Facility_Name' # emergency key if npi not provided
LABRES_CODE = 'Attribute_Code'
LABRES_VALUE = 'Attribute_Value'
MESSAGE_TYPE = 'Message_Type'
ADM_DATE_TIME = 'Admit_Date_and_Time'

# this structure describes the permissible segments for each message type
# and the names we're using for each list of instances
# we use these to prepare the ETL files.
mtypedict={'ADT':{'PV1':'pcp','ENC': 'enc', 'DG1':'enc','OBX':'vitals','AL1':'allergies','PD1':'extrademog'},
           'ORU':{'PV1':'pcp','ENC': 'enc','OBR':'laborder','OBX':'labres'},
           'VXU':{'PV1':'pcp','ENC': 'enc','RXA':'vaccinations'},
           'PPR':{'PV1':'pcp','ENC': 'enc','PRB':'problems'},
           'OMP':{'PV1':'pcp','ENC': 'enc','RXO':'rx'}}

# this defines the output keys
etlnames = ['pcp','pid','allergies','enc',
            'laborder','labres','vaccinations','problems',
            'rx']

# this defines the output file names
#outfilenames = ['esp_pcp','esp_demog','esp_enc','esp_allergy',
#            'esp_lx','esp_lx','esp_imm','esp_prob','esp_rx']

outfilenames = ['epicpro.esp.04152008','epicmem.esp.04152008',
                'epicall.esp.04152008','epicvis.esp.04152008',
                'epicord.esp.04152008','epicres.esp.04152008','epicimm.esp.04152008',
                'epicprb.esp.04152008',
                'epicmed.esp.04152008']

## the following lists control the way output ETL records are written
## each output file has a lookup list of element names from
## the grammar or an empty string for each element to be output
## The writer will use the element name to get the value
## or just pass through the empty string

## pid file has provCode,provLast_Name,provFirst_Name,
##    provMiddle_Initial,provTitle, provPrimary_Dept_Id,
##    provPrimary_Dept,provPrimary_Dept_Address_1,
##    provPrimary_Dept_Address_2,provPrimary_Dept_City,
##    provPrimary_Dept_State,provPrimary_Dept_Zip,
##    provTelAreacode,provTel)
##
## the pcp grammar has
##    Set_ID	1
##    Patient_Class	2
##    Facility_Name	3
##    Attending_Provider_NPI	7.0
##    Attending_Provider_last_name	7.1
##    Attending_Provider_First_name	7.2
##    Referring_Provider_NPI	8.0
##    Referring_Provider_last_name	8.1
##    Referring_Provider_First_name	8.2
##    Visit_Number	19
##    Admit_Date_and_Time	44

pcp_lookup = [PCP_NPI,
              'Attending_Provider_last_name',
              'Attending_Provider_First_name',
              '','','',
              FACILITY_NAME,'','','',OURSTATE,'',
              '','']

enc_lookup = [PATIENT_ID,
              PATIENT_ID,
              'Visit_Number',
              'Admit_Date_and_Time',
              '','',PCP_NPI,'',
              '','','','',
              '','','','',
              '','','','Diagnosis_Code']


#diags_lookup = [PATIENT_ID,
#                                PATIENT_ID,
#                                '',
#                                'Diagnosis_Date_and_Time',
#                                '','',PCP_NPI,'',
#                                '','','','',
#                                '','','','',
#                                '','','','Diagnosis_Code']



## note that we provide an empty string for any column that we cannot fill
## the etlWriter will take care of that. Note also that some longer constants are
## used to represent lookup keys, others are
## for things we can take a guess at like MA.

## demog etl file has
##    pid,mrn,lname,
##    fname,mname,addr1,addr2,
##    city,state,zip,
##    cty,phonearea,phone,
##    ext,dob,gender,
##    race,lang,ssn,
##    phy,mari,religion,
##    alias,mom,death)
##
## pid grammar has
##    PID	1
##    Patient ID	3.0
##    Patient IDtype	3.4
##    Patient Last Name	5.0
##    Patient First Name	5.1
##    Patient Middle Name	5.2
##    Date of Birth	7
##    Administrative Sex	8
##    Address 1	11.0
##    Address 2	11.1
##    City	11.2
##    State	11.3
##    Zip PID	11.4
##    SSN Number	19
##

demog_lookup = [PATIENT_ID,
              PATIENT_ID,'Patient_Last_Name',
              'Patient_First_Name',
              '',
              'Address1',
              '',
              'City',
              'State',
              'Zip',
              'CountryCode','','Home_Phone_Number','',
              'Date_of_Birth',
              'Sex',
              '','Language',
              'SSN_Number_Patient',
              PCP_NPI,'Marital_Status','','Alias','','']

## rx etl file has
##    (pid,mrn,orderid,
##    phy, orderd,status,
##    med,ndc,meddesc,
##    qua,ref,sdate,
##    edate,route)
##
## grammar has
##    Rx Code	1.0
##    Brand Name	1.1
##    Coding System	1.2
##    Duration	2
##    Dose Value	3.0
##    Dose Units	3.1
##    Strength Value	4.0
##    Strength Units	4.1
##    Frequency	5.0
##    Quantity	11.0
##    Form	12.0
##    Refill	13.0

rxo_lookup = [PATIENT_ID,
             PATIENT_ID,'',
              PCP_NPI,
              ADM_DATE_TIME,
              '','Brand_Name','Rx_Code',
              '','Dose_Value','Refill','','','Form']

## labres = pid,mrn,orderid,
## orderd,resd,phy,
## ordertp,cpt,comp,
## compname,res,normalf,
## refl,refh,refu,
## status,note,accessnum,impre
##
##    obxtxt = """Set_ID	1
##    Attribute_Code	3.0
##    Attribute_Name	3.1
##    Attribute_Value	5.0
##    Attribute_Units	6.0
##    Attribute_Range	7.0
##    Result_Status	11.0
##    Observation_Date_and_Time	14.0"""

labres_lookup = [PATIENT_ID,PATIENT_ID,'','Observation_Date_and_Time','',
                 PCP_NPI,'',LABRES_CODE,'',
                 'Attribute_Name',LABRES_VALUE,'',
                 'Attribute_Range','','Attribute_Units','Result_Status',
                 '','','']

## labord = pid,mrn,orderid,cpt,modi,accessnum,orderd, ordertp, phy
##    obrtxt = """Set_ID	1
##    Placer_Order_Number	2
##    Lab_Code	4.0
##    Lab_Name	4.1
##    Observation_Date_and_Time	7
##    Attending_Provider_NPI	16.0
##    Attending_Provider_Last Name	16.1
##    Attending_Provider_First name	16.2
##    Result_Status	25.0"""

labord_lookup = [PATIENT_ID,PATIENT_ID,'Placer_Order_Number',
                 'Lab_Code','','','Observation_Date_and_Time',
                 '',PCP_NPI]

allergies_lookup = []



## imm = pid, immtp, immname,immd,immdose,manf,lot,recid
## rxa has
## Set ID	1
##    Date & Time Start of Administration	3
##    Administered Code	5.0
##    Brand Name	5.1
##    Coding System	5.2
##    Lot Number	16
## RXA|1||20071113000000||90658^Influenza (adult)^C4|||||||||||U2499AA
vaccination_lookup = [PATIENT_ID,'Administered_Code','BRAND_NAME','Date_&_Time_Start_of_Administration','','',
                      'Lot_Number','']

problem_lookup = []
allergy_lookup = []

lookup_names = [pcp_lookup,demog_lookup,allergy_lookup,enc_lookup,
                labord_lookup,labres_lookup,vaccination_lookup,problem_lookup,rxo_lookup]

writer_lookups = dict(zip(etlnames,lookup_names))




def makeTests(hl7file):
    """split sudha's test messages into something to play with for testing
    the parser code
    """
    # sudha sent the following 20 tests
    tm = []
    tl  = file(hl7file,'rb').read().split('\r')
    print 'got %d rows' % len(tl)
    message = []
    for row in tl:
        if len(row) > 2:
            message.append(row)
        else: # can be multiple blanks
            if len(message) > 1: # must be at least one blank
                tm.append(message)
            message = [] # so next blank is ignored
    if len(message) > 1: # in case there's no blank line at eof
        tm.append(message)
    return tm


def makeGrammars():
    """
    # define some hl7 segment grammars from Sudha's specifications
    # the following txts are taken directly from the spec document tables
    # we want an automated way of parsing each segment
    # make a grammars dict keyed by segment
    # with field name, offset and substring offset for repeats
    """

    mshtxt = """Encoding Characters	1
Sending Application	2
Sending Facility	3
Receiving Application	4
Date and time of message	5
Message Type	8
Message Control Id	9
Test/Production	10
Version Id	11"""
#### warning - subtract 1 from all the specification field #'s for MSH because there's an extra one in encoding characters!

    obrtxt = """Set ID	1
Placer Order Number	2
Lab Code	4
Lab Name	4.1
Observation Date and Time	7
%s	16
Attending Provider Last Name	16.1
Attending Provider First name	16.2
Result Status	25""" % PCP_NPI

    obxtxt = """Set ID	1
%s	3
Attribute Name	3.1
%s	5
Attribute Units	6
Attribute Range 	7
Result Status	11
Observation Date and Time	14""" % (LABRES_CODE,LABRES_VALUE)

    adtobxtxt = """ID Counter	1
Vitals name	2
Vitals Value	3
Vitals Unit	4
Observation Date and Time	5"""

    pd1txt = """LivDep	1
LivArr	2
PrimFac	3
PCP_NPI	4.1
PCP_Sname	4.2
PCP_Fname	4.3
PCP_Middle	4.4
Student	5
Handicap	6
Living_Will	7
Organ_Donor	8
Separate_Bill	9
Dupl_patient	10
Publicity_Code	11
Protection	12
Prot_Date	13
Worship	14
Advanced	15"""

    prbtxt = """Action Code	1
Problem Code	3
Problem Name	3.1
Coding System	3.2
Onset Date and Time	16"""

    pv1txt = """Set ID	1
Patient Class	2
%s	3
%s	7
Attending Provider last name	7.1
Attending Provider First name	7.2
Referring Provider NPI	8
Referring Provider last name	8.1
Referring Provider First name	8.2
Visit Number	19
Admit Date and Time	44""" % (FACILITY_NAME,PCP_NPI)

    enctxt = """Set ID\t1
Patient Class\t2
%s\t3
%s\t7
Attending Provider last name\t7.1
Attending Provider First name\t7.2
Referring Provider NPI\t8
Referring Provider last name\t8.1
Referring Provider First name\t8.2
Visit Number\t19
Admit Date and Time\t44""" % (FACILITY_NAME,PCP_NPI)


    # 9370^^^^PID grr the spec is wrong
    pidtxt = """Set ID	1
%s	3
Patient Last Name	5
Patient First Name	5.1
Mothers Maiden name 	6
Date of Birth	7
Sex	8
race	9
Alias	10
Address1	11
City	11.1
State	11.3
Zip	11.4
CountryCode	11.5
County Code	12
Home Phone Number	13
Buisness Phone Number	14
Language	15
Marital Status	16
Religion 	17
Patient Account Number 	18
SSN Number Patient 	19
Driver's License Number Patient 	20
Mother's Identifier 	21
Ethnicity	22
Birth Place 	23
Multiple Birth Indicator 	24
Birth Order 	25
Citizenship 	26
Veterans Military Status 	27
Nationality 	28
Patient Death Date and Time 	29
Patient Death Indicator	30""" % PATIENT_ID

    al1txt = """Set ID	1
Allergen Code	3
Allergen Name	3.1
Coding System	3.2
Reaction	5
Observation Date and Time	6"""

    dg1txt = """Set ID	1
Name	2
Diagnosis Code	3
Coding System	3.2
Admit Date and Time	5
Status	6"""

    ntetxt = """Set ID	1
Family Member	2
Status	3
Description	4"""

    rxatxt = """Set ID	1
Date & Time Start of Administration	3
Administered Code	5
Brand Name	5.1
Coding System	5.2
Lot Number of vaccine	16"""

    rxotxt = """Rx Code	1
Brand Name	1.1
Coding System	1.2
Duration	2
Dose Value	3
Dose Units	3.1
Strength Value	4
Strength Units	4.1
Frequency	5
Quantity	11
Form	12
Refill	13"""

    def makeGrammar(gdef = ()):
        """parse a definition text into a form
        for our parser - a simple grammar that can drive a
        simple parser that can read a segment and place each value
        found into a simple
        dictionary based representation of each segment
        It is this representation that is returned as a dict for each message
        All of the dicts are made available after all the messages are parsed for
        conversion into ETL files
        """
        name,txt = gdef[0],gdef[1]
        
        gdef2 = txt.split('\n')
        gdef2 = [x.strip().split('\t') for x in gdef2]
        gdef2 = [[x[0],x[1].split('.')] for x in gdef2] # (name,(field,subfield))
        for i,d in enumerate(gdef2):
            d[0] = d[0].replace(' ','_') # make solid names
            if len(d[1]) == 1: # it's the first and only field
                gdef2[i] = (d[0],int(d[1][0]),0)
            else: # it has a sub field maybe other than zero
                gdef2[i] = (d[0],int(d[1][0]),int(d[1][1]))
        return gdef2

    deftxts = [('RXO',rxotxt),('RXA',rxatxt),
            ('NTE',ntetxt),('DG1',dg1txt),
            ('AL1',al1txt),('PID',pidtxt),
            ('PV1',pv1txt),('PRB',prbtxt),
            ('PV1', enctxt),
            ('OBX',obxtxt),('OBR',obrtxt),
            ('MSH',mshtxt),('ADTOBX',adtobxtxt),
            ('PD1',pd1txt)] # segment to grammar crosswalk
    g = [makeGrammar(x) for x in deftxts]
    segs = [x[0] for x in deftxts]
    grammars = dict(zip(segs,g)) # key the representation with the segment name
    return grammars # whew, segment name gets you a dict of field and where to look


# end north adams hl7 configuration
# ross lazarus 18 March 2008
# for the ESP project
