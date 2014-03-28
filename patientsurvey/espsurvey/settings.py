
# Django settings for survey project.

import os

#TODO turn this off when live
DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'espsurvey'             # Or path to database file if using sqlite3.
DATABASE_USER = 'espsurvey'           # Not used with sqlite3.
DATABASE_PASSWORD = 'espsurvey'         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'            # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

PY_DATE_FORMAT ='%d %b %Y'
ROWS_PER_PAGE ='25'
SITE_NAME = 'Boston'
STATUS_REPORT_TYPE = 'NODIS'
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

TOPDIR = '/srv/esp/espsurvey'
PACKAGE_ROOT = os.path.normpath(os.path.join(TOPDIR, '..'))
# One could also set CONFIG_FOLDER manually, to something like '/etc/esp', if 
# so desired.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'espsurvey.survey.context_processors.path_definitions' 
    )

#CONFIG_FOLDER = os.path.join(PACKAGE_ROOT, 'etc')
CONFIG_FOLDER = TOPDIR
version_path =  os.path.join(TOPDIR, 'version.txt')
VERSION = open(version_path).readline().strip()


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
ADMIN_MEDIA_PREFIX = 'http:/localhost:8000/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xbn6p9q9xif(fpt#-z8#=k-@#v4d=a(ty$9c+ipegdi5t@yj*_'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'survey.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(CONFIG_FOLDER, 'templates'),
    os.path.join(TOPDIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'survey',
)
