"""
models for espss
note that we use a lot of strings as primary keys - inefficient but makes it easier during
development - may want to revert to more usual record numbers as primary key and do the
relevant lookups in the apps.

"""


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
    address = models.TextField(null=True)  
    narrative = models.TextField(null=True)  

    def zip3(self):
        return self.zipcode[:3]

    def zip4(self):
        return self.zipcode[:4]

    def __unicode__(self):
      return '%s: la %f lo %f zip %s add %s narr %s' % (self.place,self.la,self.lo,
            self.zipcode, self.address, self.narrative[:60] ) 

class encType(models.Model):
   """ classes of encounter totals stored in the enc table
   eg atriusres, atriussite
   """   
   enctype = models.CharField(max_length=20,primary_key=True)
   narrative = models.TextField(null=True)    

   def __unicode__(self):
      return '%s: %s' % (self.enctype,self.narrative[:60])


class enc(models.Model):
   """ store total encounters for this place and event class
   note that we need to distinguish event classes because (eg) atrius data by residential
   zip will overlap atrius data by site zip
   broken down by age
   """
   etype = models.ForeignKey('encType')
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

