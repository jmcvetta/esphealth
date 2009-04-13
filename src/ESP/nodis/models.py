'''
                                  ESP Health
                         Notifiable Diseases Framework
                                  Data Models
'''


import datetime

from django.db import models

from ESP.esp.models import Demog, Provider, Enc, Lx, Rx, Immunization
from ESP.hef.models import HeuristicEvent
from ESP.conf.models import Rule
from ESP.conf.choices import WORKFLOW_STATES


class Case(models.Model):
    '''
    A case of (reportable) disease
    '''
    patient = models.ForeignKey(Demog, blank=False)
    condition = models.ForeignKey(Rule, blank=False)
    provider = models.ForeignKey(Provider, blank=False)
    date = models.DateField(blank=False, db_index=True)
    workflow_state = models.CharField(max_length=20, choices=WORKFLOW_STATES, default='AR', 
        blank=False, db_index=True )
    # Timestamps:
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    sent_timestamp = models.DateTimeField(blank=True, null=True)
    #
    # Events that define this case
    #
    events = models.ManyToManyField(HeuristicEvent, blank=False) # The events that caused this case to be generated
    #
    # Reportable Events
    #
    encounters = models.ManyToManyField(Enc, blank=True, null=True)
    lab_results = models.ManyToManyField(Lx, blank=True, null=True)
    medications = models.ManyToManyField(Rx, blank=True, null=True)
    immunizations = models.ManyToManyField(Immunization, blank=True, null=True)
    #
    notes = models.TextField(blank=True, null=True)
    
    #
    # Backward Compatibility
    #
    def getCaseDemog(self):
        return self.patient
    def getCaseProvider(self):
        return self.provider
    def getCaseRule(self):
        return self.condition
    def getCaseWorkflow(self):
        return self.workflow_state
    def getCaseLastUpDate(self):
        return self.updated_timestamp
    def getCasecreatedDate(self):
        return self.created_timestamp
    def getCaseSendDate(self):
        return self.sent_timestamp
    def getCaseQueryID(self):
        # AFAIK this field is never used.
        return None
    def getCaseMsgFormat(self):
        # AFAIK this field is never used.
        return None
    def getCaseMsgDest(self):
        # AFAIK this field is never used.
        return None
    def getCaseEncID(self):
        return ','.join([str(item.id) for item in self.encounters.all()])
    def getCaseLxID(self):
        return ','.join([str(item.id) for item in self.lab_results.all()])
    def getCaseRxID(self):
        return ','.join([str(item.id) for item in self.medications.all()])
    def getCaseICD9(self):
        result = []
        [result.extend(item.icd9_list) for item in self.encounters.all()]
        return result
    def getCaseImmID(self):
        return ','.join([str(item.id) for item in self.immunizations.all()])
    def getCaseComments(self):
        return self.notes
    def setCaseDemog(self, value):
        self.patient = value
    def setCaseProvider(self, value):
        self.provider = value
    def setCaseRule(self, value):
        self.condition = value
    def setCaseWorkflow(self, value):
        self.workflow_state = value
    def setCaseLastUpDate(self, value):
        self.updated_timestamp = value
    def setCasecreatedDate(self, value):
        self.created_timestamp = value
    def setCaseSendDate(self, value):
        self.sent_timestamp = value
    def setCaseQueryID(self, value):
        raise NotImplementedError('AFAIK this field is never used.')
    def setCaseMsgFormat(self, value):
        raise NotImplementedError('AFAIK this field is never used.')
    def setCaseMsgDest(self, value):
        raise NotImplementedError('AFAIK this field is never used.')
    def setCaseEncID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
        self.__caseEncID = value
    def setCaseLxID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseRxID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseICD9(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseImmID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseComments(self, value):
        self.notes = value

    caseDemog = property(getCaseDemog, setCaseDemog)
    caseProvider = property(getCaseProvider, setCaseProvider)
    caseRule = property(getCaseRule, setCaseRule)
    caseWorkflow = property(getCaseWorkflow, setCaseWorkflow)
    caseLastUpDate = property(getCaseLastUpDate, setCaseLastUpDate)
    casecreatedDate = property(getCasecreatedDate, setCasecreatedDate)
    caseSendDate = property(getCaseSendDate, setCaseSendDate)
    caseQueryID = property(getCaseQueryID, setCaseQueryID)
    caseMsgFormat = property(getCaseMsgFormat, setCaseMsgFormat)
    caseMsgDest = property(getCaseMsgDest, setCaseMsgDest)
    caseEncID = property(getCaseEncID, setCaseEncID)
    caseLxID = property(getCaseLxID, setCaseLxID)
    caseRxID = property(getCaseRxID, setCaseRxID)
    caseICD9 = property(getCaseICD9, setCaseICD9)
    caseImmID = property(getCaseImmID, setCaseImmID)
    caseComments = property(getCaseComments, setCaseComments)
    
    class Meta:
        permissions = [ ('view_phi', 'Can view protected health information'), ]
    
    def latest_lx(self):
        '''
        Returns the latest lab test relevant to this case
        '''
        if not self.caseLxID:
            return None

        lab_result_ids = self.caseLxID.split(',')
        lab_results = Lx.objects.filter(id__in=lab_result_ids).order_by('LxOrderDate').reverse()
        return lab_results[0]
        
    def latest_lx_order_date(self):
        '''
        Return a datetime.date instance representing the date on which the 
        latest lab test relevant to this case was ordered.
        '''
        if not self.latest_lx():
            return None

        s = self.latest_lx().LxOrderDate
        year = int(s[0:4])
        month = int(s[4:6])
        day = int(s[6:8])
        return datetime.date(year, month, day)
    
    def latest_lx_provider_site(self):
        '''
        Return the provider site for the latest lab test relevant to this case 
        '''
        lx = self.latest_lx()
        if not lx:
            return None
        return lx.LxOrdering_Provider.provPrimary_Dept

    def  __unicode__(self):
        p = self.showPatient()# self.pID
        #s = u'Patient=%s RuleID=%s MsgFormat=%s Comments=%s' % (p,self.caseRule.id, self.caseMsgFormat,self.caseComments)
        s = u'#%-10s %-10s %-15s Patient: %-10s' % (self.id, self.date, self.condition, self.patient)
        return s
 
    def showPatient(self): 
        p = self.getPatient()
        #  s = '%s, %s: %s MRN=%s' % (p.PIDLast_Name, p.PIDFirst_Name, p.PIDFacility1, p.PIDMedical_Record_Number1 )
        s = u'%s %s %s %s' % (p.DemogLast_Name, p.DemogFirst_Name, p.DemogMiddle_Initial,p.DemogMedical_Record_Number )
        return s

    def getPatient(self): # doesn't work
        p = Demog.objects.get(id__exact = self.caseDemog.id)        
        return p

    def getPregnant(self):
        p=self.getPatient()
        encdb = Enc.objects.filter(EncPatient=p, EncPregnancy_Status='Y').order_by('EncEncounter_Date')
        lxs = None
        lxi = self.caseLxID
        if len(lxi) > 0:
            lxs=Lx.objects.filter(id__in=lxi.split(','))
        if encdb and lxs:
            lx = lxs[0]
            lxorderd = lx.LxOrderDate
            lxresd=lx.LxDate_of_result
            lxresd = datetime.date(int(lxresd[:4]),int(lxresd[4:6]),int(lxresd[6:8]))+datetime.timedelta(30)
            lxresd = lxresd.strftime('%Y%m%d')
            for oneenc in encdb:
                encdate = oneenc.EncEncounter_Date
                edcdate = oneenc.EncEDC.replace('/','')
                if edcdate:
                    edcdate = datetime.date(int(edcdate[:4]),int(edcdate[4:6]), int(edcdate[6:8]))
                    dur1 =edcdate-datetime.date(int(lxorderd[:4]),int(lxorderd[4:6]), int(lxorderd[6:8]))
                    dur2 = edcdate-datetime.date(int(lxresd[:4]),int(lxresd[4:6]), int(lxresd[6:8]))
                    if dur1.days>=0 or dur2.days>=0:
                        return (u'Pregnant', oneenc.EncEDC.replace('/',''))
#            for oneenc in encdb:
#                encdate = oneencdb.EncEncounter_Date
#                dur1 =datetime.date(int(encdate[:4]),int(encdate[4:6]), int(encdate[6:8]))-datetime.date(int(lxorderd[:4]),int(lxorderd[4:6]), int(lxorderd[6:8]))
#                dur2 = datetime.date(int(lxresd[:4]),int(lxresd[4:6]), int(lxresd[6:8])) - datetime.date(int(encdate[:4]),int(encdate[4:6]), int(encdate[6:8]))
#                if dur1.days>=0 and dur2.days>=0:
#                    return ('Pregnant', oneenc.EncEDC.replace('/',''))
        elif encdb and not lxs:
            return (u'Pregnant', encdb[0].EncEDC.replace('/',''))
        return (u'',None)

    def getcaseLastUpDate(self):
        s = u'%s' % self.caseLastUpDate
        return s[:11]

    def getWorkflows(self): # return a list of workflow states for history
        wIter = CaseWorkflow.objects.iterator(workflowCaseID__exact = self.id).order_by('-workflowDate')
        return wIter
    
    def getCondition(self):
        cond = Rule.objects.get(id__exact=self.caseRule.id)
        return cond

    def getAddress(self):
        p = self.getPatient()
        s=''
        if p.DemogAddress1:
            s = u'%s %s %s, %s, %s' % (p.DemogAddress1, p.DemogAddress2, p.DemogCity,p.DemogState,p.DemogZip)
        return s

    def getPrevcases(self):
        othercases = Case.objects.filter(patient=self.patient, condition=self.condition.id, date__lt=self.date)
        returnstr=[]
        for c in othercases:
            returnstr.append(unicode(c.id))
        return returnstr

    
class CaseWorkflow(models.Model):
    workflowCaseID = models.ForeignKey(Case)
    workflowDate = models.DateTimeField('Activated',auto_now=True)
    workflowState = models.CharField('Workflow State',choices=WORKFLOW_STATES,max_length=20 )
    workflowChangedBy = models.CharField('Changed By', max_length=30)
    workflowComment = models.TextField('Comments',blank=True,null=True)
    
    def  __unicode__(self):
        return u'%s %s %s' % (self.workflowCaseID, self.workflowDate, self.workflowState)


