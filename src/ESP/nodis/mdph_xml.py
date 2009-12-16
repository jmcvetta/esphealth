'''
                                  ESP Health
                         Notifiable Diseases Framework
                              MDPH XML Generator


@author: Ross Lazarus <ross.lazarus@gmail.com>
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2006 - 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


# hl7 generating xml code
# for ESP
# ross lazarus me fecit August 4 2006
# It's not pretty, but it seems to work
# hl7 is truly a pain to work with
# this is completely specific to the MaDPH ELR
# based somewhat on the cdc ELR specification but
# in xml
# with an enigma wrapped in a riddle - the cases
# are wrapped in xml but transmitted as cdata inside
# a batch header
# go figure
# there are some small abstractions here, but the code
# is hardly reusable
# not really worth generalising imho since we hope we never
# have to write this cruft again.
# hl7 is a braindead way to get an ontology and data moved around
# there are so many arbitrary decisions that have to be catered to
# and the data types are all stupid codes instead of helpful codes 
# python dom makes it tolerable but, it's horrible complex
# very unpleasant way to express prescription details
# imposed by cost of asking vendor to change anything !! :)
# ours is but to do or die I guess.


#===============================================================================
#
#--- Configuration
#
#===============================================================================

VERSION = '2.3.1'

# Information about reporting institution.  This info should be made configurable 
# in reference localsettings.py.
class Foo(): pass
INSTITUTION = Foo()
INSTITUTION.name = 'HVMA'
INSTITUTION.clia = '22D0666230'
INSTITUTION.last_name = 'Institution First Name'
INSTITUTION.first_name = 'Institution Last Name'
INSTITUTION.address1 = 'Institution Address 1'
INSTITUTION.address2 = 'Institution Address 2'
INSTITUTION.city = 'Institution City'
INSTITUTION.state = 'Institution State'
INSTITUTION.zip = 'Institution Zip'
INSTITUTION.country = 'Institution Country'
INSTITUTION.email = 'Institution Email'
INSTITUTION.area_code = 'Institution Area Code'
INSTITUTION.tel = 'Institution Telephone Number'
INSTITUTION.tel_ext = 'Institution Telephone Extension'

APP_NAME = 'ESPv2'
SENDING_FACILITY = 'HVMA'



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

from ESP.static.models import Icd9
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.hef.models import Event
from ESP.nodis.models import Case
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


############################
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
           '': 'U'}
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
        rxobjs = case.prescriptions.order_by('order_num')
        treatclis = case.prescriptions.values_list('provider', flat=True).distinct()
        for cli in treatclis:
            nkindx=3
            p = self.makePCP(pcp=cli, addressType='O',NKindx=nkindx,NK13='TC')
            nkindx=nkindx+1
            orus2.appendChild(p)
        ##Clinical information
        lxobjs = case.lab_results.order_by('order_num')
        orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
        orus.appendChild(orcs)
        icd9_codes = Icd9.objects.filter(encounter__events__case=case)
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
            encs=case.encounters, rule=case.condition, casenote=case.notes,
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

    ###################################
    ###################################
    def removeDuplicateLx(self, lxobjs):
        """we have a nasty problem with data reloaded as we built the system
        and when the data feed is broken
        """
        lxdict={}
        for lxobj in lxobjs:
            lxkey = (lxobj.LxOrder_Id_Num, lxobj.LxTest_Code_CPT,lxobj.LxComponent,lxobj.LxOrderDate,lxobj.LxTest_results,lxobj.LxDate_of_result)
            if not lxdict.has_key(lxkey):
                lxdict[lxkey]=lxobj.id
                
        return lxdict.values() # list of unique lx ids
                                                                                
    ###################################
    def getOtherLxs(self, cond,demog,lxids):
        returnlxs=[]
        thiscases = Case.objects.filter(patient=demog,condition=cond)
        curLxids = [c.pk for c in thiscases]
        if not curLxids:
            return returnlxs

        
        curLxidlist = ','.join(curLxids).split(',')
        try:
            baselxs = LabResult.objects.filter(id__in=lxids).order_by('result_date')
            ####get lastest Lx record
            maxrec=baselxs[len(baselxs)-1].result_date
            baselxs = LabResult.objects.filter(id__in=lxids).order_by('date')
            minrec=baselxs[0].date
        except:
            return  LabResult.objects.filter(id__in=curLxidlist)
        
        if maxrec and minrec:
            try:
                maxdate = datetime.date(int(maxrec[:4]),int(maxrec[4:6]),int(maxrec[6:8]))+datetime.timedelta(30)
                mindate = datetime.date(int(minrec[:4]),int(minrec[4:6]),int(minrec[6:8]))-datetime.timedelta(30)
                
                for onelid in curLxidlist:
                    print onelid
                    onelx = LabResult.objects.get(id=onelid)
                    thisd = onelx.result_date
                    if thisd:
                        thisd = datetime.date(int(thisd[:4]),int(thisd[4:6]),int(thisd[6:8]))
                        
                    if not thisd or (thisd>=mindate and thisd<=maxdate):
                        returnlxs.append(onelx)

                return returnlxs
            except:
                pass

        return  LabResult.objects.filter(id__in=curLxidlist)

        
        
    ############################################
    ############################################
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
        self.addSimple(pid7,demog.date_of_birth,'TS.1')          
        section.appendChild(pid7)
        if demog.gender:
            self.addSimple(section,demog.gender,'PID.8')


        try:
            race = self.racedir[demog.race.upper()]
        except:
            race=''
        if race:
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

    ##############################################
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

    ##############################################
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


    
    ##################################################
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


    ############################################
    def getDurtion(self, day1, day2):
        print 'day1: %s' % day1
        print 'day2: %s' % day2
        dur =datetime.date(int(day2[:4]),int(day2[4:6]), int(day2[6:8]))-datetime.date(int(day1[:4]),int(day1[4:6]), int(day1[6:8]))
        return dur.days


    ###################################
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
        return ('77386006', edc.strftime('%Y%m%d'))


    
    #############################################
    def addCaseOBX(self, demog=None, orcs=None,icd9=None,lx=None, rx=None,encs=[],rule=None,casenote='',caseid=''):
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
                                obx5=[('TS.1',edc)])
            indx += 1
            orcs.appendChild(obx)
            pregdur =datetime.date(int(edc[:4]),int(edc[4:6]), int(edc[6:8]))-datetime.date(int(c[:4]),int(c[4:6]), int(c[6:8]))
            pregweeks = 40 - int(pregdur.days/7)
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'NM')],obx3=[('CE.4','NA-12')],
                                obx5=[('',pregweeks)])
            indx += 1
            orcs.appendChild(obx)
        ##NA_TRMT
        if rx and lx:
            rxdate = rx.date
            lxorderd = lx.date
            dur = self.getDurtion(lxorderd,rxdate)
        else:
            dur=None
            rxdate =None
        if dur and dur<15:
            trmt = '373066001' #YES
        else:
            trmt = '373067005' #NO
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','NA-TRMT')], obx5=[('CE.4',trmt)])
        indx += 1
        orcs.appendChild(obx)
        ##NA_TRMTDT
        if rxdate:
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'TS')],obx3=[('CE.4','NA-TRMTDT')], obx5=[('TS.1',rxdate)])
            indx += 1
            orcs.appendChild(obx)
        ##Symptoms
        lxresd=None
        if lx:
            lxresd=lx.result_date
        sym='373067005' #NO
        temperature=0
        for encid in encs:
            enc = Encounter.objects.filter(id__exact=encid)[0]
            try:
                temperature = enc.temperature
            except:
                temperature=0
            if lxresd:
                dur = self.getDurtion(lxresd,enc.date)
            else:
                dur = 0
            if abs(dur)<15 or temperature>100.4:
                sym='373066001' #YES
                break
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','NA-5')], obx5=[('CE.4',sym)])
        indx += 1
        orcs.appendChild(obx)
        if rule.ruleName.upper()  in ('CHLAMYDIA', 'GONORRHEA'):
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
            needsend =ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc,CondiRule=condition)[0].CondiSend
            if needsend==0: ##no need send
                continue
            
            orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
            orus.appendChild(orcs)
            orc = self.makeORC(lxRec.LxOrdering_Provider)
            orcs.appendChild(orc)
            
            obr = self.casesDoc.createElement('OBR') # need a special lx OBR
            self.addSimple(obr,n,'OBR.1')
            n+=1
    
            obr3 = self.casesDoc.createElement('OBR.3')
      
            self.addSimple(obr3,lxRec.LxOrder_Id_Num,'EI.1')
            obr.appendChild(obr3)

            obr4 = self.casesDoc.createElement('OBR.4')
            self.addSimple(obr4,lxRec.LxLoinc,'CE.4') 
            self.addSimple(obr4,'L','CE.6') # loinc code
            obr.appendChild(obr4)
            
            obr7 = self.casesDoc.createElement('OBR.7')
            obr.appendChild(obr7)
            self.addSimple(obr7,lxRec.LxOrderDate,'TS.1') # lx date
    
            obr15 = self.casesDoc.createElement('OBR.15') # noise - unknown specimen source. Eeessh
            sps = self.casesDoc.createElement('SPS.1')
            self.addSimple(sps,'261665006','CE.4') ##unknown = 261665006 (local code)
            self.addSimple(sps,'L','CE.6') # loinc code
            obr15.appendChild(sps)
            obr.appendChild(obr15)

            if lxRec.LxTest_status:  status='F'
            else: status='P'
            self.addSimple(obr,status,'OBR.25') # result status
  
            orcs.appendChild(obr)

            # now add the obx records needed to describe dose, frequency and duration
            lxTS = lxRec.LxOrderDate
            lxRange = 'Low:' + lxRec.LxReference_Low+' - High: '+lxRec.LxReference_High


            #snomed=ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc)[0].CondiSNMDPosi
            snomed=self.getSNOMED(lxRec,condition)

            if snomed=='': ##like ALT/AST
                #ALT/AST much be number
                obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'NM')],obx3=[('CE.4',lxRec.LxLoinc),('CE.6','L')],
                                   obx5=[('',lxRec.LxTest_results.split()[0])], obx7=[('',lxRange)],obx14=[('TS.1',lxTS)], obx15=[('CE.1','22D0076229'), ('CE.3','CLIA')])
            else:
                obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'CE')],obx3=[('CE.4',lxRec.LxLoinc),('CE.6','L')],
                               obx5=[('CE.4',snomed)],  obx7=[('',lxRange)],obx14=[('TS.1',lxTS)], obx15=[('CE.1','22D0076229'), ('CE.3','CLIA')])
        
            
            orcs.appendChild(obx1)
          

    ##################################
    def getSNOMED(self, lxRec,condition):
        # NOTE: See "PORTING NOTE" above.
        snomedposi =ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc,CondiRule=condition)[0].CondiSNMDPosi
        snomednega = ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc,CondiRule=condition)[0].CondiSNMDNega
        snomedinter = ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc,CondiRule=condition)[0].CondiSNMDInde
        
        if snomedposi=='' and snomednega=='': ##like ALT/AST
            return ''

        loinc_posires_map = {'5009-6':160,
                             '16934-2':100,
                             '34704-7':50}
        
        if lxRec.LxLoinc in loinc_posires_map.keys():###('5009-6','16934-2'):
            try:
                if float(lxRec.LxTest_results) <loinc_posires_map[lxRec.LxLoinc]:
                    return snomednega
                else:
                    return snomedposi
            except:
                if string.find(lxRec.LxTest_results, '>')!=-1:
                    return snomedposi
                else:
                    return snomednega
        
        if snomednega=='' and snomedinter=='':
            return snomedposi
        
        testsult = lxRec.result_string.upper()[:5]
        if testsult in ('BORDE'): ###BORDERLINE, use SNOMED for equivocal
            return snomedinter
        elif testsult not in ('REACT','POSIT','DETEC'): ##USE negative
            return snomednega
        else:
            return snomedposi
                                                        
        
    ##############################################                
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
            self.addSimple(obr7,rxRec.date,'TS.1') # rx date
            
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
                rxDur =datetime.date(int(rxRec.RxEndDate[:4]),int(rxRec.RxEndDate[4:6]), int(rxRec.RxEndDate[6:8]))  - datetime.date(int(rxRec.RxStartDate[:4]),int(rxRec.RxStartDate[4:6]), int(rxRec.RxStartDate[6:8]))
                rxDur = rxDur.days+1
           
            rxTS = rxRec.date
            #<OBX.5>NDC_Number; Drug Name; Dose; Frequency; Duration</OBX.5>
            drugstr = '%s;%s;%s;%s;%s day(s)' % (rxRec.code, rxRec.name, rxRec.dose, rxRec.frequency, rxDur)
            obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'ST')],obx3=[('CE.4','NA-56')],
                               obx5=[('', drugstr)])

            orcs.appendChild(obx1)



    ###########################################
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
       
            
    
    ########################################    
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
        address = self.makeAddress(INSTITUTION.address1, INSTITUTION.address2, INSTITUTION.ciy,
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


    #########################    
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
 
    #################################
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

    ##################################         
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
        self.addHSimple(fhs,self.config.appName,'FHS.3') # file sending app
        self.addHSimple(fhs,self.config.sendingFac,'FHS.4')
        fhs2 = self.batchDoc.createElement('FHS.7')
        self.addHSimple(fhs2,self.timestamp,'TS.1')
        fhs.appendChild(fhs2)
        self.addHSimple(fhs,self.config.instComments,'FHS.11')
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


    ####################################
    ####################################
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
I  	American Indian or Alaska Native  	     	    	
A 	Asian 			
B 	Black or African-American 			
P 	Native Hawaiian or Other Pacific Islander 			
O 	Other 			
U 	Unknown 			
W 	White"""

def test():
    """test! used during development
    Won't work now as I've cut over to using django records
    """
    ncases = 1


    testDoc = hl7Batch(configDict = configDict, nmessages=ncases)
    for case in range(ncases):
        demog = Demog.objects.filter(id__exact=12930)[0]
        pcp = Provider.objects.filter(id__exact=402)[0]
        rule = Rule.objects.filter(id=1)[0]
        c =Case.objects.filter(id__exact=56)[0]
        ex = string.split(c.caseEncID,',') 
        rx = string.split(c.caseRxID,',')
        lx = string.split(c.caseLxID,',')
        caseicd9 = string.split(c.caseICD9,',')
        ex.remove('')
        rx.remove('')
        lx.remove('')
        
        testDoc.addCase(demog=demog,pcp=pcp,rule=rule, lx=lx, rx=rx,ex=ex,icd9=caseicd9,caseid = case.id)

       
    # Print our newly created XML
    s = testDoc.renderBatch()
    f = file('hl7Sample.hl7','w')
    f.write(s)
    f.close()
    print s


def main():
    cases = Case.objects.filter(condition='acute_hep_b')[0:10]
    batch = hl7Batch()
    for case in cases:
        log.debug('Generating HL7 for %s' % case)
        try:
            batch.addCase(case)
        except IncompleteCaseData, e:
            log.critical('Could not generate HL7 message for case # %s !')
            log.critical('    %s' % e)


if __name__ == "__main__":
    main()
        
    
