import logging


USESQLITE=0
RUNFAKEDATA=0
SITEROOT='/ESP'
LOCALSITE='NORTH_ADAMS' #Prototype' #'HVMA'

MYSQL_DB_USER = 'ESP'
MYSQL_DB_PASSWORD = 'aehi7ieMooTh6Tooquoh2au7oyoobaiMich9ahko'

SQLITE_DB_USER = 'rossSQL'
SQLITE_DB_PASSWORD = 'SQLross'

FTPUSER = 'HEALTHONE\\rlazarus'
FTPPWD = 'Welcome00'
FTPSERVER = 'n2ftp001.hvma.org'


EMAILSENDER='espuser@lkenpesp.healthone.org'

#===============================================================================
#--- Logging
#-------------------------------------------------------------------------------
LOG_FORMAT = '%(levelname)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s'
LOG_LEVEL = logging.DEBUG
