#!/usr/bin/env python
'''
                                  ESP Health
                              ETL Infrastructure
                            HL7 to Database Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


import os
import datetime
import random
import pprint

from hl7 import hl7

from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.utils.utils import log



#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_e76e1d24-0e4c-11de-a002-fb07a536f7cf_2009-3-11 10.57.13.hl7'
TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_001514ea-fa42-11dd-a002-fb07a536f7cf_2009-2-13 21.48.46.hl7'
HL7_FOLDER = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/'


def load_msg(msg_str):
    #
    # MSH
    #
    message = hl7.parse(msg_str) # parsed msg
    msh_seg = hl7.segment('MSH', message)
    dateformat = '%Y%m%d%H%M%S'
    message_date = datetime.datetime.strptime(msh_seg[6][0], dateformat)
    log.debug('Message date: %s' % message_date)
    #
    # PID
    #
    pid_seg = hl7.segment('PID', message)
    patient_id_num = pid_seg[3][0]
    log.debug('Patient ID #: %s' % patient_id_num)
    



def main():
    all_files = os.listdir(HL7_FOLDER)
    filename = random.choice(all_files)
    m = open(os.path.join(HL7_FOLDER, filename)).read()
    log.debug('Parsing file "%s"' % filename)
    load_msg(m)


if __name__ == '__main__':
    main()