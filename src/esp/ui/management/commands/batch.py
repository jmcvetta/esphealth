'''
                                  ESP Health
                                User Interface
                                "batch" Command


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import datetime
import sys

from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from optparse import make_option
from optparse import Values

from esp.emr.management.commands.download_ftp  import Command as FtpCommand
from esp.emr.management.commands.load_epic     import Command as LoadEpicCommand
from esp.emr.management.commands.load_hl7      import Command as LoadHl7Command
from esp.hef.management.commands.hef           import Command as HefCommand
from esp.nodis.management.commands.nodis       import Command as NodisCommand
from esp.nodis.management.commands.case_report import Command as CaseReportCommand
from esp.emr.management.commands.concordance   import Command as ConcordanceCommand
from esp.ui.management.commands.status_report  import Command as StatusReportCommand

from esp.settings import ETL_SOURCE
from esp.settings import ETL_USE_FTP
from esp.settings import ETL_SOURCE
from esp.settings import CASE_REPORT_OUTPUT_FOLDER
from esp.settings import CASE_REPORT_MDPH
from esp.settings import CASE_REPORT_FILENAME_FORMAT
from esp.settings import CASE_REPORT_TEMPLATE
from esp.settings import SITE_NAME
from esp.settings import BATCH_ETL
from esp.settings import BATCH_MAIL_STATUS_REPORT
from esp.settings import BATCH_GENERATE_CASE_REPORT
from esp.settings import BATCH_TRANSMIT_CASE_REPORT


class Command(BaseCommand):
#    option_list = BaseCommand.option_list + (
#        make_option('--file', action='store', dest='single_file', metavar='FILEPATH', 
#            help='Load an individual message file'),
#        make_option('--input', action='store', dest='input_folder', default=INCOMING_DIR,
#            metavar='FOLDER', help='Folder from which to read incoming HL7 messages'),
#        make_option('--no-archive', action='store_false', dest='archive', default=True, 
#            help='Do NOT archive files after they have been loaded'),
#        )

    help = 'Run ESP daily batch'
    
    def handle(self, *fixture_labels, **options):
        options = Values(options)
        # Convenience method for printing progress messages when verbose output is set
        def progress(msg):
            if options.verbosity:
                datestamp = datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')
                print '%s: %s' % (datestamp, msg)
        #
        # NOTE: To run a command with default options, as though run from
        # command line w/ no arguments, use run_from_argv([None, None]).  Use
        # handle() if it is necessary to specify options.
        #
        try:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #--- ETL
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if BATCH_ETL:
                if ETL_USE_FTP:
                    progress('Fetching new ETL files from FTP')
                    cmnd = FtpCommand()
                    cmnd.run_from_argv([None, None])
                    progress('Successfully fetched new ETL files from FTP')
                    del cmnd
                if ETL_SOURCE == 'epic':
                    progress('Loading Epic ETL files')
                    cmnd = LoadEpicCommand()
                    cmnd.run_from_argv([None, None])
                    del cmnd
                    progress('Succesffully loaded Epic ETL files')
                elif ETL_SOURCE == 'hl7':
                    pass
                    cmnd = LoadHl7Command()
                    cmnd.run_from_argv([None, None])
                    del cmnd
                else:
                    print >> sys.stderr, 'Unrecognized ETL_SOURCE: "%s"' % ETL_SOURCE
                    print >> sys.stderr, ''
                    print >> sys.stderr, 'Valid case-sensitive ETL_SOURCE values are:'
                    print >> sys.stderr, '    epic'
                    print >> sys.stderr, '    hl7'
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #--- HEF
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            progress('Generating heuristic events')
            cmnd = HefCommand()
            cmnd.run_from_argv([None, None])
            del cmnd
            progress('Successfully generated heuristic events')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #--- Nodis
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            progress('Generating Nodis cases')
            cmnd = NodisCommand()
            cmnd.run_from_argv([None, None])
            del cmnd
            progress('Successfully generated Nodis cases')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #--- Case reports
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if BATCH_GENERATE_CASE_REPORT:
                progress('Generating Nodis case reports')
                cmnd = CaseReportCommand()
                cmnd.handle(
                    case_id=None,
                    status='Q',
                    batch_size=None,
                    mdph=CASE_REPORT_MDPH,
                    transmit=BATCH_TRANSMIT_CASE_REPORT,
                    mark_sent=True,
                    output_folder=CASE_REPORT_OUTPUT_FOLDER,
                    template=CASE_REPORT_TEMPLATE,
                    format=CASE_REPORT_FILENAME_FORMAT,
                    stdout=False,
                    individual=False,
                    one_file=False,
                    sample=None,
                    )
                del cmnd
                progress('Successfully generated Nodis case reports')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #--- Concordance
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            progress('Rebuilding lab tests condordance')
            cmnd = ConcordanceCommand()
            cmnd.run_from_argv([None, None])
            del cmnd
            progress('Successfully rebuilt lab tests condordance')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #--- Status Report
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if BATCH_MAIL_STATUS_REPORT:
                progress('Sending status report')
                cmnd = StatusReportCommand()
                cmnd.handle(send_mail=True)
                del cmnd
                progress('Successfully emailed status report.')
            progress('Batch run complete')
        except [KeyboardInterrupt, "-255"]:
            sys.stderr.write('Keyboard interrupt - exiting now.')
            sys.exit(-255)
        except BaseException, e:
            sub = 'WARNING! An error occurred in the ESP batch job at %s' % SITE_NAME
            msg = 'Caught the following exception: \n%s' % e
            mail_admins(sub, msg, fail_silently=False)
            print >> sys.stderr, msg
