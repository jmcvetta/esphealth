'''
                                  ESP Health
Packaging Information
                                  
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from setuptools import setup
from setuptools import find_packages

setup(
    name = 'Electronic medical record Support for Public Health (ESPnet)',
    version = '3.0a',
    packages = find_packages(),
    install_requires = [
        'Django >= 1.2',
        'south',
        ],
    package_data = {
        '': ['*.bz2',],
        'ui': ['*.html', '*.txt',], 
        },
    author = 'Jason McVetta',
    author_email = 'jason.mcvetta@heliotropi.cc',
    description = 'Disease surveillance application',
    license = 'LGPLv3',
    keywords = 'disease surveillance public health epidemiology',
    url = 'http://esphealth.org',
    )
