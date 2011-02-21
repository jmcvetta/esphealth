import os
from esp.settings import TOPDIR,CODEDIR
import datetime,logging
from esp.esp.models import config
locals = config.objects.all()
LOCALSITE='HVMA' # hack!
for l in locals:
    if l.institution_name in os.listdir(TOPDIR):
        LOCALSITE=l.institution_name


###################################


###################################
def getJavaInfo():
    javadir="/usr/java/jdk1.5.0_09/bin/"
#    javadir="/usr/bin/"
    javaclass=" /home/ESP/ESP/sendMsgs:/home/ESP/axis-1_4/activation.jar:/usr/local/axis-1_4/lib/axis.jar:/usr/local/axis-1_4/lib/commons-logging-1.0.4.jar:/usr/local/axis-1_4/lib/commons-discovery-0.2.jar:/usr/local/axis-1_4/lib/jaxrpc.jar:/usr/local/axis-1_4/lib/wsdl4j-1.5.1.jar:/usr/local/axis-1_4/lib/saaj.jar:/usr/local/axis-1_4/lib/axis-ant.jar:/usr/local/axis-1_4/lib/log4j-1.2.8.jar:/home/ESP/axis-1_4/mail.jar:/home/ESP/ESP/sendMsgs/bcdc.jar "
    sendMsgcls = 'sendMsg'
    return (javadir, javaclass,sendMsgcls)
    

###############################
def getLogging(appname,debug=0):
    logdir = os.path.join(TOPDIR,LOCALSITE, 'logs/')
    if not os.path.isdir(logdir):
        os.mkdir(logdir)
        
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
