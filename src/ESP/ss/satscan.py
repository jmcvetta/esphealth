import os, glob
import datetime
import re
import zipfile

from django.db.models import Count
from django.template import Context
from django.template.loader import get_template
from django.core.mail import mail_admins, send_mail

from ESP.settings import SERVER_EMAIL, SS_EMAIL_RECIPIENT, DEBUG
from ESP.ss.models import NonSpecialistVisitEvent, Site, age_group_filter
from ESP.ss.utils import report_folder, age_identifier
from ESP.utils.utils import log, str_from_date, days_in_interval

class Satscan(object):
    EXECUTABLE_PATH = '/usr/local/bin/satscan'
    VERSION = '8.3-beta5'

    PARAM_FILE_TEMPLATE = 'ss/files/satscan.conf'

    SITE_BASE_FILENAME = 'ESPAtrius_SyndAgg_zip5_Site_Excl_%s_%s_%s'
    RESIDENTIAL_BASE_FILENAME = 'ESPAtrius_SyndAgg_zip5_Res_%s_%s_%s'

    TIME_WINDOW = 180    
    RELEVANT_INTERVAL = 365
    

    def __init__(self, day, heuristic):
        
        self.start_date = day - datetime.timedelta(Satscan.TIME_WINDOW)
        self.end_date = day
        self.folder = report_folder(day, day, subfolder='satscan')        
        self.heuristic = heuristic
        self.age_groups = [(0, 5), (5, 25), (25, None)]


        
    def _filenames(self, base, age_group):

        # Construct file names.
        filename_params = (self.heuristic.name, 
                           str_from_date(self.start_date), 
                           str_from_date(self.end_date))

        base += age_identifier(age_group)
        
        make_filename = lambda ext: '.'.join([base % filename_params, ext])
        
        return {
            'case': make_filename('cas'),
            'parameter': make_filename('prm'),
            'results': make_filename('txt')
            }


    def make_parameter_files(self):
        groups = self.age_groups + [None]

        for group in groups:
            site_files = self._filenames(Satscan.SITE_BASE_FILENAME, group)
            residential_files = self._filenames(Satscan.RESIDENTIAL_BASE_FILENAME, group)


#            site_file = open(os.path.join(self.folder, site_files['parameter']), 'w')   
#            site_file.write(get_template(Satscan.PARAM_FILE_TEMPLATE).render(Context({
#                            'case_file': site_files['case'],
#                            'result_file': site_files['results'],
#                            'start_date': self.start_date,
#                            'end_date': self.end_date
#                            })))

            residential_file = open(os.path.join(self.folder, residential_files['parameter']), 'w')   
            residential_file.write(get_template(Satscan.PARAM_FILE_TEMPLATE).render(Context({
                            'case_file': residential_files['case'],
                            'result_file': residential_files['results'],
                            'start_date': self.start_date,
                            'end_date': self.end_date
                            })))


            residential_file.close()
#            site_file.close()
                      


    def _make_site_casefile(self, queryset, filename):
        log.info('Writing ' + filename)
        outfile = open(os.path.join(self.folder, filename), 'w')
        counts = queryset.values('reporting_site__zip_code', 'date').annotate(
            count=Count('event_ptr')).order_by('reporting_site__zip_code', 'date')
                
        for count in counts:
            outfile.write('\t'.join([count['reporting_site__zip_code'], str(count['count']), 
                                     str(count['date']), str(count['date'].isoweekday())
                                     ]))                        
            outfile.write('\n')
        
        outfile.close()

    def _make_residential_casefile(self, queryset, filename):
        log.info('Writing ' + filename)
        outfile = open(os.path.join(self.folder, filename), 'w')
        counts = queryset.values('patient_zip_code', 'date').annotate(
            count=Count('event_ptr')).order_by('patient_zip_code', 'date')
        
        

        for count in counts:
            outfile.write('\t'.join([count['patient_zip_code'], str(count['count']), 
                                     str(count['date']), str(count['date'].isoweekday())
                                     ]))
            outfile.write('\n')

        outfile.close()

        

    def make_case_files(self):
        log.info('Satscan case files for %s on %s-%s' % (self.heuristic.name, 
                                                         self.start_date, self.end_date))
        
        events = NonSpecialistVisitEvent.objects.filter(
            event_ptr__name=self.heuristic.long_name, date__gte=self.start_date, 
            date__lte=self.end_date)

        groups = self.age_groups + [None]
        
        for group in groups:
            
            group_events = events.filter(age_group_filter(*group)) if group else events


#            site_filename = self._filenames(Satscan.SITE_BASE_FILENAME, group)['case']
            residential_filename = self._filenames(Satscan.RESIDENTIAL_BASE_FILENAME, group)['case']
            
#            site_events = group_events.exclude(reporting_site__isnull=True)
            residential_events = group_events.exclude(patient_zip_code__isnull=True).order_by('patient_zip_code', 'date')
            

#            self._make_site_casefile(site_events, site_filename)
            self._make_residential_casefile(residential_events, residential_filename)
            
            
    def run_satscan(self):
        os.chdir(self.folder)
        run_with_file = lambda f: os.system('%s %s' % (Satscan.EXECUTABLE_PATH, f))

        groups = self.age_groups + [None]

        for group in groups:
#            run_with_file(self._filenames(Satscan.SITE_BASE_FILENAME, group)['parameter'])
            run_with_file(self._filenames(Satscan.RESIDENTIAL_BASE_FILENAME, group)['parameter'])
        
        
    def _recurrence_intervals(self, filename):
        os.chdir(self.folder)
        contents = open(filename, 'r').read()
        regexp = re.compile('Recurrence interval...: \w+ day')
        return [float(match.split()[2].strip()) for match in regexp.findall(contents)]


    def _package_reports(self, results_filename, package_basename, age_group):
        os.chdir(self.folder)
        max_interval = max(self._recurrence_intervals(results_filename))
        package_filename = package_basename % (str_from_date(self.end_date), age_identifier(age_group),
                                               Satscan.VERSION, max_interval)
        # Case, parameter, and satscan-generated file names should be
        # all the same Differing only by the extension(s). So we check
        # the name of the file and grab everything to add to the zip
        # file.
        common_filename = results_filename.split('.')[0]
        package = zipfile.ZipFile(package_filename, 'w')

        # excluding case files from the list.
        files = [f for f in glob.glob('%s*' % common_filename) if not f.endswith('cas')]
        for f in files:
            package.write(f, os.path.basename(f), zipfile.ZIP_DEFLATED)
            
        package.close()

        try:
            if max_interval >= Satscan.RELEVANT_INTERVAL:
                subject = ' Satscan identified relevant interval cluster'
                msg = 'Please refer to file %s' % package_filename
                fail_silently = not DEBUG
                mail_admins(subject, msg, fail_silently=fail_silently)

                assert SS_EMAIL_RECIPIENT is not None
                recipients = SS_EMAIL_RECIPIENT.split(',')
                send_mail(subject, msg, SERVER_EMAIL, recipients, fail_silently=fail_silently)

        except AssertionError:
            msg = 'ESP:SS email recipient is not defined'
            log.warn(msg)
            mail_admins('Could not send notification email related to ESP:SS', msg, fail_silently=False)

    def package(self):
        groups = self.age_groups + [None]
#        site_package_basename = 'Site-%s%s-satscan%s-interval%.0f.zip'
        residential_package_basename = 'Residential-%s%s-satscan%s-interval%.0f.zip'
        
                
        for group in groups:
            self._package_reports(self._filenames(Satscan.RESIDENTIAL_BASE_FILENAME, group)['results'], 
                                  residential_package_basename, group)
#            self._package_reports(self._filenames(Satscan.SITE_BASE_FILENAME, group)['results'], 
#                                  site_package_basename, group)
            
                                  
            
                                               
    

    
