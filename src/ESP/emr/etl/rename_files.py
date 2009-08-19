'''
Created on Aug 19, 2009

@author: jason
'''

import sys
import os
import shutil
import re


INPUT_DIR = '/srv/esp/epic/broken'
OUTPUT_DIR = '/srv/esp/epic/incoming'

def main():
    for filename in os.listdir(INPUT_DIR):
        monthly = False
        first, second, third = filename.split('.')
        if len(third) == 10 and third[-2:] == '_m':
            monthly = True
            third = third[:-2]
        if not len(third) == 8:
            print 'Could not understand date stamp: %s' % filename
            continue
        int(third) # Sanity check -- all numeric
        month = third[0:2]
        day = third[2:4]
        year = third[4:]
        assert year[:3] == '200' # Sanity check -- everything is from 2006-9
        new_name = '%s.%s.%s-%s-%s' % (first, second, year, month, day)
        if monthly:
            new_name = new_name + '_m'
        src = os.path.join(INPUT_DIR, filename)
        dst = os.path.join(OUTPUT_DIR, new_name)
        shutil.move(src, dst)


if __name__ == '__main__':
    main()