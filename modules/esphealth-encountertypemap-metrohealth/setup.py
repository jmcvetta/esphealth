'''
                                  ESP Health
                     Encounter-Type Mapper for MetroHealth
                                 Package Setup

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc.
@contact: http://www.esphealth.org
@copyright: (c) 2012 Commonwealth Informatics Inc.
@license: LGPL
'''

from setuptools import setup, find_packages

setup(
    name = 'esphealth-encountertypemap-metrohealth',
    version = '1.0',
    author = 'Bob Zambarano',
    author_email = 'bzambarano@commoninf.com',
    description = 'MetroHealth encounter-type mapper for ESP Health application',
    license = 'LGPLv3',
    keywords = 'disease surveillance public health epidemiology metrohealth',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        encountertypemap = metrohealth:encountertypemap
    '''
    )
