# snarfed from http://www.humehealth.com.au/humeNET/browse.asp?page=421
# by rml on april 18 2009
# potentially for Ohio - requires hl7 2.3.1 ELR messages
# that might work with our mdph HL7 v3 messages?
# 
#
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

import os, sys, re
import xml.parsers.expat

# Set up the state information
level = 0
fieldSep = ''
compSep = ''
repSep = ''
escChar = ''
subCompSep = ''
Seg = ''
lastField = ''
lastFieldNo = 0
lastCompNo = 0
lastSubCompNo = 0
tagMatch = re.compile('^...$')

# Called when a start tag is found
def startElement(tag, attrs) :
	global level, Seg, lastField, lastFieldNo
	global repSep, thisFieldNo, fieldSep, lastCompNo
	global thisCompNo, compSep, lastSubCompNo
	global thisSubCompNo, subCompSep
	global tagMatch

	if tag == 'escape' :
		Seg += escChar + attrs['V'] + escChar
		return

	if level == 0 :
		# Look for a segment tag
		# (only segment tags consist of 3 characters)
		m = tagMatch.match(tag)
		if m :
			if Seg != '' :
				Seg = Seg.replace('&#92;', '\\')
				Seg = Seg.replace('&gt;', ">")
				Seg = Seg.replace('&lt;', "<")
				Seg = Seg.replace('&#34;', '"')
				Seg = Seg.replace('&amp;', '&')
				print '%s\r' % (Seg),
			Seg = tag
			level = 1
			lastField = ''
			lastFieldNo = 0
			if tag == 'MSH' :
				lastFieldNo = 2
	elif level == 1 :
		if lastField == tag :
			Seg += repSep
		else :
			dot = tag.rfind('.')
			thisFieldNo = int(tag[dot + 1:])
			while thisFieldNo > lastFieldNo :
				Seg += fieldSep
				lastFieldNo += 1
		level = 2
		lastField = tag
		lastCompNo = 1
	elif level == 2 :
		dot = tag.rfind('.')
		thisCompNo = int(tag[dot + 1:])
		while thisCompNo > lastCompNo :
			Seg += compSep
			lastCompNo += 1
		level = 3
		lastSubCompNo = 1
	elif level == 3 :
		dot = tag.rfind('.')
		thisSubCompNo = int(tag[dot + 1:])
		while thisSubCompNo > lastSubCompNo :
			Seg += subCompSep
			lastSubCompNo += 1
		level = 4


# Called when an end tag is found
def endElement(tag) :
	global level

	if tag == 'escape' :
		return

	if level > 0 :
		level -= 1


# Called when a data portion is found
def characterData(data) :
	global Seg, fieldSep, compSep, repSep, escChar, subCompSep
	global inUTF, UTFval

	# UTF-8 data is always passed one character at a time
	if ord(data[0:1]) >= 0x80 :
		Seg += escChar
		Seg += 'X%x' % (ord(data[0:1]))
		Seg += escChar
		return

	if subCompSep != '' :
		# Do all the escape substitutions
		data = data.replace(escChar, escChar + 'E' + escChar)
		data = data.replace(fieldSep, escChar + 'F' + escChar)
		data = data.replace(compSep, escChar + 'S' + escChar)
		data = data.replace(subCompSep, escChar + 'T' + escChar)
		data = data.replace(repSep, escChar + 'R' + escChar)
	Seg += data
	length = len(data)
	while (length > 0) and (subCompSep == '') :
		if fieldSep == '' :
			fieldSep = data[0:1]
		elif compSep == '' :
			compSep = data[0:1]
		elif repSep == '' :
			repSep = data[0:1]
		elif escChar == '' :
			escChar = data[0:1]
		elif subCompSep == '' :
			subCompSep = data[0:1]
		data = data[1:length]
		length -= 1



# Read in the XML and strip off any start of line formatting
XML = ''
while 1 :
	line = sys.stdin.readline()
	if line == '' :
		break
	line = line.strip()
	XML += line


# Create the XML parser
xml_parser = xml.parsers.expat.ParserCreate()

# Associate the handlers with the parser
xml_parser.StartElementHandler = startElement
xml_parser.EndElementHandler = endElement
xml_parser.CharacterDataHandler = characterData

# Parse and handle the data
xml_parser.Parse(XML)

if Seg != '' :
	Seg = Seg.replace('&#92;', '\\')
	Seg = Seg.replace('&gt;', ">")
	Seg = Seg.replace('&lt;', "<")
	Seg = Seg.replace('&#34;', '"')
	Seg = Seg.replace('&amp;', '&')
	print '%s\r' % (Seg),


