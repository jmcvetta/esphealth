
import os
import sys

# Sample Django settings for esp project.
# change these for your site
# note the DEBUG setting is useful but very, very dangerous
DEBUG = True # DO NOT leave this set for production!!
# it exposes your entire site to anyone who can throw an error
TEMPLATE_DEBUG = DEBUG

try:
    import localsettings
except:
    msg = 'Unable to find localsettings.py -- cannot continue.\n'
    sys.stderr.write(msg)
    sys.exit(-255)



SITEROOT = localsettings.SITEROOT
CODEDIR = os.path.dirname(__file__)
TOPDIR= os.path.join(CODEDIR, '..')


ADMINS = localsettings.ADMINS

MANAGERS = ADMINS
#CACHE_BACKEND = "locmem:///"
#CACHE_MIDDLEWARE_SECONDS = 600
#CACHE_MIDDLEWARE_KEY_PREFIX = ''


LOCALSITE=localsettings.LOCALSITE
RUNFAKEDATA=localsettings.RUNFAKEDATA
FTPUSER = localsettings.FTPUSER
FTPPWD = localsettings.FTPPWD
FTPSERVER =localsettings.FTPSERVER
EMAILSENDER=localsettings.EMAILSENDER



USESQLITE=localsettings.USESQLITE
DATABASE_ENGINE = localsettings.DATABASE_ENGINE
DATABASE_HOST = localsettings.DATABASE_HOST
DATABASE_NAME = localsettings.DATABASE_NAME
DATABASE_USER = localsettings.DATABASE_USER
DATABASE_PASSWORD = localsettings.DATABASE_PASSWORD

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
MEDIA_ROOT = os.path.join(CODEDIR, 'templates')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/ESP/media/' 

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'make this very very long and do not change it'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
 
MIDDLEWARE_CLASSES = (
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
    import os
    import datetime,logging
    
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


                

