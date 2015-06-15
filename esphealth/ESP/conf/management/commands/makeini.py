'''
                              ESP Health Project
                            Quality Metrics module
                             make ini files

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import os
import sys
from configobj import ConfigObj
from configobj import flatten_errors
from validate import Validator
from django.core.management.base import BaseCommand

PACKAGE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../..'))
CONFIG_FOLDER = os.path.join(PACKAGE_ROOT, 'etc')

class Command(BaseCommand):
     
    help = 'generate ini files after ESP install'

    
    def handle(self, *fixture_labels, **options):
        validator = Validator()
        application_ini = os.path.join(CONFIG_FOLDER, 'application.ini')
        application_spec = ConfigObj(os.path.join(PACKAGE_ROOT, 'ESP/application.spec.ini'), interpolation=False, list_values=False)
        secrets_ini = os.path.join(CONFIG_FOLDER, 'secrets.ini')
        secrets_spec = os.path.join(PACKAGE_ROOT, 'ESP/secrets.spec.ini')
        secrets = ConfigObj(secrets_ini, configspec=secrets_spec)
        config = ConfigObj(application_ini, configspec=application_spec, interpolation=False)
        
        bad_config = False
        for ini_file, conf_obj in [(secrets_ini, secrets), (application_ini, config)]:
            if not os.path.exists(ini_file):
                print 'Could not find configuration file %s' % ini_file
                if os.access(CONFIG_FOLDER, os.W_OK):
                    print 'Creating new configuration file.  You will need to edit the default values.'
                else:
                    print 'Cannot create new configuration file -- do not have write access to %s' % CONFIG_FOLDER
                    sys.exit(-1)
                print
                bad_config = True
            results = conf_obj.validate(validator, copy=True)
            try:
                conf_obj.write()
            except IOError:
                print 'You do not have write permission on %s' % ini_file
            if results != True:
                for (section_list, key, _) in flatten_errors(config, results):
                    print '%s:' % ini_file
                    if key is not None:
                        print '    The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list))
                    else:
                        print '    The following section was missing:%s ' % ', '.join(section_list)
                bad_config = True
        if bad_config:
            print
            print 'Review messages above and modify configuration file as needed.'
            print
            sys.exit(-1)
        else:
            print 'Configuration file update complete'