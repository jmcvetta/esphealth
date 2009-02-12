# hl7 generating code
# for ESP VAERS
import os,sys
sys.path.insert(0, '/home/ESP/')
# for esphealth.org sys.path.insert(0, '/home/ESP/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'


import utils
from ESP.esp.models import *

from django.contrib.auth import REDIRECT_FIELD_NAME
from xml.dom.minidom import Document
import time,datetime,random


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
            3: (8,['30961-7','Any other vaccinations within 4 weeks prior to the date listed in #10','LN'],'',{}),
#            4: (3, ['30967-4','Was adverse event reported previously','LN'],'',{}),
#            5: (1, ['30968-2','Adverse event following prior vaccination in patient','LN'],'',{}),
#            6: (4, ['35286-4','Adverse event following prior vaccination in Sibling','LN'],'1',{}),
#            7: (1, ['35286-4','Adverse event following prior vaccination in Sibling','LN'],'2',{}),
#             8: (2, ['','For children 5 and under',''],'', {}),
#            9: (4, ['','Only for reports submitted by manufacturer/immunization project',''],'',{}),
            }


####obx_dict = {(obrseq, obxseq): [datatype, [list of observationID], subid], ...}
obx_dict = {(1,1):  ['NM',['21612-7', 'Reported Patient Age', 'LN'],''],
            (1,2):  ['TS',['30947-6', 'Date form completed', 'LN'],''],
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
           # (3,9):  ['CE',['30963-3','Vaccine purchased with','LN'], ''],
           # (3,10): ['FT',['30964-1','Other medications','LN'],''],
           # (3,11): ['FT',['30965-8','Illness at time of vaccination (specify)','LN'],''],
           # (3,12): ['FT',['30966-6','Pre-existing physician diagnosed allergies, birth defects, medical conditions','LN'],''],

            #(4,1): ['CE', ['30967-4','Was adverse event reported previously','LN'], ''],
            #(4,2): ['CE', ['30967-4','Was adverse event reported previously','LN'], ''],
            #(4,3): ['CE', ['30967-4','Was adverse event reported previously','LN'], ''],

            #(5,1): ['FT',['30968-2&30971-6','Adverse event','LN'],''],

            #(6,1): ['FT',['35286-4&30971-6','Adverse event','LN'],''],
            #(6,2): ['NM',['35286-4&30972-4','Onset age','LN'],''],
            #(6,3): ['CE',['35286-4&30956-7','Vaccine Type','LN'],''],
            #(6,4): ['NM',['35286-4&30973-2','Dose number in series','LN'],''],

            #(7,1): ['FT', ['35286-4&30971-6','Adverse event','LN'],''],

            #(8,1): ['NM',['8339-4','Body weight at birth','LN'],''],
            #(8,2): ['NM',['30974-0','Number of brothers and sisters','LN'],''],

            #(9,1): ['ST',['30975-7','Mfr./Imm. Proj. report no.','LN'],''],
            #(9,2): ['TS',['30976-5','Date received by manufacturer/immunization project','LN'],''],
            #(9,3): ['CE',['30977-3','15 day report','LN'],''],
            #(9,4): ['CE',['30978-1','Report type','LN'],''],

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
	encs = Enc.objects.extra(where=['id IN (%s)' %  self.case.caseEncID]).order_by('EncEncounter_Date')
	self.eventdatetime ='%s1200' % encs[0].EncEncounter_Date	 

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
        age = self.demog.oldGetAge()
        if type(age) != type(2):
            unit = getOnestr('^',['mo', 'month', 'ANSI'])
            agevalue = age.split()[0]
        else:
            unit = ''
            agevalue = age

	##temperature
	import re
	p = re.compile('\s+')
	temperature_str =p.sub(' ', self.case.caseComments)

	#for oneenc in encs:
	#    temperature_str =temperature_str+'%s,' % oneenc.EncTemperature

	##add value to 6,8,9
	##number of days for hospitalized
	hosp_days = 0
	dayunit = getOnestr('^',['d', 'day', 'ANSI'])

	##date of vaccine
	imms = Immunization.objects.extra(where=['id IN (%s)' %  self.case.caseImmID])
	vacdate = str(imms[0].ImmDate)

	##event data and time=case created date
	#eventdatetime =  self.case.casecreatedDate.strftime('%Y%m%d%H%M')

        ##key = the sequence of OBX
        data_dict={1: ('%.2i' % int(agevalue), unit),
		   2: (isoTime(),''),
                   3: (temperature_str,''),
                   4: ('',''),
                   5: ('',''),
                   6: ('%.2i' % hosp_days,dayunit),
		   7: ('',''),
                   8: (vacdate,''),
		   9: (self.eventdatetime,''),
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

	    temp = Immunization.objects.filter(ImmPatient__id = self.demog.id,
					       ImmName__icontains=imm.ImmName, ImmDate__lt=imm.ImmDate)
	    num_prevdose='%.2i' % len(temp)
	    data_dict[setid_start+5] = (num_prevdose,'')
        
        return data_dict

            
    ###################################
    def buildOBX_data_3(self):
        ##get all other vaccines within 4 weeks before the event date

        ##get all imms form this demog
	start_date=utils.getAnotherdate(self.eventdatetime,dayrange=-29)
	end_date = utils.getAnotherdate(self.eventdatetime,dayrange=0)
	hosp = self.case.caseProvider.provPrimary_Dept
	data_dict={}
	setid_start=1
	imms = Immunization.objects.filter(ImmPatient__id = self.demog.id)
	for imm in imms:
	    if imm.ImmDate=='':
		continue    
	    immdate = utils.getAnotherdate(imm.ImmDate,0)
	    if immdate and immdate>=start_date and immdate<=end_date:
		data_dict[setid_start] = (imm.ImmName,'')
		data_dict[setid_start+1] = (imm.ImmManuf,'')
		data_dict[setid_start+2] = (imm.ImmLot,'')
		data_dict[setid_start+3] = ('','')
		data_dict[setid_start+4] = ('','')
		temp = Immunization.objects.filter(ImmPatient__id = self.demog.id,
						   ImmName__icontains=imm.ImmName, ImmDate__lt=imm.ImmDate)

		num_prevdose='%.2i' % len(temp)
		data_dict[setid_start+5] = (num_prevdose,'')
		data_dict[setid_start+6] = (imm.ImmDate,'')
		data_dict[setid_start+7] = (hosp,'')
		setid_start=setid_start+1+7
		
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
		if int(obrseq) in (2,3):
		    subid = i
        
                obx = self.makeOBX(obxseq=realindx,datatp=datatp,obsID=getOnestr('^',obsIDl),subid=subid, 
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
             #  4: testDoc.buildOBX_data_4(),
             #  5: testDoc.buildOBX_data_5(),
             #  6: testDoc.buildOBX_data_6(),
             #  7: testDoc.buildOBX_data_7(),
             #  9: testDoc.buildOBX_data_9()
		   }

        ##Age
	age = testDoc.demog.getAge()
#	try:
#	    if int(age)>5:
#	        pass
#	    else:
#	        obxdata[8] = testDoc.buildOBX_data_8()

#	except:
#	    obxdata[8] = testDoc.buildOBX_data_8()

        for obrseq in obxdata.keys():
	    if not obxdata[obrseq]:
                continue
	    obr = testDoc.makeOBR(obrseq)
	    finalstr = finalstr +obr
	    
	    obxs = testDoc.makeOBXs(obrseq, obr_dict[int(obrseq)][0], obxdata[obrseq])
	    finalstr = finalstr +obxs
    
	# Print our newly created XML
	f = file('VARES_hl7Sample_case%s.hl7' % onecase.id,'w')
	f.write(finalstr)
	print finalstr
	f.close()
    


###################################
###################################
if __name__ == "__main__":
    test()
        
    
