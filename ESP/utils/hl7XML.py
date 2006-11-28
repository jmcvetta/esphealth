# hl7 generating xml code
# for ESP
# ross lazarus me fecit August 4 2006
# It's not pretty, but it seems to work
# hl7 is truly a pain
# python dom makes it tolerable but, it's horrible complex
# very unpleasant way to express prescription details
# imposed by cost of asking vendor to change anything !! :)
# ours is but to do or die I guess.

from ESP.esp.models import *
##from django.contrib.auth.decorators import login_required, user_passes_test
##from ESP.settings import SITEROOT
##
##from django.contrib.auth.forms import AuthenticationForm
##from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
##from django import forms
##from django.contrib.auth.models import SESSION_KEY
##from django.contrib.sites.models import Site
from django.contrib.auth import REDIRECT_FIELD_NAME
from xml.dom.minidom import Document
import time,datetime,random





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
        self.nmessages = nmessages
        self.config = config.objects.filter(institution_name__exact=institutionName)[0]
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
    def addCase(self,demog=None,pcp=None,rule=None, rx=[],lx = [], ex=[],icd9=[]):
        """Workhorse - maps cases into an xml document containing hl7
        should pass a mapping dict for each case here
        the obx records are all the case details so
        we need to iterate over the pointers stored in each case to make the
        appropriate segments
        """
        
        oru = self.casesDoc.createElement('ORU_R01')

        self.casesTopLevel.appendChild(oru)
        mhs = self.makeMSH(segcontents=None,processingFlag='T') # testing!
        oru.appendChild(mhs)
        orus = self.casesDoc.createElement('ORU_R01.PIDPD1NK1NTEPV1PV2ORCOBRNTEOBXNTECTI_SUPPGRP')
        oru.appendChild(orus)

        orus2 = self.casesDoc.createElement('ORU_R01.PIDPD1NK1NTEPV1PV2_SUPPGRP')
        orus.appendChild(orus2)
        ##demograpgic
        pid = self.makePID(demog=demog, pcp=pcp)
        orus2.appendChild(pid)

        ##PCP       
        p = self.makePCP(pcp=pcp, addressType='O')
        orus2.appendChild(p)

        ##facility information 
        p = self.makeFacility()
        orus2.appendChild(p)

        ##Treating Clinician
        rxobjs=[]
        if rx:
            rxobjs = Rx.objects.filter(id__in = rx).order_by('RxOrder_Id_Num')
        treatclis=[]
        for rxobj in rxobjs:
            if rxobj.RxProvider not in treatclis:
                treatclis.append(rxobj.RxProvider)
        for cli in treatclis:
            nkindx=3
            p = self.makePCP(pcp=cli, addressType='O',NKindx=nkindx,NK13='TC')
            nkindx=nkindx+1
            orus2.appendChild(p)


        ##Clinical information
        lxobjs = []
        if lx:
            lxobjs = Lx.objects.filter(id__in=lx).order_by('LxOrder_Id_Num')
        orcs = self.casesDoc.createElement('ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP')
        orus.appendChild(orcs)
        self.addCaseOBR(rule=rule,icd9=icd9,orcs=orcs)

        if rxobjs:
            rx=rxobjs[0]
        else:
            rx = None
        self.addCaseOBX(demog=demog, orcs=orcs,icd9=icd9,lx=lxobjs[0],rx=rx,encs=ex,rule=rule)

        totallxs =list(lxobjs)
        ##need check if any Gonorrhea test for Chlamydia
        from identifyCases import getRelatedLx
        if string.upper(rule.ruleName)=='CHLAMYDIA':
            genorlxs = getRelatedLx('GONORRHEA')
            totallxs = totallxs + list(genorlxs)
        elif string.upper(rule.ruleName)=='GONORRHEA':
            genorlxs = getRelatedLx('CHLAMYDIA')
            totallxs = totallxs + list(genorlxs)
        self.addLXOBX(lxRecList=totallxs, orus=orus)
        self.addRXOBX(rxRecList=rxobjs, orus=orus) # do same for dr

 

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
        worklist = [('MR',demog.DemogMedical_Record_Number),('SS',demog.DemogSSN)]
        for (cxtype,val) in worklist:
            if val:
                pid3 = self.casesDoc.createElement('PID.3')
                self.addSimple(pid3,val,'CX.1')
                self.addSimple(pid3,cxtype,'CX.5')
                if cxtype=='SS':
                    e = self.casesDoc.createElement('CX.6')
                    self.addSimple(e, pcp.provPrimary_Dept,'HD.2')        
                    pid3.appendChild(e)                        
                section.appendChild(pid3)

        ##PID.5
        outerElement='PID.5'
        isClinician = 0
        patname = self.makeName(demog.DemogFirst_Name, demog.DemogLast_Name, demog.DemogMiddle_Initial, demog.DemogSuffix, outerElement, isClinician)
        section.appendChild(patname)
        pid7 = self.casesDoc.createElement('PID.7')
        self.addSimple(pid7,demog.DemogDate_of_Birth,'TS.1')          
        section.appendChild(pid7)
        if demog.DemogGender:
            self.addSimple(section,demog.DemogGender,'PID.8')

        racedir = {'CAUCASIAN':'W',
                   'BLACK':'B',
                   'OTHER':'O',
                   'HISPANIC': 'W',
                   'INDIAN':'I',
                   'ASIAN':'A',
                   'NAT AMERICAN':'I',
                   'NATIVE HAWAI':'P',
                   'ALASKAN':'I',
                   '': 'U'}
        try:
            race = racedir[string.upper(demog.DemogRace)]
        except:
            race=''
        if race:
            pidsec = self.casesDoc.createElement('PID.10')
            self.addSimple(pidsec,race,'CE.4')
            section.appendChild(pidsec)
            
        outerElement='PID.11'    
        addressType = 'H'
        address = self.makeAddress(demog.DemogAddress1, demog.DemogAddress2, demog.DemogCity, demog.DemogState, demog.DemogZip, demog.DemogCountry,outerElement, addressType)
        section.appendChild(address)
        if demog.DemogTel:
            pid13 = self.casesDoc.createElement('PID.13')
            self.addSimple(pid13,demog.DemogAreaCode,'XTN.6')
            self.addSimple(pid13,demog.DemogTel,'XTN.7')
            if demog.DemogExt:
                self.addSimple(pid13,demog.DemogExt,'XTN.8')
            section.appendChild(pid13)

        for elem, sec in [(demog.DemogHome_Language,'PID.15'),(demog.DemogMaritalStat,'PID.16')]:
            if elem:
                pidsec = self.casesDoc.createElement(sec)
                self.addSimple(pidsec,elem,'CE.4')
                section.appendChild(pidsec)

        if string.upper(demog.DemogRace) == 'HISPANIC':
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
        name = self.makeName(pcp.provFirst_Name, pcp.provLast_Name, pcp.provMiddle_Initial, suffix, outerElement, isClinician)
        section.appendChild(name)
        x1 = self.casesDoc.createElement('NK1.3')
        self.addSimple(x1,NK13,'CE.4')
        section.appendChild(x1)
        outerElement='NK1.4'
       
        country='USA'
        #addressType=None
        address = self.makeAddress(pcp.provPrimary_Dept_Address_1, pcp.provPrimary_Dept_Address_2, pcp.provPrimary_Dept_City, pcp.provPrimary_Dept_State, pcp.provPrimary_Dept_Zip, country ,outerElement, addressType)
        section.appendChild(address)
        outerElement='NK1.5'
        email=''
        ext=''
        contact = self.makeContact(email,pcp.provTelAreacode,pcp.provTel,ext,outerElement)
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
        name = self.makeName(self.config.instIDFName, self.config.instIDLName, None, suffix, outerElement, isClinician)
        section.appendChild(name)
        x1 = self.casesDoc.createElement('NK1.3')
        self.addSimple(x1,'FCP','CE.4')
        section.appendChild(x1)
        outerElement='NK1.4'
       
        country='USA'
        addressType='O'
        address = self.makeAddress(self.config.instAddress1, self.config.instAddress2, self.config.instCity, self.config.instState, self.config.instZip, country ,outerElement, addressType)
        section.appendChild(address)

        outerElement='NK1.5'
        email=self.config.instIDEmail
        contact = self.makeContact(email,self.config.instIDTelArea,self.config.instIDTel,self.config.instIDTelExt,outerElement)
        if contact <> None:
            section.appendChild(contact)
        return section


    
    ##################################################
    def addCaseOBR(self, rule=None,icd9=[],orcs=None):
        """
            </OBR.31> is used to name the notifiable condition"""
        obr = self.casesDoc.createElement('OBR')
        self.addSimple(obr,'1','OBR.1')

        obr4 = self.casesDoc.createElement('OBR.4')
        self.addSimple(obr4,'Additional Patient Demographics','CE.2')
        obr.appendChild(obr4)

        for i in icd9:
            obr31 = self.casesDoc.createElement('OBR.31') 
            self.addSimple(obr31,i,'CE.1')   
            self.addSimple(obr31,rule.ruleName,'CE.2')
            self.addSimple(obr31,'I9','CE.3')
            obr.appendChild(obr31)

        orcs.appendChild(obr)


    ############################################
    def getDurtion(self, day1,day2):
        dur =datetime.date(int(day2[:4]),int(day2[4:6]), int(day2[6:8]))-datetime.date(int(day1[:4]),int(day1[4:6]), int(day1[6:8]))
        return dur.days

    
    #############################################
    def addCaseOBX(self, demog=None, orcs=None,icd9=None,lx=None, rx=None,encs=[],rule=None):
        """
        """
        indx=1
        c=time.strftime('%Y%m%d',time.localtime())
        dob=demog.DemogDate_of_Birth
        dur = self.getDurtion(dob,c)
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'NM')],obx3=[('CE.4','21612-7')],obx5=[('',int(dur/365))])
        orcs.appendChild(obx)
        indx += 1

        ##pregnancy status
        encdb = Enc.objects.filter(EncPatient__id__exact=demog.id, EncPregnancy_Status='Y')
        if encdb:
            obx5='77386006'
            edc = encdb[0].EncEDC
            edc = edc.replace('/','')
        else:
            obx5='261665006' ##unknown
            edc=None
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
            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'NM')],obx3=[('CE.4','NA-12')],
                                obx5=[('',int(pregdur.days/7))])
            
            indx += 1
            orcs.appendChild(obx)
       
        ##NA_TRMT
        if rx and lx:
            rxdate = rx.RxOrderDate
            lxorderd = lx.LxOrderDate
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
        lxresd=lx.LxDate_of_result
        sym='373067005' #NO
        temperature=0
        for encid in encs:
            enc = Enc.objects.filter(id__exact=encid)[0]
            try:
                temperature = float(enc.EncTemperature)
            except:
                temperature=0
            dur = self.getDurtion(lxresd,enc.EncEncounter_Date)
            if abs(dur)<15 or temperature>100.4:
                sym='373066001' #YES
                break
        obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'CE')],obx3=[('CE.4','NA-5')], obx5=[('CE.4',sym)])
        indx += 1
        orcs.appendChild(obx)

        ##                
        if string.upper(rule.ruleName)  in ('CHLAMYDIA', 'GONORRHEA'):
            for i in icd9:
                obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'ST')],obx3=[('CE.4','10187-3')], obx5=[('',i)])
                indx += 1
                orcs.appendChild(obx)
            if temperature>100.4:
                obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'ST')],obx3=[('CE.4','10187-3')], obx5=[('','fever')])
                indx += 1
                orcs.appendChild(obx)
                
        ##icd9
        ##for PID only
##        for i in icd9:
##            obx = self.makeOBX(obx1=[('',indx)],obx2=[('', 'ST')],obx3=[('CE.4','NA-13')], obx5=[('',i)])
##
##            indx += 1
##            orcs.appendChild(obx)


   ##############################################                
    def addLXOBX(self,lxRecList=[],orus=None):
        if not lxRecList: return
       
        n=1
        for lxRec in lxRecList:
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
            self.addSimple(obr7,lxRec.LxOrderDate,'TS.1') # rx date
    
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

            snomed=ConditionLOINC.objects.filter(CondiLOINC=lxRec.LxLoinc)[0].CondiSNMDPosi
            obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'CE')],obx3=[('CE.4',lxRec.LxLoinc),('CE.6','L')],
                               obx5=[('CE.4',snomed)],  obx7=[('',lxRange)],obx14=[('TS.1',lxTS)])
        
            
            orcs.appendChild(obx1)
          


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
            orc = self.makeORC(rxRec.RxProvider)
            orcs.appendChild(orc)
            
            obr = self.casesDoc.createElement('OBR') # need a special rx OBR
            self.addSimple(obr,'%d' % n,'OBR.1')
            n+=1
          
            obr3 = self.casesDoc.createElement('OBR.3')
            self.addSimple(obr3,rxRec.RxOrder_Id_Num,'EI.1') 
            obr.appendChild(obr3)
            
            obr4 = self.casesDoc.createElement('OBR.4')
            self.addSimple(obr4,'18776-5','CE.4') # treatment plan
            self.addSimple(obr4,'L','CE.6') # loinc code
            obr.appendChild(obr4)

            obr7 = self.casesDoc.createElement('OBR.7')
            obr.appendChild(obr7)
            self.addSimple(obr7,rxRec.RxOrderDate,'TS.1') # rx date
            
            obr15 = self.casesDoc.createElement('OBR.15') # noise - unknown specimen source. Eeessh
            sps = self.casesDoc.createElement('SPS.1')
            self.addSimple(sps,'261665006','CE.4') #unknown
            self.addSimple(sps,'L','CE.6') # loinc code
            obr15.appendChild(sps)
            obr.appendChild(obr15)
        
            obr16 =self.makeName(firstName=rxRec.RxProvider.provFirst_Name, lastName=rxRec.RxProvider.provLast_Name, middleInit=rxRec.RxProvider.provMiddle_Initial, suffix='',outerElement ='OBR.16',isClinician=1)
            obr.appendChild(obr16)

            if rxRec.RxStatus: status= 'F'
            else: status = 'P'
            self.addSimple(obr,status,'OBR.25') # result status

           
            obr29 = self.casesDoc.createElement('OBR.29') # rxid goes in here as the "parent"
            eip = self.casesDoc.createElement('EIP.2')
            self.addSimple(eip,rxRec.RxOrder_Id_Num,'EI.1')
            obr29.appendChild(eip)
            obr.appendChild(obr29)
            
            orcs.appendChild(obr)
            
            # now add the obx records needed to describe dose, frequency and duration
            rxDur='N/A'
            if rxRec.RxStartDate and rxRec.RxEndDate:
                rxDur =datetime.date(int(rxRec.RxEndDate[:4]),int(rxRec.RxEndDate[4:6]), int(rxRec.RxEndDate[6:8]))  - datetime.date(int(rxRec.RxStartDate[:4]),int(rxRec.RxStartDate[4:6]), int(rxRec.RxStartDate[6:8]))
                rxDur = rxDur.days
                       
           
            rxTS = rxRec.RxOrderDate
            #<OBX.5>NDC_Number; Drug Name; Dose; Frequency; Duration</OBX.5>
            drugstr = '%s;%s;%s;%s;%s day(s)' % (rxRec.RxNational_Drug_Code, rxRec.RxDrugName,rxRec.RxDose,rxRec.RxFrequency,rxDur)
            obx1 = self.makeOBX(obx1=[('','1')],obx2=[('', 'ST')],obx3=[('CE.4','NA-56')],
                               obx5=[('', drugstr)])

            orcs.appendChild(obx1)



    ###########################################
    def makeOBX(self, obx1=[],obx2=[],obx3=[],obx5=[],obx6=[],obx7=[],obx11=[('','')],obx14=[]):
        obx = self.casesDoc.createElement('ORU_R01.OBXNTE_SUPPGRP')
        p = self.casesDoc.createElement('OBX')
        
        for (OuterTag, obxl) in [('OBX.1',obx1),('OBX.2',obx2),('OBX.3',obx3), ('OBX.5',obx5),('OBX.6',obx6),('OBX.7',obx7),('OBX.11',obx11),('OBX.14',obx14)]:
            if len(obxl)==1 and obxl[0][0]=='':
                if string.strip('%s' % obxl[0][1]):
                    self.addSimple(p,obxl[0][1],OuterTag)
            elif len(obxl)>0:
                tempobx=None
                for tag,v in obxl:
                    if not tempobx and v:
                        tempobx = self.casesDoc.createElement(OuterTag)
                    if v:
                        self.addSimple(tempobx,v,tag)          
                if tempobx:
                    p.appendChild(tempobx)

        obx.appendChild(p)
        return obx
       
            
    
    ########################################    
    def makeORC(self, pcp=None):
        """updated like makePCP to use the pcp record
        """
        orc = self.casesDoc.createElement('ORC')
        suffix = ''
        isClinician = 1
        outerElement='ORC.12'
        name = self.makeName(pcp.provFirst_Name, pcp.provLast_Name, pcp.provMiddle_Initial, suffix, outerElement, isClinician)
        orc.appendChild(name)

        outerElement='ORC.14'
        email=''
        ext=''
        contact = self.makeContact(email,pcp.provTelAreacode,pcp.provTel,ext,outerElement)
        if contact <> None:
            orc.appendChild(contact)
        orc21 = self.casesDoc.createElement('ORC.21')
        self.addSimple(orc21,self.config.institution_name,'XON.1')
        orc.appendChild(orc21)
        
        outerElement='ORC.22'
        country='USA'
        addressType=None
        address = self.makeAddress(self.config.instAddress1, self.config.instAddress2, self.config.instCity, self.config.instState, self.config.instZip, country ,outerElement, addressType)
        orc.appendChild(address)

        outerElement='ORC.23'
        contact = self.makeContact(None,self.config.instIDTelArea,self.config.instIDTel,self.config.instIDTelExt,outerElement)
        if contact <> None:
            orc.appendChild(contact)

        outerElement='ORC.24'
        address = self.makeAddress(self.config.instAddress1, self.config.instAddress2, self.config.instCity, self.config.instState, self.config.instZip, country ,outerElement, addressType)
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
        for (element,ename) in [(self.config.institution_name, 'HD.1'),(self.config.institution_CLIA,'HD.2'), ('CLIA','HD.3')]:
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
        if not txt:
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
        self.addHSimple(bh,self.config.appName,'BHS.3')
        self.addHSimple(bh,self.config.sendingFac,'BHS.4')
        e = self.batchDoc.createElement('BHS.7')
        self.addHSimple(e,self.timestamp,'TS.1')
        bh.appendChild(e)
        return bh


    ####################################
    ####################################
    def makeName(self, firstName, lastName, middleInit, suffix, outerElement, isClinician):
        """reusable componenet = xpn1-4 pass the field names
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
        """reusable componenet = xad.1-7 pass the field names
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
        
        testDoc.addCase(demog=demog,pcp=pcp,rule=rule, lx=lx, rx=rx,ex=ex,icd9=caseicd9)

       
    # Print our newly created XML
    s = testDoc.renderBatch()
    f = file('hl7Sample.hl7','w')
    f.write(s)
    f.close()
    print s

if __name__ == "__main__":
    test()
        
    
