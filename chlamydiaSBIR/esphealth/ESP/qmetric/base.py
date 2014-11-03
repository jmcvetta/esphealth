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
import abc, xmltodict


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
        self.hqmfdict = xmltodict.parse(file_handle)
        
    def gettype(self):
        mtype=''
        for attribute in self.hqmfdict['QualityMeasureDocument']['subjectOf']:
            try:
                if attribute['measureAttribute']['value']['@displayName']=='Proportion':
                    mtype='Proportion'
                    return mtype
            except:
                #not all the attribute.measureAttribute.value nodes have @displayname values
                continue
        return mtype

class BasePopulationQualifier:
    '''
    Abstract base class for generating Population qualifier events
    '''
    
    @abc.abstractmethod
    def criteria_logic(self,entry):
        '''
        list of combinatorial logic for criteria list and data elements for population inclusion
        @return: a dictionary of Q objects
        @rtype: dictionary
        '''
        
    @abc.abstractmethod
    def qualifierQS(self):
        '''
        use criteria logic and element mapping to create a query set of qualifying results
        @return: a queryset of qualifying results
        @rtype: queryset
        '''
        
    @abc.abstractmethod
    def generate(self):
        '''
        use qualifierQS to generate population qualifying events and their EMRs
        @return: count of events created
        @rtype: integer
        '''
        
class RatioQualifier(BasePopulationQualifier):
    '''
    Generate population qualifying events for ratio (proportion) metrics
    '''
    
    def __init__(self, hqmf_parserobj):
        '''
        here is where the magic works -- call the hqmf parser to define criteria logic
        for named population, using hqmf file and name of population (numerator or denominator)
        [hardcode for now...]
        '''
        components=hqmf_parserobj.hqmfdict['QualityMeasureDocument']['component']
        for component in components:
            if component['section']['title']=='Population criteria':
                criteria = {}
                for entry in component['section']['entry']:
                    criteria.update({entry['observation']['value']['@displayName'], self.criteria_logic(entry)})
        print criteria
                
    def criteria_logic(self,entry):
        '''
        list of combinatorial logic for criteria list and data elements for population inclusion
        @return: a dictionary of Q objects
        @rtype: dictionary
        '''
        
    def qualifierQS(self):
        '''
        use values set in __init__ to create queryset
        '''
        
    def generate(self):
        '''
        generate the results by calling qualifierQS
        '''
    
class ResultGenerator:
    '''
    methods for a command that will populate results table
    '''

        