'''
                                  ESP Health
                          Electronic Lab Reporting
                             Packaging Information
                                  
@author: Rich Schaaf <rschaaf@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2012 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from setuptools import setup
from setuptools import find_packages

setup(
    name = 'esphealth-elr-positive-test',
    version = '1.0',
    author = 'Rich Schaaf',
    author_email = 'rschaaf@commoninf.com',
    description = 'electronic lab reporting module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'elr electronic lab reporting surveillance public health',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = positivetest:disease_definitions
        event_heuristics = positivetest:event_heuristics
    '''
    )
