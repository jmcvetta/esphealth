'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                                  ESP Health
                                Django settings


Most deployments should not require any changes to this file.  All passwords &
other site-specific configuration are stored in localsettings.py.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import os
import logging

from ESP import localsettings


TOPDIR = os.path.dirname(__file__)
CODEDIR = TOPDIR

DEBUG = localsettings.DEBUG
TEMPLATE_DEBUG = DEBUG

ADMINS = localsettings.ADMINS
MANAGERS = ADMINS
DEVELOPER_EMAIL_LIST = [item[1] for item in ADMINS]

DATABASE_ENGINE = localsettings.DATABASE_ENGINE
DATABASE_NAME = localsettings.DATABASE_NAME
DATABASE_USER = localsettings.DATABASE_USER
DATABASE_PASSWORD = localsettings.DATABASE_PASSWORD
DATABASE_HOST = localsettings.DATABASE_HOST
DATABASE_PORT = localsettings.DATABASE_PORT


EMAIL_SENDER = localsettings.EMAIL_SENDER
EMAIL_HOST = localsettings.EMAIL_HOST
EMAIL_HOST_USER = localsettings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = localsettings.EMAIL_HOST_PASSWORD
EMAIL_PORT = localsettings.EMAIL_PORT
EMAIL_USE_TLS = localsettings.EMAIL_USE_TLS

SECRET_KEY = localsettings.SECRET_KEY

SITE_ID = 2
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

DATE_FORMAT = '%d %b %Y'
ROWS_PER_PAGE = 50

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(TOPDIR, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


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
    'esp.context_processors.path_definitions' 
    )


TEMPLATE_DIRS = (
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(TOPDIR, 'templates'),
    os.path.join(TOPDIR, 'templates/esp')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'conf', 
    'esp',
    'vaers'
)




#===============================================================================
#
#--- ~~~ Case Generation ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
REPORT_RX_DAYS_BEFORE = localsettings.REPORT_RX_DAYS_BEFORE
REPORT_RX_DAYS_AFTER = localsettings.REPORT_RX_DAYS_AFTER
REPORT_LX_DAYS_BEFORE = localsettings.REPORT_LX_DAYS_BEFORE
REPORT_LX_DAYS_AFTER = localsettings.REPORT_LX_DAYS_AFTER
REPORT_ICD9_DAYS_BEFORE = localsettings.REPORT_ICD9_DAYS_BEFORE
REPORT_ICD9_DAYS_AFTER = localsettings.REPORT_ICD9_DAYS_AFTER

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
LOG_FILE = localsettings.LOG_FILE
# BEWARE: If you set the log level to DEBUG, *copious* info will be logged!
LOG_LEVEL_CONSOLE = localsettings.LOG_LEVEL_CONSOLE
LOG_LEVEL_FILE = localsettings.LOG_LEVEL_FILE



