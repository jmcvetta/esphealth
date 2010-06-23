'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                                  ESP Health
                                Django Settings

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import os
import sys
import logging
from configobj import ConfigObj
from configobj import flatten_errors
from validate import Validator


TOPDIR = os.path.dirname(__file__)
PACKAGE_ROOT = os.path.normpath(os.path.join(TOPDIR, '..', '..'))
# One could also set CONFIG_FOLDER manually, to something like '/etc/esp', if 
# so desired.
CONFIG_FOLDER = os.path.join(PACKAGE_ROOT, 'etc')


#-------------------------------------------------------------------------------
#
# Process INI files
#
#-------------------------------------------------------------------------------
validator = Validator()
application_ini = os.path.join(CONFIG_FOLDER, 'application.ini')
application_spec = ConfigObj(os.path.join(TOPDIR, 'application.spec.ini'), interpolation=False, list_values=False)
secrets_ini = os.path.join(CONFIG_FOLDER, 'secrets.ini')
secrets_spec = os.path.join(TOPDIR, 'secrets.spec.ini')
secrets = ConfigObj(secrets_ini, configspec=secrets_spec)
config = ConfigObj(application_ini, configspec=application_spec, interpolation=False)

bad_config = False
for ini_file, conf_obj in [(secrets_ini, secrets), (application_ini, config)]:
    if not os.path.exists(ini_file):
        print 'Cound not find configuration file %s' % ini_file
        if os.access(ini_file, os.W_OK):
            print 'Creating new configuration file.  Please fill it in with your values.'
        else:
            print 'Cannot create new configuration file -- do not have write access to %s' % ini_file
        print
        bad_config = True
    results = conf_obj.validate(validator, copy=True)
    try:
        conf_obj.write()
    except IOError:
        logging.info('Do not have write permission on %s' % ini_file)
    if results != True:
        for (section_list, key, _) in flatten_errors(config, results):
            print '%s:' % ini_file
            if key is not None:
                print '    The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list))
            else:
                print '    The following section was missing:%s ' % ', '.join(section_list)
        bad_config = True
if bad_config:
    print
    print 'Configuration error, cannot start ESP.'
    print
    sys.exit(-1)


#===============================================================================
#
# Configuration Variables
#
#===============================================================================

version_path =  os.path.join(TOPDIR, 'version.txt')
VERSION = open(version_path).readline().strip()

SECRET_KEY = secrets['General']['secret_key']
DEBUG = config['General']['django_debug']
CODEDIR = TOPDIR
TEMPLATE_DEBUG = DEBUG
ADMINS = [(i,i) for i in config['General']['admins']]
MANAGERS = [(i,i) for i in config['General']['managers']]
SITE_NAME = config['General']['site_name']
DATA_DIR = config['General']['data_folder']
FAKE_PATIENT_SURNAME = config['Reporting']['fake_patient_surname']
FAKE_PATIENT_MRN = config['Reporting']['fake_patient_mrn']
DATABASE_ENGINE = config['Database']['engine']
DATABASE_NAME = config['Database']['db_name']
DATABASE_USER = config['Database']['username']
DATABASE_PASSWORD = secrets['General']['database_password']
DATABASE_HOST = config['Database']['host']
DATABASE_PORT = config['Database']['port']
# Do we need to include DATABASE_OPTIONS in esp.ini?
DATABASE_OPTIONS = {
    # Make PostgreSQL recover gracefully from caught exceptions
    #"autocommit": True,   
}
ETL_SOURCE = config['ETL']['source']
ETL_USE_FTP = config['ETL']['retrieve_files'] # Use built-in FTP function to retrieve Epic files
ETL_ARCHIVE = config['ETL']['archive'] # Should ETL files be archived after they have been loaded?
FTP_SERVER = config['ETL']['server']
FTP_USER = config['ETL']['username']
FTP_PASSWORD = secrets['General']['etl_server_password']
FTP_PATH = config['ETL']['path']
UPLOAD_SERVER = config['Reporting']['upload_server']
UPLOAD_USER = config['Reporting']['upload_username']
UPLOAD_PASSWORD = secrets['General']['upload_password']
UPLOAD_PATH = config['Reporting']['upload_path']
HL7_DIR = os.path.join(DATA_DIR, 'hl7')
SITE_ID = 1 # This probably does not need to be configurable
TIME_ZONE = config['General']['time_zone']
LANGUAGE_CODE = config['General']['language_code']
DATE_FORMAT = config['General']['date_format']
ROWS_PER_PAGE = config['Web']['rows_per_page']
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(TOPDIR, 'media')
MEDIA_URL = config['Web']['media_url']
ADMIN_MEDIA_PREFIX = config['Web']['admin_media_prefix']
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
    os.path.join(CONFIG_FOLDER, 'templates'),
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
    #'ESP.static', 
    #'ESP.conf', 
    'ESP.emr',
    #'ESP.hef',
    #'ESP.nodis',
    #'ESP.vaers',
    #'ESP.ss',
    #'ESP.ui',
)
CASE_REPORT_OUTPUT_FOLDER = os.path.join(DATA_DIR, 'case_reports')
CASE_REPORT_MDPH = config['Reporting']['use_mdph_format']
CASE_REPORT_TEMPLATE = config['Reporting']['template']
CASE_REPORT_FILENAME_FORMAT = config['Reporting']['filename_format']
CASE_REPORT_BATCH_SIZE = config['Reporting']['cases_per_message']
CASE_REPORT_TRANSMIT = config['Reporting']['transport']
#
# Mapping table to express lab specimen source in SNOMED codes, derived
# from MDPH ELR Portal specimen source vocabulary page.
#
# Eventually this should be moved to the database -- ConfigObj doesn't handle
# dicitonaries very well, and this is not a static value, so it should not here
# in settings.py
#
CASE_REPORT_SPECIMEN_SOURCE_SNOMED_MAP = {
    'abscess':    '128477000',
    'amniotic fluid':    '77012006',
    'bile':    '70150004',
    'blood lead - capillary blood':    '31675002',
    'blood lead - venous blood':    '53130003',
    'body fluid, unsp':    '32457005',
    'bone':    '90780006',
    'brain':    '12738006',
    'bronchial washing':    '232595000',
    'bronchoalveolar lavage':    '397394009',
    'calculus (=stone)':    '56381008',
    'cerebrospinal fluid':    '65216001',
    'cervix':    '71252005',
    'cervical':    '71252005', # Added by JM to accomodate real Atrius data
    'colostrum':    '53875002',
    'cord blood':    '12499000',
    'curettage':    '68688001',
    'cyst':    '367643001',
    'dialysis fluid':    '116178008',
    'duodenal fluid specimen':    '122574004',
    'ear':    '1910005',
    'endocardium':    '37949006',
    'endometrium':    '2739003',
    'eosinophil':    '14793004',
    'erythrocyte':    '41898006',
    'exhaled air':    '65149000',
    'eye':    '81745001',
    'fibroblasts':    '52547004',
    'filter':    '116250002',
    'fistula':    '118622000',
    'gastric fluid/contents':    '258459007',
    'genital':    '263767004',
    'genital vaginal':    '76784001',
    'human milk':    '226789007',
    'line':    '50009006',
    'lymph node':    '59441001',
    'lymphocyte':    '56972008',
    'macrophage':    '58986001',
    'marrow':    '227250008',
    'meconium stool':    '28112009',
    'menstrual blood':    '312483008',
    'nasopharynx':    '71836000',
    'nose':    '45206002',
    'other':    '74964007',
    'pancreatic fluid':    '17387004',
    'penis':    '18911002',
    'pericardial fluid':    '34429004',
    'periorbital aspirate':    '263952009',
    'peritoneal fluid':    '409614007',
    'placenta':    '78067005',
    'plasma':    '50863008',
    'platelet':    '16378004',
    'pleural fluid':    '2778004',
    'polymorphonuclear neutrophil':    '119355008',
    'pus':    '11311000',
    'saliva':    '256897009',
    'seminal fluid':    '6993007',
    'serum':    '67922002',
    'skeletal muscle':    '127954009',
    'skin':    '39937001',
    'sperm':    '6789008',
    'sputum':    '45710003',
    'sterile':    '261029002',
    'stool':    '39477002',
    'surgical aspirate':    '258408006',
    'synovial fluid':    '6085005',
    'tb-accessory sinus':    '2095001',
    'tb-adenoids':    '181199001',
    'tb-adrenal gland':    '23451007',
    'tb-anus':    '53505006',
    'tb-appendix':    '66754008',
    'tb-bartholin\'s gland':    '87176006',
    'tb-blood vessel':    '361097006',
    'tb-bones of the extremities':    '48566001',
    'tb-bones of the girdle':    '272691005',
    'tb-bones of the head':    '110530005',
    'tb-bones of the pelvis':    '118645006',
    'tb-bones of the rib cage':    '113197003',
    'tb-bones of the shoulder':    '60880005',
    'tb-bones of the vertebral column':    '51282000',
    'tb-breast':    '76752008',
    'tb-broad ligament':    '34411009',
    'tb-bronchial fluid sample':    '258446004',
    'tb-bronchiole':    '55214000',
    'tb-bronchus':    '181215002',
    'tb-cardiac valve':    '17401000',
    'tb-choroid plexus':    '264450003',
    'tb-clitoris':    '65439009',
    'tb-colon':    '71854001',
    'tb-cranial nerve':    '244447006',
    'tb-dural sinus':    '54944003',
    'tb-ear appendages':    '204247007',
    'tb-embryo':    '57991002',
    'tb-epididymis':    '87644002',
    'tb-epiglottis':    '61563008',
    'tb-esophagus':    '32849002',
    'tb-extrahepatic bile duct':    '16014003',
    'tb-eye appendages':    '44888004',
    'tb-fallopian tube':    '181463001',
    'tb-fascia':    '181766008',
    'tb-female genital fluids':    '50473004',
    'tb-fetus':    '393497002',
    'tb-gallbladder':    '28231008',
    'tb-gums':    '113279002',
    'tb-heart':    '80891009',
    'tb-hypopharynx':    '81502006',
    'tb-implantation site':    '246314000',
    'tb-joints (synovial tissue)':    '118504007',
    'tb-kidney':    '64033007',
    'tb-labia':    '39117004',
    'tb-larynx':    '4596009',
    'tb-ligament':    '256660002',
    'tb-lip':    '48477009',
    'tb-liver':    '10200004',
    'tb-lung':    '39607008',
    'tb-male genital fluids':    '23378005',
    'tb-meninges':    '1231004',
    'tb-mouth':    '21082005',
    'tb-mouth, soft tissue of':    '145877004',
    'tb-myometrium':    '27232003',
    'tb-nasal passage':    '361347003',
    'tb-omentum':    '27398004',
    'tb-oropharynx':    '263376008',
    'tb-ovary':    '15497006',
    'tb-pancreas':    '15776009',
    'tb-parametrium':    '45682005',
    'tb-parathyroid gland':    '111002',
    'tb-parovarian region':    '368074001',
    'tb-pericardium':    '181295003',
    'tb-peripheral nerve':    '244457007',
    'tb-peritoneum':    '15425007',
    'tb-pharynx':    '181211006',
    'tb-pituitary gland':    '56329008',
    'tb-pleura':    '3120008',
    'tb-prostate':    '41216001',
    'tb-rectum':    '34402009',
    'tb-renal pelvis':    '25990002',
    'tb-salivary gland':    '385294005',
    'tb-scrotum':    '20233005',
    'tb-seminal vesicle':    '64739004',
    'tb-skin appendage':    '276160000',
    'tb-small intestine - duodenum':    '38848004',
    'tb-small intestine - ileum':    '34516001',
    'tb-small intestine - jejunum':    '21306003',
    'tb-soft tissue':    '181607009',
    'tb-spermatic cord':    '49957000',
    'tb-spinal cord':    '2748008',
    'tb-spleen':    '78961009',
    'tb-stomach':    '69695003',
    'tb-subcutaneus tissue':    '71966008',
    'tb-supporting structures of the tooth':    '8711009',
    'tb-tendon':    '13024002',
    'tb-tendon sheath':    '15434002',
    'tb-testis':    '40689003',
    'tb-thymus':    '9875009',
    'tb-thyroid gland':    '69748006',
    'tb-tongue':    '21974007',
    'tb-tonsil':    '367339008',
    'tb-tooth':    '38199008',
    'tb-trachea':    '44567001',
    'tb-umbilical cord':    '29870000',
    'tb-upper respiratory fluids':    '72869002',
    'tb-ureter':    '87953007',
    'tb-urinary bladder':    '89837001',
    'tb-uterus':    '35039007',
    'tb-vas deferens':    '245467009',
    'tb-vulva':    '45292006',
    'tb-mastoid cells':    '57222008',
    'tb-muscles of perinium':    '7295002',
    'tb-muscles of the head':    '22688005',
    'tb-muscles of the lower extremity':    '102292000',
    'tb-muscles of the neck':    '81727001',
    'tb-muscles of the trunk':    '68230005',
    'tb-muscles of the upper extremity':    '30608006',
    'tb-spinal nerve':    '3169005',
    'throat':    '54066008',
    'tissue':    '85756007',
    'tissue specimen from gall bladder':    '122656001',
    'tissue specimen from large intestine':    '122643008',
    'tissue specimen from lung':    '399492000',
    'tissue specimen from placenta':    '122736005',
    'tissue specimen from small intestine':    '122638001',
    'tissue specimen obtained from ulcer':    '122593002',
    'tube':    '83059008',
    'ulcer':    '56208002',
    'unknown':    '261665006',
    'urethra':    '13648007',
    'urine':    '78014005',
    'vomitus':    '1985008',
    'whole blood sample':    '258580003',
    'wick':    '116251003',
    'wound':    '13924000',
    'wound drain':    '258646005',
    }
EMAIL_HOST = config['Email']['host']
EMAIL_HOST_USER = config['Email']['username']
EMAIL_HOST_PASSWORD = secrets['General']['email_password']
EMAIL_PORT = config['Email']['port']
EMAIL_USE_TLS = config['Email']['use_tls']
SERVER_EMAIL = config['Email']['server_email']
DEFAULT_FROM_EMAIL = config['Email']['default_from_email']
EMAIL_SUBJECT_PREFIX = config['Email']['subject_prefix']
VAERS_NOTIFICATION_RECIPIENT = 'someone@example.com'
SS_EMAIL_RECIPIENT = config['SS']['email_recipient']
# Java stuff is very Atrius-specific, so it is not going in esp.ini.
# Eventually we should probably remove the entire Java upload app, since
# presumably everything it does can be handled by native Python code.
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
BATCH_ETL = config['Batch']['etl']
BATCH_MAIL_STATUS_REPORT = config['Batch']['mail_status_report']
BATCH_GENERATE_CASE_REPORT = config['Batch']['generate_case_report']
BATCH_TRANSMIT_CASE_REPORT = config['Batch']['transmit_case_report']
# Logging levels, so we can use strings for configuration
_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    }
LOG_FILE = config['Logging']['log_file'] # Used only if LOG_LEVEL_FILE != None
LOG_FORMAT_CONSOLE = config['Logging']['log_format_console']
LOG_FORMAT_FILE = config['Logging']['log_format_file']
LOG_FORMAT_SYSLOG = config['Logging']['log_format_syslog']
# BEWARE: If you set the log level to DEBUG, *copious* info will be logged!
LOG_LEVEL_CONSOLE = _levels[config['Logging']['log_level_console']]
LOG_LEVEL_FILE = _levels[config['Logging']['log_level_file']]
LOG_LEVEL_SYSLOG = _levels[config['Logging']['log_level_syslog']]

# Sphinx 0.9.9
SPHINX_API_VERSION = 0x116
