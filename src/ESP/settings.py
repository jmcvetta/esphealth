'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                                  ESP Health
                                Django Settings


Configuration settings for the ESP application.  Passwords and and site-dependent
 information are stored in files in the conf folder.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import os
import sys
import logging
from ConfigParser import ConfigParser

def missing_config(message):
    print message
    print 'Please check your configuration files'
    sys.exit(-1)


TOPDIR = os.path.dirname(__file__)
PACKAGE_ROOT = os.path.normpath(os.path.join(TOPDIR, '..', '..'))


#===============================================================================
#
#                         Site-specific Configuration
#
#===============================================================================

try:
    secrets_conf_file = os.path.join(PACKAGE_ROOT, 'conf', 'secrets.conf')
    app_conf_file = os.path.join(PACKAGE_ROOT, 'conf', 'app.conf')
    ss_conf_file = os.path.join(PACKAGE_ROOT, 'conf', 'ss.conf')

    #Check if have the files
    open(secrets_conf_file, 'r')
    open(app_conf_file, 'r')
    open(ss_conf_file, 'r')


    secrets_config = ConfigParser()
    secrets_config.read([secrets_conf_file])    

    app_config = ConfigParser()
    app_config.read([app_conf_file])

    ss_config = ConfigParser()
    ss_config.read([ss_conf_file])

except IOError, reason:
    print 'Could not open configuration file. Please check your configuration folder.'
    print reason
    sys.exit()
except Exception, reason:
    print 'Error during conf:', reason
    sys.exit()



#===============================================================================
#
#                                 Credentials
#
#===============================================================================
missing_secret_msg = '''
Please set a secret key on secrets.conf, the 'Application' Section.
It should contain a secret key for this particular ESP installation. Used to 
provide a seed in secret-key hashing algorithms. Set this to a random string 
-- the longer, the better. 
The unix utility 'pwgen' is useful for generating long random password strings.
''' 

SECRET_KEY = secrets_config.get('Application', 'secret_key') or missing_config(missing_secret_msg)




#===============================================================================
#
#                                   General
#
#===============================================================================
# Set DEBUG to False when running in production!
DEBUG = True 
# No error control, because version.txt is included with source.
version_path =  os.path.join(TOPDIR, 'version.txt')
VERSION = open(version_path).readline().strip()
CODEDIR = TOPDIR
TEMPLATE_DEBUG = DEBUG
ADMINS = (
    ('Jason McVetta', 'jason.mcvetta@channing.harvard.edu'),
    ('Ross Lazarus', 'ross.lazarus@channing.harvard.edu'),
    ('Raphael Lullis', 'raphael.lullis@channing.harvard.edu'),
)
MANAGERS = (
    ('Jason McVetta', 'jason.mcvetta@channing.harvard.edu'),
    ('Ross Lazarus', 'ross.lazarus@channing.harvard.edu'),
    ('Raphael Lullis', 'raphael.lullis@channing.harvard.edu'),
    ('Michael Klompas', 'mklompas@partners.org'),
)
SITE_NAME = app_config.get('Site', 'name')
DATA_DIR = app_config.get('Data', 'folder') or os.path.join(PACKAGE_ROOT, 'assets', 'data')

#
# Some EMR systems, for instance Atrius Healthcare, include "fake" patients -- 
# test entries referring to fictional patients and events.  The variables below
# allow you to filter "fake" patients out of case reports (generated by 
# "case_report" command).  Any patient whose surname or MRN match the corresponding
# regex will be excluded.  The regular expression dialect to be used is that of the 
# underlying database platform.  
#
FAKE_PATIENT_SURNAME = '^XB' # Starts with 'XB' -- not case sensitive
FAKE_PATIENT_MRN = None
# 





#===============================================================================
#
#                                   Database
#
#===============================================================================
DATABASE_ENGINE = secrets_config.get('Database', 'engine') or missing_config('No db engine defined')
DATABASE_NAME = secrets_config.get('Database', 'name') or missing_config('No db name defined')
DATABASE_USER = secrets_config.get('Database', 'user') or missing_config('No db user defined')
DATABASE_PASSWORD = secrets_config.get('Database', 'password') or missing_config('No db password')
DATABASE_HOST = secrets_config.get('Database', 'host') 
DATABASE_PORT = secrets_config.get('Database', 'port') 
DATABASE_OPTIONS = {
    # Make PostgreSQL recover gracefully from caught exceptions
    #"autocommit": True,
}


#===============================================================================
#
#                                     ETL
#
#===============================================================================
# ETL_SOURCE determines what loader will be used.  Valid choices are:
#    'epic'
#    'hl7'
#    None
ETL_SOURCE = 'epic'
ETL_USE_FTP = True # Use built-in FTP function to retrieve Epic files
ETL_ARCHIVE = True # Should ETL files be archived after they have been loaded?


#===============================================================================
#
#                                  DOWNLOAD
#
#===============================================================================

# The 'FTP_*' variable names are legacy.  At some point, they should be updated 
# to 'DOWNLOAD_*'.
FTP_SERVER = secrets_config.get('FTP', 'server') or missing_config('No ftp server')
FTP_USER = secrets_config.get('FTP', 'user') or missing_config('No ftp user')
FTP_PASSWORD = secrets_config.get('FTP', 'password') or missing_config('No ftp password') 



#===============================================================================
#
#                                   UPLOAD
#
#===============================================================================
UPLOAD_SERVER = secrets_config.get('Upload', 'server')
UPLOAD_USER = secrets_config.get('Upload', 'user')
UPLOAD_PATH = secrets_config.get('Upload', 'path')
UPLOAD_PASSWORD = secrets_config.get('Upload', 'password')



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
    'ESP.ss',
    'ESP.ui',
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
#                               Case Reporting
#
#===============================================================================
CASE_REPORT_OUTPUT_FOLDER = os.path.join(DATA_DIR, 'case_reports')
CASE_REPORT_MDPH = False # Use MDPH case report output
CASE_REPORT_TEMPLATE = 'odh_hl7.txt'
CASE_REPORT_FILENAME_FORMAT = '%(timestamp)s-%(serial_number)s.hl7'
CASE_REPORT_BATCH_SIZE = 30 # Integer or None
#
# What transmission system should we use to report this case?  
# Valid choices are:
#    atrius
#    metrohealth
CASE_REPORT_TRANSMIT = 'ftp' 
#
# Mapping table to express lab specimen source in SNOMED codes, derived
# from MDPH ELR Portal specimen source vocabulary page.
#
CASE_REPORT_SPECIMEN_SOURCE_SNOMED_MAP = {
    'abscess':	'128477000',
    'amniotic fluid':	'77012006',
    'bile':	'70150004',
    'blood lead - capillary blood':	'31675002',
    'blood lead - venous blood':	'53130003',
    'body fluid, unsp':	'32457005',
    'bone':	'90780006',
    'brain':	'12738006',
    'bronchial washing':	'232595000',
    'bronchoalveolar lavage':	'397394009',
    'calculus (=stone)':	'56381008',
    'cerebrospinal fluid':	'65216001',
    'cervix':	'71252005',
    'cervical':	'71252005', # Added by JM to accomodate real Atrius data
    'colostrum':	'53875002',
    'cord blood':	'12499000',
    'curettage':	'68688001',
    'cyst':	'367643001',
    'dialysis fluid':	'116178008',
    'duodenal fluid specimen':	'122574004',
    'ear':	'1910005',
    'endocardium':	'37949006',
    'endometrium':	'2739003',
    'eosinophil':	'14793004',
    'erythrocyte':	'41898006',
    'exhaled air':	'65149000',
    'eye':	'81745001',
    'fibroblasts':	'52547004',
    'filter':	'116250002',
    'fistula':	'118622000',
    'gastric fluid/contents':	'258459007',
    'genital':	'263767004',
    'genital vaginal':	'76784001',
    'human milk':	'226789007',
    'line':	'50009006',
    'lymph node':	'59441001',
    'lymphocyte':	'56972008',
    'macrophage':	'58986001',
    'marrow':	'227250008',
    'meconium stool':	'28112009',
    'menstrual blood':	'312483008',
    'nasopharynx':	'71836000',
    'nose':	'45206002',
    'other':	'74964007',
    'pancreatic fluid':	'17387004',
    'penis':	'18911002',
    'pericardial fluid':	'34429004',
    'periorbital aspirate':	'263952009',
    'peritoneal fluid':	'409614007',
    'placenta':	'78067005',
    'plasma':	'50863008',
    'platelet':	'16378004',
    'pleural fluid':	'2778004',
    'polymorphonuclear neutrophil':	'119355008',
    'pus':	'11311000',
    'saliva':	'256897009',
    'seminal fluid':	'6993007',
    'serum':	'67922002',
    'skeletal muscle':	'127954009',
    'skin':	'39937001',
    'sperm':	'6789008',
    'sputum':	'45710003',
    'sterile':	'261029002',
    'stool':	'39477002',
    'surgical aspirate':	'258408006',
    'synovial fluid':	'6085005',
    'tb-accessory sinus':	'2095001',
    'tb-adenoids':	'181199001',
    'tb-adrenal gland':	'23451007',
    'tb-anus':	'53505006',
    'tb-appendix':	'66754008',
    'tb-bartholin\'s gland':	'87176006',
    'tb-blood vessel':	'361097006',
    'tb-bones of the extremities':	'48566001',
    'tb-bones of the girdle':	'272691005',
    'tb-bones of the head':	'110530005',
    'tb-bones of the pelvis':	'118645006',
    'tb-bones of the rib cage':	'113197003',
    'tb-bones of the shoulder':	'60880005',
    'tb-bones of the vertebral column':	'51282000',
    'tb-breast':	'76752008',
    'tb-broad ligament':	'34411009',
    'tb-bronchial fluid sample':	'258446004',
    'tb-bronchiole':	'55214000',
    'tb-bronchus':	'181215002',
    'tb-cardiac valve':	'17401000',
    'tb-choroid plexus':	'264450003',
    'tb-clitoris':	'65439009',
    'tb-colon':	'71854001',
    'tb-cranial nerve':	'244447006',
    'tb-dural sinus':	'54944003',
    'tb-ear appendages':	'204247007',
    'tb-embryo':	'57991002',
    'tb-epididymis':	'87644002',
    'tb-epiglottis':	'61563008',
    'tb-esophagus':	'32849002',
    'tb-extrahepatic bile duct':	'16014003',
    'tb-eye appendages':	'44888004',
    'tb-fallopian tube':	'181463001',
    'tb-fascia':	'181766008',
    'tb-female genital fluids':	'50473004',
    'tb-fetus':	'393497002',
    'tb-gallbladder':	'28231008',
    'tb-gums':	'113279002',
    'tb-heart':	'80891009',
    'tb-hypopharynx':	'81502006',
    'tb-implantation site':	'246314000',
    'tb-joints (synovial tissue)':	'118504007',
    'tb-kidney':	'64033007',
    'tb-labia':	'39117004',
    'tb-larynx':	'4596009',
    'tb-ligament':	'256660002',
    'tb-lip':	'48477009',
    'tb-liver':	'10200004',
    'tb-lung':	'39607008',
    'tb-male genital fluids':	'23378005',
    'tb-meninges':	'1231004',
    'tb-mouth':	'21082005',
    'tb-mouth, soft tissue of':	'145877004',
    'tb-myometrium':	'27232003',
    'tb-nasal passage':	'361347003',
    'tb-omentum':	'27398004',
    'tb-oropharynx':	'263376008',
    'tb-ovary':	'15497006',
    'tb-pancreas':	'15776009',
    'tb-parametrium':	'45682005',
    'tb-parathyroid gland':	'111002',
    'tb-parovarian region':	'368074001',
    'tb-pericardium':	'181295003',
    'tb-peripheral nerve':	'244457007',
    'tb-peritoneum':	'15425007',
    'tb-pharynx':	'181211006',
    'tb-pituitary gland':	'56329008',
    'tb-pleura':	'3120008',
    'tb-prostate':	'41216001',
    'tb-rectum':	'34402009',
    'tb-renal pelvis':	'25990002',
    'tb-salivary gland':	'385294005',
    'tb-scrotum':	'20233005',
    'tb-seminal vesicle':	'64739004',
    'tb-skin appendage':	'276160000',
    'tb-small intestine - duodenum':	'38848004',
    'tb-small intestine - ileum':	'34516001',
    'tb-small intestine - jejunum':	'21306003',
    'tb-soft tissue':	'181607009',
    'tb-spermatic cord':	'49957000',
    'tb-spinal cord':	'2748008',
    'tb-spleen':	'78961009',
    'tb-stomach':	'69695003',
    'tb-subcutaneus tissue':	'71966008',
    'tb-supporting structures of the tooth':	'8711009',
    'tb-tendon':	'13024002',
    'tb-tendon sheath':	'15434002',
    'tb-testis':	'40689003',
    'tb-thymus':	'9875009',
    'tb-thyroid gland':	'69748006',
    'tb-tongue':	'21974007',
    'tb-tonsil':	'367339008',
    'tb-tooth':	'38199008',
    'tb-trachea':	'44567001',
    'tb-umbilical cord':	'29870000',
    'tb-upper respiratory fluids':	'72869002',
    'tb-ureter':	'87953007',
    'tb-urinary bladder':	'89837001',
    'tb-uterus':	'35039007',
    'tb-vas deferens':	'245467009',
    'tb-vulva':	'45292006',
    'tb-mastoid cells':	'57222008',
    'tb-muscles of perinium':	'7295002',
    'tb-muscles of the head':	'22688005',
    'tb-muscles of the lower extremity':	'102292000',
    'tb-muscles of the neck':	'81727001',
    'tb-muscles of the trunk':	'68230005',
    'tb-muscles of the upper extremity':	'30608006',
    'tb-spinal nerve':	'3169005',
    'throat':	'54066008',
    'tissue':	'85756007',
    'tissue specimen from gall bladder':	'122656001',
    'tissue specimen from large intestine':	'122643008',
    'tissue specimen from lung':	'399492000',
    'tissue specimen from placenta':	'122736005',
    'tissue specimen from small intestine':	'122638001',
    'tissue specimen obtained from ulcer':	'122593002',
    'tube':	'83059008',
    'ulcer':	'56208002',
    'unknown':	'261665006',
    'urethra':	'13648007',
    'urine':	'78014005',
    'vomitus':	'1985008',
    'whole blood sample':	'258580003',
    'wick':	'116251003',
    'wound':	'13924000',
    'wound drain':	'258646005',
    }
    



#===============================================================================
#
#                                    Email
#
#===============================================================================
EMAIL_HOST = secrets_config.get('Email', 'host') or 'localhost'
EMAIL_HOST_USER = secrets_config.get('Email', 'user') or ''
EMAIL_HOST_PASSWORD = secrets_config.get('Email', 'password') or ''
EMAIL_PORT = secrets_config.get('Email', 'port') or ''
EMAIL_USE_TLS = secrets_config.get('Email', 'use_tls') or False
SERVER_EMAIL = secrets_config.get('Email', 'server_email') or 'noreply@example.org'
DEFAULT_FROM_EMAIL = secrets_config.get('Email', 'default_email') or 'noreply@example.org'
EMAIL_SUBJECT_PREFIX = secrets_config.get('Email', 'subject_prefix') or '[ESP]'



#===============================================================================
#
#                                 VAERS
#
#===============================================================================
VAERS_NOTIFICATION_RECIPIENT = 'someone@example.com'


#===============================================================================
#
#                                  SS
#
#===============================================================================
SS_EMAIL_RECIPIENT = ss_config.get('email', 'relevant_interval_notification')






#===============================================================================
#
#                                    JAVA
#
#===============================================================================
JAVA_DIR = "/usr/bin"
JAVA_JAR_DIR = '/usr/share/java'
app_full_path = lambda folder: os.path.realpath(os.path.join(TOPDIR, folder))
java_full_path = lambda folder: os.path.join(JAVA_JAR_DIR, folder)

JAVA_JARS = [
    java_full_path('axis.jar'),
    java_full_path('commons-logging.jar'), 
    java_full_path('commons-discovery.jar'), 
    java_full_path('jaxrpc.jar'), 
    java_full_path('wsdl4j.jar'), 
    java_full_path('saaj.jar'), 
    java_full_path('axis-ant.jar'), 
    java_full_path('log4j-1.2.jar'),
    app_full_path('axis-1_4/activation.jar'),
    app_full_path('axis-1_4/mail.jar'),
    app_full_path('sendMsgs/bcdc.jar'),
    app_full_path('sendMsgs')
    ]

JAVA_CLASSPATH = " %s " % ':'.join([str(jar) for jar in JAVA_JARS])


#===============================================================================
#
#                                  BATCH JOB
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BATCH_RETRIEVE_ETL_FILES = True
BATCH_MAIL_STATUS_REPORT = True
BATCH_GENERATE_CASE_REPORT = False
BATCH_TRANSMIT_CASE_REPORT = False


#===============================================================================
#
#                                   LOGGING
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LOG_FILE = '/var/log/esp' # Used only if LOG_LEVEL_FILE != None
LOG_FORMAT_CONSOLE = '%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
LOG_FORMAT_FILE = '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
LOG_FORMAT_SYSLOG = 'ESP:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
# BEWARE: If you set the log level to DEBUG, *copious* info will be logged!
LOG_LEVEL_CONSOLE = logging.INFO
LOG_LEVEL_FILE = None
LOG_LEVEL_SYSLOG = logging.WARN

