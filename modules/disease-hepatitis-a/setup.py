'''
                                   ESP Health
                             Hepatitis A Definition
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
    name = 'esphealth-disease-hepatitis_a',
    version = '1.0',
    author = 'Jason McVetta',
    author_email = 'jason.mcvetta@gmail.com',
    description = 'Hepatitis A disease definition module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'hepatitis a algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = hepatitis_a:disease_definitions
        event_heuristics = hepatitis_a:event_heuristics
    '''
    )
