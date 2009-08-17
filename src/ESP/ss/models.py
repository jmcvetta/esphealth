'''
                                  ESP Health
                          Syndromic Surveillance Tables
                                  Data Models

@author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>

'''

from django.db import models


from ESP.hef.models import HeuristicEvent

    
class Site(models.Model):
    name = models.CharField(max_length=200, unique=True)
    region = models.CharField(max_length=20, db_index=True)
    zip_code = models.CharField(max_length=9)

class Locality(models.Model):
    zip_code = models.CharField(max_length=9, db_index=True)
    locality = models.CharField(max_length=50, db_index=True)
    city = models.CharField(max_length=50, db_index=True)
    state = models.CharField(max_length=2)
    region_code = models.CharField(max_length=5)
    region_name = models.CharField(max_length=20)
    is_official = models.BooleanField(default=True)

    
    def __unicode__(self):
        return u'%s - %s, %s (%s)' % (self.locality, self.city, self.state, self.zip_code)

class SyndromeEvent(HeuristicEvent):
    reporting_site = models.ForeignKey(Site)

    


