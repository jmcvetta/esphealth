'''
                                   ESP Health
                                Hepatitis C New 2
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
    name = 'esphealth-disease-hepatitis-new2',
    version = '1.0',
    author = 'Carolina Chacin',
    author_email = 'cchacin@commoninf.com',
    description = 'Hepatitis C new 2 disease definition module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'hepatitis c new 2 algorithm disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        disease_definitions = hepatitis_new2:disease_definitions
        event_heuristics = hepatitis_new2:event_heuristics
    '''
    )
