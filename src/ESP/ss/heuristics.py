import datetime

from django.db.models import Q

from ESP.hef.core import BaseHeuristic, EncounterHeuristic
from ESP.hef.models import Run
from ESP.static.models import Icd9

from ESP.utils.utils import log


class InfluenzaHeuristic(EncounterHeuristic):
    FEVER_TEMPERATURE = 100.0 # Temperature in Fahrenheit
    def matches(self, begin_timestamp=None):
        q_fever = Q(temperature__gte=InfluenzaHeuristic.FEVER_TEMPERATURE)
        q_unmeasured_temperature = Q(temperature__isnull=True)
        q_codes = Q(icd9_codes__in=self.icd9s)
        

        return self.encounters(begin_timestamp).filter(
            q_fever | (q_unmeasured_temperature & q_codes))





