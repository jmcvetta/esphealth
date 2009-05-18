'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                        Utility methods for ESP project

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import os
import sys
import string
import traceback
import smtplib
import datetime
import time
import logging
import simplejson
import types

from django.db.models import Q
from django.core.paginator import Paginator

from ESP import settings



#===============================================================================
#
#--- ~~~ Logger ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def __get_logger():
    #logging.basicConfig(level=logging.DEBUG, datefmt='%d-%b--%H:%M')
    log = logging.getLogger()
    if not log.handlers: # Don't register handlers more than once
        file = logging.FileHandler(settings.LOG_FILE, 'a')
        file.setLevel(settings.LOG_LEVEL_FILE)
        file.setFormatter(logging.Formatter(settings.LOG_FORMAT_FILE))
        console = logging.StreamHandler()
        console.setLevel(settings.LOG_LEVEL_CONSOLE)
        console.setFormatter(logging.Formatter(settings.LOG_FORMAT_CONSOLE))
        log.setLevel(logging.DEBUG) # Maximum level that will be logged, regardless of per-handler levels
        log.addHandler(console)
        log.addHandler(file)
    return log
log = __get_logger()
#===============================================================================



filenlist = ['epicmem.esp.','epicpro.esp.','epicvis.esp.','epicord.esp.','epicres.esp.','epicmed.esp.','epicimm.esp.']
FILEBASE='epic' ##'epic' or 'test'

###################################
###################################
def getAnotherdate(date1, dayrange):
    try:
        return datetime.date(int(date1[:4]),int(date1[4:6]),int(date1[6:8]))+datetime.timedelta(dayrange)
    except:
        print 'Error when get another date: date1=%s,range=%s' % (date1,dayrange)

    return ''

                    
###################################
###################################
# 
# This can probably be deprecated and replaced with django.core.mail.send_mail()
#
def sendoutemail(towho=['rexua@channing.harvard.edu', 'MKLOMPAS@PARTNERS.ORG'],msg='',subject='ESP management'):
    ##send email
    sender = settings.EMAIL_SENDER
    
    headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, ','.join(towho), subject)
    
    message = headers + 'on %s\n%s\n' % (datetime.datetime.now(),msg)
    mailServer = smtplib.SMTP('localhost')
    mailServer.sendmail(sender, towho, message)
    mailServer.quit()

                                
###################################
###################################
def getPeriod(date1,date2):
    try:
        timeperiod = datetime.date(int(date1[:4]),int(date1[4:6]),int(date1[6:8]))-datetime.date(int(date2[:4]),int(date2[4:6]),int(date2[6:8]))
        return abs(timeperiod.days)
    except:
        return 0
    

        
################################
def getfilesByDay(files):

    files.sort()
    dayfiles={}
    returndays=[]
    ##filename shoule be: epic***.esp.MMDDYY or epic***.esp.MMDDYYYY
    for f in files:
        if f.lower().find('test')!=-1 and FILEBASE!='test': ##test file
            continue
        
        mmddyy =f[f.find('esp.')+4:]
        if len(mmddyy)==6: ##DDMMYY
            newdate='20'+mmddyy[-2:]+mmddyy[:4]
        elif mmddyy.find('_')!= -1: #monthly or weekly update, formart is epic***.esp.MMDDYYYY_m or epic***.esp.MMDDYYYY_w
            newdate=mmddyy[-6:-2]+mmddyy[:4]
        else:
            newdate=mmddyy[-4:]+mmddyy[:4]

            
        if (newdate,mmddyy) not in returndays:
            returndays.append((newdate,mmddyy))

    returndays.sort(key=lambda x:x[0])
    return returndays

                                                                        
def date_from_str(str):
    '''
    Returns a datetime.date instance based on the string representation of a
    date from LxOrderDate field.
    '''
    assert type(str) in [types.StringType, types.UnicodeType]
    year = int(str[0:4])
    month = int(str[4:6])
    day = int(str[6:8])
    return datetime.date(year, month, day)


def str_from_date(date):
    '''
    Returns a string representing the first date of the lookback window
    '''
    if date == None:
        return None
    assert isinstance(date, datetime.date)
    return date.strftime('%Y%m%d')
        


def native_code_from_cpt(cpt, compt):
    '''
    Generate a string for Lx.native_code from CPT + CPT Component
    '''
    if compt:
        return '%s--%s' % (cpt, compt)
    else:
        return cpt
    
    
class Flexigrid:
    '''
    Utility class for interacting with Flexigrid
    '''
    
    def __init__(self, request):
        '''
        Extracts standard Flexigrid variables from a Django REQUEST object.
        '''
        log.debug('request.POST: %s' % request.POST)
        self.sortname = request.REQUEST.get('sortname', 'id') # Field to sort on
        self.page = request.REQUEST.get('page', 1) # What page we are on
        self.sortorder = request.REQUEST.get('sortorder', 'asc') # Ascending/descending
        self.rp = int(request.REQUEST.get('rp', settings.ROWS_PER_PAGE)) # Num requests per page
        self.qtype = request.REQUEST.get('qtype', None) # Query type
        self.query = request.REQUEST.get('query', None) # Query string
        log.debug('sortname: %s' % self.sortname)
        log.debug('page: %s' % self.page)
        log.debug('sortorder: %s' % self.sortorder)
        log.debug('rp: %s' % self.rp)
        log.debug('qtype: %s' % self.qtype)
        log.debug('query: %s' % self.query)
    
    def json(self, rows, use_paginator=True, page_count=None):
        '''
        Returns JSON suitable for feeding to Flexigrid.
        @type rows: [{'id': 1, 'cell': ['field1, 'field2', ...]}, ...]
        @param use_paginator: Set this to false if you are going to do 
            pagination outside this class, for instance if you have a very
            large set of objects and do not want to fetch all rows.
        @param page_count: If use_paginator == False, then page_count should
            be set
        @type page_count: Integer
        '''
        assert use_paginator or type(page_count) == types.IntType # Sanity check -- gotta have one or the other
        p = Paginator(rows, self.rp)
        if use_paginator:
            rows = p.page(self.page).object_list
            count = p.count
        else:
            count = page_count
        json_dict = {
            'page': self.page,
            'total': count,
            'rows': rows
            }
        json = simplejson.dumps(json_dict)
        return json
            

def str_to_list(str):
    '''
    Converts a string representation of comma-delimited integers to a list of 
        integers.
    @param str: Comma-delimited integers 
    @type str: String
    @return: List
    '''
    result = []
    for item in str.split(','):
        if not item: # skip blank strings
            continue
        result += [int(item)]
    return result
