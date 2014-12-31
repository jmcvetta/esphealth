'''
                                  ESP Health
                          Asthma new Disease Definition
                             Packaging Information
                                  
@author: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics 
@contact: http://esphealth.org
@copyright: (c) 2013 
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from setuptools import setup
from setuptools import find_packages

setup(
    name = 'esphealth-disease-asthma-new',
    version = '1.0',
    author = 'Carolina Chacin',
    author_email = 'cchacin@commoninf.com',
    description = 'Asthma with improved performance disease definition module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'asthma new algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = asthma-new:disease_definitions
        event_heuristics = asthma-new:event_heuristics
    '''
    )
