#!/usr/bin/env python

import os
import sys
from ESP.utils.utils import log

if not os.environ.has_key('PYTHONPATH'):
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

if not os.environ.has_key('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'
log.debug('PYTHONPATH:')
log.debug('\t%s' % os.environ['PYTHONPATH'])
log.debug('DJANGO_SETTINGS_MODULE:')
log.debug('\t%s' % os.environ['DJANGO_SETTINGS_MODULE'])


from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)

    
