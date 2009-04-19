# snarfed from http://www.humehealth.com.au/humeNET/browse.asp?page=421
# mods to read and parse out messages from our MDPH v3 HL7 batch
# turned main function of xml2bar.py into a class
# and added code to split an ESP hl7 v3 output message into
# a series of valid hl7 v3 messages (they're in cdata!)
# and feed those to the parser class
# to output individual messages for subsequent sending to
# ohio
# by rml on april 18 2009
# potentially for Ohio - requires hl7 2.3.1 ELR messages
# that might work with our mdph HL7 v3 messages?
# 
# Original xml2bar.py copyright follows 
# Copyright (c) 2000, C_Cost Systems Pty. Ltd. A.C.N. 055609099
# Copyright (c) 2004, HumeNET Ltd. A.C.N. 106 862 131
# All rights reserved.

# The authors and contributors hereby grant permission, free of charge,
# to any person obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation, the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software,
# both in source and binary forms, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:

# 1. Redistributions of source code must retain the above copyright
#    notices, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notices, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# This Software is distributed in the hope that it will be useful.
# The Software is provided by the authors, contributors and copyright holders
# ``AS IS'' WITHOUT WARRANTY OF ANY KIND. Any EXPRESS OR IMPLIED WARRANTIES,
# including, but not limited to, the IMPLIED WARRANTIES OF MERCHANTABILITY
# and FITNESS FOR A PARTICULAR PURPOSE and NONINFRINGEMENT are disclaimed.
# In no event shall the authors, contributors or copyright holders be liable
# for any DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, or CONSEQUENTIAL
# DAMAGES (including, but not limited to, PROCUREMENT OF SUBSTITUTE GOODS or
# SERVICES; LOSS OF USE, DATA, or PROFITS; or BUSINESS INTERRUPTION)
# however caused and on any theory of liability, whether in CONTRACT,
# STRICT LIABILITY, or TORT (including NEGLIGENCE OR OTHERWISE) arising
# in any way out of the use of, or dealing in, this Software,
# even if advised of the possibility of such damage.

# This program reads an XML notation HL7 message
# on it's standard input and output the equivalent
# vertical bar notation message.
# This version is really dumb.
# It makes not attempt to do any sort of validation.
# It assumes that the rules for encoding vertical bar notation
# to XML have been followed.

import os, sys, re, copy
import xml.parsers.expat

showdebug = 0
startBatch='<![CDATA[' # current ESP MDPH constants
endBatch=']]>'
startMess='<ORU_R01>'
endMess='</ORU_R01>'
# this is a test message carved out from some faked data
# and saved here for testing/development
testXML="""<ORU_R01><MSH><MSH.1>|</MSH.1><MSH.2>^~\\&amp;</MSH.2><MSH.4><HD.1>Prototype</HD.1><HD.2>22D0666230</HD.2><HD.3>CLIA</HD.3></MSH.4><MSH.5><HD.1>MDPH-ELR</HD.1></MSH.5><MSH.6><HD.1>MDPH</HD.1></MSH.6><MSH.7><TS.1>20090112155447</TS.1></MSH.7><MSH.9><MSG.1>ORU</MSG.1><MSG.2>R01</MSG.2></MSH.9><MSH.10>MDPH20090112155447</MSH.10><MSH.11><PT.1>T</PT.1></MSH.11><MSH.12><VID.1>2.3.1</VID.1></MSH.12></MSH><ORU_R01.PIDPD1NK1NTEPV1PV2ORCOBRNTEOBXNTECTI_SUPPGRP><ORU_R01.PIDPD1NK1NTEPV1PV2_SUPPGRP><PID><PID.1>1</PID.1><PID.3><CX.1>HVMA-FAKED027918351</CX.1><CX.5>MR</CX.5><CX.6><HD.2>Brookline 
Ave</HD.2></CX.6></PID.3><PID.3><CX.1>7514</CX.1><CX.5>SS</CX.5></PID.3><PID.5><XPN.1><FN.1>Barfoosotbar</FN.1></XPN.1><XPN.2>Mary</XPN.2></PID.5><PID.7><TS.1>19640908</TS.1></PID.7><PID.8>M</PID.8><PID.10><CE.4>P</CE.4></PID.10><PID.11><XAD.1>Patient 
Address 1</XAD.1><XAD.3>PEABODY</XAD.3><XAD.4>MA</XAD.4><XAD.5>01960</XAD.5><XAD.6>USA</XAD.6><XAD.7>H</XAD.7></PID.11><PID.13><XTN.6>617</XTN.6><XTN.7>1556555</XTN.7></PID.13></PID><NK1><NK1.1>1</NK1.1><NK1.2><XPN.1><FN.1>Nick</FN.1></XPN.1><XPN.2>Kylie</XPN.2></NK1.2><NK1.3><CE.4>PCP</CE.4></NK1.3><NK1.4><XAD.1>Address 
1</XAD.1><XAD.3>DEDHAM</XAD.3><XAD.4>MA</XAD.4><XAD.5>02026</XAD.5><XAD.6>USA</XAD.6><XAD.7>O</XAD.7></NK1.4><NK1.5><XTN.6>617</XTN.6><XTN.7>1234567</XTN.7></NK1.5></NK1><NK1><NK1.1>2</NK1.1><NK1.2><XPN.1><FN.1>Klompas</FN.1></XPN.1><XPN.2>Michael</XPN.2></NK1.2><NK1.3><CE.4>FCP</CE.4></NK1.3><NK1.4><XAD.1>133 
Brookline Avenue</XAD.1><XAD.3>Boston</XAD.3><XAD.4>MA</XAD.4><XAD.5>02215</XAD.5><XAD.6>USA</XAD.6><XAD.7>O</XAD.7></NK1.4><NK1.5><XTN.4>MKLOMPAS@PARTNERS.ORG</XTN.4><XTN.6>617</XTN.6><XTN.7>5099991</XTN.7></NK1.5></NK1></ORU_R01.PIDPD1NK1NTEPV1PV2_SUPPGRP><ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP><OBR><OBR.1>1</OBR.1><OBR.4><CE.2>Additional 
Patient Demographics</CE.2></OBR.4><OBR.31><CE.1>099.41</CE.1><CE.2>Chlamydia</CE.2><CE.3>I9</CE.3></OBR.31></OBR><ORU_R01.OBXNTE_SUPPGRP><OBX><OBX.1>1</OBX.1><OBX.2>NM</OBX.2><OBX.3><CE.4>21612-7</CE.4></OBX.3><OBX.5>44</OBX.5></OBX><NTE><NTE.3>Create 
New Case</NTE.3></NTE></ORU_R01.OBXNTE_SUPPGRP><ORU_R01.OBXNTE_SUPPGRP><OBX><OBX.1>2</OBX.1><OBX.2>CE</OBX.2><OBX.3><CE.4>11449-6</CE.4><CE.5>PREGNANCY 
STATUS</CE.5></OBX.3><OBX.5><CE.4>261665006</CE.4></OBX.5></OBX></ORU_R01.OBXNTE_SUPPGRP><ORU_R01.OBXNTE_SUPPGRP><OBX><OBX.1>3</OBX.1><OBX.2>CE</OBX.2><OBX.3><CE.4>NA-TRMT</CE.4></OBX.3><OBX.5><CE.4>373067005</CE.4></OBX.5></OBX></ORU_R01.OBXNTE_SUPPGRP><ORU_R01.OBXNTE_SUPPGRP><OBX><OBX.1>4</OBX.1><OBX.2>CE</OBX.2><OBX.3><CE.4>NA-5</CE.4></OBX.3><OBX.5><CE.4>373067005</CE.4></OBX.5></OBX></ORU_R01.OBXNTE_SUPPGRP></ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP><ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP><ORC><ORC.12><XCN.2><FN.1>Nick</FN.1></XCN.2><XCN.3>Barry 
Donna</XCN.3></ORC.12><ORC.14><XTN.6>617</XTN.6><XTN.7>1234567</XTN.7></ORC.14><ORC.21><XON.1>Prototype</XON.1></ORC.21><ORC.22><XAD.1>133 Brookline 
Avenue</XAD.1><XAD.3>Boston</XAD.3><XAD.4>MA</XAD.4><XAD.5>02215</XAD.5><XAD.6>USA</XAD.6></ORC.22><ORC.23><XTN.6>617</XTN.6><XTN.7>5099991</XTN.7></ORC.23><ORC.24><XAD.1>133 
Brookline Avenue</XAD.1><XAD.3>Boston</XAD.3><XAD.4>MA</XAD.4><XAD.5>02215</XAD.5><XAD.6>USA</XAD.6></ORC.24></ORC><OBR><OBR.1>1</OBR.1><OBR.3><EI.1>6690</EI.1></OBR.3><OBR.4><CE.4>16601-7</CE.4><CE.6>L</CE.6></OBR.4><OBR.7><TS.1>20061026</TS.1></OBR.7><OBR.15><SPS.1><CE.4>261665006</CE.4><CE.6>L</CE.6></SPS.1></OBR.15><OBR.25>P</OBR.25></OBR><ORU_R01.OBXNTE_SUPPGRP><OBX><OBX.1>1</OBX.1><OBX.2>CE</OBX.2><OBX.3><CE.4>16601-7</CE.4><CE.6>L</CE.6></OBX.3><OBX.5><CE.4>10828004</CE.4></OBX.5><OBX.7>Low: - High:</OBX.7><OBX.14><TS.1>20061026</TS.1>
</OBX.14><OBX.15><CE.1>22D0076229</CE.1><CE.3>CLIA</CE.3></OBX.15></OBX></ORU_R01.OBXNTE_SUPPGRP></ORU_R01.ORCOBRNTEOBXNTECTI_SUPPGRP></ORU_R01.PIDPD1NK1NTEPV1PV2ORCOBRNTEOBXNTECTI_SUPPGRP></ORU_R01>
"""
class v3Tov2:
    """class to wrap the functionality of xml2bar.py for multiple message munging
    Instantiate with a list of individual xml hl7 v3 message strings as v3XML and
    an output file prototype, and it will spit out the hl7 v2 version more or less
    as a series of indexed message files based on the prototype filename
    """
    def __init__(self,v3XML=[],outNameProto='test1'):
        """converted into a self processing class
        """                
        self.outfskel = '%s_v2_%%d.hl7' % outNameProto # use to create output name
        # Set up the state information
        self.tagMatch = re.compile('^...$')
        for i,xml in enumerate(v3XML): # expect a list of v3 messages like the test sample above
            tx = [x.strip() for x in xml.split('\n')] # remove all cr/line feeds
            s = ' '.join(tx) # one long string
            self.reset()
            self.parseOne(s)
            self.writeRes(i+1) # uses i as the index
 
    def reset(self):
        """restart the parser vars
        """
        self.level = 0
        self.fieldSep = ''
        self.compSep = ''
        self.repSep = ''
        self.escChar = ''
        self.subCompSep = ''
        self.Seg = ''
        self.lastField = ''
        self.lastFieldNo = 0
        self.lastCompNo = 0
        self.lastSubCompNo = 0
        self.thisFieldNo = 0
        self.thisCompNo = 0
        self.thisSubCompNo = 0
        self.res = []

    # Called when a start tag is found
    def startElement(self,tag, attrs) :
        
        if tag == 'escape' :
            self.Seg += self.escChar + attrs['V'] + self.escChar
            return

        if self.level == 0 :
            # Look for a segment tag
            # (only segment tags consist of 3 characters)
            m = self.tagMatch.match(tag)
            if m :
                if self.Seg != '' :
                    self.Seg = self.Seg.replace('&#92;', '\\')
                    self.Seg = self.Seg.replace('&gt;', ">")
                    self.Seg = self.Seg.replace('&lt;', "<")
                    self.Seg = self.Seg.replace('&#34;', '"')
                    self.Seg = self.Seg.replace('&amp;', '&')
                    self.res.append(copy.copy(self.Seg))
                self.Seg = tag
                self.level = 1
                self.lastField = ''
                self.lastFieldNo = 0
                if tag == 'MSH' :
                    self.lastFieldNo = 2
        elif self.level == 1 :
            if self.lastField == tag :
                self.Seg += self.repSep
            else :
                dot = tag.rfind('.')
                self.thisFieldNo = int(tag[dot + 1:])
                while self.thisFieldNo > self.lastFieldNo :
                    self.Seg += self.fieldSep
                    self.lastFieldNo += 1
            self.level = 2
            self.lastField = tag
            self.lastCompNo = 1
        elif self.level == 2 :
            dot = tag.rfind('.')
            self.thisCompNo = int(tag[dot + 1:])
            while self.thisCompNo > self.lastCompNo :
                self.Seg += self.compSep
                self.lastCompNo += 1
            self.level = 3
            self.lastSubCompNo = 1
        elif self.level == 3 :
            dot = tag.rfind('.')
            self.thisSubCompNo = int(tag[dot + 1:])
            while self.thisSubCompNo > self.lastSubCompNo :
                self.Seg += self.subCompSep
                self.lastSubCompNo += 1
            self.level = 4


    # Called when an end tag is found
    def endElement(self,tag) :
        if tag == 'escape' :
            return

        if self.level > 0 :
            self.level -= 1


    # Called when a data portion is found
    def characterData(self,data) :
        # UTF-8 data is always passed one character at a time
        if ord(data[0:1]) >= 0x80 :
            self.Seg += self.escChar
            self.Seg += 'X%x' % (ord(data[0:1]))
            self.Seg += self.escChar
            return

        if self.subCompSep != '' :
            # Do all the escape substitutions
            data = data.replace(self.escChar, self.escChar + 'E' + self.escChar)
            data = data.replace(self.fieldSep, self.escChar + 'F' + self.escChar)
            data = data.replace(self.compSep, self.escChar + 'S' + self.escChar)
            data = data.replace(self.subCompSep, self.escChar + 'T' + self.escChar)
            data = data.replace(self.repSep, self.escChar + 'R' + self.escChar)
        self.Seg += data
        length = len(data)
        while (length > 0) and (self.subCompSep == '') :
            if self.fieldSep == '' :
                self.fieldSep = data[0:1]
            elif self.compSep == '' :
                self.compSep = data[0:1]
            elif self.repSep == '' :
                self.repSep = data[0:1]
            elif self.escChar == '' :
                self.escChar = data[0:1]
            elif self.subCompSep == '' :
                self.subCompSep = data[0:1]
            data = data[1:length]
            length -= 1


    def parseOne(self,XML=''):
        """broken out so can parse one of the mdph hl7 v3 monsters and feed
        individual messages here
        """
        # Read in the XML and strip off any start of line formatting

        # Create the XML parser
        xml_parser = xml.parsers.expat.ParserCreate()

        # Associate the handlers with the parser
        xml_parser.StartElementHandler = self.startElement
        xml_parser.EndElementHandler = self.endElement
        xml_parser.CharacterDataHandler = self.characterData

        # Parse and handle the data
        xml_parser.Parse(XML)

        if self.Seg != '' :
            self.Seg = self.Seg.replace('&#92;', '\\')
            self.Seg = self.Seg.replace('&gt;', ">")
            self.Seg = self.Seg.replace('&lt;', "<")
            self.Seg = self.Seg.replace('&#34;', '"')
            self.Seg = self.Seg.replace('&amp;', '&')
            self.res.append(copy.copy(self.Seg))

    def writeRes(self,messIndex=1):
        """
        """
        fname = self.outfskel % messIndex
        f = file(fname,'w')
        f.write('\r'.join(self.res))
        f.write('\r')
        f.close()
        if showdebug:
            print 'wrote', fname,'\n','\n'.join(self.res),'\n'

def test():
    p = v3Tov2(v3XML=[testXML,],outNameProto='test1')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        infName=sys.argv[1]
        try:
            s = open(infName,'r').read()
        except:
            print 'Cannot open %s - permissions? exists?' % infName
            sys.exit(1)
        fName = os.path.splitext(infName)[0]
        s = s.split('\n') # new line list
        s = ''.join([x.strip() for x in s]) # stripped of cr/lf
        s = s.split(startBatch)[1] # each ESP v3 file has only one cdata seg
        s = s.split(endBatch)[0] # and strip off last endBatch
        xlist = s.split(startMess) 
        xlist = ['%s%s' % (startMess,x) for x in xlist if len(x) > 10]
        p = v3Tov2(v3XML=xlist,outNameProto=fName)
    else:
        print 'testing - provide an ESP batch hl7 v3 file path as a parameter to avoid this' 
        test()
    
