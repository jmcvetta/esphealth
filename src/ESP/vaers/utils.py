from django.contrib.sites.models import Site
from django.db.models import Q

from ESP import settings

import datetime

def make_clustering_event_report_file(filename, events):
    f = open(filename, 'w')
    f.write('\t'.join(['id', 'vdate', 'edate', 'gap', 'vaccine', 
                       'comment', 'age', 'gender']))
    f.write('\n')
    for ev in events:
        f.write(ev.render_temporal_report())
        f.write('\n')
    f.close()

