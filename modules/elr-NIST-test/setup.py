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
    name = 'esphealth-elr-NIST-test',
    version = '1.0',
    author = 'Bob Zambarano',
    author_email = 'bzambarno@commoninf.com',
    description = 'electronic lab reporting module for NIST Meaningful Use ELR testing',
    license = 'LGPLv3',
    keywords = 'elr electronic lab reporting NIST Meaningful Use testing',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = NISTtest:disease_definitions
        event_heuristics = NISTtest:event_heuristics
    '''
    )
