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
    name = 'esphealth-heuristic-glucose-crf',
    version = '1.0',
    author = 'Jason McVetta',
    author_email = 'jason.mcvetta@heliotropi.cc',
    description = 'Compound random/fasting glucose test heuristic module for ESP Health application',
    license = 'LGPLv3',
    keywords = 'random fasting glucose test heuristic surveillance public health epidemiology',
    url = 'http://esphealth.org',
    packages = find_packages(exclude=['ez_setup']),
    install_requires = [
        ],
    entry_points = '''
        [esphealth]
        event_heuristics = glucose_crf:get_heuristics
        abstract_lab_tests = glucose_crf:get_tests
    '''
    )
