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


from ESP.utils.utils import log
from ESP.emr.management.commands.download_ftp  import Command as FtpCommand
from ESP.emr.management.commands.load_epic     import Command as LoadEpicCommand
from ESP.emr.management.commands.load_hl7      import Command as LoadHl7Command
from ESP.emr.management.commands.concordance   import Command as ConcordanceCommand
from ESP.hef.management.commands.hef           import Command as HefCommand
from ESP.nodis.management.commands.nodis       import Command as NodisCommand
from ESP.nodis.management.commands.case_report import Command as CaseReportCommand
from ESP.ui.views import _populate_status_values

from ESP.settings import SITE_NAME
from ESP.settings import EMAIL_SUBJECT_PREFIX
from ESP.settings import SERVER_EMAIL
from ESP.settings import MANAGERS


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
                EMAIL_SUBJECT_PREFIX + 'Daily Status Report',
                report,
                SERVER_EMAIL, 
                [a[1] for a in MANAGERS],
                )
            html_content = '<pre>\n%s\n</pre>' % report
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            print report

        
