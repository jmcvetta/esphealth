'''
                                  ESP Health
                       Pelvic Inflamatory Disease (PID) Definition
                             Packaging Information
                                  
@author: Carolina Chacin <cchacin@commoninf.com>
@organization: commonwealth informatics http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from setuptools import setup
from setuptools import find_packages

setup(
    name = 'esphealth-disease-pid',
    version = '1.0',
    author = 'Carolina Chacin',
    author_email = 'cchacin@commoninf.com',
    description = 'Pelvic Inflamatory disease definition module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'Pelvic Inflamatory algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = pid:disease_definitions
        event_heuristics = pid:event_heuristics
    '''
    )
