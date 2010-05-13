#!/usr/bin/env python

import os
import sys
import logging

if sys.version_info < (2, 5):
    print 'CRITICAL FAILURE: ESP requires Python 2.5 or greater.'
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

#
# Intercept the special argument 'setup_environment' -- if someone is running this
# command, presumably 'import settings' will fail, because settings files do
# not yet exists.
#
if sys.argv[1] == 'setup_environment':
    _folders = [
        os.path.join('/', 'srv', 'esp-data'),
        os.path.join('/', 'srv', 'esp-data', 'case_reports'),
        os.path.join('/', 'srv', 'esp-data', 'epic'),
        os.path.join('/', 'srv', 'esp-data', 'epic', 'incoming'),
        os.path.join('/', 'srv', 'esp-data', 'epic', 'archive'),
        os.path.join('/', 'srv', 'esp-data', 'epic', 'error'),
        os.path.join('/', 'srv', 'esp-data', 'hl7'),
        os.path.join('/', 'srv', 'esp-data', 'hl7', 'incoming'),
        os.path.join('/', 'srv', 'esp-data', 'hl7', 'archive'),
        os.path.join('/', 'srv', 'esp-data', 'hl7', 'error'),
        ]
    print 'Checking .ini files...'
    #
    # The following code is copied verbatim from settings.py -- cannot just
    # import settings, because exit with errors when no .ini files exist.
    #
    from configobj import ConfigObj
    from validate import Validator
    TOPDIR = os.path.dirname(__file__)
    PACKAGE_ROOT = os.path.normpath(os.path.join(TOPDIR, '..', '..'))
    CONFIG_FOLDER = os.path.join(PACKAGE_ROOT, 'etc')
    validator = Validator()
    esp_ini = os.path.join(CONFIG_FOLDER, 'esp.ini')
    esp_spec = ConfigObj(os.path.join(TOPDIR, 'esp.spec.ini'), interpolation=False, list_values=False)
    secrets_ini = os.path.join(CONFIG_FOLDER, 'secrets.ini')
    secrets_spec = os.path.join(TOPDIR, 'secrets.spec.ini')
    ConfigObj(esp_ini, configspec=esp_spec, interpolation=False).validate(validator, copy=True)
    print '    esp.ini'
    ConfigObj(secrets_ini, configspec=secrets_spec).validate(validator, copy=True)
    print '    secrets.ini'
    #
    #
    print 'Checking data folders...'
    for folder in _folders:
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except OSError:
                print
                print 'You do not have permission to create folder: %s' % folder
                print
                print 'Please fix this, and try running install command again.'
                print
                sys.exit()
            print 'Added new folder:  %s' % folder
    sys.exit()

from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)

    
