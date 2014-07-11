'''
                                  ESP Health
                         Notifiable Diseases Framework
                                 Lab Reporter

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth informatics http://www.commoninf.com
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt

--------------------------------------------------------------------------------
'''

import sys, pprint, os, time, datetime, socket, subprocess, shlex, ftplib

from optparse import Values, make_option

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string, get_template
from django.core.management.base import BaseCommand

from ESP.emr.models import Patient_Addr, Patient_Guardian, LabOrder, LabResult, Specimen, Encounter
from ESP.conf.models import SiteHL7

from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.models import Case, ReportRun, Report, STATUS_CHOICES
from ESP.nodis.alt_mappings import ALTCODEMAPPING

from ESP.utils.utils import log, log_query

from ESP.settings import CASE_REPORT_OUTPUT_FOLDER, CASE_REPORT_TEMPLATE, CASE_REPORT_BATCH_SIZE 
from ESP.settings import CASE_REPORT_TRANSMIT, CASE_REPORT_TRANSPORT_SCRIPT, CASE_REPORT_FILENAME_FORMAT
from ESP.settings import FAKE_PATIENT_MRN, FAKE_PATIENT_SURNAME, CODEDIR, JAVA_DIR, JAVA_CLASSPATH, LOG_FILE, UPLOAD_SERVER
from ESP.settings import UPLOAD_USER, UPLOAD_PASSWORD, UPLOAD_PATH

#===============================================================================
#
#--- Configuration
#
#===============================================================================

VERSION = '2.5.1'

#===============================================================================
#
#--- Exceptions
#
#===============================================================================

class IncompleteCaseData(BaseException):
    '''
    Exception raised when a case does not have all the data elements required 
    to generate a valid HL7 message.
    '''
    pass

#===============================================================================
#
#--- Functions
#
#===============================================================================

def isoTime(t=None, tz=False):
    """ if tz is False, yyyymmddhhmmss - as of now unless a localtime is passed in
        if tz is True, yyyymmddhhmmss [timezone]
        Timezone is local timezone
    """
    if t == None:
        t=time.localtime()
    timeString  = time.strftime("%Y%m%d%H%M%S", t)
    if tz:
        timezone = -(time.altzone if t.tm_isdst else time.timezone)
        timeString += "Z" if timezone == 0 else "+" if timezone > 0 else "-"
        timeString += time.strftime("%H%M", time.gmtime(abs(timezone)))
        return timeString
    else:
        return timeString


#===============================================================================
#
#---  Basic structure of HL7 2.5.1 message is:
#---    MSH record (message header)
#---    SFT record (message generation software info)
#---    PID record (patient ID record)
#---      NTE record (Notes record -- can accompany any patient data record
#---    NK1 record (next of kin record -- like PID but for parent, guardian, spouse, etc.)
#---    PV1 record (patient visit record -- encounter dates)
#---    ORC record (lab order info)
#---      OBR records (observation request record.  1, or more if there are multiple distinct tests/specimens as part of order.  Think of this as one per test)
#---        OBX records (lab (observation) results record.  more than 1 if there are multiple results per test)
#---      SPM records (specimen record. 1, or more if there are multiple distinct tests/specimens as part of order. One per specimen)
#---        OBX records (specimen observations.  more than one if there are multiple observations about specimen)
#
#===============================================================================

class HL7DataObj:
    '''
    Generic data-holding object, with attributes assigned only to a specific instance.
    see https://docs.python.org/2/tutorial/classes.html#odds-and-ends
    ''' 
    pass


class MakeTemplateData:   
    '''
    class for building data required for template processing of HL7 v 2.5.1 ELR message
    ''' 
    def MakeMsh(self, patient):
        '''
        MSH data is site configured values from conf.sitehl7
        one value is created from case detail
        '''
        msh = HL7DataObj()
        msh_qs = SiteHL7.objects.all()
        msh.msh_2 = msh_qs.get(location='MSH.2').value
        msh.msh_3_1 = msh_qs.get(location='MSH.3.1').value
        msh.msh_3_2 = msh_qs.get(location='MSH.3.2').value
        msh.msh_3_3 = msh_qs.get(location='MSH.3.3').value
        msh.msh_4_1 = msh_qs.get(location='MSH.4.1').value
        msh.msh_4_2 = msh_qs.get(location='MSH.4.2').value
        msh.msh_4_3 = msh_qs.get(location='MSH.4.3').value
        msh.msh_5_1 = msh_qs.get(location='MSH.5.1').value
        msh.msh_5_2 = msh_qs.get(location='MSH.5.2').value
        msh.msh_5_3 = msh_qs.get(location='MSH.5.3').value
        msh.msh_6_1 = msh_qs.get(location='MSH.6.1').value
        msh.msh_6_2 = msh_qs.get(location='MSH.6.2').value
        msh.msh_6_3 = msh_qs.get(location='MSH.6.3').value
        #msh.msh_7_1 = isoTime(None, True)
        msh.msh_7_1 = '20120821140551-0500'
        msh.msh_9_1 = msh_qs.get(location='MSH.9.1').value
        msh.msh_9_2 = msh_qs.get(location='MSH.9.2').value
        msh.msh_9_3 = msh_qs.get(location='MSH.9.3').value
        msh.msh_10 = 'NIST-ELR-'+patient.natural_key
        msh.msh_11_1 = msh_qs.get(location='MSH.11.1').value
        msh.msh_15 = msh_qs.get(location='MSH.15').value
        msh.msh_16 = msh_qs.get(location='MSH.16').value
        msh.msh_21_1 = msh_qs.get(location='MSH.21.1').value
        msh.msh_21_2 = msh_qs.get(location='MSH.21.2').value
        msh.msh_21_3 = msh_qs.get(location='MSH.21.3').value
        msh.msh_21_4 = msh_qs.get(location='MSH.21.4').value
        return msh

    def MakeSft(self):
        '''
        SFT data is site configured values from conf.sitehl7
        '''
        sft = HL7DataObj()
        sft_qs = SiteHL7.objects.all()
        sft.sft_1_1 = sft_qs.get(location='SFT.1.1').value
        sft.sft_1_2 = sft_qs.get(location='SFT.1.2').value
        sft.sft_1_6_1 = sft_qs.get(location='SFT.1.6.1').value
        sft.sft_1_6_2 = sft_qs.get(location='SFT.1.6.2').value
        sft.sft_1_6_3 = sft_qs.get(location='SFT.1.6.3').value
        sft.sft_1_7 = sft_qs.get(location='SFT.1.7').value
        sft.sft_1_10 = sft_qs.get(location='SFT.1.10').value
        sft.sft_2 = sft_qs.get(location='SFT.2').value
        sft.sft_3 = sft_qs.get(location='SFT.3').value
        sft.sft_4 = sft_qs.get(location='SFT.4').value
        sft.sft_6_1 = sft_qs.get(location='SFT.6.1').value
        return sft

    def MakePid(self, patient):
        '''
        PID comes from emr_patient table and associated EMR data
        patient ID come from case
        '''
        pid = HL7DataObj()
        pid_site_qs = SiteHL7.objects.all()
        pid.pid_3 = self.MakePid_3(patient) 
        pid.pid_5 = self.MakePid_5(patient)
        if patient.mother_maiden_name:
            pid.pid_6_1_1 = patient.mother_maiden_name.split(" ")[3]
            pid.pid_6_2 = patient.mother_maiden_name.split(" ")[1]
            pid.pid_6_3 = patient.mother_maiden_name.split(" ")[2]
            pid.pid_6_4 = patient.mother_maiden_name.split(" ")[4]
            pid.pid_6_5 = patient.mother_maiden_name.split(" ")[0]
            pid.pid_6_7 = pid_site_qs.get(location='PID.6.7').value
            pid.pid_6_14 = patient.mother_maiden_name.split(" ")[5]
        else:
            pid.pid_6_1_1 = ''
            pid.pid_6_2 = ''
            pid.pid_6_3 = ''
            pid.pid_6_4 = ''
            pid.pid_6_5 = ''
            pid.pid_6_7 = ''
            pid.pid_6_14 = ''            
        pid.pid_7_1 = patient.date_of_birth.strftime("%Y%m%d")
        pid.pid_8 = patient.get_hl7('patient','gender',patient.gender, 'value')
        pid.pid_10_1  = patient.get_hl7('patient','race',patient.race, 'value')
        pid.pid_10_2  = patient.get_hl7('patient','race',patient.race, 'description')
        pid.pid_10_3 = patient.get_hl7('patient','race',patient.race, 'codesys')
        pid.pid_10_4 = ALTCODEMAPPING['patient.race'][patient.race][0]
        pid.pid_10_5 = ALTCODEMAPPING['patient.race'][patient.race][1]
        pid.pid_10_6 = ALTCODEMAPPING['patient.race'][patient.race][2]
        pid.pid_10_7  = patient.get_hl7('patient','race',patient.race, 'version')
        pid.pid_10_8 = ALTCODEMAPPING['patient.race'][patient.race][3]
        pid.pid_11 = self.MakePid_11(patient)
        pid.pid_13 = self.MakePid_13(patient)
        try:
            bsn_phn = Patient_Addr.objects.get(patient=patient.id, type='business phone')
            pid.pid_14_2 = 'WPN'
            pid.pid_14_3 = 'PH'
            pid.pid_14_4 = ''
            pid.pid_14_5 = bsn_phn.tel_country_code
            pid.pid_14_6 = bsn_phn.areacode
            pid.pid_14_7 = bsn_phn.tel
            pid.pid_14_8 = bsn_phn.tel_ext
            pid.pid_14_9 = bsn_phn.call_info
        except:
            pid.pid_14_2 = ''
            pid.pid_14_3 = ''
            pid.pid_14_4 = ''
            pid.pid_14_5 = ''
            pid.pid_14_6 = ''
            pid.pid_14_7 = ''
            pid.pid_14_8 = ''
            pid.pid_14_9 = ''
        pid.pid_22_1 = patient.get_hl7('patient','ethnicity',patient.ethnicity, 'value')
        pid.pid_22_2 = patient.get_hl7('patient','ethnicity',patient.ethnicity, 'description')
        pid.pid_22_3 = patient.get_hl7('patient','ethnicity',patient.ethnicity, 'codesys')
        pid.pid_22_4 = ALTCODEMAPPING['patient.ethnicity'][patient.ethnicity][0]
        pid.pid_22_5 = ALTCODEMAPPING['patient.ethnicity'][patient.ethnicity][1]
        pid.pid_22_6 = ALTCODEMAPPING['patient.ethnicity'][patient.ethnicity][2]
        pid.pid_22_7 = patient.get_hl7('patient','ethnicity',patient.ethnicity, 'version')
        pid.pid_22_8 = ALTCODEMAPPING['patient.ethnicity'][patient.ethnicity][3]
        pid.pid_29_1 = patient.cdate_of_death
        pid.pid_30 = patient.patient_extradata_set.get().death_ind
        pid.pid_33_1 = patient.clast_update
        pid.pid_34_1 = patient.last_update_site 
        pid.pid_34_2 = patient.patient_extradata_set.get().lsu_uid
        pid.pid_34_3 = patient.patient_extradata_set.get().lsu_uidtype
        pid.pid_35_1 = patient.get_hl7('patient','species',patient.patient_extradata_set.get().species,'value')
        pid.pid_35_2 = patient.get_hl7('patient','species',patient.patient_extradata_set.get().species,'description')
        pid.pid_35_3 = patient.get_hl7('patient','species',patient.patient_extradata_set.get().species,'codesys')
        pid.pid_35_4 = ALTCODEMAPPING['patient.species'][patient.patient_extradata_set.get().species][0]
        pid.pid_35_5 = ALTCODEMAPPING['patient.species'][patient.patient_extradata_set.get().species][1]
        pid.pid_35_6 = ALTCODEMAPPING['patient.species'][patient.patient_extradata_set.get().species][2]
        pid.pid_35_7 = patient.get_hl7('patient','species',patient.patient_extradata_set.get().species,'version')
        pid.pid_35_8 = ALTCODEMAPPING['patient.species'][patient.patient_extradata_set.get().species][3]
        return pid
        
    def MakePid_3(self,patient):
        '''
        PID3 is a repeating set
        '''
        #pid.incr pid_3_1 pid_3_4_1 pid_3_4_2 pid_3_4_3 pid_3_5 pid_3_6_1 pid_3_6_2 pid_3_6_3 repeating
        pid_3 = []
        pid = HL7DataObj() 

        xInfo = patient.patient_extradata_set.get()
        pid.incr = 1
        pid.pid_3_1 = patient.mrn
        pid.pid_3_4_1 = xInfo.auth_nid 
        pid.pid_3_4_2 = xInfo.auth_uid
        pid.pid_3_4_3 = xInfo.auth_uidtype
        pid.pid_3_5 = xInfo.id_typecode 
        pid.pid_3_6_1 = xInfo.fac_nid 
        pid.pid_3_6_2 = xInfo.fac_uid 
        pid.pid_3_6_3 = xInfo.fac_uidtype
        pid_3.append(pid)
        if patient.ssn:
            site_qs = SiteHL7.objects.all()
            pid = HL7DataObj()
            pid.incr = 2
            pid.pid_3_1 = patient.ssn 
            pid.pid_3_4_1 = site_qs.get(location='PID.3.4.1').value 
            pid.pid_3_4_2 = site_qs.get(location='PID.3.4.2').value
            pid.pid_3_4_3 = site_qs.get(location='PID.3.4.3').value  
            pid.pid_3_5 = site_qs.get(location='PID.3.5').value
            pid.pid_3_6_1 = site_qs.get(location='PID.3.6.1').value  
            pid.pid_3_6_2 = site_qs.get(location='PID.3.6.2').value
            pid.pid_3_6_3 = site_qs.get(location='PID.3.6.3').value
            pid_3.append(pid)
        return pid_3

    def MakePid_5(self,patient):
        '''
        PID5 is a repeating set
        '''
        #pid_5_1_1 pid_5_2 pid_5_3 pid_5_4 pid_5_5 pid_5_7 pid_5_14 repeating
        pid_5 = []
        pid = HL7DataObj() 
        pid.incr = 1
        pid.pid_5_1_1 = patient.last_name
        pid.pid_5_2 = patient.first_name
        pid.pid_5_3 = patient.middle_name
        sfxlist = patient.titles.split(',')
        pid.pid_5_4 = sfxlist[0] if len(sfxlist)>0 else ''
        pid.pid_5_5 = sfxlist[1] if len(sfxlist)>1 else '' 
        pid.pid_5_7 = sfxlist[3] if len(sfxlist)>3 else ''
        pid.pid_5_14 = sfxlist[2] if len(sfxlist)>2 else ''
        pid_5.append(pid)
        if patient.aliases:
            pid = HL7DataObj()
            aliaslst = patient.aliases.split(' ')
            #TODO: this currently works if there is only one alias.  Spliting/parsing will need to get much trickier for multiple aliases.
            pid.incr = 2
            pid.pid_5_1_1 = aliaslst[2] if len(aliaslst)>2 else '' 
            pid.pid_5_2 = aliaslst[0] if len(aliaslst)>0 else ''  
            pid.pid_5_3 = aliaslst[1] if len(aliaslst)>1 else ''   
            pid.pid_5_4 = aliaslst[3] if len(aliaslst)>3 else ''
            pid.pid_5_5 = ''  
            pid.pid_5_7 = 'B'  
            pid.pid_5_14 = ''  
            pid_5.append(pid)
        return pid_5
    
    def MakePid_11(self, patient):
        '''
        PID11 is a repeating set
        '''
        #pid_11_1_1 pid_11_2 pid_11_3 pid_11_4 pid_11_5 pid_11_6 pid_11_7 pid_11_9 repeating
        inc = 0
        pid_11 = []
        addresses = Patient_Addr.objects.filter(patient=patient.id).order_by('-type')
        for address in addresses:
            if address.address1:
                pid = HL7DataObj()
                pid.incr = inc + 1 
                pid.pid_11_1_1 = address.address1
                pid.pid_11_2 = address.address2
                pid.pid_11_3 = address.city
                pid.pid_11_4 = address.state
                pid.pid_11_5 = address.zip
                pid.pid_11_6 = address.country
                pid.pid_11_7 = patient.get_hl7('patient','type',address.type, 'value')
                pid.pid_11_9 = address.county_code
                pid_11.append(pid)
                inc += 1
        return pid_11        
                
    def MakePid_13(self,patient):
        '''
        PID13 is a repeating set
        '''
        #pid_13_2 pid_13_3 pid_13_4 pid_13_5 pid_13_6 pid_13_7 pid_13_8 pid_13_9 repeating 
        inc = 0
        pid_13 = []
        addresses = Patient_Addr.objects.filter(patient=patient.id).order_by('type')
        for address in addresses:
            if any(atype in address.type for atype in ['home address','other phone']):
                pid = HL7DataObj()
                pid.incr = inc + 1
                pid.pid_13_2 = address.use
                pid.pid_13_3 = address.eqptype
                pid.pid_13_4 = ''
                pid.pid_13_5 = address.tel_country_code
                pid.pid_13_6 = address.areacode
                pid.pid_13_7 = address.tel
                pid.pid_13_8 = address.tel_ext
                pid.pid_13_9 = address.call_info
                pid_13.append(pid)
                inc += 1
            if address.type=='primary email':
                pid = HL7DataObj()
                pid.incr = inc + 1
                pid.pid_13_2 = 'NET'
                pid.pid_13_3 = 'Internet'
                pid.pid_13_4 = address.email
                pid.pid_13_5 = ''
                pid.pid_13_6 = ''
                pid.pid_13_7 = ''
                pid.pid_13_8 = ''
                pid.pid_13_9 = address.call_info
                pid_13.append(pid)
                inc += 1
        return pid_13        

    def MakeNteP(self,patient):
        '''
        NTE is notes and comments and can follow PID, OBR or OBX
        This is the PID version
        This is an optional record
        '''
        if patient.remark:
            nte = HL7DataObj()
            nte.nte_1 = '1'
            nte.nte_2 = 'P'
            nte.nte_3 = patient.remark
            nte.nte_4_1 = 'RE'
            nte.nte_4_2 = 'Remark'
            nte.nte_4_3 = 'HL70364'
            nte.nte_4_4 = 'C'
            nte.nte_4_5 = 'Comment'
            nte.nte_4_6 = 'L'
            nte.nte_4_7 = '2.5.1'
            nte.nte_4_8 = 'V1'
        else:
            nte = []
        return nte
    
    def MakeNk1(self,patient):
        '''
        NK1 is next of kin and follow PID (or PID-NTE)
        This is an optional record, but is typically available
        '''
        grd_qs = Patient_Guardian.objects.filter(patient=patient.id)
        nk1_lst = []
        incr=1
        for grd in grd_qs:
            nk1 = HL7DataObj()
            nk1.nk1_1 = incr
            if grd.relationship:
                nk1.person=True
                nk1.nk1_2_1_1 = grd.last_name
                nk1.nk1_2_2 = grd.first_name
                nk1.nk1_2_3 = grd.middle_name
                if grd.suffix:
                    nk1.nk1_2_4 = grd.suffix.split(" ")[0] 
                nk1.nk1_2_5 = grd.title
                nk1.nk1_2_7 = 'L'
                if grd.suffix:
                    try:
                        nk1.nk1_2_14 = grd.suffix.split(" ")[1]
                    except:
                        nk1.nk1_2_14 = ''
                nk1.nk1_3_1 = grd.get_basePat_hl7('patient_guardian','relationship',grd.relationship, 'value')
                nk1.nk1_3_2 = grd.get_basePat_hl7('patient_guardian','relationship',grd.relationship, 'description')
                nk1.nk1_3_3 = grd.get_basePat_hl7('patient_guardian','relationship',grd.relationship, 'codesys')
                nk1.nk1_3_4 = ALTCODEMAPPING['patient_guardian.relationship'][grd.relationship][0]
                nk1.nk1_3_5 = ALTCODEMAPPING['patient_guardian.relationship'][grd.relationship][1]
                nk1.nk1_3_6 = ALTCODEMAPPING['patient_guardian.relationship'][grd.relationship][2]
                nk1.nk1_3_7 = grd.get_basePat_hl7('patient_guardian','relationship',grd.relationship, 'version')
                nk1.nk1_3_8 = ALTCODEMAPPING['patient_guardian.relationship'][grd.relationship][3]
                nk1.nk1_4_1_1 = grd.address1
                nk1.nk1_4_2 = grd.address2
                nk1.nk1_4_3 = grd.city
                nk1.nk1_4_4 = grd.state
                nk1.nk1_4_5 = grd.zip
                nk1.nk1_4_6 = grd.country
                nk1.nk1_4_7 = grd.get_basePat_hl7('patient_guardian','type',grd.type,'value')
                nk1.nk1_4_9 = grd.county_code
                nk1.nk1_5 = self.MakeNk1_5(grd)
                nk1_lst.append(nk1)
                incr += 1
            elif grd.organization:
                nk1.person=False
                nk1.nk1_13_1 = grd.organization
                nk1.nk1_13_2='L'
                nk1.nk1_13_6_1 = grd.auth_nid 
                nk1.nk1_13_6_2 = grd.auth_uid
                nk1.nk1_13_6_3 = grd.auth_uidtype
                nk1.nk1_13_7 = grd.idtype_code
                nk1.nk1_13_10 = grd.org_id
                nk1.nk1_30_1_1 = grd.last_name
                nk1.nk1_30_2 = grd.first_name
                nk1.nk1_30_3 = grd.middle_name
                if grd.suffix:
                    nk1.nk1_30_4 = grd.suffix.split(" ")[0]
                nk1.nk1_30_5 = grd.title
                nk1.nk1_30_7 = 'L'
                if grd.suffix:
                    try:
                        nk1.nk1_30_14 = grd.suffix.split(" ")[1]
                    except:
                        nk1.nk1_30_14 = ''
                nk1.nk1_31_2 = 'WPN'
                nk1.nk1_31_3 = 'PH'
                nk1.nk1_31_4 = ''
                nk1.nk1_31_5 = grd.tel_country_code
                nk1.nk1_31_6 = grd.areacode
                nk1.nk1_31_7 = grd.tel
                nk1.nk1_31_8 = grd.tel_ext
                nk1.nk1_31_9 = grd.call_info
                nk1.nk1_32_1_1 = grd.address1
                nk1.nk1_32_2 = grd.address2
                nk1.nk1_32_3 = grd.city
                nk1.nk1_32_4 = grd.state
                nk1.nk1_32_5 = grd.zip
                nk1.nk1_32_6 = grd.country
                nk1.nk1_32_7 = grd.type
                nk1.nk1_32_9 = grd.county_code
                nk1_lst.append(nk1)
                incr += 1
        return nk1_lst
 
    def MakeNk1_5(self,grd):   
        '''
        NK1_5 is a repeating set
        '''
        #nk1.incr nk1.nk1_5_2 nk1.nk1_5_3 nk1.nk1_5_4 nk1.nk1_5_5 nk1.nk1_5_6 nk1.nk1_5_7 nk1.nk1_5_8 nk1.nk1_5_9
        nk1_5= []
        nk1 = HL7DataObj()
        nk1.incr = 1 
        nk1.nk1_5_2 = 'PRN'
        nk1.nk1_5_3 = 'PH'
        nk1.nk1_5_4 = ''
        nk1.nk1_5_5 = grd.tel_country_code
        nk1.nk1_5_6 = grd.areacode
        nk1.nk1_5_7 = grd.tel
        nk1.nk1_5_8 = grd.tel_ext
        nk1.nk1_5_9 = grd.call_info
        nk1_5.append(nk1)
        nk1 = HL7DataObj()
        nk1.incr = 2 
        nk1.nk1_5_2 = 'NET'
        nk1.nk1_5_3 = 'Internet'
        nk1.nk1_5_4 = grd.email
        nk1.nk1_5_5 = ''
        nk1.nk1_5_6 = ''
        nk1.nk1_5_7 = ''
        nk1.nk1_5_8 = ''
        nk1.nk1_5_9 = grd.email_info
        nk1_5.append(nk1)
        return nk1_5

    def MakePv1(self,enc):
        '''
        Pv1 is patient visit info
        This is an optional record, but is typically available
        '''
        if enc.raw_date:
            pv1 = HL7DataObj()
            pv1.pv1_1 = '1'
            pv1.pv1_2 = 'O'
            pv1.pv1_4 = 'C'
            pv1.pv1_44_1 = enc.raw_date
            pv1.pv1_45_1 = enc.raw_date_closed
        else:
            pv1 = []
        return pv1

    def MakeOrc(self, ordr):
        '''
        ORC is the common order record
        There will one of these
        '''
        orc = HL7DataObj()
        #implicit assumption that there will be a single order_idinfo record.  Unique constraint in model enforces this
        orc.orc_1 = 'RE'
        orc.orc_2_1 = ordr.order_idinfo_set.get().placer_ord_eid
        orc.orc_2_2 = ordr.order_idinfo_set.get().placer_ord_nid
        orc.orc_2_3 = ordr.order_idinfo_set.get().placer_ord_uid
        orc.orc_2_4 = ordr.order_idinfo_set.get().placer_ord_uid_type
        orc.orc_3_1 = ordr.order_idinfo_set.get().filler_ord_eid
        orc.orc_3_2 = ordr.order_idinfo_set.get().filler_ord_nid
        orc.orc_3_3 = ordr.order_idinfo_set.get().filler_ord_uid
        orc.orc_3_4 = ordr.order_idinfo_set.get().filler_ord_uid_type
        orc.orc_4_1 = ordr.order_idinfo_set.get().placer_grp_eid
        orc.orc_4_2 = ordr.order_idinfo_set.get().placer_grp_nid
        orc.orc_4_3 = ordr.order_idinfo_set.get().placer_grp_uid
        orc.orc_4_4 = ordr.order_idinfo_set.get().placer_grp_uid_type
        orc.orc_12_1 = ''
        orc.orc_12_2_1 = ordr.provider.last_name
        orc.orc_12_3 = ordr.provider.first_name
        orc.orc_12_4 = ordr.provider.middle_name
        orc.orc_12_5 = ''
        if ordr.provider.suffix:
            orc.orc_12_5 = ordr.provider.suffix.split(',')[0]
        orc.orc_12_6 = ordr.provider.title
        try:
            orc.orc_12_1 = ordr.provider.provider_idinfo_set.get().provider_nistid
            orc.orc_12_9_1 = ordr.provider.provider_idinfo_set.get().auth_namespaceid
            orc.orc_12_9_2 = ordr.provider.provider_idinfo_set.get().auth_universalid
            orc.orc_12_9_3 = ordr.provider.provider_idinfo_set.get().auth_universalidtype
            orc.orc_12_10 = ordr.provider.provider_idinfo_set.get().name_typecode
            orc.orc_12_13 = ordr.provider.provider_idinfo_set.get().identifier_typecode
            orc.orc_12_14_1 = ordr.provider.provider_idinfo_set.get().fac_namespaceid
            orc.orc_12_14_2 = ordr.provider.provider_idinfo_set.get().fac_universalid
            orc.orc_12_14_3 = ordr.provider.provider_idinfo_set.get().fac_universalidtype
            orc.orc_21_2 = ordr.provider.provider_idinfo_set.get().facname_type
            orc.orc_21_6_1 = ordr.provider.provider_idinfo_set.get().facname_auth_nid
            orc.orc_21_6_2 = ordr.provider.provider_idinfo_set.get().facname_auth_uid
            orc.orc_21_6_3 = ordr.provider.provider_idinfo_set.get().facname_auth_uidtype
            orc.orc_21_7 = ordr.provider.provider_idinfo_set.get().facname_auth_idtype
            orc.orc_21_10 = ordr.provider.provider_idinfo_set.get().facname_auth_id
        except:
            orc.orc_12_1 = ''
            orc.orc_12_9_1 = ''
            orc.orc_12_9_2 = ''
            orc.orc_12_9_3 = ''
            orc.orc_12_10 = ''
            orc.orc_12_13 = ''
            orc.orc_12_14_1 = ''
            orc.orc_12_14_2 = ''
            orc.orc_12_14_3 = ''
            orc.orc_21_2 = ''
            orc.orc_21_6_1 = ''
            orc.orc_21_6_2 = ''
            orc.orc_21_6_3 = ''
            orc.orc_21_7 = ''
            orc.orc_21_10 = ''
        orc.orc_12_21 = ''
        if ordr.provider.suffix:
            try:
                orc.orc_12_21 = ordr.provider.suffix.split(',')[1]
            except:
                pass #noting to do -- just leave 12_21 as empty          
        orc.orc_14 = self.MakeOrc_14(ordr)
        orc.orc_21_1 = ordr.provider.dept
        orc.orc_22_1_1 = ordr.provider.dept_address_1
        orc.orc_22_2 = ordr.provider.dept_address_2
        orc.orc_22_3 = ordr.provider.dept_city
        orc.orc_22_4 = ordr.provider.dept_state
        orc.orc_22_5 = ordr.provider.dept_zip
        orc.orc_22_6 = ordr.provider.dept_country
        orc.orc_22_7 = ordr.provider.dept_addr_type
        orc.orc_22_9 = ordr.provider.dept_county_code
        orc.orc_23_2 = 'WPN'
        orc.orc_23_3 = 'PH'
        orc.orc_23_4 = ''
        orc.orc_23_5 = ordr.provider.tel_country_code
        orc.orc_23_6 = ordr.provider.area_code
        orc.orc_23_7 = ordr.provider.telephone
        orc.orc_23_8 = ordr.provider.tel_ext
        orc.orc_23_9 = ordr.provider.call_info
        orc.orc_24_1_1 = ordr.provider.clin_address1
        orc.orc_24_2 = ordr.provider.clin_address2
        orc.orc_24_3 = ordr.provider.clin_city
        orc.orc_24_4 = ordr.provider.clin_state
        orc.orc_24_5 = ordr.provider.clin_zip
        orc.orc_24_6 = ordr.provider.clin_country
        orc.orc_24_7 = ordr.provider.clin_addr_type
        orc.orc_24_9 = ordr.provider.clin_county_code
        return orc
    
    def MakeOrc_14(self, ordr):
        '''
        ORC_14 is a repeating set
        '''
        #orc.orc_14_2 orc.orc_14_3 orc.orc_14_4 orc.orc_14_5 orc.orc_14_6 orc.orc_14_7 orc.orc_14_8 orc.orc_14_9
        orc_14 = []
        incr = 1
        for phn in ordr.provider.provider_phones_set.all().order_by('tel_info'):
            orc = HL7DataObj()
            orc.incr = incr
            orc.orc_14_2 = phn.tel_use_code 
            orc.orc_14_3 = phn.tel_eqp_type
            orc.orc_14_4 = phn.email
            orc.orc_14_5 = phn.tel_countrycode
            orc.orc_14_6 = phn.tel_areacode
            orc.orc_14_7 = phn.tel
            orc.orc_14_8 = phn.tel_extension
            orc.orc_14_9 = phn.tel_info
            orc_14.append(orc)
            incr += 1
        return orc_14

        
    def MakeObr(self,ordr,ordLabs,n):
        '''
        OBR is Observation Request
        '''
        obr = HL7DataObj()
        obr.obr_1 = n
        obr.obr_2_1 = ordr.order_idinfo_set.get().placer_ord_eid
        obr.obr_2_2 = ordr.order_idinfo_set.get().placer_ord_nid
        obr.obr_2_3 = ordr.order_idinfo_set.get().placer_ord_uid
        obr.obr_2_4 = ordr.order_idinfo_set.get().placer_ord_uid_type
        obr.obr_3_1 = ordr.order_idinfo_set.get().filler_ord_eid
        obr.obr_3_2 = ordr.order_idinfo_set.get().filler_ord_nid
        obr.obr_3_3 = ordr.order_idinfo_set.get().filler_ord_uid
        obr.obr_3_4 = ordr.order_idinfo_set.get().filler_ord_uid_type
        obr.obr_4_1 = ordr.get_hl7('laborder','procedure_code',ordr.procedure_code, 'value')
        obr.obr_4_2 = ordr.get_hl7('laborder','procedure_code',ordr.procedure_code, 'description')
        obr.obr_4_3 = ordr.get_hl7('laborder','procedure_code',ordr.procedure_code, 'codesys')
        obr.obr_4_4 = ALTCODEMAPPING['laborder.procedure_code'][ordr.procedure_code][0]
        obr.obr_4_5 = ALTCODEMAPPING['laborder.procedure_code'][ordr.procedure_code][1]
        obr.obr_4_6 = ALTCODEMAPPING['laborder.procedure_code'][ordr.procedure_code][2]
        obr.obr_4_7 = ordr.get_hl7('laborder','procedure_code',ordr.procedure_code, 'version')
        obr.obr_4_8 = ALTCODEMAPPING['laborder.procedure_code'][ordr.procedure_code][3]
        obr.obr_7_1 = ordr.obs_start_date
        obr.obr_8_1 = ordr.obs_end_date
        obr.obr_13 = ordr.order_info
        try:
            obr.obr_16_1 = ordr.provider.provider_idinfo_set.get().provider_nistid
        except:
            obr.obr_16_1 = ''
        obr.obr_16_2_1 = ordr.provider.last_name
        obr.obr_16_3 = ordr.provider.first_name
        obr.obr_16_4 = ordr.provider.middle_name
        obr.obr_16_5 = ''
        if ordr.provider.suffix:
            obr.obr_16_5 = ordr.provider.suffix.split(',')[0]
        obr.obr_16_6 = ordr.provider.title
        try:
            obr.obr_16_9_1 = ordr.provider.provider_idinfo_set.get().auth_namespaceid
            obr.obr_16_9_2 = ordr.provider.provider_idinfo_set.get().auth_universalid
            obr.obr_16_9_3 = ordr.provider.provider_idinfo_set.get().auth_universalidtype
            obr.obr_16_10 = ordr.provider.provider_idinfo_set.get().name_typecode
            obr.obr_16_13 = ordr.provider.provider_idinfo_set.get().identifier_typecode
            obr.obr_16_14_1 = ordr.provider.provider_idinfo_set.get().fac_namespaceid
            obr.obr_16_14_2 = ordr.provider.provider_idinfo_set.get().fac_universalid
            obr.obr_16_14_3 = ordr.provider.provider_idinfo_set.get().fac_universalidtype
        except:
            obr.obr_16_9_1 = ''
            obr.obr_16_9_2 = ''
            obr.obr_16_9_3 = ''
            obr.obr_16_10 = ''
            obr.obr_16_13 = ''
            obr.obr_16_14_1 = ''
            obr.obr_16_14_2 = ''
            obr.obr_16_14_3 = ''
        obr.obr_16_21 = ''
        if ordr.provider.suffix:
            try:
                obr.obr_16_21 = ordr.provider.suffix.split(',')[1]
            except:
                pass #noting to do -- just leave 12_21 as empty          
        obr.obr_17 = self.MakeObr_17(ordr)
        obr.obr_22_1 = ordLabs[0].cresult_date
        obr.obr_25 = ordr.test_status
        obr.obr_26 = False
        obr.obr_29 = False
        if ordr.parent_res:
            obr.obr_26 = True
            obr.obr_29 = True
            prntlb = LabResult.objects.get(natural_key=ordr.parent_res)
            obr.obr_26_1_1 = prntlb.get_hl7('labresult','native_code',prntlb.native_code, 'value')
            obr.obr_26_1_2 = prntlb.get_hl7('labresult','native_code',prntlb.native_code, 'description')
            obr.obr_26_1_3 = prntlb.get_hl7('labresult','native_code',prntlb.native_code, 'codesys')
            obr.obr_26_1_4 = ALTCODEMAPPING['labresult.native_code'][prntlb.native_code][0]
            obr.obr_26_1_5 = ALTCODEMAPPING['labresult.native_code'][prntlb.native_code][1]
            obr.obr_26_1_6 = ALTCODEMAPPING['labresult.native_code'][prntlb.native_code][2]
            obr.obr_26_2 = ''
            if prntlb.labresult_details_set.get().char_finding:
                obr.obr_26_3 = prntlb.get_hl7('labresult','char_finding',prntlb.labresult_details_set.get().char_finding,'description')
            elif prntlb.labresult_details_set.get().num1:
                obr.obr_26_3 = prntlb.labresult_details_set.get().num1
            else: 
                obr.obr_26_3 = None
            prntord = LabOrder.objects.get(natural_key=prntlb.order_natural_key)
            obr.obr_29_2_1 = prntord.order_idinfo_set.get().filler_ord_eid
            obr.obr_29_2_2 = prntord.order_idinfo_set.get().filler_ord_nid
            obr.obr_29_2_3 = prntord.order_idinfo_set.get().filler_ord_uid
            obr.obr_29_2_4 = prntord.order_idinfo_set.get().filler_ord_uid_type
        obr.obr_31_1 = ordr.reason_code
        obr.obr_31_2 = ordr.get_hl7('laborder','reason_code',ordr.reason_code, 'description') if ordr.reason_code else ''
        obr.obr_31_3 = ordr.get_hl7('laborder','reason_code',ordr.reason_code, 'codesys') if ordr.reason_code else ''
        obr.obr_31_4 = ALTCODEMAPPING['laborder.reason_code'][ordr.reason_code][0] if ordr.reason_code else ''
        obr.obr_31_5 = ALTCODEMAPPING['laborder.reason_code'][ordr.reason_code][1] if ordr.reason_code else ''
        obr.obr_31_6 = ALTCODEMAPPING['laborder.reason_code'][ordr.reason_code][2] if ordr.reason_code else ''
        obr.obr_31_7 = ordr.get_hl7('laborder','reason_code',ordr.reason_code, 'version') if ordr.reason_code else ''
        obr.obr_31_8 = ALTCODEMAPPING['laborder.reason_code'][ordr.reason_code][3] if ordr.reason_code else ''
        obr.obr_31_9 = ''
        obr.obr_32_1_1 = ordLabs[0].interpreter_id
        obr.obr_32_1_2 = ''
        obr.obr_32_1_3 = ''
        obr.obr_32_1_4 = ''
        obr.obr_32_1_5 = ''
        obr.obr_32_1_6 = ''
        obr.obr_32_1_7 = ''
        if ordLabs[0].interpreter:
            try:
                obr.obr_32_1_3 = ordLabs[0].interpreter.split(' ')[0]
                obr.obr_32_1_4 = ordLabs[0].interpreter.split(' ')[1]
                obr.obr_32_1_2 = ordLabs[0].interpreter.split(' ')[2]
                obr.obr_32_1_5 = ordLabs[0].interpreter.split(' ')[3]
                obr.obr_32_1_6 = ordLabs[0].interpreter.split(' ')[4]
                obr.obr_32_1_7 = ordLabs[0].interpreter.split(' ')[5]
            except:
                pass #just leave them empty if values aren't there
        obr.obr_32_1_9 = ordLabs[0].interp_id_auth
        obr.obr_32_1_10 = ordLabs[0].interp_uid
        if ordLabs[0].interp_uid:
            obr.obr_32_1_11 = 'ISO'
        return obr
    
    def MakeObr_17(self, ordr):
        '''
        OBR_17 is a repeating set
        '''
        #obr_17.obr_17_2 obr_17.obr_17_3 obr_17.obr_17_4 obr_17.obr_17_5 obr_17.obr_17_6 obr_17.obr_17_7 obr_17.obr_17_8 obr_17.obr_17_9 
        obr_17 = []
        incr = 1
        for phn in ordr.provider.provider_phones_set.all().order_by('tel_info'):
            obr = HL7DataObj()
            obr.incr = incr
            obr.obr_17_2 = phn.tel_use_code 
            obr.obr_17_3 = phn.tel_eqp_type
            obr.obr_17_4 = phn.email
            obr.obr_17_5 = phn.tel_countrycode
            obr.obr_17_6 = phn.tel_areacode
            obr.obr_17_7 = phn.tel
            obr.obr_17_8 = phn.tel_extension
            obr.obr_17_9 = phn.tel_info
            obr_17.append(obr)
            incr += 1
        return obr_17

    def MakeNteR(self,ordr):
        '''
        NTE is notes and comments and can follow PID, OBR or OBX
        This is the OBR version
        This is an optional record
        '''
        if ordr.remark:
            nte = HL7DataObj()
            nte.nte_1 = '1'
            nte.nte_2 = 'L'
            nte.nte_3 = ordr.remark
            nte.nte_4_1 = 'RE'
            nte.nte_4_2 = 'Remark'
            nte.nte_4_3 = 'HL70364'
            nte.nte_4_4 = ''
            nte.nte_4_5 = ''
            nte.nte_4_6 = ''
            nte.nte_4_7 = ''
            nte.nte_4_8 = ''
        else:
            nte = []
        return nte
    
    def MakeObxL(self,lab, n):
        '''
        OBX is the observation record, you can have them for Lab results, or specimen observations.
        This version is for labs
        '''
        obx = HL7DataObj()
        obx.obx_1 = n
        if lab.labresult_details_set.get().num1:
            obx.obx_2 = 'SN'
        else:
            obx.obx_2 = 'CWE'
        obx.obx_3_1 = lab.get_hl7('labresult','native_code',lab.native_code, 'value')
        obx.obx_3_2 = lab.get_hl7('labresult','native_code',lab.native_code, 'description')
        obx.obx_3_3 = lab.get_hl7('labresult','native_code',lab.native_code, 'codesys')
        obx.obx_3_4 = ALTCODEMAPPING['labresult.native_code'][lab.native_code][0]
        obx.obx_3_5 = ALTCODEMAPPING['labresult.native_code'][lab.native_code][1]
        obx.obx_3_6 = ALTCODEMAPPING['labresult.native_code'][lab.native_code][2]
        obx.obx_3_7 = lab.get_hl7('labresult','native_code',lab.native_code, 'version')
        obx.obx_3_8 = ALTCODEMAPPING['labresult.native_code'][lab.native_code][3]
        obx.obx_3_9 =''
        obx.obx_4 = lab.labresult_details_set.get().sub_id
        if lab.labresult_details_set.get().num1:
            obx.obx_5_sn_1 = lab.labresult_details_set.get().comparator
            obx.obx_5_sn_2 = lab.labresult_details_set.get().num1
            obx.obx_5_sn_3 = lab.labresult_details_set.get().sep_suff
            obx.obx_5_sn_4 = lab.labresult_details_set.get().num2
        else:
            obx.obx_5_cwe_1 = lab.get_hl7('labresult','char_finding',lab.labresult_details_set.get().char_finding, 'value')
            obx.obx_5_cwe_2 = lab.get_hl7('labresult','char_finding',lab.labresult_details_set.get().char_finding, 'description')
            obx.obx_5_cwe_3 = lab.get_hl7('labresult','char_finding',lab.labresult_details_set.get().char_finding, 'codesys')
            obx.obx_5_cwe_4 = ALTCODEMAPPING['labresult.char_finding'][lab.labresult_details_set.get().char_finding][0]
            obx.obx_5_cwe_5 = ALTCODEMAPPING['labresult.char_finding'][lab.labresult_details_set.get().char_finding][1]
            obx.obx_5_cwe_6 = ALTCODEMAPPING['labresult.char_finding'][lab.labresult_details_set.get().char_finding][2]
            obx.obx_5_cwe_7 = lab.get_hl7('labresult','char_finding',lab.labresult_details_set.get().char_finding, 'version')
            obx.obx_5_cwe_8 = ALTCODEMAPPING['labresult.char_finding'][lab.labresult_details_set.get().char_finding][3]
            obx.obx_5_cwe_9 = lab.labresult_details_set.get().orig_text
        obx.obx_6_1 = lab.ref_unit
        obx.obx_6_2 = lab.get_hl7('labresult','ref_unit',lab.ref_unit, 'description')
        obx.obx_6_3 = lab.get_hl7('labresult','ref_unit',lab.ref_unit, 'codesys')
        obx.obx_6_4 = ALTCODEMAPPING['labresult.ref_unit'][lab.ref_unit][0]
        obx.obx_6_5 = ALTCODEMAPPING['labresult.ref_unit'][lab.ref_unit][1]
        obx.obx_6_6 = ALTCODEMAPPING['labresult.ref_unit'][lab.ref_unit][2]
        obx.obx_6_7 = lab.get_hl7('labresult','ref_unit',lab.ref_unit, 'version')
        obx.obx_6_8 = ALTCODEMAPPING['labresult.ref_unit'][lab.ref_unit][3]
        obx.obx_6_9 = ''
        obx.obx_7 = lab.labresult_details_set.get().ref_range
        obx.obx_8_1 = lab.get_hl7('labresult','abnormal_flag',lab.abnormal_flag, 'value')
        obx.obx_8_2 = lab.get_hl7('labresult','abnormal_flag',lab.abnormal_flag, 'description')
        obx.obx_8_3 = lab.get_hl7('labresult','abnormal_flag',lab.abnormal_flag, 'codesys')
        obx.obx_8_4 = ALTCODEMAPPING['labresult.abnormal_flag'][lab.abnormal_flag][0]
        obx.obx_8_5 = ALTCODEMAPPING['labresult.abnormal_flag'][lab.abnormal_flag][1]
        obx.obx_8_6 = ALTCODEMAPPING['labresult.abnormal_flag'][lab.abnormal_flag][2]
        obx.obx_8_7 = lab.get_hl7('labresult','abnormal_flag',lab.abnormal_flag, 'version')
        obx.obx_8_8 = ALTCODEMAPPING['labresult.abnormal_flag'][lab.abnormal_flag][3]
        obx.obx_11 = lab.status
        obx.obx_14_1 = lab.ccollection_date
        obx.obx_17_1 = lab.get_hl7('labresult','lab_method',lab.lab_method, 'value')
        obx.obx_17_2 = lab.get_hl7('labresult','lab_method',lab.lab_method, 'description')
        obx.obx_17_3 = lab.get_hl7('labresult','lab_method',lab.lab_method, 'codesys')
        obx.obx_17_4 = ALTCODEMAPPING['labresult.lab_method'][lab.lab_method][0]
        obx.obx_17_5 = ALTCODEMAPPING['labresult.lab_method'][lab.lab_method][1]
        obx.obx_17_6 = ALTCODEMAPPING['labresult.lab_method'][lab.lab_method][2]
        obx.obx_17_7 = lab.get_hl7('labresult','lab_method',lab.lab_method, 'version')
        obx.obx_17_8 = ALTCODEMAPPING['labresult.lab_method'][lab.lab_method][3]
        obx.obx_19_1 = lab.cstatus_date
        obx.obx_23_1 = lab.CLIA_ID.laboratory_name
        obx.obx_23_2 = lab.CLIA_ID.lab_name_type_code
        obx.obx_23_6_1 = lab.CLIA_ID.perf_auth_nid
        obx.obx_23_6_2 = lab.CLIA_ID.perf_auth_uid
        obx.obx_23_6_3 = lab.CLIA_ID.perf_auth_uidtype
        obx.obx_23_7 = lab.CLIA_ID.perf_idtypecode
        obx.obx_23_10 = '' if "_none" in lab.CLIA_ID.CLIA_ID else lab.CLIA_ID.CLIA_ID
        obx.obx_24_1_1 = lab.CLIA_ID.address1
        obx.obx_24_2 = lab.CLIA_ID.address2
        obx.obx_24_3 = lab.CLIA_ID.city
        obx.obx_24_4 = lab.CLIA_ID.state
        obx.obx_24_5 = lab.CLIA_ID.zip
        obx.obx_24_6 = lab.CLIA_ID.country
        obx.obx_24_7 = lab.CLIA_ID.addr_type
        obx.obx_24_9 = lab.CLIA_ID.county_code
        obx.obx_25_1 = lab.CLIA_ID.NPI_ID
        obx.obx_25_2_1 = lab.CLIA_ID.Lab_Director_lname
        obx.obx_25_3 = lab.CLIA_ID.Lab_Director_fname
        obx.obx_25_4 = lab.CLIA_ID.Lab_Director_mname
        obx.obx_25_5 = lab.CLIA_ID.Lab_Director_suff
        obx.obx_25_6 = lab.CLIA_ID.Lab_Director_pref
        obx.obx_25_9_1 = lab.CLIA_ID.labdir_auth_nid
        obx.obx_25_9_2 = lab.CLIA_ID.labdir_auth_uid
        obx.obx_25_9_3 = lab.CLIA_ID.labdir_auth_uidtype
        obx.obx_25_10 = lab.CLIA_ID.labdir_nametypecode
        obx.obx_25_13 = lab.CLIA_ID.labdir_idtypecode
        obx.obx_25_14_1 = lab.CLIA_ID.labdir_fac_nid
        obx.obx_25_14_2 = lab.CLIA_ID.labdir_fac_uid
        obx.obx_25_14_3 = lab.CLIA_ID.labdir_fac_uidtype
        obx.obx_25_21 = lab.CLIA_ID.labdir_profsuff
        return obx
    
    def MakeNteX(self,lab):
        '''
        NTE is notes and comments and can follow PID, OBR or OBX
        This is the OBX version
        This is an optional record
        '''
        if lab.comment:
            nte = HL7DataObj()
            nte.nte_1 = '1'
            nte.nte_2 = lab.labresult_details_set.get().comment_source
            nte.nte_3 = lab.comment
            nte.nte_4_1 = lab.get_hl7('labresult','comment',lab.labresult_details_set.get().comment_type, 'value')
            nte.nte_4_2 = lab.get_hl7('labresult','comment',lab.labresult_details_set.get().comment_type, 'description')
            nte.nte_4_3 = lab.get_hl7('labresult','comment',lab.labresult_details_set.get().comment_type, 'codesys')
            nte.nte_4_4 = ALTCODEMAPPING['labresult.comment'][lab.labresult_details_set.get().comment_type][0]
            nte.nte_4_5 = ALTCODEMAPPING['labresult.comment'][lab.labresult_details_set.get().comment_type][1]
            nte.nte_4_6 = ALTCODEMAPPING['labresult.comment'][lab.labresult_details_set.get().comment_type][2]
            nte.nte_4_7 = lab.get_hl7('labresult','comment',lab.labresult_details_set.get().comment_type, 'version')
            nte.nte_4_8 = ALTCODEMAPPING['labresult.comment'][lab.labresult_details_set.get().comment_type][3]
        else:
            nte = []
        return nte
    
    def MakeSpm(self,spcmn):
        '''
        SPM is the specimen record
        '''
        spm = HL7DataObj()
        spm.spm_1 = 1
        spm.spm_2_2_1 = spcmn.specimen_num
        spm.spm_2_2_2 = spcmn.fill_nid
        spm.spm_2_2_3 = spcmn.fill_uid
        spm.spm_2_2_4 = spcmn.fill_uidtype
        spm.spm_4_1 = spcmn.get_hl7('specimen','specimen_source',spcmn.specimen_source, 'value')
        spm.spm_4_2 = spcmn.get_hl7('specimen','specimen_source',spcmn.specimen_source, 'description')
        spm.spm_4_3 = spcmn.get_hl7('specimen','specimen_source',spcmn.specimen_source, 'codesys')
        spm.spm_4_4 = ALTCODEMAPPING['specimen.specimen_source'][spcmn.specimen_source][0]
        spm.spm_4_5 = ALTCODEMAPPING['specimen.specimen_source'][spcmn.specimen_source][1]
        spm.spm_4_6 = ALTCODEMAPPING['specimen.specimen_source'][spcmn.specimen_source][2]
        spm.spm_4_7 = spcmn.get_hl7('specimen','specimen_source',spcmn.specimen_source, 'version')
        spm.spm_4_8 = ALTCODEMAPPING['specimen.specimen_source'][spcmn.specimen_source][3]
        spm.spm_5_1 = spcmn.get_hl7('specimen','type_modifier',spcmn.type_modifier, 'value')
        spm.spm_5_2 = spcmn.get_hl7('specimen','type_modifier',spcmn.type_modifier, 'description')
        spm.spm_5_3 = spcmn.get_hl7('specimen','type_modifier',spcmn.type_modifier, 'codesys')
        spm.spm_5_4 = ALTCODEMAPPING['specimen.type_modifier'][spcmn.type_modifier][0]
        spm.spm_5_5 = ALTCODEMAPPING['specimen.type_modifier'][spcmn.type_modifier][1]
        spm.spm_5_6 = ALTCODEMAPPING['specimen.type_modifier'][spcmn.type_modifier][2]
        spm.spm_5_7 = spcmn.get_hl7('specimen','type_modifier',spcmn.type_modifier, 'version')
        spm.spm_5_8 = ALTCODEMAPPING['specimen.type_modifier'][spcmn.type_modifier][3]
        spm.spm_6_1 = spcmn.get_hl7('specimen','additives',spcmn.additives, 'value')
        spm.spm_6_2 = spcmn.get_hl7('specimen','additives',spcmn.additives, 'description')
        spm.spm_6_3 = spcmn.get_hl7('specimen','additives',spcmn.additives, 'codesys')
        spm.spm_6_4 = ALTCODEMAPPING['specimen.additives'][spcmn.additives][0]
        spm.spm_6_5 = ALTCODEMAPPING['specimen.additives'][spcmn.additives][1]
        spm.spm_6_6 = ALTCODEMAPPING['specimen.additives'][spcmn.additives][2]
        spm.spm_6_7 = spcmn.get_hl7('specimen','additives',spcmn.additives, 'version')
        spm.spm_6_8 = ALTCODEMAPPING['specimen.additives'][spcmn.additives][3]
        spm.spm_7_1 = spcmn.get_hl7('specimen','collection_method',spcmn.collection_method, 'value')
        spm.spm_7_2 = spcmn.get_hl7('specimen','collection_method',spcmn.collection_method, 'description')
        spm.spm_7_3 = spcmn.get_hl7('specimen','collection_method',spcmn.collection_method, 'codesys')
        spm.spm_7_4 = ALTCODEMAPPING['specimen.collection_method'][spcmn.collection_method][0]
        spm.spm_7_5 = ALTCODEMAPPING['specimen.collection_method'][spcmn.collection_method][1]
        spm.spm_7_6 = ALTCODEMAPPING['specimen.collection_method'][spcmn.collection_method][2]
        spm.spm_7_7 = spcmn.get_hl7('specimen','collection_method',spcmn.collection_method, 'version')
        spm.spm_7_8 = ALTCODEMAPPING['specimen.collection_method'][spcmn.collection_method][3]
        spm.spm_8_1 = spcmn.get_hl7('specimen','source_site',spcmn.Source_site, 'value')
        spm.spm_8_2 = spcmn.get_hl7('specimen','source_site',spcmn.Source_site, 'description')
        spm.spm_8_3 = spcmn.get_hl7('specimen','source_site',spcmn.Source_site, 'codesys')
        spm.spm_8_4 = ALTCODEMAPPING['specimen.source_site'][spcmn.Source_site][0]
        spm.spm_8_5 = ALTCODEMAPPING['specimen.source_site'][spcmn.Source_site][1]
        spm.spm_8_6 = ALTCODEMAPPING['specimen.source_site'][spcmn.Source_site][2]
        spm.spm_8_7 = spcmn.get_hl7('specimen','source_site',spcmn.Source_site, 'version')
        spm.spm_8_8 = ALTCODEMAPPING['specimen.source_site'][spcmn.Source_site][3]
        spm.spm_9_1 = spcmn.get_hl7('specimen','source_site_modifier',spcmn.Source_site_modifier, 'value')
        spm.spm_9_2 = spcmn.get_hl7('specimen','source_site_modifier',spcmn.Source_site_modifier, 'description')
        spm.spm_9_3 = spcmn.get_hl7('specimen','source_site_modifier',spcmn.Source_site_modifier, 'codesys')
        spm.spm_9_4 = ALTCODEMAPPING['specimen.source_site_modifier'][spcmn.Source_site_modifier][0]
        spm.spm_9_5 = ALTCODEMAPPING['specimen.source_site_modifier'][spcmn.Source_site_modifier][1]
        spm.spm_9_6 = ALTCODEMAPPING['specimen.source_site_modifier'][spcmn.Source_site_modifier][2]
        spm.spm_9_7 = spcmn.get_hl7('specimen','source_site_modifier',spcmn.Source_site_modifier, 'version')
        spm.spm_9_8 = ALTCODEMAPPING['specimen.source_site_modifier'][spcmn.Source_site_modifier][3]
        spm.spm_11_1 = spcmn.get_hl7('specimen','specimen_role',spcmn.Specimen_role, 'value')
        spm.spm_11_2 = spcmn.Specimen_role
        spm.spm_11_3 = spcmn.get_hl7('specimen','specimen_role',spcmn.Specimen_role, 'codesys')
        spm.spm_11_4 = ALTCODEMAPPING['specimen.specimen_role'][spcmn.Specimen_role][0]
        spm.spm_11_5 = ALTCODEMAPPING['specimen.specimen_role'][spcmn.Specimen_role][1]
        spm.spm_11_6 = ALTCODEMAPPING['specimen.specimen_role'][spcmn.Specimen_role][2]
        spm.spm_11_7 = spcmn.get_hl7('specimen','specimen_role',spcmn.Specimen_role, 'version')
        spm.spm_11_8 = ALTCODEMAPPING['specimen.specimen_role'][spcmn.Specimen_role][3]
        spm.spm_12_1 = spcmn.Collection_amount
        spm.spm_12_2_1 = spcmn.get_hl7('specimen','amount_id',spcmn.amount_id, 'value')
        spm.spm_12_2_2 = spcmn.get_hl7('specimen','amount_id',spcmn.amount_id, 'description')
        spm.spm_12_2_3 = spcmn.get_hl7('specimen','amount_id',spcmn.amount_id, 'codesys')
        spm.spm_12_2_4 = ALTCODEMAPPING['specimen.amount_id'][spcmn.amount_id][0]
        spm.spm_12_2_5 = ALTCODEMAPPING['specimen.amount_id'][spcmn.amount_id][1]
        spm.spm_12_2_6 = ALTCODEMAPPING['specimen.amount_id'][spcmn.amount_id][2]
        spm.spm_12_2_7 = spcmn.get_hl7('specimen','amount_id',spcmn.amount_id, 'version')
        spm.spm_12_2_8 = ALTCODEMAPPING['specimen.amount_id'][spcmn.amount_id][3]
        spm.spm_17_1_1 = spcmn.range_startdt
        spm.spm_17_2_1 = spcmn.range_enddt
        spm.spm_18_1 = spcmn.creceived_date
        return spm

    def MakeObxS(self,order,ordLabs):
        '''
        OBX is the observation record.
        This version is for Specimen
        '''
        try:
            spc = order.specimen_set.get()
        except:
            spc = None
        spcobs=None
        obx=None
        try:
            spcobs = spc.specobs_set.get()
        except:
            #not every specmen has an observation attached
            pass
        if spcobs:    
            obx = HL7DataObj()
            obx.obx_1 = '1'
            obx.obx_2 = 'SN'
            obx.obx_3_1 = spcobs.get_hl7('specobs','type',spcobs.type, 'value')
            obx.obx_3_2 = spcobs.get_hl7('specobs','type',spcobs.type, 'description')
            obx.obx_3_3 = spcobs.get_hl7('specobs','type',spcobs.type, 'codesys')
            obx.obx_3_4 = ALTCODEMAPPING['specobs.type'][spcobs.type][0]
            obx.obx_3_5 = ALTCODEMAPPING['specobs.type'][spcobs.type][1]
            obx.obx_3_6 = ALTCODEMAPPING['specobs.type'][spcobs.type][2]
            obx.obx_3_7 = spcobs.get_hl7('specobs','type',spcobs.type, 'version')
            obx.obx_3_8 = ALTCODEMAPPING['specobs.type'][spcobs.type][3]
            obx.obx_5_sn_1 = '='
            obx.obx_5_sn_2 = spcobs.result
            obx.obx_5_sn_3 = ''
            obx.obx_5_sn_4 = ''
            obx.obx_6_1 = spcobs.get_hl7('specobs','unit',spcobs.unit, 'value')
            obx.obx_6_2 = spcobs.unit
            obx.obx_6_3 = spcobs.get_hl7('specobs','unit',spcobs.unit, 'codesys')
            obx.obx_6_4 = ALTCODEMAPPING['specobs.unit'][spcobs.unit][0]
            obx.obx_6_5 = ALTCODEMAPPING['specobs.unit'][spcobs.unit][1]
            obx.obx_6_6 = ALTCODEMAPPING['specobs.unit'][spcobs.unit][2]
            obx.obx_6_7 = spcobs.get_hl7('specobs','unit',spcobs.unit, 'version')
            obx.obx_6_8 = ALTCODEMAPPING['specobs.unit'][spcobs.unit][3]
            obx.obx_6_9 = ''
            obx.obx_7 = ''
            obx.obx_8_1 = ''
            obx.obx_8_2 = ''
            obx.obx_8_3 = ''
            obx.obx_8_4 = ''
            obx.obx_8_5 = ''
            obx.obx_8_6 = ''
            obx.obx_8_7 = ''
            obx.obx_8_8 = ''
            obx.obx_11 = ordLabs[0].status
            obx.obx_14_1 = ordLabs[0].ccollection_date
            obx.obx_17_1 = ''
            obx.obx_17_2 = ''
            obx.obx_17_3 = ''
            obx.obx_17_4 = ''
            obx.obx_17_5 = ''
            obx.obx_17_6 = ''
            obx.obx_17_7 = ''
            obx.obx_17_8 = ''
            obx.obx_19_1 = ordLabs[0].cstatus_date
            obx.obx_23_1 = ordLabs[0].CLIA_ID.laboratory_name
            obx.obx_23_2 = ordLabs[0].CLIA_ID.lab_name_type_code
            obx.obx_23_6_1 = ordLabs[0].CLIA_ID.perf_auth_nid
            obx.obx_23_6_2 = ordLabs[0].CLIA_ID.perf_auth_uid
            obx.obx_23_6_3 = ordLabs[0].CLIA_ID.perf_auth_uidtype
            obx.obx_23_7 = ordLabs[0].CLIA_ID.perf_idtypecode
            obx.obx_23_10 = ordLabs[0].CLIA_ID.CLIA_ID
            obx.obx_24_1_1 = ordLabs[0].CLIA_ID.address1
            obx.obx_24_2 = ordLabs[0].CLIA_ID.address2
            obx.obx_24_3 = ordLabs[0].CLIA_ID.city
            obx.obx_24_4 = ordLabs[0].CLIA_ID.state
            obx.obx_24_5 = ordLabs[0].CLIA_ID.zip
            obx.obx_24_6 = ordLabs[0].CLIA_ID.country
            obx.obx_24_7 = ordLabs[0].CLIA_ID.addr_type
            obx.obx_24_9 = ordLabs[0].CLIA_ID.county_code
            obx.obx_25_1 = ordLabs[0].CLIA_ID.NPI_ID
            obx.obx_25_2_1 = ordLabs[0].CLIA_ID.Lab_Director_lname
            obx.obx_25_3 = ordLabs[0].CLIA_ID.Lab_Director_fname
            obx.obx_25_4 = ordLabs[0].CLIA_ID.Lab_Director_mname
            obx.obx_25_5 = ordLabs[0].CLIA_ID.Lab_Director_suff
            obx.obx_25_6 = ordLabs[0].CLIA_ID.Lab_Director_pref
            obx.obx_25_9_1 = ordLabs[0].CLIA_ID.labdir_auth_nid
            obx.obx_25_9_2 = ordLabs[0].CLIA_ID.labdir_auth_uid
            obx.obx_25_9_3 = ordLabs[0].CLIA_ID.labdir_auth_uidtype
            obx.obx_25_10 = ordLabs[0].CLIA_ID.labdir_nametypecode
            obx.obx_25_13 = ordLabs[0].CLIA_ID.labdir_idtypecode
            obx.obx_25_14_1 = ordLabs[0].CLIA_ID.labdir_fac_nid
            obx.obx_25_14_2 = ordLabs[0].CLIA_ID.labdir_fac_uid
            obx.obx_25_14_3 = ordLabs[0].CLIA_ID.labdir_fac_uidtype
            obx.obx_25_21 = ordLabs[0].CLIA_ID.labdir_profsuff
        return obx
    
    def MakeHL7Data(self,rawcases):
        '''
        This fills the data object that is used by the template
        '''
        #TODO: delete this marker when everything else is done
        cases = []
        for rawcase in rawcases:
            case = HL7DataObj()
            patient = rawcase.patient
            labs = rawcase.lab_results
            case.msh = self.MakeMsh(patient)
            case.sft = self.MakeSft()
            case.pid = self.MakePid(patient) 
            case.pid.nte = self.MakeNteP(patient)
            case.nk1 = self.MakeNk1(patient) #gets guardian from patient
            #here we need to work backwards and find the set of orders associated with the set of reportable labs
            orders = LabOrder.objects.filter(natural_key__in=labs.values_list('order_natural_key')).order_by('order_type')
            try:
                case.pv1 = self.MakePv1(Encounter.objects.get(raw_encounter_type=orders.get(order_type='1').natural_key))
                #for lab encounters, I am using raw_encounter type with the lab order natural key value as the link.  Not 
                # particularly appropriate, but I'm not sure we'll need this after NIST testing
            except:
                pass #only three cases include visit data 
            case.orc = self.MakeOrc(orders.get(order_type='1'))
            case.obr = []
            incr_obr=1
            for order in orders:
                #this builds the OBR sections
                ordLabs = LabResult.objects.filter(order_natural_key=order.natural_key, id__in=labs.values_list('id')).order_by('order_type')
                obr = self.MakeObr(order,ordLabs,incr_obr)
                obr.nte = self.MakeNteR(order)
                obr.obx = []
                incr_obx = 1
                for lab in ordLabs:
                    obx = self.MakeObxL(lab,incr_obx)
                    obx.nte = self.MakeNteX(lab)
                    obr.obx.append(obx)
                    incr_obx += 1
                try:
                    spcmn = order.specimen_set.get()
                except:
                    spcmn = False
                if spcmn:
                    obr.spm = self.MakeSpm(spcmn) 
                    obr.spm.obx = self.MakeObxS(order,ordLabs)
                else:
                    obr.spm = False
                case.obr.append(obr)
                incr_obr += 1
            cases.append(case)
        return cases

class Command(BaseCommand):
    
    help = 'Generate lab reports for Nodis cases'
    
    args = '[conditions]'
    
    option_list = BaseCommand.option_list + (
        make_option('--case', action='store', dest='case_id', type='int', metavar='ID', 
            help='Export a single case with specified case ID'),
        make_option('--status', action='store', dest='status', default='Q',
            help='Export only cases with this status ("Q" by default)'),
        make_option('--batch-size', action='store', type='int', dest='batch_size', metavar='NUM',
            default=1, help='Generate batches of NUM cases per file'),
        make_option('--transmit', action='store_true', dest='transmit', default=False, 
            help='Transmit cases after generation'),
        make_option('--no-mark-sent', action='store_false', dest='mark_sent', default=True,
            help='Do NOT set cases status to "S"'),
        make_option('-o', action='store', metavar='FOLDER', dest='output_folder',
            default=CASE_REPORT_OUTPUT_FOLDER, help='Output case report file(s) to FOLDER'),
        make_option('-f', action='store', dest='format', metavar='FORMAT', default=CASE_REPORT_FILENAME_FORMAT,
            help='Create file names using FORMAT.  Default: %s' % CASE_REPORT_FILENAME_FORMAT),
        make_option('--individual', action='store_false', dest='one_file',
            default=False, help='Export each cases to an individual file (default)'),
        make_option('--sample', action='store', dest='sample', metavar='NUM', type='int', 
            help='Report only first NUM cases matching criteria; do NOT set status to "s"'),
        )
        
    
    def handle(self, *args, **options):
        output_file_paths = [] # Full path to each output file
        report_conditions = [] # Names of conditions for which we will export cases
        #
        # Parse and sanity check command line for options
        #
        all_conditions = DiseaseDefinition.get_all_conditions()
        all_conditions.sort()
        options = Values(options)
        if options.sample: # '--sample' implies '--no-sent-status'
            options.sent_status = False
        for a in args:
            print a
            if a in all_conditions:
                report_conditions.append(a)
            else:
                print >> sys.stderr
                print >> sys.stderr, 'Unrecognized condition: "%s".  Aborting.' % a
                print >> sys.stderr
                print >> sys.stderr, 'Valid conditions are:'
                print >> sys.stderr, '    --------'
                print >> sys.stderr, '    all (reports all conditions below)'
                print >> sys.stderr, '    --------'
                for con in all_conditions:
                    print >> sys.stderr, '    %s' % con
                sys.exit(101)
        if not args:
            report_conditions = all_conditions
        log.debug('conditions: %s' % report_conditions)
        valid_status_choices = [item[0] for item in STATUS_CHOICES]
        if options.status not in valid_status_choices:
                print >> sys.stderr
                print >> sys.stderr, 'Unrecognized status: "%s".  Aborting.' % options.status
                print >> sys.stderr
                print >> sys.stderr, 'Valid status choices are:'
                for stat in valid_status_choices:
                    print >> sys.stderr, '    %s' % stat
                sys.exit(102)
        log.debug('status: %s' % options.status)
        #
        # Set up case report run object
        #
        run = ReportRun(hostname=socket.gethostname())
        run.save()
        #
        # Generate case query
        #
        if options.case_id:
            q_obj = Q(pk__exact=options.case_id)
        else:
            q_obj = Q(condition__in=report_conditions)
            q_obj = q_obj & Q(status=options.status)
        if FAKE_PATIENT_MRN:
            q_obj &= ~Q(patient__mrn__iregex=FAKE_PATIENT_MRN)
        if FAKE_PATIENT_SURNAME:
            q_obj &= ~Q(patient__last_name__iregex=FAKE_PATIENT_SURNAME)
        cases = Case.objects.filter(q_obj).order_by('pk')
        log_query('Filtered cases', cases)
        
        if not cases:
            msg = 'No cases found matching your specifications.  Empty output generated.'
            log.info(msg)
            print >> sys.stderr, ''
            print >> sys.stderr, msg
            print >> sys.stderr, ''
            case_count = 1
            
            batch_cases = []
        else:
            if options.sample: # Report only sample number of cases
                cases = cases[0:options.sample]
                case_count = options.sample
            else:
                case_count =  cases.count()
        #
        # Split cases into batches
        #
        options.batch_size = CASE_REPORT_BATCH_SIZE
        if options.one_file or not options.batch_size:
            options.batch_size = case_count
        batch_serial = 0
        self.timestamp = datetime.datetime.now().strftime('%Y-%b-%d.%H.%M.%s')
        for index in range(0, case_count, options.batch_size):
            filename_values = { 
                # Used to populate file name template -- serial is updated below
                'serial_number': batch_serial,
                'timestamp': self.timestamp,
                }
            if cases:
                batch_cases = cases[index:index+options.batch_size]
            #
            # Generate report message
            #
            report_str = self.use_template(options, batch_serial, batch_cases)
            log.debug('Message to report:\n%s' % report_str)
            #clean up the report_str per HL7 delimiter use specs
            temp = report_str.replace('^|','|')
            temp = temp.replace('&|','|')
            temp = temp.replace('&^','^')
            temp = temp.replace('^~','~')
            temp = temp.replace('None','')
            temp = temp.replace('^\n','\n')
            temp = temp.replace('|\n','\n')
            temp = temp.replace('&\n','\n')
            while report_str != temp:
                report_str = temp
                temp = report_str.replace('^|','|')
                temp = temp.replace('&|','|')
                temp = temp.replace('&^','^')
                temp = temp.replace('^~','~')
                temp = temp.replace('None','')
                temp = temp.replace('^\n','\n')
                temp = temp.replace('|\n','\n')
                temp = temp.replace('&\n','\n')
            #kludge. 
            report_str = report_str.replace('MSH|~','MSH|^~')
            report_str = report_str.replace('\n#EOF#','\n')
            report_obj = Report(
                run = run,
                message = report_str,
                ) 
            #
            # Output
            #
            filename = options.format % filename_values
            report_obj.filename = filename
            filepath = os.path.join(options.output_folder, filename)
            output_file_paths.append(filepath)
            file = open(filepath, 'w')
            file.write(report_str)
            file.close()
            log.info('Wrote case report to file: %s' % filepath)
            #
            # Transmission
            #
            if options.transmit:
                success = self.transmit(options, filepath)
                if success:
                    if options.mark_sent:
                        for case in batch_cases:
                            # redmine 467 checking other status if case events were  
                            # modified after report sent
                            if (case.status == 'RQ'):
                                case.status = 'RS'
                            else:
                                case.status = 'S'
                            case.sent_timestamp = datetime.datetime.now()
                            case.save()
                        log.debug("Set status to 'S' or 'RS' for this batch of cases")
                    report_obj.sent = True
            report_obj.save()
            report_obj.cases = batch_cases # 'Report' instance needs to have a primary key value before a many-to-many relationship can be used.
            report_obj.save()
            batch_serial += 1
        #
        # Print the full path of each output file, for the consumption of any script that may call this command.
        #
        for path in output_file_paths:
            print path
    
    def use_template(self, options, batch_serial, cases):
        '''
        Generate report messages based on a template
        '''
        #
        # Sanity check -- does specified template exist?
        #
        template_name = os.path.join('lab_report', CASE_REPORT_TEMPLATE)
        log.debug('template_name: %s' % template_name)
        try:
            get_template(template_name)
        except TemplateDoesNotExist:
            print >> sys.stderr
            print >> sys.stderr, 'Unrecognized template name: "%s".  Aborting.' % CASE_REPORT_TEMPLATE
            print >> sys.stderr
            sys.exit(103)
        #
        # Build report message 
        #
        hl7 = MakeTemplateData()
        values = {
            'cases': hl7.MakeHL7Data(cases),
            'batch_serial': batch_serial,
            }
        log.debug('values for template: \n%s' % pprint.pformat(values))
        case_report = render_to_string(template_name, values)
        # Remove blank lines -- allows us to have neater templates
        case_report = '\n'.join([x for x in case_report.split("\n") if x.strip()!=''])
        return case_report
    
    def transmit(self, options, report_file):
        '''
        Transmit a batch of cases to its recipient (e.g. dept of public health)
        @param options:          Generated by optparse
        @type options:           Values instance
        @param report_file_path: Full path to file that is to be uploaded
        @type report_file_path:  String
        '''
        if str(CASE_REPORT_TRANSMIT).lower() == 'script':
            return self.transmit_via_script(options, report_file)
        elif str(CASE_REPORT_TRANSMIT).lower() == 'java':
            return self.transmit_java(options, report_file)
        elif str(CASE_REPORT_TRANSMIT).lower() == 'ftp':
            return self.transmit_ftp(options, report_file)
        else:
            raise NotImplementedError('Support for "%s" transmit is not implemented' % CASE_REPORT_TRANSMIT)
    
    def transmit_via_script(self, options, report_file_path):
        '''
        Call a script that will upload the case report file.
        '''
        log.info('Calling script "%s" to upload case report file "%s".' 
            % (CASE_REPORT_TRANSPORT_SCRIPT, report_file_path))
        # It would be nice to use subprocess.check_output() instead here; 
        # however that function requires Python >= 2.7, which we don't
        # want to make a requirement just yet.  - JM 2011 Aug 17
        args = shlex.split(CASE_REPORT_TRANSPORT_SCRIPT) + [report_file_path]
        subprocess.check_call(args)
        log.info('Case report upload script exited with success!')
        return True # Indicats success to calling function
          
    def transmit_ftp(self, options, report_file_path):
        '''
        Upload a file using cleartext FTP.  Why must people insist on doing this??
        '''
        log.info('Transmitting case report via FTP')
        log.warning("Using FTP to transmit patient data is a *horrible* idea.  You've been warned.")
        log.debug('Case report file: %s' % report_file_path)
        log.debug('FTP server: %s' % UPLOAD_SERVER)
        log.debug('FTP user: %s' % UPLOAD_USER)
        log.debug('Attempting to connect...')
        conn = ftplib.FTP(UPLOAD_SERVER, UPLOAD_USER, UPLOAD_PASSWORD)
        log.debug('Connected to %s' % UPLOAD_SERVER)
        log.debug('CWD to %s' % UPLOAD_PATH)
        conn.cwd(UPLOAD_PATH)
        #
        # Code below taken from Anthony McDonald's post at:
        #    http://bytes.com/topic/python/answers/22534-ftplib-question-how-upload-files
        #
        (head, tail) = os.path.split(report_file_path)
        command = "STOR " + tail
        log.debug(command)
        fd = open(report_file_path, 'rb')
        temp = fd.read(2048)
        fd.seek(0, 0)
        try:
            if temp.find('\0') != -1:
                log.debug('storbinary')
                conn.storbinary(command, fd)
            else:
                log.debug('storlines')
                conn.storlines(command, fd)
            log.info('Successfully uploaded %s' % report_file_path)
        except BaseException, e:
            log.error('FTP ERROR: %s' % e)
        fd.close()
        return True
            
        
    def transmit_java(self, options, report_file_path):
        '''
        Transmits file using custom Java component.
        '''
        #
        # Compile Java sender application
        #
        send_msg_command = os.path.join(CODEDIR, 'sendMsgs', 'sendMsg')
        javac = os.path.join(JAVA_DIR, 'javac')
        compile_cmd = "%s -classpath %s %s.java" % (javac, JAVA_CLASSPATH, send_msg_command)
        log.debug(compile_cmd)
        compile_args = shlex.split(compile_cmd)
        p = subprocess.Popen(compile_args)
        retcode = p.wait()
        if retcode: # Error
            msg = 'Compile java Exception: %s' % compile_cmd
            log.error(msg)
            print >> sys.stderr, msg
            sys.exit()
        java_runtime = os.path.join(JAVA_DIR, 'java')
        # Do we really want to tee off to a log file here?
        transmit_cmd = "%s -classpath %s %s %s | tee %s" % (java_runtime, JAVA_CLASSPATH, 'sendMsg', report_file_path, LOG_FILE)
        log.debug(transmit_cmd)
        transmit_args = shlex.split(transmit_cmd)
        p = subprocess.Popen(transmit_args)
        retcode = p.wait()
        if retcode == 0: # Error
            return True
        else:
            msg = 'Error sending message with command:\n    %s' % transmit_cmd
            log.error(msg)
            print >> sys.stderr, msg
            return False
    
