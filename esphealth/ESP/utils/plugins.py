'''
                              ESP Health Project
Utilities
Plugin Infrastructure

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2012 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''
import os
import sys

from sprinkles import ISprinkle
from sprinkles import Attribute
from sprinkles import fromPath
from django_nose import NoseTestSuiteRunner

from ESP.settings import PACKAGE_ROOT
from ESP.settings import TOPDIR
from ESP.utils import log

PLUGIN_PATHS = []
for plugin_folder_path in [
    os.path.join(PACKAGE_ROOT, 'plugins'),
    #os.path.join(TOPDIR, 'standard_plugins'),
    ]:
    subdir_name_list = os.walk(plugin_folder_path).next()[1]
    for subdir_name in subdir_name_list:
        if subdir_name[0] == '.':
            continue
        plugin_path = os.path.join(plugin_folder_path, subdir_name)
        PLUGIN_PATHS.append(plugin_path)

class IPlugin(ISprinkle):
    event_heuristics = Attribute('List of EventHeuristic instances')
    timespan_heuristics = Attribute('List of TimespanHeuristic instances')
    disease_definitions = Attribute('List of DiseaseDefinition instances')
    reports = Attribute('List of Report instances')

def get_plugins():
    plugins = []
    for path in PLUGIN_PATHS:
        log.debug(path)
        plugins.extend(fromPath(path))
    return plugins

class PluginNoseTestSuiteRunner(NoseTestSuiteRunner):
    '''
    Automatigically include plugin tests when running Nose.
    '''
    
    def run_tests(self, test_labels, extra_tests=None):
        for path in PLUGIN_PATHS:
            where_arg = '--where=%s' % path
            sys.argv.append(where_arg)
        super(PluginNoseTestSuiteRunner, self).run_tests(test_labels, extra_tests)

