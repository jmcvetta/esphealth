"""
#For NORTH Adams
# mostly generic functions driven by
# Lots'0'configuration data (TM)
# moved to a configuration file
# northadams.py for North Adams hl7
#
#
# parse sudha's messages
# ross lazarus
# march 2008
# for the ESP project
# moving to North Adams
# message type ADT^A04 has obx vital signs, allergies, demog and pcp
# ORU^R01 has lab results and each test may have multiple lines of report that
# need to be stitched together...
# VXU^V04 is immunization with RXA
# PPR^PC1 has PRB
# OMP^O09 has RXO
Plan is to collect these messages as they arrive over a period and
process them all into the Atrius ETL format - so 1 (and only 1!) record for each
PCP and demographic record in each period, with as many Ex, Rx, Lx, Imx, Allergy
file rows as needed.


We need
1) a new encounter record for each unique PVX PID/visit with all the diagnoses for that visit
2) a new Rx record for each unique RXO record in each OMP message
3) a new Lx record for each unique OBX test code in each ORU message
4) a new allergy record for each new ADT message
5) a new immunization record for each RXA in any VXU message

"""
INCOMING_DIR = '/home/ESP/NORTH_ADAMS/incomingHL7/'
DEST_DIR = '/home/ESP/NORTH_ADAMS/archivedHL7/'


import sys
import os
import datetime
import time
import utils
import shutil
import string
import logging
import pprint

from ESP.utils.utils import log
from ESP.utils import northadams

from northadams import * # that's where all our configuration lives


prog = os.path.split(sys.argv[0])[-1]

def timenow():
    """return current time as a string
    """
    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))

def setLogging(appname=''):
    """setup a logger
    """
    logdir = './'
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
    today=datetime.datetime.now().strftime('%Y%m%d')
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=os.path.join(logdir,'%s_%s.log' % (appname,today)),
                filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.error)
    formatter = logging.Formatter('%(levelname)-4s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def etl_Writer(rdict={},lookups=[],outdest=None):
    """write a delimited ESP atrius style etl record to outdest
    lookups is the list of grammar element names for this
    segment in the order they should be written with empty
    strings where no data is provided

    Each lookup list is defined in the configuration file - northadams.py eg
    """
    outrec = []

    for x in lookups:
        if rdict.get(x,None):
            outrec.append(rdict[x])
        else:
            outrec.append('') # should be there but missing
            pid = rdict.get(PATIENT_ID,'UNKNOWN')
           # log.error('Missing element %s for %s %s in %s' % (x,pid,PATIENT_ID,rdict))

    outrec = [x.replace(ETL_DELIMITER,'*') for x in outrec] # purge delims
    if outrec:
        outdest.write('%s\n' % ETL_DELIMITER.join(outrec))


def countSets(messages=[]):
    """initial testing/development code to check header and check number of rows
    print types and counts for checking
    first version just reports something like:
    Analysis of test messages of March 9
    AL1: len = 6
    OBR: len = 25
    OBX: len = 15
    PD1: len = 15
    PID: len = 30
    PRB: len = 16
    PV1: len = 44
    RXA: len = 16
    RXO: len = 13
    """
    res = {} # dict keyed by mtypes for count of segments
    for ml in messages:
        header = parseMSH(ml[0])
        segs = ml[1:]
        for s in segs:
            mtype,nsegs = parseHell7row(s)
            if not res.get(mtype,None):
                res[mtype] = []
            res[mtype].append(nsegs)
    rk = res.keys()
    rk.sort()
    #print '\nAnalysis of test messages of March 9' # Why was this here??
    for r in rk:
        rr = res[r]
        firstlen = rr[0]
        if max(rr) == firstlen and min(rr) == firstlen:
            s = 'len = %d' % firstlen
        else:
            s = 'lens = %s' % (','.join(['%d' % x for x in res[r]]))
        print '%s: %s' % (r,s)
        
        
def apply_grammar(seg_list, grammar):
    '''
    Apply the grammar to segment, returning a dictionary expression
    of said segment.
    @type segment: List
    @type grammar: List
    @return: Dict
    '''
    seg_dict = {}
    for ename,eoffset,esubfield in grammar:
        try:
            if string.find(string.upper(ename), 'DATE')!=-1: ##it is a data field
                if len(seg_list[eoffset][esubfield])==6:
                    e = seg_list[eoffset][esubfield][:6]+'01'
                    log.warning('Modify Date Field %s (%d:%d) in %s' % (ename,eoffset,esubfield,seg_list))
                else:
                    e = seg_list[eoffset][esubfield][:8]
            else:
                e = seg_list[eoffset][esubfield]
        except:
            e = None
            log.warning('## Missing segment %s (%d:%d) in %s' % (ename,eoffset,esubfield,seg_list))
        seg_dict[ename] = e
    return seg_dict


def messageIterator(
    m=[],
    grammar_dict={},
    msg_type_segments=northadams.msg_type_segments,
    incominghl7f=None
    ):
    """Generator function that takes a message split into rows,
    and yields the components of each message as a (target,(id,message)) tuple
    We have to make sure we have MSH and PID segments so message type and patient id
    are known before we can yield anything.
    Once they are found, other permissible segments are yielded that should be
    reported individually - allergies, and lists of OBX lists for each OBR

    There is a lot of curly logic here to deal with the stupidities of the
    HL7 feed. I hate working with HL7 - it's really, really stupid
    Using a generator allows substantial control - we can retain the first
    few segments until we're ready to fire them off fully populated

    Note that we reconstruct the falsely split multiple line reports for a specific
    lab test within each set of obx records.

    All messages start with MSH and have PID and PV1
    We use the Message Type to figure out what the legal
    segments are and what name we're using for the list of values from this
    message. Add patient id, provider npi to all message rdicts

    In the message representation each segment is the dictionary set up by the grammar
    stored in a list keyed by the segment dictionary key from msg_type_segments

    TODO - replace all grammar names with constants
    """
    # Lexicon:
    #    ADT: Administration, Discharge, & Transfer
    #    MSH: Message Header
    #    NPI: National Provider Identifier
    #    OBR: Observation Request
    #    OBX: Observation or Observation Fragment
    #    PD1: Patient Additional Demographic
    log.debug('grammars: %s' % pprint.pformat(grammar_dict))
    allowed_segs = {}
    msh_seg = {} # Message header segment
    pid_seg = {} # Patient ID segment
    npi = None # National Provider Identifier number
    pd1 = None # Patient Additional Demographic
    pid_num  = None # WTF: How is this different from pid?
    admitdatetime = 'UNKNOWN'
    mtype = None
    inobr = False # an OBR may be followed by a sequence of OBX
    current_obr = None # sometimes we need to amalgamate multiple OBX segments
    current_obxattrcode = None # allows amalgamating falsely split single test multiline reports
    obxs = [] # for accumulating all the different test obx for each obr
    totalI9=''
    final_I9dict=None
    for row_num, row_txt in enumerate(m): # i=0 must be msh
        # Convert a segment (row) into a list of fields.  Each field item is 
        # itself expressed as a list, containing one or more subfields.
        seg_list = row_txt.strip().split(FIELD_DELIMITER)
        seg_list = [x.strip().split(SUBFIELD_DELIMITER) for x in seg_list] # each element now a list
        seg_type = seg_list[0][0].upper() # What kind of segment are we working with?
        # ADTOBX has different structure
        if seg_type == 'OBX' and mtype == 'ADT':
            seg_type = 'ADTOBX' 
        grammar = grammar_dict.get(seg_type,None)
        if not grammar:
            log.critical('Cannot find a grammar for segment type %s' % seg_type)
            continue
        segment = apply_grammar(seg_list, grammar) # Dictionary expression of this segment
        log.debug('segment: %s' % pprint.pformat(segment))
        if seg_type == 'MSH': # set aside - we don't have id yet
            msh_seg = segment
            mtype = segment[MESSAGE_TYPE]
            allowed_segs = msg_type_segments.get(mtype,{}) # allowable segments for this messagetype
        elif seg_type == 'PID': # must be able to identify PID
            pid_num = segment.get(PATIENT_ID,None)
            log.debug('pid_num: %s' % pid_num)
            if pid_num == None:
                log.critical('%s not found in PID segment of message %s' % (PATIENT_ID,row_txt))
                # raise StopIteration
                continue # WTF: Is this appropriate?
            pid_seg = segment # for yielding after pv1
            msh_seg[PATIENT_ID] = pid_num
            # pid[PATIENT_ID] = id # This is redundant
        elif seg_type == 'PD1':
            pd1 = segment # probably would need a list of these if they arrive -- JRM: why a list?
        elif seg_type == 'PV1': # need the provider for rx messages eg
            if pid_num == None: ###No patient ID
                msg = 'No Patient ID info in file: "%s": %s' % (incominghl7f, row_txt)
                print msg
                log.critical(msg)
#                    utils.sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg=msg,subject='ESP Northadams incoming HL7 parsing Error')
                raise StopIteration
            admdatetime = segment.get(ADM_DATE_TIME,None) # only place it's given
            if not admdatetime: # needed for rx record eg
                log.critical('PV1 without an %s Cannot cope - %s' % (ADM_DATE_TIME,row))
                admdatetime = ''
            npi = segment.get('Attending_Provider_NPI',None)
            if not npi:
                # WTF: If we cannot cope, why do we continue iteration?
                log.critical('PV1 without an NPI! Cannot cope -- File: "%s"; Row: %s' % (incominghl7f, row_txt))
                npi = 'UNKNOWN'
            segment[PCP_NPI] = npi # add some useful elements to all records
            msh_seg[PCP_NPI] = npi
            pid_seg[PCP_NPI] = npi
            pid_seg[ADM_DATE_TIME] = admdatetime
            pid_seg['Visit_Number'] = segment.get('Visit_Number', None)

            yield ('msh',(pid_num,msh_seg)) # Now that we have the id, npi
            yield ('pid',(pid_num,pid_seg)) # and the pid, add them to the pile
            yield ('pcp',(pid_num,segment)) # pcp
            # yield ('enc',(pid_num,pid_seg)) # FIXME: THis was formerly commented out!!
            # don't yield pc1 -
        elif pid_num and msh_seg and npi and allowed_segs.get(seg_type,None): # is expected in this message type
            segment[ADM_DATE_TIME] = admdatetime # for posterity
            segment[PCP_NPI] = npi
            segment[PATIENT_ID] = pid_num
            target = allowed_segs.get(seg_type) # where to push the message
            log.debug('target: %s' % target)
            log.debug('segment: %s' % segment)
            if inobr: # special - must output if not another obx
                if seg_type == 'OBX':
                    obxattrcode = segment.get(LABRES_CODE,None)
                    if not obxattrcode:
                        log.critical('OBX encountered without %s for pid_num: %s: File %s: %s' % 
                            (LABRES_CODE, pid_num, incominghl7f, segment))
                    elif obxattrcode == current_obxattrcode: # falsely split text!
                        # FIXME: this should be handled in a better way
                        try:
                            last = obxs[-1] # get result to be extended
                        except IndexError:
                            log.critical('Invalid record, zero-length OBX: %s' % incominghl7f)
                            continue
                        sofar = '%s; %s' % (last.get(LABRES_VALUE,''),
                                            segment.get(LABRES_VALUE,''))
                        last[LABRES_VALUE] = sofar
                        obxs[-1] = last
                    else:
                        current_obxattrcode = obxattrcode
                        obxs.append(segment)
                else: # time to write - something other than another obx while inobr
                    ot = allowed_segs.get('OBR') # what's the target pid_num for an OBR in this segment?
                    yield(ot,(pid_num,current_obr))
                    if len(obxs) > 0:
                        ot = allowed_segs.get('OBX')
                        for obx in obxs:
                            yield (ot,(pid_num,obx)) # special treatment for obxs
                    inobr = False
                    current_obr = None
                    obxs = []
                    thisattrcode = None
            if seg_type == 'OBR': # new obr or first
                inobr = True
                current_obr = segment # save for next time to output obr/obxs
            elif seg_type <> 'OBX': # some other legal segment - we took care if we were inobr
                if seg_type=='DG1':
                    if segment['Coding_System']=='I9': ##ICD9
                        totalI9 = segment['Diagnosis_Code']+','+totalI9
                        segment['Visit_Number']=pid_seg['Visit_Number']
                        final_I9dict = segment
                        #yield ('enc',(pid_num,segment))
                else:  ##other than 'DG1' type
                    yield (target,(pid_num,segment))
        else: # invalid segment or no PID/MSH found yet
            if not pid_num or not msh_seg or not npi:
                log.critical('Message segment found before MSH, PV1 and PID in: %s: %s: %s' 
                    % (seg_type, incominghl7f, m))
            else:
                if inobr:
                    ot = allowed_segs.get('OBR')
                    yield(ot,(pid_num,current_obr))
                    if len(obxs) > 0:
                        ot = allowed_segs.get('OBX')
                        for obx in obxs:
                            yield (ot,(pid_num,obx)) # special treatment for obxs
                    inobr = False
                    current_obr = None
                    obxs = []
                    thisattrcode = None
                s = 'Unexpected segment; Mtype: %s; Seg_Type: %s; File: %s' % (mtype, seg_type, incominghl7f)
                log.critical(s)
    if final_I9dict:
        final_I9dict['Diagnosis_Code']=totalI9
        yield ('enc',(pid_num,final_I9dict))
    if inobr: # we appear to have fallen off the end of the message so send now
        ot = allowed_segs.get('OBR')
        yield(ot,(pid_num,current_obr))
        if len(obxs) > 0:
            ot = allowed_segs.get('OBX')
            for obx in obxs:
                yield (ot,(pid_num,obx)) # special treatment for obxs
        inobr = False
        current_obr = None
        obxs = []
        thisattrcode = None
    raise StopIteration


def writeMDicts(mclasses={}):
    """We now have a dict of message classes, each pointing to
    an id and a list of instances.
    We need to write an
    encounter record for each separate visit
    rx for each prescription
    lx for each lab result
    lo for each lab order (?)
    imx for each immunization
    allergy for each allergy
    problem for each problem
    and one provider and one demog record for each subject found
    in the entire batch read.

    We use a very generic writer function that can take the generic
    rdicts and write out the bits needed to the appropriate file
    - driven by configuration lookups of course :)

    """
    # separated all different classes of messages out
    flist = [file('%s' % x,'a+') for x in outfilenames] # list of files!

    writefiles = dict(zip(etlnames,flist)) # get dest output file from etlname!
    targets = mclasses.keys()
    targets.sort()
    for t in targets:
        if t <> "msh":
            log.debug('\tMessage class: %s' % t)
            lookups = writer_lookups[t] # the output etl row
            writefile = writefiles[t] # and file
            iddict = mclasses[t]
            idk = iddict.keys()
            idk.sort()
            for k in idk:
                log.debug('id: %s' % k)
                mlist = mclasses[t][k]
                for m in mlist:
                    etl_Writer(rdict=m,lookups=lookups,outdest=writefile)

    for x in writefiles.values():
        x.close() # close etl files


###################################
def movefile(f, fromdir, DEST_DIR):
    shutil.move(fromdir+'/%s' % f, DEST_DIR)
    log.info('Moving file %s from %s to %s\n' % (f, fromdir, DEST_DIR))

###################################
def parseMessages(mlist=[],grammar_dict={},incominghl7f=None):
    '''
    Parses HL7 messages.
    Expects a list of individual messages, each of which is a list of 
    segment lines.
    '''
    mclasses = {}
    for i,m in enumerate(mlist): # generator will yield message segments
        messages = messageIterator(m=m,grammar_dict=grammar_dict,incominghl7f=incominghl7f)
        npi = None
        for kind, thing in messages: # each message has (id,rdict) or (id,(obr,[obx,..obx]))
            log.debug('message kind: %s' % kind)
            log.debug('message thing: %s' % pprint.pformat(thing))
            if not mclasses.get(kind,None):
                mclasses[kind] = {}
            id,message = thing # split out
            if kind <> 'msh': # don't want these now
                if kind == 'pid': # only want one of these for each unique patient -> demog
                    if not mclasses[kind].get(id,None): # not there yet
                        mclasses[kind][id] = [message,] # put message into this class
                elif kind == 'pcp': # one per provider
                    npi = message.get(PCP_NPI,None)
                    if not npi:
                        npi = message.get(FACILITY_NAME,None) # hack...
                    if not npi:
                        log.critical('PV1 without an NPI! Cannot cope - %s' % message)
                    else:
                        if not mclasses[kind].get(npi,None): # not there yet
                            mclasses[kind][npi] = [message,] # put message into this class
                else:
                    sofar = mclasses[kind].get(id,[])
                    sofar.append(message)
                    mclasses[kind][id] = sofar # replace with update
    return mclasses

def main():
    #setLogging(appname=prog)
    log.info('HL7 message processing started at %s' % timenow())
    hlfiles=os.listdir(INCOMING_DIR)
    for f in hlfiles:
        print 'Processing: %s' % f
        mlist = split_hl7_message(INCOMING_DIR+f)
        grammar_dict = makeGrammars()
        mclasses = parseMessages(mlist=mlist,grammar_dict=grammar_dict,incominghl7f = f)
        writeMDicts(mclasses=mclasses)
        movefile(f, INCOMING_DIR, DEST_DIR)

    for x in dict(map(lambda x:(x,None), outfilenames)).keys():
        xh  =file(x,'a+')
        xh.write('CONTROL TOTALS^NorthAdams^^^^\n')
        xh.close() # close etl files
                                               


    log.info('##########Processing completed at %s' % timenow())


if __name__ == "__main__":
    main()


