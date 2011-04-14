'''
                                  ESP Health
                          Heuristic Events Framework
                              Command Line Runner


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL
'''

import sys
import datetime
import optparse
import threading
import Queue
import thread
import signal
import time

from pkg_resources import iter_entry_points

from django.db import connection
from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.settings import HEF_THREAD_COUNT
from ESP.hef.base import BaseHeuristic
from ESP.hef.base import BaseEventHeuristic
from ESP.hef.base import BaseTimespanHeuristic
from ESP.hef.base import AbstractLabTest
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import PrescriptionHeuristic
from ESP.nodis.models import Case # hef.core and .models are dependencies of nodis/models, but this command script is not
from ESP import settings
from ESP.utils import log
from ESP.utils import log_query


#===============================================================================
#
#--- ~~~ Main ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
class Command(BaseCommand):
    
    help = 'Generate heuristic events'
    
    usage_str = '[options] [NAME, NAME, ...] \n'
    usage_str += '\n'
    usage_str += 'Runs heuristics for NAME if specified; otherwise, runs all heuristics.\n'
    usage_str += '\n'
    option_list = BaseCommand.option_list + (
        make_option('--list', action='store_true', dest='list', 
            help='List all abstract tests'),
        make_option('--threads', action='store', dest='thread_count', default=HEF_THREAD_COUNT,
            type='int', metavar='COUNT', help='Run in COUNT threads'),
        make_option('-n', '--new', action='store_true', dest='new'),
        )

    def handle(self, *args, **options):
        # TODO: We need a lockfile or some other means to prevent multiple 
        # instances running at once.
        log.debug('options: %s' % options)
        if options['new']:
            self.new_hef(args, options)
            return
        # 
        # Create dispatch dictionary of abstract tests and heuristics
        #
        dispatch = {}
        abstract_tests = AbstractLabTest.objects.all().order_by('name')
        for test in abstract_tests:
            dispatch[test.name] = test
        for dh in DiagnosisHeuristic.objects.all():
            name = 'dx--%s' % dh.name
            assert name not in dispatch
            dispatch[name] = dh
        for ph in PrescriptionHeuristic.objects.all():
            name = 'rx--%s' % ph.name
            assert name not in dispatch
            dispatch[name] = ph
        name_list = dispatch.keys()
        name_list.sort()
        if options['list']:
            print '-' * 80
            print '%-32s  %s' % ('NAME', 'DESCRIPTION')
            print '-' * 80
            for name in name_list:
                print '%-32s  %s' % (name, dispatch[name])
            sys.exit()
        if settings.DEBUG:
            log.warning('Django DEBUG is set to True.  This can cause massive memory consumption and slow performance.  Do not run in production without disabling debug in $ESP_HOME/etc/application.ini.')
        if args:
            #
            # Sanity Check
            #
            name_list = []
            for name in args:
                if not name in dispatch:
                    sys.stderr.write('Error, unknown test name: %s\n' % name)
                    sys.exit()
                name_list.append(name)
        #
        # Generate Events
        #
        log.debug('Starting %s threads' % options['thread_count'])
        if options['thread_count'] == 0:
            count = 0
            for name in name_list:
                count += dispatch[name].generate_events()
        else:
            queue = Queue.Queue()
            counter = Queue.Queue()
            counter.put(0)
            for i in range(options['thread_count']):
                t = ThreadedEventGenerator(queue, counter)
                t.daemon = True
                t.start()
            for name in name_list:
                event_generating_obj = dispatch[name]
                if isinstance(event_generating_obj, AbstractLabTest):
                    for heuristic in event_generating_obj.heuristic_set:
                        queue.put(heuristic)
                else:
                    queue.put(event_generating_obj)
            while threading.active_count() > 0:
                time.sleep(0.1)
            count = counter.get()
        log.info('Generated %s total new events' % count)
    
    def new_hef(self, args, options):
        if options['list']:
            return self.list(args, options)
        elif args:
            return self.by_name(args, options)
        else:
            return self.all(args, options)
    
    def by_name(self, args, options):
        '''
        Run heuristic(s) specified by name as arguments
        '''
        heuristics = {}
        selected_heuristics = []
        for h in BaseHeuristic.get_all():
            heuristics[h.short_name] = h
        for uri in args:
            if not uri in heuristics:
                print >> sys.stderr, 'Unknown heuristic specified:  %s' % uri
                sys.exit('-1')
            selected_heuristics.append(heuristics[uri])
        for h in selected_heuristics:
            h.generate()
    
    def all(self, args, options):
        event_counter = 0
        ts_counter = 0
        if options['thread_count'] == 0:
            count = 0
            for heuristic in BaseEventHeuristic.get_all():
                log.info('Running %s' % heuristic)
                count += heuristic.generate()
        else:
            queue = Queue.Queue()
            counter = Queue.Queue()
            error = Queue.Queue()
            counter.put(0)
            for i in range(options['thread_count']):
                t = ThreadedEventGenerator(queue, counter, error)
                t.daemon = True
                t.start()
            for heuristic in BaseEventHeuristic.get_all():
                log.info('Running %s' % heuristic)
                queue.put(heuristic)
            while error.empty() and threading.active_count() > 1:
                time.sleep(0.1)
            if not error.empty():
                sys.exit(-1)
            count = counter.get()
        for heuristic in BaseTimespanHeuristic.get_all():
            log.info('Running %s' % heuristic)
            ts_counter += heuristic.generate()
        log.info('Generated %20s events' % event_counter)
        log.info('Generated %20s timespans' % ts_counter)
        return event_counter + ts_counter
    
    def list(self, args, options):
        for h in BaseHeuristic.get_all():
            print h.short_name


class ThreadedEventGenerator(threading.Thread):
    '''
    Thread subclass to call generate_events() on various HEF objects
    '''
    
    def __init__(self, queue, counter, error):
        self.queue = queue
        self.counter = counter
        self.error = error
        threading.Thread.__init__(self)
    
    def run(self):
        try:
            event_generating_obj = self.queue.get()
            count = event_generating_obj.generate()
            i = self.counter.get()
            self.counter.put(i+count)
            del event_generating_obj
            self.queue.task_done()
        except BaseException, e:
            self.error.put(e)
            raise e
                    
            
