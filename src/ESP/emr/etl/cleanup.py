'''
                                  ESP Health
                            EMR ETL Infrastructure
ETL Cleanup Tool


The cleanup tool allows operator to remove from the database records with bad
provenance.  


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


import optparse

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from ESP.nodis.models import Case
from ESP.hef.models import HeuristicEvent
from ESP.emr.models import Provenance
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription



def main():
    parser = optparse.OptionParser()
    parser.add_option('--status', action='store', dest='purge', metavar='STATUS',
        help="Purge records with specified whose provenance matches STATUS.  Possible " + \
        "values are 'failure' and 'attempted'.")
    options, args = parser.parse_args()
    #
    # Discover "bad" cases -- those based on events with bad provenance
    #
    prov_stat_q = Q(provenance__status='failure')
    bad_events = None
    rec_type = Prescription
    for rec_type in [LabResult, Encounter, Prescription]:
        content_type = ContentType.objects.get_for_model(rec_type)
        bad_records = rec_type.objects.filter(prov_stat_q)
        new_bad_events = HeuristicEvent.objects.filter(content_type=content_type, object_id__in=bad_records)
        try:
            bad_events = bad_events | new_bad_events
        except TypeError:
            bad_events = new_bad_events
    bad_cases = Case.objects.filter(events__in=bad_events)
    sent_bad_cases = bad_cases.filter(status='S')
        
        

if __name__ == '__main__':
    main()