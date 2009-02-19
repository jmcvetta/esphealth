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
import sys, os
sys.path.append('../')

import settings 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import datetime, time, logging
from northadams import * # that's where all our configuration lives
import utils
import shutil
import string

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
           # logging.error('Missing element %s for %s %s in %s' % (x,pid,PATIENT_ID,rdict))

    outrec = [x.replace(etldelim,'*') for x in outrec] # purge delims
    if outrec:
        outdest.write('%s\n' % etldelim.join(outrec))


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
    print '\nAnalysis of test messages of March 9'
    for r in rk:
        rr = res[r]
        firstlen = rr[0]
        if max(rr) == firstlen and min(rr) == firstlen:
            s = 'len = %d' % firstlen
        else:
            s = 'lens = %s' % (','.join(['%d' % x for x in res[r]]))
        print '%s: %s' % (r,s)

def messageIterator(m=[],grammars={},mtypedict=mtypedict,incominghl7f=None):
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
    stored in a list keyed by the segment dictionary key from mtypedict

    TODO - replace all grammar names with constants
    """

    def gApply(lrow=[],grammar=[]):
        """ apply the right grammar to this row
        """
        rowdict = {}
        for ename,eoffset,esubfield in grammar:
            
            try:
                if string.find(string.upper(ename), 'DATE')!=-1: ##it is a data field
                    if len(lrow[eoffset][esubfield])==6:
                        e = lrow[eoffset][esubfield][:6]+'01'
                        logging.warning('Modify Date Field %s (%d:%d) in %s' % (ename,eoffset,esubfield,lrow))
                        
                    else:
                        e = lrow[eoffset][esubfield][:8]
                else:
                    e = lrow[eoffset][esubfield]

            except:
                e = None
                logging.warning('## Missing segment %s (%d:%d) in %s' % (ename,eoffset,esubfield,lrow))
            rowdict[ename] = e
        return rowdict


    segdict = {}
    msh = None
    pid = None

    npi = None
    pd1 = None
    id=None
    admitdatetime = 'UNKNOWN'
    mtype = None
    inobr = False # an OBR may be followed by a sequence of OBX
    current_obr = None # sometimes we need to amalgamate multiple OBX segments
    current_obxattrcode = None # allows amalgamating falsely split single test multiline reports
    obxs = [] # for accumulating all the different test obx for each obr
    totalI9=''
    final_I9dict=None
    for i,row in enumerate(m): # i=0 must be msh
        
        lrow = row.strip().split(sdelim)
        lrow = [x.strip().split(sfdelim) for x in lrow] # each element now a list
        gtype = lrow[0][0].upper()

        if gtype == 'OBX' and mtype == 'ADT':
            gtype = 'ADTOBX' # hack - different structure :(
        g = grammars.get(gtype,None)

        if not g:
            logging.critical('Cannot find a grammar for segment type %s' % gtype)
        else: # parse this segment with the grammar g
            rdict = gApply(lrow,g) # g is the right grammar for gtype
            if gtype == 'MSH': # set aside - we don't have id yet
                msh = rdict
                mtype = rdict[MESSAGE_TYPE]
                segdict = mtypedict.get(mtype,{}) # allowable segments for this messagetype
            elif gtype == 'PID': # must be able to identify PID
                id = rdict.get(PATIENT_ID,None)
                if id == None:
                    logging.critical('%s not found in PID segment of message %s' % (PATIENT_ID,row))
                    # raise StopIteration
                pid = rdict # for yielding after pv1
                msh[PATIENT_ID] = id
                pid[PATIENT_ID] = id
                
            elif gtype == 'PD1':
                pd1 = rdict # probably would need a list of these if they arrive
            elif gtype == 'PV1': # need the provider for rx messages eg
                if id == None: ###No patient ID
                    msg = 'In File %s: No PID info - %s' % (incominghl7f, row)
                    print msg
                    logging.critical(msg)
#                    utils.sendoutemail(towho=['rerla@channing.harvard.edu','rexua@channing.harvard.edu'],msg=msg,subject='ESP Northadams incoming HL7 parsing Error')
                    raise StopIteration
                
                    
                admdatetime = rdict.get(ADM_DATE_TIME,None) # only place it's given
                if not admdatetime: # needed for rx record eg
                    logging.critical('PV1 without an %s Cannot cope - %s' % (ADM_DATE_TIME,row))
                    admdatetime = ''

                npi = rdict.get('Attending_Provider_NPI',None)
                if not npi:
                    logging.critical('PV1 without an NPI! Cannot cope - %s' % row)
                    npi = 'UNKNOWN'
                rdict[PCP_NPI] = npi # add some useful elements to all records
                msh[PCP_NPI] = npi
                pid[PCP_NPI] = npi
                pid[ADM_DATE_TIME] = admdatetime
                pid['Visit_Number'] = rdict.get('Visit_Number', None)

                yield ('msh',(id,msh)) # Now that we have the id, npi
                yield ('pid',(id,pid)) # and the pid, add them to the pile
                yield ('pcp',(id,rdict)) # pcp
                #yield ('enc',(id,pid))

                # don't yield pc1 -
            elif id and msh and npi and segdict.get(gtype,None): # is expected in this message type
                rdict[ADM_DATE_TIME] = admdatetime # for posterity
                rdict[PCP_NPI] = npi
                rdict[PATIENT_ID] = id
                target = segdict.get(gtype) # where to push the message
                if inobr: # special - must output if not another obx
                    if gtype == 'OBX':
                        obxattrcode = rdict.get(LABRES_CODE,None)
                        if not obxattrcode:
                            logging.critical('OBX %s for id %s encountered without a %s?' \
                                          % (rdict,id,LABRES_CODE))
                        elif obxattrcode == current_obxattrcode: # falsely split text!
                            last = obxs[-1] # get result to be extended
                            sofar = '%s; %s' % (last.get(LABRES_VALUE,''),
                                                rdict.get(LABRES_VALUE,''))
                            last[LABRES_VALUE] = sofar
                            obxs[-1] = last
                        else:
                            current_obxattrcode = obxattrcode
                            obxs.append(rdict)
                    else: # time to write - something other than another obx while inobr
                        ot = segdict.get('OBR') # what's the target id for an OBR in this segment?
                        yield(ot,(id,current_obr))
                        if len(obxs) > 0:
                            ot = segdict.get('OBX')
                            for obx in obxs:
                                yield (ot,(id,obx)) # special treatment for obxs
                        inobr = False
                        current_obr = None
                        obxs = []
                        thisattrcode = None
                if gtype == 'OBR': # new obr or first
                    inobr = True
                    current_obr = rdict # save for next time to output obr/obxs
                elif gtype <> 'OBX': # some other legal segment - we took care if we were inobr
                    if gtype=='DG1':

                        if rdict['Coding_System']=='I9': ##ICD9
                            totalI9 = rdict['Diagnosis_Code']+','+totalI9
                            rdict['Visit_Number']=pid['Visit_Number']
                            final_I9dict = rdict
                            #yield ('enc',(id,rdict))
                    else:  ##other than 'DG1' type
                        yield (target,(id,rdict))
                        
            else: # invalid segment or no PID/MSH found yet
                if not id or not msh or not npi:
                    logging.critical('Message segment %s found before MSH, PV1 and PID in %s' \
                                     % (gtype,m))
                else:
                    if inobr:
                        ot = segdict.get('OBR')
                        yield(ot,(id,current_obr))
                        if len(obxs) > 0:
                            ot = segdict.get('OBX')
                            for obx in obxs:
                                yield (ot,(id,obx)) # special treatment for obxs
                        inobr = False
                        current_obr = None
                        obxs = []
                        thisattrcode = None
                    s = '## Unexpected segment %s in %s message' % (gtype,mtype)
                    logging.critical(s)

    if final_I9dict:
        final_I9dict['Diagnosis_Code']=totalI9
        yield ('enc',(id,final_I9dict))
    
    if inobr: # we appear to have fallen off the end of the message so send now
        ot = segdict.get('OBR')
        yield(ot,(id,current_obr))
        if len(obxs) > 0:
            ot = segdict.get('OBX')
            for obx in obxs:
                yield (ot,(id,obx)) # special treatment for obxs
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
            print '###Message class = %s' % t
            lookups = writer_lookups[t] # the output etl row
            writefile = writefiles[t] # and file
            iddict = mclasses[t]
            idk = iddict.keys()
            idk.sort()
            for k in idk:
                print '#*** id =',k
                mlist = mclasses[t][k]
                for m in mlist:
                    etl_Writer(rdict=m,lookups=lookups,outdest=writefile)

    for x in writefiles.values():
        x.close() # close etl files


###################################
def movefile(f, fromdir, todir):
    shutil.move(fromdir+'/%s' % f, todir)
    logging.info('Moving file %s from %s to %s\n' % (f, fromdir, todir))

###################################
def parseMessages(mlist=[],grammars={},incominghl7f=None):
    """test the grammar driven parser
    expects a list of individual messages,
    each of which is a list of segment lines
    """
    mclasses = {}
    for i,m in enumerate(mlist): # generator will yield message segments
        messages = messageIterator(m=m,grammars=grammars,incominghl7f=incominghl7f)
        npi = None
        for k,thing in messages: # each message has (id,rdict) or (id,(obr,[obx,..obx]))
            if not mclasses.get(k,None):
                mclasses[k] = {}
            id,message = thing # split out
            if k <> 'msh': # don't want these now
                if k == 'pid': # only want one of these for each unique patient -> demog
                    if not mclasses[k].get(id,None): # not there yet
                        mclasses[k][id] = [message,] # put message into this class
                elif k == 'pcp': # one per provider
                    npi = message.get(PCP_NPI,None)
                    if not npi:
                        npi = message.get(FACILITY_NAME,None) # hack...
                    if not npi:
                        logging.critical('PV1 without an NPI! Cannot cope - %s' % message)
                    else:
                        if not mclasses[k].get(npi,None): # not there yet
                            mclasses[k][npi] = [message,] # put message into this class
                else:
                    sofar = mclasses[k].get(id,[])
                    sofar.append(message)
                    mclasses[k][id] = sofar # replace with update
    return mclasses

if __name__ == "__main__":
    setLogging(appname=prog)
    logging.info('##########Processing started at %s' % timenow())

    hlfiles=os.listdir('/home/ESP/NORTH_ADAMS/incomingHL7/')
    incomdir = '/home/ESP/NORTH_ADAMS/incomingHL7/'
    todir = '/home/ESP/NORTH_ADAMS/archivedHL7/'
    for f in hlfiles:
        print 'PROCESS %s' % f
        tm = makeTests(incomdir+f)
        grammars = makeGrammars()
        mclasses = parseMessages(mlist=tm,grammars=grammars,incominghl7f = f)
        writeMDicts(mclasses=mclasses)
        movefile(f, incomdir, todir)

    for x in dict(map(lambda x:(x,None), outfilenames)).keys():
        xh  =file(x,'a+')
        xh.write('CONTROL TOTALS^NorthAdams^^^^\n')
        xh.close() # close etl files
                                               


    logging.info('##########Processing completed at %s' % timenow())
    logging.shutdown()

