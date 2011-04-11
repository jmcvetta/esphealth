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

#
# FIXME: Update this file to reflect current ESP setup
#
'''
setup(
    name = 'esphealth-core',
    version = '3.0',
    author = 'Jason McVetta',
    author_email = 'jason.mcvetta@heliotropi.cc',
    description = 'Disease surveillance application',
    license = 'LGPLv3',
    keywords = 'disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    install_requires = [
        'django >= 1.2',
        'south',
        'python-dateutil',
        'simplejson',
        'sqlparse',
        'hl7',
        'django_tables',
        'configobj',
        ],
    packages = find_packages(exclude=['ez_setup']),
    package_data = {
        '': ['*.bz2',],
        'ui': ['*.html', '*.txt',], 
        },
    )
'''
