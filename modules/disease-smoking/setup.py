'''
                                  ESP Health
                          Smoking Disease Definition
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
    name = 'esphealth-disease-smoking',
    version = '1.0',
    author = 'Carolina Chacin',
    author_email = 'cchacin@commoninf.com',
    description = 'Smoking disease definition module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'smoking algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = smoking:disease_definitions
        event_heuristics = smoking:event_heuristics
    '''
    )
