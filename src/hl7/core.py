#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from copy import deepcopy

ENCODING = '^~\&'
VERSION = '2.3.1'
EMPTY = ''


import pdb

class Field(object):
    def __init__(self, name, *values, **kw):
        self.name = name
        default_value = str(kw.get('default', EMPTY))
        self.value = '^'.join([str(v) for v in values]) or default_value

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value

    def __cmp__(self, value):
        '''
        From python doc: object.__cmp__(self, other) Should return a
        negative integer if self < other, zero if self == other, a
        positive integer if self > other.  Considering we are
        interested in the value of the field, that's what we compare
        with.
        '''
        if self.value == value:
            return 0
        elif self.value > value:
            return 1
        else:
            return -1

class Segment():
    Fields = []
    def __init__(self, **kw):
        fields = dict([(f.name, f) for f in deepcopy(self.__class__.Fields)])
        
        for k, v in fields.items():
            self.__dict__[k] = v
                   
        for key, value in kw.items():
            if key in fields:
                self.__dict__[key] = value

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else: raise NameError, '%s Not a valid field for %s' % (
            name, self.__class__.__name__)
    

    def __str__(self):

        field_names = [f.name for f in self.__class__.Fields]
        return '|'.join([str(self.__dict__[k]) for k in field_names])


        
class Message(object):
    def __init__(self, version=VERSION, encoding=ENCODING):
        self.version = version
        self.encoding = encoding
        self.created_on = datetime.datetime.now()

    def __str__(self):
        raise NotImplementedError
    
    
    
    
    
      
        
        
        
    
    
