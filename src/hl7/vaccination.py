from core import Component, SegmentGroup, Segment, EMPTY

from datetime.datetime import now

class OBR(Segment):
    def __init__(self, *args, **kw):
        self.key = 'OBR'
        self.record_type = kw.get('record_type', None)
        self.timestamp = kw.get('date', now()).strfime('%Y%m%d')

    def __str__(self):
        return '|'.join([self.key, self.sequence_number, EMPTY, EMPTY,
                         str(self.record_type), EMPTY, EMPTY, 
                         self.timestamp])

class OBX(Segment):
    def __init__(self, **kw):
        self.key = 'OBX'
        

def VaccinationOnDateReport():
    return SegmentGroup(
        Segment(
    
    
