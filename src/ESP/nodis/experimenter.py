#!/usr/bin/env python

class DiseaseCriterion(object):
    '''
    One set of rules for algorithmically defining a disease.  Satisfying a 
    single disease criterion is sufficient to indicate a case of that disease, 
    but a given disease may have arbitrarily many criteria.
    '''
    def __init__(self,  name, version, window, require, require_past = None, require_past_window = None,
        exclude = None, exclude_past = None):
        '''
        @param name: Name of this criterion
        @type name: String
        @param version: Definition version
        @type version: Integer
        @param window: Time window in days
        @type window: Integer
        @param require: Events that must have occurred within 'window' days of one another
        @type require:  List of tuples of HeuristicEvent instances.  The tuples 
            are AND'ed together, and each item in a tuple is OR'ed.
        @param require_past: Events that must have occurred in the past, but 
            not within this criterion's time window
        @type require_past: List of tuples.  See above.
        @param require_past_window: require_past events must have occurred 
            prior to 'window', but less than this many days in the past
        @type require_past_window: Integer
        @param exclude: Events that must not have occurred within window days of one another
        @type exclude: List of tuples.  See above.
        @param exclude_past: Events that must not have ever occurred prior to 'window'
        @type exclude_past: List of tuples.  See above.
        '''
        assert name
        assert version
        assert window
        assert require
        if require_past:
            assert require_past_window
        self.name = name
        self.version = version
        self.window = datetime.timedelta(window)
        self.require = require
        self.require_past = require_past
        self.require_past_window = require_past_window
        self.exclude = exclude
        self.exclude_past = exclude_past
    
    def matches(self, begin_date=None, end_date=None):
        #
        # Examine only the time slice specified
        #
        all_events = HeuristicEvent.objects.all()
        if begin_date:
            all_events = all_events.filter(date__gte=begin_date)
        if end_date:
            all_events = all_events.filter(date__lte=end_date)
        #
        # Do we match all required events?
        #
        pde = {} # patient/date/event:  {patient: {date: [event, ...], date: [event, ...], ...}, ...}
        # Each requirement is an instance of (a subclass of) BaseHeuristic
        first_req = self.require[0] # Doesn't matter which tuple is considered first, since they are AND'ed
        other_reqs = self.require[1:]
        for e in all_events.filter(heuristic_name__in=[h.name for h in first_req]):
            #
            print e.date
            print type(e.date)
            sys.exit()
            #
            try:
                events_by_date = pde[e.patient]
            except KeyError:
                events_by_date = pde[e.patient] = {}
            try:
                events_by_date[e.date].append(e)
            except KeyError:
                events_by_date[e.date] = [e]
        # For each patient we have one or more dates, and for each of those 
        # dates we have one or more events.  Since these events
        # are required, each (event +/- self.window) defines a temporal slice
        # in which to query for other events.
        for patient in pde:
            for date in pde[patient]: # 'day' so not to conflict w/ reserved word 'date'
                begin = date - self.window
                end = date + self.window



def main():
    pass


if __name__ == '__main__':
    main()