#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
List LOINCs Utility


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from ESP.hef.core import BaseHeuristic
from ESP.hef.events import * # Needed for all events to be registered


def main():
    print '=' * 80
    print 'ESP Health'.center(80)
    print ''
    print 'List of LOINC codes used in heuristic event definitions:'
    print '-' * 80
    print '%10s\t%s' % ('LOINC', 'Heuristic Name')
    print '-' * 80
    lbe = BaseHeuristic.get_all_loincs_by_event()
    keys = lbe.keys()
    keys.sort(key=lambda x: x.name)
    for h in keys:
        for loinc in lbe[h]:
            print '%10s\t%s' % (loinc, h.name)
    print '=' * 80


if __name__ == '__main__':
    main()