import os
import logging
from ESP.settings import TOPDIR
import datetime,logging
from ESP.esp.models import config
locals = config.objects.all()
for l in locals:
    if l.institution_name in os.listdir(TOPDIR):
        LOCALSITE=l.institution_name



###############################
def getLogging(appname,debug=0):
    
    appname = TOPDIR+ LOCALSITE +'/logs/'+appname
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