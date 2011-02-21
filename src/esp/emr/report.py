import os


from esp.emr.models import Patient


DOC_FOLDER = os.path.join(os.path.dirname(__file__), 'assets', 'documents')

if __name__ == '__main__':

    date_processed = Patient.objects.get(pk=575467).updated_timestamp
    patients_to_process = Patient.objects.exclude(updated_timestamp__lt=date_processed)

    patient_count = patients_to_process.count()
    # print 'Creating folders'

    # for i in xrange(patient_count/1000):
    #     folder_name = '%06d' % (i*1000)
    #     full_path = os.path.abspath(os.path.join(DOC_FOLDER, folder_name))
    #     if not os.path.exists(full_path):
    #         os.mkdir(full_path)
                                  
    

    print 'Creating summary documents for %d patients' % patient_count
    patients = patients_to_process.order_by('updated_timestamp').iterator()

    try:
        patient = patients.next()
        total_processed = 0
    except StopIteration: patient = None
    

    while patient:
        try:
            PATIENT_FOLDER = os.path.join(DOC_FOLDER, '%06d' % int((patient.pk/1000)*1000) )
            f = open(os.path.join(PATIENT_FOLDER, 'patient.%06d.%s.json' % (patient.pk, patient.patient_id_num)), 'w')
            f.write(patient.document_summary())
            f.close()
            total_processed += 1
            if (total_processed % 1000) == 0: print 'Total processed:', total_processed
            patient = patients.next()
        except StopIteration:
            break
        except Exception, why:
            print 'Could not process information for patient %d. Reason: %s' % (patient.pk, why)
            patient = patients.next()
        
