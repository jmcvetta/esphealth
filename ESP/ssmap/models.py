from django.db import models
import datetime
from django.contrib.auth.models import User 
import string

class eventdate(models.Model):
    """cheap way to get all events on any date
    should do a fixture to create a few years worth
    """
    edate=models.DateField(primary_key=True)

    def __unicode__(self):
        return('%s' % self.edate)
        

class rule(models.Model):
    """versions are supported - always ask for the latest one if
    creating an event. Once created, the event will retain it's correct rule
    version for posterity but you may want to filter these if they're importantly
    different
    """
    rulename = models.CharField(max_length=50,primary_key=True,unique=True)
    narrative = models.TextField()
    vdate = models.DateField(auto_now_add=True)
    unique_together = ('rulename','vdate')
    
    def __unicode__(self):
        return '%s: %s' % (self.rulename,self.narrative[:100])
 
class geoplace(models.Model):
    """ the fk's allow all events to be snarfed
    for any given geoplace - if all encounters are considered -
    via all their demogid geoplaces
    makes getting volumes a lot easier
    """
    place = models.CharField(max_length=50,primary_key=True,unique=True)
    la = models.DecimalField(max_digits=9, decimal_places=6)
    lo = models.DecimalField(max_digits=9, decimal_places=6)
    zipcode = models.CharField(max_length=10,db_index=True)
    address = models.TextField()
    narrative = models.TextField()

    def zip3(self):
        return self.zipcode[:3]

    def zip4(self):
        return self.zipcode[:4]

    def __unicode__(self):
      return '%s: la %f lo %f zip %s add %s narr %s' % (self.place,self.la,self.lo,
            self.zipcode, self.address, self.narrative[:60] ) 
   
class enc(models.Model):
   """ store total encounters for this place
   broken down by age
   """
   edate = models.ForeignKey('eventDate')
   place = models.ForeignKey('geoplace')
   agecounts = models.TextField() # use this to store age counts eg
   total = models.IntegerField()

   def __unicode__(self):
      return 'On %s total = %d at %s ' % (self.edate,self.total,self.place)
       

   def __unicode__(self):
      return '%s: on %s at %s age %d' % (self.rule,self.edate,self.age)

class event(models.Model):
   rule = models.ForeignKey('rule')
   edate = models.ForeignKey('eventDate') # this allows us to get all events on any date
   res_place = models.ForeignKey('geoplace',related_name='res',null=True)
   seen_place = models.ForeignKey('geoplace',related_name='seen',null=True)
   temp = models.FloatField()
   icd = models.TextField()
   age = models.IntegerField()

