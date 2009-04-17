#! /usr/bin/python
import glob
g = glob.glob('/home/ESP/NORTH_ADAMS/incomingHL7/*.hl7')
n = len(g) # tot messages
nppv1 = 0
nppd1 = 0
nppv1n = 0
nppd1n = 0
nnone = 0
n1 = 0
n2 = 0
nsame = 0
ndiff = 0
nopv = []
for i,fname in enumerate(g):
     l = file(fname,'r').read().split('\r')
     gotone = False
     for s in l:
             pv = None
             pd = None
	     if s[:3] == 'PV1':
                 nppv1n += 1
                 pseg = s.split('|')[7] 
                 if pseg <> '^^':
                    nppv1 += 1
                    gotone = True      
                    pv = pseg  
                 else:
                    nopv.append(fname)

	     if s[:3] == 'PD1':
                 nppd1n += 1
                 pseg = s.split('|')[4] 
                 if pseg <> '^^^':
                    nppd1 += 1
                    gotone = True      
                    pd = pseg 

     if not gotone: 
              nnone += 1
     elif pd and pv:
           if pd == pv and (pd <> None):
                nsame += 1
           else:
                ndiff += 1    
     else:
          n1 += 1


print 'found %d messages with no physician of %d' % (nnone,n)
print '%d pv1 and %d pd1 with a physician' % (nppv1,nppd1)
print '%d one physician, %d two, %d different and %d both same' % (n1,n2,ndiff,nsame)
f = file('noNPI.txt','w')
for fname in nopv:
    eg = open(fname,'r').read().split('\r')
    f.write('\n'.join(eg))
    f.write('\n========================\n')
f.close()
