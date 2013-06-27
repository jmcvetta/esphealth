#!/usr/bin/python

from optparse import OptionParser
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

#run from command line e.g.: > send_attached_file.py -f <from address> -r <to address> -p <path to file> -n <name of file> -s <subject line for email>
parser = OptionParser()
parser.add_option("-f", "--from", dest="sender", help="Sender email adr")
parser.add_option("-r", "--recipients", dest="receivers", help="comma with space delimited list of recipients")
parser.add_option("-p", "--path", dest="path", help="Path to attachment file")
parser.add_option("-n", "--name", dest="nicename", help="filename to attach")
parser.add_option("-s", "--subject", dest="subject", help="Subject of email")
(options, args) = parser.parse_args()

sender = options.sender
receivers = options.receivers
filename = options.path + '/' + options.nicename
nicename = options.nicename

msgbody = MIMEMultipart('alternative')
msgbody.attach(MIMEText('See attached file.', 'plain'))

msg = MIMEMultipart()
msg['Subject'] = options.subject
msg['From'] = options.sender
msg['To'] = options.receivers
msg.attach(msgbody)

attchmnt = MIMEBase('application', "octet-stream")
attchmnt.set_payload(open(filename, "rb").read())
Encoders.encode_base64(attchmnt)

attchmnt.add_header('Content-Disposition', 'attachment; filename="' + nicename +'"')

msg.attach(attchmnt)

try:
    #Change the smtp server address for your site/
    smtpServ = smtplib.SMTP('172.22.193.11','25')
    smtpServ.sendmail(options.sender, options.receivers, msg.as_string())         
    print "Seems to have been sent"
except Exception:
    print "Something is broken"
