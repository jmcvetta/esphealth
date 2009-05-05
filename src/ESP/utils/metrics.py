#!/usr/bin/env python
'''
Report on data flow metrics
'''

import datetime
import csv
import sys

from ESP.utils import utils
from ESP.esp import models
from django.db.models import Avg, Max, Min, Count


OUT_FILE = '/home/rejmv/work/dev-esp/metrics.csv'


class Metric:
    
    # Class variable
    result = {} # {date: metric} where metric = {model: count}
    
    def __init__(self, model, date_field, convert_date=False):
        '''
        @param table:
        @type table:
        @param date_field:
        @type date_field:
        '''
        self.model = model
        self.date_field = date_field
        self.convert_date = convert_date
    
    def measure(self):
        for item in self.model.objects.values(self.date_field).distinct().annotate(count=Count('id')):
            day = item[self.date_field].date()
            count = item['count']
            try:
                day_result = self.result[day]
            except KeyError:
                self.result[day] = {}
                day_result = self.result[day]
            day_result[self.model._meta.object_name] = count
        


def main():
    Metric(model=models.Rx, date_field='lastUpDate').measure()
    Metric(model=models.Enc, date_field='lastUpDate').measure()
    Metric(model=models.Immunization, date_field='lastUpDate').measure()
    Metric(model=models.Lx, date_field='lastUpDate').measure()
    Metric(model=models.Case, date_field='caseLastUpDate').measure()
    all_days = Metric.result.keys()
    all_days.sort()
    writer = csv.writer(open(OUT_FILE, 'w'), delimiter=',')
    row = ['Date', 'Rx', 'Enc', 'Imm', 'Lx', 'Case']
    writer.writerow(row)
    for day in all_days:
        rx = Metric.result[day].get('Rx', 0)
        enc = Metric.result[day].get('Enc', 0)
        imm = Metric.result[day].get('Immunization', 0)
        lx = Metric.result[day].get('Lx', 0)
        case = Metric.result[day].get('Case', 0)
        row = [day, rx, enc, imm, lx, case]
        writer.writerow(row)

if __name__ == '__main__':
    main()