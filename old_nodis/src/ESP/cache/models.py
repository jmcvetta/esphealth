'''
                              ESP Health Project
                                  Cached Data
                                  Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from django.db import models


class SiteName(models.Model):
    '''
    Name & zip code of all sites where physician encounters have occurred
    '''
    name = models.CharField(max_length=100, blank=False)
    zip = models.CharField(max_length=20, blank=False)
    
