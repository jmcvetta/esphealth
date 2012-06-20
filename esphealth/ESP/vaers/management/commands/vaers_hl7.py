#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from ESP.vaers.models import Questionnaire
from ESP.vaers.hl7_clinbasket import HL7_clinbasket
from ESP.vaers.hl7_report import AdverseReactionReport



class Command(BaseCommand):
    '''
    Finds all vaers questionnaire records that have not had a message sent, build messages and FTPs to defined
    staging area.  Staging area is specified in application.ini, and FTP password is specified in secrets.ini.
    Test FTP access from ESP server to HL7 message staging area before you run this command
    '''
    help = 'Generates HL7 messages for VAERS and FTPs to appropriate sites.'
    
    def handle(self, *args, **options):
        #this queryset is based on a zero-length inbox message, not available in standard Django queryset API 
        ques_qs=Questionnaire.objects.raw('select * from vaers_questionnaire where length(inbox_message)=0 ')
        for ques in ques_qs:
            hl7msg=HL7_clinbasket(ques)
            hl7msg.make_msgs()

        #this queryset could have been created with a series of filter passes using standard queryset API, but it's messy either way.    
        vaers_qs=Questionnaire.objects.raw('select distinct a.* from vaers_questionnaire a, vaers_case_adverse_events b, vaers_adverseevent c ' +
                                          'where a.case_id=b.case_id and b.adverseevent_id=c.id and (a.state=\'Q\' or ' +
                                          '(a.state in (\'AR\',\'UR\',\'RM\') and date(now())-date(a.created_on) > 7 and c.category=\'2_severe\'))')
        for vques in vaers_qs:
            vaersmsg=AdverseReactionReport(vques)
            vaersmsg.render()
    

        
