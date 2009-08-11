from ESP.emr.models import Patient


if __name__ == '__main__':
    p = Patient.objects.order_by('?')[0]
    print p.document_summary()
