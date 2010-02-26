'''
                                  ESP Health
                                User Interface
                                "status_report" Command


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import datetime
import sys

from optparse import make_option
from optparse import Values

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from ESP.emr.management.commands.download_ftp  import Command as FtpCommand
from ESP.emr.management.commands.load_epic     import Command as LoadEpicCommand
from ESP.emr.management.commands.load_hl7      import Command as LoadHl7Command
from ESP.emr.management.commands.concordance   import Command as ConcordanceCommand
from ESP.hef.management.commands.hef           import Command as HefCommand
from ESP.nodis.management.commands.nodis       import Command as NodisCommand
from ESP.nodis.management.commands.case_report import Command as CaseReportCommand
from ESP.ui.views import _populate_status_values

from ESP.settings import ETL_SOURCE
from ESP.settings import ETL_USE_FTP
from ESP.settings import ETL_SOURCE
from ESP.settings import CASE_REPORT_OUTPUT_FOLDER
from ESP.settings import CASE_REPORT_MDPH
from ESP.settings import CASE_REPORT_FILENAME_FORMAT
from ESP.settings import CASE_REPORT_TEMPLATE


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--send-mail', action='store_true', dest='send_mail', default=False,
            help='Email report to admins'),
        )

    help = 'Generate a status report'
    
    def handle(self, *fixture_labels, **options):
        options = Values(options)
        values = _populate_status_values()
        return render_to_string('ui/status.txt', values)

        