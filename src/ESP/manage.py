#!/usr/bin/env python

import os
import sys
import logging

if sys.version_info < (2, 6):
    print 'CRITICAL FAILURE: ESP requires Python 2.6 or greater.'
    sys.exit(1)


logging.log(logging.DEBUG, 'PYTHONPATH:')
if not os.environ.has_key('PYTHONPATH'):
    pypath = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )
    sys.path.append(pypath)
    logging.log(logging.DEBUG, '\t%s' % pypath)
else:
    logging.log(logging.DEBUG, '\t%s' % os.environ['PYTHONPATH'])

if not os.environ.has_key('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ESP.settings'
    logging.log(logging.DEBUG, 'DJANGO_SETTINGS_MODULE:')
    logging.log(logging.DEBUG, '\t%s' % os.environ['DJANGO_SETTINGS_MODULE'])


from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)

    
