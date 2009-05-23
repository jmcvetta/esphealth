# hl7 generating code
# for ESP VAERS
# need to add MVX and CVX codes somehow..

import os,sys,re
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'



from ESP.esp.models import *

from django.contrib.auth import REDIRECT_FIELD_NAME
from xml.dom.minidom import Document
import time,datetime,random

# Ayee from http://www.cdc.gov/vaccines/programs/iis/stds/cvx.htm

cvxs = """Code  	Short Description  	Full Vaccine Name
54 	adenovirus, type 4 	adenovirus vaccine, type 4, live, oral
55 	adenovirus, type 7 	adenovirus vaccine, type 7, live, oral
82 	adenovirus, NOS1 	adenovirus vaccine, NOS
24 	anthrax 	anthrax vaccine
19 	BCG 	Bacillus Calmette-Guerin vaccine
27 	botulinum antitoxin 	botulinum antitoxin
26 	cholera 	cholera vaccine
29 	CMVIG 	cytomegalovirus immune globulin, intravenous
56 	dengue fever 	dengue fever vaccine
12 	diphtheria antitoxin 	diphtheria antitoxin
28 	DT (pediatric) 	diphtheria and tetanus toxoids, adsorbed for pediatric use
20 	DTaP 	diphtheria, tetanus toxoids and acellular pertussis vaccine
106 	DTaP, 5 pertussis antigens 	diphtheria, tetanus toxoids and acellular pertussis vaccine, 5 pertussis antigens
107 	DTaP, NOS 	diphtheria, tetanus toxoids and acellular pertussis vaccine, NOS
110 	DTaP-Hep B-IPV 	DTaP-hepatitis B and poliovirus vaccine
50 	DTaP-Hib 	DTaP-Haemophilus influenzae type b conjugate vaccine
120 	DTaP-Hib-IPV 	diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine,inactivated (DTaP-Hib-IPV)Changes last made on Feb. 28, 2006
130 	DTaP-IPV 	Diphtheria, tetanus toxoids and acellular pertussis vaccine, and poliovirus vaccine, inactivated(Changes made July 25, 2008)
01 	DTP 	diphtheria, tetanus toxoids and pertussis vaccine
22 	DTP-Hib 	DTP-Haemophilus influenzae type b conjugate vaccine
102 	DTP-Hib-Hep B 	DTP- Haemophilus influenzae type b conjugate and hepatitis b vaccine
57 	hantavirus 	hantavirus vaccine
52 	Hep A, adult 	hepatitis A vaccine, adult dosage
83 	Hep A, ped/adol, 2 dose 	hepatitis A vaccine, pediatric/adolescent dosage, 2 dose schedule
84 	Hep A, ped/adol, 3 dose 	hepatitis A vaccine, pediatric/adolescent dosage, 3 dose schedule
31 	Hep A, pediatric, NOS 	hepatitis A vaccine, pediatric dosage, NOS
85 	Hep A, NOS 	hepatitis A vaccine, NOS
104 	Hep A-Hep B 	hepatitis A and hepatitis B vaccine
30 	HBIG 	hepatitis B immune globulin
08 	Hep B, adolescent or pediatric 	hepatitis B vaccine, pediatric or pediatric/adolescent dosage
42 	Hep B, adolescent/high risk infant2 	hepatitis B vaccine, adolescent/high risk infant dosage
43 	Hep B, adult 	hepatitis B vaccine, adult dosage
44 	Hep B, dialysis 	hepatitis B vaccine, dialysis patient dosage
45 	Hep B, NOS 	hepatitis B vaccine, NOS
58 	Hep C 	hepatitis C vaccine
59 	Hep E 	hepatitis E vaccine
60 	herpes simplex 2 	herpes simplex virus, type 2 vaccine
46 	Hib (PRP-D) 	Haemophilus influenzae type b vaccine, PRP-D conjugate
47 	Hib (HbOC) 	Haemophilus influenzae type b vaccine, HbOC conjugate
48 	Hib (PRP-T) 	Haemophilus influenzae type b vaccine, PRP-T conjugate
49 	Hib (PRP-OMP) 	Haemophilus influenzae type b vaccine, PRP-OMP conjugate
17 	Hib, NOS 	Haemophilus influenzae type b vaccine, conjugate NOS
51 	Hib-Hep B 	Haemophilus influenzae type b conjugate and Hepatitis B vaccine
61 	HIV 	human immunodeficiency virus vaccine
118 	HPV, bivalent 	human papilloma virus vaccine, bivalent Changes last made on Feb. 28, 2006
62 	HPV, quadrivalent 	human papilloma virus vaccine, quadrivalent Changes last made on Feb. 28, 2006
86 	IG 	immune globulin, intramuscular
87 	IGIV 	immune globulin, intravenous
14 	IG, NOS 	immune globulin, NOS
111 	influenza, live, intranasal 	influenza virus vaccine, live, attenuated, for intranasal use
15 	influenza, split (incl. purified surface antigen) 	influenza virus vaccine, split virus (incl. purified surface antigen)
16 	influenza, whole 	influenza virus vaccine, whole virus
88 	influenza, NOS 	influenza virus vaccine, NOS
123 	influenza, H5N1-1203    influenza virus vaccine, H5N1, A/Vietnam/1203/2004 (national stockpile) (Changes made September 23, 2008)
10 	IPV 	poliovirus vaccine, inactivated
02 	OPV 	poliovirus vaccine, live, oral
89 	polio, NOS 	poliovirus vaccine, NOS
39 	Japanese encephalitis 	Japanese encephalitis vaccine
63 	Junin virus 	Junin virus vaccine
64 	leishmaniasis 	leishmaniasis vaccine
65 	leprosy 	leprosy vaccine
66 	Lyme disease 	Lyme disease vaccine
03 	MMR 	measles, mumps and rubella virus vaccine
04 	M/R 	measles and rubella virus vaccine
94 	MMRV 	measles, mumps, rubella, and varicella virus vaccine
67 	malaria 	malaria vaccine
05 	measles 	measles virus vaccine
68 	melanoma 	melanoma vaccine
32 	meningococcal 	meningococcal polysaccharide vaccine (MPSV4)
103 	meningococcal C conjugate 	meningococcal C conjugate vaccine
114 	meningococcal A,C,Y,W-135 diphtheria conjugate 	meningococcal polysaccharide (groups A, C, Y and W-135) diphtheria toxoid conjugate vaccine (MCV4)
108 	meningococcal, NOS 	meningococcal vaccine, NOSChanges last made on May 10, 2006
07 	mumps 	mumps virus vaccine
69 	parainfluenza-3 	parainfluenza-3 virus vaccine
11 	pertussis 	pertussis vaccine
23 	plague 	plague vaccine
33 	pneumococcal 	pneumococcal polysaccharide vaccine
100 	pneumococcal conjugate 	pneumococcal conjugate vaccine, polyvalent
109 	pneumococcal, NOS 	pneumococcal vaccine, NOS
70 	Q fever 	Q fever vaccine
18 	rabies, intramuscular injection 	rabies vaccine, for intramuscular injection
40 	rabies, intradermal injection 	rabies vaccine, for intradermal injection
90 	rabies, NOS 	rabies vaccine, NOS
72 	rheumatic fever 	rheumatic fever vaccine
73 	Rift Valley fever 	Rift Valley fever vaccine
34 	RIG 	rabies immune globulin
119 	rotavirus, monovalent 	rotavirus, live, monovalent vaccineChanges last made on Feb. 28, 2006
122 	rotavirus, NOS1 	rotavirus vaccine, NOSChanges last made on June 1, 2006
116 	rotavirus, pentavalent 	rotavirus, live, pentavalent vaccineChanges last made on Feb. 28, 2006
74 	rotavirus, tetravalent 	rotavirus, live, tetravalent vaccineChanges last made on Feb. 28, 2006
71 	RSV-IGIV 	respiratory syncytial virus immune globulin, intravenous
93 	RSV-MAb 	respiratory syncytial virus monoclonal antibody (palivizumab), intramuscular
06 	rubella 	rubella virus vaccine
38 	rubella/mumps 	rubella and mumps virus vaccine
76 	Staphylococcus bacterio lysate 	Staphylococcus bacteriophage lysate
113 	Td (adult) 	tetanus and diphtheria toxoids, adsorbed, preservative free, for adult use
09 	Td (adult) 	tetanus and diphtheria toxoids, adsorbed for adult use
115 	Tdap 	tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed Changes last made on May 10, 2006
35 	tetanus toxoid 	tetanus toxoid, adsorbed
112 	tetanus toxoid, NOS 	tetanus toxoid, NOS
77 	tick-borne encephalitis 	tick-borne encephalitis vaccine
13 	TIG 	tetanus immune globulin
95 	TST-OT tine test 	tuberculin skin test; old tuberculin, multipuncture device
96 	TST-PPD intradermal 	tuberculin skin test; purified protein derivative solution, intradermal
97 	TST-PPD tine test 	tuberculin skin test; purified protein derivative, multipuncture device
98 	TST, NOS 	tuberculin skin test; NOS
78 	tularemia vaccine 	tularemia vaccine
91 	typhoid, NOS 	typhoid vaccine, NOS
25 	typhoid, oral 	typhoid vaccine, live, oral
41 	typhoid, parenteral 	typhoid vaccine, parenteral, other than acetone-killed, dried
53 	typhoid, parenteral, AKD (U.S. military) 	typhoid vaccine, parenteral, acetone-killed, dried (U.S. military)
101 	typhoid, ViCPs 	typhoid Vi capsular polysaccharide vaccine
75 	vaccinia (smallpox) 	vaccinia (smallpox) vaccine
105 	vaccinia (smallpox) diluted 	vaccinia (smallpox) vaccine, diluted
79 	vaccinia immune globulin 	vaccinia immune globulin
21 	varicella 	varicella virus vaccine
81 	VEE, inactivated 	Venezuelan equine encephalitis, inactivated
80 	VEE, live 	Venezuelan equine encephalitis, live, attenuated
92 	VEE, NOS 	Venezuelan equine encephalitis vaccine, NOS
36 	VZIG 	varicella zoster immune globulin
117 	VZIG (IND) 	varicella zoster immune globulin (Investigational New Drug) Changes last made on Feb. 28, 2006
37 	yellow fever 	yellow fever vaccine
121 	zoster 	zoster vaccine, live Changes last made on June 1, 2006
998 	no vaccine administered5 	no vaccine administered
999 	unknown 	unknown vaccine or immune globulin
99 	RESERVED - do not use3 	RESERVED - do not use"""
cvxl = cvxs.split('\n')[1:] # drop header
cvxl = [x.split('\t') for x in cvxl]
print cvxl[:10]
cvxd = dict(zip([x[1] for x in cvxl],cvxl)) # key by short name


# ayee and at http://www.cdc.gov/vaccines/programs/iis/stds/mvx.htm
mvxs = """Code  	Vaccine Manufacturer/Distributor
AB 	Abbott Laboratories (includes Ross Products Division)
ACA 	Acambis, Inc
AD 	Adams Laboratories, Inc.
ALP 	Alpha Therapeutic Corporation
AR 	Armour [Inactive--use AVB]
AVB 	Aventis Behring L.L.C. (formerly Centeon L.L.C.; includes Armour Pharmaceutical Company) [Inactive--use ZLB] Changes made on: Feb. 28, 2006
AVI 	Aviron
BA 	Baxter Healthcare Corporation [Inactive--use BAH]
BAH 	Baxter Healthcare Corporation (includes Hyland Immuno, Immuno International AG, and North American Vaccine, Inc.)
BAY 	Bayer Corporation (includes Miles, Inc. and Cutter Laboratories)
BP 	Berna Products [Inactive--use BPC]
BPC 	Berna Products Corporation (includes Swiss Serum and Vaccine Institute Berne)
MIP 	Bioport Corporation (formerly Michigan Biolologic Products Institute)
CSL 	CSL Biotherapies, Inc.
CNJ 	Cangene Corporation Changes made on: Feb. 28, 2006
CMP 	Celltech Medeva Pharmaceuticals [Inactive--use NOV] Changes made on: July 14, 2006
CEN 	Centeon L.L.C. [Inactive--use AVB]
CHI 	Chiron Corporation [Inactive--use NOV] includes PowderJect Pharmaceuticals, Celltech Medeva Vaccines and Evans Medical Limited Changes made on: July 14, 2006
CON 	Connaught [Inactive--use PMC]
DVC 	DynPort Vaccine Company, LLC Changes made on: July 14, 2006
EVN 	Evans Medical Limited [Inactive--use NOV] Changes made on: July 14, 2006
GEO 	GeoVax Labs, Inc. Changes made on: July 14, 2006
SKB 	GlaxoSmithKline (formerly SmithKline Beecham; includes SmithKline Beecham and Glaxo Welcome)
GRE 	Greer Laboratories, Inc.
IAG 	Immuno International AG [Inactive--use BAH]
IUS 	Immuno-U.S., Inc.
KGC 	Korea Green Cross Corporation
LED 	Lederle [Inactive--use WAL]
MBL 	Massachusetts Biologic Laboratories (formerly Massachusetts Public Health Biologic Laboratories)
MA 	Massachusetts Public Health Biologic Laboratories [Inactive--use MBL]
MED 	MedImmune, Inc.
MSD 	Merck & Co., Inc.
IM 	Merieux [Inactive--use PMC]
MIL 	Miles [Inactive--use BAY]
NAB 	NABI (formerly North American Biologicals, Inc.)
NYB 	New York Blood Center
NAV 	North American Vaccine, Inc. [Inactive--use BAH]
NOV 	Novartis Pharmaceutical Corporation (includes Chiron, PowderJect Pharmaceuticals, Celltech Medeva Vaccines and Evans Limited, Ciba-Geigy Limited and Sandoz Limited)
NVX 	Novavax, Inc. Changes made on: July 14, 2006
OTC 	Organon Teknika Corporation
ORT 	Ortho-Clinical Diagnostics (formerly Ortho Diagnostic Systems, Inc.)
PD 	Parkedale Pharmaceuticals (formerly Parke-Davis)
PWJ 	PowderJect Pharmaceuticals (includes Celltech Medeva Vaccines and Evans Medical Limited) [Inactive--use NOV] Changes made on: July 14, 2006
PRX 	Praxis Biologics [Inactive--use WAL]
PMC 	sanofi pasteur (formerly Aventis Pasteur, Pasteur Merieux Connaught; includes Connaught Laboratories and Pasteur Merieux) Changes made on: Feb. 28, 2006
JPN 	The Research Foundation for Microbial Diseases of Osaka University (BIKEN)
SCL 	Sclavo, Inc.
SOL 	Solvay Pharmaceuticals Changes made on: July 14, 2006
SI 	Swiss Serum and Vaccine Inst. [Inactive--use BPC]
TAL 	Talecris Biotherapeutics (includes Bayer Biologicals) Changes made on: Feb. 28, 2006
USA 	United States Army Medical Research and Material Command
VXG 	VaxGen Changes made on: July 14, 2006
WA 	Wyeth-Ayerst [Inactive--use WAL]
WAL 	Wyeth-Ayerst (includes Wyeth-Lederle Vaccines and Pediatrics, Wyeth Laboratories, Lederle Laboratories, and Praxis Biologics)
ZLB 	ZLB Behring (includes Aventis Behring and Armour Pharmaceutical Company) Changes made on: Feb. 28, 2006
OTH 	Other manufacturer
UNK 	Unknown manufacturer"""
mvxl = mvxs.split('\n')[1:] # drop header
mvxl = [x.split('\t') for x in mvxl]
mvxd = dict(zip([x[1] for x in mvxl],mvxl)) # key by short name

###################################
def isoTime(t=None):
        """ yyyymmddhhmmss - as at now unless a localtime is passed in
            """
        if t == None:
            return time.strftime('%Y%m%d',time.localtime())
        #        return time.strftime('%Y%m%d%H%M%S',time.localtime())
        else:
            return time.strftime('%Y%m%d%H%M%S',t)


###################################
def getOnestr(delimiter, templ):
    return '%s' % delimiter.join(templ)



###################################
####obr_dict ={obrseq: (total_OBXseq, [list of Universal IDs], subid, addition_value_dict), ...}
obr_dict = {1: (10,['','CDC VAERS-1 (FDA) Report'],'', {5:'',6:'',7:isoTime()}),
            2: (6, ['30955-9','All vaccines given on date listed in #10','LN'],'', {}),
            3: (12,['30961-7','Any other vaccinations within 4 weeks prior to the date listed in #10','LN'],'',{}),
            4: (3, ['30967-4','Was adverse event reported previously','LN'],'',{}),
            5: (1, ['30968-2','Adverse event following prior vaccination in patient','LN'],'',{}),
            6: (4, ['35286-4','Adverse event following prior vaccination in Sibling','LN'],'1',{}),
            7: (1, ['35286-4','Adverse event following prior vaccination in Sibling','LN'],'2',{}),
            8: (2, ['','For children 5 and under',''],'', {}),
            9: (4, ['','Only for reports submitted by manufacturer/immunization project',''],'',{}),
            }


####obx_dict = {(obrseq, obxseq): [datatype, [list of observationID], subid], ...}
obx_dict = {(1,1):  ['NM',['21612-7', 'Reported Patient Age', 'LN'],''],
            (1,2):  ['TS',['30947-6', 'Date form compelted', 'LN'],''],
            (1,3):  ['FT',['30948-4', 'Vaccination adverse events and treatment, if any','LN'],'1'],
            (1,4):  ['CE',['30949-2','Vaccination adverse event outcome','LN'],'1'],
            (1,5):  ['CE',['30949-2','Vaccination adverse event outcome','LN'],'1'],
            (1,6):  ['NM',['30950-0','Number of days hospitalized due to vaccination adverse event','LN'],'1'],
            (1,7):  ['CE',['30951-8','Patient recovered','LN'],''],
            (1,8):  ['TS',['30952-6','Date of vaccination','LN'],''],
            (1,9):  ['TS',['30953-4','Adverse event onset date and time','LN'],''],
            (1,10): ['FT',['30954-2','Relevent diagnostic tests/lab data','LN'],''],

            (2,1):  ['CE',['30955-9&30956-7','Vaccine type','LN'],'1'],
            (2,2):  ['CE',['30955-9&30957-5','Manufacturer','LN'],'1'],
            (2,3):  ['ST',['30955-9&30959-1','Lot number','LN'],'1'],
            (2,4):  ['CE',['30955-9&30958-3','Route','LN'], '1'],
            (2,5):  ['CE',['30955-9&31034-2','Site','LN'],'1'],
            (2,6):  ['NM',['30955-9&30960-9','Number of previous doses','LN'],'1'],


            (3,1):  ['CE',['30955-9&30956-7','Vaccine type','LN'],'1'],
            (3,2):  ['CE',['30955-9&30957-5','Manufacturer','LN'],'1'],
            (3,3):  ['ST',['30955-9&30959-1','Lot number','LN'],'1'],
            (3,4):  ['CE',['30955-9&30958-3','Route','LN'], '1'],
            (3,5):  ['CE',['30955-9&31034-2','Site','LN'],'1'],
            (3,6):  ['NM',['30955-9&30960-9','Number of previous doses','LN'],'1'],
            (3,7):  ['TS',['30961-7&31035-9','date given','LN'],'1'],
            (3,8):  ['CE',['30962-5','Vaccinated at','LN'],''],
            (3,9):  ['CE',['30963-3','Vaccine purchased with','LN'], ''],
            (3,10): ['FT',['30964-1','Other medications','LN'],''],
            (3,11): ['FT',['30965-8','Illness at time of vaccination (specify)','LN'],''],
            (3,12): ['FT',['30966-6','Pre-existing physician diagnosed allergies, birth defects, medical conditions','LN'],''],

            (4,1): ['CE', ['30967-4','Was adverse event reported previously','LN'], ''],
            (4,2): ['CE', ['30967-4','Was adverse event reported previously','LN'], ''],
            (4,3): ['CE', ['30967-4','Was adverse event reported previously','LN'], ''],

            (5,1): ['FT',['30968-2&30971-6','Adverse event','LN'],''],

            (6,1): ['FT',['35286-4&30971-6','Adverse event','LN'],''],
            (6,2): ['NM',['35286-4&30972-4','Onset age','LN'],''],
            (6,3): ['CE',['35286-4&30956-7','Vaccine Type','LN'],''],
            (6,4): ['NM',['35286-4&30973-2','Dose number in series','LN'],''],

            (7,1): ['FT', ['35286-4&30971-6','Adverse event','LN'],''],

            (8,1): ['NM',['8339-4','Body weight at birth','LN'],''],
            (8,2): ['NM',['30974-0','Number of brothers and sisters','LN'],''],

            (9,1): ['ST',['30975-7','Mfr./Imm. Proj. report no.','LN'],''],
            (9,2): ['TS',['30976-5','Date received by manufacturer/immunization project','LN'],''],
            (9,3): ['CE',['30977-3','15 day report','LN'],''],
            (9,4): ['CE',['30978-1','Report type','LN'],''],

            }



############################
class onehl7:
    """ class for building an hl7 message
    eeesh this is horrible. hl7 sucks.
    two dom objects - one for cases and one for the batch
    the cases are added by calling addCase, then rendered and inserted into
    the batch by the renderBatch method
    """

    def __init__(self, onecase, institutionName='HVMA'):

        self.encoding = '^~\&'
        self.recvfacility = 'VAERS PROCESSOR'
        self.version ='2.3.1'
        self.procID = 'T'
        self.acceptTp = 'NE'
        self.applicationTp = 'AL'
        self.msgTp = 'ORU^R01'
        self.sendfacility = institutionName
        self.case = onecase
        self.demog = Demog.objects.filter(id=self.case.caseDemog_id)[0]


    ###################################
    def build_seg(self, temp_d):
        seq = temp_d.keys()
        seq.sort()
        return getOnestr('|',['%s' % temp_d[i] for i in seq])



    ###################################
    def makeMSH(self):
        temp_d = {0: 'MSH',
                  2: self.encoding,
                  3: '',
                  4: self.sendfacility,
                  5: '',
                  6: self.recvfacility,
                  7: isoTime(),
                  8: '',
                  9: self.msgTp,
                  10: isoTime()+self.sendfacility,
                  11: self.procID,
                  12: self.version,
                  13: '',
                  14: '',
                  15: self.acceptTp,
                  16: self.applicationTp,
                  21: '\n'
                  }
        return self.build_seg(temp_d)




    def makePID(self):
        pidlist = [self.demog.DemogPatient_Identifier, 'MR~'+self.demog.DemogMedical_Record_Number, 'SS~'+self.demog.DemogSSN]
        name =[self.demog.DemogLast_Name, self.demog.DemogFirst_Name, self.demog.DemogMiddle_Initial,self.demog.DemogSuffix, '','','L']
        race_d = {'ALASKAN': ['1002-5', 'American Indian or Alaska Native'],
                  'ASIAN': ['2028-9', 'Asian'],
                  'BLACK':['2054-5', 'Black or Aferican-American'],
                  'CAUCASIAN':['2106-3', 'White'],
                  'HISPANIC':['2135-2', 'Hispanic or Latino'],
                  'INDIAN':['1002-5', 'American Indian or Alaska Nat'],
                  'NAT AMERICAN':['1002-5', 'American Indian or Alaska Nat'],
                  'NATIVE HAWAI':['2076-8', 'Native Hawaiian or Other Pacific Islander'],
                  'OTHER':['2131-1', 'Other Race'],
            }
        if race_d.has_key(self.demog.DemogRace):
            race = race_d[self.demog.DemogRace]
        else:
            race = race_d['OTHER']
        race =race + ['HL70005']

        address = [self.demog.DemogAddress1, self.demog.DemogAddress2, self.demog.DemogCity, self.demog.DemogState, self.demog.DemogZip,'','M']
        phone =  [self.demog.DemogTel, 'PRN']
        temp_d = {0:'PID',
                  1: '',
                  2:'',
                  3: getOnestr('^',pidlist),
                  4: '',
                  5: getOnestr('^',name),
                  6: '',
                  7: self.demog.DemogDate_of_Birth,
                  8: self.demog.DemogGender,
                  9: self.demog.DemogAliases,
                  10: getOnestr('^',race),
                  11: getOnestr('^',address),
                  12: '',
                  13: getOnestr('^',phone),
                  14: '',
                  15: self.demog.DemogHome_Language,
                  31: '\n'

            }
        return self.build_seg(temp_d)

    ###################################
    def makeOBR(self,obrseq):
        temp_d = {0: 'OBR',
                  1: '%s' % obrseq,
                  2: '',
                  3: '',
                  4: getOnestr('^',obr_dict[int(obrseq)][1]),
                  5: obr_dict[int(obrseq)][2],
                  100: '\n'
                  }

        temp_d.update(obr_dict[int(obrseq)][3])
        return self.build_seg(temp_d)


    ###################################
    def makeOBX(self,obxseq,datatp,obsID,subid,value,unit):
        ##make one OBX
        temp_d = {0: 'OBX',
                  1: obxseq,
                  2: datatp,
                  3: obsID,
                  4: subid,
                  5: '%s' % value,
                  6: unit,
                  7: '',
                  8:'',
                  9: '',
                  10: '',
                  11: 'F',
                  18: '\n'
                                                      }
        return self.build_seg(temp_d)

    ###################################
    def buildOBX_data_1(self):
        ##OBX
        age = self.demog.getAge()
        if type(age) != type(2):
            unit = getOnestr('^',['mo', 'month', 'ANSI'])
            value = age.split()[0]
        else:
            unit = ''
            value = age


        ##temperature
        encs = Enc.objects.extra(where=['id IN (%s)' %  self.case.caseEncID])

        p = re.compile('\s+')
        temperature_str =p.sub(' ', self.case.caseComments)

        #for oneenc in encs:
        #    temperature_str =temperature_str+'%s,' % oneenc.EncTemperature


        ##key = the sequence of OBX
        data_dict={1: (age, unit),
                   2: (isoTime(),''),
                   3: (temperature_str,''),
                   4: ('',''),
                   5: ('',''),
                   6: ('',''),
                   7: ('',''),
                   8: ('',''),
                   9: ('',''),
                   10:('',''),
                   }

        return data_dict

    ###################################
    def buildOBX_data_2(self):

        ##Imm recs
        imms = Immunization.objects.extra(where=['id IN (%s)' %  self.case.caseImmID])
        data_dict={}
        obxseq_l = range(1, 6*len(imms), 6)
        for indx in range(len(imms)):
                imm = imms[indx]
                setid_start = obxseq_l[indx]
                data_dict[setid_start] = (imm.ImmName,'')
                data_dict[setid_start+1] = (imm.ImmManuf,'')
                data_dict[setid_start+2] = (imm.ImmLot,'')
                data_dict[setid_start+3] = ('','')
                data_dict[setid_start+4] = ('','')
                data_dict[setid_start+5] = ('','')
        return data_dict

    ###################################
    def buildOBX_data_3(self):
        data_dict={1: ('', ''),
                   2: ('',''),
                   3: ('',''),
                   4: ('',''),
                   5: ('',''),
                   6: ('',''),
                   7: ('',''),
                   8: ('',''),
                   9: ('',''),
                   10:('',''),
                   11:('',''),
                   12:('',''),

                   }

        return data_dict

    ###################################
    def buildOBX_data_4(self):
        data_dict={1: ('', ''),
                   2: ('',''),
                   3: ('',''),
                   }
        return data_dict

    ###################################
    def buildOBX_data_5(self):
        data_dict={1: ('',''),
                   }
        return data_dict


    ###################################
    def buildOBX_data_6(self):
        data_dict={1: ('', ''),
                   2: ('',''),
                   3: ('',''),
                   4: ('',''),
                   }
        return data_dict

    ###################################
    def buildOBX_data_7(self):
        data_dict={1: ('None', ''),
                   }
        return data_dict

    ###################################
    def buildOBX_data_8(self):
        data_dict={1: ('',  getOnestr('^',['oz', 'ounces', 'ANSI'])),
                   2: ('',''),
                   }
        return data_dict

    ###################################
    def buildOBX_data_9(self):
        data_dict={1: ('', ''),
                   2: ('',''),
                   3: ('',''),
                   4: ('',''),
                   }
        return data_dict


    ###################################
    def makeOBXs(self, obrseq, totalobxseq, data_dict):
        returnseg=''
        repeats_seq = len(data_dict)/totalobxseq
        for i in range(1, repeats_seq +1,1):
            for obxseq in range(1,totalobxseq+1,1):
                (datatp, obsIDl,subid) = obx_dict[(obrseq, obxseq)]
                realindx = totalobxseq*(i-1)+obxseq
                (value, unit) = data_dict[realindx]

                obx = self.makeOBX(obxseq=realindx,
                        datatp=datatp,obsID=getOnestr('^',obsIDl),subid=subid,
                        value=value,unit=unit)
                returnseg =returnseg+obx
        return returnseg


    ###########################################

def test():
    """test! used during development
    Won't work now as I've cut over to using django records
    """
    immcases = TestCase.objects.filter(caseImmID__isnull=False)
    for onecase in immcases:
        testDoc = onehl7(onecase)  ##1946 is esp_demog.id
        msh = testDoc.makeMSH()
        pid =  testDoc.makePID()
        finalstr = msh +pid
        ##we do not have patient parents info and Immunization info, so there is no NK1 seqment

        ##ORC = Provider who orders vaccination

        ##OBR
        obxdata = {1: testDoc.buildOBX_data_1(),
               2: testDoc.buildOBX_data_2(),
               3: testDoc.buildOBX_data_3(),
               4: testDoc.buildOBX_data_4(),
               5: testDoc.buildOBX_data_5(),
               6: testDoc.buildOBX_data_6(),
               7: testDoc.buildOBX_data_7(),
               9: testDoc.buildOBX_data_9()}

        ##Age
        age = testDoc.demog.getAge()
        try:
            if int(age)>5:
                pass
            else:
                obxdata[8] = testDoc.buildOBX_data_8()
        except:
            obxdata[8] = testDoc.buildOBX_data_8()

        for obrseq in obxdata.keys():
                obr = testDoc.makeOBR(obrseq)
                finalstr = finalstr +obr
                obxs = testDoc.makeOBXs(obrseq, obr_dict[int(obrseq)][0], obxdata[obrseq])
                finalstr = finalstr + obxs

        # Print our newly created XML
        f = file('VAERS_hl7Sample_case%s.hl7' % onecase.id,'w')
        f.write(finalstr)
        print finalstr
        f.close()



###################################
###################################
if __name__ == "__main__":
    test()


