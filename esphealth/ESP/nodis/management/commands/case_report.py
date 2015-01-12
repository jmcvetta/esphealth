'''
                                  ESP Health
                         Notifiable Diseases Framework
                                 Case Reporter

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt

--------------------------------------------------------------------------------
EXIT CODES

10     Keyboard interrupt
11     No cases found matching query
101    Unrecognized condition
102    Unrecognized case status
103    Unrecognized template name
104    Invalid combination of command line options
999    Functionality not yet implemented
'''


from ESP.settings import CASE_REPORT_OUTPUT_FOLDER
from ESP.settings import CASE_REPORT_TEMPLATE
from ESP.settings import CASE_REPORT_FILENAME_FORMAT
from ESP.settings import CASE_REPORT_BATCH_SIZE
from ESP.settings import CASE_REPORT_TRANSMIT
from ESP.settings import CASE_REPORT_TRANSPORT_SCRIPT
from ESP.settings import CASE_REPORT_SPECIMEN_SOURCE_SNOMED_MAP
from ESP.settings import FAKE_PATIENT_MRN
from ESP.settings import FAKE_PATIENT_SURNAME
from ESP.settings import CODEDIR
from ESP.settings import JAVA_DIR
from ESP.settings import JAVA_CLASSPATH
from ESP.settings import JAVA_JARS
from ESP.settings import LOG_FILE
from ESP.settings import UPLOAD_SERVER
from ESP.settings import UPLOAD_USER
from ESP.settings import UPLOAD_PASSWORD
from ESP.settings import UPLOAD_PATH

import optparse
import sys
import pprint
import os
import cStringIO as StringIO
import time
import datetime
import re
import socket
import subprocess
import shlex
import ftplib
import math


from optparse import Values
from optparse import make_option
from xml.dom.minidom import Document

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template.loader import get_template
from django.core.management.base import BaseCommand

from ESP.conf.models import LabTestMap
from ESP.emr.models import Provider
from ESP.emr.models import LabResult, Order_Extension
from ESP.emr.models import Encounter
from ESP.conf.models import ResultString
from ESP.conf.models import ConditionConfig

from ESP.hef.base import BaseLabResultHeuristic, TITER_DILUTION_CHOICES

from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.models import Case
from ESP.nodis.models import ReportRun
from ESP.nodis.models import Report
from ESP.nodis.models import STATUS_CHOICES

from ESP.utils.utils import log
from ESP.utils.utils import log_query

from ESP.settings import CASE_REPORT_SITE_NAME , SITE_CLIA ,SITE_LAST_NAME ,SITE_FIRST_NAME ,SITE_ADDRESS1 ,SITE_ADDRESS2 
from ESP.settings import  SITE_CITY ,SITE_STATE ,SITE_ZIP ,SITE_COUNTRY ,SITE_EMAIL ,SITE_AREA_CODE ,SITE_TEL_NUMERIC 
from ESP.settings import SITE_TEL_EXT ,SITE_APP_NAME ,SITE_SENDING_FACILITY ,SITE_COMMENTS  , SITE_HEADER

#===============================================================================
#
#--- Configuration
#
#===============================================================================

VERSION = '2.3.1'
DATE_FORMAT = '%Y%m%d'

# Information about reporting institution.  This info should be made configurable 
# in settings.py.

class Foo(): pass
INSTITUTION = Foo()
INSTITUTION.name = CASE_REPORT_SITE_NAME
INSTITUTION.clia = SITE_CLIA
INSTITUTION.last_name = SITE_LAST_NAME
INSTITUTION.first_name = SITE_FIRST_NAME
INSTITUTION.address1 = SITE_ADDRESS1
INSTITUTION.address2 = SITE_ADDRESS2
INSTITUTION.city = SITE_CITY
INSTITUTION.state = SITE_STATE
INSTITUTION.zip = SITE_ZIP
INSTITUTION.country = SITE_COUNTRY
INSTITUTION.email = SITE_EMAIL
INSTITUTION.area_code = SITE_AREA_CODE
INSTITUTION.tel_numeric = SITE_TEL_NUMERIC
INSTITUTION.tel_ext = SITE_TEL_EXT

APP_NAME = SITE_APP_NAME
SENDING_FACILITY = SITE_SENDING_FACILITY
COMMENTS = SITE_COMMENTS # What goes in comments?



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

class NoConditionConfigurationException(BaseException):
    '''
    raised when no conf.config defined for a disease, needed for reportable items (encounters, icd9s, prescriptions and labs)
    '''
    pass


def isoTime(t=None):
    """ yyyymmddhhmmss - as at now unless a localtime is passed in
    """
    if t == None:
        return time.strftime('%Y%m%d%H%M%S',time.localtime())
    else:
        return time.strftime('%Y%m%d%H%M%S',t)

class hl7Batch:
    """ class for building an hl7 message
    eeesh this is horrible. hl7 sucks.
    two dom objects - one for cases and one for the batch
    the cases are added by calling addCase, then rendered and inserted into
    the batch by the renderBatch method
    """
    
    def __init__(self, doc=None, institutionName=CASE_REPORT_SITE_NAME, nmessages = None):
        """ doc must be a dom document
        set up the batch structures
        order of creation is not important
        order in which things are added is crucial
        leave self.main as the place to hang all the cases
        expect contents dict to have fields like institution_name, clia etc
        this gets used as the default if any methods called without a specific
        mapping dictionary.
        Ah there's a complication. They really want all the cases in a cdata section
        so we're going to have to create a separate document with all the cases and render it as
        a text string to enclose in a cdata section...
        """
        self.racedir = {'CAUCASIAN':'W',
           'WHITE':'W',
           'BLACK':'B',
           'OTHER':'O',
           'HISPANIC': 'W',
           'INDIAN':'I',
           'AMERICAN INDIAN/ALASKAN NATIVE':'I',
           'ASIAN':'A',
           'NAT AMERICAN':'I',
           'NATIVE HAWAI':'P',
           'PACIFIC ISLANDER/HAWAIIAN':'P',
           'ALASKAN':'I',
           }
        self.nmessages = nmessages
        self.timestamp = isoTime() # will return time now
        self.batchDoc = Document() # create a dom root 
        self.casesDoc = Document() # create a dom root for all the cases
        self.casesTopLevel = self.casesDoc.createElement("rossfoo") # this is a placeholder which is removed at rendering
        self.casesDoc.appendChild(self.casesTopLevel)
        self.currentCase = None
    
    def renderBatch(self):
        """ To render the entire document, batchdoc needs to be rendered, with a cdata section containing
        a rendered version of the casesdoc. Please, don't ask me why.
        """
        c = self.casesDoc.toprettyxml(indent = "  ") # render all the cases as a string
        cstring = '\n'.join(c.split('\n')[2:-2]) # get rid of header and rossfoo lines
        batch = self.batchDoc.createElement("BATCH") # top level element
        batch.setAttribute("xmlns","urn:hl7-org:v2xml")
        self.batchDoc.appendChild(batch) # this is the top level now
        fhs = self.makeFHS()
        batch.appendChild(fhs) # now a subsection        
        mbatch = self.batchDoc.createElement("MESSAGEBATCH")
        batch.appendChild(mbatch)        
        bh = self.makeBHS()
        mbatch.appendChild(bh)
        messages = self.batchDoc.createElement("MESSAGES") # this is where calls to message segments will add stuff
        # note that the entire sequence of ORU cases must be enclosed in a
        # <![CDATA[...]]> tag so they are rendered and cleaned of cruft above.
        cdata = self.batchDoc.createCDATASection(cstring) # this single string substitution is replaced with all messages
        messages.appendChild(cdata) 
        mbatch.appendChild(messages) # now add all the footers
        if self.nmessages <> None:
            bt = self.batchDoc.createElement("BTS")
            self.addHSimple(bt,'%d' % self.nmessages,'BTS.1')
            mbatch.appendChild(bt)
        ft = self.batchDoc.createElement("FTS")
        self.addHSimple(ft,'1','FTS.1')
        batch.appendChild(ft)
        s = self.batchDoc.toprettyxml(indent="  ")
        return s

    
    ####################################
    def addCase(self, case, elr):
        """Workhorse - maps cases into an xml document containing hl7
        should pass a mapping dict for each case here
        the obx records are all the case details so
        we need to iterate over the pointers stored in each case to make the
        appropriate segments
        """
        
        self.currentCase=case.id
        patient = case.patient
        oru = self.casesDoc.createElement('ORU_R01')
        self.casesTopLevel.appendChild(oru)
        mhs = self.makeMSH(elr, case.patient.center_id, segcontents=None, processingFlag='T') 
        oru.appendChild(mhs)
        orus = self.casesDoc.createElement('ORU_R01.PIDPD1NK1NTEPV1PV2ORCOBRNTEOBXNTECTI_SUPPGRP')
        oru.appendChild(orus)
        orus2 = self.casesDoc.createElement('ORU_R01.PIDPD1NK1NTEPV1PV2_SUPPGRP')
        orus.appendChild(orus2)
        ##demograpgic
        pid = self.makePID(demog=patient, pcp=case.provider)
        orus2.appendChild(pid)
        ##PCP       
        p = self.makePCP(pcp=case.provider, addressType='O')
        orus2.appendChild(p)
        ##facility information 
        p = self.makeFacility()
        orus2.appendChild(p)
        ##Treating Clinician
        if not case.condition_config:
            raise NoConditionConfigurationException('Condition %s has no Reportable Configuration. Please configure it under Administration/Site Administration/Conf - Condition Configurations' % case.condition)
        
        rxobjs = case.reportable_prescriptions.order_by('natural_key')
        treatclis = set( rxobjs.values_list('provider', flat=True) )
        for cli in treatclis:
            nkindx=3
            pcp = Provider.objects.get(pk=cli)
            p = self.makePCP(pcp=pcp, addressType='O',NKindx=nkindx,NK13='TC')
            nkindx=nkindx+1
            orus2.appendChild(p)
        ##Clinical information
        orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
        orus.appendChild(orcs)
        rep_dx_codes = case.reportable_dx_codes
        rep_encounters = case.reportable_encounters[0]
        
        #adds repotable dx codes obr 
        self.addCaseOBR(condition=case.condition, dx_code=rep_dx_codes, orcs=orcs, gender=case.patient.gender)
        if rxobjs:
            rx=rxobjs[0]
        else:
            rx = None
        lxobjs = case.reportable_labs.order_by('order_natural_key')
        
        if len(lxobjs):
            lx =lxobjs[0]
        else:
            lx = None
        #adds dx codes and encounters obx 
        self.addCaseOBX(demog=patient, orcs=orcs, dx_code=rep_dx_codes, lx=lx, rx=rx,
            encounters=rep_encounters, condition=case.condition, casenote=case.notes,
            caseid=case.pk)  
                      
        totallxs = list(lxobjs)
       
        # only removing duplicates if they are real labs except the tb dummy lab  
        if totallxs and totallxs[0].pk != 0:
            cleanlxids = self.removeDuplicateLx(totallxs)
            totallxs = LabResult.objects.filter(pk__in=cleanlxids).order_by('order_natural_key')
        self.addLXOBX(case=case,lxRecList=totallxs, orus=orus)
        #add reinfection objects 
        self.genReinfection(case=case, orus=orus)
        
        self.addRXOBX(rxRecList=rxobjs, orus=orus) # do same for dr
        # generate extended variables for all conditions , same orus
        self.addEXVOBX(exvRecList=case.reportable_extended_variables, orus=orus) 
        
        return [i.id for i in totallxs]

    def removeDuplicateLx(self, lxobjs):
        """we have a nasty problem with data reloaded as we built the system
        and when the data feed is broken
        """
        lxdict={}
        for lxobj in lxobjs:
            lxkey = (lxobj.order_natural_key, lxobj.native_code, lxobj.date, lxobj.result_string, lxobj.result_date)
            if not lxdict.has_key(lxkey):
                lxdict[lxkey]=lxobj.id
        return lxdict.values() # list of unique lx ids
          
    
                                                                                
    def getOtherLxs(self, cond,demog,lxids):
        returnlxs=[]

        # NOTE: TODO ask:Do we really want lab results from all of this patient's cases
        # of this condition, rather than lab results from only this particular
        # case? if this is not correct.. then remove this code because it will 
        # return all the lab events in the new heuristic labs.
        # this goes across all cases, based on 30 after result date of first reportable lab
        # and 30 days before the order date of the first reportable lab
        cases = Case.objects.filter(patient=demog, condition=cond)
        all_case_labs = LabResult.objects.filter(events__case__in=cases)
        # exclude labs anyway if they have reportable flag as false.
        lab_native_codes  = all_case_labs.values_list('native_code', flat=True)
        all_case_labs = all_case_labs.exclude (native_code__in = LabTestMap.objects.filter(native_code__in = lab_native_codes, reportable=False).values_list('native_code', flat=True))
        # the exception will be when lxids is null 
        try:
            baselxs = LabResult.objects.filter(id =lxids.id).order_by('result_date')
            # get lastest Lx record
            maxrec=baselxs[len(baselxs)-1].result_date
            baselxs = LabResult.objects.filter(id =lxids.id).order_by('date')
            minrec=baselxs[0].date
        except:
            return all_case_labs
        if maxrec and minrec:
            try:
                maxdate = datetime.date(maxrec.year,maxrec.month,maxrec.day)+datetime.timedelta(30)
                mindate = datetime.date(minrec.year,minrec.month,minrec.day)-datetime.timedelta(30)
                for onelx in all_case_labs:
                    thisd = onelx.result_date
                    if thisd:
                        thisd = datetime.date(thisd.year,thisd.month,thisd.day)
                    if not thisd or (thisd>=mindate and thisd<=maxdate):
                        returnlxs.append(onelx)
                return returnlxs
            except:
                pass
        return  all_case_labs

    def makePID(self, demog=None, pcp=None, ):
        """
        patient demography and pcp
        need to change these so pass in relevant demog and pcp records
        """
        section = self.casesDoc.createElement("PID")
        self.addSimple(section,'1','PID.1')
        ##PID.3
        pid3 = self.casesDoc.createElement('PID.3')        
        if demog.ssn:
            last_four = demog.ssn[-4:]
        else:
            last_four = None
        worklist = [('MR', demog.mrn), ('SS', last_four)]
        for (cxtype,val) in worklist:
            if val:
                pid3 = self.casesDoc.createElement('PID.3')
                self.addSimple(pid3,val,'CX.1')
                self.addSimple(pid3,cxtype,'CX.5')
                if cxtype=='MR':
                    e = self.casesDoc.createElement('CX.6')
                    self.addSimple(e, pcp.dept,'HD.2')        
                    pid3.appendChild(e)                        
                section.appendChild(pid3)
        ##PID.5
        outerElement='PID.5'
        isClinician = 0
        patname = self.makeName(demog.first_name, demog.last_name, demog.middle_name, 
            demog.suffix, outerElement, isClinician)
        section.appendChild(patname)
        pid7 = self.casesDoc.createElement('PID.7')
        if demog.date_of_birth:
            formatted_dob = demog.date_of_birth.strftime(DATE_FORMAT)
        else:
            formatted_dob = ''
        self.addSimple(pid7, formatted_dob, 'TS.1')          
        section.appendChild(pid7)
        if demog.gender:
            self.addSimple(section,demog.gender,'PID.8')
        if demog.race and demog.race.upper() in self.racedir:
            race = self.racedir[demog.race.upper()]
        else:
            race = 'U' # Unknown race
        pidsec = self.casesDoc.createElement('PID.10')
        self.addSimple(pidsec,race,'CE.4')
        section.appendChild(pidsec)
        outerElement='PID.11'    
        addressType = 'H'
        address = self.makeAddress(demog.address1, demog.address2, demog.city, 
           demog.state, demog.zip, demog.country, outerElement, addressType)
        section.appendChild(address)
        if demog.tel:
            pid13 = self.casesDoc.createElement('PID.13')
            tac = demog.areacode
            tel = demog.tel_numeric
            ext = demog.tel_ext
            if tac == None: tac = ''
            if tel == None: tel = ''
            if ext == None: ext = ''
            self.addSimple(pid13,tac,'XTN.6')
            self.addSimple(pid13,tel,'XTN.7')
            if demog.tel_ext:
                self.addSimple(pid13,demog.tel_ext,'XTN.8') 
            else:
                self.addSimple(pid13,'','XTN.8') 
            section.appendChild(pid13)
        for elem, sec in [(demog.home_language,'PID.15'),(demog.marital_stat,'PID.16')]:
            if elem:
                pidsec = self.casesDoc.createElement(sec)
                self.addSimple(pidsec,elem,'CE.4')
                section.appendChild(pidsec)
        if demog.race and demog.race.upper() == 'HISPANIC':
            pidsec = self.casesDoc.createElement('PID.22')
            self.addSimple(pidsec,'H','CE.4')
            section.appendChild(pidsec)
        return section

    def makePCP(self, pcp=None, addressType=None, NKindx=1,NK13='PCP'):
        """ expect contents dict to have fields like firstName,telAreaCode etc
        writes out a couple of sections so broken out, so specific
        mapping dictionaries can be passed in to write different nk1 records
        """
        section = self.casesDoc.createElement("NK1")
        self.addSimple(section,'%s' % NKindx,'NK1.1')
        suffix = None
        isClinician = 0
        outerElement='NK1.2'
        name = self.makeName(pcp.first_name, pcp.last_name, pcp.middle_name, suffix, outerElement, isClinician)
        section.appendChild(name)
        x1 = self.casesDoc.createElement('NK1.3')
        self.addSimple(x1,NK13,'CE.4')
        section.appendChild(x1)
        outerElement='NK1.4'
        country='USA'
        #addressType=None
        address = self.makeAddress(pcp.dept_address_1, pcp.dept_address_2, 
            pcp.dept_city, pcp.dept_state, pcp.dept_zip, country, outerElement, addressType)
        section.appendChild(address)
        outerElement='NK1.5'
        email=''
        ext=''
        contact = self.makeContact(email,pcp.area_code,pcp.tel_numeric, ext,outerElement)
        if contact <> None:
            section.appendChild(contact)
        return section

    def makeFacility(self):
        """ expect contents dict to have fields like firstName,telAreaCode etc
        writes out a couple of sections so broken out, so specific
        mapping dictionaries can be passed in to write different nk1 records
        """
        section = self.casesDoc.createElement("NK1")
        self.addSimple(section,'2','NK1.1')
        suffix = None
        isClinician = 0
        outerElement='NK1.2'
        name = self.makeName(INSTITUTION.first_name, INSTITUTION.last_name, None, suffix, outerElement, isClinician)
        section.appendChild(name)
        x1 = self.casesDoc.createElement('NK1.3')
        self.addSimple(x1,'FCP','CE.4')
        section.appendChild(x1)
        outerElement='NK1.4'
        addressType='O'
        address = self.makeAddress(INSTITUTION.address1, INSTITUTION.address2, INSTITUTION.city,
            INSTITUTION.state, INSTITUTION.zip, INSTITUTION.country ,outerElement, addressType)
        section.appendChild(address)
        outerElement='NK1.5'
        email=INSTITUTION.email
        contact = self.makeContact(email, INSTITUTION.area_code, INSTITUTION.tel_numeric, INSTITUTION.tel_ext, outerElement)
        if contact <> None:
            section.appendChild(contact)
        return section

    def addCaseOBR(self, condition=None, dx_code=[], orcs=None, gender=''):
        """
            </OBR.31> is used to name the notifiable condition"""
        # TODO fix for icd10 patched for now
        obr = self.casesDoc.createElement('OBR')
        self.addSimple(obr,'1','OBR.1')
        obr4 = self.casesDoc.createElement('OBR.4')
        self.addSimple(obr4,'Additional Patient Demographics','CE.2')
        obr.appendChild(obr4)
        fakedx_code={'PID':'614.9',
                  'CHLAMYDIA':{'F':'099.53','M':'099.41','U':'099.41', '':'099.41'},
                  'GONORRHEA':'098.0',
                  'ACUTE HEPATITIS A':'070.10',
                  'ACUTE HEPATITIS B':'070.30'
                  }
        if not dx_code and condition.upper() in fakedx_code.keys():
            gender = gender.upper()
            dx_codevalues = fakedx_code[condition.upper()]
            if type(dx_codevalues)==type(''): ##a string
                dx_code=[dx_codevalues]
            else:
                try:
                    dx_code=[dx_codevalues[gender]]
                except: ##all other gender
                    dx_code = ['099.41']
        if dx_code:
            for i in dx_code:
                obr31 = self.casesDoc.createElement('OBR.31') 
                self.addSimple(obr31,i,'CE.1')   
                self.addSimple(obr31,condition,'CE.2')
                #TODO add support for Icd10
                self.addSimple(obr31,'I9','CE.3')
                obr.appendChild(obr31)
                orcs.appendChild(obr)

    def getPregnancyStatus(self, caseid):
        ##Email on 8/22/2007: Report patient as being pregnant if pregnancy flag active anytime between (test order date) and (test result date + 30 days inclusive).
        obx5='261665006' ##unknown
        #
        #
        case = Case.objects.get(pk=caseid)
        if case.patient.gender and case.patient.gender.upper().startswith('M'):
            return ('60001007' ,None)  
        if case.events.order_by('date'):
            first_event = case.events.order_by('date')[0]
            start_date = first_event.date
            end_date = start_date + datetime.timedelta(days=30)
            preg_encounters = Encounter.objects.filter(patient=case.patient, pregnant=True, date__gte=start_date,
                date__lte=end_date)
            if not preg_encounters:
                return (obx5, None)
            edd_encs = preg_encounters.filter(edd__isnull=False).order_by('date')
            if not edd_encs:
                raise IncompleteCaseData('Patient %s is pregnant during case window, but has no EDD.')
            edd = edd_encs[0].edd
            return ('77386006', edd)
        return (obx5, None)

    def addCaseOBX(self, demog=None, orcs=None,dx_code=None,lx=None, rx=None, encounters=[], condition=None, casenote='',caseid=''):
        """
        """
        indx=1
        #
        # Testing - Does MDPH accept null age?
        #
        if demog.date_of_birth:
            dur = (datetime.datetime.today() - demog.date_of_birth).days
            age = int(dur/365)
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'NM')],obx3=[('CE.4','21612-7')],obx5=[('',age)],nte=casenote)
            orcs.appendChild(obx)
            indx += 1
        ##pregnancy status
        (obx5, edd) = self.getPregnancyStatus(caseid)
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','11449-6'),('CE.5','PREGNANCY STATUS')],obx5=[('CE.4',obx5)])
        orcs.appendChild(obx)
        indx += 1
        ##EDD
        if edd:
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'TS')],obx3=[('CE.4','NA-8'),('CE.5','EXPECTED DATE OF CONFINEMENT')],
                                obx5=[('TS.1',edd.strftime(DATE_FORMAT))])
            indx += 1
            orcs.appendChild(obx)
            pregdur = edd - datetime.date.today()
            pregweeks = 40 - int(pregdur.days/7)
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'NM')],obx3=[('CE.4','NA-12')],
                                obx5=[('',pregweeks)])
            indx += 1
            orcs.appendChild(obx)
        ##NA_TRMT
        if rx and lx:
            rxdate = rx.date
            trmt = '373066001' #YES
        else:
            dur=None
            rxdate =None
            trmt = '373067005' #NO
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','NA-TRMT')], obx5=[('CE.4',trmt)])
        indx += 1
        orcs.appendChild(obx)
        ##NA_TRMTDT
        if rxdate:
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'TS')],obx3=[('CE.4','NA-TRMTDT')], obx5=[('TS.1',rxdate.strftime(DATE_FORMAT))])
            indx += 1
            orcs.appendChild(obx)
        ##Symptoms
        lxresd=None
        if lx:
            lxresd=lx.result_date #this will always be datetime
        sym='373067005' #NO
        temperature=0
        for enc in encounters:
            try:
                temperature = enc.temperature
            except:
                temperature=0
            if lxresd: 
                dur = enc.date - lxresd.date()
            else:
                dur = datetime.timedelta(days=0)
            if abs(dur.days)<15 or temperature>100.4:
                sym='373066001' #YES
                break
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','NA-5')], obx5=[('CE.4',sym)])
        indx += 1
        orcs.appendChild(obx)
        #removed for specific condition --if condition.upper()  in ('CHLAMYDIA', 'GONORRHEA'):
        if dx_code:
            for i in dx_code:
                obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'ST')],obx3=[('CE.4','10187-3')], obx5=[('',i)])
                indx += 1
                orcs.appendChild(obx)
        if temperature>100.4:
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'ST')],obx3=[('CE.4','10187-3')], obx5=[('','fever')])
            indx += 1
            orcs.appendChild(obx)

    def genReinfection(self,case,orus=None):
        #for now only labs but in the future the rest of heuristic types
        #TODO inspect what type of event is the first event and decide how to add the tag. 
        lxRecList = []
        reinfection_days = ConditionConfig.objects.get(name=case.condition).reinfection_days
        if reinfection_days >0 and case.followup_events.all():
            #only report the first one on the list
            if case.followup_events.all():
                for event in case.followup_events.all():
                    first_event = event.content_object
                    break
                
            lxRecList.insert(0, first_event)
                #if the event is a prescription  then use self.addRXOBX(rxRecList=rxobjs, orus=orus)
                # if the event is an encounter then use  self.addCaseOBX(demog=patient, orcs=orcs, dx_code=rep_dx_codes, lx=lx, rx=rx,
                #encounters=rep_encounters, condition=case.condition, casenote=case.notes,
                #caseid=case.pk)  
            #send it as rx record
            return self.addReinfOBX(case,lxRecList,orus)
    
    def addSpecimenSource (self, reinf, lxRec):
            #
            # Specimen Source 
            #
            obr15 = self.casesDoc.createElement('OBR.15') # noise - unknown specimen source. Eeessh
            sps = self.casesDoc.createElement('SPS.1')
            specso = lxRec.specimen_source
            snomed_spec_source_code = '261665006' # Local code for 'Unknown'
            #TODO for fenway we need to process the specimen source from the lab name to pull out the specimen source. 
            if specso:
                if CASE_REPORT_SPECIMEN_SOURCE_SNOMED_MAP.has_key(specso.lower()):
                    snomed_spec_source_code = CASE_REPORT_SPECIMEN_SOURCE_SNOMED_MAP[specso.lower()]
                    log.debug('Mapped specimen source "%s" to snomed code %s' % (specso, snomed_spec_source_code))
                else:
                    log.warning('Lab record has specimen source "%s", but no SNOMED code is known for that source.  Using SNOMED code for "unknown".' % specso)
            else:
                log.debug('No specimen source in lab record -- using SNOMED code for "unknown"')
            if reinf:
                obx = self.makeOBX(
                    obx1  = [('','4')],
                    obx2  = [('', 'CE')],
                    obx3  = [('CE.4','NA-286'), ('CE.5','Reinfection test source')],
                    obx5  = [('CE.4',snomed_spec_source_code)]
                    )
                return obx
            self.addSimple(sps, snomed_spec_source_code, 'CE.4')
            self.addSimple(sps,'L','CE.6') #TODO loinc code , why L 
            obr15.appendChild(sps)
            return obr15
            
    def addReinfOBX(self,case,lxRecList=[],orus=None):
        if not lxRecList: return
        
        m=1
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #
        # PORTING NOTE:  This will need more detailed attention, since LOINC removal 
        # means ConditionLOINC objects cannot be directly translated to new code base.
        #
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        for lxRec in lxRecList:
            n = 1        
            # redmine to not create an object if the result is null?? is this valid for reinfection too?
            if not lxRec.result_float and not lxRec.result_string:
                continue

            reinf_output_code = lxRec.output_or_native_code 
            reinf_output_code = LabTestMap.objects.filter (native_code =  lxRec.native_code).values_list('reinf_output_code', flat=True)
            if reinf_output_code:
                reinf_output_code= reinf_output_code[0]
        
            top = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP ')
            
            obr = self.casesDoc.createElement('OBR')
            self.addSimple(obr,'1','OBR.1')
            obr4 = self.casesDoc.createElement('OBR.4')
            self.addSimple(obr4,'Additional Patient Demographics','CE.2')
            obr.appendChild(obr4)
            top.appendChild(obr)
            
            obx1 = self.makeOBX(
                    obx1  = [('',n)],
                    obx2  = [('', 'CE')],
                    obx3  = [('CE.4','NA-283'), ('CE.5','Test of reinfection done')],
                    obx5  = [('CE.4','373066001' )]
                    )
         
            top.appendChild(obx1)
            n+=1
            
            obx1 = self.makeOBX(
                    obx1  = [('',n)],
                    obx2  = [('', 'TS')],
                    obx3  = [('CE.4','NA-284'), ('CE.5','Reinfection test date')],
                    obx5  = [('TS.1',lxRec.date.strftime(DATE_FORMAT) )]
                    )
            top.appendChild(obx1)
            
            n+=1
            #find out if lab is positive or negative or indetermined
            case_lx = Case.objects.get(id=case.id, followup_events__name__startswith='lx', followup_events__object_id=lxRec.id)
            if "positive" in str(case_lx.followup_events.get(object_id=lxRec.id).name):
                resultsnomed = '10828004'
            elif "negative" in str(case_lx.followup_events.get(object_id=lxRec.id).name):
                resultsnomed = '260385009'
            elif "indeterminate" in str(case_lx.followup_events.get(object_id=lxRec.id).name):
                resultsnomed = '42425007'
            
            obx1 = self.makeOBX(
                    obx1  = [('',n)],
                    obx2  = [('', 'CE')],
                    obx3  = [('CE.4','NA-285'), ('CE.5','Reinfection test result')],
                    obx5  = [('CE.4',resultsnomed )]
                    )
            top.appendChild(obx1)
            n+=1
            # add specimen source 
            
            obx1 = self.addSpecimenSource(True, lxRec)
            top.appendChild(obx1)   
            orus.appendChild(top)     
            
                
    def addLXOBX(self,case,lxRecList=[],orus=None):
        if not lxRecList: return
        condition=case.condition
        n=1
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #
        # PORTING NOTE:  This will need more detailed attention, since LOINC removal 
        # means ConditionLOINC objects cannot be directly translated to new code base.
        #
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        for lxRec in lxRecList:
            #
            # Don't think we need this, since cases that should not be sent 
            # will have their initial status set to "NO"
            #
            #needsend =ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc,CondiRule=condition)[0].CondiSend
            #if needsend==0: ##no need send
                #continue
            # redmine to not create an object if the result is null
            if not lxRec.result_float and not lxRec.result_string:
                continue
            snomed, snomed2, titer_dilution, finding =self.getSNOMED(lxRec,condition) 
            if finding:
                if LabTestMap.objects.filter(native_code__exact=lxRec.native_code, donotsend_results__indicates__iexact=finding).exists():
                    continue
            orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
            orus.appendChild(orcs)
            orc = self.makeORC(lxRec.provider)
            orcs.appendChild(orc)
            obr = self.casesDoc.createElement('OBR') # need a special lx OBR
            self.addSimple(obr,n,'OBR.1')
            n+=1
            obr3 = self.casesDoc.createElement('OBR.3')
            self.addSimple(obr3,lxRec.order_natural_key,'EI.1')
            obr.appendChild(obr3)
            obr4 = self.casesDoc.createElement('OBR.4')
            self.addSimple(obr4,lxRec.output_or_native_code,'CE.4') 
            self.addSimple(obr4,'L','CE.6') # loinc code
            obr.appendChild(obr4)
            obr7 = self.casesDoc.createElement('OBR.7')
            obr.appendChild(obr7)
            self.addSimple(obr7,lxRec.date.strftime(DATE_FORMAT),'TS.1') # lx date
            # add specimen source 
            obr.appendChild(self.addSpecimenSource ( False, lxRec))
            #
            #
            if lxRec.status in ('FINAL','F'):
                status='F'
            else:
                status='P'
            self.addSimple(obr,status,'OBR.25') # result status
            orcs.appendChild(obr)
            # now add the obx records needed to describe dose, frequency and duration
            lxTS = lxRec.date
            lxRange = 'Low: %s - High: %s' % (lxRec.ref_low_string, lxRec.ref_high_string)
            if titer_dilution:
                res = lxRec.result_string
                obx2_type = 'ST'
                obx5_type = ''
                ref_unit = '' # When ref_unit is blank string, makeOBX does not add an OBX.6 tag
                lxRange = '<1:%s' % (titer_dilution)
            elif lxRec.result_float:
                res = lxRec.result_float
                obx2_type = 'SN'
                obx5_type = 'SN.2'
                if lxRec.ref_unit:
                    ref_unit = lxRec.ref_unit
                else:
                    ref_unit = 'Unknown'
            elif lxRec.result_string:
                res = lxRec.result_string.split()[0]
                obx2_type = 'ST'
                obx5_type = ''
                ref_unit = '' # When ref_unit is blank string, makeOBX does not add an OBX.6 tag
            else:
                res = ''
                obx2_type = 'ST'
                obx5_type = ''
                ref_unit = ''
                
            clia  = lxRec.CLIA_ID
            if not clia:
                clia = INSTITUTION.clia # it was hard coded to '22D0076229'    
            
            if not snomed: ##like ALT/AST and must be number
                obx1 = self.makeOBX(
                    obx1  = [('','1')],
                    obx2  = [('', obx2_type)],
                    obx3  = [('CE.4',lxRec.output_or_native_code),('CE.6','L')],
                    obx6  = [('CE.1', ref_unit)],
                    obx5  = [(obx5_type, res)], 
                    obx7  = [('',lxRange)],
                    obx11 = [('', lxRec.status)],
                    obx14 = [('TS.1',lxTS.strftime(DATE_FORMAT))], 
                    obx15 = [('CE.1',clia), ('CE.3','CLIA')]
                    )
            else:
                obx1 = self.makeOBX(
                    obx1  = [('','1')],
                    obx2  = [('', 'CE')],
                    obx3  = [('CE.4',lxRec.output_or_native_code),('CE.6','L')],
                    obx5  = [('CE.4',snomed)],  
                    obx7  = [('',lxRange)],
                    obx11 = [('', lxRec.status)],
                    obx14 = [('TS.1',lxTS.strftime(DATE_FORMAT))], 
                    obx15 = [('CE.1',clia), ('CE.3','CLIA')]
                    )
            orcs.appendChild(obx1)
            
            
            if snomed2:
                orcs.appendChild(self.makeOBX(
                    obx1  = [('','2')],
                    obx2  = [('', 'CE')],
                    obx3  = [('CE.4',lxRec.output_or_native_code),('CE.6','L')],
                    obx5  = [('CE.4',snomed2)],  
                    obx7  = [('',lxRange)],
                    obx11 = [('', lxRec.status)],
                    obx14 = [('TS.1',lxTS.strftime(DATE_FORMAT))], 
                    obx15 = [('CE.1',clia), ('CE.3','CLIA')]
                    ))
                        
    def getSNOMED(self, lxRec,condition):
        # returns four values related to lab finding used in LXOBX
        # the return statements 
        snomed=None
        snomed2=None
        titer_dilution=None
        finding=None
        #dummy lab
        if condition.upper() == 'TUBERCULOSIS' and lxRec.output_or_native_code == 'MDPH-250' :
            snomed='MDPH-R348'
            finding='ind'
            return snomed, snomed2, titer_dilution, finding
        snomedposi = lxRec.snomed_pos
        snomednega = lxRec.snomed_neg
        snomedinter = lxRec.snomed_ind
        if snomedposi=='' and snomednega=='': ##like ALT/AST
            return snomed, snomed2, titer_dilution, finding
        # we have to get the titer dilution level for positive results from
        # the lab heuristic in order to determine if a titer lab is positive.
        # This is clunky.  BaseLabResultsHeuristic.get_all returns a set of heuristic
        # objects, some of which have the titer_dilution attribute, and some of 
        # those have value titer_dilution values.
        titerHset=set(h for h in BaseLabResultHeuristic.get_all() if hasattr(h,'titer_dilution') and h.titer_dilution)
        for h in titerHset:
            try:
                if LabTestMap.objects.filter(test_name=h.test_name, native_code=lxRec.native_code).exists():
                    titer_dilution=h.titer_dilution
                    continue
            except:
                msg = 'heuristic %s is mapped to test_name %s but no such test mapped in Labtestmap' % (str(h), h.test_name)
                log.debug(msg)
            #this breaks if a lab test can be part of more than one test heuristic, AND titer dilution level is different over these heuristics.                        
        if titer_dilution:
            if next((s for s in ['1:%s' % 2**i for i in range(int(math.log(4096,2)), int(math.log(titer_dilution, 2))-1, -1)] if s in lxRec.result_string), None):
                snomed=snomedposi
                finding='pos'
                snomed2=TITER_DILUTION_CHOICES[next(s for s in ['1:%s' % 2**i for i in range(int(math.log(4096,2)), int(math.log(titer_dilution, 2))-1, -1)] if s in lxRec.result_string)]
            elif next((s for s in ['1:%s' % 2**i for i in range(int(math.log(titer_dilution, 2)),0,-1)] if s in lxRec.result_string), None):
                snomed=snomednega
                snomed2=TITER_DILUTION_CHOICES[next(s for s in ['1:%s' % 2**i for i in range(int(math.log(titer_dilution, 2)),0,-1)] if s in lxRec.result_string)]
                finding='neg'
            else: 
                snomed=snomedinter
                finding='ind'
            return snomed, snomed2, titer_dilution, finding
        #now check the case lx events to see if this lab matches one of those -- if so, get the finding and set snomed
        try:
            case_lx = Case.objects.get(id=self.currentCase, events__name__startswith='lx', events__object_id=lxRec.id)
            if "positive" in str(case_lx.events.get(object_id=lxRec.id).name):
                snomed=snomedposi
                finding='pos'
            elif "negative" in str(case_lx.events.get(object_id=lxRec.id).name):
                snomed=snomednega
                finding='neg'
            elif "indeterminate" in str(case_lx.events.get(object_id=lxRec.id).name):
                snomed=snomedinter
                finding='ind' 
            return snomed, snomed2, titer_dilution, finding
        except: 
            #now we essentially replicate hef.base.labresultpositiveheuristic
            try:
                if lxRec.result_float < lxRec.threshold:
                    snomed=snomednega
                    finding='neg'
                else:
                    snomed=snomedposi
                    finding='pos'
                return snomed, snomed2, titer_dilution, finding
            except:
                #now it gets messy.  The resultstring stuff is designed to build django queryset definitions
                # so we're stuck re-querying for the lab result.
                map_obj = LabTestMap.objects.get(native_code=lxRec.native_code)
                pos_q = ResultString.get_q_by_indication('pos')
                neg_q = ResultString.get_q_by_indication('neg')
                ind_q = ResultString.get_q_by_indication('ind')
                if map_obj.extra_positive_strings.all() \
                    or map_obj.excluded_positive_strings.all():
                    pos_q &= map_obj.positive_string_q_obj
                if LabResult.objects.filter(Q(id=lxRec.id),pos_q).exists():
                    snomed=snomedposi
                    finding='pos'
                    return snomed, snomed2, titer_dilution, finding
                if map_obj.extra_negative_strings.all() \
                    or map_obj.excluded_negative_strings.all():
                    neg_q &= map_obj.negative_string_q_obj
                if LabResult.objects.filter(Q(id=lxRec.id),neg_q).exists():
                    snomed=snomednega
                    finding='neg'
                    return snomed, snomed2, titer_dilution, finding
                if map_obj.extra_indeterminate_strings.all() \
                    or map_obj.excluded_indeterminate_strings.all():
                    ind_q &= map_obj.indeterminate_string_q_obj
                if LabResult.objects.filter(Q(id=lxRec.id),ind_q).exists():
                    snomed=snomedinter
                    finding='ind'
                    return snomed, snomed2, titer_dilution, finding
                #if nothing hits, return all None
                return None, None, None, None
        
    def addEXVOBX(self,exvRecList=[],orus=None):
        """
        make a record for each extended variable record in the caseDict
        whew, this hl7 stuff really is a pain to write.
        All detail, no fun.
        """
        if exvRecList:
            orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
            orus.appendChild(orcs)
            notified = False
            obr = self.casesDoc.createElement('OBR')
            self.addSimple(obr,'1','OBR.1')
            obr4 = self.casesDoc.createElement('OBR.4')
            self.addSimple(obr4,'Additional Patient Demographics','CE.2')
            obr.appendChild(obr4)
            orcs.appendChild(obr)
            
            for lab in exvRecList:
                extended_variables  = Order_Extension.objects.filter( order_natural_key = lab.order_natural_key)
                
                n=1
                for exvRec in extended_variables:
                    obx1 = None
                    if exvRec.question == 'Number of partners that were provided EPT' :
                        obx1 = self.makeOBX(
                        obx1  = [('',n)],
                        obx2  = [('', 'ST')],
                        obx3  = [('CE.4','NA-352'), ('CE.5','EPT_NUMBER_CONTACTS')],
                        obx5  = [('',exvRec.answer )]
                        )
                    elif lab.native_code == '355804--' and exvRec.answer.upper() == 'NO' and exvRec.question == 'Did the partner have their own encounter with this office for evaluation and treatment?' :                             
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-351'), ('CE.5','EPT_CONTACTS_TREATED')],
                            obx5  = [('CE.4','373067005' ), ('CE.5',exvRec.answer)]     )
                            # what if not yes or no ????
                    elif lab.native_code == '355806--' and exvRec.answer.upper() == 'NO' and exvRec.question == 'Did the partner have their own encounter with this office for evaluation and treatment?': 
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-351'), ('CE.5','EPT_CONTACTS_TREATED')],
                            obx5  = [('CE.4','NAR-42' ), ('CE.5','YES-extra prescription provided')]     )
                    elif lab.native_code == '355805--' and exvRec.answer.upper() == 'NO' and exvRec.question == 'Did the partner have their own encounter with this office for evaluation and treatment?':                           
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-351'), ('CE.5','EPT_CONTACTS_TREATED')],
                            obx5  = [('CE.4','NAR-43' ), ('CE.5','YES- extra medication provided')]    )
                    elif (lab.native_code == '355806--' or lab.native_code == '355805--' or lab.native_code == '355804--' ) and  exvRec.answer.upper() == 'YES' and  exvRec.question == 'Did the partner have their own encounter with this office for evaluation and treatment?' :
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-351'), ('CE.5','EPT_CONTACTS_TREATED')],
                            obx5  = [('CE.4','NAR-44' ), ('CE.5',exvRec.answer)]    )
                    elif exvRec.question == 'Were any of the patient\'s sex partners notified of possible exposure to chlamydia?' and not notified:
                        notified = True;
                        if exvRec.answer.upper() == 'NO':  
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-354'), ('CE.5','CRF_CONTACTS_NOTIFIED')],
                            obx5  = [('CE.4','373067005' ), ('CE.5',exvRec.answer)]     )
                        elif exvRec.answer == 'Yes, our office notified the partner(s)':
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-354'), ('CE.5','CRF_CONTACTS_NOTIFIED')],
                            obx5  = [('CE.4','NAR-45' ), ('CE.5',exvRec.answer)]     )
                        elif exvRec.answer == 'Yes, the patient was asked to notify the partner(s)':
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-354'), ('CE.5','CRF_CONTACTS_NOTIFIED')],
                            obx5  = [('CE.4','NAR-46' ), ('CE.5',exvRec.answer)]     )
                        elif exvRec.answer.upper() == 'UNKNOWN':  
                            obx1 = self.makeOBX(
                            obx1  = [('',n)],
                            obx2  = [('', 'CE')],
                            obx3  = [('CE.4','NA-354'), ('CE.5','CRF_CONTACTS_NOTIFIED')],
                            obx5  = [('CE.4','NAR-37' ), ('CE.5',exvRec.answer)]     )
                            
                    if obx1:
                        orcs.appendChild(obx1)
                        n+=1 
        
    def addRXOBX(self,rxRecList=[],orus=None):
        """
        make a record for each drug record in the caseDict
        whew, this hl7 stuff really is a pain to write.
        All detail, no fun.
        """
        n=1
        for rxRec in rxRecList:
            orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
            orus.appendChild(orcs)
            orc = self.makeORC(rxRec.provider)
            orcs.appendChild(orc)
            obr = self.casesDoc.createElement('OBR') # need a special rx OBR
            self.addSimple(obr,'%d' % n,'OBR.1')
            n+=1
            obr3 = self.casesDoc.createElement('OBR.3')
            self.addSimple(obr3,rxRec.order_natural_key,'EI.1') 
            obr.appendChild(obr3)
            obr4 = self.casesDoc.createElement('OBR.4')
            ########Added Jan,2009 to fix EMR Mapping question in order to
            ########integrate with MAVEN system from Barrus, Stephen (DPH)
            self.addSimple(obr4,'Additional Patient Demographics','CE.2')
            self.addSimple(obr4,'18776-5','CE.4') # treatment plan
            self.addSimple(obr4,'L','CE.6') # loinc code
            obr.appendChild(obr4)
            obr7 = self.casesDoc.createElement('OBR.7')
            obr.appendChild(obr7)
            self.addSimple(obr7,rxRec.date.strftime(DATE_FORMAT),'TS.1') # rx date
            obr15 = self.casesDoc.createElement('OBR.15') # noise - unknown specimen source. Eeessh
            sps = self.casesDoc.createElement('SPS.1')
            self.addSimple(sps,'261665006','CE.4') #unknown
            self.addSimple(sps,'L','CE.6') # loinc code
            obr15.appendChild(sps)
            obr.appendChild(obr15)
            provider = rxRec.provider
            obr16 =self.makeName(firstName=provider.first_name, lastName=provider.last_name, 
                middleInit=provider.middle_name, suffix='', outerElement ='OBR.16', isClinician=1)
            obr.appendChild(obr16)
            if rxRec.status: status= 'F'
            else: status = 'P'
            self.addSimple(obr,status,'OBR.25') # result status
            orcs.appendChild(obr)
            # now add the obx records needed to describe dose, frequency and duration
            rxDur='N/A'
            if rxRec.start_date and not rxRec.end_date:
                rxDur ='1'
            elif rxRec.start_date and rxRec.end_date:
                #
                # PORTING NOTE: This should blow up, because it's assuming dates are strings.
                #
                rxDur = rxRec.end_date - rxRec.start_date
                rxDur = rxDur.days+1
            rxTS = rxRec.date #TODO time stamp is not sent should it?
            #<OBX.5>NDC_Number; Drug Name; Dose; Frequency; Duration</OBX.5>
            drugstr = '%s;%s;%s;%s;%s day(s)' % (rxRec.code, rxRec.name, rxRec.dose, rxRec.frequency, rxDur)
            obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'ST')],obx3=[('CE.4','NA-56')],
                               obx5=[('', drugstr)])
            orcs.appendChild(obx1)

    def makeOBX(self, obx1=[],obx2=[],obx3=[],obx5=[],obx6=[],obx7=[],obx11=[('','')],obx14=[],obx15=[],nte=''):
        """observation segment constructor
        """
        obx = self.casesDoc.createElement('ORU_R01.OBXNTE_SUPPGRP')
        p = self.casesDoc.createElement('OBX')
        for (OuterTag, obxl) in [('OBX.1',obx1),('OBX.2',obx2),('OBX.3',obx3), ('OBX.5',obx5),('OBX.6',obx6),('OBX.7',obx7),('OBX.11',obx11),('OBX.14',obx14),('OBX.15',obx15)]:
            if len(obxl)==1 and obxl[0][0]=='':
                if '%s'.strip() % obxl[0][1]:
                    self.addSimple(p,obxl[0][1],OuterTag)
            elif len(obxl)>0:
                tempobx=None
                for tag,v in obxl:
                    if not tempobx and '%s' % v  !='':
                        tempobx = self.casesDoc.createElement(OuterTag)
                    if '%s' % v !='':
                        self.addSimple(tempobx,v,tag)          
                if tempobx:
                    p.appendChild(tempobx)
        obx.appendChild(p)
        if nte:
            n = self.casesDoc.createElement('NTE')
            self.addSimple(n,  nte,'NTE.3')
            obx.appendChild(n)
        return obx
       
    def makeORC(self, pcp=None):
        """updated like makePCP to use the pcp record
        """
        orc = self.casesDoc.createElement('ORC')
        suffix = ''
        isClinician = 1
        outerElement='ORC.12'
        name = self.makeName(pcp.first_name, pcp.last_name, pcp.middle_name, suffix, outerElement, isClinician)
        orc.appendChild(name)
        outerElement='ORC.14'
        email=''
        ext=''
        if pcp.tel_numeric:
            contact = self.makeContact(email, pcp.area_code, pcp.tel_numeric, ext, outerElement)
        else: 
            contact = self.makeContact(INSTITUTION.email, INSTITUTION.area_code, INSTITUTION.tel_numeric, INSTITUTION.tel_ext, outerElement)
        
        if contact <> None:
            orc.appendChild(contact)
        orc21 = self.casesDoc.createElement('ORC.21')
        if pcp.dept:
            self.addSimple(orc21, pcp.dept, 'XON.1')
        else: 
            self.addSimple(orc21, INSTITUTION.name, 'XON.1')
        
        orc.appendChild(orc21)
        outerElement='ORC.22'
        country='USA'
        addressType=None
        if pcp.dept_address_1:
            address = self.makeAddress(pcp.dept_address_1, pcp.dept_address_2, pcp.dept_city, pcp.dept_state,
                pcp.dept_zip, country ,outerElement, addressType)
        else: 
            address = self.makeAddress(INSTITUTION.address1, INSTITUTION.address2, INSTITUTION.city,
                INSTITUTION.state, INSTITUTION.zip, country ,outerElement, addressType)
        orc.appendChild(address)
        outerElement='ORC.23'
        if pcp.tel_numeric:
            contact = self.makeContact(email, pcp.area_code, pcp.tel_numeric, ext, outerElement)
        else:  
            contact = self.makeContact(INSTITUTION.email, INSTITUTION.area_code, INSTITUTION.tel_numeric, INSTITUTION.tel_ext, outerElement)
        
        if contact <> None:
            orc.appendChild(contact)
        outerElement='ORC.24'
        #TODO why is this done twice? was it meant to be address2?
        if pcp.dept_address_1:
            address = self.makeAddress(pcp.dept_address_1, pcp.dept_address_2, pcp.dept_city, pcp.dept_state,
                pcp.dept_zip, country ,outerElement, addressType)
        else: 
            address = self.makeAddress(None, None, None, None, None, country ,outerElement, addressType)
        
        orc.appendChild(address)
        return orc

    def makeMSH(self, elr, center_id, segcontents = None, processingFlag='P', versionFlag='2.3.1'):
        """MSH segment
        """
        # Create the elements
        section = self.casesDoc.createElement("MSH")
        self.addSimple(section,'|','MSH.1')
        self.addSimple(section,u'^~\&','MSH.2')
        e = self.casesDoc.createElement('MSH.3')
        self.addSimple(e,SITE_HEADER,'HD.1')
        section.appendChild(e)
        e = self.casesDoc.createElement('MSH.4')
        
        #TODO redmine 492 waiting to see where to put the center id.
        #TODO mayb find out a clia for mass leage to add here.. 
        #hd_name= INSTITUTION.name
        #if hd_name.find('%')>-1:
            #hd_name = center_id 
        #TODO for (element,ename) in [(INSTITUTION.name, 'HD.1'),(INSTITUTION.clia, 'HD.2'), ('CLIA','HD.3'), (center_id,'HD.4')]:
        # 
        if elr:
            self.addSimple(e,INSTITUTION.name+'ELR','HD.1')
        else:
            self.addSimple(e,INSTITUTION.name,'HD.1')
        for (element,ename) in [(INSTITUTION.clia, 'HD.2'), ('CLIA','HD.3')]:   
            if element <> '':
                self.addSimple(e,element,ename)    
        section.appendChild(e)
        e = self.casesDoc.createElement('MSH.5')         
        self.addSimple(e,'MDPH','HD.1')
        section.appendChild(e)
        e = self.casesDoc.createElement('MSH.6')         
        self.addSimple(e,'MDPH','HD.1')
        section.appendChild(e)
        e = self.casesDoc.createElement('MSH.7')
        timestamp = isoTime() # will give now
        self.addSimple(e,timestamp,'TS.1')
        section.appendChild(e)
        e = self.casesDoc.createElement('MSH.9')
        self.addSimple(e,'ORU','MSG.1')
        self.addSimple(e,'R01','MSG.2')
        section.appendChild(e)
        self.addSimple(section,'MDPH%s' % timestamp,'MSH.10')
        e = self.casesDoc.createElement('MSH.11')
        self.addSimple(e,processingFlag,'PT.1')
        section.appendChild(e)
        e = self.casesDoc.createElement('MSH.12')        
        self.addSimple(e,versionFlag,'VID.1')
        section.appendChild(e)
        return section
 
    def addSimple(self,dest=None, txt='',ename=''):
        """ Version for cases - must add to self.casesDoc
        abstracted out to add a single child element to an existing element
        """
        if txt =='':
            return
        tt = self.casesDoc.createTextNode('%s' % txt) 
        e = self.casesDoc.createElement(ename)
        e.appendChild(tt)
        if dest == None:
            self.casesDoc.appendChild(e)
        else:
            dest.appendChild(e)

    def addHSimple(self,dest=None, txt='',ename=''):
        """ Version for headers - must add to self.batchDoc
        abstracted out to add a single child element to an existing element
        """
        if not txt:
            return
        tt = self.batchDoc.createTextNode(txt) 
        e = self.batchDoc.createElement(ename)
        e.appendChild(tt)
        if dest == None:
            self.batchDoc.appendChild(e)
        else:
            dest.appendChild(e)

    def makeFHS(self):
        """broken out for clarity
        """
        fhs = self.batchDoc.createElement("FHS")
        self.addHSimple(fhs,'|','FHS.1')
        self.addHSimple(fhs,'^\&','FHS.2')
        self.addHSimple(fhs, APP_NAME, 'FHS.3') # file sending app
        self.addHSimple(fhs, SENDING_FACILITY, 'FHS.4')
        fhs2 = self.batchDoc.createElement('FHS.7')
        self.addHSimple(fhs2,self.timestamp,'TS.1')
        fhs.appendChild(fhs2)
        self.addHSimple(fhs, COMMENTS, 'FHS.11')
        return fhs

    def makeBHS(self):
        """broken out. Should have one per institution I think
        """
        bh = self.batchDoc.createElement("BHS")
        self.addHSimple(bh,'|','BHS.1')
        self.addHSimple(bh,u'^\&','BHS.2') # has to be unicode to avoid quoting
        self.addHSimple(bh, APP_NAME, 'BHS.3')
        self.addHSimple(bh, SENDING_FACILITY, 'BHS.4')
        e = self.batchDoc.createElement('BHS.7')
        self.addHSimple(e,self.timestamp,'TS.1')
        bh.appendChild(e)
        return bh

    def makeName(self, firstName, lastName, middleInit, suffix, outerElement, isClinician):
        """reusable component = xpn1-4 pass the field names
        from the right record!
        if is clinician, need XCN rather than XPN (!) with different sequence numbers...
        """
        if lastName:
            lastName = lastName.strip()
        if not lastName: lastName='Unknown'
                
        if firstName:
            firstName = firstName.strip()
        if not firstName: firstName='Unknown'
        
        outer = self.casesDoc.createElement(outerElement)
        if not isClinician:
            n = self.casesDoc.createElement('XPN.1')
        else:
            n = self.casesDoc.createElement('XCN.2')
        self.addSimple(n,lastName,'FN.1')
        outer.appendChild(n)
        if not isClinician:
            worklist = [(firstName,'XPN.2'),(middleInit,'XPN.3'),(suffix,'XPN.4')]
        else:
            worklist = [(firstName,'XCN.3'),(middleInit,'XCN.4'),(suffix,'XCN.5')]
        for (evar,ename) in worklist:
            if evar:
                self.addSimple(outer,evar,ename)
        return outer
                 
    def makeAddress(self, address, addressOther, city, state, zipcode, country ,outerElement, addressType):
        """reusable component = xad.1-7 pass the field names
        from the right record!
        """
        outer = self.casesDoc.createElement(outerElement)
        worklist = [(address,'XAD.1'),(addressOther,'XAD.2'),(city,'XAD.3'),(state,'XAD.4'),
                    (zipcode,'XAD.5'),(country,'XAD.6')]
        for (evar,ename) in worklist:
            if evar:
                self.addSimple(outer,evar,ename)
        if addressType <> None:
            self.addSimple(outer,addressType,'XAD.7')
        return outer

    def makeContact(self, email, tac, tel, ext, outerElement):
        """xtn4,6,7 and 8
        pass the right values in the segcontents dict!
        """
        outer = None
        if email==None: email=''
        if tac == None: tac = ''
        if tel == None: tel = ''
        if ext == None: ext=''
        (email,tac,tel,ext) = (email.strip(),tac.strip(),tel.strip(),ext.strip())
        s = '%s%s%s%s' % (email,tac,tel,ext)
        if len(s) > 0: # something there...
            outer = self.casesDoc.createElement(outerElement)
            worklist = [(email,'XTN.4'),(tac,'XTN.6'),(tel,'XTN.7'),(ext,'XTN.8')]
            for (element,ename) in worklist:
                if element:
                    self.addSimple(outer,element,ename)
        return outer



# from the mapping software
hl7races = """
I      American Indian or Alaska Native                       
A     Asian             
B     Black or African-American             
P     Native Hawaiian or Other Pacific Islander             
O     Other             
U     Unknown             
W     White"""

class Command(BaseCommand):
    
    help = 'Geneate reports for Nodis cases'
    
    args = '[conditions]'
    
    option_list = BaseCommand.option_list + (
        make_option('--case', action='store', dest='case_id', type='int', metavar='ID', 
            help='Export a single case with specified case ID'),
        make_option('--status', action='store', dest='status', default='Q',
            help='Export only cases with this status ("Q" by default)'),
        make_option('--elr', action='store_true', dest='elr',
            default=False, help='generates only elr cases'), 
        make_option('--mdph', action='store_true', dest='mdph', default=False,
            help='Export cases in HL7v3 dialect required by Massachusetts Department of Public Health'),
        make_option('--transmit', action='store_true', dest='transmit', default=False, 
            help='Transmit cases after generation'),
        make_option('--no-mark-sent', action='store_false', dest='mark_sent', default=True,
            help='Do NOT set cases status to "S"'),
        make_option('-o', action='store', metavar='FOLDER', dest='output_folder',
            default=CASE_REPORT_OUTPUT_FOLDER, help='Output case report file(s) to FOLDER'),
        make_option('-t', action='store', metavar='TEMPLATE', dest='template', 
            default=CASE_REPORT_TEMPLATE, help='Use TEMPLATE to generate HL7 messages'),
        make_option('-f', action='store', dest='format', metavar='FORMAT', default=CASE_REPORT_FILENAME_FORMAT,
            help='Create file names using FORMAT.  Default: %s' % CASE_REPORT_FILENAME_FORMAT),
        make_option('--stdout', action='store_true', dest='stdout', default=False,
            help='Print output to STDOUT (no files created)'),
        make_option('--individual', action='store_false', dest='one_file',
            default=False, help='Export each cases to an individual file (default)'),
        make_option('--one-file', action='store_true', dest='one_file',
            default=False, help='Export all cases to one file.  Always true for MDPH reports.'),
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
        if options.one_file and CASE_REPORT_BATCH_SIZE:
            print >> sys.stderr, '--batch-size and --one-file cannot be used together'
            sys.exit(104)
        if options.stdout and options.transmit:
            print >> sys.stderr, '--stdout and --transmit cannot be used together'
            sys.exit(104)
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
            q_obj = Q(condition__in=report_conditions) & Q(status=options.status)
        
        if options.elr:
            q_obj &= Q(condition__startswith='elr')
        else:
            q_obj &= ~Q(condition__startswith='elr')
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
        batch_size = CASE_REPORT_BATCH_SIZE
        if options.one_file or not batch_size:
            batch_size = case_count
        batch_serial = 0
        self.timestamp = datetime.datetime.now().strftime('%Y-%b-%d.%H.%M.%s')
        for index in range(0, case_count, batch_size):
            filename_values = { 
                # Used to populate file name template -- serial is updated below
                'serial_number': batch_serial,
                'timestamp': self.timestamp,
                }
            if cases:
                batch_cases = cases[index:index+batch_size]
            #
            # Generate report message
            #
            if options.mdph:
                report_str = self.mdph(options.elr, batch_serial, batch_cases)
            else:
                report_str = self.use_template(options, batch_serial, batch_cases)
            log.debug('Message to report:\n%s' % report_str)
            report_obj = Report(
                run = run,
                message = report_str,
                ) 
            #
            # Output
            #
            if options.stdout: # Print case reports to STDOUT
                log.debug('Printing message to stdout')
                report_obj.filename = 'STDOUT'
                print report_str
            else: # Produce one output file per batch
                filename = options.format % filename_values
                report_obj.filename = filename
                filepath = os.path.join(options.output_folder, filename)
                output_file_paths.append(filepath)
                casefile = open(filepath, 'w')
                casefile.write(report_str)
                casefile.close()
                log.info('Wrote case report to file: %s' % filepath)
                #
                # Transmission
                #
                if options.transmit: 
                    success = True #TODO for testing and comment out the line below
                    #success = self.transmit(options, filepath)
                    if success:
                        if options.mark_sent:
                            for case in batch_cases:
                                # redmine 467 checking other status if case events were  
                                # modified after report sent
                                if (case.status == 'RQ'):
                                    case.status = 'RS'
                                else:
                                    case.status = 'S'
                                case.reportables = case.create_reportables_list()
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
        template_name = os.path.join('case_report', options.template)
        log.debug('template_name: %s' % template_name)
        try:
            get_template(template_name)
        except TemplateDoesNotExist:
            print >> sys.stderr
            print >> sys.stderr, 'Unrecognized template name: "%s".  Aborting.' % options.template
            print >> sys.stderr
            sys.exit(103)
        #
        # Build report message 
        #
        values = {
            'cases': cases,
            'batch_serial': batch_serial,
            }
        log.debug('values for template: \n%s' % pprint.pformat(values))
        case_report = render_to_string(template_name, values)
        # Remove blank lines -- allows us to have neater templates
        case_report = '\n'.join([x for x in case_report.split("\n") if x.strip()!=''])
        return case_report
    
    def mdph(self, elr, batch_serial, cases):
        batch = hl7Batch(nmessages=len(cases))
        for case in cases:
            log.debug('Generating HL7 for %s' % case)
            try:
                batch.addCase(case, elr)
            except NoConditionConfigurationException, e:
                log.critical('Could not generate HL7 message for case %s!' % case)
                log.critical('    %s' % e)
            except IncompleteCaseData, e:
                log.critical('Could not generate HL7 message for case %s !' % case)
                log.critical('    %s' % e)
        case_report = batch.renderBatch()
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
    
