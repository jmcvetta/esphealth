#! /usr/bin/python
import glob
g = glob.glob('/home/ESP/NORTH_ADAMS/incomingHL7/*.hl7')
print 'found',g[:10]
for i,fname in enumerate(g):
     l = file(fname,'r').read().split('\r')
     for s in l:
	     if s[:3] == 'PD1':
              print i,s
