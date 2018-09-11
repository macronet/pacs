#!/usr/bin/python
# -*- coding: UTF-8 -*-
# service-libnfc.py v2018091101
import time
import os
import datetime
import config
import MySQLdb

hostname=config.DATABASE_CONFIG['hostname']
database=config.DATABASE_CONFIG['database']
username=config.DATABASE_CONFIG['username']
password=config.DATABASE_CONFIG['password']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    OKGREENBG = '\033[42m'
    FAILREDBG = '\033[41m'

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

import nfc
rdwr_options = {
    'targets': ['106A', '106B', '212F', '424F'],
    'on-connect': lambda tag: False,
    'iterations': 1,
    'interval': 0
}
import ndef
from nfc.tag import tt1
from nfc.tag import tt2
from nfc.tag import tt3
from nfc.tag import tt4
tagtypes = (
    ('uid', nfc.tag.tt1.Type1Tag),
    ('uid', nfc.tag.tt2.Type2Tag),
    ('idm', nfc.tag.tt3.Type3Tag),
    ('uid', nfc.tag.tt4.Type4Tag)
)

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    timestamp = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
#    timestampSQL = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print '                        '
    print(' Puolametsä Lämpöyhtiö' + '     ' + timestamp + '     ')
    print '                        '
    print hostname
    print database
    print username
    print password
    clf = nfc.ContactlessFrontend('tty:S0:pn532')
    after1s = lambda: time.time() - started > 0.5
    started = time.time()
    tag = clf.connect(rdwr=rdwr_options, llcp={}, terminate=after1s)
    if tag:
        uid = str(tag.identifier).encode('hex')
# Verify
        db = MySQLdb.connect(read_default_file="./config.ini",db=database)
        cur = db.cursor()
        sql = "SELECT cards.uid,cards.owner,owner.house,owner.apartment,owner.name FROM cards RIGHT JOIN owner ON cards.owner = owner.id WHERE cards.uid = %s AND cards.active = 1 LIMIT 1"
        cur.execute(sql, [uid])
        if not cur.rowcount:
            # Fail
            #sql = "INSERT INTO poller (poller.uid) VALUES (%s)"
            #cur.execute(sql, [uid])
            #db.commit()
            os.system('cls' if os.name == 'nt' else 'clear')
            print bcolors.FAILREDBG
            print(' Puolametsä Lämpöyhtiö' + '     ' + timestamp + '     ')
            print '                        '
            print '      Unknown tag!      '
            print '     ' + uid + '     '
            print '                        '
            print bcolors.ENDC
            time.sleep(5)
        else:
            # OK
            os.system('cls' if os.name == 'nt' else 'clear')
            print bcolors.OKGREENBG
            print(' Puolametsä Lämpöyhtiö' + '     ' + timestamp + '     ')
            print '                        '
            print '     Known tag, OK!     '
            print '     ' + uid + '     '
            print '                        '
            print bcolors.ENDC
            time.sleep(5)
