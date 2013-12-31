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
from django.core.exceptions import ObjectDoesNotExist
from ESP.static.models import Vaccine, ImmunizationManufacturer, Icd9
from ESP.vaers.models import Case, Questionnaire, Sender

from ESP.utils.hl7_builder.segments import MSH, EVN, PID, OBX, PV1, TXA
from ESP.utils.hl7_builder.core import SegmentTree
from ESP.utils.utils import log

from ESP.settings import UPLOAD_SERVER
from ESP.settings import UPLOAD_USER
from ESP.settings import UPLOAD_PASSWORD
from ESP.settings import UPLOAD_PATH
from ESP.settings import SITE_NAME
from ESP.settings import VAERS_OVERRIDE_CLINICIAN_REVIEWER
from ESP.emr.models import Provider

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

    def makeTXA(self,messaged):
        #again, the DI and UN values seem to be MetroHealth specific.  These should be plugin specified
        txa = TXA()
        enc = self.case
        ques = self.ques
        txa.report_type = 33
        txa.activity_date=enc.date.strftime("%Y%m%d%H%M%s")
        txa.primary_activity_provider='3480'
        txa.originator_codename='3480'
        txa.distributed_copies=messaged
        txa.unique_document_number='^^ESPMH_' + str(ques.id)
        txa.document_completion_status='AU'
        txa.document_availability_status='AV'
        return txa
    
    def makeOBX(self, rowcode, override):
        #This does all the heavy lifting
        obx = OBX()
        patient = self.case.patient
        if rowcode!='RP':
            AEs = self.case.adverse_events.distinct().order_by('date')
            j=1
            obx.set_id=str(j).zfill(3)
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            if not override:
                salutation='Dear ' + str(self.ques.provider.first_name) + ', '
                if self.ques.provider.title in ['MD','DO']:
                    salutation='Dear Dr. ' + str(self.ques.provider.last_name) + ', '
                obx.value=salutation 
            else:
                obx.value='This message was generated as part of an initial pilot of the VAERS automatic detection system.'
            obxstr=str(obx)+'\r'
            j=j+1
            obx.set_id=str(j).zfill(3)
            obx.value_type='TX'
            obx.identifier='REP^Report Text'
            if self.case.adverse_events.filter(category='1_rare').exists():
                #Rare, severe AE
                caseDescription = ('~ ~Your patient, ' + patient.first_name + ' ' + patient.last_name +  ', may have experienced a serious adverse event following a recent vaccination. ' + 
                        'PLEASE NOTE: DUE TO THE SEVERITY OF THE ADVERSE EVENT, A VAERS REPORT WILL AUTOMATICALLY BE GENERATED AND SUBMITTED TO CDC-VAERS IF YOU DO NOT RESPOND TO THIS MESSAGE. ' +
                        patient.first_name + ' ' + patient.last_name + ', was recently noted to have: ')
            elif self.case.adverse_events.filter(category='3_reportable').exists():
                #Possible AE
                caseDescription = ('~ ~Your patient, ' + patient.first_name + ' ' + patient.last_name +  ', was recently diagnosed with a reportable vaccination adverse reaction.  ' +
                        'PLEASE NOTE: DUE TO THE REPORTABLE NATURE OF THE DIAGNOSIS, A VAERS REPORT WILL AUTOMATICALLY BE GENERATED AND SUBMITTED TO CDC-VAERS IF YOU DO NOT RESPOND TO THIS MESSAGE. ' +
                         patient.first_name + ' ' + patient.last_name + ', was recently noted to have: ')
            elif self.case.adverse_events.filter(category='2_possible').exists():
                #Possible AE
                caseDescription = ('~ ~Your patient, ' + patient.first_name + ' ' + patient.last_name +  ', may have experienced an adverse reaction to a recent vaccination. ' +
                                   'Please note this is a preliminary assessment and must be reviewed, otherwise it will be presumed to be a false positive detection. ' +
                                   patient.first_name + ' ' + patient.last_name + ', was recently noted to have: ')
            obx.value=caseDescription
            obxstr=obxstr+str(obx)+'\r'
            i=1
            for AE in AEs:
                if ContentType.objects.get_for_id(AE.content_type_id).model.startswith('encounter'):
                    icd9codes = AE.matching_rule_explain.split()
                    for icd9code in icd9codes:
                        if Icd9.objects.filter(code=icd9code).exists():
                            obx.value = '~(' + str(i) + ') a diagnosis of ' + Icd9.objects.get(code=icd9code).longname + ' on ' + str(AE.encounterevent.date) 
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
                obx.value = '~(' + str(i) + ') ' + imm.get('name') + ' on ' + str(imm.get('date'))
                j=j+1
                obx.set_id=str(j).zfill(3)
                i=i+1
                obxstr=obxstr+str(obx)+'\r' 
            if self.case.adverse_events.filter(category='3_reportable').exists():
                obx.value =  '~ ~Can you confirm your patient experienced an adverse event (a possible side effect) of a vaccination? '
            else:
                obx.value =  '~ ~Is it possible your patient experienced an adverse event (a possible side effect) of a vaccination? '
            j=j+1
            obx.set_id=str(j).zfill(3)
            obxstr=obxstr+str(obx)+'\r'
            obx.value='If you wish, we can submit an electronic report to the CDC/FDA\'s Vaccine Adverse Event Reporting System (VAERS) on your behalf.'
            j=j+1
            obx.set_id=str(j).zfill(3)
            obxstr=obxstr+str(obx)+'\r'
            obx.value='~ ~Please click the link below to review and comment on this issue.'
            j=j+1
            obx.set_id=str(j).zfill(3)
            obxstr=obxstr+str(obx)+'\r'
            obx.value=u'~ ~This note was automatically generated by the Electronic Support for Public health system (ESP), a joint venture of MetroHealth, the Centers for Disease Control and Prevention, and Harvard Pilgrim Health Care Institute. The project is funded by the Centers for Disease Control and Prevention. If you have clinical questions about an adverse event, please contact the CDC/FDA\'s Vaccine Adverse Event Reporting System helpline at 1-800-822-7967 email: info@vaers.org. If you have questions about this project please contact the MetroHealth Physician Liason, David Kaelber, MD, at dkaelber@metrohealth.org.'
            j=j+1
            obx.set_id=str(j).zfill(3)
            obxstr=obxstr+str(obx)+'\r'
            return obxstr
        elif rowcode=='RP':
        #last obx record is not supposed to have a set_id value for some reason 
            obx.set_id=''
            obx.value_type='RP'
            obx.identifier='Review and comment on this issue at:'
            obx.value='http://' + SITE_NAME + '/vaers/digest/' + self.ques.digest + '^EPIC^LINK^WEBURL^OTHER' 
            return obx

    def make_msgs(self):
        '''
        Assembles an hl7 message file of VAERs case for Clinician's In Basket
        '''
        patient = self.case.patient
        if patient.mrn:    
            senderset=Provider.objects.filter(id__in=Sender.objects.all().values_list('provider_id'))
            senderset_count = senderset.count()
            if VAERS_OVERRIDE_CLINICIAN_REVIEWER=='' and senderset_count==0:
                messaged=self.ques.provider.natural_key
                override=False
            elif VAERS_OVERRIDE_CLINICIAN_REVIEWER!='' and senderset_count==0:
                messaged = VAERS_OVERRIDE_CLINICIAN_REVIEWER
                override=True
            elif VAERS_OVERRIDE_CLINICIAN_REVIEWER!='' and senderset_count>0:
                try:
                    senderset.get(natural_key=self.ques.provider.natural_key)
                    messaged = (VAERS_OVERRIDE_CLINICIAN_REVIEWER + '~' + 
                            self.ques.provider.natural_key + '^' + self.ques.provider.first_name + ' ' + self.ques.provider.last_name)
                    override=False
                except ObjectDoesNotExist:
                    messaged = VAERS_OVERRIDE_CLINICIAN_REVIEWER
                    override=True
            all_text = (str(self.makeMSH()) + '\r' +
                    str(self.makeEVN()) + '\r' + 
                    str(self.makePID()) + '\r' + 
                    str(self.makePV1()) + '\r' + 
                    str(self.makeTXA(messaged)) + '\r' + 
                    self.makeOBX('main',override) +
                    str(self.makeOBX('RP',override)) + '\r' + '\n' )
            #the cStringIO.StringIO object is built in memory, not saved to disk.
            hl7file = cStringIO.StringIO()
            hl7file.write(all_text)
            hl7file.seek(0)
            if transmit_ftp(hl7file, 'clinbox_msg_ID' + '_' + str(self.ques.id) + '.txt'):
                Questionnaire.objects.filter(id=self.ques.id).update(inbox_message=hl7file.getvalue())
            hl7file.close()
        else:
            msg='Patient has no MRN.  ID: ' + str(patient.id)
            log.warning(msg)

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
            conn.storbinary(command, fileObj)
            log.info('Successfully uploaded Clin Inbasket HL7 message')
        except BaseException, e:
            log.error('FTP ERROR: %s' % e)
            return False
        return True
