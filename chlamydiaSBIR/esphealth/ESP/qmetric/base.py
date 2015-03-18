'''
                              ESP Health Project
                            Quality Metrics module
                           Base classes and methods

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''
import abc, ntpath, collections, xmltodict
from ESP.qmetric.models import Element, Elementmapping, Criteria, Population, Results
from ESP.emr.models import Patient
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.db import connection
from django.db.models import Q, F

#TODO: this is the max measurement period allowed by the system.  Should be a config setting
MAX_PERIOD=1

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
            self.codes.apself.pend(emap.code)

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
        self.q_obj_lst = []
        self.f_expr_lst = []
        components=hqmf_parserobj.hqmfdict['QualityMeasureDocument']['component']
        for component in components:
            if component['section']['title']=='Population criteria':
                self.criteria = {}
                for entry in component['section']['entry']: 
                    #criteria_qs returns a query set, but also updates q_obj and f_expr lists as relevant info is found
                    # The q_objects and f_expressions have to be gathered as a set, then are applied as additional
                    # filters to each querset.
                    self.criteria.update(self.criteria_qs(entry))
            
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
                    ename, critQ = self.get_qset(elems,ename,crit)
                    if critQ != None: qsets.update({ename:critQ})
                except (KeyError, TypeError):
                    pass
                try:
                    for crit_s1 in crit['act']['sourceOf']:
                        if type(crit_s1) is collections.OrderedDict:
                            try:
                                ename=self.get_ename(crit_s1)
                                ename, critQ = self.get_qset(elems,ename,crit)
                                if critQ != None: qsets.update({ename:critQ})
                            except (KeyError, TypeError):
                                pass
                            try:
                                for crit_s2 in crit_s1['act']['sourceOf']:
                                    if type(crit_s2) is collections.OrderedDict:
                                        try:
                                            ename=self.get_ename(crit_s2)
                                            ename, critQ = self.get_qset(elems,ename,crit)
                                            if critQ != None: qsets.update({ename:critQ})
                                        except (KeyError, TypeError):
                                            pass
                                        try:
                                            for crit_s3 in crit_s2['act']['sourceOf']:
                                                if type(crit_s3) is collections.OrderedDict:
                                                #TODO: This whole nested approach will have to be redesigned
                                                # The nesting actually conveys important information about condition grouping
                                                # (ANDs and ORs)  I have that all hardcoded in the resultgenerator class.    
                                                    try:
                                                        ename=self.get_ename(crit_s3)
                                                        ename, critQ = self.get_qset(elems,ename,crit)
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
        for i, q_obj in enumerate(self.q_obj_lst):
            if i==0:
                q = Q(**q_obj['q_kwargs'])
            elif q_obj['conj']=='AND': 
                #TODO: here for OR NOT etc.
                q = q & Q(**q_obj['q_kwargs'])
        for key, crit in self.criteria.iteritems():
            if not crit: 
                pass
            else:
                elem=Element.objects.get(cmsname=self.cmsname,ename=key)
                modl = elem.content_type.model
                #apply the q and f lists.  This does not do the conjunction piece
                #  at all correctly.  
                #TODO: Needs to deal with OR, NOT, etc. in a coherent way.
                #TODO: date is hardcoded below.  This is the target var in the domain modl, and probably needs to be dynamic
                crit = crit.filter(q)
                for i, f_expr in enumerate(self.f_expr_lst):
                    exp_str=modl+"__date%s" % (f_expr['f_opr'])
                    fkwargs={exp_str:f_expr['f_expr']}
                    if i ==0:
                        fq=Q(**fkwargs)
                    elif f_expr['f_conj']=='AND':
                        fq=fq & Q(**fkwargs)
                crit = crit.filter(fq).prefetch_related(modl+'_set')
                try:
                    for patrec in crit:
                        if modl=='encounter':
                            for enc in patrec.encounter_set.all():
                                crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                                date=enc.date, content_type=elem.content_type,
                                                object_id=enc.id)
                                crec.save(force_insert=True)
                                count+=1
                                if (count % 1000)==0: print str(count) + " criteria records loaded"
                        elif modl=='laborder':
                            for ordr in patrec.laborder_set.all():
                                crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                                date=ordr.date, content_type=elem.content_type,
                                                object_id=ordr.id)
                                crec.save(force_insert=True)
                                count+=1
                                if (count % 1000)==0: print str(count) + " criteria records loaded"
                        elif modl=='labresult':
                            for res in patrec.labresult_set.all():
                                crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                                date=res.date, content_type=elem.content_type,
                                                object_id=res.id)
                                crec.save(force_insert=True)
                                count+=1
                                if (count % 1000)==0: print str(count) + " criteria records loaded"
                        elif modl=='prescription':
                            for rx in patrec.prescription_set.all():
                                crec = Criteria(cmsname=self.cmsname,critname=key,patient=patrec,
                                                date=rx.date, content_type=elem.content_type,
                                                object_id=rx.id)
                                crec.save(force_insert=True)
                                count+=1
                                if (count % 1000)==0: print str(count) + " criteria records loaded"
                        else: 
                            print modl + " model not handled.  BOOM!  (Fix me)"
                except AttributeError:
                    pass
        return count
    
    def get_qset(self,elems,elemname,crit):
        '''
        Returns a queryset or a q object (both are returned, one will = None), based on values passed
        '''
        # Doing some hand standing here because the HQMF document can prefix element titles 
        #   with additional descriptive info in the population criteria section so they don't match the
        #   titles in the data criteria section titles.  The Django ORM does not include a "contained in" 
        #   operator (inverse of contains).  If anyone knows a better way to do this, let me know.  BZ    
        try: 
            elem = elems.extra(where=["%s like '%%' || ename || '%%'"], params=[elemname]).get()
        except Element.DoesNotExist:
            return None
        #    return None
        ename=elem.ename
        qset = None
        if "Patient Characteristic" in ename:
            #gender is best used as an additional filter on the other query sets
            #but birth date is only directly relevant to the measurement period
            #we can still apply the birthdate requirement to limit criteria records collected
            #if a patient must have aged out of or can't have aged in to the measurement period
            #then the record should be excluded.  
            #This is a problem if birthdate high restrictions are imposed for the start of the period
            # or low is imposed for end of period.  Chlamydia uses SBS (start before start) for both
            # so patients can be up to [max period duration] older when an event occurs.
            #TODO: temporal relation typeCode needs to be dealt with -- Chlamydia uses SBS in all cases so it is assumed here 
            if 'sourceOf' in crit['act']['sourceOf']['observation']:
                #get stuff for F expression
                f_dict={}
                f_dict['f_conj']=crit['conjunctionCode']['@code']
                #TODO: will certainly need to deal with more than years
                if 'low' in crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']:
                    pq=crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']['low']
                    #Tried using relativedelta here, but F expression didn't like it
                    f_dict['f_expr']=F(elem.mapped_field) + timedelta(days=int((int(pq['@value'])+MAX_PERIOD)*365.25) )
                    if pq['@inclusive']=='false':
                        f_dict['f_opr']='__gt'
                    else:
                        f_dict['f_opr']='__gte'
                    self.f_expr_lst.append(f_dict)
                elif 'high' in crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']:
                    pq=crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']['high']
                    f_dict['f_expr']=F(elem.mapped_field) + timedelta(days=int((int(pq['@value'])+MAX_PERIOD)*365.25) )
                    if pq['@inclusive']=='false':
                        f_dict['f_opr']='__lt'
                    else:
                        f_dict['f_opr']='__lte'
                    self.f_expr_lst.append(f_dict)
            else:
                #get stuff for Q object
                q_dict={}
                q_dict['q_conj']=crit['conjunctionCode']['@code']
                q_dict['q_kwargs']={elem.mapped_field+'__in':elem.elementmapping_set.values_list('code')}
                self.q_obj_lst.append(q_dict)
        else:
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
            qset=Patient.objects.filter(**kwargs).distinct()
        return ename, qset
        
    
class ResultGenerator:
    '''
    methods for a command that will populate results table
    '''
    def __init__(self,pstart,pend,cmsname):
        self.pstart=pstart
        self.pend=pend
        self.cmsname=cmsname

    def loadPop(self,patlist, etype):
        count=0
        for pat in patlist:
            patient = Patient.objects.get(id=pat)
            pRec=Population(cmsname=self.cmsname, etype=etype, periodstartdate=self.pstart, periodenddate=self.pend, patient=patient)
            pRec.save(force_insert=True)
            count+=1
        return count
    
    def make_qstring(self, cname):
        return "select distinct patient_id from qmetric_criteria where critname='" + cname + "' and cmsname='" + self.cmsname + "' " 

    def genpop(self):
        '''
        generate the population qualifiers by applying hqmf logic to criteria elements for the specified period
        '''
        ageQ = "select id as patient_id from emr_patient where " \
               + " date_of_birth > '" + (self.pstart-relativedelta(years=24)).strftime('%Y-%m-%d') + "'::date and date_of_birth <= '" \
               + (self.pstart-relativedelta(years=16)).strftime('%Y-%m-%d') + "'::date"
        encQ_1 = self.make_qstring('Encounter, Performed: Office Visit') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        encQ_2 = self.make_qstring('Encounter, Performed: Face-to-Face Interaction') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        encQ_3 = self.make_qstring('Encounter, Performed: Preventive Care Services - Established Office Visit, 18 and Up') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        encQ_4 = self.make_qstring('Encounter, Performed: Preventive Care Services-Initial Office Visit, 18 and Up') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        encQ_5 = self.make_qstring('Encounter, Performed: Preventive Care - Established Office Visit, 0 to 17') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        encQ_6 = self.make_qstring('Encounter, Performed: Preventive Care- Initial Office Visit, 0 to 17') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        encQ_7 = self.make_qstring('Encounter, Performed: Home Healthcare Services') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_1 = self.make_qstring('Diagnosis, Active: Other Female Reproductive Conditions') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_2 = self.make_qstring('Diagnosis, Active: Genital Herpes') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_3 = self.make_qstring('Diagnosis, Active: Gonococcal Infections and Venereal Diseases') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_4 = self.make_qstring('Medication, Active: Contraceptive Medications') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_5 = self.make_qstring('Diagnosis, Active: Inflammatory Diseases of Female Reproductive Organs') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_6 = self.make_qstring('Diagnosis, Active: Chlamydia') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_7 = self.make_qstring('Diagnosis, Active: HIV') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_8 = self.make_qstring('Diagnosis, Active: Syphilis') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        diagQ_9 = self.make_qstring('Diagnosis, Active: Complications of Pregnancy, Childbirth and the Puerperium') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        #labQ_1 is involved in the exclusion rule, so it has to be built differently
        labQ_2 = self.make_qstring('Laboratory Test, Order: Pap Test') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        labQ_3 = self.make_qstring('Laboratory Test, Order: Lab Tests During Pregnancy') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        labQ_4 = self.make_qstring('Laboratory Test, Order: Lab Tests for Sexually Transmitted Infections') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        procQ_1 = self.make_qstring('Procedure, Performed: Delivery Live Births') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        procQ_2 = self.make_qstring('Diagnostic Study, Order: Diagnostic Studies During Pregnancy') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        procQ_3 = self.make_qstring('Procedure, Performed: Procedures During Pregnancy') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        procQ_4 = self.make_qstring('Procedure, Performed: Procedures Involving Contraceptive Devices') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        medQ_1 = self.make_qstring('Medication, Order: Contraceptive Medications') \
               + " and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        #these queries have to be joined based on relative date values, so date is included
        labQ_1 = "select distinct patient_id, date from qmetric_criteria where critname='Laboratory Test, Order: Pregnancy Test' and cmsname='" + self.cmsname \
               + "' and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        exclQ_1 = "select distinct patient_id, date from qmetric_criteria where critname='Medication, Order: Isotretinoin' and cmsname='" + self.cmsname \
               + "' and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
        exclQ_2 = "select distinct patient_id, date from qmetric_criteria where critname='Diagnostic Study, Order: X-Ray Study (all inclusive)' and cmsname='" + self.cmsname \
               + "' and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"
               
        headrQ = 'select age.patient_id ' 
        denomQ = ' from (' + ageQ + ') age  ' \
              + ' inner join (select * from (' + encQ_1 + ') enc1 ' \
                   + ' union select * from (' + encQ_2 + ') enc2 ' \
                   + ' union select * from (' + encQ_3 + ') enc3 ' \
                   + ' union select * from (' + encQ_4 + ') enc4 ' \
                   + ' union select * from (' + encQ_5 + ') enc5 ' \
                   + ' union select * from (' + encQ_6 + ') enc6 ' \
                   + ' union select * from (' + encQ_7 + ') enc7 ) enc on age.patient_id=enc.patient_id ' \
              + 'inner join (select * from (' + diagQ_1 + ') diag1 ' \
                   + ' union select * from (' + diagQ_2 + ') diag2 ' \
                   + ' union select * from (' + diagQ_3 + ') diag3 ' \
                   + ' union select * from (' + diagQ_4 + ') diag4 ' \
                   + ' union select * from (' + diagQ_5 + ') diag5 ' \
                   + ' union select * from (' + diagQ_6 + ') diag6 ' \
                   + ' union select * from (' + diagQ_7 + ') diag7 ' \
                   + ' union select * from (' + diagQ_8 + ') diag8 ' \
                   + ' union select * from (' + diagQ_9 + ') diag9 ' \
                   + ' union select distinct lab1.patient_id from (' + labQ_1 + ') lab1 ' \
                       + ' where not exists (select null from (' + exclQ_1 + ') excl1 where excl1.patient_id=lab1.patient_id and (excl1.date-lab1.date between 0 and 7) ) ' \
                       + ' and not exists (select null from (' + exclQ_2 + ') excl1 where excl1.patient_id=lab1.patient_id and (excl1.date-lab1.date between 0 and 7) ) ' \
                   + ' union select * from (' + labQ_2 + ') lab2 ' \
                   + ' union select * from (' + labQ_3 + ') lab3 ' \
                   + ' union select * from (' + labQ_4 + ') lab4 ' \
                   + ' union select * from (' + procQ_1 + ') proc1 ' \
                   + ' union select * from (' + procQ_2 + ') proc2 ' \
                   + ' union select * from (' + procQ_3 + ') proc3 ' \
                   + ' union select * from (' + procQ_4 + ') proc4 ' \
                   + ' union select * from (' + medQ_1 + ') med1 ) diag on age.patient_id=diag.patient_id '
        labQ_5 = "select distinct patient_id from qmetric_criteria where critname='Laboratory Test, Result: Chlamydia Screening' and cmsname='" + self.cmsname \
               + "' and date between '" + self.pstart.strftime('%Y-%m-%d') + "'::date and '" + self.pend.strftime('%Y-%m-%d') + "'::date"

        denomlist = Criteria.critpats.getqdata(headrQ+denomQ)
        dcounts = self.loadPop(denomlist,'denominator')
        numQ = denomQ + ' inner join (' + labQ_5 + ') numr on age.patient_id=numr.patient_id ' 
        numlist = Criteria.critpats.getqdata(headrQ+numQ)
        ncounts = self.loadPop(numlist,'numerator')
        return ncounts, dcounts
    
    def genres(self):
        '''
        Generate results and load to result table
        '''
        baseQ = ' select pat.ethnicity, pat.race, pop.etype, case ' \
                 + " when pat.date_of_birth::date < '" + (self.pstart-relativedelta(years=21)).strftime('%Y-%m-%d') + "'::date then '16-20' " \
                 + " when pat.date_of_birth::date >= '" + (self.pstart-relativedelta(years=21)).strftime('%Y-%m-%d') + "'::date then '21-24' end as age_groups " \
                 + ' from qmetric_population pop join emr_patient pat on pat.id=pop.patient_id ' \
                 + " where pop.cmsname ='" + self.cmsname + "' and pop.periodstartdate='" \
                 + self.pstart.strftime('%Y-%m-%d') + "'::date and pop.periodenddate='" + self.pend.strftime('%Y-%m-%d') + "'::date "
        denomQ = 'select count(*) as denominator, ' \
                 + ' ethnicity, race, age_groups ' \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' " \
                 + ' group by ethnicity, race, age_groups ' \
                 + ' union all select count(*) as denominator, ' \
                 + " ethnicity, race, 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' " \
                 + ' group by ethnicity, race ' \
                 + ' union all select count(*) as denominator, ' \
                 + " ethnicity, 'all', age_groups " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' " \
                 + ' group by ethnicity, age_groups ' \
                 + ' union all select count(*) as denominator, ' \
                 + " 'all', race, age_groups " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' " \
                 + ' group by race, age_groups ' \
                 + ' union all select count(*) as denominator, ' \
                 + " ethnicity, 'all', 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' " \
                 + ' group by ethnicity ' \
                 + ' union all select count(*) as denominator, ' \
                 + " 'all', race, 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' " \
                 + ' group by race ' \
                 + ' union all select count(*) as denominator, ' \
                 + " 'all', 'all', age_groups " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' " \
                 + ' group by age_groups ' \
                 + ' union all select count(*) as denominator, ' \
                 + " 'all', 'all', 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='denominator' "  
        numerQ = 'select count(*) as numerator, ' \
                 + ' ethnicity, race, age_groups ' \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' " \
                 + ' group by ethnicity, race, age_groups ' \
                 + ' union all select count(*) as numerator, ' \
                 + " ethnicity, race, 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' " \
                 + ' group by ethnicity, race ' \
                 + ' union all select count(*) as numerator, ' \
                 + " ethnicity, 'all', age_groups " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' " \
                 + ' group by ethnicity, age_groups ' \
                 + ' union all select count(*) as numerator, ' \
                 + " 'all', race, age_groups " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' " \
                 + ' group by race, age_groups ' \
                 + ' union all select count(*) as numerator, ' \
                 + " ethnicity, 'all', 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' " \
                 + ' group by ethnicity ' \
                 + ' union all select count(*) as numerator, ' \
                 + " 'all', race, 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' " \
                 + ' group by race ' \
                 + ' union all select count(*) as numerator, ' \
                 + " 'all', 'all', age_groups " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' " \
                 + ' group by age_groups ' \
                 + ' union all select count(*) as numerator, ' \
                 + " 'all', 'all', 'all' " \
                 + ' from (' + baseQ + ') t1 ' + " where etype='numerator' "  
        cubeQ = "select '" + self.cmsname + "' as cmsname, d.denominator, (case when n.numerator is not null then n.numerator when d.denominator is not null then 0 else null end) numerator, " \
                 + " (case when n.numerator is not null then n.numerator when d.denominator is not null then 0 else null end)/d.denominator::float as rate, " \
                 + " d.ethnicity || ' | ' || d.race || ' | ' || d.age_groups as stratification, '" \
                 + self.pstart.strftime('%Y-%m-%d') + "'::date as periodstartdate, '" + self.pend.strftime('%Y-%m-%d') + "'::date as periodenddate " \
                 + ' from (' + denomQ + ') as d left join (' + numerQ + ') as n on d.ethnicity=n.ethnicity and d.race=n.race and d.age_groups=n.age_groups'
        rescurs = connection.cursor()
        rescurs.execute(cubeQ)
        count=0
        for r in rescurs:
            res = Results(cmsname=r[0], denominator=r[1], numerator=r[2],rate=r[3], stratification=r[4],
                          periodstartdate=r[5], periodenddate=r[6]) 
            res.save()
            count+=1
        return count
    
class PivotQueryGen:
    '''
    Methods for generating pivot query for results
    '''
    def __init__(self,tfield,cfield,rfield1,wcrit1,wcrit2):
        '''
        t field is the value field that get's transposed
        c field is the field that defines new column names
        r field1 is row fields that stays as is (anticipating later addition of more potential row fields)
        wcrit1, wcrit2 are the where values for ethnicity (1) and race (2) -- this will need more work to be more data dynamic
        '''
        self.tfield=tfield
        self.cfield=cfield
        self.rfield1=rfield1
        filterby = "where split_part(stratification,' | ',1)='" + wcrit1 +"'" + " and split_part(stratification,' | ',2)='" + wcrit2 +"'"
        self.basesql = ("select trim(to_char(numerator,'9999999'))||'/'||trim(to_char(denominator,'9999999'))||'='||trim(to_char(round(rate::numeric,2),'0D99')) rate, "
                     + "split_part(stratification,' | ',1) ethnicity, "
                     + "split_part(stratification,' | ',2) race, "
                     + "split_part(stratification,' | ',3) age_group, "
                     + "to_char(periodstartdate,'Monddyy')||'_'||to_char(periodenddate,'Monddyy') period "
                     + "from qmetric_results " + filterby)
    
    def subsql(self, cval):
        '''
        builds the individual component to be joined
        '''
        sqltxt = ('select ' + self.tfield + ' ' + cval + ', ' + self.rfield1  
                 + " from (" + self.basesql + ") " + cval + " where period='" + cval +"'")
        return sqltxt
    
    def rowsql(self):
        sqltxt = 'select distinct ' + self.rfield1 + ' from (' + self.basesql +') rows '
        return sqltxt
    
    def displayquery(self):
        cval_qs = Results.objects.distinct('periodstartdate','periodenddate')
        i=0
        cols=[]
        for row in cval_qs:
            cval = row.periodstartdate.strftime('%b%d%y')+'_'+row.periodenddate.strftime('%b%d%y')
            cols.append(cval)
            if i==0:
                q0 = 'select '
                q1 = ' from (' + self.rowsql() + ') t0'
                i+=1
            q0 = q0 + 't' + str(i) + '.' + cval + ', '
            q1 = q1 + ' left join (' + self.subsql(cval) + ') t' + str(i) + ' on t0.' + self.rfield1 + '=t' + str(i) + '.' + self.rfield1 
            i+=1
        cols.append(self.rfield1)
        q0 = q0 + 't0.' + self.rfield1 
        q = q0 + q1
        return q, cols
        