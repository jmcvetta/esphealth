import random
import string

from ESP.esp.models import Provider, Demog, Enc
from ESP.esp.models import Immunization

from ESP.conf.models import Icd9

from ESP.utils import randomizer





class CareProvider():
    POPULATION_SIZE = 100

    @staticmethod
    def clear():
        print 'Clearing Providers'
        for p in Provider.objects.filter(id__lte=CareProvider.POPULATION_SIZE):
            p.delete()

        

        print 'Providers Cleared'
            
    @staticmethod
    def make_fakes():
        for i in xrange(0, CareProvider.POPULATION_SIZE):
            p = Provider(
                provCode = 'FAKE-%05d' % i,
                provLast_Name = randomizer.first_name(),
                provFirst_Name = randomizer.last_name(),
                provMiddle_Initial = random.choice(string.uppercase),
                provTitle = 'Fake Dr.',
                provPrimary_Dept = 'Department of Wonderland',
                provPrimary_Dept_Address_1 = randomizer.address(),
                provPrimary_Dept_Zip = randomizer.zip_code(),
                provTel = randomizer.phone_number()
                )
            p.id = i
            p.save()
            print 'saving %s: Id=%s' % (p, p.pk)


class Patient():
    POPULATION_SIZE = 2000

    @staticmethod
    def clear():
        Demog.objects.filter(id__lte=Patient.POPULATION_SIZE).delete()
            
    @staticmethod
    def make_fakes():
        for i in xrange(Patient.POPULATION_SIZE):
            phone_number = randomizer.phone_number()
            address = randomizer.address()
            city = randomizer.city()

            p = Demog(
                DemogPatient_Identifier = 'FAKE-%05d' % i,
                DemogMedical_Record_Number = 'FAKE-%d%s' % (
                    i, randomizer.string()),
                DemogLast_Name = randomizer.last_name(),
                DemogFirst_Name = randomizer.first_name(),
                DemogSuffix = '',
                DemogCountry = 'United States',
                DemogCity = city[0],
                DemogState = city[1],
                DemogZip = randomizer.zip_code(),
                DemogAddress1 = address,
                DemogAddress2 = '',
                DemogMiddle_Initial = random.choice(string.uppercase),
                DemogDate_of_Birth = randomizer.date_of_birth(as_string=True),
                DemogGender = randomizer.gender(),
                DemogRace = randomizer.race(),
                DemogAreaCode = phone_number.split('-')[0],
                DemogTel = phone_number[4:],
                DemogExt = '',
                DemogSSN = randomizer.ssn(),
                DemogMaritalStat = randomizer.marital_status(),
                DemogReligion = '',
                DemogAliases = '',
                DemogHome_Language = '',
                DemogMotherMRN = '',
                DemogDeath_Date = '',
                DemogDeath_Indicator = '',
                DemogOccupation = ''
                )
            p.id = i
            p.save()
            print 'saving %s: Id=%s' % (p, p.pk)


def encounters():
    pass

    
def fake_world():
    pass


if __name__ == '__main__':
    for klass in [CareProvider, Patient]:
        klass.make_fakes()

