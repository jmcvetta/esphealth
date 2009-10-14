import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'
sys.path.append('/opt/esp/src')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

