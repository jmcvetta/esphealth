import os, sys
import datetime

from optparse import OptionParser
from ftplib import FTP

from ESP.settings import DATA_DIR, FTP_USER, FTP_PASSWORD, FTP_SERVER
from ESP.utils.utils import log, days_in_interval, str_from_date, date_from_str

usage_msg = """espmanager.py
Usage: python utils/espmanager.py --begin=[date as 20090101] --end_date=[date] 
"""

def doFTP(days):
    try:
    	ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USER, FTP_PASSWORD)
    except Exception, why:
        log.error(why)
        return
        
    #local site directory
    todir = os.path.join(DATA_DIR, 'epic', 'incoming')
    os.chdir(todir)    
    #remote site directory
    ftp.cwd('ESPFiles')
    filenames = ftp.nlst()
           
    datestamps = [day.strftime('%m%d%Y') for day in days]

    for eachfile in filenames:
        if eachfile.split('.')[-1] in datestamps:
            log.info('Retrieving file ' + eachfile)
            ftp.retrbinary('RETR ' + eachfile, open(eachfile, 'wb').write)
            
    ftp.quit()
    return


if __name__ == "__main__":
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)

    parser = OptionParser(usage=usage_msg)
    parser.add_option('-b', '--begin', dest='begin_date', default=yesterday.strftime('%Y%m%d'))
    parser.add_option('-e', '--end', dest='end_date', default=today.strftime('%Y%m%d'))

    options, args = parser.parse_args()

    try:
        begin_date = date_from_str(options.begin_date)
        end_date = date_from_str(options.end_date)
    except:
        log.error('Invalid dates')
        sys.exit(-2)

    days = days_in_interval(begin_date, end_date)

    try:
        doFTP(days)
    except Exception, why:
        log.error(why)
                                             
