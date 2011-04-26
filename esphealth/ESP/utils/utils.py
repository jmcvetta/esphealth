'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                        Utility methods for ESP project

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import os
import gc
import re
import sys
import datetime
import time
import logging
import simplejson
import types
import sqlparse
import threading
import Queue
from concurrent import futures
from decimal import Decimal

from django.db import connection
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.forms.widgets import CheckboxInput, SelectMultiple
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe

from ESP import settings
from ESP.settings import LOG_FILE
from ESP.settings import LOG_LEVEL_FILE
from ESP.settings import LOG_LEVEL_CONSOLE
from ESP.settings import LOG_LEVEL_SYSLOG
from ESP.settings import LOG_FORMAT_FILE
from ESP.settings import LOG_FORMAT_CONSOLE
from ESP.settings import LOG_FORMAT_SYSLOG
from ESP.settings import QUERYSET_ITERATOR_CHUNKSIZE



#===============================================================================
#
#--- ~~~ Logger ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def __get_logger():
    '''
    Returns a logger configured per your settings
    '''
    log = logging.getLogger()
    log.handlers = [] # Clear out the handler set by manage.py
    log.setLevel(logging.DEBUG) # Maximum level that will be logged, regardless of per-handler levels
    if LOG_LEVEL_FILE:
        f = logging.FileHandler(LOG_FILE, 'a')
        f.setLevel(LOG_LEVEL_FILE)
        f.setFormatter(logging.Formatter(LOG_FORMAT_FILE))
        log.addHandler(f)
    if LOG_LEVEL_CONSOLE:
        console = logging.StreamHandler()
        console.setLevel(LOG_LEVEL_CONSOLE)
        console.setFormatter(logging.Formatter(LOG_FORMAT_CONSOLE))
        log.addHandler(console)
#    if LOG_LEVEL_SYSLOG:
#        sl = SysLogHandler('/dev/log')
#        sl.setLevel(LOG_LEVEL_SYSLOG)
#        sl.setFormatter(logging.Formatter(LOG_FORMAT_SYSLOG))
#        log.addHandler(sl)
    return log
log = __get_logger()
#===============================================================================


def log_query(purpose, qs):
    '''
    Log the SQL query that will be use to evaluate a queryset.
    @param purpose: Description of this query's purpose
    @type purpose:  String
    @param qs: QuerySet to evaluate
    @type qs:  QuerySet instance
    '''
    assert isinstance(qs, QuerySet)
    # If qs returns no result, then str(qs.query) throws an exception.  Hideous.
    try:
        sql = str(qs.query)
    except:
        log.debug('Django problems - could not render SQL for empty QuerySet')
        return
    try:
        formatted = '\n' + sqlparse.format(sql, reindent=True)
    except: # Sometimes Django produces invalid SQL
        log.debug('Invalid SQL produced by qs.query -- unable to pretty print')
        formatted = sql
    log.debug(purpose)
    log.debug(formatted)


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


class Profiler(object):
    def __init__(self):
        self.mark = datetime.datetime.now()

    def check(self, message=None):
        new_time = datetime.datetime.now()
        msg = str(message) or ''
        log.info(': '.join([msg, str(new_time - self.mark)]))
        self.mark = new_time


def timeit():
    '''Poor man's profiler'''
    def decorator(func):
        def proxyfunc(self, *args, **kw):
            import datetime
            before = datetime.datetime.now()
            res = func(self, *args, **kw)
            print('%s took %s' % (func.__name__, (datetime.datetime.now() - before)))
            return res
        return proxyfunc
    return decorator


def days_in_interval(begin_date, end_date):
    # We are going to get all of the days that cover the period between date and end_date
    # Note that xrange works on (0..end_date-1). If end_date is larger than
    # date, it will not be on the list, so we append to it.

    assert begin_date <= end_date

    days = [begin_date + datetime.timedelta(d) for d in xrange((end_date-begin_date).days)]
    days.append(end_date)

    return days


                                                                        
def date_from_str(timestamp):
    '''
    Given a string in timestamp format (YYYYMMDD), returns the corresponding date.
    If the string is only 6 characters long, assumes that is YYYYMM format and make day=1
    '''
    if re.match('^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d$', timestamp):
        format = '%Y-%m-%d %H:%M:%S'
    elif re.match('^\d{14}$', timestamp):
        format = '%Y%m%d%H%M%S'
    elif re.match('^\d{8}$', timestamp):
        format = '%Y%m%d'
    elif re.match('^\d{6}$', timestamp):
        format = '%Y%m'
    else:
        raise ValueError, '%s can not be converted into a date' % str(timestamp)
    
    return datetime.datetime.strptime(timestamp, format).date()

def make_date_folders(begin_date, end_date, **kw):
    folder = kw.get('root', os.path.dirname(__file__))
    subfolder = kw.get('subfolder', None)
    
    if subfolder: folder = os.path.join(folder, subfolder)

    same_year = (begin_date.year == end_date.year)
    same_month = same_year and (begin_date.month == end_date.month)
    same_day = same_month and (begin_date.day == end_date.day)

    if same_year: folder = os.path.join(folder, '%04d' % begin_date.year)
    if same_month: folder = os.path.join(folder, '%02d' % begin_date.month)
    if same_day: folder = os.path.join(folder, '%02d' % begin_date.day)

    if not os.path.isdir(folder): os.makedirs(folder)
    return folder


    

def str_from_date(date):
    '''
    Returns a string representing the first date of the lookback window
    '''
    if date == None:
        return None
    assert isinstance(date, datetime.date)
    try:
        return date.strftime('%Y%m%d')
    except ValueError: # ValueError: year=1898 is before 1900; the datetime strftime() methods require year >= 1900
        return datetime.date(1900,1,1).strftime('%Y%m%d')
        


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


def to_sql(model_instance):
    pass


class TableSelectMultiple(SelectMultiple):
    # This class taken from Django Snippets.
    # URL:    http://www.djangosnippets.org/snippets/518/
    # Author:  insin
    """
    Provides selection of items via checkboxes, with a table row
    being rendered for each item, the first cell in which contains the
    checkbox.

    When providing choices for this field, give the item as the second
    item in all choice tuples. For example, where you might have
    previously used::

        field.choices = [(item.id, item.name) for item in item_list]

    ...you should use::

        field.choices = [(item.id, item) for item in item_list]
    """
    def __init__(self, item_attrs, *args, **kwargs):
        """
        item_attrs
            Defines the attributes of each item which will be displayed
            as a column in each table row, in the order given.

            Any callable attributes specified will be called and have
            their return value used for display.

            All attribute values will be escaped.
        """
        super(TableSelectMultiple, self).__init__(*args, **kwargs)
        self.item_attrs = item_attrs

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        str_values = set([force_unicode(v) for v in value]) # Normalize to strings.
        for i, (option_value, item) in enumerate(self.choices):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            output.append(u'<tr><td>%s</td>' % rendered_cb)
            for attr in self.item_attrs:
                if callable(getattr(item, attr)):
                    content = getattr(item, attr)()
                else:
                    content = getattr(item, attr)
                output.append(u'<td>%s</td>' % escape(content))
            output.append(u'</tr>')
        return mark_safe(u'\n'.join(output))



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#--- Unit Conversion
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WEIGHT_REGEX = re.compile(r'''
(?P<lbs>\d+(\.\d*)?) \s* lbs? \s* ( (?P<oz>\d+(\.\d*)?) \s* (o|oz)?)?
''', 
re.VERBOSE)

def weight_str_to_kg(raw_string):
    '''
    Parses the content of raw_string and returns weight in kilograms as a Float.  
    '''
    if not raw_string:
        return None
    match = WEIGHT_REGEX.match(raw_string)
    if match:
        lbs = float(match.group('lbs'))
        if match.group('oz'):
            lbs += ( float(match.group('oz')) / 16 )
        kg = lbs / 2.20462262185
        return kg
    else:
        log.debug('Could not extract numeric weight from raw string: "%s"' % raw_string)
        return None
        
HEIGHT_REGEX = re.compile(r'''
(?P<feet>\d+(\.\d*)?) \s* ' \s* (?P<inches>\d+\.?\d*)?
''', re.VERBOSE)

def height_str_to_cm(raw_string):
    '''
    Parses the content of raw_string and returns height in centimeters as a Float.  
    If string parses to a height of 0, method will return None instead, to avoid 
    divide by zero issues in BMI calculation.
    '''
    if not raw_string:
        return None
    match = HEIGHT_REGEX.match(raw_string)
    if match:
        feet = float(match.group('feet'))
        if match.group('inches'):
            feet += ( float(match.group('inches')) / 12 )
        cm = feet * 30.48
        if cm: # Don't return 0 height
            return cm
    log.debug('Could not extract valid numeric height from raw string: "%s"' % raw_string)
    return None


def queryset_iterator(queryset, chunksize=QUERYSET_ITERATOR_CHUNKSIZE):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    If chunksize is -1, just returns the QuerySet that was passed in.
    
    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    
    
    --------------------------------------------------------------------------------
    
    Copied from http://djangosnippets.org/snippets/1949/ with modifications.
    '''
    if not queryset:
        return
    if chunksize < 0:
        for row in queryset.iterator():
            yield row
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()



def wait_for_threads(fs, max_workers=settings.HEF_THREAD_COUNT):
    '''
    Utility function for running time consuming tasks in threads.  
    @param fs: Functions to be run concurrently.  Each function should return an integer 'count' value
    @type  fs: List of callables
    @return: Sum of all count values returned by functions
    @rtype:  Integer
    '''
    log.debug('Starting thread pool executor with max %s workers' % max_workers)
    if not max_workers > 0:
        raise RuntimeError('Cannot call wait_for_threads with max_workers less than 1, but you called it with %s workers' % max_workers)
    counter = 0
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submitted = []
        for func in fs:
            log.debug('Submitting to thread pool: %s' % func)
            if type(func) is tuple: # If this function has arguments
                submitted.append( executor.submit(*func) )
            else:
                submitted.append( executor.submit(func) )
        try:
            log.debug('Waiting for thread completion')
            #while futures.wait(submitted, timeout=1).not_done: # Wait until all futures are done
                #pass
            for future in futures.as_completed(submitted):
                log.debug('Completed: %s' % future)
                error = future.exception(timeout=0.1)
                if error is not None:
                    log.critical('Unhandled exception in %s:\n%s' % (future, error))
                    raise error
                result = future.result(timeout=0.1)
                if type(result) in [int, float, Decimal]:
                    counter += result
        except BaseException, e:
            for future in submitted:
                future.cancel()
            executor.shutdown(wait=False)
            raise e
    return counter