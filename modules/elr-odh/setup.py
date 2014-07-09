'''
                                  ESP Health
                          Electronic Lab Reporting
                             Packaging Information
                                  
@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2014 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from setuptools import setup
from setuptools import find_packages

setup(
    name = 'esphealth-elr-odh',
    version = '1.0',
    author = 'Bob Zambarano',
    author_email = 'bzambarano@commoninf.com',
    description = 'electronic lab reporting module for ODH ELR',
    license = 'LGPLv3',
    keywords = 'elr electronic lab reporting ODH Meaningful Use',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = odh:disease_definitions
        event_heuristics = odh:event_heuristics
    '''
    )
