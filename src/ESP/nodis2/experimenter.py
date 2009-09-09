from ESP.nodis2.defs import chlamydia
import datetime
import pprint
import types
import sets
import sys
import optparse
import re
from operator import itemgetter

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Model
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.hef2 import events
from ESP.hef2.core import BaseHeuristic
from ESP.hef2.models import HeuristicEvent
from ESP.nodis.models import Case
from ESP.nodis2.defs import chlamydia




def main():
    print chlamydia.plausible_patients()


if __name__ == '__main__':
    main()