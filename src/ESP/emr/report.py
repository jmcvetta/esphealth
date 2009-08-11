import os

from ESP.emr.models import Patient


DOC_FOLDER = os.path.join(os.path.abspath('.'), 'assets', 'documents')

if __name__ == '__main__':
    print 'Creating summary documents for %d patients' % Patient.objects.count()
    for p in Patient.objects.all():
        f = open(os.path.join(DOC_FOLDER, 'patient.%d.%s.json' % (p.pk, p.patient_id_num)), 'w')
        f.write(p.document_summary())
        f.close()
        
