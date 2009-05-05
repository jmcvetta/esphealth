import os, sys
import datetime, random
import simplejson
import optparse
import string
import pdb

PWD = os.path.dirname(__file__)
PARENT_DIR = os.path.realpath(os.path.join(PWD, '..'))
FIXTURE_DIR = os.path.join(PWD, 'fixtures')

if PARENT_DIR not in sys.path: sys.path.append(PARENT_DIR)

import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from esp.models import Demog, Immunization, Enc, Provider
from esp.models import Vaccine, ImmunizationManufacturer
from esp.models import icd9
from utils import utils

import rules
import diagnostics

# For testing
FIRST_NAMES = ['Bill', 'Mary', 'Jim', 'Donna', 'Patricia', 
               'Susan', 'Robert', 'Barry', 'Bazza', 'Deena', 
               'Kylie', 'Shane', 'John', 'Michael', 'Anne',
               'Spock', 'Kruskal', 'Platt', 'Klompas', 'Lazarus', 
               'Who', 'Nick', 'Livingston', 'Doolittle', 'Casey', 'Finlay'
               ]


LAST_NAMES = ['Bazfar', 'Barfoo', 'Hoobaz', 'Sotbar', 'Farbaz', 
              'Zotbaz', 'Smith', 'Jones', 'Fitz', 'Wong', 'Wright', 
              'Ngyin', 'Miller']


SITES = ['Brookline Ave', 'West Roxbury', 'Matapan', 'Sydney', 'Kansas']
MARITAL_STATUS = ['Single', 'Married', 'Widowed', 'Divorced']
RACES = ['Caucasian', 'Black', 'Asian', 'Hispanic', 'Indian', 
         'Native American', 'Alaskan', 'Other']
STATES = ['MA', 'RI', 'NY', 'CT', 'ME']

CITIES = [ 
    'SOUTH TAMWORTH', 'MIDDLETON', 'GRAPELAND', 'UNCASVILLE', 'W. BOYLSTON', 
    'PROVIDENCE', 'ROCKVILLE', 'EXTON', 'GROTTOES', 'PINE BROOK', 
    'NO FALMOUTH', 'CASPER', 'PAWTUCKET', 'ATHENS', 'NSW', 'BOLINGBROOK', 
    'BOXBOUGH', 'GREAT BARRINGTON', 'EASTBOSTON', 'CENTERDALE', 'SAN CARLOS', 
    'CENTEREACH', 'ST. LOUIS', 'HARWINTON', 'PEEKSKILL', 'NORTHPORT', 
    'BALDWINSVILLE', 'STILL RIVER', 'EAGLE LAKE', 'TEATICKET', 
    'NORTHBRIDGE', 'ALLENSTOWN', 'MARSHFIELD', 'WATERVILLE VALLE', 
    'MATAPAN', 'WALNUT', 'RUSSIA', 'DORCHESTER', 'SKILLMAN', 
    'MOLINE', 'RAYNHAM CENTER', 'NEW YORK CITY', 'URXBRIDGE', 'FRUITPORT', 
    'SPARTANBURG', 'HURST', 'WABAN', 'ORLANDO', 'LAKEVILLE', 'ELLSWORTH', 
    'TURNER''S FALLS', 'RAHWAY', 'WEXFORD', 'OAK HILL', 'BROOKLINE', 
    'DAYTONA BEACH', 'SHAWNEE MISSION', 'WILSON', 'SOTHBORO', 'CAMBRIGDE',
    'LA CRESCENTA', 'ATTLEBORRO', 'N WEYMOUTH','CHELMAFORD', 
    'NORTH HATFIELD', 'WEEMS', 'EAST BRIDGEWATER', 'PROVIDENCE RI', 
    'MORRISTOWN', 'FAIRBURN', 'WOBURN', 'WEST SENECA', 'CLEMMONS', 
    'FORT WAYNE', 'THETFORD', 'NEWTONVILLE', 'MARLBORO MA', 'ST CROIX',
    'MCALLEN', 'DORCESTER', 'BALDWINVILLE', 'YAKIMA', 'S.EASTON', 'ARDMORE',
    'NETHERLANDS', 'GREENLAWN', 'OGDEN', 'N. DIGHTON', 'NO HAVEN', 'WOLLISON',
    'SUMNER', 'NORWWOD', 'WINCHENDON', 'TUCSON', 'RICHMOND HILL', 
    'S. GRAFTON', 'FRAMKLIN', 'CLERMONT', 'LUNENBURG', 'BOSTON'
    ]

ADDRESSES = [
    'COUNTRY FARM RD', 'LOWDEN AVE', 'HIGH ST', 'VINE ST',
    'CLYDE TERR.', 'SHERMAN ST', 'JACKSON TERRACE', 'POND ST',
    'OLD FARM ROAD', 'TRAYER RD', 'SHEPARD ST', 'GROVE ST',
    'CLIFTON RD', 'REVILLA TERRACE', 'WINCHESTER STREET', 
    'CENTRAL ST', 'BENNETT STREET', 'DWIGHT STREET', 
    'GEORGE BROWN STREET', 'WESTVIEW DR', 'BILLINGS AVE', 
    'WHITNEY RD','HOWARD ST', 'BRETTON RD', 'CARLISLE RD',
    'BALOU AVE', 'FERN ST', 'PLEASANT ST', 'MATTAKEESETT ST', 
    'BROOK RD', 'GROVE ST', 'GREENWICH ST', 'EMERALD AVENUE', 
    'BLACKWELL STREET', 'GARVEY RD', 'NIPMUCK DRIVE', 'CENTRAL ST',
    'DONNELLY DR', 'NICHOLAS RD', 'LAKE SHORE ROAD', 'BURLEY ST', 
    'TAUNTON AVE', 'TAURASI RD', 'UMSTEAD HOLLOW PL', 'WHARF ST', 
    'MEADOWS DR', 'FEDERAL WAY', 'VOLUNTEER ROAD', 'ALGONQUIN ROAD',
    'CORDWOOD PATH', 'DELMONT AVENUE', 'WRIGHT FARM RD', 'RANDALL RD',
    'AUDUBON RD', 'CROWDIS ST', 'TREMONT STREET', 'AGREW AVE', 
    'KENNEDY DRIVE', 'CREST ST', 'OLD FARM ROAD', 'SENECA DR.', 
    'BELNAP STREET', 'ASTORIA STREET', 'GROVE STREET', 
    'LITTLETON ROAD', 'BOX 43024', 'UNION ST',
    'CLARK ST', 'HOLDEN STREET', 'SUGAR RD', 'COMMOMWEALTH AVE',
    'PLEASANT STREET', 'CASTLE GREEN ST', 'POPE RD', 
    'HARLOW STREET', 'BEMUTH ROAD', 'HARRISHOF STREET', 
    'W 49TH STREET', 'ANN MARIE DRIVE', 'YORK AVE', 'PEARL ST',
    'GARDNER', 'SNOW CIRCLE', 'CONCORD ST', 'QUEENSBERRY STREET',
    'FLINTLOCK ROAD', 'OCEAN ST', 'COMMONWEALTH AVE', 'MAIN ST',
    'E PROVIDENCE RD', 'DELAWARE AVE', 'MARIE AVE', 
    'TOPICA RD', 'LAUREL HILL LN', 'FOREST ST', 'WHIP O WILL LN', 
    'CEDAR STREET', 'STANLEY AVE', 'ACTON ROAD', 'CASTLE DR'
    ]


POPULATION_SIZE = 1000

class obj():
    pass


# Get a dictionary with a bag of data and write to file.
def write_to_file(filename, fixture):

    def json():
        return simplejson.dumps(fixture, indent=4)

    def sql_script():
        result = []
        for entry in fixture:
            table = entry['model'].replace('.', '_').lower()
            fields = entry['fields']
            fields['id'] = entry['pk']
            
            keys, values = [], []
            for k, v in fields.items():
                keys.append(k)
                values.append(v)
            
            

            outstring = 'INSERT INTO %s (%s) VALUES (%s);' % (
                table, 
                ', '.join([str(x) for x in keys]), 
                ', '.join(["'%s'" % x for x in values])
                )
            
            result.append(outstring)

        return '\n'.join(result)



    action = {
        'json':json,
        'sql':sql_script
        }
        
    f = open(os.path.join(FIXTURE_DIR, filename), 'w')
    file_ext = filename.split('.')[-1]
    contents = action[file_ext]()
    f.write(contents)
    f.close()


def icd9_codes():
    model = 'esp.icd9'
    fixture = []

    for idx, code in enumerate(icd9.objects.all()):
        c = obj()
        c.icd9Code = code.icd9Code
        c.icd9Long = code.icd9Long

        entry = obj() # class to hold fixture data info
        entry.pk = idx
        entry.model = model
        entry.fields = c.__dict__

        fixture.append(entry.__dict__)


    return fixture

    
    


# Our fixtures are bags of data
def patients():
    model = 'esp.Demog'
    fixture = []

    for i in xrange(POPULATION_SIZE):

        p = obj() # class to hold patients attributes
        # Populate with random info
        p.DemogPatient_Identifier = utils.random_string(length=20)
        p.DemogMedical_Record_Number = utils.random_string(length=20)
        p.DemogLast_Name = random.choice(LAST_NAMES)
        p.DemogFirst_Name = random.choice(FIRST_NAMES)
        p.DemogSuffix = ''
        p.DemogCountry = 'United States'
        p.DemogState = random.choice(STATES)
        p.DemogCity = random.choice(CITIES)
        p.DemogZip = '%05d' % random.randrange(1000, 10000)
        p.DemogAddress1 = '%d %s' % (random.randrange(1, 500), random.choice(ADDRESSES))
        p.DemogAddress2 = ''
        p.DemogMiddle_Initial = random.choice(string.uppercase)
        p.DemogDate_of_Birth = (datetime.datetime.now() - datetime.timedelta(
            days=random.randrange(0, 36500),
            minutes=random.randrange(0, 1440),
            seconds=random.randrange(0, 60)
            )).strftime('%Y%m%d')
    
        p.DemogGender = 'M' if random.random() <= 0.49 else 'F'
        p.DemogRace = random.choice(RACES)

        phone_number = utils.random_phone_number()
        p.DemogAreaCode = phone_number.split('-')[0]
        p.DemogTel = phone_number[4:]
        p.DemogExt = ''

        p.DemogSSN = utils.random_ssn()


        p.DemogMaritalStat = random.choice(MARITAL_STATUS)
        p.DemogReligion = ''
        p.DemogAliases = ''
        p.DemogHome_Language = ''
        p.DemogMotherMRN = ''
        p.DemogDeath_Date = ''
        p.DemogDeath_Indicator = ''
        p.DemogOccupation = ''

        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        p.createdDate = now_str
        p.lastUpDate = now_str

        entry = obj() # class to hold fixture data info
        entry.pk = i
        entry.model = model
        entry.fields = p.__dict__

        fixture.append(entry.__dict__)


    return fixture

    

def providers():
    fixture = []
    model = 'esp.Provider'

    for i in xrange(POPULATION_SIZE/10):
        p = obj()
        p.provCode = utils.random_string(length=10)
        p.provLast_Name = random.choice(LAST_NAMES)
        p.provFirst_Name = random.choice(FIRST_NAMES)
        p.provMiddle_Initial = random.choice(string.uppercase)
        p.provTitle = random.choice(['Dr.', 'M.D', 'Ph.D', ''])
        p.provPrimary_Dept = department = 'MCIR VIM LHD Site' # kind of value should go here
                
        p.provPrimary_Dept_Address_1 = ' '.join([str(random.randrange(1000)), 
                                       random.choice(ADDRESSES)])
        p.provPrimary_Dept_Zip = '%05d' % random.randrange(90000)
        p.provTel = utils.random_phone_number()
    
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        p.createdDate = now_str
        p.lastUpDate = now_str

        entry = obj() # class to hold fixture data info
        entry.pk = i
        entry.model = model
        entry.fields = p.__dict__

        fixture.append(entry.__dict__)


    return fixture

def immunizations():
    
    model = 'esp.Immunization'
    fixture = []
    vaccines = Vaccine.objects.all()
    manufacturers = ImmunizationManufacturer.objects.all()

    now = datetime.datetime.now()
    
    pk = 0

    for i in xrange(POPULATION_SIZE):
        imm = obj()
        patient = Demog.objects.get(id=i)
        
        patient_dob = datetime.datetime.strptime(patient.DemogDate_of_Birth, '%Y%m%d')
        date_vaccinated = patient_dob + datetime.timedelta(days=60)
    

        for j in xrange(10): # We're giving 10 shots for each patient
            try:
                assert(now > date_vaccinated)
                imm.ImmPatient = i
                
                vaccine = random.choice(vaccines)
                manuf = random.choice(manufacturers)
                imm.ImmType = vaccine.code
                imm.ImmRecId = 'TEST-%s' % patient.DemogPatient_Identifier
                imm.ImmName = vaccine.short_name
                imm.ImmDate = date_vaccinated.strftime('%Y%m%d')
                imm.ImmDose = '0.%d %s' % (
                    (0.25 * random.randrange(10)), 
                    random.choice(['cc', 'ml'])
                    )
                imm.ImmManuf = random.choice(manufacturers).full_name
                imm.ImmLot = utils.random_string(length=6)
                imm.ImmVisDate = date_vaccinated.strftime('%Y%m%d')

                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                imm.createdDate = now_str
                imm.lastUpDate = now_str

                entry = obj()
                entry.pk = pk

                entry.model = model
                entry.fields = imm.__dict__
                fixture.append(entry.__dict__)
                
                # Every thing went fine. 
                pk += 1
                date_vaccinated += datetime.timedelta(
                    days=random.randrange(7)
                    )

            except Exception, why:
                pass



    return fixture
                

def encounters():
    # We'll make random encounters with indication of fever events or 
    # diagnostics with icd9 that may represent an adverse event

    FEVER_PCT = 85
    DIAGNOSTICS_PCT = 100 - FEVER_PCT
    model = 'esp.Enc'
    fixture = []
    now = datetime.datetime.now()
    
    diagnostics_codes = list(diagnostics.VAERS_DIAGNOSTICS_CODES)
    pk = 0

    for i in xrange(POPULATION_SIZE):
        patient = Demog.objects.get(id=i)
        patient_mnr = patient.DemogMedical_Record_Number
        patient_dob = datetime.datetime.strptime(patient.DemogDate_of_Birth, '%Y%m%d')
        first_encounter = patient_dob + datetime.timedelta(days=60)
        provider = (patient.DemogProvider and patient.DemogProvider) or None
    

        imms = Immunization.objects.filter(ImmPatient=patient)

        for imm in imms:
            try:
                enc = obj()
                imm_date = datetime.datetime.strptime(imm.ImmDate, '%Y%m%d')
                time_delta = datetime.timedelta(
                    days=random.randrange(rules.TIME_WINDOW_POST_EVENT))
                
                when = imm_date + time_delta
                assert(now > when)
                enc.EncPatient = i
                enc.EncMedical_Record_Number = patient_mnr
                
                EncEncounter_ID=utils.random_string(length=10)
                
                if random.randrange(100) <= FEVER_PCT:
                    temp =  101 + float(random.randrange(-5, 5))/10
                    icd9_codes = ''
                else:
                    # Instead of a fever event, let's make this a
                    # diagnostics event. Temp is below fever, with
                    # some small variance.
                    temp =  98 - float(random.randrange(-2, 2))/10
                    icd9_codes = random.choice(diagnostics_codes).strip()

                enc.EncTemperature = temp
                enc.EncICD9_Codes = icd9_codes
                
                enc.EncCPT_codes = ''
                enc.EncEDC = ''
                enc.EncEncounter_SiteName = ''
                enc.EncEncounter_Status = 'TEST'
                enc.EncEvent_Type = 'TEST'
                enc.EncEncounter_Date = when.strftime('%Y%m%d')
                enc.EncEncounter_ClosedDate = when.strftime('%Y%m%d')
                enc.EncEncounter_Provider = provider and provider.id or 0
                enc.EncPregnancy_Status = ''
                
                
                now_str = now.strftime('%Y-%m-%d %H:%M')
                enc.createdDate = now_str
                enc.lastUpDate = now_str

                entry = obj()
                entry.pk = pk

                entry.model = model
                entry.fields = enc.__dict__
                fixture.append(entry.__dict__)
                
                # Every thing went fine. 
                pk += 1

            except Exception, why:
                print why



    return fixture


def lab_results():
    model = 'esp.Lx'
    fixture = []
    now = datetime.datetime.now()
    
    lab_tests = rules.VAERS_LAB_RESULTS
    pk = 0

    def find_trigger_value(lab_test):
        # lab_test is a list of dictionaries that contains the rules 
        # that define trigger values, units exclusion rules, etc.
        # We get one of these rules and find an according value
        rule = random.choice(lab_test)
        trigger = rule['trigger']
        assert ('>' in trigger or '<' in trigger)
        if '>' in trigger:
            value =  2 * float(trigger.split('>')[-1])
        else:
            value = 0.5 * float(trigger.split('<')[-1])

        return {
            'value':value,
            'unit':rule['unit']
            }

    for i in xrange(POPULATION_SIZE):
        patient = Demog.objects.get(id=i)
        patient_mnr = patient.DemogMedical_Record_Number
        patient_dob = datetime.datetime.strptime(patient.DemogDate_of_Birth, '%Y%m%d')
        first_lx = patient_dob + datetime.timedelta(days=60)
        provider = (patient.DemogProvider and patient.DemogProvider) or None
    

        imms = Immunization.objects.filter(ImmPatient=patient)

      
        for imm in imms:
      
            try:
                lx = obj()
                lab_type = random.choice(lab_tests.keys())
                lab_test = lab_tests[lab_type]
                imm_date = datetime.datetime.strptime(imm.ImmDate, '%Y%m%d')
                time_delta = datetime.timedelta(
                    days=random.randrange(rules.TIME_WINDOW_POST_EVENT))
                
                when = imm_date + time_delta
                assert(now > when)
                lx.LxPatient = patient.id
                lx.LxMedical_Record_Number = patient_mnr
                
                
                lx.LxOrder_Id_Num = 'TEST_%d' % pk
                lx.LxTest_Code_CPT = ''
                lx.LxTest_Code_CPT_mod = ''
                lx.LxOrderDate = when.strftime('%Y%m%d')
                lx.LxOrderType = 'Testing'
                lx.LxOrdering_Provider = (provider and provider.id) or 0
                lx.LxDate_of_result = (when + datetime.timedelta(
                        days=random.randrange(2, 7))).strftime('%Y%m%d')
            
                lab_result = find_trigger_value(lab_test)
       
                lx.LxComponentName = lab_type.upper()
                lx.LxTest_results = str(lab_result['value'])
                lx.LxReference_Unit = str(lab_result['unit'])
                
            
                now_str = now.strftime('%Y-%m-%d %H:%M')
                lx.createdDate = now_str
                lx.lastUpDate = now_str
                
                entry = obj()
                entry.pk = pk
                entry.model = model
                entry.fields = lx.__dict__
                fixture.append(entry.__dict__)
                
                # Every thing went fine. 
                pk += 1
                
            except AssertionError:
                pass

    return fixture


def main():
    parser = optparse.OptionParser()
    parser.add_option('-e', '--events', action='store_true', dest='events',
        help='Generate heuristic events')
    parser.add_option('-c', '--cases', action='store_true', dest='cases',
        help='Generate new cases')
    parser.add_option('-u', '--update-cases', action='store_true', dest='update',
        help='Update cases')
    parser.add_option('-a', '--all', action='store_true', dest='all', 
        help='Generate heuristic events, generate new cases, and update existing cases')
    parser.add_option('--begin', action='store', dest='begin', type='string', 
        metavar='DATE', help='Analyze time window beginning at DATE')
    parser.add_option('--end', action='store', dest='end', type='string', 
        metavar='DATE', help='Analyze time window ending at DATE')
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    #
    # Date Parser
    #
    date_format = '%d-%b-%Y'
    if options.begin:
        options.begin = datetime.datetime.strptime(options.begin, date_format).date()
    if options.end:
        options.end = datetime.datetime.strptime(options.end, date_format).date()
    #
    # Main Control block
    #
    if options.all: # '--all' is exactly equivalent to '--events --cases --update-cases'
        options.events = True
        options.cases = True
        options.update = True
    if options.events:
        BaseHeuristic.generate_all_events(begin_date=options.begin, end_date=options.end)
    if options.cases:
        BaseDiseaseDefinition.generate_all_cases(begin_date=options.begin, end_date=options.end)
    if options.update:
        BaseDiseaseDefinition.update_all_cases(begin_date=options.begin, end_date=options.end)
    if not (options.events or options.cases or options.update):
        parser.print_help()



if __name__ == "__main__":
    main()
#    write_to_file('patients.json', patients())    
#    write_to_file('providers.json', providers())
#    write_to_file('immunizations.json', immunizations())
#    write_to_file('encounters.json', encounters())
#    write_to_file('lab_results.json', lab_results())
#    write_to_file('icd9.json', icd9_codes())


