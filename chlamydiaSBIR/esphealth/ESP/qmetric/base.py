'''
                              ESP Health Project
                            Quality Metrics module
                           Update ValueSets from VSA

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''
import abc, xmltodict, ntpath, collections
from ESP.qmetric.models import Element, Elementmapping, Criteria, Population
from ESP.emr.models import Patient
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from dateutil.relativedelta import relativedelta


class ElementMapCollection:
    '''
    Class containing properties and methods for HQMF qMetric data element
    '''

    def __init__(self, ElementQS):
        self.cmsname=ElementQS.cmsname
        self.ename=ElementQS.ename
        self.oid=ElementQS.oid
        self.category=ElementQS.category
        self.use=ElementQS.use
        self.source=ElementQS.source
        self.content_type=ElementQS.content_type
        self.mapped_field=ElementQS.mapped_field
        self.codes=[]
        for emap in ElementQS.ElementMapping_set.all():
            self.codes.append(emap.code)

class HQMF_Parser:
    '''
    method for reading hqmf document
    '''
    
    def __init__(self,hqmf_filepath):
        assert hqmf_filepath
        file_handle = open(hqmf_filepath)
        self.cmsname=ntpath.splitext(ntpath.basename(hqmf_filepath))[0]
        self.hqmfdict = xmltodict.parse(file_handle)
        
    def gettype(self):
        return self.hqmfdict['QualityMeasureDocument']['typeId']['@extension']

class BasePopulationQualifier:
    '''
    Abstract base class for generating Population qualifier events
    '''
    
    @abc.abstractmethod
    def criteria_qs(self,entry):
        '''
        list of combinatorial logic for criteria list and data elements for population inclusion
        @return: a dictionary of Q objects
        @rtype: dictionary
        '''
        
    @abc.abstractmethod
    def generate(self):
        '''
        use qualifierQS to generate population qualifying events and their EMRs
        @return: count of events created
        @rtype: integer
        '''
        
class DSTU2Qualifier(BasePopulationQualifier):
    '''
    Generate population qualifying events using HL7 HQMF specification DSTU Release 2, 2.1 metrics
    '''
    
    def __init__(self, hqmf_parserobj):
        '''
        here is where the magic works -- call the hqmf parser to define criteria logic
        for named population, using hqmf file
        The qualifier object will include a dictionary with the different population groups as lookup names
        each associated with a dictionary of querysets.  The querysets will be used to populate the population events table. 
        '''
        self.cmsname=hqmf_parserobj.cmsname
        components=hqmf_parserobj.hqmfdict['QualityMeasureDocument']['component']
        for component in components:
            if component['section']['title']=='Population criteria':
                self.criteria = {}
                for entry in component['section']['entry']:
                    self.criteria.update(self.criteria_qs(entry))
                
    def get_ename(self,cdict):
        try:
            ename=cdict['act']['sourceOf']['observation']['title']
            return ename
        except KeyError:
            pass
        try:
            ename=cdict['act']['sourceOf']['encounter']['title']
            return ename
        except:
            pass
        try:
            ename=cdict['act']['sourceOf']['substanceAdministration']['title']
            return ename
        except:
            pass
        try:
            ename=cdict['act']['sourceOf']['procedure']['title']
            return ename
        except:
            pass
    
    def criteria_qs(self,entry):
        '''
        Queryset to generate criteria record
        @return: a dictionary of querysets
        @rtype: dictionary
        '''
        qsets = {}
        elems = Element.objects.filter(cmsname=self.cmsname)
        for crit in entry['observation']['sourceOf']:
            if type(crit) is collections.OrderedDict:
                try:
                    ename=self.get_ename(crit)
                    #reset ename because population criteria section uses slightly different titles than data criteria section.
                    ename, critQ = self.get_qset(elems,ename)
                    if critQ != None: qsets.update({ename:critQ})
                except (KeyError, TypeError):
                    pass
                try:
                    for crit_s1 in crit['act']['sourceOf']:
                        if type(crit_s1) is collections.OrderedDict:
                            try:
                                ename=self.get_ename(crit_s1)
                                ename, critQ = self.get_qset(elems,ename)
                                if critQ != None: qsets.update({ename:critQ})
                            except (KeyError, TypeError):
                                pass
                            try:
                                for crit_s2 in crit_s1['act']['sourceOf']:
                                    if type(crit_s2) is collections.OrderedDict:
                                        try:
                                            ename=self.get_ename(crit_s2)
                                            ename, critQ = self.get_qset(elems,ename)
                                            if critQ != None: qsets.update({ename:critQ})
                                        except (KeyError, TypeError):
                                            pass
                                        try:
                                            for crit_s3 in crit_s2['act']['sourceOf']:
                                                if type(crit_s3) is collections.OrderedDict:
                                                #TODO: have not seen element logic deeper than 3 sub levels, but should have some test for this
                                                    try:
                                                        ename=self.get_ename(crit_s3)
                                                        ename, critQ = self.get_qset(elems,ename)
                                                        if critQ != None: qsets.update({ename:critQ})
                                                    except (KeyError, TypeError):
                                                        pass
                                        except (KeyError, TypeError):
                                            pass
                            except (KeyError, TypeError):
                                pass
                except (KeyError, TypeError):
                    pass
                    #we expect key errors.
        return qsets     
                
    def load_criteria(self):
        #get patient vars that must have values or specific values
        count=0
        for key, crit in self.criteria.iteritems():
            if not crit: 
                pass
            else:
                elem=Element.objects.get(cmsname=self.cmsname,ename=key)
                modl = elem.content_type.model
                for patrec in crit:
                    if patrec.date_of_birth==None or patrec.gender!='F':
                        pass
                        #this excludes any patients who don't meet basic criteria required inclusion
                        #TODO: get this from the xml or element/elementmapping
                    elif modl=='encounter':
                        for enc in patrec.encounter_set.all():
                            crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                            date=enc.date, content_type=elem.content_type,
                                            object_id=enc.id)
                            crec.save(force_insert=True)
                            count+=1
                    elif modl=='laborder':
                        for ordr in patrec.laborder_set.all():
                            crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                            date=ordr.date, content_type=elem.content_type,
                                            object_id=ordr.id)
                            crec.save(force_insert=True)
                            count+=1
                    elif modl=='labresult':
                        for res in patrec.labresult_set.all():
                            crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                            date=res.date, content_type=elem.content_type,
                                            object_id=res.id)
                            crec.save(force_insert=True)
                            count+=1
                    elif modl=='prescription':
                        for rx in patrec.prescription_set.all():
                            crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                            date=rx.date, content_type=elem.content_type,
                                            object_id=rx.id)
                            crec.save(force_insert=True)
                            count+=1
                    elif modl=='patient':
                        crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                        date=patrec.date_of_birth.date(), content_type=elem.content_type,
                                        object_id=patrec.id)
                        crec.save(force_insert=True)
                        count+=1
        return count
    
    def generate(self, pstart, pend):
        '''
        generate the population qualifiers by applying hqmf logic to criteria elements for the specified period
        '''
        ageQ = "select distinct patient_id from qmetric_criteria where critname='Patient Characteristic Birthdate: birth date' and cmsname='" \
               + self.cmsname + "' and date > '" + (pstart-relativedelta(years=24)).strftime('%Y-%m-%d') + "'::date and date <= '" \
               + (pstart-relativedelta(years=16)).strftime('%Y-%m-%d') + "'::date"
        sexQ = "select distinct patient_id from qmetric_criteria where critname='Patient Characteristic Sex: Female' and cmsname='" + self.cmsname + "'"
        encQ_1 = "select distinct patient_id from qmetric_criteria where critname='Encounter, Performed: Office Visit' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        encQ_2 = "select distinct patient_id from qmetric_criteria where critname='Encounter, Performed: Face-to-Face Interaction' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        encQ_3 = "select distinct patient_id from qmetric_criteria where critname='Encounter, Performed: Preventive Care Services - Established Office Visit, 18 and Up' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        encQ_4 = "select distinct patient_id from qmetric_criteria where critname='Encounter, Performed: Preventive Care Services-Initial Office Visit, 18 and Up' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        encQ_5 = "select distinct patient_id from qmetric_criteria where critname='Encounter, Performed: Preventive Care - Established Office Visit, 0 to 17' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        encQ_6 = "select distinct patient_id from qmetric_criteria where critname='Encounter, Performed: Preventive Care- Initial Office Visit, 0 to 17' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        encQ_7 = "select distinct patient_id from qmetric_criteria where critname='Encounter, Performed: Home Healthcare Services' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_1 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: Other Female Reproductive Conditions' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_2 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: Genital Herpes' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_3 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: Gonococcal Infections and Venereal Diseases' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_4 = "select distinct patient_id from qmetric_criteria where critname='Medication, Active: Contraceptive Medications' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_5 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: Inflammatory Diseases of Female Reproductive Organs' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_6 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: Chlamydia' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_7 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: HIV' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_8 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: Syphilis' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_9 = "select distinct patient_id from qmetric_criteria where critname='Diagnosis, Active: Complications of Pregnancy, Childbirth and the Puerperium' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        labQ_1 = "select distinct patient_id from qmetric_criteria where critname='Laboratory Test, Order: Pregnancy Test' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        labQ_2 = "select distinct patient_id from qmetric_criteria where critname='Laboratory Test, Order: Pap Test' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        labQ_3 = "select distinct patient_id from qmetric_criteria where critname='Laboratory Test, Order: Lab Tests During Pregnancy' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        labQ_4 = "select distinct patient_id from qmetric_criteria where critname='Laboratory Test, Order: Lab Tests for Sexually Transmitted Infections' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        procQ_1 = "select distinct patient_id from qmetric_criteria where critname='Procedure, Performed: Delivery Live Births' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        procQ_2 = "select distinct patient_id from qmetric_criteria where critname='Diagnostic Study, Order: Diagnostic Studies During Pregnancy' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        procQ_3 = "select distinct patient_id from qmetric_criteria where critname='Procedure, Performed: Procedures During Pregnancy' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        procQ_4 = "select distinct patient_id from qmetric_criteria where critname='Procedure, Performed: Procedures Involving Contraceptive Devices' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        medQ_1 = "select distinct patient_id from qmetric_criteria where critname='Medication, Order: Contraceptive Medications' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        exclQ_1 = "select distinct patient_id from qmetric_criteria where critname='Medication, Order: Isotretinoin' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
        exclQ_1 = "select distinct patient_id from qmetric_criteria where critname='Diagnostic Study, Order: X-Ray Study (all inclusive)' and cmsname='" + self.cmsname \
               + "' and date between '" + pstart.strftime('%Y-%m-%d') + "'::date and '" + pend.strftime('%Y-%m-%d') + "'::date"
               
        allQ = 'select * from (' + ageQ + ') age inner join (' + sexQ + ') sex on sex.patient_id=age.patient_id ' \
              + 'inner join (select * from (' + encQ_1 + ') enc1 ' \
                   + ' union select * from (' + encQ_2 + ') enc2 ' \
                   + ' union select * from (' + encQ_3 + ') enc3 ' \
                   + ' union select * from (' + encQ_4 + ') enc4 ' \
                   + ' union select * from (' + encQ_5 + ') enc5 ' \
                   + ' union select * from (' + encQ_6 + ') enc6 ' \
                   + ' union select * from (' + encQ_7 + ') enc7 ) enc on sex.patient_id=enc.patient_id ' \
              + 'inner join (select * from (' + diagQ_1 + ') diag1 ' \
                   + ' union select * from (' + diagQ_2 + ') diag2 ' \
                   + ' union select * from (' + diagQ_3 + ') diag3 ' \
                   + ' union select * from (' + diagQ_4 + ') diag4 ' \
                   + ' union select * from (' + diagQ_5 + ') diag5 ' \
                   + ' union select * from (' + diagQ_6 + ') diag6 ' \
                   + ' union select * from (' + diagQ_7 + ') diag7 ' \
                   + ' union select * from (' + diagQ_8 + ') diag8 ' \
                   + ' union select * from (' + diagQ_9 + ') diag9 ) diag on sex.patient_id=diag.patient_id ' \


    
    def get_qset(self,elems,elemname):
        '''
        Returns a Q object based on values passed
        '''
        # Doing some hand standing here because the HQMF document can prefix element titles 
        #   with additional descriptive info in the population criteria section so they don't match the
        #   titles in the data criteria section titles.  The Django ORM does not include a "contained in" 
        #   operator.  If anyone knows a better way to do this, let me know.  BZ    
        try: 
            elem = elems.extra(where=["%s like '%%' || ename || '%%'"], params=[elemname]).get()
        except Element.DoesNotExist:
            return None
        #    return None
        ename=elem.ename
        modl = elem.content_type.model
        var = elem.mapped_field
        try:
            codelist = elem.elementmapping_set.values_list('code')
        except Elementmapping.DoesNotExist:
            return None
        if not var:
            return ename, Patient.objects.all()
        if modl=='patient':
            leftside = var + '__in'
        else:
            leftside= modl + '__' + var + '__in'
        kwargs={leftside:codelist}
        qset=Patient.objects.filter(**kwargs)
        return ename, qset
        
    
class ResultGenerator:
    '''
    methods for a command that will populate results table
    '''

        