import os, logging

# These variables are needed for Django settings, but are site-specific. settings module read the values here for application setup and initialization.

PWD = os.path.dirname(__file__)


DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(PWD, 'esp.db')          # Or path to database file if using sqlite3.
DATABASE_USER = ''    # Not used with sqlite3.
DATABASE_PASSWORD = '' # Not used with sqlite3.
DATABASE_HOST = ''    # Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default.


EMAIL_SENDER = 'espuser@lkenpesp.healthone.org'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'raphael@lullis.net'
EMAIL_HOST_PASSWORD = '.K1d+kom'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# These variables are site-specific, but the settings module does not
# need it. Other modules should import from here directly.
DEBUG = True
LOCALSITE='NORTH_ADAMS'

ADMINS = (
    ('Raphael Lullis', 'raphael.lullis@channing.harvard.edu'),
)

SECRET_KEY = 'em%two7cgv*ro6r@b+d(m@)jyfa!y9w$&9wy_=fqwek@3-9m47'

VAERS_EMAIL_RECIPIENT = 'lullis@gmail.com'
VAERS_EMAIL_SUBJECT = 'Testing VAERS NOTIFICATION'
VAERS_EMAIL_SENDER = 'raphael.lullis@harvard.channing.edu'


FTP_SERVER = 'n2ftp001.hvma.org'
FTP_USER = 'HEALTHONE\\rlazarus'
FTP_PASSWORD = 'Welcome00'

REPORT_RX_DAYS_BEFORE = 7
REPORT_RX_DAYS_AFTER = 14
REPORT_LX_DAYS_BEFORE = 30
REPORT_LX_DAYS_AFTER = 30
REPORT_ICD9_DAYS_BEFORE = 14
REPORT_ICD9_DAYS_AFTER = 14


#===============================================================================
#
#--- ~~~ Case Generation ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Default set of ICD9 codes to report
DEFAULT_REPORTABLE_ICD9S = [
    '780.6A',
    '782.4',
    '783.0',
    '780.79B',
    '789.00',
    '789.01',
    '789.02',
    '789.03',
    '789.04',
    '789.05',
    '789.06',
    '789.07',
    '789.08',
    '789.09',
    '787.01',
    '787.02',
    '787.03',
    '787.91',
    ]


#===============================================================================
#
#                                   Logging
#
#===============================================================================
LOG_FILE = '/tmp/esp.log'
# WARNING: If you set the log level to DEBUG, *copious* info will be logged!
LOG_LEVEL_CONSOLE = logging.INFO
LOG_LEVEL_FILE = logging.INFO 
