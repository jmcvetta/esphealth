#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime


EMPTY = ''

def mark_subsequences(seq):
    '''For a given sequence, we want to put find child elements that
    are sequences themselves. These elements receive a subsequence_num
    attribute.'''
    

class Component(object):
    def __init__(self, *subcomponents):
        self.subcomponents = subcomponents
        
    def render(self):
        '^'.join(self.components)

class ComponentCluster(object):
    def __init__(self, *components):
        self.components = components

class Segment(object):
    def __init__(self, *components, **kw):
        self.key = kw.get('key', None)
        self.components = components
        self.fields.insert(0, Component(self.key))

    def render(self, seq_counter=None):
        return '|'.join([str(x) for x in self.fields])


class SegmentGroup(object):
    def __init__(self, *segments):
        self.segments = segments

        
class Message(object):
    def __init__(self, *args, **kw):
        self.segments = args
        self.version = kw.get('version', '2.3.1') # Default version
        self.encoding = kw.get('encoding', '^~\&') # Default encoding
        self.receiving_facility = kw.get('receiving_facility', None)
        self.sending_facility = kw.get('sending_facility', None)
        self.application_type = kw.get('application_type', None)
        self.accept_type = kw.get('accept_type', None)
        self.type = kw.get('type', None)
        self.proc_id = kw.get('proc_id', None)


        self.header = Segment(
            self.encoding, EMPTY, self.sending_facility, EMPTY, 
            self.receiving_facility, timestamp, EMPTY, self.message_type, 
            timestamp+self.sending_facility, self.proc_id, self.version, 
            EMPTY, EMPTY, self.accept_type, self.application_type, 
            key='MSH'
            )


    def _render_header(self):
        now = datetime.datetime.now()
        timestamp = now.isoformat()
        
        return '|'.join([
            ])
    

    def render(self):
        return '\n'.join([
                _render_header(),
                self.segments])
    
    
    
    
    
            
        
        
        
        
    
    
