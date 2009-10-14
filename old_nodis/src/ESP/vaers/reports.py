#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from ESP.vaers.models import EncounterEvent, LabResultEvent
from ESP import settings

REPORTS_DESTINATION_DIR = os.path.join(settings.TOPDIR, 'assets', 'reports')

def write_temporal_clustering_reports(folder):
    EncounterEvent.write_fever_clustering_file_report(folder)
    EncounterEvent.write_diagnostics_clustering_file_report(folder)
    LabResultEvent.write_clustering_file_report(folder)




if __name__ == '__main__':
    write_temporal_clustering_reports(REPORTS_DESTINATION_DIR)



