import os, glob
import datetime
import pdb

from django.db.models import Count

from ESP.emr.models import Encounter
from ESP.ss.models import NonSpecialistVisitEvent, Site, age_group_filter
from ESP.ss.utils import report_folder, age_identifier
from ESP.utils.utils import log, str_from_date, days_in_interval

def make_age_group_column(prefix, age_group):
    lower = age_group[0] if type(age_group[0]) is int else 'under'
    upper = (age_group[1] - 1) if type(age_group[1]) is int else 'plus'
    return '%s %s-%s' % (prefix, lower, upper)


class Hsph(object):

    BASE_FILENAME = 'ESP_Atrius_HSPH_%s_%s.xls'
   
    def __init__(self, begin_date, end_date, heuristic):
        self.begin_date = begin_date
        self.end_date = end_date
        self.days = days_in_interval(self.begin_date, self.end_date)
        self.folder = report_folder(begin_date, end_date, subfolder='hsph', resolution='month')
        self.heuristic = heuristic
        self.age_groups = [(0, 5), (5, 20), (20, 25), (25, 50), (50, 65), (65, None)]

    def report(self):
        log.info('HSPH files for %s on week %s-%s' % (self.heuristic.name, 
                                                      self.begin_date, self.end_date))

        filename = Hsph.BASE_FILENAME % (str_from_date(self.begin_date), str_from_date(self.end_date))
        age_group_syndrome_columns = [make_age_group_column(self.heuristic.name, group) 
                                      for group in self.age_groups] 
        age_group_visit_columns = [make_age_group_column('Visits', group) for group in self.age_groups] 

        header = ['encounter date', 'residential zip'] 
        header += age_group_syndrome_columns + age_group_visit_columns 
        header += ['total visits', '% ILI']

        outfile = open(os.path.join(self.folder, filename), 'w')
        outfile.write('\t'.join(header) + '\n')
        
        for day in self.days:
            events = NonSpecialistVisitEvent.objects.filter(
                event_ptr__name=self.heuristic.long_name, date=day)
            encounters = Encounter.objects.syndrome_care_visits(sites=Site.site_ids()).filter(date=day)

            zip_codes = events.values_list('patient_zip_code', flat=True).distinct().order_by(
                'patient_zip_code')
                     
            for zip_code in zip_codes:
                group_case_counts = [
                    events.filter(patient_zip_code=zip_code).filter(age_group_filter(*group)).count()
                    for group in self.age_groups
                    ]
                
                group_visit_counts = [
                    encounters.filter(patient__zip5=zip_code).filter(age_group_filter(*group)).count()
                    for group in self.age_groups
                    ]
            
                total_cases = sum(group_case_counts)
                total_visits = sum(group_visit_counts)
                
                if not (total_visits and total_cases): continue

                heuristic_pct = 100 * (float(total_cases)/float(total_visits))

                columns = [str_from_date(day), zip_code] + group_case_counts + group_visit_counts
                columns += [total_visits, '%2.3f' % heuristic_pct]

                line = '\t'.join([str(x) for x in columns])
                log.info(line)
                outfile.write(line + '\n')

        outfile.close()
                
                
            
                                               
    

    
