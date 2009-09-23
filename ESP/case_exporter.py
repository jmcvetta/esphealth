'''
Created on Sep 23, 2009

@author: rejmv
'''


import csv
import sys
import pprint

from ESP.esp.models import Case
from ESP.esp.models import Lx


file = open('old_cases.csv', 'w')

writer = csv.writer(file)

barfed = []

total = Case.objects.all().count()
counter = 0

for c in Case.objects.all().order_by('pk'):
    try:
        condition = c.caseRule.ruleName
        first = c.caseDemog.DemogFirst_Name
        last = c.caseDemog.DemogLast_Name
        mrn = c.caseDemog.DemogMedical_Record_Number
        date = Lx.objects.filter(pk__in=c.caseLxID.split(',')).order_by('LxOrderDate')[0].LxOrderDate
        line = [condition, date, mrn, last, first]
        writer.writerow(line)
    except KeyboardInterrupt:
        sys.exit()
    except:
        barfed.append(c.pk)
    counter += 1
    print '%20s / %s' % (counter, total)
    
print '-' * 80
print 'Barfed out on these cases:'
print [str(int(i)) for i in barfed]
	