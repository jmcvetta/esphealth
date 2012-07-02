'''
                                  ESP Health
                         Notifiable Diseases Framework
                         Clinician Inbasket HL7 Message

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc. http://www.commoninf.com
@copyright: (c) 2012 Commonwealth Informatics Inc.
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


from django.contrib.contenttypes.models import ContentType
from ESP.static.models import Vaccine, ImmunizationManufacturer, Icd9
from ESP.vaers.models import Case, Questionnaire

from ESP.utils.hl7_builder.segments import MSH, EVN, PID, OBX, PV1, TXA
from ESP.utils.utils import log

from ESP.settings import UPLOAD_SERVER
from ESP.settings import UPLOAD_USER
from ESP.settings import UPLOAD_PASSWORD
from ESP.settings import UPLOAD_PATH
from ESP.settings import SITE_NAME
from ESP.settings import VAERS_OVERRIDE_CLINICIAN_REVIEWER

import ftplib
import cStringIO
import datetime



UNKNOWN_VACCINE = Vaccine.objects.get(short_name='unknown')
UNKNOWN_MANUFACTURER = ImmunizationManufacturer.objects.get(code='UNK')
now = datetime.datetime.now()

class HL7_clinbasket(object):
    '''
    Format and generate the HL7 message for delivery to the Clinician Inbasket.
    Content is per ESP-VAERS algorithm specification.
    '''
    #initialize with a questionnaire record
    def __init__(self, questionnaire):
        self.ques = questionnaire
        self.case = Case.objects.get(id=self.ques.case_id)
        self.immunizations = self.case.immunizations.all()
        
    def makeMSH(self):
        msh = MSH()
        # the following values for MetroHealth systems
        #todo: these values should be provided via a plugin for metrohealth
        msh.sending_application ='SICIR'
        msh.sending_facility = 'SICIR'
        msh.receiving_application = 'EPIC'
        msh.receiving_facility = 'EPICCARE'
        msh.time = now.strftime("%Y%m%d%H%M%s")
        msh.message_type = 'MDM^T02'
        msh.message_control_id='ESP'+str(self.ques.id).zfill(7)
        msh.processing_id = 'P'
        return msh

    def makeEVN(self):
        #minimal values required for clinicians inbasket
        evn = EVN()
        # probably  need more here
        evn.event_type_code = 'T02'
        evn.recorded_datetime = self.case.date.strftime("%Y%m%d%H%M%s")
        
        return evn
        
    def makePID(self):
        patient = self.case.patient
        pid = PID()
        words =patient.natural_key.split()
        #TODO: this should be a metrohealth plugin, as it is specific to metrohealth natural key values
        if words[0].isdigit():
            pid.patient_external_id = words[0] + '^^^^ID 1'
        else:
            pid.patient_external_id = patient.natural_key
        #We currently don't need the following but could provide at some point if desired.
        #pid.patient_name = patient._get_name
        #pid.date_of_birth = utils.str_from_date(patient.date_of_birth)
        #pid.sex = patient.gender
        #pid.race = patient.race
        #pid.patient_address = patient._get_address
        #pid.home_phone = u'(%s) %s' % (patient.areacode, patient.phone_number)
        #pid.primary_language = patient.home_language
        #pid.marital_status = patient.marital_stat
        #pid.country_code = patient.country
        return pid

    def makePV1(self):
        pv1 = PV1()
        #we don't currently do anything with this record.
        return pv1

    def makeTXA(self):
        #again, the DI and UN values seem to be MetroHealth specific.  These should be plugin specified
        txa = TXA()
        enc = self.case
        ques = self.ques
        txa.report_type = 33
        txa.activity_date=enc.date.strftime("%Y%m%d%H%M%s")
        if VAERS_OVERRIDE_CLINICIAN_REVIEWER=='':
            txa.primary_activity_provider=ques.provider_id
            txa.originator_codename=ques.provider_id
        else:
            txa.primary_activity_provider=VAERS_OVERRIDE_CLINICIAN_REVIEWER
            txa.originator_codename=VAERS_OVERRIDE_CLINICIAN_REVIEWER
        txa.unique_document_number='^^ESPMH_' + str(ques.id)
        txa.document_completion_status='DI'
        txa.document_availability_status='UN'
        return txa
    
    def makeOBX(self, rowcode):
        #This does all the heavy lifting
        obx = OBX()
        patient = self.case.patient
        AEs = self.case.adverse_events.distinct().order_by('date')
        if rowcode=='RP':
            obx.value_type=rowcode
            obx.identifier='Review and comment on this issue at:'
            obx.value='http://' + SITE_NAME + '/vaers/digest/' + self.ques.digest + '^EPIC^LINK^WEBURL^OTHER' 
            return obx
        elif rowcode=='001':
            obx.set_id=rowcode
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            obx.value='Dear Dr. ' + str(self.ques.provider.first_name) + ' ' + str(self.ques.provider.last_name) + ', '
            return obx
        elif rowcode=='002':
            obx.set_id=rowcode
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            if self.case.adverse_events.filter(category='2_rare').exists():
                #Rare, severe AE
                caseDescription = '~ ~Your patient, ' + patient.name + ', may have experienced a serious adverse event following a recent vaccination. ' + patient.name + ', was recently noted to have '
            elif self.case.adverse_events.filter(category='3_possible').exists():
                #Possible AE
                caseDescription = '~ ~Your patient, ' + patient.name + ', was recently noted to have '
            evntlist=[]
            for AE in AEs:
                if ContentType.objects.get_for_id(AE.content_type_id).model.startswith('encounter'):
                    icd9codes = AE.matching_rule_explain.split()
                    for icd9code in icd9codes:
                        if Icd9.objects.filter(code=icd9code).exists():
                            evntlist.append(Icd9.objects.get(code=icd9code).name)
                            caseDescription += Icd9.objects.get(code=icd9code).name + ', '
                    caseDescription = caseDescription[0:-2] + ' on ' + str(AE.encounterevent.date) + ', '  
                elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('prescription'):
                    caseDescription = caseDescription + AE.prescriptionevent.content_object.name + ' on ' + str(AE.prescriptionevent.content_object.date) + ', '
                    evntlist.append(AE.prescriptionevent.content_object.name)
                elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('labresult'):
                    caseDescription = caseDescription + AE.labresultevent.content_object.native_name + ' on ' + str(AE.labresultevent.content_object.result_date) + ', '
                    evntlist.append(AE.labresultevent.content_object.native_name)
                elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('allergy'):
                    #adding the term 'allergy' to the name, as it is otherwise confusing with the test data.
                    #this may not be the case with real allergen names and if so the code will need to be revised.
                    caseDescription = caseDescription + AE.allergyevent.content_object.name + ' allergy on ' + str(AE.allergyevent.content_object.date) + ', '
                    evntlist.append(AE.allergyevent.content_object.name + ' allergy')
            caseDescription = caseDescription[0:-2] + '. ' + patient.name + ' was vaccinated with '
            for imm in self.case.immunizations.all():
                caseDescription = caseDescription + imm.name + ', '
            caseDescription  = caseDescription[0:-2] + ' on ' + str(imm.date) + '. Do you think that it is possible that '
            for evnt in evntlist:
                caseDescription = caseDescription + evnt + ' or '
            caseDescription = caseDescription[0:-4] + ' was due to an adverse effect (a possible side effect) of a vaccine? '
            obx.value=caseDescription 
            return obx
        elif rowcode=='003':   
            obx.set_id=rowcode
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            obx.value='~ ~If so, we can automatically submit an electronic report to the CDC/FDAs Vaccine Adverse Event Reporting System (VAERS) on your behalf.'
            return obx
        elif rowcode=='004':   
            obx.set_id=rowcode
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            obx.value='~ ~Please click the link below to review and comment on this issue.'
            return obx
        elif rowcode=='005':   
            obx.set_id=rowcode
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            obx.value=u'~ ~This note was automatically generated by the Electronic Support for Public health system (ESP), a joint venture of MetroHealth, the Centers for Disease Control and Prevention, and Harvard Pilgrim Health Care Institute. The project is funded by the Centers for Disease Control and Prevention. If you have clinical questions about an adverse event, please contact the CDC/FDA\'s Vaccine Adverse Event Reporting System helpline at 1-800-822-7967 email: info@vaers.org. If you have questions about this project please contact the MetroHealth Physician Liason, David Kaelber, MD, at dkaelber@metrohealth.org.'
            return obx

    def make_msgs(self):
        '''
        Assembles an hl7 message file of VAERs case for Clinician's In Basket
        '''
        all_segs = [self.makeMSH(), 
                    self.makeEVN(), 
                    self.makePID(), 
                    self.makePV1(), 
                    self.makeTXA(), 
                    self.makeOBX('001'),
                    self.makeOBX('002'),
                    self.makeOBX('003'),
                    self.makeOBX('004'),
                    self.makeOBX('005'),
                    self.makeOBX('RP')]
        all_text = '\n'.join([str(x) for x in all_segs])
        #the cStringIO.StringIO object is built in memory, not saved to disk.
        hl7file = cStringIO.StringIO()
        hl7file.write(all_text)
        hl7file.seek(0)
        if transmit_ftp(hl7file, 'clinbox_msg_ID' + str(self.ques.id)):
            Questionnaire.objects.filter(id=self.ques.id).update(inbox_message=hl7file.getvalue())
        hl7file.close()


def transmit_ftp(fileObj, filename):
        '''
        Upload a file using cleartext FTP.  Adapted from ESP.nodis.management.commands.case_report.py
        '''
        log.info('Transmitting case report via FTP')
        log.debug('FTP server: %s' % UPLOAD_SERVER)
        log.debug('FTP user: %s' % UPLOAD_USER)
        log.debug('Attempting to connect...')
        conn = ftplib.FTP(UPLOAD_SERVER, UPLOAD_USER, UPLOAD_PASSWORD)
        log.debug('Connected to %s' % UPLOAD_SERVER)
        log.debug('CWD to %s' % UPLOAD_PATH)
        conn.cwd(UPLOAD_PATH)
        command = 'STOR ' + filename
        try:
            conn.storlines(command, fileObj)
            log.info('Successfully uploaded Clin Inbasket HL7 message')
        except BaseException, e:
            log.error('FTP ERROR: %s' % e)
            return False
        return True
