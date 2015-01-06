import os, sys
import datetime
import paramiko
from optparse import OptionParser, make_option

from django.core.management.base import BaseCommand

from ESP.emr.models import Provenance
from ESP.settings import DATA_DIR, SFTP_PORT, SFTP_USER, SFTP_PASSWORD, SFTP_SERVER, SFTP_PATH
from ESP.utils.utils import log, days_in_interval, str_from_date, date_from_str


class Command(BaseCommand):
    #
    # Parse command line options
    #
    option_list = BaseCommand.option_list + (
        make_option('-b', '--begin', dest='begin_date', help='Begin date',
                    default=(datetime.date.today() - datetime.timedelta(30)).strftime('%Y%m%d')),
        make_option('-e', '--end', dest='end_date', help='End date',
                    default=datetime.date.today().strftime('%Y%m%d'))
        )
    
    help = 'Fetch ETL files via SFTP'
    
    def handle(self, *fixture_labels, **options):
        try:
            begin_date = date_from_str(options['begin_date'])
            end_date = date_from_str(options['end_date'])
        except:
            log.error('Invalid dates')
            sys.exit(-2)

        try:
            ssh = paramiko.SSHClient
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            ssh.connect(SFTP_SERVER, SFTP_PORT, SFTP_USER, SFTP_PASSWORD)
            sftp=ssh.open_sftp()

        except Exception, why:
            log.error(why)
            return
        
        #local site directory
        todir = os.path.join(DATA_DIR, 'epic', 'incoming')
        os.chdir(todir)    

        #remote site directory
        sftp.chdir(SFTP_PATH)
        filenames = sftp.listdir()
           
        # Find files that need to be downloaded
        days = days_in_interval(begin_date, end_date)
        datestamps = [day.strftime('%m%d%Y') for day in days]

        for eachfile in filenames:
            processed = Provenance.objects.filter(source=eachfile) # Not evaluated until second half of 'and not' clause below
            if eachfile.split('.')[-1] in datestamps and not processed:
                try:
                    log.info('Retrieving file ' + eachfile)
                    sftp.get(eachfile)
                except:
                    log.warn('Could not write file: ' + eachfile)
                
        sftp.close()
        return        
