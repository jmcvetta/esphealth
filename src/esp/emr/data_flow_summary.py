
'''
                                  ESP Health
                         Notifiable Diseases Framework
                            Data Flow Summary Tool


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import csv
import sys
import optparse

from esp.emr.models import Provenance
from esp.emr.models import Provider
from esp.emr.models import Patient
from esp.emr.models import LabResult
from esp.emr.models import Encounter
from esp.emr.models import Prescription
from esp.emr.models import Immunization


def data_flow_summary_generator(provenances=None):
    '''
    Yields dictionary with data flow summary for each provenance
    '''
    if not provenances:
        provenances = Provenance.objects.all().order_by('source')
    for prov in provenances:
        row = {
            'source': prov.source,
            #'timestamp': prov.timestamp,
            'providers': prov.provider_set.count(),
            'patients': prov.patient_set.count(),
            'lab_results': prov.labresult_set.count(),
            'encounters': prov.encounter_set.count(),
            'prescriptions': prov.prescription_set.count(),
            'immunizations': prov.immunization_set.count(),
            }
        yield row


def main():
    # TODO: Add begin/end date options to parser
    parser = optparse.OptionParser()
    (options, args) = parser.parse_args()
    #
    #
    #
    fields = [
        'source',
        'providers',
        'patients',
        'lab_results',
        'encounters',
        'prescriptions',
        'immunizations',
        ]
    outfile = sys.stdout
    writer = csv.DictWriter(outfile, fields, dialect='excel-tab')
    provenances = None # TODO: constrain by date, per opt parser
    writer.writerow( dict(zip(fields, fields)) )
    for row in data_flow_summary_generator(provenances=provenances):
        writer.writerow(row)
    
    
if __name__ == '__main__':
    main()