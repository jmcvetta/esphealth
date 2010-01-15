'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                                  ESP Health
                                Django Settings


Configuration settings for the ESP application.  Passwords and other private 
information are stored in external plain text files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import os
import sys
import logging


#===============================================================================
#
#                                 Credentials
#
#===============================================================================
try:
    SECRET_KEY = open('secret_key.txt').readline().strip()
except IOError:
    print >> sys.stderr, \
'''
You must create a $ESP_HOME/secret_key.txt file, and populate it with a unique 
string, which should not be shared.  The unix utility 'pwgen' is useful  for 
generating long random password strings.
'''
    sys.exit(1001)
try:
    DATABASE_PASSWORD = open('database_password.txt').readline().strip()
except IOError:
    print >> sys.stderr, \
'''
You must create a $ESP_HOME/database_password.txt file, and populate it with 
your database  password. The unix utility 'pwgen' is useful for generating long 
random password strings.
'''
    sys.exit(1002)



#===============================================================================
#
#                                   General
#
#===============================================================================
# Set DEBUG to False before running in production!
DEBUG = True 
# No error control, because version.txt is included with source.
VERSION = open('version.txt').readline().strip()
TOPDIR = os.path.dirname(__file__)
CODEDIR = TOPDIR
TEMPLATE_DEBUG = DEBUG
ADMINS = (
    ('Jason McVetta', 'jason.mcvetta@channing.harvard.edu'),
)
MANAGERS = ADMINS
DEVELOPER_EMAIL_LIST = [item[1] for item in ADMINS]
SITE_NAME = 'Development (localhost)' # Name of your local site
DATA_DIR = '/srv/esp'


#===============================================================================
#
#                                   Database
#
#===============================================================================
DATABASE_ENGINE = 'postgresql_psycopg2' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'esp'
#DATABASE_NAME = 'dev_esp_jm'
DATABASE_USER = 'esp'
DATABASE_HOST = 'localhost'
DATABASE_PORT = ''
DATABASE_OPTIONS = {
    # Make PostgreSQL recover gracefully from caught exceptions
    #"autocommit": True,
}






#===============================================================================
#
#                                Miscellaneous
#
#===============================================================================
HL7_DIR = os.path.join(DATA_DIR, 'hl7')
SITE_ID = 1
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
DATE_FORMAT = '%d %b %Y'
ROWS_PER_PAGE = 25
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(TOPDIR, 'media')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source'
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'ESP.urls'
LOGIN_URL = '/login'
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'ESP.conf.context_processors.path_definitions' 
    )
TEMPLATE_DIRS = (
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(TOPDIR, 'templates'),
    os.path.join(TOPDIR, 'templates/esp'),
    os.path.join(TOPDIR, 'templates/pages/vaers'),
    os.path.join(TOPDIR, 'templates/pages/ss')
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'ESP.static', 
    'ESP.conf', 
    'ESP.emr',
    'ESP.hef',
    'ESP.nodis',
    'ESP.vaers',
    'ESP.ss'
)

#===============================================================================
#
#                               Case Generation
#
#===============================================================================
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
#                                    Email
#
#===============================================================================
EMAIL_SENDER = 'esp-noreply@your_domain.com'
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = ''
EMAIL_USE_TLS = True


#===============================================================================
#
#                                 VAERS
#
#===============================================================================
VAERS_NOTIFICATION_RECIPIENT = 'someone@example.com'





#===============================================================================
#
#--- ~~~ Logging Configuration ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LOG_FORMAT_CONSOLE = '%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
LOG_FORMAT_FILE = '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
# BEWARE: If you set the log level to DEBUG, *copious* info will be logged!
LOG_FILE = '/var/log/esp'
LOG_LEVEL_CONSOLE = logging.DEBUG
LOG_LEVEL_FILE = logging.DEBUG 


