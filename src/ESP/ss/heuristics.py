import datetime

from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType

from ESP.hef.core import BaseHeuristic, EncounterHeuristic
from ESP.hef.models import Run
from ESP.static.models import Icd9
from ESP.utils.utils import log

from ESP.ss.models import NonSpecialistVisitEvent, Site


from definitions import ICD9_FEVER_CODES
from definitions import influenza_like_illness, haematological, lesions, lymphatic, lower_gi
from definitions import upper_gi, neurological, rash, respiratory

# According to the specs, all of the syndromes have their specific
# lists of icd9 codes that are always required as part of the
# definition. They could've been simply defined as encounter
# heuristics, except for the fact that some might require a fever
# measurement, and ILI always required a fever to be reported. (Either
# through an icd9 code indicating fever, or through a measured
# temperature).

# So, we're creating two classes for Syndromic
# Surveillance. InfluenzaHeuristic is for events that are defined by a
# set of icd9 and always a fever. SyndromeHeuristic is for events that
# have a set of icd9s and that a fever *may* be required, depending on
# the icd9 code.

# The definitions that rely only on a set of icd9s (no fever) are just
# instantiated as regular EncounterHeuristics.


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
                    date = encounter.date,
                    patient = encounter.patient,
                    definition = self.def_name,
                    def_version = self.def_version,
                    patient_zip_code = encounter.patient.zip,
                    reporting_site = site,
                    defaults = {
                        'content_type':encounter_type,
                        'object_id':encounter.id
                        }
            except:
                import pdb
                pdb.set_trace()
    


    def counts_by_site_zip(self, zip_code=None, date=None):
        events = NonSpecialistVisitEvent.objects.filter(
            heuristic_name=self.heuristic_name)

        if zip_code: 
            events = events.filter(reporting_site__zip_code=zip_code)
        if date: events = events.filter(date=date)

        return events.annotate(total=Count('reporting_site__zip_code'))

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
            



ili_syndrome = InfluenzaHeuristic(
    'influenza like illness', 'ILI', 1, dict(influenza_like_illness).keys())

haematological_syndrome = OptionalFeverSyndromeHeuristic(
    'Haematological', 'haematological', 1, dict(haematological))
lymphatic_syndrome = OptionalFeverSyndromeHeuristic(
    'Lymphatic', 'lymphatic', 1, dict(lymphatic))
rash_syndrome = OptionalFeverSyndromeHeuristic(
    'Rash', 'rash', 1, dict(rash))


lesions_syndrome = SyndromeHeuristic(
    'Lesions', 'lesions', 1, dict(lesions).keys())
respiratory_syndrome = SyndromeHeuristic(
    'Respiratory', 'respiratory', 1, dict(respiratory).keys())
lower_gi_syndrome = SyndromeHeuristic(
    'Lower GI', 'lower gi', 1, dict(lower_gi).keys())
upper_gi_syndrome = SyndromeHeuristic(
    'Upper GI', 'uppper gi', 1, dict(upper_gi).keys())
neuro_syndrome = SyndromeHeuristic(
    'Neurological', 'neurological', 1, dict(neurological).keys())

