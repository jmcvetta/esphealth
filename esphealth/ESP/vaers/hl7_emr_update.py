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
from ESP.static.models import Vaccine, ImmunizationManufacturer, Dx_code
from ESP.vaers.models import Case, Report_Sent, Questionnaire
from ESP.emr.models import Provider

from ESP.utils.hl7_builder.segments import MSH, EVN, PID, OBX, PV1, TXA
from ESP.utils.utils import log

from ESP.settings import EMRUPDATE_SERVER
from ESP.settings import EMRUPDATE_USER
from ESP.settings import EMRUPDATE_PASSWORD
from ESP.settings import EMRUPDATE_PATH, PHINMS_PATH
from ESP.settings import VAERS_AUTOSENDER

import ftplib
import cStringIO
import datetime

UNKNOWN_VACCINE = Vaccine.objects.get(short_name='unknown')
UNKNOWN_MANUFACTURER = ImmunizationManufacturer.objects.get(code='UNK')
now = datetime.datetime.now()

class HL7_emr_update(object):
    '''
    Format and generate the HL7 message for updating the EPIC EMR.
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
        words =patient.mrn.split('-')
        #TODO: this should be a metrohealth plugin, as it is specific to metrohealth values
        if words[1]:
            pid.patient_internal_id = words[1] + '^^^^ID 1'
        else:
            pid.patient_internal_id = patient.mrn+ '^^^^ID 1'
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
        txa.primary_activity_provider='3480'
        txa.originator_codename='3480'
        if ques.state=='AR':
            txa.distributed_copies=VAERS_AUTOSENDER
        else:
            txa.distributed_copies=ques.provider.natural_key
        txa.unique_document_number='^^ESPMH_' + str(ques.id)
        txa.document_completion_status='AU'
        txa.document_availability_status='AV'
        return txa
    
    def makeOBX(self, rowcode):
        #This does all the heavy lifting
        obx = OBX()
        patient = self.case.patient
        if self.ques.state=='FP':
            obx.set_id='001'
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            obx.value='A potential vaccine adverse event was detected but was determined to be false upon review. ' 
            if self.ques.comment:
                obx.value=obx.value + 'Reviewer comment was: ' + self.ques.comment
            else:
                obx.value=obx.value + 'No comment provided.'
            obxstr=str(obx)+'\r'
        else:
            if self.ques.state=='AR':
                autoprovider=Provider.objects.get(natural_key=VAERS_AUTOSENDER)
                provider_name = str(autoprovider.first_name) + ' ' + str(autoprovider.last_name)
            else:
                provider_name = str(self.ques.provider.first_name) + ' ' + str(self.ques.provider.last_name)
            AEs = self.case.adverse_events.distinct().order_by('date')
            j=1
            obx.set_id=str(j).zfill(3)
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            obx.value=('A potential vaccine adverse event was reported to CDC-VAERS on ' + str(now) + ' by '  +
                       provider_name + 
                       ' via the Electronic medical record Support for Public Health systems (ESP).  Details in this report include: ')
            obxstr=str(obx)+'\r'
            obx.value='~ ~Patient ' + patient.first_name + ' ' + patient.last_name +  ', was recently noted to have: '
            i=1
            for AE in AEs:
                if ContentType.objects.get_for_id(AE.content_type_id).model.startswith('encounter'):
                    #TODO icd10 check the dx_code filter by combotype or code and type
                    dx_codes = AE.matching_rule_explain.split()
                    for dx_code in dx_codes:
                        if Dx_code.objects.filter(code=dx_code, type='ICD9').exists():
                            obx.value = '~(' + str(i) + ') a diagnosis of ' + Dx_code.objects.get(code=dx_code, type='ICD9').longname + ' on ' + str(AE.encounterevent.date) 
                            j=j+1
                            obx.set_id=str(j).zfill(3)
                            i=i+1 
                            obxstr=obxstr+str(obx)+'\r'
                elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('prescription'):
                    obx.value = '~(' + str(i) + ') a prescription for ' + AE.prescriptionevent.content_object.name + ' on ' + str(AE.prescriptionevent.content_object.date) 
                    j=j+1
                    obx.set_id=str(j).zfill(3)
                    i=i+1
                    obxstr=obxstr+str(obx)+'\r'
                elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('labresult'):
                    obx.value = ('~(' + str(i) + ') a lab test for ' + AE.labresultevent.content_object.native_name 
                            + ' with a result of ' + AE.labresultevent.content_object.result_string + ' on ' + str(AE.labresultevent.content_object.result_date) )
                    j=j+1
                    obx.set_id=str(j).zfill(3)
                    i=i+1
                    obxstr=obxstr+str(obx)+'\r'
                elif ContentType.objects.get_for_id(AE.content_type_id).model.startswith('allergy'):
                        #adding the term 'allergy' to the name, as it is otherwise confusing with the test data.
                        #this may not be the case with real allergen names and if so the code will need to be revised.
                    obx.value = '~(' + str(i) + ') an allergic reaction to ' + AE.allergyevent.content_object.name + ' on ' + str(AE.allergyevent.content_object.date) 
                    j=j+1
                    obx.set_id=str(j).zfill(3)
                    i=i+1
                    obxstr=obxstr+str(obx)+'\r'
            obx.value = '~ ~' + patient.first_name + ' ' + patient.last_name + ' was vaccinated with: '
            j=j+1
            obx.set_id=str(j).zfill(3)
            obxstr=obxstr+str(obx)+'\r'
            i=1
            for imm in self.case.immunizations.values('name','date').distinct():
                obx.value = '(' + str(i) + ') ' + imm.get('name') + ' on ' + str(imm.get('date'))
                j=j+1
                obx.set_id=str(j).zfill(3)
                i=i+1
                obxstr=obxstr+str(obx)+'\r'
            if self.case.prior_immunizations.all().exists():
                obx.value = '~ ~' + patient.first_name + ' ' + patient.last_name + ' was previously vaccinated with: '
                j=j+1
                obx.set_id=str(j).zfill(3)
                obxstr=obxstr+str(obx)+'\r'
                i=1
                for p_imm in self.case.prior_immunizations.all():
                    obx.value = '(' + str(i) + ') ' + p_imm.get('name') + ' on ' + str(p_imm.get('date'))
                    j=j+1
                    obx.set_id=str(j).zfill(3)
                    i=i+1
                    obxstr=obxstr+str(obx)+'\r'
            if Case.objects.filter(patient=self.case.patient, date__lt=self.case.date).exists():        
                pcases = Case.objects.filter(patient=self.case.patient, date__lt=self.case.date, report_sent__id__isnull=False)
                for pcase in pcases:
                    obx.value = '~ ~' + patient.first_name + ' ' + patient.last_name + ' had a previously reported Vaccine AE case reported: '
                    j=j+1
                    obx.set_id=str(j).zfill(3)
                    obxstr=obxstr+str(obx)+'\r'
                    i=1
                    AEs = pcase.adverse_events.distinct().order_by('date')
                    for AE in AEs:
                        obx.value = '(' + str(i) + ') ' + p_imm.get('name') + ' on ' + str(p_imm.get('date'))
                        j=j+1
                        obx.set_id=str(j).zfill(3)
                        i=i+1
                        obxstr=obxstr+str(obx)+'\r'
            j=j+1
            obx.set_id=str(j).zfill(3)
            if self.ques.comment :
                obx.value =  '~ ~ ' + str(self.ques.provider.first_name) + ' ' + str(self.ques.provider.last_name) + ' commented: ' +self.ques.comment
            else:
                obx.value =  '~ ~No comment was provided '
            obxstr=obxstr+str(obx)+'\r'
            if self.ques.state=='AR' and self.case.adverse_events.filter(category='1_rare').exists():
                j=j+1
                obx.set_id=str(j).zfill(3)
                obx.value_type='TX'
                obx.identifier='REP^Report Text'
                obx.value='~ ~Due to the severity of the events, this message was automatically sent seven days after initial detection.  These details were not reviewed.'
                obxstr=obxstr+str(obx)+'\r'
            elif self.ques.state=='AR' and self.case.adverse_events.filter(category='3_reportable').exists():
                j=j+1
                obx.set_id=str(j).zfill(3)
                obx.value_type='TX'
                obx.identifier='REP^Report Text'
                obx.value='~ ~Due to a vaccine-specific diagnosis, this message was automatically sent seven days after initial detection.  These details were not reviewed.'
                obxstr=obxstr+str(obx)+'\r'
        return obxstr

    def render(self):
        '''
        Assembles an hl7 message file of VAERs case for EMR Update
        '''
        all_text = (str(self.makeMSH()) + '\r' +
                    str(self.makeEVN()) + '\r' + 
                    str(self.makePID()) + '\r' + 
                    str(self.makePV1()) + '\r' + 
                    str(self.makeTXA()) + '\r' + 
                    self.makeOBX('main') + '\n' )
            #the cStringIO.StringIO object is built in memory, not saved to disk.  Don't build anything too big.
        hl7file = cStringIO.StringIO()
        hl7file.write(all_text)
        hl7file.seek(0)
        if self.transmit_ftp(hl7file, 'clinbox_msg_ID2_' + str(self.ques.id) + '.txt'):
            log.info('Successfully uploaded EMR Update HL7 message')
            Report_Sent.objects.create(questionnaire_id=self.ques.id,
                                       case_id=self.case.id,
                                       date=now,
                                       report=hl7file.getvalue(),
                                       report_type='EMR update')            
        hl7file.close()
        if Questionnaire.objects.filter(id=self.ques.id, state='FP'):
            Questionnaire.objects.filter(id=self.ques.id).update(state='FU')
            


    def transmit_ftp(self, fileObj, filename):
        '''
        Upload a file using cleartext FTP.  Adapted from ESP.nodis.management.commands.case_report.py
        '''
        if self.ques.state in ['AS','AR']:
            filepath=PHINMS_PATH
        else:
            filepath=EMRUPDATE_PATH
        log.info('Transmitting case report via FTP')
        log.debug('FTP server: %s' % EMRUPDATE_SERVER)
        log.debug('FTP user: %s' % EMRUPDATE_USER)
        log.debug('Attempting to connect...')
        conn = ftplib.FTP(EMRUPDATE_SERVER, EMRUPDATE_USER, EMRUPDATE_PASSWORD)
        log.debug('Connected to %s' % EMRUPDATE_SERVER)
        log.debug('CWD to %s' % filepath)
        conn.cwd(filepath)
        command = 'STOR ' + filename
        try:
            conn.storbinary(command, fileObj)
        except BaseException, e:
            log.error('FTP ERROR: %s' % e)
            return False
        return True
