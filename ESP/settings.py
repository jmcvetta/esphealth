# Django settings for esp project.
 
DEBUG = False
TEMPLATE_DEBUG = DEBUG
#ENABLE_PSYCO = True

SITEROOT = '/ESP'
TOPDIR='/home/ESP'
CODEDIR = '%s/ESP' % TOPDIR

ADMINS = (
    ('Ross Lazarus', 'ross.lazarus@gmail.com'),
)

MANAGERS = ADMINS
#CACHE_BACKEND = "locmem:///"
#CACHE_MIDDLEWARE_SECONDS = 600
#CACHE_MIDDLEWARE_KEY_PREFIX = ''
usesqlite=0

if usesqlite:
    DATABASE_ENGINE = 'sqlite3' # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'ESPsqlite'             # Or path to database file if using sqlite3.
    DATABASE_USER = 'rossSQL'             # Not used with sqlite3.
    DATABASE_PASSWORD = 'SQLross'         # Not used with sqlite3.
    DATABASE_HOST = '127.0.0.1'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = 3306             # Set to empty string for default. Not used with sqlite3.
else:
    DATABASE_ENGINE = 'mysql' # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'esp'             # Or path to database file if using sqlite3.
    DATABASE_USER = 'ESP'             # Not used with sqlite3.
    DATABASE_PASSWORD = '3spuser2006'         # Not used with sqlite3.
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
     'django.template.loaders.eggs.load_template_source',
)

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

