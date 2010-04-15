import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

# Insert ESP src folder at beginning of PYTHONPATH, in case an older version of
# Django is installed system-wide.
sys.path.insert(0, '/opt/esp/src')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

