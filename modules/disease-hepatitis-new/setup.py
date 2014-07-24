'''
                                   ESP Health
                                Hepatitis C New
                             Packaging Information
                                  
@author: Carolina Chacin <cchacin@commoninf.com>
@organization: Commonwealth informatics
@contact: http://www.esphealth.org
@copyright: (c) 2011-2012 Channing Laboratory, 2011-2014 Commonwealth informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


from setuptools import setup
from setuptools import find_packages

setup(
    name = 'esphealth-disease-hepatitis-new',
    version = '1.0',
    author = 'Carolina Chacin',
    author_email = 'cchacin@commoninf.com',
    description = 'Hepatitis C new disease definition module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'hepatitis c new algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = hepatitis_new:disease_definitions
        event_heuristics = hepatitis_new:event_heuristics
    '''
    )
