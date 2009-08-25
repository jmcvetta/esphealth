import datetime

from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType

from ESP.emr.models import Encounter
from ESP.hef.core import BaseHeuristic, EncounterHeuristic
from ESP.hef.models import Run
from ESP.static.models import Icd9
from ESP.utils.utils import log

from ESP.ss.models import NonSpecialistVisitEvent, Site

from definitions import ICD9_FEVER_CODES
from definitions import influenza_like_illness, haematological, lesions, rash
from definitions import lymphatic, lower_gi, upper_gi, neurological, respiratory

# According to the specs, all of the syndromes have their specific
# lists of icd9 codes that are always required as part of the
# definition. They could've been simply defined as encounter
# heuristics, except for the fact that some might require a fever
# measurement, and ILI always required a fever to be reported. (Either
# through an icd9 code indicating fever, or through a measured
# temperature).

# So, we're creating two classes for Syndromic
# Surveillance. InfluenzaHeuristic is for events that are defined by a
# set of icd9 and always a fever. OptionFeverHeuristic is for events that
# have a set of icd9s and that a fever *may* be required, depending on
# the icd9 code.

# The definitions that rely only on a set of icd9s (no fever) are just
# instantiated as regular SyndromeHeuristics.


class SyndromeHeuristic(EncounterHeuristic):
    def generate_events(self, incremental=True, **kw):
        encounter_type = ContentType.objects.get_for_model(Encounter)
        for encounter in self.matches():
            try:
                site = Site.objects.get(code=encounter.native_site_num)
            except:
                site = None
                
            try:
                NonSpecialistVisitEvent.objects.get_or_create(
                    heuristic_name = self.heuristic_name,
                    encounter = encounter,
                    date = encounter.date,
                    patient = encounter.patient,
                    definition = self.def_name,
                    def_version = self.def_version,
                    patient_zip_code = encounter.patient.zip[:10].strip(),
                    reporting_site = site,
                    object_id = encounter.id,
                    defaults = {
                        'content_type':encounter_type
                        }
                    )
            except Exception, why:
                import pdb
                pdb.set_trace()
    


    def from_site_zip(self, zip_code):
        return NonSpecialistVisitEvent.objects.filter(
            heuristic_name=self.heuristic_name,
            reporting_site__zip_code=zip_code)
    
    def from_locality(self, zip_code):
        return NonSpecialistVisitEvent.objects.filter(
            heuristic_name=self.heuristic_name,
            patient_zip_code=zip_code)
    
        

    def counts_by_age_range(self, lower, upper=150, **kw):
        '''
        returns the count of occurances of this event, that occur with
        patients only on the date range defined by lower and upper.
        Can also break it by zip code and by date.
        '''
        
        date = kw.get('date', None)
        locality_zip_code = kw.get('locality_zip_code', None)
        site_zip_code = kw.get('site_zip_code', None)

        today = datetime.date.today()
        
        younger_patient_date = datetime.date(year=(today.year - abs(lower)), 
                                     month=today.month, day=today.day)
        older_patient_date = datetime.date(year=(today.year - abs(upper)), 
                                   month=today.month, day=today.day)

        events = NonSpecialistVisitEvent.objects.filter(
            heuristic_name=self.heuristic_name, 
            patient__date_of_birth__gte=older_patient_date,
            patient__date_of_birth__lt=younger_patient_date)

        if date:
            events = events.filter(date=date)

        if locality_zip_code:
            events = events.filter(patient_zip_code=locality_zip_code)

        if site_zip_code:
            events = events.filter(reporting_site__zip_code=site_zip_code)

        return events.count()


class InfluenzaHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0 # Temperature in Fahrenheit
    def matches(self, begin_timestamp=None):
        q_measured_fever = Q(temperature__gte=InfluenzaHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_fever = Q(temperature__isnull=True, icd9_codes__in=ICD9_FEVER_CODES)
        q_codes = Q(icd9_codes__in=self.icd9s)
        
        # Make it really readable. 
        # (icd9 code + measured fever) or (icd9 code + icd9code for fever)
        # Logically: (a&b)+(a&c) = a&(b+c)
        influenza = (q_codes & (q_measured_fever | q_unmeasured_fever))
        return self.encounters(begin_timestamp).filter(influenza)

                
class OptionalFeverSyndromeHeuristic(SyndromeHeuristic):
    FEVER_TEMPERATURE = 100.0
    def __init__(self, heuristic_name, def_name, def_version, icd9_fever_map):
        # The only reason why we are overriding __init__ is because
        # each the heuristic depends on the icd9 as well as if a fever
        # is required for that icd9.
        super(OptionalFeverSyndromeHeuristic, self).__init__(heuristic_name, def_name, 
                                                def_version, icd9_fever_map.keys())
        self.required_fevers = icd9_fever_map

    def matches(self, begin_timestamp=None):
        icd9_requiring_fever = [code for code, required in self.required_fevers.items() if required]
        icd9_non_fever = [code for code, required in self.required_fevers.items() if not required]

        
        q_measured_fever = Q(temperature__gte=OptionalFeverSyndromeHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_fever = Q(temperature__isnull=True, icd9_codes__in=ICD9_FEVER_CODES)

        q_fever_requiring_codes = Q(icd9_codes__in=icd9_requiring_fever)
    
        fever_requiring = (q_fever_requiring_codes & (q_measured_fever | q_unmeasured_fever))
        non_fever_requiring = Q(icd9_codes__in=icd9_non_fever)
        
        return self.encounters(begin_timestamp).filter(fever_requiring | non_fever_requiring)
            



ili = InfluenzaHeuristic('influenza like illness', 'ILI', 1, 
                         dict(influenza_like_illness).keys())
    
haematological = OptionalFeverSyndromeHeuristic(
    'Haematological', 'haematological', 1, dict(haematological))

lymphatic = OptionalFeverSyndromeHeuristic('Lymphatic', 'lymphatic', 
                                           1, dict(lymphatic))

rash = OptionalFeverSyndromeHeuristic('Rash', 'rash', 1, dict(rash))
    
lesions = SyndromeHeuristic('Lesions', 'lesions', 1, dict(lesions).keys())
respiratory = SyndromeHeuristic('Respiratory', 'respiratory', 1, 
                                dict(respiratory).keys())

lower_gi = SyndromeHeuristic('Lower GI', 'lower gi', 1, 
                             dict(lower_gi).keys())

upper_gi = SyndromeHeuristic('Upper GI', 'uppper gi', 1, dict(upper_gi).keys())

neuro = SyndromeHeuristic('Neurological', 'neurological', 1, dict(neurological).keys())


def syndrome_heuristics():
    return {
        'ili':ili,
        'haemotological':haematological,
        'lymphatic':lymphatic,
        'rash':rash,
        'lesions':lesions,
        'respiratory':respiratory,
        'lower_gi':lower_gi,
        'upper_gi':upper_gi,
        'neuro':neuro
    }

