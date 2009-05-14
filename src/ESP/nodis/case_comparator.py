#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
                             Case Comparator Tool


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


import datetime

from ESP.esp.models import Case as OldCase
from ESP.esp.models import Case
from ESP.nodis.models import Case as NewCase



BEGIN_COMPARE_DATE = datetime.date(2009, 1, 1)


def main():
    print OldCase.objects.filter(casecreatedDate__gte=BEGIN_COMPARE_DATE).values_list('caseRule', 'caseDemog')


if __name__ == '__main__':
    main()