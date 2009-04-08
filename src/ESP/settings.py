'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                        Django settings for ESP project

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Do we really need both settings.py and localsettings.py?  Not sure what
# benefit we get from them.


import sys
import os
import datetime
import logging


DEBUG = True
TEMPLATE_DEBUG = DEBUG

TOPDIR='/srv/esp' # Top folder of ESP installation 

ADMINS = (
    ('Ross Lazarus', 'ross.lazarus@gmail.com'),
    ('Jason McVetta', 'jason.mcvetta@channing.harvard.edu'),
    ('Xuanlin Hou', 'rexua@channing.harvard.edu'),
)

DEVELOPER_EMAIL_LIST = [item[1] for item in ADMINS]


MANAGERS = ADMINS


SITEROOT='/ESP'

# This is used by incomingParser.py and a few other deprecated or nearly-
# deprecated tools.
LOCALSITE='MYSITE'



# FTP credentials for fetching data in espmanager.py
FTPUSER = ''
FTPPWD = ''
FTPSERVER = ''


EMAIL_SENDER='user@domain.com'


DATABASE_ENGINE = 'mysql' 
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

ROOT_URLCONF = 'ESP.urls'

CODEDIR = os.path.join(TOPDIR, 'src', 'ESP')

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(CODEDIR, 'static')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/ESP/media/' 

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''  #  MUST fill me in to run ESP web app!

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'ESP.esp.context_processors.path_definitions',
)

 
MIDDLEWARE_CLASSES = (
    #"django.middleware.cache.CacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "django.middleware.gzip.GZipMiddleware",
)


TEMPLATE_DIRS = (
    "%s/templates" % CODEDIR,
    "%s/templates/esp" % CODEDIR,
    "%s/templates" % TOPDIR,
    "%s/templates/esp" % TOPDIR,
)

INSTALLED_APPS = (
       'django.contrib.auth',
       'django.contrib.sites',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.admin',
       'ESP.esp',
       'ESP.conf',
)



# Display format for date objects in the web interface
DATE_FORMAT = '%d %b %Y'

# Default number of rows per page displayed in Flexigrids.  Should be in [10, 25, 50, 100]
ROWS_PER_PAGE = 10  


#===============================================================================
#
#--- ~~~ Case Generation ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
REPORT_RX_DAYS_BEFORE = 7
REPORT_RX_DAYS_AFTER = 14
REPORT_LX_DAYS_BEFORE = 30
REPORT_LX_DAYS_AFTER = 30
REPORT_ICD9_DAYS_BEFORE = 14
REPORT_ICD9_DAYS_AFTER = 14

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
#--- ~~~ Logging Configuration ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LOG_FORMAT_CONSOLE = '%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
LOG_FORMAT_FILE = '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
LOG_FILE = '/tmp/esp.log'
# NOTE WELL: If you set the log level to DEBUG, *copious* info will be logged!
LOG_LEVEL_CONSOLE = logging.ERROR
LOG_LEVEL_FILE = logging.INFO

