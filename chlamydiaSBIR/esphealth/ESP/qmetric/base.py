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
#        if 'high' in crit.get('act',{}).get('sourceOf',{}).get('observation',{}).get('sourceOf',{}).get('pauseQuantity',{}):
#            vlist=crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']['high']['@value']
#            if crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']['high']['@inclusive']=='false':
#                opr='lt'
#            else:
#                opr='lte'
#        if 'low' in crit.get('act',{}).get('sourceOf',{}).get('observation',{}).get('sourceOf',{}).get('pauseQuantity',{}):
#            vlist=crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']['low']['@value']
#            if crit['act']['sourceOf']['observation']['sourceOf']['pauseQuantity']['low']['@inclusive']=='false':
#                opr='gt'
#            else:
#                opr='gte'
        ageQ = Q(date__lte=pstart-relativedelta(years=16))
        ageQ = ageQ & Q(date__gt=pstart-relativedelta(years=24))
        ageQ = ageQ & Q(critname='Patient Characteristic Birthdate: birth date')


    
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

        