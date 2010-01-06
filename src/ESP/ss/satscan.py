"""
TODO: we need age groups - presumably each age group is run independently?

quick hack
to make
[rerla@esphealth satscan]$ head real_2004-05-09.cas
01027 1 2006-01-11
01104 1 2004-02-25
01118 1 2005-07-12
01129 1 2004-12-28
01236 20 2004-05-08
01237 20 2004-05-08
01238 20 2004-05-08
01420 1 2005-08-17
01420 1 2005-11-30
01431 1 2003-12-19

from
edate	zip_site	syndrome	nsyndrome	nallEnc	pctsyndrome
20060701	01824	ILI	1	120	0.833333
20060701	02144	ILI	2	171	1.169591
20060701	02184	ILI	2	177	1.129944
20060701	02215	ILI	4	181	2.209945
;5B20060701	02481	ILI	1	161	0.621118
20060702	01742	ILI	2	23	8.695652
20060702	01824	ILI	1	68	1.470588
20060702	01961	ILI	2	38	5.263158


"""
import datetime,os,sys
ourdur = 180 # days to include

prm="""[Input]
; case data filename
CaseFile=%s.cas
; control data filename
ControlFile=
; population data filename
PopulationFile=
; coordinate data filename
CoordinatesFile=boston.geo
; use grid file? (y/n)
UseGridFile=n
; grid data filename
GridFile=
; time precision (0=None, 1=Year, 2=Month, 3=Day)
PrecisionCaseTimes=3
; coordinate type (0=Cartesian, 1=latitude/longitude)
CoordinatesType=1
; study period start date (YYYY/MM/DD)
StartDate=%s
; study period end date (YYYY/MM/DD)
EndDate=%s

[Analysis]
; analysis type (1=Purely Spatial, 2=Purely Temporal, 3=Retrospective Space-Time, 4=Prospective Space-Time, 5=N/A, 6=Prospective Purely Temporal)
AnalysisType=4
; model type (0=Poisson, 1=Bernoulli, 2=Space-Time Permutation, 3=Ordinal, 4=Exponential, 5=Normal)
ModelType=2
; scan areas (1=High Rates(Poison,Bernoulli,STP); High Values(Ordinal,Normal); Short Survival(Exponential), 2=Low Rates(Poison,Bernoulli,STP); Low 
Values(Ordinal,Normal); Long Survival(Exponential), 3=Both Areas)
ScanAreas=1
; time aggregation units (0=None, 1=Year, 2=Month, 3=Day)
TimeAggregationUnits=3
; time aggregation length (Positive Integer)
TimeAggregationLength=1
; Monte Carlo replications (0, 9, 999, n999)
MonteCarloReps=9999

[Output]
; analysis results output filename
ResultsFile=%s.txt
; output simulated log likelihoods ratios in ASCII format? (y/n)
SaveSimLLRsASCII=y
; output simulated log likelihoods ratios in dBase format? (y/n)
SaveSimLLRsDBase=n
; output relative risks in ASCII format? (y/n)
IncludeRelativeRisksCensusAreasASCII=n
; output relative risks in dBase format? (y/n)
IncludeRelativeRisksCensusAreasDBase=n
; output location information in ASCII format? (y/n)
CensusAreasReportedClustersASCII=y
; output location information in dBase format? (y/n)
CensusAreasReportedClustersDBase=n
; output cluster information in ASCII format? (y/n)
MostLikelyClusterEachCentroidASCII=y
; output cluster information in dBase format? (y/n)
MostLikelyClusterEachCentroidDBase=n
; output cluster case information in ASCII format? (y/n)
MostLikelyClusterCaseInfoEachCentroidASCII=n
; output cluster case information in dBase format? (y/n)
MostLikelyClusterCaseInfoEachCentroidDBase=n

[Multiple Data Sets]
; multiple data sets purpose type (0=Multivariate, 1=Adjustment)
MultipleDataSetsPurposeType=0

[Data Checking]
; study period data check (0=Strict Bounds, 1=Relaxed Bounds)
StudyPeriodCheckType=1
; geographical coordinates data check (0=Strict Coordinates, 1=Relaxed Coordinates)
GeographicalCoordinatesCheckType=1

[Non-Eucledian Neighbors]
; neighbors file
NeighborsFilename=
; use neighbors file (y/n)
UseNeighborsFile=n

[Spatial Window]
; maximum spatial size in population at risk (<=50pct)
MaxSpatialSizeInPopulationAtRisk=50
; maximum spatial size in max circle population file (<=50pct)
MaxSpatialSizeInMaxCirclePopulationFile=50
; maximum spatial size in distance from center (positive integer)
MaxSpatialSizeInDistanceFromCenter=1
; restrict maximum spatial size - max circle file? (y/n)
UseMaxCirclePopulationFileOption=n
; restrict maximum spatial size - distance? (y/n)
UseDistanceFromCenterOption=n
; include purely temporal clusters? (y/n)
IncludePurelyTemporal=n
; maximum circle size filename
MaxCirclePopulationFile=
; window shape (0=Circular, 1=Elliptic)
SpatialWindowShapeType=0
; elliptic non-compactness penalty (0=NoPenalty, 1=MediumPenalty, 2=StrongPenalty)
NonCompactnessPenalty=1

[Temporal Window]
; maximum temporal cluster size (<=90pct)
MaxTemporalSize=7
; include purely spatial clusters? (y/n)
IncludePurelySpatial=n
; how max temporal size should be interpretted (0=Percentage, 1=Time)
MaxTemporalSizeInterpretation=1
; temporal clusters evaluated (0=All, 1=Alive, 2=Flexible Window)
IncludeClusters=0
; flexible temporal window start range (YYYY/MM/DD,YYYY/MM/DD)
IntervalStartRange=2008/12/03,2009/06/01
; flexible temporal window end range (YYYY/MM/DD,YYYY/MM/DD)
IntervalEndRange=2008/12/03,2009/06/01

[Space and Time Adjustments]
; time trend adjustment type (0=None, 1=Nonparametric, 2=LogLinearPercentage, 3=CalculatedLogLinearPercentage, 4=TimeStratifiedRandomization)
TimeTrendAdjustmentType=0
; time trend adjustment percentage (>-100)
TimeTrendPercentage=0
; adjustments by known relative risks file name (with HA Randomization=1)
AdjustmentsByKnownRelativeRisksFilename=
; use adjustments by known relative risks file? (y/n)
UseAdjustmentsByRRFile=n
; spatial adjustments type (0=No Spatial Adjustment, 1=Spatially Stratified Randomization)
SpatialAdjustmentType=0

[Inference]
; prospective surveillance start date (YYYY/MM/DD)
ProspectiveStartDate=2009/03/01
; terminate simulations early for large p-values? (y/n)
EarlySimulationTermination=y
; adjust for earlier analyses(prospective analyses only)? (y/n)
AdjustForEarlierAnalyses=n
; report critical values for .01 and .05? (y/n)
CriticalValue=n
; perform iterative scans? (y/n)
IterativeScan=n
; maximum iterations for iterative scan (0-32000)
IterativeScanMaxIterations=10
; max p-value for iterative scan before cutoff (0.000-1.000)
IterativeScanMaxPValue=0.05

[Clusters Reported]
; criteria for reporting secondary clusters(0=NoGeoOverlap, 1=NoCentersInOther, 2=NoCentersInMostLikely,  3=NoCentersInLessLikely, 4=NoPairsCentersEachOther, 
5=NoRestrictions)
CriteriaForReportingSecondaryClusters=0
; restrict reported clusters to maximum geographical cluster size? (y/n)
UseReportOnlySmallerClusters=n
; maximum reported spatial size in population at risk (<=50pct)
MaxSpatialSizeInPopulationAtRisk_Reported=50
; maximum reported spatial size in max circle population file (<=50pct)
MaxSizeInMaxCirclePopulationFile_Reported=50
; maximum reported spatial size in distance from center {positive integer)
MaxSpatialSizeInDistanceFromCenter_Reported=1
; restrict maximum reported spatial size - max circle file? (y/n)
UseMaxCirclePopulationFileOption_Reported=n
; restrict maximum reported spatial size - distance? (y/n)
UseDistanceFromCenterOption_Reported=n

[Elliptic Scan]
; elliptic shapes - one value for each ellipse (comma separated decimal values)
EllipseShapes=1.5,2,3,4,5
; elliptic angles - one value for each ellipse (comma separated integer values)
EllipseAngles=4,6,9,12,15

[Isotonic Scan]
; isotonic scan (0=Standard, 1=Monotone)
IsotonicScan=0

[Power Simulations]
; p-values for 2 pre-specified log likelihood ratios? (y/n)
PValues2PrespecifiedLLRs=n
; power calculation log likelihood ratio (no. 1)
LLR1=0
; power calculation log likelihood ratio (no. 2)
LLR2=0
; simulation methods (0=Null Randomization, 1=HA Randomization, 2=File Import)
SimulatedDataMethodType=0
; simulation data input file name (with File Import=2)
SimulatedDataInputFilename=
; print simulation data to file? (y/n)
PrintSimulatedDataToFile=n
; simulation data output filename
SimulatedDataOutputFilename=

[Run Options]
; analysis execution method  (0=Automatic, 1=Successively, 2=Centrically)
ExecutionType=0
; number of parallel processes to execute (0=All Processors, x=At Most X Processors)
NumberParallelProcesses=0
; log analysis run to history file? (y/n)
LogRunToHistoryFile=y
; suppressing warnings? (y/n)
SuppressWarnings=n

[System]
; system setting - do not modify
Version=7.0.3
"""
# needs fbase,sd,ed,fbase

def writeprm(fbase='',sd='',ed=''):
    """ substitute minimum params and make a corresponding prm file for satscan
    """
    ofname = '%s.prm' % fbase
    f = file(ofname,'w')
    p = prm % (fbase,sd,ed,fbase)
    f.write(p)
    f.write('\n')
    f.close()
    

def maked(d='20090601'):
   try:
   	ds = datetime.date(int(d[:4]),int(d[4:6]),int(d[6:]))
   except:
        print '## bad date %s - %s %s %s' % (d,d[:4],d[4:6],d[7:])
        ds = None
   return ds

def makeCas(inf='ESPAtrius_SyndAgg_zip5_Site_Excl_ILI_20060701_20090623.xls',ed='20090601'):
   """
   write a satscan cas file
   """
   fpath,fname = os.path.split(inf) # get rid of any path
   fb = os.path.splitext(fname)[0]
   fbase = '_'.join(fb.split('_')[:-2]) # exclude dates 
   fl = file(inf,'r').readlines()
   fl = [x.split('\t') for x in fl]
   edd = maked(ed)
   sdd = edd - datetime.timedelta(days=ourdur)
   sd = '%04d%02d%02d' % (sdd.year,sdd.month,sdd.day)
   ssd = '%04d/%02d/%02d' % (sdd.year,sdd.month,sdd.day)
   esd = '%04d/%02d/%02d' % (edd.year,edd.month,edd.day)
   outbase = '%s_%s_%s' % (fbase,sd,ed)
   print 'using %s as outbase' % outbase
   outf = '%s.cas' % (outbase)
   writeprm(outbase,ssd,esd)
   f = file(outf,'w')
   for i,row in enumerate(fl[1:]): # ignore header
      d = maked(row[0])
      sd = '%04d/%02d/%02d' % (d.year,d.month,d.day)
      if d and (d >= sdd) and (d <= edd):
          f.write('\t'.join((row[1],row[3],sd)))
          f.write('\n')
   f.close()



if __name__ == "__main__":
    inf='ESPAtrius_SyndAgg_zip5_Site_Excl_ILI_20060701_20090623.xls'
    ed='20090601'
    if len(sys.argv) < 2:
       'using defaults %s %s - override with esp ss infile path and YYYYMMDD start date for 180 day window' % (inf,ed)
    else:
       inf = sys.argv[1]
       ed = sys.argv[2]
       'using supplied %s %s for 180 day window' % (inf,ed)       
    makeCas(inf=inf, ed=ed)


