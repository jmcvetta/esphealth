'''
                                  ESP Health
                             Packaging Information
                                  
@author: Jason McVetta <jason.mcvetta@heliotropi.cc>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from setuptools import setup
from setuptools import find_packages

setup(
    name = 'esphealth-heuristic-pregnancy',
    version = '1.0',
    author = 'Jason McVetta',
    author_email = 'jason.mcvetta@heliotropi.cc',
    description = 'Pregnancy heuristic module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'pregnancy algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        timespan_heuristics = pregnancy:timespan_heuristics
        event_heuristics = pregnancy:event_heuristics
    '''
    )
