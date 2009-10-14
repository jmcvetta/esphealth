
import os

from couchdb import Server

import ESP.localsettings
import simplejson

# Get a connection to the server running on localhost, default port
server = Server()


# get the patients db. Create it if does not exist.
if not server.__contains__('patients'):
    server.create('patients')

patients = server['patients']


for f in os.listdir(ESP.localsettings.DOCUMENTS_DIR):
    try:
        pid = f.split('.')[2]
        patient_file = open(os.path.join(ESP.localsettings.DOCUMENTS_DIR, f), 'r')
        contents = simplejson.loads(patient_file.read())    
        patient_file.close()
        patients[pid] = contents
    except Exception, why:
        print 'failed to process file %s. Reason: %s ' % (f, why)









