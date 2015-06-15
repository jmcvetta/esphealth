'''
ESP Health
Data Loading 
Base Classes

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc.
@contact: http://esphealth.org
@copyright: (c) 2012 Commonwealth Informatics Inc.
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


import abc

from pkg_resources import iter_entry_points

from ESP.utils import log


class UnknownSiteException(BaseException):
    '''
    Raised when a named site cannot be found
    '''
    pass


class SiteDefinition(object):

    __metaclass__ = abc.ABCMeta
    
    #
    # Abstract class interface
    #
            
    @abc.abstractproperty
    def short_name(self):
        '''
        Short name (SlugField-compatible).
        @rtype: String
        '''
    
    @abc.abstractproperty
    def uri(self):
        '''
        A URI which uniquely describes this site definition.  URIs should
        follow this general format:
            'urn:x-esphealth:encounter-type-mapper:developers_organization_name:site_name:version'
        For example:
            'urn:x-esphealth:encountertypemapper:commoninf:metrohealth:v1'
        @rtype: String
        '''
    
    @abc.abstractmethod
    def set_enctype(self):
        '''
        Examine the database and generate encounter type values
        @return: Success or Fail (Boolean)
        @rtype:  Boolean
        '''
    
    #-------------------------------------------------------------------------------
    #
    # Class Methods
    #
    #-------------------------------------------------------------------------------
    
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known sites
        @rtype:  List
        '''
        #
        # Retrieve from modules
        #
        sites = []
        for entry_point in iter_entry_points(group='esphealth', name='encountertypemap'):
            factory = entry_point.load()
            sites += factory()
        sites.sort(key = lambda h: h.short_name)
        # 
        # Sanity check
        #
        names = {}
        uris = {}
        for d in sites:
            if d.uri in uris:
                msg = 'Cannot load: %s' % d
                msg = 'Duplicate site URI: "%s"' % d.uri
                log.critical(msg)
                raise RuntimeError(msg)
            else:
                uris[d.uri] = d
            if d.short_name in names:
                msg = 'Cannot load: %s' % d
                msg = 'Duplicate site name "%s"' % d.short_name
                log.critical(msg)
                raise RuntimeError(msg)
            else:
                names[d.short_name] = d
        return sites
    
    @classmethod
    def get_by_short_name(cls, short_name):
        '''
        Returns the site specified by short name
        '''
        site = {}
        for d in cls.get_all():
            site[d.short_name] = d
        if not short_name in site:
            raise UnknownSiteException('Could not get site for name: "%s"' % short_name)
        return site[short_name]
    
    @classmethod
    def get_by_uri(cls, uri):
        '''
        Returns the disease indicated by URI
        '''
        site = {}
        for d in cls.get_all():
            site[d.uri] = d
        if not uri in site:
            raise UnknownSiteException('Could not get disease definition for uri: "%s"' % uri)
        return site[uri]
