#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from ESP.vaers.models import Questionaire
from ESP.vaers.hl7_clinbasket import HL7_clinbasket



class Command(BaseCommand):
    '''
    Finds all vaers questionaire records that have not had a message sent, build messages and FTPs to defined
    staging area.  Staging area is specified in application.ini, and FTP password is specified in secrets.ini.
    Test FTP access from ESP server to HL7 message staging area before you run this command
    '''
    help = 'Generates HL7 messages for VAERS and FTPs to appropriate sites.  No options.'
    
    def handle(self, *args, **options):
        ques_qs=Questionaire.objects.raw('select * from vaers_questionaire where length(inbox_message)=0')
        for ques in ques_qs:
            hl7msg=HL7_clinbasket(ques)
            hl7msg.make_msgs()

        
