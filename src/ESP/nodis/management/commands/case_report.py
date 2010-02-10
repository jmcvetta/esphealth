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
999    Functionality not yet implemented
'''


from ESP.settings import CASE_REPORT_OUTPUT_FOLDER
from ESP.settings import CASE_REPORT_TEMPLATE
from ESP.settings import CASE_REPORT_FILENAME_FORMAT
from ESP.settings import FAKE_PATIENT_MRN
from ESP.settings import FAKE_PATIENT_SURNAME


import optparse
import sys
import pprint
import os
import cStringIO as StringIO
import datetime
import re
from optparse import Values

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template.loader import get_template
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.nodis import defs
from ESP.nodis.models import Condition
from ESP.nodis.models import Case
from ESP.nodis.models import STATUS_CHOICES



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
INSTITUTION.name = 'HVMA'
INSTITUTION.clia = '22D0666230'
INSTITUTION.last_name = 'Klompas'
INSTITUTION.first_name = 'Michael'
INSTITUTION.address1 = '133 Brookline Avenue'
INSTITUTION.address2 = None
INSTITUTION.city = 'Boston'
INSTITUTION.state = 'MA'
INSTITUTION.zip = '02215'
INSTITUTION.country = 'USA'
INSTITUTION.email = 'MKLOMPAS@PARTNERS.ORG'
INSTITUTION.area_code = '617'
INSTITUTION.tel = '5099991'
INSTITUTION.tel_ext = None

APP_NAME = 'ESPv2'
SENDING_FACILITY = 'Test'
COMMENTS = '' # What goes in comments?



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
#--- Core
#
#===============================================================================

import time
import datetime
import random
import string
import pprint

from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.static.models import Icd9
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.hef.models import Event
from ESP.nodis.models import Case
from ESP.nodis.models import Condition as ConditionModel
from ESP.nodis.defs import *
from ESP.utils.utils import log
from ESP.utils.utils import log_query

from django.contrib.auth import REDIRECT_FIELD_NAME
from xml.dom.minidom import Document


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
    
    def __init__(self, doc=None, institutionName='HVMA', nmessages = None):
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
           'BLACK':'B',
           'OTHER':'O',
           'HISPANIC': 'W',
           'INDIAN':'I',
           'ASIAN':'A',
           'NAT AMERICAN':'I',
           'NATIVE HAWAI':'P',
           'ALASKAN':'I',
           }
        self.nmessages = nmessages
        self.timestamp = isoTime() # will return time now
        self.batchDoc = Document() # create a dom root 
        self.casesDoc = Document() # create a dom root for all the cases
        self.casesTopLevel = self.casesDoc.createElement("rossfoo") # this is a placeholder which is removed at rendering
        self.casesDoc.appendChild(self.casesTopLevel)
        
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
    def addCase(self, case):
        """Workhorse - maps cases into an xml document containing hl7
        should pass a mapping dict for each case here
        the obx records are all the case details so
        we need to iterate over the pointers stored in each case to make the
        appropriate segments
        """
        patient = case.patient
        oru = self.casesDoc.createElement('ORU_R01')
        self.casesTopLevel.appendChild(oru)
        mhs = self.makeMSH(segcontents=None,processingFlag='T') # testing!
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
        rxobjs = case.reportable_prescriptions.order_by('order_num')
        treatclis = set( case.reportable_prescriptions.values_list('provider', flat=True) )
        for cli in treatclis:
            nkindx=3
            pcp = Provider.objects.get(pk=cli)
            p = self.makePCP(pcp=pcp, addressType='O',NKindx=nkindx,NK13='TC')
            nkindx=nkindx+1
            orus2.appendChild(p)
        ##Clinical information
        lxobjs = case.reportable_labs.order_by('order_num')
        orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
        orus.appendChild(orcs)
        icd9_codes = Icd9.objects.filter(encounter__events__case=case)
        # Would the line below be a better way to do the line above?
        #icd9_codes = case.reportable_icd9s
        self.addCaseOBR(condition=case.condition, icd9=icd9_codes, orcs=orcs, gender=case.patient.gender)
        if rxobjs:
            rx=rxobjs[0]
        else:
            rx = None
        if len(lxobjs):
            lx =lxobjs[0]
        else:
            lx = None
        self.addCaseOBX(demog=patient, orcs=orcs, icd9=icd9_codes, lx=lx, rx=rx,
            encounters=case.reportable_encounters, condition=case.condition, casenote=case.notes,
            caseid=case.pk)
        totallxs = list(lxobjs)
        ##need check if any Gonorrhea test for Chlamydia
        if case.condition == 'chlamydia':
            genorlxs =self.getOtherLxs('gonorrhea', patient, lx)
            totallxs = totallxs + list(genorlxs)
        elif case.condition == 'gonorrhea':
            genorlxs =self.getOtherLxs('chlamydia', patient, lx)
            totallxs = totallxs + list(genorlxs)
        cleanlxids = self.removeDuplicateLx(totallxs)
        totallxs = LabResult.objects.filter(pk__in=cleanlxids).order_by('order_num')
        self.addLXOBX(lxRecList=totallxs, orus=orus,condition=case.condition)
        self.addRXOBX(rxRecList=rxobjs, orus=orus) # do same for dr
        return [i.id for i in totallxs]

    def removeDuplicateLx(self, lxobjs):
        """we have a nasty problem with data reloaded as we built the system
        and when the data feed is broken
        """
        lxdict={}
        for lxobj in lxobjs:
            lxkey = (lxobj.order_num, lxobj.native_code, lxobj.date, lxobj.result_string, lxobj.result_date)
            if not lxdict.has_key(lxkey):
                lxdict[lxkey]=lxobj.id
        return lxdict.values() # list of unique lx ids
                                                                                
    def getOtherLxs(self, cond,demog,lxids):
        returnlxs=[]
        # NOTE: Do we really want lab results from all of this patient's cases
        # of this condition, rather than lab results from only this particular
        # case?
        thiscases = Case.objects.filter(patient=demog,condition=cond)
        cases = Case.objects.filter(patient=demog, condition=cond)
        all_case_labs = LabResult.objects.filter(events__case__in=cases)
        if not all_case_labs:
            return returnlxs
        # What kind of exception are we expecting here??
        try:
            baselxs = LabResult.objects.filter(id__in=lxids).order_by('result_date')
            ####get lastest Lx record
            maxrec=baselxs[len(baselxs)-1].result_date
            baselxs = LabResult.objects.filter(id__in=lxids).order_by('date')
            minrec=baselxs[0].date
        except:
            return all_case_labs
        if maxrec and minrec:
            try:
                maxdate = datetime.date(int(maxrec[:4]),int(maxrec[4:6]),int(maxrec[6:8]))+datetime.timedelta(30)
                mindate = datetime.date(int(minrec[:4]),int(minrec[4:6]),int(minrec[6:8]))-datetime.timedelta(30)
                for onelx in all_case_labs:
                    thisd = onelx.result_date
                    if thisd:
                        thisd = datetime.date(int(thisd[:4]),int(thisd[4:6]),int(thisd[6:8]))
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
        self.addSimple(pid7,demog.date_of_birth.strftime(DATE_FORMAT),'TS.1')          
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
            self.addSimple(pid13,demog.areacode,'XTN.6')
            self.addSimple(pid13,demog.tel,'XTN.7')
            if demog.tel_ext:
                self.addSimple(pid13,demog.tel_ext,'XTN.8')
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
        contact = self.makeContact(email,pcp.area_code,pcp.telephone,ext,outerElement)
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
        country='USA'
        addressType='O'
        address = self.makeAddress(INSTITUTION.address1, INSTITUTION.address2, INSTITUTION.city,
            INSTITUTION.state, INSTITUTION.zip, INSTITUTION.country ,outerElement, addressType)
        section.appendChild(address)
        outerElement='NK1.5'
        email=INSTITUTION.email
        contact = self.makeContact(email, INSTITUTION.area_code, INSTITUTION.tel, INSTITUTION.tel_ext, outerElement)
        if contact <> None:
            section.appendChild(contact)
        return section

    def addCaseOBR(self, condition=None, icd9=[], orcs=None, gender=''):
        """
            </OBR.31> is used to name the notifiable condition"""
        obr = self.casesDoc.createElement('OBR')
        self.addSimple(obr,'1','OBR.1')
        obr4 = self.casesDoc.createElement('OBR.4')
        self.addSimple(obr4,'Additional Patient Demographics','CE.2')
        obr.appendChild(obr4)
        fakeicd9={'PID':'614.9',
                  'CHLAMYDIA':{'F':'099.53','M':'099.41','U':'099.41', '':'099.41'},
                  'GONORRHEA':'098.0',
                  'ACUTE HEPATITIS A':'070.10',
                  'ACUTE HEPATITIS B':'070.30'
                  }
        if not icd9 and condition.upper() in fakeicd9.keys():
            gender = gender.upper()
            icd9values = fakeicd9[condition.upper()]
            if type(icd9values)==type(''): ##a string
                icd9=[icd9values]
            else:
                try:
                    icd9=[icd9values[gender]]
                except: ##all other gender
                    icd9 = ['099.41']
        for i in icd9:
            obr31 = self.casesDoc.createElement('OBR.31') 
            self.addSimple(obr31,i,'CE.1')   
            self.addSimple(obr31,condition,'CE.2')
            self.addSimple(obr31,'I9','CE.3')
            obr.appendChild(obr31)
        orcs.appendChild(obr)

    def getPregnancyStatus(self, caseid):
        ##Email on 8/22/2007: Report patient as being pregnant if pregnancy flag active anytime between (test order date) and (test result date + 30 days inclusive).
        obx5='261665006' ##unknown
        #
        #
        case = Case.objects.get(pk=caseid)
        first_event = case.events.order_by('date')[0]
        start_date = first_event.date
        end_date = start_date + datetime.timedelta(days=30)
        preg_encounters = Encounter.objects.filter(patient=case.patient, pregnancy_status='Y', date__gte=start_date,
            date__lte=end_date)
        if not preg_encounters:
            return ('261665006', None)
        edc_encs = preg_encounters.filter(edc__isnull=False).order_by('date')
        if not edc_encs:
            raise IncompleteCaseData('Patient %s is pregnant during case window, but has no EDC.')
        edc = edc_encs[0].edc
        return ('77386006', edc)

    def addCaseOBX(self, demog=None, orcs=None,icd9=None,lx=None, rx=None, encounters=[], condition=None, casenote='',caseid=''):
        """
        """
        indx=1
        if not demog.date_of_birth:
            raise IncompleteCaseData('No date of birth for patient %s' %  demog)
        dur = (datetime.date.today() - demog.date_of_birth).days
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'NM')],obx3=[('CE.4','21612-7')],obx5=[('',int(dur/365))],nte=casenote)
        orcs.appendChild(obx)
        indx += 1
        ##pregnancy status
        (obx5, edc) = self.getPregnancyStatus(caseid)
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','11449-6'),('CE.5','PREGNANCY STATUS')],obx5=[('CE.4',obx5)])
        orcs.appendChild(obx)
        indx += 1
        ##EDC
        if edc:
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'TS')],obx3=[('CE.4','NA-8'),('CE.5','EXPECTED DATE OF CONFINEMENT')],
                                obx5=[('TS.1',edc.strftime(DATE_FORMAT))])
            indx += 1
            orcs.appendChild(obx)
            pregdur = edc - datetime.date.today()
            pregweeks = 40 - int(pregdur.days/7)
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'NM')],obx3=[('CE.4','NA-12')],
                                obx5=[('',pregweeks)])
            indx += 1
            orcs.appendChild(obx)
        ##NA_TRMT
        if rx and lx:
            rxdate = rx.date
            lxorderd = lx.date
            dur = rxdate - lxorderd
        else:
            dur=None
            rxdate =None
        if dur and dur.days < 15:
            trmt = '373066001' #YES
        else:
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
            lxresd=lx.result_date
        sym='373067005' #NO
        temperature=0
        for enc in encounters:
            try:
                temperature = enc.temperature
            except:
                temperature=0
            if lxresd:
                dur = enc.date - lxresd
            else:
                dur = datetime.timedelta(days=0)
            if abs(dur.days)<15 or temperature>100.4:
                sym='373066001' #YES
                break
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','NA-5')], obx5=[('CE.4',sym)])
        indx += 1
        orcs.appendChild(obx)
        if condition.upper()  in ('CHLAMYDIA', 'GONORRHEA'):
            for i in icd9:
                obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'ST')],obx3=[('CE.4','10187-3')], obx5=[('',i)])
                indx += 1
                orcs.appendChild(obx)
            if temperature>100.4:
                obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'ST')],obx3=[('CE.4','10187-3')], obx5=[('','fever')])
                indx += 1
                orcs.appendChild(obx)

    def addLXOBX(self,lxRecList=[],orus=None,condition=None):
        if not lxRecList: return
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
            orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
            orus.appendChild(orcs)
            orc = self.makeORC(lxRec.provider)
            orcs.appendChild(orc)
            obr = self.casesDoc.createElement('OBR') # need a special lx OBR
            self.addSimple(obr,n,'OBR.1')
            n+=1
            obr3 = self.casesDoc.createElement('OBR.3')
            self.addSimple(obr3,lxRec.order_num,'EI.1')
            obr.appendChild(obr3)
            obr4 = self.casesDoc.createElement('OBR.4')
            self.addSimple(obr4,lxRec.output_or_native_code,'CE.4') 
            self.addSimple(obr4,'L','CE.6') # loinc code
            obr.appendChild(obr4)
            obr7 = self.casesDoc.createElement('OBR.7')
            obr.appendChild(obr7)
            self.addSimple(obr7,lxRec.date.strftime(DATE_FORMAT),'TS.1') # lx date
            obr15 = self.casesDoc.createElement('OBR.15') # noise - unknown specimen source. Eeessh
            sps = self.casesDoc.createElement('SPS.1')
            self.addSimple(sps,'261665006','CE.4') ##unknown = 261665006 (local code)
            self.addSimple(sps,'L','CE.6') # loinc code
            obr15.appendChild(sps)
            obr.appendChild(obr15)
            if lxRec.status:
                status='F'
            else:
                status='P'
            self.addSimple(obr,status,'OBR.25') # result status
            orcs.appendChild(obr)
            # now add the obx records needed to describe dose, frequency and duration
            lxTS = lxRec.date
            lxRange = 'Low: %s - High: %s' % (lxRec.ref_low_string, lxRec.ref_high_string)
            #snomed=ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc)[0].CondiSNMDPosi
            snomed=self.getSNOMED(lxRec,condition)
            if lxRec.result_string:
                res = lxRec.result_string
            else:
                res = ''
            if not snomed: ##like ALT/AST
                #ALT/AST much be number
                obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'NM')],obx3=[('CE.4',lxRec.output_or_native_code),('CE.6','L')],
                                   obx5=[('', res.split()[0])], obx7=[('',lxRange)],obx14=[('TS.1',lxTS.strftime(DATE_FORMAT))], obx15=[('CE.1','22D0076229'), ('CE.3','CLIA')])
            else:
                obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'CE')],obx3=[('CE.4',lxRec.output_or_native_code),('CE.6','L')],
                               obx5=[('CE.4',snomed)],  obx7=[('',lxRange)],obx14=[('TS.1',lxTS.strftime(DATE_FORMAT))], obx15=[('CE.1','22D0076229'), ('CE.3','CLIA')])
            orcs.appendChild(obx1)
          
    def getSNOMED(self, lxRec,condition):
        # NOTE: See "PORTING NOTE" above.
        snomedposi = lxRec.snomed_pos
        snomednega = lxRec.snomed_neg
        snomedinter = lxRec.snomed_ind
        if snomedposi=='' and snomednega=='': ##like ALT/AST
            return ''
        #
        # FIXME: It can't be good to have a hard-coded, LOINC-based table here.
        #
        loinc_posires_map = {'5009-6':160,
                             '16934-2':100,
                             '34704-7':50}
        if lxRec.output_or_native_code in loinc_posires_map.keys():###('5009-6','16934-2'):
            try:
                if lxRec.result_float < loinc_posires_map[lxRec.output_or_native_code]:
                    return snomednega
                else:
                    return snomedposi
            except:
                if string.find(lxRec.result_string, '>')!=-1:
                    return snomedposi
                else:
                    return snomednega
        if snomednega=='' and snomedinter=='':
            return snomedposi
        if lxRec.result_string:
            testsult = lxRec.result_string.upper()[:5]
        else:
            testsult = '' # Must be string for elif below
        if testsult in ('BORDE'): ###BORDERLINE, use SNOMED for equivocal
            return snomedinter
        elif testsult not in ('REACT','POSIT','DETEC'): ##USE negative
            return snomednega
        else:
            return snomedposi
        
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
            self.addSimple(obr3,rxRec.order_num,'EI.1') 
            obr.appendChild(obr3)
            obr4 = self.casesDoc.createElement('OBR.4')
            ########Added Jan,2009 to fix EMR Mappign question in order to
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
            rxTS = rxRec.date
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
        contact = self.makeContact(email, pcp.area_code, pcp.telephone, ext, outerElement)
        if contact <> None:
            orc.appendChild(contact)
        orc21 = self.casesDoc.createElement('ORC.21')
        self.addSimple(orc21, INSTITUTION.name, 'XON.1')
        orc.appendChild(orc21)
        outerElement='ORC.22'
        country='USA'
        addressType=None
        address = self.makeAddress(INSTITUTION.address1, INSTITUTION.address2, INSTITUTION.city,
            INSTITUTION.state, INSTITUTION.zip, country ,outerElement, addressType)
        orc.appendChild(address)
        outerElement='ORC.23'
        contact = self.makeContact(None, INSTITUTION.area_code, INSTITUTION.tel, INSTITUTION.tel_ext, outerElement)
        if contact <> None:
            orc.appendChild(contact)
        outerElement='ORC.24'
        address = self.makeAddress(INSTITUTION.address1, INSTITUTION.address2, INSTITUTION.city, INSTITUTION.state,
            INSTITUTION.zip, country ,outerElement, addressType)
        orc.appendChild(address)
        return orc

    def makeMSH(self, segcontents = None, processingFlag='P', versionFlag='2.3.1'):
        """MSH segment
        """
        # Create the elements
        section = self.casesDoc.createElement("MSH")
        self.addSimple(section,'|','MSH.1')
        self.addSimple(section,u'^~\&','MSH.2')
        e = self.casesDoc.createElement('MSH.4')
        for (element,ename) in [(INSTITUTION.name, 'HD.1'),(INSTITUTION.clia, 'HD.2'), ('CLIA','HD.3')]:
            if element <> '':
                self.addSimple(e,element,ename)
        section.appendChild(e)
        e = self.casesDoc.createElement('MSH.5')         
        self.addSimple(e,'MDPH-ELR','HD.1')
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
        lastName = lastName.strip()
        if not lastName: lastName='Unknown'
        firstName =firstName.strip()
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
                 
    def makeAddress(self, address, addressOther, city, state, zip, country ,outerElement, addressType):
        """reusable component = xad.1-7 pass the field names
        from the right record!
        """
        outer = self.casesDoc.createElement(outerElement)
        worklist = [(address,'XAD.1'),(addressOther,'XAD.2'),(city,'XAD.3'),(state,'XAD.4'),
                    (zip,'XAD.5'),(country,'XAD.6')]
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
        make_option('-o', action='store', metavar='FOLDER', dest='output_folder',
            default=CASE_REPORT_OUTPUT_FOLDER, help='Output case report file(s) to FOLDER'),
        make_option('-t', action='store', metavar='TEMPLATE', dest='template', 
            default=CASE_REPORT_TEMPLATE, help='Use TEMPLATE to generate HL7 messages'),
        make_option('-f', action='store', dest='format', metavar='FORMAT', default=CASE_REPORT_FILENAME_FORMAT,
            help='Create file names using FORMAT.  Default: %s' % CASE_REPORT_FILENAME_FORMAT),
        make_option('--mdph', action='store_true', dest='mdph', default=False,
            help='Export cases in HL7v3 dialect required by Mass Dept of Public Health'),
        make_option('--stdout', action='store_true', dest='stdout', default=False,
            help='Print output to STDOUT (no files created)'),
        make_option('--case', action='store', dest='case_id', metavar='ID', 
            help='Export a single case with specified case ID'),
        make_option('--individual', action='store_false', dest='one_file',
            default=False, help='Export each cases to an individual file (default)'),
        make_option('--one-file', action='store_true', dest='one_file',
            default=False, help='Export all cases to one file.  Always true for MDPH reports.'),
        make_option('--status', action='store', dest='status', default='Q',
            help='Export only cases with this status ("Q" by default)'),
        make_option('--no-sent-status', action='store_false', dest='sent_status', default=True,
            help='Do NOT set case status to "S" after export'),
        make_option('--sample', action='store', dest='sample', metavar='NUM', type='int', 
            help='Report only first NUM cases matching criteria; do NOT set status to sent'),
        )
    
    def handle(self, *args, **options):
        report_conditions = [] # Names of conditions for which we will export cases
        self.timestamp = datetime.datetime.now().strftime('%Y-%b-%d-%H:%M:%s')
        #
        # Parse command line for options
        #
        all_conditions = Condition.list_all_condition_names()
        all_conditions.sort()
        case_id = options['case_id']
        sample = options['sample']
        format = options['format']
        status = options['status']
        one_file = options['one_file']
        stdout = options['stdout']
        sent_status = options['sent_status']
        output_folder = options['output_folder']
        template = options['template']
        mdph = options['mdph']
        #
        # Sanity check options
        #
        for a in args:
            if a.lower() == 'all':
                report_conditions = all_conditions
                break
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
        log.debug('conditions: %s' % report_conditions)
        valid_status_choices = [item[0] for item in STATUS_CHOICES]
        if status not in valid_status_choices:
                print >> sys.stderr
                print >> sys.stderr, 'Unrecognized status: "%s".  Aborting.' % status
                print >> sys.stderr
                print >> sys.stderr, 'Valid status choices are:'
                for stat in valid_status_choices:
                    print >> sys.stderr, '    %s' % stat
                sys.exit(102)
        log.debug('status: %s' % status)
        #
        # Generate case query
        #
        if case_id:
            q_obj = Q(pk__exact=case_id)
        else:
            q_obj = Q(condition__in=report_conditions)
            q_obj = q_obj & Q(status=status)
        if FAKE_PATIENT_MRN:
            q_obj &= ~Q(patient__mrn__iregex=FAKE_PATIENT_MRN)
        if FAKE_PATIENT_SURNAME:
            q_obj &= ~Q(patient__last_name__iregex=FAKE_PATIENT_SURNAME)
        cases = Case.objects.filter(q_obj).order_by('pk')
        if not cases:
            print 
            print 'No cases found matching your specifications.  No output generated.'
            print
            sys.exit(11)
        log_query('Filtered cases', cases)
        if sample: # Report only a single, random sample case
            cases = cases[0:sample]
        if options['mdph']:
            self.mdph(options, cases)
        else:
            self.use_template(options, cases)
    
    def use_template(self, options, cases):
        '''
        Generate report messages based on a template
        '''
        one_file = options['one_file']
        stdout = options['stdout']
        sent_status = options['sent_status']
        if options['sample']: # '--sample' implies '--no-sent-status'
            sent_status = False
        output_folder = options['output_folder']
        template = options['template']
        format = options['format']
        if one_file:
            output_file = StringIO.StringIO()
        template_name = os.path.join('nodis', 'report', template)
        try:
            get_template(template_name)
        except TemplateDoesNotExist:
            print >> sys.stderr
            print >> sys.stderr, 'Unrecognized template name: "%s".  Aborting.' % template
            print >> sys.stderr
            sys.exit(103)
        filename_values = { 
            # Used to populate file name template -- serial is updated below
            'serial_number': 0,
            'timestamp': self.timestamp,
            }
        #
        # Build message string
        #
        serial_number = 0 # Serial number of case reported for this timestamp
        for case in cases:
            serial_number += 1 # Increment serial number for this case
            matched_labs = []
            matched_encounters = []
            matched_prescriptions = []
            matched_immunizations = []
            for event in case.events.all():
                content = event.content_object
                if isinstance(content, LabResult):
                    matched_labs.append(content)
                if isinstance(content, Encounter):
                    matched_encounters.append(content)
                if isinstance(content, Prescription):
                    matched_prescriptions.append(content)
                if isinstance(content, Immunization):
                    matched_immunizations.append(content)
            labs = case.lab_results.all()
            # Case.events is blank=False, so this shouldn't ever thrown an index error.
            provider = case.events.all().order_by('date')[0].content_object.provider
            values = {
                'case': case,
                'patient': case.patient,
                'provider': provider,
                'matched_labs': matched_labs,
                'matched_encounters': matched_encounters,
                'matched_prescriptions': matched_prescriptions,
                'matched_immunizations': matched_immunizations,
                #'all_labs': labs,
                #'all_encounters': case.encounters.all(),
                #'all_prescriptions': case.medications.all(),
                #'all_immunizations': case.immunizations.all(),
                'serial_number': serial_number,
                }
            log.debug('values for template: \n%s' % pprint.pformat(values))
            case_report = render_to_string(template_name, values)
            # Remove blank lines -- allows us to have neater templates
            case_report = re.sub("\n\s*\n*", "\n", case_report)
            #
            # Report message
            #
            log.debug('Message to report:\n%s' % case_report)
            if stdout: # Print case reports to STDOUT
                log.debug('Printing message to stdout')
                print case_report
            elif one_file: # All reports in one big file
                log.debug('Adding case #%s report to single output file' % case.pk)
                output_file.write(case_report)
                pass
            else: # Produce an individual file for every case report [default]
                filename = format % filename_values
                filepath = os.path.join(output_folder, filename)
                file = open(filepath, 'w')
                file.write(case_report)
                file.close()
                log.info('Wrote case #%s report to file: %s' % (case.pk, filepath))
            if sent_status:
                case.status = 'S'
                case.save()
                log.debug("Set status to 'S' for case #%s" % case.pk)
        if one_file:
            filename = format % filename_values
            filepath = os.path.join(output_folder, filename)
            file = open(filepath, 'w')
            file.write(output_file.getvalue())
            file.close()
            # serial_number is equal to the number of cases reported
            log.info('Wrote single report for all %s cases to file: %s' % (serial_number, filepath))
    
    def mdph(self, options, cases):
        options = Values(options)
        batch = hl7Batch(nmessages=len(cases))
        for case in cases:
            log.debug('Generating HL7 for %s' % case)
            try:
                batch.addCase(case)
            except IncompleteCaseData, e:
                log.critical('Could not generate HL7 message for case # %s !' % case)
                log.critical('    %s' % e)
        case_report = batch.renderBatch()
        if options.stdout:
            print case_report
        else:
            values = { 
                # Used to populate file name template -- serial is updated below
                'serial_number': 0,
                'timestamp': self.timestamp,
                }
            filename = options.format % values
            filepath = os.path.join(options.output_folder, filename)
            file = open(filepath, 'w')
            file.write(case_report)
            file.close()
            log.info('Wrote case report to file: %s' % filepath)
