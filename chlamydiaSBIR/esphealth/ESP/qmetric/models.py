'''
                              ESP Health Project
                          Quality Metrics data table
                                  Data Models

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from django.db import models
from ESP.emr.models import Patient, Provider
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from ESP.utils import log

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Models
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Element(models.Model):
    '''
    QDM Data Elements
    '''
    TYPE_CHOICES = [ ('vsac','Value Set Authority'),
                     ('local','Not available at VSA'),
                    ]
    cmsname = models.CharField('CMS HQMF document name (no extension)',max_length=50, blank=False, db_index=True)
    ename = models.CharField('QDM Data Element name',max_length=200, blank=False, db_index=True)
    oid = models.CharField('Value Set OID',max_length=100, blank=False, db_index=True)
    use = models.CharField('Primary Use',max_length=100, blank=False, db_index=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    source = models.CharField('Element source: local or VSA',max_length=5,blank=False,db_index=True,choices=TYPE_CHOICES,null=True)
    content_type = models.ForeignKey(ContentType, db_index=True, null=True)
    mapped_field = models.CharField('Field name in emr table containing codes for element mapping',max_length=40, blank=False,null=True)

    class Meta:
        unique_together = ['cmsname', 'ename', 'oid']
        
    def _get_uname(self):
        name = u'%s: %s' % (self.cmsname, self.ename)
        return name
    uname = property(_get_uname)
    
class ElementMapping(models.Model):
    '''
    Mapping of QDM Data Elements to locally available data codes
    If local codes match Value Set Authority available value sets, these values sets will be downloaded.
    If local codes do not match any available VSA value sets, these codes must be manually addded
    '''
    element = models.ForeignKey(Element, blank=False)
    code = models.CharField('code value',max_length=100, blank=False, db_index=True)
    description = models.CharField('code text',max_length=400, blank=False, db_index=True)
    codesystem = models.CharField('code system name',max_length=50, blank=False, db_index=True)
    
    
#TODO: create a results model that will contain cube results for reporting


class Population(models.Model):
    '''
    A medical event
    '''
    TYPE_CHOICES = [ ('numerator','Numerator'),
                     ('denominator','Denominator'),
                    ]
    cmsname = models.CharField('CMSname for this event type', max_length=20, blank=False, db_index=True)
    etype = models.CharField('Event type', max_length=128, blank=False, db_index=True, choices=TYPE_CHOICES)
    source = models.TextField('logic that created this event', blank=False, db_index=True)
    date = models.DateField('Date event occurred', blank=False, db_index=True)
    patient = models.ForeignKey(Patient, blank=False, db_index=True)
    provider = models.ForeignKey(Provider, blank=False, db_index=True)
    timestamp = models.DateTimeField('Time event was created in db', blank=False, auto_now_add=True)
    #TODO: add admin interface
    class Meta:
        unique_together = [('cmsname', 'etype', 'patient','date')]
    
    def __unicode__(self):
        return u'Event # %s (%s %s)' % (self.pk, self.cmsname, self.date)
    
    def verbose_str(self):
        return 'Event # %s (%s %s)' % (self.pk, self.cmsname, self.date)
        
class Population_emr(models.Model):
    population = models.ForeignKey(Population,db_index=True)
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, 
        cmsname,
        etype,
        source,
        date,
        patient,
        provider,
        emr_records,
        ):
        '''
        Creates an event and event_emr records linked to emr_records.  
        
        @return: (new_event)
        @rtype: (object)
        '''
        #records = []
        p = Population(
            cmsname = cmsname,
            etype_ = etype,
            source =source,
            date = date,
            patient = patient,
            provider = provider,
            )
        p.save()
        for obj in emr_records:
            content_type = ContentType.objects.get_for_model(obj)
            o = Population_emr(
                event = p,
                content_type = content_type,
                object_id = obj.pk,
                )
            o.save()
        log.debug('Created new event: %s' % p)
        return ( p )

    
    
    


