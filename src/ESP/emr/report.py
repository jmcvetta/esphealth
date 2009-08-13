import os

from ESP.emr.models import Patient


DOC_FOLDER = os.path.join(os.path.abspath('.'), 'assets', 'documents')

if __name__ == '__main__':


    patient_count = Patient.objects.count()
    print 'Creating folders'

    for i in xrange(patient_count/1000):
        folder_name = '%06d' % (i*1000)
        full_path = os.path.abspath(os.path.join(DOC_FOLDER, folder_name))
        if not os.path.exists(full_path):
            os.mkdir(full_path)
                                  
    

    print 'Creating summary documents for %d patients' % patient_count
    for patient in Patient.objects.order_by('id'):
        try:
            PATIENT_FOLDER = os.path.join(DOC_FOLDER, '%06d' % int((patient.pk/1000)*1000) )
            f = open(os.path.join(PATIENT_FOLDER, 'patient.%06d.%s.json' % (patient.pk, patient.patient_id_num)), 'w')
            f.write(patient.document_summary())
            f.close()
        except Exception, why:
            print 'Could not process information for patient %d. Reason: %s' % (patient.pk, why)
        
