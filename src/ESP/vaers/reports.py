#!/usr/bin/python
# -*- coding: utf-8 -*-

from ESP.vaers.models import EncounterEvent, LabResultEvent

def write_temporal_clustering_reports():
    EncounterEvent.write_fever_clustering_file_report()
    EncounterEvent.write_diagnostics_clustering_file_report()
    LabResultEvent.write_clustering_file_report()


if __name__ == '__main__':
    write_temporal_clustering_reports()



