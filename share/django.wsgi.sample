import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'

# Enable this to prepend your ESP src folder to the beginning of PYTHONPATH, in
# case an older version of Django is installed system-wide.
#
#sys.path.insert(0, '/opt/esp/src')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

