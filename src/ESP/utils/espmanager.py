import os
import datetime

from optparse import OptionParser
from ftplib import FTP

from ESP.settings import DATA_DIR, FTP_USER, FTP_PASSWORD, FTP_SERVER
from ESP.utils.utils import log, days_in_interval, str_from_date

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
    todir = os.path.join(DATA_DIR, 'incoming/')
    os.chdir(todir)    
    #remote site directory
    ftp.cwd('ESPFiles')
    filenames = ftp.nlst()
           
    
    datestamps = [str_from_date(day) for day in days]

    for eachfile in filenames:
        if eachfile.split('.')[-1] in datestamps:
            ftp.retrbinary('RETR ' + eachfile, open(eachfile, 'wb').write)
            
    ftp.quit()
    return newfiles


if __name__ == "__main__":
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)

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
                                             
