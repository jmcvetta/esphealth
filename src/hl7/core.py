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
        self.is_serial = kw.get('serial', False)
        self.is_subsequence_indicator = kw.get('subsequence', False)
        self.value = list(values) or default_value

        
    def __str__(self):
        if type(self.value) is list:
            return '^'.join([str(x) for x in self.value])
        
        return str(self.value)

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
    PROTECTED_NAMES = ['_fields', '_sequence_field', '_subsequence_field']
    def __init__(self, **kw):
              
        self._fields = dict(
            [(f.name, f) for f in deepcopy(self.__class__.Fields)])
        self._sequence_field = None
        self._subsequence_field = None


        # Find the sequence and subsequence fields, if they exist.
        for field in self._fields.values():
            if field.is_serial: 
                self._sequence_field = field.name
            if field.is_subsequence_indicator: 
                self._subsequence_field = field.name

        # Set the values that were passed during initizalition
        for key, value in kw.items():
            if key in self._fields:
                self._fields[key] = value

        

    def __setattr__(self, name, value):
        '''
        This allows us to set values from the Segment by the name of
        the field. E.g.: aOBR.ordering_provider = 'John Smith'.
        
        Also, it allows us to define the sequence and subsequence
        values always using the same name. For instance, in some
        fields, the sequence number is called set_id, on others
        sequence_number. To make things more uniform, trying to set
        the attribute sequence_id will look for the correct field name
        and set the value of the sequence.
        '''

        if name in Segment.PROTECTED_NAMES:
            self.__dict__[name] = value
            return

        if name in self._fields:
            self._fields[name].value = value
        elif name == 'sequence_id': 
            self._fields[self._sequence_field].value = value
        elif name == 'subsequence_id': 
            self._fields[self._subsequence_field].value = value            
        else: raise NameError, '%s Not a valid field for %s' % (
            name, self.__class__.__name__)


    def __getattr__(self, name):
        if name in Segment.PROTECTED_NAMES:
            return self.__dict__[name]
        else:
            return self._fields[name].value

    def __str__(self):

        field_names = [f.name for f in self.__class__.Fields]
        values = [str(self._fields[k]) for k in field_names]
        values.insert(0, self.__class__.__name__)
        return '|'.join(values)


class SegmentTree():
    '''
    Hl7 is a pipe-delimited, line-oriented text format. Despite that,
    most of the messages require some format of tree like hierachy
    between the segments. To keep the internal organization of the
    segments, the class SegmentTree should be used to define a parent
    segment and its children.
    '''
    def __init__(self, parent, children):
        self.parent = parent
        self.children = children if type(children) is list else [children]
        
        for idx, child in enumerate(self.children):
            child.sequence_id = idx+1

    def __str__(self):
        parent_and_children = [self.parent] + self.children
        return '\n'.join([str(x) for x in parent_and_children])
            
    


        
class Message(object):
    def __init__(self, version=VERSION, encoding=ENCODING):
        self.version = version
        self.encoding = encoding
        self.created_on = datetime.datetime.now()

    def __str__(self):
        raise NotImplementedError
