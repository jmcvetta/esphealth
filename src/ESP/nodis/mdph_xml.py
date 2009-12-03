'''
                                  ESP Health
                         Notifiable Diseases Framework
                              MDPH XML Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


VERSION = '2.3.1'

# Information about reporting institution.  This info should be made configurable 
# in reference localsettings.py.
class Foo(): pass
INSTITUTION = Foo()
INSTITUTION.name = 'HVMA'
INSTITUTION.clia = '22D0666230'
INSTITUTION.last_name = '???'
INSTITUTION.first_name = '???'
INSTITUTION.last_name = '???'
INSTITUTION.address1 = '???'
INSTITUTION.address2 = '???'
INSTITUTION.city = '???'
INSTITUTION.state = '???'
INSTITUTION.zip = '???'
INSTITUTION.country = '???'
INSTITUTION.email = '???'
INSTITUTION.area_code = '???'
INSTITUTION.tel = '???'
INSTITUTION.tel_ext = '???'



import time
from lxml import etree

from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.nodis.models import Case


#
# This is used in various places, and needs to be same everywhere
#
ISO_DATE = time.strftime('%Y%m%d%H%M%S',time.localtime())


HL7_RACES = {
    'CAUCASIAN':'W',
    'BLACK':'B',
    'OTHER':'O',
    'HISPANIC': 'W',
    'INDIAN':'I',
    'ASIAN':'A',
    'NAT AMERICAN':'I',
    'NATIVE HAWAI':'P',
    'ALASKAN':'I',
    # '': 'U' # Removed because we handle null race = U in the code
    }


def make_name_element(element, person, is_clinician=False):
    '''
    Returns an Element containing name information.  Element is somewhat 
    different when person is a patient than when person is a provider.
    @param element: Name of the element to be created
    @type element:  String
    @param person: The person described by this element
    @type person:  Patient or Provider object
    @param is_clinician: Is this person treating clinician?
    @type is_clinician:  Boolean
    '''
    e = etree.Element(element)
    if person.first_name:
        first = person.first_name
    else:
        first = 'Unknown'
    if person.last_name:
        last = person.last_name
    else:
        last = 'Unknown'
    try:
        suffix = person.suffix
    except AttributeError:
        suffix = ''
    for data, tag, clinician_tag in [
        (first,  'XCN.2', 'XCN.3'),
        (last,   'XCN.3', 'XCN.4'),
        (suffix, 'XCN.4', 'XCN.5'),
        ]:
        if data:
            if is_clinician:
                etree.SubElement(e, clinician_tag).text = data
            else:
                etree.SubElement(e, tag).text = data
    return e


def make_address_element(element, addr_type, address1, address2, city, state, zip, country):
    '''
    Returns an Element containing address information.
    @param element: Name of the element to be created
    @type element:  String
    @param addr_type: Address type code
    @type addr_type:  String or None
    Remaining elements are all strings; names should be self-explanatory.
    '''
    e = etree.Element(element)
    for data, tag in  [
        (address1,'XAD.1'),
        (address2,'XAD.2'),
        (city,'XAD.3'),
        (state,'XAD.4'), 
        (zip,'XAD.5'),
        (country,'XAD.6'),
        (addr_type,'XAD.7'),
        ]:
        if data:
            etree.SubElement(e, tag).text = data
    return e
        
        
def make_provider_element(provider, addr_type, prov_type, nk_set_id):
    '''
    Returns an Element containing provider information.
    @param addr_type: Address type code
    @type addr_type:  String or None
    @param addr_type: Provider type code
    @type addr_type:  String
    @param nk_set_id: Set ID for this NK record
    @type nk_set_id:  String or Integer
    '''
    #
    # Why are we using NK1 ("Next of Kin") element for provider?  Can this be right??!
    e = etree.Element('NK1')
    etree.SubElement(e, 'NK1.1').text = '%s' % nk_set_id
    e.append( make_name_element('NK1.2', provider, is_clinician=False) ) 
    etree.SubElement(etree.SubElement(e, 'NK1.3'), 'CE.4').text = prov_type
    # WARNING:  We do not keep country data in Provider model.  This script will 
    # always report providers as located in USA.
    addr_element = make_address_element('NK1.4', addr_type=None, address1=provider.dept_address_1, 
        address2=provider.dept_address_2, city=provider.dept_city, state=provider.dept_state, 
        zip=provider.dept_zip, country='USA')
    e.append(addr_element)
    
    outerElement='NK1.5'
    email=''
    ext=''
    contact_element = make_contact_element('NK1.5', email=None, area_code=provider.area_code, tel=provider.telephone, ext=None)
    if contact_element:
        e.append(contact_element)
    return e

    
def make_contact_element(element, email, area_code, tel, ext):
    '''
    Returns an Element containing contact information.
    @param element: Name of the element to be created
    @type element:  String
    Remaining elements are all strings; names should be self-explanatory.
    '''
    # If there's no contact info, nothing to do here
    if not element or email or area_code or tel or ext:
        return None
    for item in (element, email, area_code, tel, ext):
        if item: 
            item = item.strip()
        else:
            item = ''
    e = etree.Element(element)
    for data, tag in [(email,'XTN.4'),(area_code,'XTN.6'),(tel,'XTN.7'),(ext,'XTN.8')]:
        if data:
            etree.SubElement(e, tag).text = data
    return e
    

def compose():
    #
    # Batch root container
    #
    namespace = 'urn:hl7-org:v2xml'
    nsmap = {None: namespace}
    batch = etree.Element('BATCH', nsmap=nsmap)
    #
    # Batch Headers
    #
    fhs = etree.SubElement(batch, 'FHS')
    etree.SubElement(fhs, 'FHS.1').text = '|'
    etree.SubElement(fhs, 'FHS.2').text = '^\&amp;'
    etree.SubElement(fhs, 'FHS.3').text = 'ESP0.001'
    etree.SubElement(fhs, 'FHS.4').text = 'Test'
    etree.SubElement(etree.SubElement(fhs, 'FHS.7'), 'TS.1').text = ISO_DATE
    messagebatch = etree.SubElement(batch, 'MESSAGEBATCH')
    bhs = etree.SubElement(messagebatch, 'BHS')
    etree.SubElement(bhs, 'BHS.1').text = '|'
    etree.SubElement(bhs, 'BHS.2').text = '^\&amp;'
    etree.SubElement(bhs, 'BHS.3').text = 'ESP0.001'
    etree.SubElement(bhs, 'BHS.4').text = 'Test'
    etree.SubElement(etree.SubElement(bhs, 'BHS.7'), 'TS.1').text = ISO_DATE
    messages = etree.SubElement(messagebatch, 'MESSAGES')
    #
    # Message List
    #
    #oru_r01 = etree.Element('ORU_R01')
    #
    #
    #
    #messages.text = etree.CDATA(etree.tostring(oru_r01, pretty_print=True))
    return batch


def encode_case(case):
    '''
    @param case: Case to be encoded in HL7v3
    @type case: Case
    '''
    patient = case.patient
    provider = case.provider
    oru = etree.Element('ORU_R01')
    #
    # Message Header
    #
    msh = etree.SubElement(oru, 'MSH')
    etree.SubElement(msh, 'MSH.1').text = '|'
    etree.SubElement(msh, 'MSH.2').text = '^~\&'
    msh4 = etree.SubElement(msh, 'MSH.4')
    etree.SubElement(msh4, 'HD.1').text = INSTITUTION.name
    etree.SubElement(msh4, 'HD.2').text = INSTITUTION.clia
    etree.SubElement(msh4, 'HD.3').text = 'CLIA'
    etree.SubElement(etree.SubElement(msh, 'MSH.5'), 'HD.1').text = 'MDPH-ELR'
    etree.SubElement(etree.SubElement(msh, 'MSH.6'), 'HD.1').text = 'MDPH'
    etree.SubElement(etree.SubElement(msh, 'MSH.7'), 'TS.1').text = ISO_DATE
    msh9 = etree.SubElement(msh, 'MSH.9')
    etree.SubElement(msh9, 'MSG.1').text = 'ORU'
    etree.SubElement(msh9, 'MSG.2').text = 'R01'
    etree.SubElement(msh, 'MSH.10').text = 'MDPH%s' % ISO_DATE
    # MSH.11, the 'processingFlag', was passed as an argument in the old code.
    # While the only value that code ever passed for it was 'T', nevertheless
    # Ross et al must have thought the value would sometimes be other than 'T'.
    etree.SubElement(etree.SubElement(msh, 'MSH.11'), 'PT.1').text = 'T'
    etree.SubElement(etree.SubElement(msh, 'MSH.12'), 'VID.1').text = VERSION
    #
    #
    #
    oru_sub1 = etree.SubElement(oru, 'ORU_R01.PIDPD1NK1NTEPV1PV2ORCOBRNTEOBXNTECTI_SUPPGRP')
    oru_sub2 = etree.SubElement(oru_sub1, 'ORU_R01.PIDPD1NK1NTEPV1PV2_SUPPGRP')
    #
    # Patient Information
    #
    pid = etree.SubElement(oru_sub2, 'PID')
    etree.SubElement(pid, 'PID.1').text = '1'
    # MRN
    pid3 = etree.SubElement(pid, 'PID.3')
    etree.SubElement(pid3, 'CX.1').text = patient.mrn
    etree.SubElement(pid3, 'CX.5').text = 'MR'
    etree.SubElement(etree.SubElement(pid3, 'CX.6'), 'HD.2').text = provider.dept
    # SSN
    pid3 = etree.SubElement(pid, 'PID.3') # New 'PID.3' section
    etree.SubElement(pid3, 'CX.1').text = patient.ssn[-4:]
    etree.SubElement(pid3, 'CX.5').text = 'SS'
    # Name
    pid.append( make_name_element('PID.5', patient) )
    # DoB  -- do we need to convert date to some specific string format?
    etree.SubElement(etree.SubElement(pid, 'PID.7'), 'TS.1').text = '%s' % patient.date_of_birth
    # Gender
    etree.SubElement(pid, 'PID.8').text = patient.gender
    # Race
    try:
        race = HL7_RACES[patient.race.upper()]
    except:
        race = 'U'
    etree.SubElement(etree.SubElement(pid, 'PID.10'), 'CE.4').text = race
    # Patient Home Address
    addr_element = make_address_element('PID.11', 'H', patient.address1, patient.address2, 
        patient.city, patient.state, patient.zip, patient.country)
    pid.append(addr_element)
    # Patient Telephone
    if patient.tel:
        pid13 = etree.SubElement(pid, 'PID.13')
        etree.SubElement(pid13, 'XTN.6').text = patient.areacode
        etree.SubElement(pid13, 'XTN.7').text = patient.tel
        if patient.tel_ext:
            etree.SubElement(pid13, 'XTN.8').text = patient.tel_ext
    for data, tag in [
        (patient.home_language,'PID.15'),
        (patient.marital_stat,'PID.16'),
        ]:
        if data:
            etree.SubElement(etree.SubElement(pid, tag), 'CE.4').text = data
    if patient.race and patient.race.upper() == 'HISPANIC':
        etree.SubElement(etree.SubElement(pid, 'PID.22'), 'CE.4').text = 'H'
    #
    # PCP
    #
    pid.append( make_provider_element(provider=provider, addr_type='O', prov_type='PCP', nk_set_id=1) )
    #
    # Facility
    #
    facility = etree.SubElement(pid, 'NK1')
    etree.SubElement(facility, 'NK1.1').text = '2'
    facility.append( make_name_element('NK1.2', INSTITUTION, is_clinician=False) )
    etree.SubElement(etree.SubElement(facility, 'NK1.3'), 'CE.4').text = 'FCP'
    address_element = make_address_element('NK1.4', addr_type='O', address1=INSTITUTION.address1, 
        address2=INSTITUTION.address2, city=INSTITUTION.city, state=INSTITUTION.state, 
        zip=INSTITUTION.zip, country=INSTITUTION.country)
    facility.append(address_element)
    contact_element = make_contact_element('NK1.5', email=INSTITUTION.email, 
        area_code=INSTITUTION.area_code, tel=INSTITUTION.tel, ext=INSTITUTION.tel_ext)
    if contact_element: facility.append(contact_element)
    #
    # Treating Clinician
    #
    for clinician in case.prescriptions.values_list('provider', flat=True).distinct():
        oru.append( make_provider_element(clinician, addr_type='O', prov_type='TC', nk_set_id=3) )
    return oru


    




#batch = compose()
#print(etree.tostring(batch, pretty_print=True))

c = Case.objects.all()[0]
print etree.tostring(encode_case(c), pretty_print=True)
