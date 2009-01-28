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
import localsettings


DEBUG = True
TEMPLATE_DEBUG = DEBUG



TOPDIR='/home/ESP'
CODEDIR = os.path.join(TOPDIR, 'src', 'ESP')

ADMINS = (
    ('Ross Lazarus', 'ross.lazarus@gmail.com'),
)

MANAGERS = ADMINS
#CACHE_BACKEND = "locmem:///"
#CACHE_MIDDLEWARE_SECONDS = 600
#CACHE_MIDDLEWARE_KEY_PREFIX = ''


SITEROOT = localsettings.SITEROOT
LOCALSITE=localsettings.LOCALSITE
RUNFAKEDATA=localsettings.RUNFAKEDATA
FTPUSER = localsettings.FTPUSER
FTPPWD = localsettings.FTPPWD
FTPSERVER =localsettings.FTPSERVER
EMAIL_SENDER=localsettings.EMAIL_SENDER
USESQLITE=localsettings.USESQLITE


if localsettings.USESQLITE:
    DATABASE_ENGINE = 'sqlite3' # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = CODEDIR + '/ESPsqlite'             # Or path to database file if using sqlite3.
    DATABASE_USER = localsettings.SQLITE_DB_USER             # Not used with sqlite3.
    DATABASE_PASSWORD = localsettings.SQLITE_DB_PASSWORD         # Not used with sqlite3.
    DATABASE_HOST = '127.0.0.1'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = 3306             # Set to empty string for default. Not used with sqlite3.
    SITEROOT = ''
else:
    DATABASE_ENGINE = 'mysql' # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'esp'             # Or path to database file if using sqlite3.
    DATABASE_USER = localsettings.MYSQL_DB_USER             # Not used with sqlite3.
    DATABASE_PASSWORD = localsettings.MYSQL_DB_PASSWORD        # Not used with sqlite3.
    DATABASE_HOST = '127.0.0.1'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = 3306             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/NewYork'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%s/templates/' % CODEDIR

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/ESP/media/' 

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lo(g8i)a(g%&(4-*9@w#w2u#wfq(tjf5o+f4#6q7mg(k%9h%j5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
#     'django.template.loaders.eggs.load_template_source',
 
MIDDLEWARE_CLASSES = (
    #"django.middleware.cache.CacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "django.middleware.gzip.GZipMiddleware",
)

ROOT_URLCONF = 'ESP.utils.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
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
)



###################################
def getJavaInfo():
    javadir="/usr/java/jdk1.5.0_09/bin/"
    #    javadir="/usr/bin/"
    javaclass=" /home/ESP/ESP/sendMsgs:/home/ESP/axis-1_4/activation.jar:/usr/local/axis-1_4/lib/axis.jar:/usr/local/axis-1_4/lib/commons-logging-1.0.4.jar:/usr/local/axis-1_4/lib/commons-discovery-0.2.jar:/usr/local/axis-1_4/lib/jaxrpc.jar:/usr/local/axis-1_4/lib/wsdl4j-1.5.1.jar:/usr/local/axis-1_4/lib/saaj.jar:/usr/local/axis-1_4/lib/axis-ant.jar:/usr/local/axis-1_4/lib/log4j-1.2.8.jar:/home/ESP/axis-1_4/mail.jar:/home/ESP/ESP/sendMsgs/bcdc.jar  "
    sendMsgcls = 'sendMsg'
    return (javadir, javaclass,sendMsgcls)

###############################
def getLogging(appname,debug=0):
    
    logdir = os.path.join(TOPDIR,LOCALSITE, 'logs/')
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
        
    appname = logdir+appname
    debug=debug
    today=datetime.datetime.now().strftime('%Y%m%d')
    if debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='%s.%s.log' % (appname,today),
                            filemode='a')
        
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='%s.%s.log' % (appname,today),
                            filemode='a')
        
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-4s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    return logging


                


#===============================================================================
#
#--- ~~~ Logging Configuration ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LOG_FORMAT = '%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_STREAM = open('/tmp/esp.log', 'w')
#LOG_STREAM = sys.stdout