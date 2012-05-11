import datetime
import random
import string as pstring

import common

def string(length=10):
    chars = pstring.digits + pstring.letters
    return ''.join([random.choice(chars) for x in xrange(length)])

def numeric_id():
    return random.randrange(1, 100500)

def first_name():
    return random.choice(common.FIRST_NAMES)

def last_name():
    return random.choice(common.LAST_NAMES)

def date_of_birth(as_string=False, format='%Y%m%d'):
    days_old = random.randrange(0, 36500) # Up to a hundred years old
    dob = datetime.date.today() - datetime.timedelta(days=days_old)
    
    return dob.strftime(format) if as_string else dob         

rec =0
def autoIncrement():
        global rec
        pStart = 1 #adjust start value, if req'd 
        pInterval = 1 #adjust interval value, if req'd
        if (rec == 0): 
            rec = pStart 
        else: 
            rec = rec + pInterval 
        return rec
 
def date_range(as_string=False, format='%Y%m%d'):
    days_range = random.randrange(0, 365*3) # Up to 3 years 
    date = datetime.date.today() - datetime.timedelta(days=days_range)
    
    return date.strftime(format) if as_string else date         

def gender():
    return ('M' if random.random() <= 0.49 else 'F')

def marital_status():
    return random.choice(common.MARITAL_STATUS)

def race():
    return random.choice(common.RACES)
    

def phone_number():
    area_code = '555'
    prefix = str(100 + random.randrange(900))
    suffix = '%04d' % (random.randrange(10000))
    
    return '-'.join([area_code, prefix, suffix])


def city():
    return random.choice(common.CITIES), random.choice(common.STATES)

def address():
    return ' '.join([
            str(random.randrange(1000)), 
            random.choice(common.ADDRESSES),
            random.choice(['', 'Apt %d' % random.randrange(1, 40)])
            ])
    
def ssn():
    prefix = '%03d' % random.randrange(1000)
    infix = '%02d' % random.randrange(100)
    suffix = '%04d' % random.randrange(10000)
    
    return '-'.join([prefix, infix, suffix])

def zip_code():
    return '%05d' % random.randrange(90000)

def fever_temperature():
    '''Returns a float that can be interpreted as a fever-high temperature'''
    return 101 + float(random.randrange(-5, 5))/10

def body_temperature():
    '''returns a value common for human temperature (in F)'''
    return 98 - float(random.randrange(-2, 2))/10
