import os, glob
import datetime
import re
import zipfile

from django.db.models import Count

from ESP.emr.models import Encounter
from ESP.ss.models import NonSpecialistVisitEvent, Site, age_group_filter
from ESP.ss.utils import report_folder, age_identifier
from ESP.utils.utils import log, str_from_date, days_in_interval

class Hsph(object):

    BASE_FILENAME = 'ESP_Atrius_HSPH_week_%s_%s.xls'
   
    def __init__(self, day, heuristic):
        self.begin_date = day - datetime.timedelta(7)
        self.end_date = day
        self.days = days_in_interval(self.begin_date, self.end_date)
        self.folder = report_folder(begin_date, day, subfolder='hsph', resolution='month')        
        self.heuristic = heuristic
        self.age_groups = [(0, 5), (5, 20), (20, 25), (25, 50), (50, 65), (65, None)]
        

    def make_case_files(self):
        log.info('HSPH files for %s on week %s-%s' % (self.heuristic.name, 
                                                      self.start_date, self.end_date))

        filename = Hsph.BASE_FILENAME % (str_from_date(self.begin_date), str_from_date(self.end_date))
        age_group_columns = [age_group_identifier(group) for group in self.age_groups] 
        header = ['encounter date', 'residential zip'] + age_group_columns + [
            'total ILI visits', 'total clinic + urgent visits', '% ILI']

        outfile = open(os.path.join(self.folder, filename), 'w')
        outfile.write('\t'.join(header) + '\n')
        
        for day in self.days:
            total_encounters = Encounter.objects.syndrome_care_visits().filter(date=day).count()
            events = NonSpecialistVisitEvent.objects.filter(
                event_ptr__name=self.heuristic.long_name, date=day)

            zip_codes = events.values_list('patient_zip_code', flat=True).distinct().order_by(
                'patient_zip_code')
                     
            for zip_code in zip_codes:
                group_counts = [events.filter(age_group_filter(*group)).count()
                                for groups in self.age_groups]
                total_heuristic_visits = sum(group_counts)
                heuristic_pct = 100 * (float(total_heuristic_visits)/total_encounters)
                columns = [day, zip_code] + group_counts + [total_heuristic_visits, total_encounters]
                line = '\t'.join(columns)
                log.info(line)
                outfile.write(line + '\n')

        outfile.close()
                
                
            
                                               
    

    
