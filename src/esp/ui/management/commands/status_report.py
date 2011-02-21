'''
                                  ESP Health
                             User Interface Module
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
from django.core.mail import mail_managers
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


from esp.utils.utils import log
from esp.emr.management.commands.download_ftp  import Command as FtpCommand
from esp.emr.management.commands.load_epic     import Command as LoadEpicCommand
from esp.emr.management.commands.load_hl7      import Command as LoadHl7Command
from esp.emr.management.commands.concordance   import Command as ConcordanceCommand
from esp.hef.management.commands.hef           import Command as HefCommand
from esp.nodis.management.commands.nodis       import Command as NodisCommand
from esp.nodis.management.commands.case_report import Command as CaseReportCommand
from esp.ui.views import _populate_status_values

from esp.settings import SITE_NAME
from esp.settings import EMAIL_SUBJECT_PREFIX
from esp.settings import SERVER_EMAIL
from esp.settings import MANAGERS


class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--send-mail', action='store_true', dest='send_mail', default=False,
            help='Email report to admins'),
        )

    help = 'Generate a status report'
    
    def handle(self, *fixture_labels, **options):
        options = Values(options)
        log.debug('Generating status report')
        values = _populate_status_values()
        report = render_to_string('ui/status.txt', values)
        if options.send_mail:
            log.debug('Emailing status report to site managers')
            #mail_managers(
                #'ESP Status Report (%s)' % SITE_NAME,
                #report,
                #)
            msg = EmailMultiAlternatives(
                EMAIL_SUBJECT_PREFIX + ' Status Report -- ' + SITE_NAME,
                report,
                SERVER_EMAIL, 
                [a[1] for a in MANAGERS],
                )
            html_content = '<pre>\n%s\n</pre>' % report
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            print report

        
