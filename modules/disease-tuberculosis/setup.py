'''
                                  ESP Health
                          Diabetes Disease Definition
                             Packaging Information
                                  
@author: Carolina Chacin <cchacin@commoninf.com>
@organization: Commonwealth Informatics.
@contact: http://esphealth.org
@copyright: (c) 2012 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from setuptools import setup
from setuptools import find_packages

setup(
    name = 'esphealth-disease-tuberculosis',
    version = '1.0',
    author = 'Carolina Chacin',
    author_email = 'cchacin@commoninf.com',
    description = 'tuberculosis disease definition module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'tuberculosis algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = tuberculosis:disease_definitions
        event_heuristics = tuberculosis:event_heuristics
    '''
    )
