#!/usr/bin/env python
'''
Report on data flow metrics
'''

import datetime

from ESP.utils import utils
from ESP.esp import models
from django.db.models import Avg, Max, Min, Count


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
        for item in self.model.objects.values(self.date_field).distinct().annotate(count=Count('id'))[100]:
            day = item[self.date_field] 
            if self.convert_date:
                day = utils.date_from_str(day)
            count = item['count']
            try:
                day_result = self.result[day]
            except KeyError:
                self.result[day] = {}
                day_result = self.result[day]
            day_result[self.model._meta.object_name] = count
        


def main():
    Metric(model=models.Rx, date_field='RxOrderDate').measure()
    Metric(model=models.Enc, date_field='EncEncounter_Date').measure()
    Metric(model=models.Immunization, date_field='ImmDate').measure()
    Metric(model=models.Lx, date_field='LxDate_of_result').measure()
    r = Metric.result
    for i in r:
        print i, r[i]


if __name__ == '__main__':
    main()