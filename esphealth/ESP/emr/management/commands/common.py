'''
                                  ESP Health
                            EMR ETL Infrastructure
                              HL7 Message Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import os
import shutil
from optparse import make_option
from optparse import Values

from django.core.management.base import BaseCommand

from ESP.utils.utils import log
from ESP.settings import DATA_DIR
from ESP.settings import ETL_SOURCE
from ESP.settings import ETL_ARCHIVE


class LoaderCommand(BaseCommand):
    '''
    Adds directory constands and file disposition method to BaseCommand.
    '''
    
    INCOMING_DIR = os.path.join(DATA_DIR, ETL_SOURCE, 'incoming')
    ARCHIVE_DIR = os.path.join(DATA_DIR, ETL_SOURCE, 'archive') # Successfully loaded files
    FAILURE_DIR = os.path.join(DATA_DIR, ETL_SOURCE, 'error') # Files that failed to load (w/ unhandled exception)
    
    option_list = BaseCommand.option_list + (
        make_option('--file', action='store', dest='single_file', metavar='FILEPATH', 
            help='Load an individual message file'),
        make_option('--input', action='store', dest='input_folder', default=INCOMING_DIR,
            metavar='FOLDER', help='Folder from which to read incoming HL7 messages'),
        make_option('--no-archive', action='store_false', dest='archive', default=ETL_ARCHIVE, 
            help='Do NOT archive files after they have been loaded'),
        make_option('--site', action='store', dest='site_name', 
            help='Provide site name for site-specific encounter type mapping'),
        make_option('--reload', action='store_true', dest='reload', default=False,
            help='Reload data even if same filename has already been loaded')
        )

    def archive(self, options, filepath, disposition):
        '''
        Dispose of a file after attempting to load it.
        @param filepath: Full path to file
        @type filepath:  String
        @param disposition: What to do with this file?
        @type disposition:  String - ('success', 'errors', 'failure')
        '''
        if type(options) == dict:
            options = Values(options)
        if not options.archive:
            return
        if disposition == 'failure':
            folder = self.FAILURE_DIR
        else: # 'success' and 'errors'
            folder = self.ARCHIVE_DIR
        log.info('Moving file "%s" to %s' % (filepath, folder))
        try:
            shutil.move(filepath, folder)
        except shutil.Error, e:
            msg = 'shutil Error:  %s' % e
            log.warning(msg)
            print msg
    
    def folder_check(self):
        '''
        Ensure all required folders exist
        '''
        for folder in [self.ARCHIVE_DIR, self.FAILURE_DIR]:
            if not os.path.exists(folder): 
                os.makedirs(folder)
                log.debug('Created new folder: %s' % folder)
